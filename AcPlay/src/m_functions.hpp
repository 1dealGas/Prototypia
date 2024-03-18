/* Aerials Audio System */
#include <includes.h>
#pragma once


static int AmCreateResource(lua_State* L) {
	const auto LB = dmScript::CheckBuffer(L, 1);   // Buf

	// Copy the ByteArray from Defold Lua
	void *OB;
	uint32_t BSize;
	dmBuffer::GetBytes(LB -> m_Buffer, &OB, &BSize);

	void *B = malloc(BSize);
	memcpy(B, OB, BSize);

	// Decoding
	auto R = new ma_resource_manager_data_source;
	const auto N = ma_resource_manager_pipeline_notifications_init();
	ma_resource_manager_register_encoded_data(PlayerRM, "B", B, (size_t)BSize);
	const auto result = ma_resource_manager_data_source_init(
		PlayerRM, "B",
		// For "flags", using bor for the combination is recommended here
		MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_DECODE | MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT,
		&N, R);
	ma_resource_manager_unregister_data(PlayerRM, "B");

	// Do Returns
	if(result == MA_SUCCESS) {
		lua_pushboolean(L, true);   // OK
		lua_pushlightuserdata(L, R);   // Resource Handle or Msg
		PlayerResources.emplace(R, B);
	}
	else {
		lua_pushboolean(L, false);   // OK
		lua_pushstring(L, "[!] Audio format not supported by miniaudio");   // Resource Handle or Msg
		delete R;
		free(B);
	}
	return 2;
}

static int AmReleaseResource(lua_State* L) {
	/*
	 * Notice:
	 * You CANNOT release a resource refed by some unit(s).
	 */
	const auto RH = (ma_resource_manager_data_source*)lua_touserdata(L, 1);   // Resource Handle
	if( PlayerResources.count(RH) ) {
		ma_resource_manager_data_source_uninit(RH);
		free(PlayerResources[RH]);			PlayerResources.erase(RH);
		lua_pushboolean(L, true);   // OK
		delete RH;
	}
	else
		lua_pushboolean(L, false);   // OK
	return 1;
}


// Unit Level
static int AmCreateUnit(lua_State* L) {
	// Create a Sound
	const auto S = new ma_sound;
	const auto RH = (ma_resource_manager_data_source*)lua_touserdata(L, 1);   // Resource Handle
	const auto result = ma_sound_init_from_data_source(
		&PlayerEngine, RH,
		// Notice that some "sound" flags same as "resource manager data source" flags are omitted here
		MA_SOUND_FLAG_NO_PITCH | MA_SOUND_FLAG_NO_SPATIALIZATION,
		nullptr, S   // Set Group to nullptr is allowed here
		);

	// Do Returns
	if(result == MA_SUCCESS) {
		lua_pushboolean(L, true);   // OK
		lua_pushlightuserdata(L, S);   // Unit Handle or Msg

		// Audio Length in Ms
		float len = 0;   // The length getter needs to return a ma_result value
		ma_sound_get_length_in_seconds(S, &len);
		lua_pushnumber( L, (uint64_t)(len * 1000.0) );

		// Unit Emplacing
		PlayerUnits[S] = false;
		return 3;
	}
	else {
		lua_pushboolean(L, false);   // OK
		lua_pushstring(L, "[!] Failed to Initialize the Unit");   // Unit Handle or Msg
		delete S;
		return 2;
	}
}

static int AmReleaseUnit(lua_State* L) {
	const auto S = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle

	if( PlayerUnits.count(S) ) {
		// Stop & Uninitialize
		if( PlayerUnits[S] )
			ma_sound_stop(S);
		ma_sound_uninit(S);

		// Clean Up & Return
		lua_pushboolean(L, true);   // OK
		PlayerUnits.erase(S);
		delete S;   // Remind to pair the "new" operator
	}
	else
		lua_pushboolean(L, false);   // OK

	return 1;
}

static int AmPlayUnit(lua_State* L) {
	const auto UH = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle
	const bool is_looping = lua_toboolean(L, 2);   // IsLooping

	if( PlayerUnits.count(UH) ) {
		// Set Looping
		ma_sound_set_looping(UH, is_looping);

		// Start
		if( ma_sound_start(UH) == MA_SUCCESS ) {
			PlayerUnits[UH] = true;
			lua_pushboolean(L, true);   // OK
		}
		else {
			PlayerUnits[UH] = false;
			lua_pushboolean(L, false);   // OK
		}
	}
	else
		lua_pushboolean(L, false);   // OK

	return 1;
}

static int AmStopUnit(lua_State* L) {
	const auto UH = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle

	if( PlayerUnits.count(UH) ) {
		if( ma_sound_stop(UH) == MA_SUCCESS) {
			if( lua_toboolean(L, 2) )   // Rewind to Start
				ma_sound_seek_to_pcm_frame(UH, 0);
			PlayerUnits[UH] = false;
			lua_pushboolean(L, true);   // OK
		}
		else
			lua_pushboolean(L, false);   // OK
	}
	else
		lua_pushboolean(L, false);   // OK

	return 1;
}

