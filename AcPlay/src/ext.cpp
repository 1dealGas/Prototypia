// Defold Binding Related Stuff for Aerials
#pragma once


// Module "AcAudio"
#include "m_functions.hpp"
constexpr luaL_reg AcAudio[] = {
	{"CreateResource", AmCreateResource}, {"ReleaseResource", AmReleaseResource},
	{"CreateUnit", AmCreateUnit}, {"ReleaseUnit", AmReleaseUnit},

	{"PlayUnit", AmPlayUnit}, {"CheckPlaying", AmCheckPlaying}, {"StopUnit", AmStopUnit},
	{"PlayPreview", AmPlayPreview}, {"StopPreview", AmStopPreview},
	{"GetTime", AmGetTime}, {"SetTime", AmSetTime},
	{nullptr, nullptr}
};


// Module "Arf2"
#include "p_functions.hpp"
constexpr luaL_reg Arf2[] =   // Considering Adding a "JudgeArfController" Function.
{
	{"InitArf", InitArf}, {"FinalArf", FinalArf}, {"UpdateArf", UpdateArf},
	{"SetAudioOffset", SetAudioOffset}, {"SetIDelta", SetIDelta},

	{"SetXScale", SetXS}, {"SetYScale", SetYS}, {"SetXDelta", SetXD}, {"SetYDelta", SetYD},
	{"SetRotDeg", SetRotDeg}, {"SetDaymode", SetDaymode}, {"SetAnmitsu", SetAnmitsu},

	#if !defined(DM_PLATFORM_IOS) && !defined(DM_PLATFORM_ANDROID)
	{"JudgeArfDesktop", JudgeArfDesktop},
	#endif

	{"NewTable", NewTable}, {nullptr, nullptr}
};


// Input Related
#include "i_impl.cpp"
#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
uint8_t eq_idx_judge = 0, dq_idx_judge = 0;
uint8_t eq_idx_gui = 0, dq_idx_gui = 0;

jud qJudge[256];
struct{double x,y; uint8_t p;} qGui[256];
dmSpinlock::Spinlock qJudgeLock, qGuiLock;

void JudgeEnqueue(jud result) {
	if(input_booted) {
		dmSpinlock::Lock(&qJudgeLock);
		qJudge[eq_idx_judge] = result;
		eq_idx_judge++;
		dmSpinlock::Unlock(&qJudgeLock);
	}
}
void GUIEnqueue(const double x, const double y, const uint8_t p) {
	if(input_booted) {
		dmSpinlock::Lock(&qGuiLock);
		qGui[eq_idx_gui].x = x;
		qGui[eq_idx_gui].y = y;
		qGui[eq_idx_gui].p = p;
		eq_idx_gui++;
		dmSpinlock::Unlock(&qGuiLock);
	}
}
inline dmExtension::Result AcUpdate(dmExtension::Params* p) {
	if(input_booted) {
		lua_State* L = p->m_L;
		dmSpinlock::Lock(&qJudgeLock);
		while(dq_idx_judge != eq_idx_judge) {
			lua_getglobal(L, "J");
			lua_pushnumber(L, qJudge[dq_idx_judge].hit);
			lua_pushnumber(L, qJudge[dq_idx_judge].early);
			lua_pushnumber(L, qJudge[dq_idx_judge].late);
			lua_pushnumber(L, qJudge[dq_idx_judge].swept);
			lua_pushboolean(L, qJudge[dq_idx_judge].special_hint_judged);
			lua_call(L, 5, 0);
			dq_idx_judge++;
		}
		dmSpinlock::Unlock(&qJudgeLock);

		dmSpinlock::Lock(&qGuiLock);
		while(dq_idx_gui != eq_idx_gui) {
			lua_getglobal(L, "I");
			lua_pushnumber(L, qGui[dq_idx_gui].x);
			lua_pushnumber(L, qGui[dq_idx_gui].y);
			lua_pushnumber(L, qGui[dq_idx_gui].p);
			lua_call(L, 3, 0);
			dq_idx_gui++;
		}
		dmSpinlock::Unlock(&qGuiLock);
	}
	return dmExtension::RESULT_OK;
}
inline int InputBoot(lua_State* L) {
	input_booted = true;
	return 0;
}
#endif


/* Binding Stuff */
inline dmExtension::Result AcAppInit(dmExtension::AppParams* params) {
	dmSpinlock::Create(&mLock);
	dmSpinlock::Create(&hLock);
	dmSpinlock::Create(&bhLock);
#if defined(DM_PLATFORM_IOS)
	dmSpinlock::Create(&qJudgeLock);
	dmSpinlock::Create(&qGuiLock);
	InputInit();
#elif defined(DM_PLATFORM_ANDROID)
	dmSpinlock::Create(&qJudgeLock);
	dmSpinlock::Create(&qGuiLock);
#endif
	return dmExtension::RESULT_OK;
}

