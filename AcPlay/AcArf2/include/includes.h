// Aerials Common Header
// We use the "pragma once" Style.
#pragma once


// Sys Includes
#include <dmsdk/sdk.h>
#include <dmsdk/dlib/vmath.h>
#include <dmsdk/dlib/buffer.h>
#include <dmsdk/script/script.h>
#include <dmsdk/gameobject/gameobject.h>
#include <unordered_map>

// Aerials Includes
#include <arf2_generated.h>   // std::vector included
#include <ease_constants.h>


// Commons
struct ab { float a,b; };   // 2-float Structure
enum {
	// Hint Status Constants
	HINT_NONJUDGED_NONLIT = 0, HINT_NONJUDGED_LIT,
	HINT_JUDGED, HINT_JUDGED_LIT, HINT_SWEEPED, HINT_AUTO,

	// Hint Judge Constants
	HINT_HIT = 0, HINT_EARLY, HINT_LATE,

	// Table Update Constants
	T_WGO = 2, T_HGO, T_AGO_L, T_AGO_R,
	T_WTINT, T_HTINT, T_ATINT
};


/* A hack method to get the elem count of a new[] array */
#define COUNT(x) *( (size_t*)x - 1 )

/* Customized Syntax to State Classes with Non-Trivial Destructors */
#define Node(x) struct x {~x(){}
#define End };