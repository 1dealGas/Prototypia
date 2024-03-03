// Aerials Player API Functions
#include "p_singleton.h"
#pragma once


// Hint Color Settings
#define H_EARLY_R 0.275f
#define H_EARLY_G 0.495f
#define H_EARLY_B 0.5603125f

#define H_HIT_C 0.73f
#define H_HIT_R 0.73f
#define H_HIT_G 0.6244921875f
#define H_HIT_B 0.4591015625f

#define H_LATE_R 0.5603125f
#define H_LATE_G 0.3403125f
#define H_LATE_B 0.275f

// Effect Color Settings
#define A_EARLY_R 0.3125f
#define A_EARLY_G 0.5625f
#define A_EARLY_B 0.63671875f

#define A_HIT_C 1.0f
#define A_HIT_R 1.0f
#define A_HIT_G 0.85546875f
#define A_HIT_B 0.62890625f

#define A_LATE_R 0.63671875f
#define A_LATE_G 0.38671875f
#define A_LATE_B 0.3125f

// Judge Range Setting   [0,100)
constexpr uint8_t JUDGE_RANGE = 37;


// Typedefs
typedef dmVMath::Vector3 v3i, *v3;
typedef dmVMath::Vector4 v4i, *v4;
typedef dmGameObject::HInstance GO;
typedef dmVMath::Point3 p3;

// Settings
static uint32_t before;
static uint16_t special_hint;
static float xscale, yscale, xdelta, ydelta, rotsin, rotcos;
static bool daymode, allow_anmitsu;

// Internals
static float SIN, COS;
static uint32_t last_ms;
static uint16_t dt_p1, dt_p2;
static int8_t mindt = -37, maxdt = 37, idelta = 0;
static std::unordered_map<uint32_t, uint8_t> last_wgo;
static std::vector<ArHint*> blocked;


