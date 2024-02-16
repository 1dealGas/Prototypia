// Aerials Common Header
// We use the "pragma once" Style.
#pragma once


// Aerials Includes & Caches
#include <dmsdk/sdk.h>
#include <dmsdk/dlib/vmath.h>
#include <dmsdk/dlib/buffer.h>
#include <dmsdk/script/script.h>
#include <ease_constants.h> // extern const double DSIN[901], DCOS[901],
							//					   ESIN[1001], ECOS[1001], RCP[8192];
#include <arf2_generated.h>
#include <unordered_map>
#include <vector>


// Structs & Enums
struct pdp {float p; float dp;} ;
enum { HINT_NONJUDGED_NONLIT = 0, HINT_NONJUDGED_LIT,
	   HINT_JUDGED = 10, HINT_JUDGED_LIT, HINT_SWEEPED, HINT_AUTO };