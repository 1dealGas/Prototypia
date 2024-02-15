// Defold Binding Related Stuff for Aerials
#include "libarf2.hpp"   // Use quotes when including sth in "src"
#pragma once


// Module "Arf2"
static const luaL_reg Arf2[] =   // Considering Adding a "JudgeArfController" Function.
{
	{"SetXScale", SetXS}, {"SetYScale", SetYS}, {"SetXDelta", SetXD}, {"SetYDelta", SetYD},
	{"InitArf", InitArf}, {"SetTbls", SetTbls}, {"UpdateArf", UpdateArf}, {"FinalArf", FinalArf},
	{"SetTouches", SetTouches}, {"SetIDelta", SetIDelta}, {"JudgeArf", JudgeArf},
	{"SetRotDeg", SetRotDeg}, {"SetDaymode", SetDaymode}, {"SetAnmitsu", SetAnmitsu},
	{"NewTable", NewTable}, {0, 0}
};


static inline dmExtension::Result LuaInit(dmExtension::Params* p) {
	luaL_register(p->m_L, "Arf2", Arf2);
    lua_pop(p->m_L, 1);   // Defold Restriction: Must Get the Lua Stack Balanced in the Initiation Process.
    return dmExtension::RESULT_OK;
}

static inline dmExtension::Result OK(dmExtension::Params* params) {
    return dmExtension::RESULT_OK;
}

static inline dmExtension::Result APPOK(dmExtension::AppParams* params) {
    return dmExtension::RESULT_OK;
}

DM_DECLARE_EXTENSION(AcPlay, "AcPlay", APPOK, APPOK, LuaInit, 0, 0, OK)