// Init Function
static int InitArf(lua_State* L) {
	// InitArf(buf, is_auto) -> before, total_hints, wgo_required, hgo_required
	// Recommended Usage (Requires Defold 1.6.4 or Newer):
	//     local buf = sys.load_buffer( "Arf/1011.ar" )   -- Also allows a path on your disk.
	//     local b,t,w,h = Arf2.InitArf(buf)

	// Before our next refactoring, we'll deserialize and decode our chart[fumen] into
	// C++ object instances. See "p_singleton.h" for more info.


	// Prevent Repeated Calling
	if(before) return 0;

	// Reset Params
	daymode = false;
	allow_anmitsu = true;
	xdelta = ydelta = rotsin = 0.0f;
	xscale = yscale = rotcos = 1.0f;
	last_ms = dt_p1 = dt_p2 = 0;

	// Ensure a clean Initialization
	last_wgo.clear();
	blocked.clear();

	// Get the Chart[Fumen] Buffer
	void* ArfBuf = nullptr; {
		uint32_t ArfSize = 0;
		dmScript::LuaHBuffer *B = dmScript::CheckBuffer(L, 1);
		dmBuffer::GetBytes(B -> m_Buffer, &ArfBuf, &ArfSize);
		if(!ArfSize) return 0;
	}


	// Decode Stuff
	// Code Style: If there is no element in a container, we'll remain the handle as nullptr.
	//             Be Sure to Detect Nullptrs before Using Containers.
	auto A = GetArf2( ArfBuf );
	before = A -> before();
	special_hint = A -> special_hint();

	/* DeltaNodes in Layer 1 */ {
		auto d = A -> dts_layer1();
		uint16_t dsize = d -> size();

		Arf::d1 = new ArDeltaNode[dsize];
		for(uint16_t i = 0; i < dsize; i++) {
			auto dn = d -> Get(i);
			auto& dnobj = Arf::d1[i];

			dnobj.base = (dn & 0xffffffff) * 0.00002;
			dnobj.ratio = (dn >> 50) * 0.00001f;
			dnobj.init_ms = ((dn>>32) & 0x3ffff) * 2;
		}
	}
	
	/* DeltaNodes in Layer 2 */ {
		auto d = A -> dts_layer2();
		uint16_t dsize = d -> size();

		Arf::d2 = new ArDeltaNode[dsize];
		for(uint16_t i = 0; i < dsize; i++) {
			auto dn = d -> Get(i);
			auto& dnobj = Arf::d2[i];

			dnobj.base = (dn & 0xffffffff) * 0.00002;
			dnobj.ratio = (dn >> 50) * 0.00001f;
			dnobj.init_ms = ((dn>>32) & 0x3ffff) * 2;
		}
	}

	/* Group Index */ {
		auto idx = A -> index();
		uint16_t idx_size = idx -> size();

		Arf::index = new ArIndex[idx_size];
		for(uint16_t i = 0; i < idx_size; i++) {
			auto& idxobj = Arf::index[i];

			/* Wish Index of Current Group */ {
				auto widxfb = idx -> Get(i) -> widx();
				uint16_t widx_size = widxfb -> size();

				if(widx_size) {
					auto widx = new uint16_t[widx_size];
					for(uint16_t wi = 0; wi < widx_size; wi++) {
						widx[wi] = widxfb -> Get(wi);
					}
					idxobj.widx = widx;
				}
			}

			/* Hint Index of Current Group */ {
				auto hidxfb = idx -> Get(i) -> hidx();
				uint16_t hidx_size = hidxfb -> size();

				if(hidx_size) {
					auto hidx = new uint16_t[hidx_size];
					for(uint16_t hi = 0; hi < hidx_size; hi++) {
						hidx[hi] = hidxfb -> Get(hi);
					}
					idxobj.hidx = hidx;
				}
			}

			// Echo Index of Current Group (NYI)
		}
	}

	/* WishGroups */ {
		auto wish = A -> wish();
		uint16_t wish_size = wish -> size();

		if(wish_size) {
			Arf::wish = new ArWishGroup[wish_size];
			for(uint16_t i = 0; i < wish_size; i++) {
				auto w = wish -> Get(i);
				auto& wobj = Arf::wish[i];

				/* Scalars */ {
					auto winfo = w -> info();
					wobj.mvb = (winfo & 0x1fff) * 1024.0f;
					wobj.ofl2 = (bool)((winfo>>13) & 0b1);
				}

				/* PosNodes */ {
					auto nodesfb = w -> nodes();
					uint8_t node_size = nodesfb -> size();

					if(node_size) {
						auto nodes = new ArPosNode[node_size];
						for(uint8_t ni = 0; ni < node_size; ni++) {

							auto p = nodesfb -> Get(ni);
							auto& pobj = nodes[ni];

							// node.x = ((p>>31) & 0x1fff) * 0.0078125f - 16.0f
							// node.y = ((p>>19) & 0xfff) * 0.0078125f - 8.0f
							pobj.ms = p & 0x7ffff;
							pobj.c_dx = ((p>>31) & 0x1fff) * 0.87890625f - 2700.0f;
							pobj.c_dy = ((p>>19) & 0xfff) * 0.87890625f - 1350.0f;
							pobj.easetype = ((p>>44) & 0b11);

							float ci = (p>>55) * 0.001956947162f; {
								if(ci < 0.0f)		ci = 0.0f;
								else if(ci > 1.0f)	ci = 1.0f;
							}

							float ce = ((p>>46) & 0x1ff) * 0.001956947162f; {
								if(ce < 0.0f)		ce = 0.0f;
								else if(ce > 1.0f)	ce = 1.0f;
							}

							// Process Easetype
							uint16_t dnm;
							if(ci > ce) {   // OutQuad
								pobj.ci = ce;   // Reversed
								pobj.ce = ci;   // Reversed
								pobj.easetype = 4;

								if( (ce != 0.0f) || (ci != 1.0f) ) {   // Reversed
									ce = 1.0f - ce;
									ce = 1.0f - ce*ce;
									pobj.x_fci = pobj.y_fci = ce;   // Reversed

									ci = 1.0f - ci;
									ci = 1.0f - ci*ci;
									pobj.x_fce = pobj.y_fce = ci;   // Reversed

									dnm = (uint16_t)( (ci-ce) * 8192.0f );
									pobj.x_dnm = pobj.y_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);
								}
							}
							else if(pobj.easetype) {
								pobj.ci = ci;
								pobj.ce = ce;

								if( (ci != 0.0f) || (ce != 1.0f) ) switch(pobj.easetype) {
									case 1:   /*  x -> ESIN   y -> ECOS  */
										pobj.x_fci = ESIN[ (uint16_t)(1000 * ci) ];
										pobj.x_fce = ESIN[ (uint16_t)(1000 * ce) ];

										dnm = (uint16_t)( (pobj.x_fce - pobj.x_fci) * 8192.0f );
										pobj.x_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);

										pobj.y_fci = ECOS[ (uint16_t)(1000 * ci) ];
										pobj.y_fce = ECOS[ (uint16_t)(1000 * ce) ];

										dnm = (uint16_t)( (pobj.y_fce - pobj.y_fci) * 8192.0f );
										pobj.y_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);

										break;
									case 2:   /*  x -> ECOS   y -> ESIN  */
										pobj.x_fci = ECOS[ (uint16_t)(1000 * ci) ];
										pobj.x_fce = ECOS[ (uint16_t)(1000 * ce) ];

										dnm = (uint16_t)( (pobj.x_fce - pobj.x_fci) * 8192.0f );
										pobj.x_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);

										pobj.y_fci = ESIN[ (uint16_t)(1000 * ci) ];
										pobj.y_fce = ESIN[ (uint16_t)(1000 * ce) ];

										dnm = (uint16_t)( (pobj.y_fce - pobj.y_fci) * 8192.0f );
										pobj.y_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);

										break;
									case 3:   // InQuad
										pobj.x_fci = pobj.y_fci = (ci * ci);
										pobj.x_fce = pobj.y_fce = (ce * ce);

										dnm = (uint16_t)( (ce-ci) * 8192.0f );
										pobj.x_dnm = pobj.y_dnm = (float)(RCP[ (dnm>1) ? (dnm-1) : 0 ] * 8192.0);

										break;
									default:;
								}
							}
						}
						wobj.nodes = nodes;
					}
				}

				/* WishChilds */ {
					auto childsfb = w -> childs();
					uint16_t child_size = childsfb -> size();

					if(child_size) {
						auto childs = new ArWishChild[child_size];
						for(uint16_t ci = 0; ci < child_size; ci++) {
							auto c = childsfb -> Get(ci);
							auto& cobj = childs[ci];

							auto an = c -> anodes();
							uint8_t an_size = an -> size();

							auto anodes = new ArAngleNode[an_size];
							for(uint8_t ai = 0; ai < an_size; ai++) {
								auto a = an -> Get(ai);
								auto& aobj = anodes[ai];

								aobj.ms = (a & 0x3ffff) * 2;
								aobj.degree = (a>>20) - 1800;
								aobj.easetype = ((a>>18) & 0b11);
							}

							cobj.dt = ( c->dt() ) * 0.00002f;
							cobj.anodes = anodes;
						}
						wobj.childs = childs;
					}
				}
			}
		}
	}

	/* Hints */
	auto hint = A -> hint();
	uint16_t hint_size = hint -> size();
	if(hint_size) {
		uint8_t init_status = lua_toboolean(L, 2) ? HINT_AUTO : HINT_NONJUDGED;
		Arf::hint = new ArHint[hint_size];

		for(uint16_t i = 0; i < hint_size; i++) {
			auto h = hint -> Get(i);
			auto& hobj = Arf::hint[i];

			// hint.x = (h & 0x1fff) * 0.0078125f - 16.0f
			// hint.y = ((h>>13) & 0xfff) * 0.0078125f - 8.0f
			hobj.ms = (h>>25) & 0x7ffff;
			hobj.c_dx = (h & 0x1fff) * 0.87890625f - 2700.0f;
			hobj.c_dy = ((h>>13) & 0xfff) * 0.87890625f - 1350.0f;
			hobj.status = init_status;
		}
	}


	// Do Returns
	lua_checkstack(L, 4);
	lua_pushnumber( L, before );				lua_pushnumber( L, hint_size );
	lua_pushnumber( L, A->wgo_required() );	lua_pushnumber( L, A->hgo_required() );
	return 4;
}


