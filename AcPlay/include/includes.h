// Aerials Common Header
/* We use the "pragma once" Style. */
#pragma once

// Sys Includes
#include <dmsdk/sdk.h>
#include <dmsdk/dlib/log.h>
#include <dmsdk/dlib/vmath.h>
#include <dmsdk/dlib/buffer.h>
#include <dmsdk/dlib/spinlock.h>
#include <dmsdk/gameobject/gameobject.h>
#include <dmsdk/script/script.h>
#include <unordered_map>
#include <miniaudio.h>

// Aerials Includes
#include <arf2_generated.h>   // std::vector included
#include <ease_constants.h>


// Commons
struct ab { float a = 0.0f, b = 0.0f; };   // 2-float Structure
enum {
	// Hint Status Constants
	HINT_NONJUDGED = 0, HINT_NONJUDGED_LIT,
	HINT_JUDGED, HINT_JUDGED_LIT, HINT_SWEEPED, HINT_AUTO,

	// Hint Judge Constants
	HINT_HIT = 0, HINT_EARLY, HINT_LATE,

	// Table Update Constants
	T_WGO = 2, T_HGO, T_AGO_L, T_AGO_R,
	T_WTINT, T_HTINT, T_ATINT
};


// miniaudio Related
/* We put our miniaudio-related global variables here,
 * for they are used both in the Defold Lifecycle, and the Judge Func of Aerials Player. */

/* The "Preview" Engine (fast to load, and slow to play) */
ma_engine PreviewEngine;
ma_resource_manager* PreviewRM;
ma_resource_manager_data_source* PreviewResource;   // delete & Set nullptr
ma_sound* PreviewSound;   // sound_handle: delete & Set nullptr
bool PreviewPlaying;

/* The "Player" Engine (slow to load, and fast to play) */
ma_engine PlayerEngine;
ma_resource_manager player_rm, *PlayerRM;
std::unordered_map<ma_resource_manager_data_source*, void*> PlayerResources;   // HResource -> CopiedBuffer
std::unordered_map<ma_sound*, bool> PlayerUnits;   // HSound -> IsPlaying


// Judge System Related
uint32_t ArfBefore;
std::vector<void*> BlockedHints;   // <ArHint*>
std::unordered_map<void*, ab> Motions;
dmSpinlock::Spinlock mLock, hLock, bhLock;
struct jud {
	uint8_t hit = 0, early = 0, late = 0, swept = 0;
	bool special_hint_judged = false;
};


#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)

bool input_booted = false;
double PosDnm = 1.0, CenterX = 900.0, CenterY = 540.0;  // Use Lua to manage them on desktop platforms.

jud JudgeArf(bool);
void JudgeEnqueue(jud);
void GUIEnqueue(double, double, uint8_t);

void InputInit();
void InputUninit();

#endif