// Defold Binding Related Stuff for Aerials
#pragma once


// Module "Arf2"
#include "p_functions.hpp"
static const luaL_reg Arf2[] =   // Considering Adding a "JudgeArfController" Function.
{

	{"InitArf", InitArf}, {"UpdateArf", UpdateArf}, {"FinalArf", FinalArf},
	{"SetIDelta", SetIDelta}, {"JudgeArf", JudgeArf},

	{"SetXScale", SetXS}, {"SetYScale", SetYS}, {"SetXDelta", SetXD}, {"SetYDelta", SetYD},
	{"SetRotDeg", SetRotDeg}, {"SetDaymode", SetDaymode}, {"SetAnmitsu", SetAnmitsu},

	{"NewTable", NewTable}, {0, 0}

};


inline dmExtension::Result Arf2LuaInit(dmExtension::Params* p) {
	lua_State* L = p->m_L;

	// Register Modules
	luaL_register(L, "Arf2", Arf2);

	// Do API Stuff
    lua_pop(L, 1);   // Defold Restriction: Must Get the Lua Stack Balanced in the Initiation Process.
    return dmExtension::RESULT_OK;
}

inline dmExtension::Result Arf2OK(dmExtension::Params* params) {
    return dmExtension::RESULT_OK;
}

inline dmExtension::Result Arf2APPOK(dmExtension::AppParams* params) {
    return dmExtension::RESULT_OK;
}

DM_DECLARE_EXTENSION(AcPlay, "AcPlay", Arf2APPOK, Arf2APPOK, Arf2LuaInit, nullptr, nullptr, Arf2OK)