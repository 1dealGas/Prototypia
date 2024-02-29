// Singleton Class for Decoded Aerials Chart[Fumen] Data
#include <includes.h>
#pragma once


// Compressible Nodes
Node(ArDeltaNode)
	double base = 0.0;
	float ratio = 0.0f;
	uint32_t init_ms = 0;
End

Node(ArAngleNode)
	uint32_t ms = 0;
	int16_t degree = 0;
	uint8_t easetype = 0;
End

Node(ArPosNode)
	float c_dx = 0.0f,  c_dy = 0.0f;
	uint32_t ms = 0;
/*--------------------------------*/
	float curve_init = 0.0f;
	float curve_end = 0.0f;
	uint8_t easetype = 0;
End

Node(ArHint)
	float c_dx = 0.0f,  c_dy = 0.0f;
	uint32_t ms = 0;
/*--------------------------------*/
	uint32_t judged_ms = 0;
	uint8_t elstatus = 0;   // To Utilize the Memory Alignment Padding Better
	uint8_t status = 0;
End


// Incompressible Nodes
// We call "new sth[size]" on InitArf(),
// And "delete[] sth" will be recursively called using "Arf.clear()"
struct ArWishChild {

	ArAngleNode* anodes = nullptr;
	float dt = 0.0f;
	uint8_t ap = 0;   // Progress of AngleNodes Iteration

	~ArWishChild() { delete[] anodes; }

};

struct ArEchoChild {

	ArAngleNode* anodes = nullptr;
	float dt = 0.0f;
	uint32_t ms = 0;
	uint8_t ap = 0;   // Progress of AngleNodes Iteration

	~ArEchoChild() { delete[] anodes; }

};

struct ArWishGroup {

	ArPosNode* nodes = nullptr;
	ArWishChild* childs = nullptr;
	ArEchoChild* echilds = nullptr;

	float mvb = 0.0f;   // Max Visible Distance

	uint16_t cp = 0;   // Progress of WishChilds Iteration
	uint16_t ep = 0;   // Progress of EchoChilds Iteration

	uint8_t np = 0;   // Progress of PosNodes Iteration
	bool ofl2 = false;    // Instance belonging to Layer 2 or Not

	~ArWishGroup() {
		delete[] nodes;
		delete[] childs;
		delete[] echilds;
	}

};

struct ArIndex {

	uint16_t* widx = nullptr;
	uint16_t* hidx = nullptr;
	uint16_t* eidx = nullptr;

	~ArIndex() {
		delete[] widx;
		delete[] hidx;
		delete[] eidx;
	}

};


// Root Type
// Scalar vars are saved internally
class Arf {

	public:
	static ArDeltaNode* d1;   // DeltaNodes in Layer 1
	static ArDeltaNode* d2;   // DeltaNodes in Layer 2
	static ArIndex* index;

	static ArWishGroup* wish;
	static ArHint *hint, *echo;

	static void clear() {
		if(d1) { delete[] d1;	d1 = nullptr; }
		if(d2) { delete[] d2;	d2 = nullptr; }
		if(wish) { delete[] wish;	wish = nullptr; }
		if(hint) { delete[] hint;	hint = nullptr; }
		if(echo) { delete[] echo;	echo = nullptr; }
		if(index) { delete[] index;	index = nullptr; }
	}

};

// Link Symbols
ArDeltaNode* Arf::d1;
ArDeltaNode* Arf::d2;
ArIndex* Arf::index;
ArWishGroup* Arf::wish;
ArHint* Arf::hint;
ArHint* Arf::echo;