// Judge Functions
static int SetIDelta(lua_State *L) {
	constexpr uint8_t JR_REV = 100 - JUDGE_RANGE;
	const int8_t _id = luaL_checknumber(L, 1);
	if( _id>=-JR_REV && _id<=JR_REV )
	{ idelta = _id;		mindt = -JUDGE_RANGE + _id;		maxdt = JUDGE_RANGE + _id; }
	else
	{ idelta = 0;		mindt = -JUDGE_RANGE;			maxdt = JUDGE_RANGE; }
	return 0;
}
inline bool has_touch_near(const ArHint& hint, const ab* valid_fingers, const uint8_t vf_count) {

	// Unpack the Hint
	const float hl = 731.25f + (hint.c_dx * rotcos - hint.c_dy * rotsin) * xscale + xdelta;   // 900 - 112.5 * 1.5
	const float hd = 371.25f + (hint.c_dx * rotsin + hint.c_dy * rotcos) * yscale + ydelta;   // 540 - 112.5 * 1.5
	const float hr = hl + 337.5f, hu = hd + 337.5f;

	// Detect Touches
	for( uint8_t i=0; i<vf_count; i++ ) {
		const float x = valid_fingers[i].a;
		if( (x>=hl) && x<=hr ) {
			const float y = valid_fingers[i].b;
			if( (y>=hd) && y<=hu ) return true;
		}
	}

	// Process Detection Failure
	return false;
}
inline bool is_safe_to_anmitsu(ArHint& hint) {

	// Preparations
	if(!allow_anmitsu) return false;
	const float hl = hint.c_dx - 337.5f, hr = hint.c_dx + 337.5f;
	const float hd = hint.c_dy - 337.5f, hu = hint.c_dy + 337.5f;

	// Iterate blocked blocks
	const uint16_t bs = blocked.size();
	for( uint16_t i=0; i<bs; i++ ) {
		const float x = blocked[i] -> c_dx;
		if( (x>hl) && x<hr ) {
			const float y = blocked[i] -> c_dy;
			if( (y>hu) && y<hd ) return false;
		}
	}

	// Register "Safe to Anmitsu" Hints
	blocked.emplace_back(&hint);
	return true;
}
static int JudgeArf(lua_State* L) {
	// JudgeArf(mstime, table_touch)
	//       -> hint_hit, hint_early, hint_late, special_hint_judged
	if( !before ) return 0;

	// State Variables
	bool any_pressed = false, any_released = false, special_hint_judged = false;
	lua_Number hint_hit = 0, hint_early = 0, hint_late = 0;
	const uint32_t mstime = luaL_checknumber(L, 1);

	// Prepare the Iteration Scale
	uint16_t current_group = 0; {
		const uint16_t location_group = mstime >> 9 ;   // floordiv 512
		current_group = (location_group > 1) ? (location_group - 1) : 0 ;
	}
	uint16_t beyond_group = current_group + 3; {
		const uint16_t group_count = COUNT(Arf::index);
		beyond_group = (beyond_group < group_count) ? beyond_group : group_count ;
	}

	// Unpack Touches
	ab vf[10];
	uint8_t vfcount = 0;
	for( uint8_t i=0; i<10; i++ ) {
		lua_rawgeti(L, 2, i+1);
		const v3 f = dmScript::CheckVector3(L, -1);
		lua_pop(L, 1);

		switch( (uint8_t)f->getZ() ) {
			case 1:
				any_pressed = true;   // No break here
			case 2:
				vf[vfcount].a = f->getX();
				vf[vfcount].b = f->getY();
				vfcount++;
				break;
			case 3:
				any_released = true;
				break;
			default:;
		}
	}
	{ if(any_released) blocked.clear(); }

	// Start Judging
	if(any_pressed) {
		uint32_t min_time = 0;
		for( ; current_group < beyond_group; current_group++ ) {
			const auto hint_ids = Arf::index[current_group].hidx;	if(!hint_ids) continue;
			const uint8_t hint_count = COUNT(hint_ids);

			for( uint8_t i=0; i<hint_count; i++ ) {
				const auto current_hint_id = hint_ids[i];
				auto& current_hint = Arf::hint[current_hint_id];

				// Jump Judging based on the Sort Assumption
				const int32_t dt = mstime - current_hint.ms;
				if(dt < -510) break;
				if(dt > 470) continue;

				// Hint Status Manipulation
				const bool htn = has_touch_near(current_hint, vf, vfcount);
				switch(current_hint.status) {
					case HINT_NONJUDGED:   // No break here
					case HINT_NONJUDGED_LIT:
						if(htn) {
							if( (dt >= -100) && dt <= 100 ) {
								const bool ista = is_safe_to_anmitsu(current_hint);

								if(!min_time) {

									// Data Update
									min_time = current_hint.ms;
									if(current_hint_id == special_hint) {
										special_hint_judged = (bool)special_hint;
									}
									current_hint.status = HINT_JUDGED_LIT;
									current_hint.judged_ms = mstime;

									// Classify
									if(dt < mindt) {
										current_hint.elstatus = HINT_EARLY;
										hint_early++;
									}
									else if(dt <= maxdt) hint_hit++;
									else {
										current_hint.elstatus = HINT_LATE;
										hint_late++;
									}

								}
								else if( (current_hint.ms == min_time) || ista ) {

									// Data Update
									if(current_hint_id == special_hint) {
										special_hint_judged = (bool)special_hint;
									}
									current_hint.status = HINT_JUDGED_LIT;
									current_hint.judged_ms = mstime;

									// Classify
									if(dt < mindt) {
										current_hint.elstatus = HINT_EARLY;
										hint_early++;
									}
									else if(dt <= maxdt) hint_hit++;
									else {
										current_hint.elstatus = HINT_LATE;
										hint_late++;
									}

								}
								else current_hint.status = HINT_NONJUDGED_LIT;

							}
							else current_hint.status = HINT_NONJUDGED_LIT;
						}
						else current_hint.status = HINT_NONJUDGED;
					case HINT_JUDGED_LIT:
						if(!htn) current_hint.status = HINT_JUDGED;
						break;
					default:;
				}
			}
		}
	}
	else for( ; current_group < beyond_group; current_group++ ) {
		const auto hint_ids = Arf::index[current_group].hidx;	if(!hint_ids) continue;
		const uint8_t hint_count = COUNT(hint_ids);

		for( uint8_t i=0; i<hint_count; i++ ) {
			const auto current_hint_id = hint_ids[i];
			auto& current_hint = Arf::hint[current_hint_id];

			// Jump Judging based on the Sort Assumption
			const int32_t dt = mstime - current_hint.ms;
			if(dt < -510) break;
			if(dt > 470) continue;

			// Hint Status Manipulation
			const bool htn = has_touch_near(current_hint, vf, vfcount);
			switch(current_hint.status) {
				case HINT_NONJUDGED:   // No break here
				case HINT_NONJUDGED_LIT:
					if(htn) current_hint.status = HINT_NONJUDGED_LIT;
					else current_hint.status = HINT_NONJUDGED;
					break;
				case HINT_JUDGED_LIT:
					if(!htn) current_hint.status = HINT_JUDGED;
					break;
				default:;
			}
		}
	}

	// Do Returns
	lua_checkstack(L, 4);
	lua_pushnumber(L, hint_hit);	lua_pushnumber(L, hint_early);		lua_pushnumber(L, hint_late);
	lua_pushboolean(L, special_hint_judged);
	return 4;
}


