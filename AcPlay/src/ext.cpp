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
	{"SetAudioOffset", SetAudioOffset}, {"SetIDelta", SetIDelta}, {"SetHaptic", SetHaptic},

	{"SetXScale", SetXS}, {"SetYScale", SetYS}, {"SetXDelta", SetXD}, {"SetYDelta", SetYD},
	{"SetRotDeg", SetRotDeg}, {"SetDaymode", SetDaymode}, {"SetAnmitsu", SetAnmitsu},

	#if !defined(DM_PLATFORM_IOS) && !defined(DM_PLATFORM_ANDROID)
	{"JudgeArfDesktop", JudgeArfDesktop},
	#endif

	{"NewTable", NewTable},
	{nullptr, nullptr}
};


// Input Queue
#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
#include <atomic>
std::atomic<uint64_t> input_queue[256];
uint8_t eq_idx = 0, dq_idx = 0;

inline int InputBoot(lua_State* L) {
	input_booted = true;
	return 0;
}

inline void InputEnqueue(const double gui_x, const double gui_y, const uint64_t gui_phase, const uint64_t has_obj_judged, const uint64_t special_judged) {
	// gui_x(0~30, always non-negative), gui_y(31~60, always non-negative)
	// gui_phase(61~62), has_obj_judged(63), special_judged(64)
	const auto s = (uint64_t)(gui_x*1024) + ((uint64_t)(gui_y*1024)<<30) + (gui_phase<<60) + (has_obj_judged<<62) + (special_judged<<63);
	input_queue[eq_idx].store(s);
	eq_idx = (eq_idx+1) % 256;
}

inline int InputDequeue(lua_State* L) {
	while(dq_idx != eq_idx) {
		const auto s = input_queue[dq_idx].load();
		lua_getglobal(L, "I");
		lua_pushnumber( L, (s & 0x3fffffff) / 1024.0 );
		lua_pushnumber( L, ((s>>30) & 0x3fffffff) / 1024.0 );
		lua_pushnumber( L, (s>>60) & 0b11 );
		lua_pushboolean( L, (s>>62) & 0b1 );
		lua_pushboolean( L, (s>>63) );
		lua_call(L, 5, 0);
		dq_idx = (dq_idx+1) % 256;
	}
	return 0;
}
#endif


/* Binding Stuff */
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
	rm_config.decodedFormat					= device -> playback.format;
	rm_config.decodedChannels				= device -> playback.channels;
	rm_config.decodedSampleRate				= device -> sampleRate;
	if( ma_resource_manager_init(&rm_config, &player_rm) != MA_SUCCESS) {
		dmLogFatal("Failed to Init the miniaudio Resource Manager \"PlayerRM\".");
		return dmExtension::RESULT_INIT_ERROR;
	}
	PlayerRM = &player_rm;

	// Init the Player Engine: a custom engine config
	auto engine_config	= ma_engine_config_init();
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
	lua_pushcfunction(L, InputBoot);				lua_setglobal(L, "InputBoot");
	lua_pushcfunction(L, InputDequeue);				lua_setglobal(L, "InputDequeue");
	InputInit();
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
	ma_engine_uninit(&PreviewEngine);
	ma_engine_uninit(&PlayerEngine);

	// Uninit Platform-Specific Stuff
	// Then Do Return. No further cleranup since it's the finalizer.
	#if defined(DM_PLATFORM_IOS) || defined(DM_PLATFORM_ANDROID)
	InputUninit();
	#endif
	return dmExtension::RESULT_OK;
}

inline dmExtension::Result AcPlayOK(dmExtension::AppParams* params) { return dmExtension::RESULT_OK; }
DM_DECLARE_EXTENSION(AcPlay, "AcPlay", AcPlayOK, AcPlayOK, AcPlayInit, nullptr, AcPlayOnEvent, AcPlayFinal)