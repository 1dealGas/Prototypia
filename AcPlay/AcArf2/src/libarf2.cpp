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

// Judge Range Setting
// [0,100)
#define JUDGE_RANGE 37
#define JR_REV 63


// Includes & Caches
#include <dmsdk/sdk.h>
#include <dmsdk/dlib/vmath.h>
#include <dmsdk/dlib/buffer.h>
#include <dmsdk/script/script.h>
#include <dmsdk/gameobject/gameobject.h>
#include <arf2_generated.h>
#include <unordered_map>
#include <vector>
extern const double DSIN[901], DCOS[901],
					ESIN[1001], ECOS[1001], RCP[8192];

// Data & Globals
// For Safety Concern, Nothing will happen if !ArfSize.
static uint32_t ArfSize = 0;
static uint8_t* ArfBuf = nullptr;
static float xscale, yscale, xdelta, ydelta, rotsin, rotcos;
static bool daymode, allow_anmitsu;

// Internal Globals
static float SIN, COS;
static uint16_t special_hint, dt_p1, dt_p2;
static int8_t mindt = -37, maxdt = 37, idelta = 0;
static std::unordered_map<uint32_t,uint8_t> last_wgo;
static std::vector<uint32_t> blnums;


// Assistant Ease Functions
struct pdp {float p; float dp;} ;
static std::unordered_map<int16_t,pdp> orig_cache;
static inline uint16_t mod_degree( uint64_t deg ) {
	// Actually while(xxx)···
	do {
		if(deg > 7200) { if(deg > 14400) deg-=14400;	else deg-=7200; }
		else deg-=3600;
	}	while(deg > 3600);
	return deg;
}
static inline void GetSINCOS(const double degree) {
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
static inline void GetORIG(const float p1, const float p2, uint8_t et, const bool for_y,
						   float curve_init, float curve_end, float &p, float &dp) {

	// EaseType in this func:
	// 0 -> ESIN   1 -> ECOS   2 -> InQuad   3 -> OutQuad

	if(et == 3) {
		if(curve_init >= curve_end) {   // 3.OutQuad
			float _swap;				curve_init = _swap;
			curve_init = curve_end;		curve_end = _swap;
		}
		else et = 2;   // 2.Inquad
	}
	else if(for_y) {
		// if(et == 1) -> 1.ECOS  for y
		if(et == 2) et = 0;   // 0.ESIN  for y
	}
	else et -= 1;   // 0.ESIN & 1.ECOS  for x

	int16_t ocnum = (int16_t)(p1*131) + (int16_t)(p2*137) +
					(int16_t)(curve_init*521) + (int16_t)(curve_end*523) + (int16_t)(et*1009);
	if( orig_cache.count(ocnum) ) {
		pdp orig_pdp = orig_cache[ocnum];
		p = orig_pdp.p;		dp = orig_pdp.dp;
	}
	else {
		double fci = curve_init;		double fce = curve_end;
		switch(et) {
			case 0: {
				fci = ESIN[ (uint16_t)(1000 * fci) ];
				fce = ESIN[ (uint16_t)(1000 * fce) ];
				break; }
			case 1: {
				fci = ECOS[ (uint16_t)(1000 * fci) ];
				fce = ECOS[ (uint16_t)(1000 * fce) ];
				break; }
			case 2: {
				fci *= fci;		fce *= fce;		break; }
			case 3: {
				fci = 1.0 - fci;		fci = 1.0 - fci * fci;
				fce = 1.0 - fce;		fce = 1.0 - fce * fce; }
		}

		// To control the scale of the precision loss, the divisions here won't be optimized.
		// The orig_cache should work.
		double dnm = fce - fci;
		p = (float)( (fce*p1 - fci*p2) / dnm );
		dp = (float)( (p2 - p1) / dnm );

		pdp orig_pdp;
		orig_pdp.p = p;		orig_pdp.dp = dp;
		orig_cache[ocnum] = orig_pdp;
	}
}


// Input Functions
static dmVMath::Vector3* T[10];
typedef dmVMath::Vector3 v3, *v3p;
typedef dmVMath::Vector4 v4, *v4p;
enum { HINT_NONJUDGED_NONLIT = 0, HINT_NONJUDGED_LIT,
	   HINT_JUDGED = 10, HINT_JUDGED_LIT, HINT_SWEEPED, HINT_AUTO };

// Recommended Usage of "SetTouches"
//     local v3,T = vmath.vector3, Arf2.NewTable(10,0);    for i=1,10 do T[i]=v3() end
//     Arf2.SetTouches( T[1], T[2], T[3], T[4], T[5], T[6], T[7], T[8], T[9], T[10] )
// Should be done in the initialization of the Game.
static inline int SetTouches(lua_State *L) {
	for( uint8_t i=0; i<10; i++)  T[i] = dmScript::CheckVector3(L, i+1);
	return 0;
}
static inline int SetIDelta(lua_State *L) {
	int8_t _id = luaL_checknumber(L, 1);
	if( _id>=-JR_REV && _id<=JR_REV )
		{ idelta = _id;		mindt = -JUDGE_RANGE + _id;		maxdt = JUDGE_RANGE + _id; }
	else
		{ idelta = 0;		mindt = -JUDGE_RANGE;			maxdt = JUDGE_RANGE; }
	return 0;
}
static inline bool has_touch_near(const uint64_t hint) {

	// Hint: (1)TAG+(19)judged_ms+(19)ms+(12)y+(13)x
	// x:[0,48]   visible -> [16,32]
	// y:[0,24]   visible -> [8,16]

	float hint_l, hint_r, hint_d, hint_u;
	{
		uint64_t u;
		u = hint & 0x1fff;			float dx = ( (int16_t)u - 3072 ) * 0.0078125f * xscale;
		u = (hint>>13) & 0xfff;		float dy = ( (int16_t)u - 1536 ) * 0.0078125f * yscale;

		// Camera transformation integrated.
		hint_l = 8.0f + dx*rotcos - dy*rotsin + xdelta;
		hint_d = 4.0f + dx*rotsin + dy*rotcos + ydelta;

		hint_l = hint_l * 112.5f - 168.75f;		hint_r = hint_l + 337.5f;
		hint_d = hint_d * 112.5f - 78.75f;		hint_u = hint_d + 337.5f;
	}

	// For each finger,
	for( uint8_t i=0; i<10; i++ ){

		v3p f = T[i];
		uint8_t fs = (uint8_t)( f->getZ() );   // s0->invalid, s1->pressed, s2->onscreen, s3->released

		// if the finger is just pressed, or onscreen,
		if ( fs==1 || fs==2 ){

			// check its x pivot
			float x = f->getX();
			if( (x>=hint_l) && x<=hint_r ) {

				// if no problem with pos_x of the touch, check its y pivot.
				// if no problem with pos_y of the touch, return true.
				float y = f->getY();
				if ( (y>=hint_d) && y<=hint_u )  return true;

			}
		}
	}

	// if the table does contain a valid touch,
	return false;

}
static inline bool is_safe_to_anmitsu( const uint64_t hint ){

	if(!allow_anmitsu) return false;

	uint64_t u;					// No overflowing risk here.
	u = hint & 0x1fff;			int16_t hint_l = (int16_t)u - 384;		int16_t hint_r = (int16_t)u + 384;
	u = (hint>>13) & 0xfff;		int16_t hint_d = (int16_t)u - 384;		int16_t hint_u = (int16_t)u + 384;

	// Safe when blnums.size()==0. The circulation is to be skipped then.
	// For registered Hints,
	uint16_t bs = blnums.size();
	for( uint16_t i=0; i<bs; i++ ){

		// check its x pivot,
		uint32_t blnum = blnums[i];		u = blnum & 0x1fff;
		if( (u>hint_l) && u<hint_r ){

			// if problem happens with the x pivot,
			// check its y pivot, and if problem happens with the y pivot, return false.
			u = ( blnum >> 13 ) & 0xfff;
			if( (u>hint_d) && u<hint_u ) return false;

		}
	}

	// If the Hint is safe to "Anmitsu", register it, and return true.
	u = hint & 0x1ffffff;
	blnums.push_back( (uint32_t)u );
	return true;

}
static inline uint8_t HStatus(uint64_t Hint){
	Hint >>= 44;
	bool TAG = (bool)(Hint >> 19);
	Hint &= 0x7ffff;
	if( Hint==1 ) {
		if(TAG)			return HINT_AUTO;
		else			return HINT_SWEEPED;
	}
	else if(Hint) {
		if(TAG)			return HINT_JUDGED_LIT;
		else			return HINT_JUDGED;
	}
	else {
		if(TAG) 		return HINT_NONJUDGED_LIT;
		else			return HINT_NONJUDGED_NONLIT;
	}
}



/* Script APIs, Under Construction
   S --> Safety guaranteed, by precluding the memory leakage.  */
static Arf2* Arf = nullptr;
static v3p *T_WPOS = nullptr, *T_HPOS = nullptr, *T_APOS = nullptr;
static v4p *T_HTINT = nullptr, *T_ATINT = nullptr;
#define S if( !ArfSize || T_WPOS==nullptr ) return 0;

// InitArf(buf, is_auto) -> before, total_hints, wgo_required, hgo_required
// Recommended Usage (Requires Defold 1.6.4 or Newer):
//     local buf = sys.load_buffer( "Arf/1011.ar" )   -- Also allows a path on your disk.
//     local b,t,w,h = InitArf(buf)
// Before calling FinalArf(), DO NOT remove the reference of the Arf2 buffer.
static inline int InitArf(lua_State *L)
{ if(ArfSize) return 0;

	// No need to Reset: SIN,COS,mindt,maxdt,idelta
	// "special_hint" will be set later
	xdelta = ydelta = rotsin = 0.0f;
	xscale = yscale = rotcos = 1.0f;
	dt_p1 = dt_p2 = daymode = 0;
	allow_anmitsu = true;

	// Ensure a clean Initialization
	last_wgo.clear();
	orig_cache.clear();
	blnums.clear();

	// (DEPRECATED) Copy the Lua String returned by sys.load_resource() to acquire a mutable buffer.
	// const char* B = luaL_checklstring(L, 1, &ArfSize);
	// if(!ArfSize) return 0;					ArfBuf = (unsigned char*)malloc(ArfSize);
	// memcpy(ArfBuf, B, ArfSize);

	// Switched to the Defold Buffer.
	dmBuffer::HBuffer B = dmScript::CheckBufferUnpack(L, 1);
	dmBuffer::GetBytes(B, (void**)ArfBuf, &ArfSize);
	if(!ArfSize) return 0;

	// Register Arf  &  Set Auto Status
	Arf = GetMutableArf2( ArfBuf );			int total_hints = Arf -> hint() -> size();
	if( lua_toboolean(L, 2) ) {   // is_auto
		auto H = Arf -> mutable_hint();
		for( uint16_t i=0; i<total_hints; i++ ){
			auto hint_automated = H->Get(i) + 0x8000100000000000;
			H -> Mutate(i, hint_automated);
		}
	}

	// Do API Stuff
	DM_LUA_STACK_CHECK(L, 4);
	special_hint = Arf->special_hint();
	lua_pushnumber( L, Arf->before() );				lua_pushnumber( L, total_hints );
	lua_pushnumber( L, Arf->wgo_required() );		lua_pushnumber( L, Arf->hgo_required() );
	return 4;
}

// SetVecs(table_wpos/hpos/apos/htint/atint)
// Recommended Usage:
//     local wpos,hpos,apos,htint,atint
//     if b then   -- Don't forget the judging.
//         wpos = Arf2.NewTable(w,0);		for i=1,w do wpos[i] = vmath.vector3() end
//         hpos = Arf2.NewTable(h,0);		for i=1,h do hpos[i] = vmath.vector3() end
//         apos = Arf2.NewTable(h,0);		for i=1,h do apos[i] = vmath.vector3() end
//         htint = Arf2.NewTable(h,0);		for i=1,h do htint[i] = vmath.vector4() end
//         atint = Arf2.NewTable(h,0);		for i=1,h do atint[i] = vmath.vector4() end
//         SetVecs(wpos,hpos,apos,htint,atint)
//     end
// Before calling FinalArf(), DO NOT deref these Tables.
static inline int SetVecs(lua_State *L)
{ if( !ArfSize || T_WPOS!=nullptr ) return 0;

	uint8_t wgo_required = Arf->wgo_required();
	uint8_t hgo_required = Arf->hgo_required();

	T_WPOS = (v3p*)malloc( sizeof(v3p) * wgo_required );
	T_HPOS = (v3p*)malloc( sizeof(v3p) * hgo_required );
	T_APOS = (v3p*)malloc( sizeof(v3p) * hgo_required );
	T_HTINT = (v4p*)malloc( sizeof(v4p) * hgo_required );
	T_ATINT = (v4p*)malloc( sizeof(v4p) * hgo_required );

	DM_LUA_STACK_CHECK(L, 4);
	for( uint8_t i=0; i<wgo_required; i++ ) {
		lua_rawgeti(L, 1, i+1);		T_WPOS[i] = dmScript::CheckVector3(L, 7);		lua_pop(L, 1);
	}
	for( uint8_t i=0, ii=1; i<hgo_required; ii = (++i) + 1 ) {
		lua_rawgeti(L, 2, ii);		T_HPOS[i] = dmScript::CheckVector3(L, 7);
		lua_rawgeti(L, 3, ii);		T_APOS[i] = dmScript::CheckVector3(L, 8);
		lua_rawgeti(L, 4, ii);		T_HTINT[i] = dmScript::CheckVector4(L, 9);		T_HTINT[i] -> setW(1.0f);
		lua_rawgeti(L, 5, ii);		T_ATINT[i] = dmScript::CheckVector4(L, 10);		lua_pop(L, 4);
	}
	return 0;
}


// UpdateArf(mstime, table_wst, table_ainfo) -> hint_lost, wgo/hgo/ago_used
static inline int UpdateArf(lua_State *L)
{S
	// Prepare Returns & Process msTime
	// Z Distribution: Wish{0,0.05,0.1,0.15}  Hint(-0.06,0)
	DM_LUA_STACK_CHECK(L, 4);
	uint8_t wgo_used, hgo_used, ago_used;			uint16_t hint_lost;
	uint32_t mstime = (uint32_t)luaL_checknumber(L, 1);
	{
		if(mstime < 2)							mstime = 2;
		else if( mstime >= Arf->before() )		return 0;
	}

	// Check DTime
	// For Arf2 charts(fumens), init_ms of each layer's 1st DeltaNode must be 0ms.
	// [) Left Close, Right Open
	double dt1; {
	bool found;		auto dts1 = Arf -> dts_layer1();		auto dts1_last = dts1->size() - 1;
	while(!found) {
		if( dt_p1 >= dts1_last ) {   // "==" is replaced by ">=" to enhance the robustness.
			uint64_t last_deltanode = dts1 -> Get(dts1_last);		uint64_t u;
			u = (last_deltanode>>32) & 0x3ffff;						uint32_t init_ms = u*2;
			if( init_ms <= mstime ) {
				u = last_deltanode & 0xffffffff;					double base = (double)u * 0.00002;
				u = last_deltanode >> 50;							double ratio = (double)u * 0.00001;
				dt1 = base + ratio * (mstime - init_ms);			found = true;	break;
			}
			else dt_p1--;
		}
		while( dt_p1 < dts1_last ) {   // ++ or --? Not determined this time.
			uint64_t u;

			uint64_t next_deltanode = dts1 -> Get(dt_p1+1);
			u = (next_deltanode>>32) & 0x3ffff;						uint32_t next_init_ms = u*2;
			if( mstime >= next_init_ms ) { dt_p1++; continue; }

			uint64_t current_deltanode = dts1 -> Get(dt_p1);
			u = (current_deltanode>>32) & 0x3ffff;					uint32_t current_init_ms = u*2;
			if( mstime < current_init_ms ) { dt_p1--; continue; }

			u = next_deltanode & 0xffffffff;						double next_base = (double)u * 0.00002;
			u = current_deltanode & 0xffffffff;						double current_base = (double)u * 0.00002;
			u = current_deltanode >> 50;							double current_ratio = (double)u * 0.00001;
			if( current_base > next_base ) dt1 = current_base - current_ratio * (mstime - current_init_ms);
			else dt1 = current_base + current_ratio * (mstime - current_init_ms);
			found = true;	break;
		}
	} }

	// Same. It makes no sense to use an array/vector for the stuff fixed to contain 2 elements.
	double dt2; {
	bool found;		auto dts2 = Arf -> dts_layer2();		auto dts2_last = dts2->size() - 1;
	while(!found) {
		if( dt_p2 >= dts2_last ) {
			uint64_t last_deltanode = dts2 -> Get(dts2_last);		uint64_t u;
			u = (last_deltanode>>32) & 0x3ffff;						uint32_t init_ms = u*2;
			if( init_ms <= mstime ) {
				u = last_deltanode & 0xffffffff;					double base = (double)u * 0.00002;
				u = last_deltanode >> 50;							double ratio = (double)u * 0.00001;
				dt2 = base + ratio * (mstime - init_ms);			found = true;	break;
			}
			else dt_p2--;
		}
		while( dt_p2 < dts2_last ) {
			uint64_t u;

			uint64_t next_deltanode = dts2 -> Get(dt_p2+1);
			u = (next_deltanode>>32) & 0x3ffff;						uint32_t next_init_ms = u*2;
			if( mstime >= next_init_ms ) { dt_p2++; continue; }

			uint64_t current_deltanode = dts2 -> Get(dt_p2);
			u = (current_deltanode>>32) & 0x3ffff;					uint32_t current_init_ms = u*2;
			if( mstime < current_init_ms ) { dt_p2--; continue; }

			u = next_deltanode & 0xffffffff;						double next_base = (double)u * 0.00002;
			u = current_deltanode & 0xffffffff;						double current_base = (double)u * 0.00002;
			u = current_deltanode >> 50;							double current_ratio = (double)u * 0.00001;
			if( current_base > next_base ) dt2 = current_base - current_ratio * (mstime - current_init_ms);
			else dt2 = current_base + current_ratio * (mstime - current_init_ms);
			found = true;	break;
		}
	} }


	// Search & Interpolate & Render Wishes
	uint32_t which_widx = mstime >> 9;
	auto current_wgids = Arf -> index() -> Get( which_widx ) -> widx();
	auto how_many_wgs = current_wgids -> size();

	auto Wish = Arf -> mutable_wish();
	for(uint8_t which_wgid=0; which_wgid<how_many_wgs; which_wgid++) {
		auto current_wgid = current_wgids -> Get(which_wgid);
		auto current_wishgroup = Wish -> GetMutableObject( current_wgid );

		// A. Info
		//    current_wishgroup -> mutate_info(new_stuff);
		uint32_t info = current_wishgroup -> info();
		bool of_layer2 = (bool)( (info>>13) & 0b1 );

		uint8_t node_progress = (uint8_t)( (info>>14) & 0xff );
		uint16_t child_progress = (uint16_t)(info >> 22);

		// B. Nodes
		bool node_found; 	float node_x, node_y;
	{	auto nodes = current_wishgroup -> nodes();

		uint32_t current_ms;
		uint8_t nodes_bound = nodes->size() - 1;
		{
			if(nodes_bound < 1)											continue;
			else if( mstime < (uint32_t)(nodes->Get(0) & 0x7ffff) )		continue;
			else if( node_progress >= nodes_bound )						node_progress = nodes_bound - 1;
		}
		while( node_progress<nodes_bound ) {   // A "break;" added at the end of the circulation body.
			// 1. Info & Judgement
			uint64_t next_node = nodes -> Get(node_progress+1);
			uint64_t current_node = nodes -> Get(node_progress);

			uint32_t next_ms = (uint32_t)(next_node & 0x7ffff);
					 current_ms = (uint32_t)(current_node & 0x7ffff);

			if( mstime < current_ms ) { node_progress--; continue; }
			else if( mstime >= next_ms ) { node_progress++; continue; }
			node_found = true;

			// 2. Interpolation
			float node_ratio;
			{
				uint32_t difms = next_ms - current_ms;
				if(!difms)				node_ratio = 0.0f;
				else if(difms<8193)		node_ratio = (mstime-current_ms) * RCP[ difms-1 ];
				else					node_ratio = (mstime-current_ms) / (float)difms;
			}

		{	uint8_t et = (uint8_t)( (current_node>>44) & 0b11 );
			if(et) {
				float x1, y1, dx, dy;
				float curve_init = (current_node>>55) * 0.001956947162f;
				{	if(curve_init > 1.0f)			curve_init = 1.0f;
					else if(curve_init < 0.0f)		curve_init = 0.0f;	}
				float curve_end = ( (current_node>>46) & 0x1ff ) * 0.001956947162f;
				{	if(curve_end > 1.0f)			curve_end = 1.0f;
					else if(curve_end < 0.0f)		curve_end = 0.0f;	}

				if( curve_init==0.0f && curve_end==1.0f ) {
					x1 = ( ( (current_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f;
					y1 = ( ( (current_node>>19) & 0xfff ) - 1024 ) * 0.0078125f;
					dx = ( ( (next_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f - x1;
					dy = ( ( (next_node>>19) & 0xfff ) - 1024 ) * 0.0078125f - y1;
				}
				else {
					// Get the true x1,dx
					float fm_x1 = ( ( (current_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f;
					float fm_x2 = ( ( (next_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f;
					GetORIG(fm_x1, fm_x2, et, false, curve_init, curve_end, x1, dx);

					// Get the true y1,dy
					float fm_y1 = ( ( (current_node>>19) & 0xfff ) - 1024 ) * 0.0078125f;
					float fm_y2 = ( ( (next_node>>19) & 0xfff ) - 1024 ) * 0.0078125f;
					GetORIG(fm_y1, fm_y2, et, true, curve_init, curve_end, y1, dy);
				}


				switch(et) {
					case 1: {
						uint16_t curve_ratio = (uint16_t)
											   ( 1000 * ( curve_init + (curve_end-curve_init) * node_ratio ) );
						node_x = x1 + dx * ESIN[curve_ratio];
						node_y = y1 + dy * ECOS[curve_ratio];
						break; }
					case 2: {
						uint16_t curve_ratio = (uint16_t)
											   ( 1000 * ( curve_init + (curve_end-curve_init) * node_ratio ) );
						node_x = x1 + dx * ECOS[curve_ratio];
						node_y = y1 + dy * ESIN[curve_ratio];
						break; }
					default: {   // case 3
						float ease_ratio; {
							if(curve_init > curve_end) {
								// The ACTUAL init ratio of the curve IS "curve_end" here
								ease_ratio = curve_end + (curve_init - curve_end) * node_ratio;
								ease_ratio = 1.0f - ease_ratio;
								ease_ratio = 1.0f - ease_ratio * ease_ratio;
							}
							else {
								ease_ratio = curve_init + (curve_end - curve_init) * node_ratio;
								ease_ratio *= ease_ratio;
							}
						}
						node_x = x1 + dx * ease_ratio;
						node_y = y1 + dy * ease_ratio; }
				}
			}
			else {
				float x1 = ( ( (current_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f;
				float y1 = ( ( (current_node>>19) & 0xfff ) - 1024 ) * 0.0078125f;
				float dx = ( ( (next_node>>31) & 0x1fff ) - 2048 ) * 0.0078125f - x1;
				float dy = ( ( (next_node>>19) & 0xfff ) - 1024 ) * 0.0078125f - y1;
				node_x = x1 + dx * node_ratio;
				node_y = y1 + dy * node_ratio;
			}
		}
		{	// 3. Param Setting
			float px,py;
			{
				float pdx = (node_x - 8.0f) * xscale,	pdy = (node_y - 4.0f) * yscale;
				px = 112.5f * ( 8.0f + pdx*rotcos - pdy*rotsin + xdelta );
				py = 112.5f * ( 4.0f + pdx*rotsin + pdy*rotcos + ydelta ) + 90.0f;
			}
			if( px<66.0f || px>1734.0f || py<66.0f || py>1014.0f ) break;

			uint32_t poskey = (uint32_t)(px * 1009.0f) + (uint32_t)(py * 1013.0f);
			if( last_wgo.count(poskey) ) {   // Overlapped
				lua_pushnumber(L, 1.0);
				lua_rawseti(L, 2, last_wgo[poskey]+1);
			}
			else {
				last_wgo[poskey] = wgo_used;
				T_WPOS[wgo_used] -> setX(px).setY(py).setZ( of_layer2 ? 0.1f : 0.0f );
				float wst_ratio;
				{
					uint32_t dms_from_1st_node; {
						if(node_progress)	dms_from_1st_node = mstime - (uint32_t)(nodes->Get(0) & 0x7ffff);
						else				dms_from_1st_node = mstime - current_ms;
					}
					if( dms_from_1st_node > 237 ) wst_ratio = 1.0f;
					else						  wst_ratio = dms_from_1st_node * 0.00421940928270042194092827f;
				}
				lua_pushnumber(L, wst_ratio);		lua_rawseti(L, 2, ++wgo_used);
			}
		}	break;
	}}

		// C. Childs
		if(node_found) {
			auto childs = current_wishgroup -> mutable_childs();
			uint16_t how_many_childs = childs -> size();

			if(how_many_childs) {
				double current_dt = of_layer2 ? dt2 : dt1 ;

				// Verify Child Progress I
				bool has_child_to_search = true;
				if( (child_progress+1) >= how_many_childs ) {
					double last_dt = (childs->Get( how_many_childs-1 )->dt()) * 0.00002;
					if(last_dt <= current_dt)	has_child_to_search = false;
					else						child_progress = how_many_childs - 1;
				}

				// Search Childs
				if(has_child_to_search) {
					double max_visible_distance = (info & 0x1fff) / 1024.0;
					while(child_progress < how_many_childs) {

						// Verify Child Progress II
						if( child_progress && childs->Get( child_progress-1 )->dt()*0.00002 > current_dt )
							{ child_progress--; continue; }
						else if( childs->Get( child_progress )->dt()*0.00002 <= current_dt )
							{ child_progress++; continue; }
						for( uint16_t i=child_progress; i<how_many_childs; i++) {

							// Get Radius
							auto current_child = childs -> GetMutableObject(i);
							double radius = current_child->dt() * 0.00002 - current_dt;
							if( radius > max_visible_distance ) break;

							// Get Angle
							{
								double current_degree = 90.0;
								{
									auto anodes = current_child -> anodes();
									uint8_t anodes_bound = anodes->size() - 1;

									// Unique Value
									if(!anodes_bound) {
										current_degree = (double)(anodes->Get(0) >> 20) - 1800.0;
									}

									// A Series of Values
									else if(anodes_bound > 0) {

										// Trial
										bool anode_search_required = true;
										{
											uint32_t last_anode = anodes -> Get(anodes_bound);
											uint32_t last_ms = (last_anode&0x3ffff) * 2;
											if( mstime >= last_ms ) {
												anode_search_required = false;
												current_degree = (double)(last_anode>>20) - 1800.0;
											}
										}

										// Trial II
										if(anode_search_required) {
											uint32_t first_anode = anodes -> Get(0);
											uint32_t first_ms = (first_anode&0x3ffff) * 2;
											if( mstime <= first_ms ) {
												anode_search_required = false;
												current_degree = (double)(first_anode>>20) - 1800.0;
											}
										}

										// Search if Required
										if(anode_search_required) {
											uint8_t a_progress = current_child -> p();
											if( a_progress >= anodes_bound ) a_progress = anodes_bound - 1;
											while( a_progress<anodes_bound ) {

												uint32_t next_anode = anodes -> Get(a_progress+1);
												uint32_t current_anode = anodes -> Get(a_progress);

												uint32_t a_next_ms = (next_anode&0x3ffff) * 2;
												uint32_t a_current_ms = (current_anode&0x3ffff) * 2;

												if( mstime < a_current_ms ) {
													a_progress--;
													continue;
												}
												else if( mstime >= a_next_ms ) {
													a_progress++;
													continue;
												}

												float a_ratio;
												{
													uint32_t difms = a_next_ms - a_current_ms;
													if(!difms)
														a_ratio = 0.0f;
													else if(difms<8193)
														a_ratio = (mstime-a_current_ms) * RCP[ difms-1 ];
													else
														a_ratio = (mstime-a_current_ms) / (float)difms;
												}

												double a1 = (double)(current_anode >> 20);
												double da = (double)(next_anode >> 20) - a1;
												uint8_t et = (uint8_t)( (current_anode>>18) & 0b11 );
												switch(et) {
													case 0: {
														current_degree = a1 - 1800.0;
														break; }
													case 1: {
														current_degree = a1 + da * a_ratio;
														current_degree -= 1800.0;
														break; }
													case 2: {
														a_ratio *= a_ratio;
														current_degree = a1 + da * a_ratio;
														current_degree -= 1800.0;
														break; }
													case 3: {
														a_ratio = 1.0f - a_ratio;
														a_ratio = 1.0f - a_ratio * a_ratio;
														current_degree = a1 + da * a_ratio;
														current_degree -= 1800.0;
														break; }
												}	break;
											}	current_child -> mutate_p( a_progress );
										}
									}			// There must be sth wrong if anodes_bound==-1.
								}				GetSINCOS(current_degree);
							}

							// Param Setting
							float px,py;
							{
								float pdx = (node_x + radius*COS - 8.0f) * xscale;
								float pdy = (node_y + radius*SIN - 4.0f) * yscale;
								px = 112.5f * ( 8.0f + pdx*rotcos - pdy*rotsin + xdelta );
								py = 112.5f * ( 4.0f + pdx*rotsin + pdy*rotcos + ydelta ) + 90.0f;
							}
							if( px<66.0f || px>1734.0f || py<66.0f || py>1014.0f ) break;

							uint32_t poskey = (uint32_t)(px * 1009.0f) + (uint32_t)(py * 1013.0f);
							if( last_wgo.count(poskey) ) {   // Overlapped
								lua_pushnumber(L, 1.0);
								lua_rawseti(L, 2, last_wgo[poskey]+1);
							}
							else {
								last_wgo[poskey] = wgo_used;
								T_WPOS[wgo_used] -> setX(px).setY(py).setZ( of_layer2 ? 0.15f : 0.05f );
								float wst_ratio;
								{
									float div  =  max_visible_distance - radius;
										  div /= (max_visible_distance * 0.237f);
									wst_ratio  =  div>1.0f ? 1.0f : div;
								}	lua_pushnumber(L, wst_ratio);		lua_rawseti(L, 2, ++wgo_used);
							}
						}			break;
					}
				}
			}   // L. Mutate Info
		}		current_wishgroup -> mutate_info( (info&0x3fff) + (node_progress<<14) + (child_progress<<22) );
	}


  { // Sweep Hints, then Render Hints & Effects
	auto hint = Arf -> mutable_hint();		auto idx_size = Arf -> index() -> size();
	uint32_t _group = which_widx;			uint16_t which_group = _group>1 ? _group-1 : 0 ;
			 _group = which_group + 3;		uint16_t byd1_group = _group<idx_size ? _group : idx_size;

	for(; which_group<byd1_group; which_group++) {
		auto current_hint_ids = Arf -> index() -> Get( which_group ) -> hidx();
		auto how_many_hints = current_hint_ids->size();

		for(uint8_t i=0; i<how_many_hints; i++) {
			auto current_hint_id = current_hint_ids -> Get(i);
			auto current_hint = hint -> Get( current_hint_id );

			uint64_t u;   // Acquire the status of current Hint.
			u = (current_hint>>25) & 0x7ffff;		int32_t dt = mstime - (int32_t)u;
			if(dt < -510) break;					if(dt > 470) continue;   // Asserted to be sorted.

			uint8_t ch_status = HStatus(current_hint);
			if( (ch_status<2) && dt>100 ) {   // Sweep, before generating rendering parameters.
				hint_lost += 1;
				hint -> Mutate(current_hint_id, (current_hint & 0xfffffffffff) + 0x100000000000 );
				ch_status = HINT_SWEEPED;
			}
			u = (current_hint<<1) >> 45;			int32_t pt = mstime - (int32_t)u;
													int32_t elt = dt - pt - idelta;

			float posx, posy; {
			u = current_hint & 0x1fff;				float dx = ( (int16_t)u - 3072 ) * 0.0078125f * xscale;
			u = (current_hint>>13) & 0xfff;			float dy = ( (int16_t)u - 1536 ) * 0.0078125f * yscale;
			posx = (8.0f + dx*rotcos - dy*rotsin + xdelta) * 112.5f;
			posy = (4.0f + dx*rotsin + dy*rotcos + ydelta) * 112.5f;
			}

			// Prepare Render Elements
			v3p hpos = T_HPOS[hgo_used];	v4p htint = T_HTINT[hgo_used];
			v3p apos = T_APOS[ago_used];	v4p atint = T_ATINT[ago_used];

			// Start The Access.
			if( dt < -370 ) {
				float hi_rt = 0.1337f + (float)(0.07 * (510+dt) / 140.0);
				htint -> setX(hi_rt).setY(hi_rt).setZ(hi_rt);   // Elegant?
				hpos -> setX(posx).setY(posy).setZ( -(0.05f + dt*0.00001f) );
				hgo_used++;
			}
			else if( dt <= 370 ) switch(ch_status) {
				case HINT_NONJUDGED_NONLIT: {
					hpos -> setX(posx).setY(posy).setZ( -0.04f );
					htint -> setX(0.2037f).setY(0.2037f).setZ(0.2037f);
					hgo_used++;		break; }
				case HINT_NONJUDGED_LIT: {
					hpos -> setX(posx).setY(posy).setZ( -0.03f );
					htint -> setX(0.3737f).setY(0.3737f).setZ(0.3737f);
					hgo_used++;		break; }
				case HINT_JUDGED_LIT: {   // No "break" here
					hpos -> setX(posx).setY(posy).setZ( -0.01f );
					if ( elt>=-37 && elt<=37 ) {
						if(daymode)		htint -> setX(H_HIT_R).setY(H_HIT_G).setZ(H_HIT_B);
						else 			htint -> setX(H_HIT_C).setY(H_HIT_C).setZ(H_HIT_C);
					}
					else {
						if( elt>37 ) 	htint -> setX(H_LATE_R).setY(H_LATE_G).setZ(H_LATE_B);
						else 			htint -> setX(H_EARLY_R).setY(H_EARLY_G).setZ(H_EARLY_B);
					}
					hgo_used++; }
				case HINT_JUDGED: {
					if( pt <= 370 ) {
						apos -> setX(posx).setY(posy).setZ( -pt*0.00001f );
						if( pt<73 ) {
							float tintw = pt * 0.01f;
							tintw = 0.637f * tintw * (2.f - tintw);
							atint -> setW( 0.17199f + tintw );
						}
						else {
							float tintw = (pt-73) * 0.003367003367f;   // "/297.0f"
							tintw = 0.637f * tintw * (2.f - tintw);
							atint -> setW( 0.637f - tintw );
						}
						if ( elt>=-37 && elt<=37 ) {
							if(daymode) 	atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
							else 			atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
						}
						else {
							if( elt>37 ) 	atint -> setX(A_LATE_R).setY(A_LATE_G).setZ(A_LATE_B);
							else 			atint -> setX(A_EARLY_R).setY(A_EARLY_G).setZ(A_EARLY_B);
						}
						lua_pushnumber(L, pt);	lua_rawseti(L, 3, ++ago_used);
					}							// Sh*t from C++
					break; }
				case HINT_SWEEPED: {
					float hl_rt = 0.437f - dt*0.00037f;
					htint -> setX(hl_rt);		hl_rt *= 0.51f;		htint -> setY(hl_rt).setZ(hl_rt);
					hpos -> setX(posx).setY(posy).setZ( -0.02f + dt*0.00001f );
					hgo_used++;		break; }
				case HINT_AUTO: {
					if( dt>0 ) {

						// HGo
						if (dt<101) {
							hpos -> setX(posx).setY(posy).setZ( -0.01f );
							if(daymode)		htint -> setX(H_HIT_R).setY(H_HIT_G).setZ(H_HIT_B);
							else 			htint -> setX(H_HIT_C).setY(H_HIT_C).setZ(H_HIT_C);
							hgo_used++;
						}

						// AGo
						apos -> setX(posx).setY(posy).setZ( -dt*0.00001f );
						if( dt<73 ) {
							float tintw = dt * 0.01f;
							tintw = 0.637f * tintw * (2.f - tintw);
							atint -> setW( 0.17199f + tintw );
						}
						else {
							float tintw = (dt-73) * 0.003367003367f;   // "/297.0f"
							tintw = 0.637f * tintw * (2.f - tintw);
							atint -> setW( 0.637f - tintw );
						}
						if(daymode) 	atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
						else 			atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
						lua_pushnumber(L, pt);	lua_rawseti(L, 3, ++ago_used);
					}
					else {
						hpos -> setX(posx).setY(posy).setZ( -0.04f );
						htint -> setX(0.2037f).setY(0.2037f).setZ(0.2037f);
						hgo_used++;		break;
					} }
				// default:
			}
			else if(
				(ch_status==HINT_JUDGED || ch_status==HINT_JUDGED_LIT) && ( pt<=370 )
			) {
				apos -> setX(posx).setY(posy).setZ( -pt*0.00001f );
				if( pt<73 ) {
					float tintw = pt * 0.01f;
					tintw = 0.637f * tintw * (2.f - tintw);
					atint -> setW( 0.17199f + tintw );
				}
				else {
					float tintw = (pt-73) * 0.003367003367003367f;   // 1/297 = 0.003367···
					tintw = 0.637f * tintw * (2.f - tintw);
					atint -> setW( 0.637f - tintw );
				}
				if ( elt<=37 ) {
					if(daymode) 	atint -> setX(A_HIT_R).setY(A_HIT_G).setZ(A_HIT_B);
					else 			atint -> setX(A_HIT_C).setY(A_HIT_C).setZ(A_HIT_C);
				}
				else 				atint -> setX(A_LATE_R).setY(A_LATE_G).setZ(A_LATE_B);
				lua_pushnumber(L, pt);	lua_rawseti(L, 3, ++ago_used);
			}
		}
	}
}
	// Do Returns. No need to check the capacity of Lua Stack.
	lua_pushnumber( L, hint_lost );		lua_pushnumber( L, wgo_used );
	lua_pushnumber( L, hgo_used );		lua_pushnumber( L, ago_used );
	last_wgo.clear();   // Cleanup
	return 4;
}


// JudgeArf(mstime, any_pressed, any_released) -> hint_hit, hint_lost, special_hint_judged
static inline int JudgeArf(lua_State *L)
{S
	double mstime = luaL_checknumber(L, 1);
	bool any_pressed = lua_toboolean(L, 2);
	if( lua_toboolean(L, 3) ) blnums.clear();   // Discard blocking conditions if any_released.
	lua_pop(L, 3);

	// Acquired mstime, min/max dt, any pressed from Lua.
	// Now we prepare returns, and then acquire some stuff from C++ logics.
	bool special_hint_judged;					lua_Number hint_hit, hint_lost;
	auto hint = Arf -> mutable_hint();			auto idx_size = Arf -> index() -> size();
	uint64_t _group = (uint64_t)mstime >> 9;	uint16_t which_group = _group>1 ? _group-1 : 0 ;
			 _group = which_group + 3;			uint16_t byd1_group = _group<idx_size ? _group : idx_size;

	// Start Judging.
	if(any_pressed){

		uint32_t min_time = 0;
		for(; which_group<byd1_group; which_group++) {
			auto current_hint_ids = Arf -> index() -> Get( which_group ) -> hidx();
			auto how_many_hints = current_hint_ids->size();

			for(uint16_t i=0; i<how_many_hints; i++) {
				auto current_hint_id = current_hint_ids->Get(i);
				auto current_hint = hint->Get( current_hint_id );

				// Acquire the status of current Hint.
				uint64_t hint_time = (current_hint>>25) & 0x7ffff;
				double dt = mstime - (double)hint_time;
				/// Asserted to be sorted.
				if(dt <- 370.0f) break;
				if(dt >  470.0f) continue;
				///
				uint8_t ch_status = HStatus(current_hint);
				bool htn = has_touch_near(current_hint);

				// For non-judged hints,
				if( ch_status<2 ) {   // HINT_NONJUDGED
					if(htn) {   // if we have touch(es) near the Hint,
						if( dt>=-100.0f && dt<=100.0f ) {   // we try to judge the Hint if dt[-100ms,100ms].
							bool checker_true = is_safe_to_anmitsu(current_hint);

							// for earliest Hint(s) valid in this touch_press,
							if( !min_time ){

								min_time = hint_time;
								if( dt>=mindt && dt<=maxdt )	hint_hit += 1;
								else							hint_lost += 1;

								hint -> Mutate(current_hint_id, (uint64_t)(mstime << 44) +
								(current_hint & 0xfffffffffff) + 0x8000000000000000 );

								if( current_hint_id == special_hint )
								special_hint_judged = (bool)special_hint;
							}
							// for other Hint(s) valid and safe_to_anmitsu,
							else if( hint_time==min_time || checker_true ){

								if( dt>=mindt && dt<=maxdt )	hint_hit += 1;
								else							hint_lost += 1;

								hint -> Mutate(current_hint_id, (uint64_t)(mstime << 44) +
								(current_hint & 0xfffffffffff) + 0x8000000000000000 );

								if( current_hint_id == special_hint )
								special_hint_judged = (bool)special_hint;
							}
							// for Hints unsuitable to judge, just switch it into HINT_NONJUDGED_LIT.
							else hint -> Mutate( current_hint_id,
							( (current_hint<<1) >> 1) + 0x8000000000000000 );
						}
						// for Hints out of judging range, just switch it into HINT_NONJUDGED_LIT.
						else hint -> Mutate( current_hint_id,
						( (current_hint<<1) >> 1 ) + 0x8000000000000000 );
					}
					else hint -> Mutate( current_hint_id, (current_hint<<1) >> 1 );
				}

				// For judged hints,
				else if ( ch_status==HINT_JUDGED_LIT && (!htn) ){
					hint -> Mutate( current_hint_id, (current_hint<<1) >> 1 );
				}
			}
		}
	}
	else {
		for(; which_group<byd1_group; which_group++) {
			auto current_hint_ids = Arf -> index() -> Get( which_group ) -> hidx();
			auto how_many_hints = current_hint_ids->size();

			for(uint16_t i=0; i<how_many_hints; i++) {
				auto current_hint_id = current_hint_ids->Get(i);
				auto current_hint = hint->Get( current_hint_id );

				// Acquire the status of current Hint.
				uint64_t hint_time = (current_hint>>25) & 0x7ffff;
				double dt = mstime - (double)hint_time;
				/// Asserted to be sorted.
				if(dt <- 510.0f) break;
				if(dt > 470.0f) continue;
				///
				uint8_t ch_status = HStatus(current_hint);
				bool htn = has_touch_near(current_hint);

				if( ch_status<2 ) {   // HINT_NONJUDGED
					if(htn) hint -> Mutate( current_hint_id, ( (current_hint<<1) >> 1 ) + 0x8000000000000000 );
					else	hint -> Mutate( current_hint_id, (current_hint<<1) >> 1 );
				}
				else if ( ch_status==HINT_JUDGED_LIT && (!htn) ){
					hint -> Mutate( current_hint_id, (current_hint<<1) >> 1 );
				}
			}
		}
	}

	// No need to check the stack size since we popped 4 Lua values.
	lua_pushnumber(L, hint_hit);		lua_pushnumber(L, hint_lost);
	lua_pushboolean(L, special_hint_judged);
	return 3;
}


static inline int FinalArf(lua_State *L)
{S
	orig_cache.clear();
	ArfBuf = nullptr;	Arf = nullptr;   // The Buffer will be GCed after derefing its Handle in Lua.
	free(T_WPOS);		T_WPOS = nullptr;
	free(T_HPOS);		T_HPOS = nullptr;
	free(T_APOS);		T_APOS = nullptr;
	free(T_HTINT);		T_HTINT = nullptr;
	free(T_ATINT);		T_ATINT = nullptr;
	ArfSize = 0;		return 0;
}


static inline int SetXS(lua_State *L) { xscale = luaL_checknumber(L, 1); return 0; }
static inline int SetYS(lua_State *L) { yscale = luaL_checknumber(L, 1); return 0; }
static inline int SetXD(lua_State *L) { xdelta = luaL_checknumber(L, 1); return 0; }
static inline int SetYD(lua_State *L) { ydelta = luaL_checknumber(L, 1); return 0; }
static inline int SetRotDeg(lua_State *L) {
	GetSINCOS( luaL_checknumber(L, 1) );
	rotsin = SIN;	rotcos = COS;
	return 0;
}
static inline int NewTable(lua_State *L) {
	DM_LUA_STACK_CHECK(L, 1);
	lua_createtable( L, (int)luaL_checknumber(L, 1), (int)luaL_checknumber(L, 2) );
	return 1;
}
static inline int SetDaymode(lua_State *L) { daymode		= lua_toboolean(L, 1);	return 0; }
static inline int SetAnmitsu(lua_State *L) { allow_anmitsu	= lua_toboolean(L, 1);	return 0; }

// Defold Binding Related Stuff
static const luaL_reg M[] =   // Considering Adding a "JudgeArfController" Function.
{
	{"SetXScale", SetXS}, {"SetYScale", SetYS}, {"SetXDelta", SetXD}, {"SetYDelta", SetYD},
	{"InitArf", InitArf}, {"SetVecs", SetVecs}, {"UpdateArf", UpdateArf}, {"FinalArf", FinalArf},
	{"SetTouches", SetTouches}, {"SetIDelta", SetIDelta}, {"JudgeArf", JudgeArf},
	{"SetRotDeg", SetRotDeg}, {"SetDaymode", SetDaymode}, {"SetAnmitsu", SetAnmitsu},
	{"NewTable", NewTable}, {0, 0}
};
static inline dmExtension::Result LuaInit(dmExtension::Params* p) {
	luaL_register(p -> m_L, "Arf2", M);		return dmExtension::RESULT_OK;
}
static inline dmExtension::Result OK(dmExtension::Params* params) { return dmExtension::RESULT_OK; }
static inline dmExtension::Result APPOK(dmExtension::AppParams* params) { return dmExtension::RESULT_OK; }
DM_DECLARE_EXTENSION(libArf2, "libArf2", APPOK, APPOK, LuaInit, 0, 0, OK)