// Update Functions
static const dmVMath::Quat D73(0.0f, 0.0f, 0.594822786751341f, 0.803856860617217f);
inline uint16_t mod_degree(uint64_t deg) {
	// Actually while(xxx)···
	do {
		if(deg > 7200)  deg -= (deg > 14400) ? 14400 : 7200 ;
		else			deg -= 3600;
	}
	while(deg > 3600);
	return deg;
}
inline void GetSINCOS(const double degree) {
	if( degree >= 0 ) {
		auto deg = (uint64_t)(degree*10.0);			deg = (deg>3600) ? mod_degree(deg) : deg ;
		if(deg > 1800) {
			if(deg > 2700)	{ SIN = -DSIN[3600-deg];	COS = DCOS[3600-deg];  }
			else 			{ SIN = -DSIN[deg-1800];	COS = -DCOS[deg-1800]; }
		}
		else {
			if(deg > 900)	{ SIN = DSIN[1800-deg];		COS = -DCOS[1800-deg]; }
			else			{ SIN = DSIN[deg]; 			COS = DCOS[deg];	   }
		}
	}
	else {   // sin(-x) = -sin(x), cos(-x) = cos(x)
		auto deg = (uint64_t)(-degree*10.0);		deg = (deg>3600) ? mod_degree(deg) : deg ;
		if(deg > 1800) {
			if(deg > 2700)	{ SIN = DSIN[3600-deg];		COS = DCOS[3600-deg];  }
			else 			{ SIN = DSIN[deg-1800];		COS = -DCOS[deg-1800]; }
		}
		else {
			if(deg > 900)	{ SIN = -DSIN[1800-deg];	COS = -DCOS[1800-deg]; }
			else			{ SIN = -DSIN[deg]; 		COS = DCOS[deg];	   }
		}
	}
}
inline dmVMath::Quat GetZQuad(const double degree) {
	GetSINCOS( degree * 0.5 );
	return dmVMath::Quat(0.0f, 0.0f, SIN, COS);
}
static int UpdateArf(lua_State* L) {
	// UpdateArf(mstime, table_wgo/hgo/agol/agor/wtint/htint/atint)
	//        -> hint_lost, wgo/hgo/ago_used
	if( !before ) return 0;

	/* Prepare Returns & Process msTime */
	// Z Distribution: Wish{0,0.05,0.1,0.15}  Hint(-0.06,0)
	auto mstime = (uint32_t)luaL_checknumber(L, 1); {
		if(mstime < 2)											mstime = 2;
		else if( (mstime == last_ms) || mstime >= before )		return 0;
	}
	const uint16_t location_group = mstime >> 9 ;   // floordiv 512

	uint16_t hint_lost = 0;
	uint8_t wgo_used = 0, hgo_used = 0, ago_used = 0;


	/* Check DTimes */
	// We use the last_ms cache to condition the fallback iteration this time.
	double dt1 = 0.0; {

		// Tail Judging
		// Prototypia guarantees that init_ms of the 1st DetlaNode of each layer equals to 0
		const uint16_t dt_tail = COUNT(Arf::d1) - 1;
		const auto& node_l = Arf::d1[dt_tail];
		if( mstime >= node_l.init_ms )
			dt1 = node_l.base + (mstime - node_l.init_ms) * node_l.ratio;

		// Iterating When Tail Judging Fails
		else {
			if( mstime < last_ms )   // Regression
				while( (dt_p1 > 0) && mstime < Arf::d1[dt_p1].init_ms ) dt_p1--;

			for( ; dt_p1 < dt_tail; dt_p1++ ) {
				const auto& node_n = Arf::d1[dt_p1 + 1];
				if( mstime < node_n.init_ms ) {   // Actually  if( mstime >= node_n.init_ms ) continue;
					const auto& node_c = Arf::d1[dt_p1];
					if( node_c.ratio > node_n.ratio )
						dt1 = node_c.base - (mstime - node_c.init_ms) * node_c.ratio;
					else
						dt1 = node_c.base + (mstime - node_c.init_ms) * node_c.ratio;
				}
			}
		}
	}

	double dt2 = 0.0; {

		// Tail Judging
		const uint16_t dt_tail = COUNT(Arf::d2) - 1;
		const auto& node_l = Arf::d2[dt_tail];
		if( mstime >= node_l.init_ms )
			dt2 = node_l.base + (mstime - node_l.init_ms) * node_l.ratio;

		// Iterating When Tail Judging Fails
		else {
			if( mstime < last_ms )   // Regression
				while( (dt_p2 > 0) && mstime < Arf::d2[dt_p2].init_ms ) dt_p2--;

			for( ; dt_p2 < dt_tail; dt_p2++ ) {
				const auto& node_n = Arf::d2[dt_p2 + 1];
				if( mstime < node_n.init_ms ) {   // Actually  if( mstime >= node_n.init_ms ) continue;
					const auto& node_c = Arf::d2[dt_p2];
					if( node_c.ratio > node_n.ratio )
						dt2 = node_c.base - (mstime - node_c.init_ms) * node_c.ratio;
					else
						dt2 = node_c.base + (mstime - node_c.init_ms) * node_c.ratio;
				}
			}
		}
	}


	/* Process Wish(es) */ {
		const auto wish_ids = Arf::index[location_group].widx;
		if(wish_ids) {

			// Wish Iteration
			const uint16_t wish_count = COUNT(wish_ids);
			for( uint16_t wi=0; wi<wish_count; wi++ ) {
				auto& wish_c = Arf::wish[ wish_ids[wi] ];

				/* Node Iteration */
				// Prototypia guarantees that each Wish has at least 2 PosNodes.
				const auto nodes = wish_c.nodes;
				float node_x, node_y; {

					// Jump Judging
					if(mstime < nodes[0].ms) continue;   // Wish For loop
					const uint8_t nodes_tail = COUNT(nodes) - 1;
					if(mstime >= nodes[nodes_tail].ms) continue;   // Wish For loop

					// Regression
					if(mstime < last_ms) {
						while( (wish_c.np > 0) && mstime < nodes[ wish_c.np ].ms ) wish_c.np--;
					}

					// Pos Acquisition
					while(wish_c.np < nodes_tail) {   // [)

						/* Interval Acquisition */
						const auto& node_c = nodes[ wish_c.np ];
						const auto& node_n = nodes[ wish_c.np + 1 ];
						if(mstime >= node_n.ms) {
							wish_c.np++;
							continue;   // Node While loop
						}

						/* Ratio Acquisition */
						float ratio; {
							uint32_t difms = node_n.ms - node_c.ms;
							if(!difms)				ratio = 0.0f;
							else if(difms<8193)		ratio = (mstime - node_c.ms) * RCP[ difms-1 ];
							else					ratio = (mstime - node_c.ms) / (float)difms;
						}

						/* Easing */
						if(node_c.easetype) {

							// Get fr
							float xfr, yfr;
							xfr = yfr = ( node_c.ci + (node_c.ce - node_c.ci) * ratio );
							switch(node_c.easetype) {
								case 1:   /*  x -> ESIN   y -> ECOS  */
									xfr = ESIN[ (uint16_t)(1000 * ratio) ];
									yfr = ECOS[ (uint16_t)(1000 * ratio) ];
									break;
								case 2:   /*  x -> ECOS   y -> ESIN  */
									xfr = ECOS[ (uint16_t)(1000 * ratio) ];
									yfr = ESIN[ (uint16_t)(1000 * ratio) ];
									break;
								case 3:   // InQuad
									xfr = yfr = (ratio * ratio);
									break;
								case 4:   // OutQuad
									ratio = 1.0f - ratio;
									xfr = yfr = (1.0f - ratio * ratio);
									break;
								default:;
							}

							// Apply the Formula
							// P = ( (fce - fr) * p1 + (fr - fci) * p2 ) * p_dnm
							// P = p1 + fr * (p2 - p1)   when fce=1, fci = 0
							if( (node_c.ci != 0.0f) || (node_c.ce != 1.0f) ) {
								node_x = (node_c.x_fce - xfr) * node_c.c_dx + (xfr - node_c.x_fci) * node_n.c_dx;
								node_x *= node_c.x_dnm;
								node_y = (node_c.y_fce - yfr) * node_c.c_dy + (yfr - node_c.y_fci) * node_n.c_dy;
								node_y *= node_c.y_dnm;
							}
							else {
								node_x = node_n.c_dx - node_c.c_dx;   // As dx
								node_x = node_c.c_dx + node_x * xfr;
								node_y = node_n.c_dy - node_c.c_dy;   // As dy
								node_y = node_c.c_dy + node_y * yfr;
							}
						}
						else {
							node_x = node_n.c_dx - node_c.c_dx;   // As dx
							node_x = node_c.c_dx + node_x * ratio;
							node_y = node_n.c_dy - node_c.c_dy;   // As dy
							node_y = node_c.c_dy + node_y * ratio;
						}

						break;   // Node While loop
					}
				}

				/* Self Param Setting */ {
					const float x = 900.f + (node_x * rotcos - node_y * rotsin) * xscale + xdelta;
					if( (x>=66.0f) && x<=1734.0f ) {   // X trim
						const float y = 540.f + (node_x * rotsin + node_y * rotcos) * yscale + ydelta;
						if( (y>=66.0f) && y<=1014.0f ) {   // Y trim
							const uint32_t k = (uint32_t)(x * 1009.0f) + (uint32_t)(y * 1013.0f);
							if( last_wgo.count(k) ) {   // Overlap trim
								uint8_t lwidx_lua = last_wgo[k];

								// tint.w Setting
								lua_pushnumber(L, 1.0);
								lua_rawseti(L, T_WTINT, lwidx_lua);

								// Scale Setting
								lua_rawgeti(L, T_WGO, lwidx_lua);
								GO WGO = dmScript::CheckGOInstance(L, -1);
								SetScale(WGO, 0.637f);
								lua_pop(L, 1);
							}
							else {   // Pass
								wgo_used++;   // This functions as the wgo_used result and lua index simultaneously

								// tint.w Setting
								float tintw = mstime - nodes[0].ms;
								tintw = (tintw > 237) ? 1.0f : tintw * 0.0042194092827f;   // As  ms_passed / 237.0f
								lua_pushnumber(L, tintw);
								lua_rawseti(L, T_WTINT, wgo_used);

								// Scale Setting
								lua_rawgeti(L, T_WGO, wgo_used);
								GO WGO = dmScript::CheckGOInstance(L, -1);
								SetScale( WGO, 0.637f * tintw );
								lua_pop(L, 1);
							}
						}
					}
				}

				/* WishChild Iteration */
				const auto childs = wish_c.childs;
				if(childs) {   // current_dt < dt <= current_dt + mvb
					const double current_dt = wish_c.ofl2 ? dt2 : dt1;

					// Jump Judging
					if(childs[0].dt - current_dt > wish_c.mvb) continue;   // Wish For Loop
					const uint16_t child_count = COUNT(childs);
					if(current_dt >= childs[ child_count-1 ].dt) continue;   // Wish For Loop

					// Regression
					// Child Progress: index_of_1st_child_disappeared, or -1
					while( (wish_c.cp > -1) && current_dt < childs[ wish_c.cp ].dt ) wish_c.cp--;

					// Process Childs
					// We use an internal iterator, and sync the iteration progress to wish_c.cp
					for(auto ci = (uint16_t)(wish_c.cp+1); ci < child_count; ci++) {
						auto& child_c = childs[ci];   // Non-Const

						// "Too Late" Judging
						if(current_dt >= child_c.dt) {
							wish_c.cp = ci;
							continue;   // Child For Loop
						}

						// "Too Early" Judging
						const double radius = child_c.dt - current_dt;   /* Radius Acquisition */
						if(radius > wish_c.mvb) break;   // Child For Loop

						/* Angle Iteration */
						// Prototypia guarantees that each WishChild has at least 1 AngleNode.
						double angle = 90.0; {
							const auto anodes = child_c.anodes;
							const uint8_t anodes_tail = COUNT(anodes) - 1;

							if(mstime >= anodes[anodes_tail].ms) {   // Tail Judging
								angle = anodes[anodes_tail].degree;
							}
							else if(mstime <= anodes[0].ms) {   // Head Judging
								angle = anodes[0].degree;
							}
							else {   // Iteration when Needed

								if(mstime < last_ms) {   // Regression
									while( (child_c.ap > 0) && mstime < anodes[ child_c.ap ].ms ) child_c.ap--;
								}

								while(child_c.ap < anodes_tail) {   // Angle Acquisition

									/* Interval Acquisition */
									const auto& anode_c = anodes[ child_c.ap ];
									const auto& anode_n = anodes[ child_c.ap + 1 ];
									if(mstime >= anode_n.ms) {
										child_c.ap++;
										continue;   // Angle While loop
									}

									/* Angle Acquisition */
									if(anode_c.easetype) {
										float ratio; {
											uint32_t difms = anode_n.ms - anode_c.ms;
											if(!difms)				ratio = 0.0f;
											else if(difms<8193)		ratio = (mstime - anode_c.ms) * RCP[ difms-1 ];
											else					ratio = (mstime - anode_c.ms) / (float)difms;
										}

										/* Easing */
										switch(anode_c.easetype) {
											case 1:   // LINEAR
												break;
											case 2:   // INQUAD
												ratio *= ratio;
												break;
											case 3:   // OUTQUAD
												ratio = 1.0f - ratio;
												ratio = 1.0f - ratio * ratio;
												break;
											default:;
										}

										angle = anode_c.degree + (anode_n.degree - anode_c.degree) * ratio;
									}
									else angle = anode_c.degree;
									break;   // Angle While loop
								}
							}
						}

						/* Child Param Setting */ {
							GetSINCOS(angle);
							const float child_x = node_x + radius * COS;
							const float child_y = node_y + radius * SIN;

							const float x = 900.f + (child_x * rotcos - child_y * rotsin) * xscale + xdelta;
							if( (x>=66.0f) && x<=1734.0f ) {   // X trim
								const float y = 540.f + (child_x * rotsin + child_y * rotcos) * yscale + ydelta;
								if( (y>=66.0f) && y<=1014.0f ) {   // Y trim
									const uint32_t k = (uint32_t)(x * 1009.0f) + (uint32_t)(y * 1013.0f);
									if( last_wgo.count(k) ) {   // Overlap trim
										uint8_t lwidx_lua = last_wgo[k];

										// tint.w Setting
										lua_pushnumber(L, 1.0);
										lua_rawseti(L, T_WTINT, lwidx_lua);

										// Scale Setting
										lua_rawgeti(L, T_WGO, lwidx_lua);
										GO WGO = dmScript::CheckGOInstance(L, -1);
										SetScale(WGO, 0.637f);
										lua_pop(L, 1);
									}
									else {   // Pass
										// This functions as the wgo_used result and lua index simultaneously
										wgo_used++;

										// tint.w Setting
										// As (wish_c.mvb - radius) / (wish_c.mvb * 0.237f)
										float tintw = 8192 * (wish_c.mvb - radius) *
													  RCP[ (uint16_t)(wish_c.mvb * 1941.504f) ];
										tintw = (tintw>1.0f) ? 1.0f : tintw;
										lua_pushnumber(L, tintw);
										lua_rawseti(L, T_WTINT, wgo_used);

										// Scale Setting
										lua_rawgeti(L, T_WGO, wgo_used);
										GO WGO = dmScript::CheckGOInstance(L, -1);
										SetScale( WGO, 0.637f * tintw );
										lua_pop(L, 1);
									}
								}
							}
						}
					}
				}
				/* EchoChild Iteration */   // NYI
			}
		}
	}


	/* Process Hint(s) */ {

		// Prepare the Iteration Scale
		uint16_t current_group = (location_group > 1) ? (location_group - 1) : 0 ;
		uint16_t beyond_group = current_group + 3; {
			const uint16_t group_count = COUNT(Arf::index);
			beyond_group = (beyond_group < group_count) ? beyond_group : group_count ;
		}

		// Group Iteration
		for( ; current_group < beyond_group; current_group++ ) {
			const auto hint_ids = Arf::index[current_group].hidx;	if(!hint_ids) continue;
			const uint8_t hint_count = COUNT(hint_ids);

			// Element Iteration
			for(uint8_t i=0; i<hint_count; i++) {
				const auto hint_cid = hint_ids[i];
				auto& hint_c = Arf::hint[hint_cid];

				/* Calculate Dt & Jump Judging based on the Sort Assumption */
				const auto dt = (int32_t)mstime - (int32_t)hint_c.ms;
				const auto jdt = (int32_t)mstime - (int32_t)hint_c.judged_ms;
				if (dt > 470) continue;
				if (dt < -510) break;

				/* Do Hint Sweeping */
				if( dt>100 && (hint_c.status==HINT_NONJUDGED || hint_c.status==HINT_NONJUDGED_LIT) ) {
					hint_c.status = HINT_SWEEPED;
					hint_lost++;
				}

				/* Calculate the Real Position & Prepare Rennder Elements */
				using namespace dmScript;
				const float x = 900.f + (hint_c.c_dx * rotcos - hint_c.c_dy * rotsin) * xscale + xdelta;
				const float y = 540.f + (hint_c.c_dx * rotsin + hint_c.c_dy * rotcos) * yscale + ydelta;
				lua_rawgeti(L, T_HGO, hgo_used+1);		const GO hgo = CheckGOInstance(L, -1);
				lua_rawgeti(L, T_HTINT, hgo_used+1);	const v4 htint = CheckVector4(L, -1);
				lua_rawgeti(L, T_AGO_L, ago_used+1);	const GO agol = CheckGOInstance(L, -1);
				lua_rawgeti(L, T_AGO_R, ago_used+1);	const GO agor = CheckGOInstance(L, -1);
				lua_rawgeti(L, T_ATINT, ago_used+1);	const v4 atint = CheckVector4(L, -1);
				lua_pop(L, 5);

				/* Pass Hint & Anim Params */
				// Specify all tint.w as 1 in the initialization
				if( dt < -370 ) {
					SetPosition( hgo, p3(x, y, -(0.05f + dt*0.00001f)) );
					const float color = 0.1337f + (float)(0.07 * (510+dt) / 140.0);
					htint -> setX(color).setY(color).setZ(color);
					hgo_used++;
				}
				else if( dt <= 370 ) switch(hint_c.status) {
					case HINT_NONJUDGED:
						htint -> setX(0.2037f).setY(0.2037f).setZ(0.2037f);
						SetPosition( hgo, p3(x, y, -0.04f) );
						hgo_used++;
						break;
					case HINT_NONJUDGED_LIT:
						htint -> setX(0.3737f).setY(0.3737f).setZ(0.3737f);
						SetPosition( hgo, p3(x, y, -0.04f) );
						hgo_used++;
						break;
					case HINT_JUDGED_LIT:   // No break here
						SetPosition( hgo, p3(x, y, -0.01f) );
						switch(hint_c.elstatus) {
							case HINT_HIT:
								{
									if(daymode)		htint -> setX(H_HIT_R).setY(H_HIT_G).setZ(H_HIT_B);
									else			htint -> setX(H_HIT_C).setY(H_HIT_C).setZ(H_HIT_C);
								}
								break;
							case HINT_EARLY:
								htint -> setX(H_EARLY_R).setY(H_EARLY_G).setZ(H_EARLY_B);
								break;
							case HINT_LATE:
								htint -> setX(H_LATE_R).setY(H_LATE_G).setZ(H_LATE_B);
								break;
							default:;
						}
						hgo_used++;
					case HINT_JUDGED:
						if(jdt <= 370) {
							// Anim Settings
							ago_used++;

							/* Position */ {
								const p3 agopos(x, y, -jdt * 0.00001f);
								SetPosition(agol, agopos);
								SetPosition(agor, agopos);
							}

							/* tint.w */
							if(jdt < 73) {
								float tintw = jdt * 0.01f;
								tintw = 0.637f * tintw * (2.0f - tintw);
								atint -> setW( 0.17199f + tintw );
							}
							else {
								float tintw = (jdt - 73) * 0.003367003367003367f;   // 1/297 = 0.003367···
								tintw = 0.637f * tintw * (2.0f - tintw);
								atint -> setW(0.637f - tintw);
							}

							/* tint.xyz */
							switch(hint_c.elstatus) {
								case HINT_HIT:
									{
										if(daymode)		atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
										else			atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
									}
									break;
								case HINT_EARLY:
									atint -> setX(A_EARLY_R).setY(A_EARLY_G).setZ(A_EARLY_B);
									break;
								case HINT_LATE:
									atint -> setX(A_LATE_R).setY(A_LATE_G).setZ(A_LATE_B);
									break;
								default:;
							}

							/* Rotation & Scale */ {
								double anim_calculate = 0.0;

								if(jdt <= 193) {
									anim_calculate = jdt * 0.005181347150259;   // 1/193
									SetRotation( agol, GetZQuad(45.0 + 28.0*anim_calculate) );
									anim_calculate = anim_calculate * (2.0 - anim_calculate);
									SetScale( agol, 1.0 + 0.637 * anim_calculate );
								}
								else {
									SetRotation(agol, D73);
									SetScale(agol, 1.637f);
								}

								anim_calculate = jdt * 0.002702702702702;   // 1/370
								anim_calculate = anim_calculate * (2.0 - anim_calculate);
								SetRotation( agor, GetZQuad(45.0 - 8.0 * anim_calculate) );
								SetScale( agor, 1.0 + 0.637 * anim_calculate );
							}
						}
						break;
					case HINT_SWEEPED:
						{
							SetPosition( hgo, p3(x, y, -0.02f + dt*0.00001f) );
							float color = 0.437f - dt*0.00037f;			htint -> setX(color);
							color *= 0.51f;								htint -> setY(color).setZ(color);
							hgo_used++;
						}
						break;
					case HINT_AUTO:

						// Hint
						{
							if(dt < 0) {
								htint -> setX(0.2037f).setY(0.2037f).setZ(0.2037f);
								SetPosition( hgo, p3(x, y, -0.04f) );
								hgo_used++;
							}
							else if(dt < 101) {
								SetPosition( hgo, p3(x, y, -0.01f) );
								if(daymode)		htint -> setX(H_HIT_R).setY(H_HIT_G).setZ(H_HIT_B);
								else 			htint -> setX(H_HIT_C).setY(H_HIT_C).setZ(H_HIT_C);
								hgo_used++;
							}
						}

						// Anim
						if(dt >= 0) {
							ago_used++;

							/* Position */ {
								const p3 agopos(x, y, -dt * 0.00001f);
								SetPosition(agol, agopos);
								SetPosition(agor, agopos);
							}

							/* tint.w */
							if(dt < 73) {
								float tintw = dt * 0.01f;
								tintw = 0.637f * tintw * (2.0f - tintw);
								atint -> setW( 0.17199f + tintw );
							}
							else {
								float tintw = (dt - 73) * 0.003367003367003367f;   // 1/297 = 0.003367···
								tintw = 0.637f * tintw * (2.0f - tintw);
								atint -> setW(0.637f - tintw);
							}

							/* tint.xyz */ {
								if(daymode)		atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
								else			atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
							}

							/* Rotation & Scale */
							{
								double anim_calculate = 0.0;

								if(dt <= 193) {
									anim_calculate = dt * 0.005181347150259;   // 1/193
									SetRotation( agol, GetZQuad(45.0 + 28.0*anim_calculate) );
									anim_calculate = anim_calculate * (2.0 - anim_calculate);
									SetScale( agol, 1.0 + 0.637 * anim_calculate );
								}
								else {
									SetRotation(agol, D73);
									SetScale(agol, 1.637f);
								}

								anim_calculate = dt * 0.002702702702702;   // 1/370
								anim_calculate = anim_calculate * (2.0 - anim_calculate);
								SetRotation( agor, GetZQuad(45.0 - 8.0*anim_calculate) );
								SetScale( agor, 1.0 + 0.637 * anim_calculate );
							}
						}
						break;
					default:;
				}
				else if( jdt<=370 && (hint_c.status==HINT_JUDGED || hint_c.status==HINT_JUDGED_LIT) ) {
					// We only render the Anim here.
					ago_used++;

					/* Position */ {
						const p3 agopos(x, y, -jdt * 0.00001f);
						SetPosition(agol, agopos);
						SetPosition(agor, agopos);
					}

					/* tint.w */ {   // jdt must be larger than 270
						float tintw = (jdt - 73) * 0.003367003367003367f;   // 1/297 = 0.003367···
						tintw = 0.637f * tintw * (2.f - tintw);
						atint -> setW(0.637f - tintw);
					}

					/* tint.xyz */ {
						if(hint_c.elstatus == HINT_LATE)
							atint -> setX(A_LATE_R).setY(A_LATE_G).setZ(A_LATE_B);
						else if(daymode)
							atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
						else
							atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
					}

					/* Rotation & Scale */ {   // jdt must be larger than 270
						SetRotation(agol, D73);
						SetScale(agol, 1.637f);

						double anim_calculate = jdt * 0.002702702702702;   // 1/370
						anim_calculate = anim_calculate * (2.0 - anim_calculate);
						SetRotation( agor, GetZQuad(45.0 - 8.0*anim_calculate) );
						SetScale( agor, 1.0 + 0.637 * anim_calculate );
					}
				}
			}
		}
	}


	/* Process Echoes */
	// NYI


	/* Clean Up & Do Returns */
	lua_checkstack(L, 4);				lua_pushnumber(L, hint_lost);
	lua_pushnumber(L, wgo_used);		lua_pushnumber(L, hgo_used);		lua_pushnumber(L, ago_used);
	last_ms = mstime;					last_wgo.clear();					return 4;
}



// Sundries
static int FinalArf(lua_State *L) {
	Arf::clear();
	before = 0;
	return 0;
}
static int SetXS(lua_State *L) {
	xscale = luaL_checknumber(L, 1);
	return 0;
}
static int SetYS(lua_State *L) {
	yscale = luaL_checknumber(L, 1);
	return 0;
}
static int SetXD(lua_State *L) {
	xdelta = luaL_checknumber(L, 1);
	return 0;
}
static int SetYD(lua_State *L) {
	ydelta = luaL_checknumber(L, 1);
	return 0;
}
static int SetRotDeg(lua_State *L) {
	GetSINCOS( luaL_checknumber(L, 1) );
	rotsin = SIN;	rotcos = COS;
	return 0;
}
static int SetDaymode(lua_State *L) {
	daymode = lua_toboolean(L, 1);
	return 0;
}
static int SetAnmitsu(lua_State *L) {
	allow_anmitsu = lua_toboolean(L, 1);
	return 0;
}
static int NewTable(lua_State *L) {
	lua_checkstack(L, 1);
	lua_createtable( L, (int)luaL_checknumber(L, 1), (int)luaL_checknumber(L, 2) );
	return 1;
}