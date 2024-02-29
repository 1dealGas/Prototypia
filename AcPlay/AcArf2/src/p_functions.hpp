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
typedef dmVMath::Vector3 v3, *v3p;
typedef dmVMath::Vector4 v4, *v4p;
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
static std::unordered_map<int16_t, ab> orig_cache;
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
	orig_cache.clear();
	blocked.clear();

	// Get the Chart[Fumen] Buffer
	void* ArfBuf = nullptr; {
		uint32_t ArfSize = 0;
		dmScript::LuaHBuffer *B = dmScript::CheckBuffer(L, 1);
		dmBuffer::GetBytes(B -> m_Buffer, &ArfBuf, &ArfSize);
		if(!ArfSize) return 0;
	}


	// Decode Stuff
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
							pobj.curve_init = ci;

							float ce = ((p>>46) & 0x1ff) * 0.001956947162f; {
								if(ce < 0.0f)		ce = 0.0f;
								else if(ce > 1.0f)	ce = 1.0f;
							}
							pobj.curve_end = ce;

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
		uint8_t init_status = lua_toboolean(L, 2) ? HINT_AUTO : HINT_NONJUDGED_NONLIT;
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
	const float hl = 731.25f + hint.c_dx * rotcos - hint.c_dy * rotsin + xdelta;   // 900 - 112.5 * 1.5
	const float hd = 371.25f + hint.c_dx * rotsin + hint.c_dy * rotcos + ydelta;   // 540 - 112.5 * 1.5
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
		beyond_group = (beyond_group > group_count) ? beyond_group : group_count ;
	}

	// Unpack Touches
	ab vf[10];
	uint8_t vfcount = 0;
	for( uint8_t i=0; i<10; i++ ) {
		lua_rawgeti(L, 2, i+1);
		const v3p f = dmScript::CheckVector3(L, -1);
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
					case HINT_NONJUDGED_NONLIT:   // No break here
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
										++hint_early;
									}
									else if(dt <= maxdt) ++hint_hit;
									else {
										current_hint.elstatus = HINT_LATE;
										++hint_late;
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
										++hint_early;
									}
									else if(dt <= maxdt) ++hint_hit;
									else {
										current_hint.elstatus = HINT_LATE;
										++hint_late;
									}

								}
								else current_hint.status = HINT_NONJUDGED_LIT;

							}
							else current_hint.status = HINT_NONJUDGED_LIT;
						}
						else current_hint.status = HINT_NONJUDGED_NONLIT;
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
				case HINT_NONJUDGED_NONLIT:   // No break here
				case HINT_NONJUDGED_LIT:
					if(htn) current_hint.status = HINT_NONJUDGED_LIT;
					else current_hint.status = HINT_NONJUDGED_NONLIT;
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
		uint64_t deg = (uint64_t)(degree*10.0);			deg = (deg>3600) ? mod_degree(deg) : deg ;
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
		uint64_t deg = (uint64_t)(-degree*10.0);		deg = (deg>3600) ? mod_degree(deg) : deg ;
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
inline void GetORIG(const float p1, const float p2, uint8_t et, const bool for_y,
					float curve_init, float curve_end, float &p, float &dp) {

	// EaseType in this func:
	// 0 -> ESIN   1 -> ECOS   2 -> InQuad   3 -> OutQuad

	// EaseType Check: InQuad & OutQuad
	if(et == 3) {
		if(curve_init >= curve_end) {   // 3.OutQuad
			const float s = curve_init;
			curve_init = curve_end;		curve_end = s;
		}
		else et = 2;   // 2.Inquad
	}
	else if(for_y && et==2) et = 0;		// ESIN & ECOS for Axis Y   (ECOS 1->1  ESIN 2->0)
	else et -= 1;						// ESIN & ECOS for Axis X   (ECOS 2->1  ESIN 1->0)

	// Hashnum Caculation & Cache Searching
	typedef int16_t I;
	const I H = (I)(p1*131) + (I)(p2*137) + (I)(curve_init*521) + (I)(curve_end*523) + (I)(et*1009);
	if( orig_cache.count(H) ) {
		const ab orig_pdp = orig_cache[H];
		p = orig_pdp.a;		dp = orig_pdp.b;
	}

	// Cache Miss Calculation
	else {
		double fci = curve_init;		double fce = curve_end;
		switch(et) {
			case 0: {
				fci = ESIN[ (uint16_t)(1000 * fci) ];
				fce = ESIN[ (uint16_t)(1000 * fce) ]; }
				break;
			case 1: {
				fci = ECOS[ (uint16_t)(1000 * fci) ];
				fce = ECOS[ (uint16_t)(1000 * fce) ]; }
				break;
			case 2: {
				fci *= fci;		fce *= fce; }		break;
			case 3: {
				fci = 1.0 - fci;		fci = 1.0 - fci * fci;
				fce = 1.0 - fce;		fce = 1.0 - fce * fce; }
			default:;
		}

		// To control the scale of the precision loss, the divisions here won't be optimized.
		// The orig_cache should work.
		const double dnm = fce - fci;
		p = (fce*p1 - fci*p2) / dnm;		dp = (p2 - p1) / dnm;
		orig_cache[H] = {p, dp};
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

	// Prepare Returns & Process msTime
	// Z Distribution: Wish{0,0.05,0.1,0.15}  Hint(-0.06,0)
	uint8_t wgo_used = 0, hgo_used = 0, ago_used = 0;			uint16_t hint_lost = 0;
	uint32_t mstime = (uint32_t)luaL_checknumber(L, 1); {
		if(mstime < 2)					mstime = 2;
		else if( mstime >= before )		return 0;
	}

	// Check DTimes
	// This time, we use the last_ms cache to condition the fallback iteration.
	double dt1 = 0.0; {}
	double dt2 = 0.0; {}


	/* Process Wish(es) */ {}


	/* Process Hint(s) */ {}


	// Clean Up & Do Returns
	lua_checkstack(L, 4);				lua_pushnumber(L, hint_lost);
	lua_pushnumber(L, wgo_used);		lua_pushnumber(L, hgo_used);		lua_pushnumber(L, ago_used);
	last_ms = mstime;					last_wgo.clear();					return 4;
}



// Sundries
static int FinalArf(lua_State *L) {
	Arf::clear();
	orig_cache.clear();
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