inline dmExtension::Result AcPlayInit(dmExtension::Params* p) {
	// Init the Preview Engine, with Default Behaviors
	if( ma_engine_init(nullptr, &PreviewEngine) != MA_SUCCESS ) {
		dmLogFatal("Failed to Init the miniaudio Engine \"Preview\".");
		return dmExtension::RESULT_INIT_ERROR;
	}
	PreviewRM = ma_engine_get_resource_manager(&PreviewEngine);

	// Init the Player Engine: a custom resource manager
	const auto device = ma_engine_get_device(&PreviewEngine);   // The default device info
	auto rm_config	= ma_resource_manager_config_init();
	rm_config.decodedFormat				= device -> playback.format;
	rm_config.decodedChannels			= device -> playback.channels;
	rm_config.decodedSampleRate			= device -> sampleRate;
	if( ma_resource_manager_init(&rm_config, &player_rm) != MA_SUCCESS) {
		dmLogFatal("Failed to Init the miniaudio Resource Manager \"PlayerRM\".");
		return dmExtension::RESULT_INIT_ERROR;
	}
	PlayerRM = &player_rm;

	// Init the Player Engine: a custom engine config
	auto engine_config		= ma_engine_config_init();
	engine_config.pResourceManager		= PlayerRM;
	if( ma_engine_init(&engine_config, &PlayerEngine) != MA_SUCCESS ) {
		dmLogFatal("Failed to Init the miniaudio Engine \"Player\".");
		return dmExtension::RESULT_INIT_ERROR;
	}

	// Register Lua Modules
	/* Defold Restriction: Must Get the Lua Stack Balanced in the Initiation Process. */
	const auto L = p->m_L;
	luaL_register(L, "AcAudio", AcAudio);		luaL_register(L, "Arf2", Arf2);
	lua_pop(L, 2);

	// Register Platform-Specific Stuff
#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
	luaL_loadstring(L, "return");					lua_setglobal(L, "I");
	luaL_loadstring(L, "return");					lua_setglobal(L, "T");
	lua_pushcfunction(L, InputBoot);				lua_setglobal(L, "InputBoot");
#ifdef DM_PLATFORM_ANDROID
	InputInit();
#endif
#endif

	return dmExtension::RESULT_OK;
}

inline void AcPlayOnEvent(dmExtension::Params* p, const dmExtension::Event* e) {
	switch(e->m_Event) {   // PreviewSound won't be nullptr when playing
		case dmExtension::EVENT_ID_ICONIFYAPP:
		case dmExtension::EVENT_ID_ACTIVATEAPP: {
			if( (PreviewPlaying) && !ma_sound_is_playing(PreviewSound) )
				ma_sound_start(PreviewSound);
			if( !PlayerUnits.empty() )
				for(auto it : PlayerUnits) {   // Use range-based for loop instead
					auto& UH = it.first;
					if( (it.second) && !ma_sound_is_playing(UH) )
						ma_sound_start(UH);
				}
		}
		break;

		case dmExtension::EVENT_ID_DEICONIFYAPP:
		case dmExtension::EVENT_ID_DEACTIVATEAPP: {   // Sounds won't rewind when "stopping"
			if(PreviewPlaying)
				if( ma_sound_is_playing(PreviewSound) )
					ma_sound_stop(PreviewSound);
				else
					PreviewPlaying = false;
			if( !PlayerUnits.empty() )
				for(auto it : PlayerUnits) {
					auto& UH = it.first;   // Abandoned the const iterator
					if(it.second)
						if( ma_sound_is_playing(UH) )
							ma_sound_stop(UH);
						else
							it.second = false;
				}
		}

		default:;   /* break omitted */
	}
}

inline dmExtension::Result AcPlayFinal(dmExtension::Params* p) {
#if defined(DM_PLATFORM_IOS)   // Do Platform-Specific Stuff
	input_booted = false;
	InputUninit();
#elif defined(DM_PLATFORM_ANDROID)
	input_booted = false;
#endif

	// Close Exisiting Units(miniaudio sounds)
	if(PreviewSound) {
		ma_sound_stop(PreviewSound);
		ma_sound_uninit(PreviewSound);
	}
	if( !PlayerUnits.empty() )   // No free() calls since it's the finalizer
		for(const auto it : PlayerUnits) {
			ma_sound_stop(it.first);
			ma_sound_uninit(it.first);
		}

	// Close Existing Resources(miniaudio data sources)
	if(PreviewResource)
		ma_resource_manager_data_source_uninit(PreviewResource);
	if( !PlayerResources.empty() )
		for(const auto it : PlayerResources)
			ma_resource_manager_data_source_uninit(it.first);

	// Uninit (miniaudio)Engines; resource managers will be uninitialized automatically here.
	// Then Do Return. No further cleranup since it's the finalizer.
	ma_engine_uninit(&PreviewEngine);
	ma_engine_uninit(&PlayerEngine);
	return dmExtension::RESULT_OK;
}

inline dmExtension::Result AcAppFinal(dmExtension::AppParams* params) {
	dmSpinlock::Destroy(&mLock);
	dmSpinlock::Destroy(&hLock);
	dmSpinlock::Destroy(&bhLock);
#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
	dmSpinlock::Destroy(&qJudgeLock);
	dmSpinlock::Destroy(&qGuiLock);
#endif
	return dmExtension::RESULT_OK;
}

#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
DM_DECLARE_EXTENSION(AcPlay, "AcPlay", AcAppInit, AcAppFinal, AcPlayInit, AcUpdate, AcPlayOnEvent, AcPlayFinal)
#else
DM_DECLARE_EXTENSION(AcPlay, "AcPlay", AcAppInit, AcAppFinal, AcPlayInit, nullptr, AcPlayOnEvent, AcPlayFinal)
#endif