static int AmCheckPlaying(lua_State* L) {
	const auto UH = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle

	if( PlayerUnits.count(UH) ) {
		const bool p = ma_sound_is_playing(UH);
		PlayerUnits[UH] = p;
		lua_pushboolean(L, p);   // Status
	}
	else
		lua_pushnil(L);   // Status

	return 1;
}

static int AmGetTime(lua_State* L) {
	const auto UH = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle

	if( PlayerUnits.count(UH) )
		lua_pushnumber( L, ma_sound_get_time_in_milliseconds(UH) );   // Actual ms or nil
	else
		lua_pushnil(L);   // Actual ms or nil

	return 1;
}

static int AmSetTime(lua_State* L) {
	/* Keep in mind that this is an ASYNC API. */
	const auto U = (ma_sound*)lua_touserdata(L, 1);   // Unit Handle
	auto ms = (int64_t)luaL_checknumber(L, 2);   // mstime

	if( PlayerUnits.count(U) && (!PlayerUnits[U]) ) {
		// Get the sound length
		float len = 0;
		ma_sound_get_length_in_seconds(U, &len);		len *= 1000.0f;

		// Set the time
		ms = (ms > 0) ? ms : 0;
		ms = (ms < len-2.0) ? ms : len-2.0;
		const auto result = ma_sound_seek_to_pcm_frame(U,
			(uint64_t)(ms * ma_engine_get_sample_rate(&PlayerEngine) / 1000.0)
		);
		lua_pushboolean(L, result == MA_SUCCESS);   // OK
	}
	else
		lua_pushboolean(L, false);   // OK

	return 1;
}


// Preview Functions
static int AmStopPreview(lua_State* L) {   // Should be always safe
	if(PreviewSound) {
		ma_sound_stop(PreviewSound);
		ma_sound_uninit(PreviewSound);
		delete PreviewSound;

		PreviewSound = nullptr;
		PreviewPlaying = false;

		ma_resource_manager_data_source_uninit(PreviewResource);
		delete PreviewResource;
		PreviewResource = nullptr;
	}
	return 0;
}

static int AmPlayPreview(lua_State* L) {
	const auto LB = dmScript::CheckBuffer(L, 1);   // Buf
	const bool is_looping = lua_toboolean(L, 2);   // IsLooping

	// Get the ByteArray & Pre-Cleaning
	uint32_t BSize, *B;
	dmBuffer::GetBytes(LB -> m_Buffer, (void**)&B, &BSize);
	AmStopPreview(L);

	// Load Resource
	PreviewResource = new ma_resource_manager_data_source;
	const auto N = ma_resource_manager_pipeline_notifications_init();
	ma_resource_manager_register_encoded_data(PreviewRM, "PD", B, (size_t)BSize);
	const auto res_result = ma_resource_manager_data_source_init(
		PreviewRM, "PD",
		MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_STREAM | MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT,
		&N, PreviewResource);
	ma_resource_manager_unregister_data(PreviewRM, "PD");

	// Load Unit & Play
	if(res_result == MA_SUCCESS) {
		PreviewSound = new ma_sound;
		const auto unit_result = ma_sound_init_from_data_source(
			&PreviewEngine, PreviewResource,
			MA_SOUND_FLAG_NO_PITCH | MA_SOUND_FLAG_NO_SPATIALIZATION,
			nullptr, PreviewSound
		);
		if(unit_result == MA_SUCCESS) {
			// Set Looping
			ma_sound_set_looping( PreviewSound, is_looping );

			// Start
			if( ma_sound_start(PreviewSound) == MA_SUCCESS ) {
				lua_pushboolean(L, true);   // OK
				PreviewPlaying = true;
			}
			else {
				// Clean Up 1
				ma_sound_stop(PreviewSound);
				ma_sound_uninit(PreviewSound);

				delete PreviewSound;
				PreviewSound = nullptr;
				PreviewPlaying = false;

				// Clean Up 2
				lua_pushboolean(L, false);   // OK
				ma_resource_manager_data_source_uninit(PreviewResource);
				delete PreviewResource;		PreviewResource = nullptr;
			}
		}
		else {
			// Clean Up 1
			delete PreviewSound;
			PreviewSound = nullptr;
			PreviewPlaying = false;

			// Clean Up 2
			lua_pushboolean(L, false);   // OK
			ma_resource_manager_data_source_uninit(PreviewResource);
			delete PreviewResource;		PreviewResource = nullptr;
		}
	}
	else {   // Clean Up 2
		lua_pushboolean(L, false);   // OK
		delete PreviewResource;
		PreviewResource = nullptr;
	}

	return 1;
}
