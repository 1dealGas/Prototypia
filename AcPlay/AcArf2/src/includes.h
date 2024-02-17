// Aerials Common Header
// We use the "pragma once" Style.
#pragma once


// Aerials Includes & Caches
#include <dmsdk/sdk.h>
#include <dmsdk/dlib/vmath.h>
#include <dmsdk/dlib/buffer.h>
#include <dmsdk/script/script.h>
#include <dmsdk/gameobject/gameobject.h>
#include <ease_constants.h> // extern const double DSIN[901], DCOS[901],
							//					   ESIN[1001], ECOS[1001], RCP[8192];
#include <arf2_generated.h>
#include <unordered_map>
#include <vector>


// Structs & Enums
struct pdp {   // 2-float Structure
	float p;
	float dp;
};

enum {   // Hint Judge Constants
	HINT_NONJUDGED_NONLIT = 0, HINT_NONJUDGED_LIT,
	HINT_JUDGED = 10, HINT_JUDGED_LIT, HINT_SWEEPED, HINT_AUTO
};

enum {   // Table Update Constants
	T_WGO = 2, T_HGO, T_AGO_L, T_AGO_R,
	T_WTINT, T_HTINT, T_ATINT,
	T_TOUCHES = 4
};

enum {   // Table Acquire Constants
	I_MS = 1,
	E_UPD = 8,
	E_JUD = 5
};