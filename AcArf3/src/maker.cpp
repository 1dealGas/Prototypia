/* Arf3 Maker API */
#if defined(AR_BUILD_VIEWER)

#include <arf3.h>
using namespace Arf3;
constexpr uint8_t MERGEDTIME1=1, MERGEDTIME2=2, WGOREQUIRED=3, EGOREQUIRED=4, WISHES=5, ECHOES=6;
static const auto EMSRT = [](const Arf3::EchoChild* const a, const Arf3::EchoChild* const b)
						  {  return (a->ms) < (b->ms);  };
struct HintWithSpecialTag {
	uint32_t	ms = 0;
	float		c_dx = 0.0f,  c_dy = 0.0f;
	bool		special = false;
};


Arf3_API MakeArf(lua_State* L) {
	if(Arf) return 0;
	std::vector<HintWithSpecialTag> tagged_hints;				// To keep the id of the Special Hint.
	std::unordered_map<uint64_t, HintWithSpecialTag> hintset;   // To filter Hint(s).
	std::unordered_map<uint64_t, Arf3::Object> echoset;			// To filter Echo(es).
	Arf = new Fumen;

	// MergedTime1
	auto& d1 = Arf->d1;
	const uint64_t dt1_size = lua_objlen(L, MERGEDTIME1) / 3;   // You know, LuaJIT is f*cking compatible with Lua 5.1
	d1.reserve(dt1_size);
	for(uint64_t i=1; i<=dt1_size; i++) {
		const uint64_t ix3 = i*3;
		d1.push_back({
			.init_ms = ( lua_rawgeti(L, MERGEDTIME1, ix3-2), (uint32_t)lua_tonumber(L, -1) ),
			.base_dt = ( lua_rawgeti(L, MERGEDTIME1, ix3-1), (double)lua_tonumber(L, -1) ),
			.ratio = ( lua_rawgeti(L, MERGEDTIME1, ix3), (float)lua_tonumber(L, -1) )
		});
		lua_pop(L, 3);
	}

	// MergedTime2
	auto& d2 = Arf->d2;
	const uint64_t dt2_size = lua_objlen(L, MERGEDTIME2) / 3;
	d2.reserve(dt2_size);
	for(uint64_t i=1; i<=dt2_size; i++) {
		const uint64_t ix3 = i*3;
		d2.push_back({
			.init_ms = ( lua_rawgeti(L, MERGEDTIME2, ix3-2), (uint32_t)lua_tonumber(L, -1) ),
			.base_dt = ( lua_rawgeti(L, MERGEDTIME2, ix3-1), (double)lua_tonumber(L, -1) ),
			.ratio = ( lua_rawgeti(L, MERGEDTIME2, ix3), (float)lua_tonumber(L, -1) )
		});
		lua_pop(L, 3);
	}


	// Wishes
	auto& wishes = Arf->wish;
	const uint64_t wishes_size = lua_objlen(L, WISHES);
		  uint64_t echochild_count = 0;
	wishes.resize(wishes_size);   // resize is a little bit convenient here
	for(uint64_t i=1; i<=wishes_size; i++) {
		lua_rawgeti(L, WISHES, i); {
			constexpr uint8_t CURRENT_WISH = 7;
			auto& current_wish = wishes[i-1];

			// Meta
			current_wish.of_layer2 = ( lua_pushstring(L, "of_layer2"), lua_rawget(L, CURRENT_WISH), lua_toboolean(L, -1) );
			current_wish.max_visitable_distance = ( lua_pushstring(L, "max_visible_distance"), lua_rawget(L, CURRENT_WISH), lua_tonumber(L, -1) );
			lua_pop(L, 2);

			// Common Hint(s)
			lua_pushstring(L, "hints"), lua_rawget(L, CURRENT_WISH); {
				constexpr uint8_t CURRENT_HINTS = CURRENT_WISH + 1;
				const uint64_t hints_size = lua_objlen(L, CURRENT_HINTS);
				for(uint64_t j=1; j<=hints_size; j++) {
					lua_rawgeti(L, CURRENT_HINTS, j);
					constexpr uint8_t CURRENT_HINT = CURRENT_HINTS + 1;
					const int32_t hint_ms = ( lua_rawgeti(L, CURRENT_HINT, 1), lua_tonumber(L, -1) );
					const double hint_original_x = ( lua_rawgeti(L, CURRENT_HINT, 2), lua_tonumber(L, -1) );
					const double hint_original_y = ( lua_rawgeti(L, CURRENT_HINT, 3), lua_tonumber(L, -1) );
					lua_pop(L, 4);   // 3 Params with CURRENT_HINT

					if(hint_ms>=0 && hint_ms<=512000) {
						const uint64_t k = (uint64_t)hint_ms * 127 + (uint64_t)(hint_original_x*1009.0) + (uint64_t)(hint_original_y*1013.0);
						hintset[k] = {
							.ms = (uint32_t)hint_ms,
							.c_dx = (float)((hint_original_x-8) * 112.5),
							.c_dy = (float)((hint_original_y-4) * 112.5),
							.special = false
						};
					}
				}
			}
			lua_pop(L, 1);

			// Special Hint
			lua_pushstring(L, "special_hint"), lua_rawget(L, CURRENT_WISH);
			if( lua_type(L, -1) != LUA_TNIL ) {   // if( !lua_isnil(L, -1) )
				constexpr uint8_t CURRENT_SPECIAL_HINT = CURRENT_WISH + 1;
				const int32_t sh_ms = ( lua_rawgeti(L, CURRENT_SPECIAL_HINT, 1), lua_tonumber(L, -1) );
				const double sh_original_x = ( lua_rawgeti(L, CURRENT_SPECIAL_HINT, 2), lua_tonumber(L, -1) );
				const double sh_original_y = ( lua_rawgeti(L, CURRENT_SPECIAL_HINT, 3), lua_tonumber(L, -1) );
				lua_pop(L, 3);   // 3 Params without CURRENT_SPECIAL_HINT

				if(sh_ms>=0 && sh_ms<=512000) {
					const uint64_t k = (uint64_t)sh_ms * 127 + (uint64_t)(sh_original_x*1009.0) + (uint64_t)(sh_original_y*1013.0);
					hintset[k] = {
						.ms = (uint32_t)sh_ms,
						.c_dx = (float)((sh_original_x-8) * 112.5),
						.c_dy = (float)((sh_original_y-4) * 112.5),
						.special = true
					};
				}
			}
			lua_pop(L, 1);

			// Nodes
			lua_pushstring(L, "nodes"), lua_rawget(L, CURRENT_WISH); {
				constexpr uint8_t CURRENT_NODES = CURRENT_WISH + 1;
				auto& nodes = current_wish.nodes;

				const uint64_t nodes_size = lua_objlen(L, CURRENT_NODES);
				nodes.resize(nodes_size);

				// Dump Nodes
				for(uint64_t j=1; j<=nodes_size; j++) {
					lua_rawgeti(L, CURRENT_NODES, j);
					constexpr uint8_t CURRENT_NODE = CURRENT_NODES + 1;
					auto& current_node = nodes[j-1];

					current_node.ms = ( lua_rawgeti(L, CURRENT_NODE, 1), lua_tonumber(L, -1) );
					current_node.c_dx = ( lua_rawgeti(L, CURRENT_NODE, 2), lua_tonumber(L, -1) );   // Not Final
					current_node.c_dy = ( lua_rawgeti(L, CURRENT_NODE, 3), lua_tonumber(L, -1) );   // Not Final
					current_node.easetype = ( lua_rawgeti(L, CURRENT_NODE, 4), lua_tonumber(L, -1) );
					current_node.ci = ( lua_rawgeti(L, CURRENT_NODE, 5), lua_tonumber(L, -1) );
					current_node.ce = ( lua_rawgeti(L, CURRENT_NODE, 6), lua_tonumber(L, -1) );
					lua_pop(L, 7);   // 6 Params + CURRENT_NODE
				}

				// Remove ms<0 Nodes by Trim
				if( nodes[0].ms < 0 ) {
					auto node_a = nodes.begin();
					while( node_a->ms < 0 )
						++node_a;   // node_a points to the 1st Node with ms>=0 here
					if( node_a->ms != 0 ) {
						nodes.erase( nodes.cbegin(), --node_a );   // The range is the f*cking [first,last)

						// Do some interpolation here
						// node_a: the last Node with ms<0; node_b: the 1st Node with ms>=0
						if( node_a->easetype ) {
							const auto node_b = node_a + 1;
							double ratio = node_a->ms / (node_a->ms - node_b->ms);   // (0-a_ms) / (b_ms-a_ms)
							if( node_a->easetype > LINEAR ) {
								const float original_fr = node_a->ci + (node_a->ce - node_a->ci) * ratio ;
									  float xfr = original_fr, yfr = original_fr;
								if( node_a->ci != 0.0f  ||  node_a->ce != 1.0f ) {
									float xfci, yfci, xfce, yfce;
									switch( node_a->easetype ) {
										case LCIRC:   /*  x -> ESIN   y -> ECOS  */
											xfr = ESIN[ (uint16_t)(1000 * ratio) ];
											yfr = ECOS[ (uint16_t)(1000 * ratio) ];

											xfci = ESIN[ (uint16_t)(1000 * node_a->ci) ];
											yfci = ECOS[ (uint16_t)(1000 * node_a->ci) ];
											xfce = ESIN[ (uint16_t)(1000 * node_a->ce) ];
											yfce = ECOS[ (uint16_t)(1000 * node_a->ce) ];
											break;
										case RCIRC:   /*  x -> ECOS   y -> ESIN  */
											xfr = ECOS[ (uint16_t)(1000 * ratio) ];
											yfr = ESIN[ (uint16_t)(1000 * ratio) ];

											xfci = ECOS[ (uint16_t)(1000 * node_a->ci) ];
											yfci = ESIN[ (uint16_t)(1000 * node_a->ci) ];
											xfce = ECOS[ (uint16_t)(1000 * node_a->ce) ];
											yfce = ESIN[ (uint16_t)(1000 * node_a->ce) ];
											break;
										case INQUAD:
											xfr = yfr = (ratio * ratio);
											xfci = yfci = (node_a->ci) * (node_a->ci);
											xfce = yfce = (node_a->ce) * (node_a->ce);
											break;
										case OUTQUAD:
											ratio = 1.0f - ratio;
											xfr = yfr = (1.0f - ratio * ratio);
										{
											const auto one_minus_ci = 1.0f-node_a->ci,
													   one_minus_ce = 1.0f-node_a->ce;
											xfci = yfci = 1.0f - one_minus_ci * one_minus_ci;
											xfce = yfce = 1.0f - one_minus_ce * one_minus_ce;
										}
										default:;   // break omitted
									}
									const auto fdx = (xfce - xfr) * node_a->c_dx + (xfr - xfci) * node_b->c_dx;
									const auto fdy = (yfce - yfr) * node_a->c_dy + (yfr - yfci) * node_b->c_dy;
									node_a->c_dx = fdx / (xfce - xfci);
									node_a->c_dy = fdy / (yfce - yfci);
								}
								else {
									switch( node_a->easetype ) {
										case LCIRC:   /*  x -> ESIN   y -> ECOS  */
											xfr = ESIN[ (uint16_t)(1000 * ratio) ];
											yfr = ECOS[ (uint16_t)(1000 * ratio) ];
											break;
										case RCIRC:   /*  x -> ECOS   y -> ESIN  */
											xfr = ECOS[ (uint16_t)(1000 * ratio) ];
											yfr = ESIN[ (uint16_t)(1000 * ratio) ];
											break;
										case INQUAD:
											xfr = yfr = (ratio * ratio);
											break;
										case OUTQUAD:
											ratio = 1.0f - ratio;
											xfr = yfr = (1.0f - ratio * ratio);
										default:;   // break omitted
									}
									const auto dx = node_b->c_dx - node_a->c_dx;
									const auto dy = node_b->c_dy - node_a->c_dy;
									node_a->c_dx = node_a->c_dx + dx * xfr;
									node_a->c_dy = node_a->c_dy + dy * yfr;
								}
								node_a->ci = original_fr;
							}
							else {
								const auto dx = node_b->c_dx - node_a->c_dx;
								const auto dy = node_b->c_dy - node_a->c_dy;
								node_a->c_dx = node_a->c_dx + dx * ratio;
								node_a->c_dy = node_a->c_dy + dy * ratio;
							}
						}
						node_a->ms = 0;
					}
					else
						nodes.erase( nodes.cbegin(), node_a );
				}

				/* Before Tracker: Nodes */ {
					uint64_t nodes_max_ms = nodes[nodes_size-1].ms;
					if(Arf->before < nodes_max_ms)
						Arf->before = nodes_max_ms;
				}

				// Calculate Inner Params
				for(auto& current_node : nodes) {
					current_node.c_dx = (current_node.c_dx - 8) * 112.5;
					current_node.c_dy = (current_node.c_dy - 4) * 112.5;
					if( current_node.easetype > LINEAR  &&  (current_node.ci != 0.0f  ||  current_node.ce != 1.0f) ) {
						float ci = current_node.ci,  ce = current_node.ce;
						switch(current_node.easetype) {
							case LCIRC:   /*  x -> ESIN   y -> ECOS  */
								current_node.x_fci = ESIN[ (uint16_t)(1000*ci) ], current_node.y_fci = ECOS[ (uint16_t)(1000*ci) ];
								current_node.x_fce = ESIN[ (uint16_t)(1000*ce) ], current_node.y_fce = ECOS[ (uint16_t)(1000*ce) ];
								current_node.x_dnm = (float)( 1.0 / (current_node.x_fce - current_node.x_fci) );
								current_node.y_dnm = (float)( 1.0 / (current_node.y_fce - current_node.y_fci) );
								break;
							case RCIRC:   /*  x -> ECOS   y -> ESIN  */
								current_node.x_fci = ECOS[ (uint16_t)(1000*ci) ], current_node.y_fci = ESIN[ (uint16_t)(1000*ci) ];
								current_node.x_fce = ECOS[ (uint16_t)(1000*ce) ], current_node.y_fce = ESIN[ (uint16_t)(1000*ce) ];
								current_node.x_dnm = (float)( 1.0 / (current_node.x_fce - current_node.x_fci) );
								current_node.y_dnm = (float)( 1.0 / (current_node.y_fce - current_node.y_fci) );
								break;
							case INQUAD:
								current_node.x_fci = current_node.y_fci = (ci * ci);
								current_node.x_fce = current_node.y_fce = (ce * ce);
								current_node.x_dnm = current_node.y_dnm = (float)( 1.0 / (current_node.x_fce - current_node.x_fci) );
								break;
							case OUTQUAD:
								ci = 1.0f-ci, ce = 1.0f-ce;
								current_node.x_fci = current_node.y_fci = (1.0f - ci*ci);
								current_node.x_fce = current_node.y_fce = (1.0f - ce*ce);
								current_node.x_dnm = current_node.y_dnm = (float)( 1.0 / (current_node.x_fce - current_node.x_fci) );
							default:;   // break omitted
						}
					}
				}
			}
			lua_pop(L, 1);

			// WishChilds
			lua_pushstring(L, "wishchilds"), lua_rawget(L, CURRENT_WISH); {
				constexpr uint8_t CURRENT_WISHCHILDS = CURRENT_WISH + 1;
				auto& wishchilds = current_wish.wishchilds;

				const uint64_t wishchilds_size = lua_objlen(L, CURRENT_WISHCHILDS);
				wishchilds.resize(wishchilds_size);

				for(uint64_t j=1; j<=wishchilds_size; j++) {
					lua_rawgeti(L, CURRENT_WISHCHILDS, j);
					constexpr uint8_t CURRENT_WISHCHILD = CURRENT_WISHCHILDS + 1;

					auto& current_wishchild = wishchilds[j-1];
					current_wishchild.dt = ( lua_rawgeti(L, CURRENT_WISHCHILD, 1), lua_tonumber(L, -1) );

					lua_rawgeti(L, CURRENT_WISHCHILD, 2);
					constexpr uint8_t CURRENT_ANODES = CURRENT_WISHCHILD + 2;   // ···current_wishchild, dt, anodes
					auto& current_anodes = current_wishchild.anodes;

					const uint64_t anodes_size = lua_objlen(L, CURRENT_ANODES);
					current_anodes.resize(anodes_size);

					for(uint64_t k=1; k<=anodes_size; k++) {
						lua_rawgeti(L, CURRENT_ANODES, k);
						constexpr uint8_t CURRENT_ANODE = CURRENT_ANODES + 1;
						auto& current_anode = current_anodes[k-1];

						current_anode.dt = ( lua_rawgeti(L, CURRENT_ANODE, 1), lua_tonumber(L, -1) );
						current_anode.degree = ( lua_rawgeti(L, CURRENT_ANODE, 2), lua_tonumber(L, -1) );
						current_anode.easetype = ( lua_rawgeti(L, CURRENT_ANODE, 3), lua_tonumber(L, -1) );
						lua_pop(L, 4);   // 3 Params + CURRENT_ANODE
					}

					// Set RCPs
					for(uint64_t ai = anodes_size-1; ai > 0; ai--)
						current_anodes[ai-1].rcp = 1.0 / (current_anodes[ai].dt - current_anodes[ai-1].dt);
					lua_pop(L, 3);   // 2 Params + CURRENT_WISHCHILD
				}
			}
			lua_pop(L, 1);

			// EchoChilds
			lua_pushstring(L, "echochilds"), lua_rawget(L, CURRENT_WISH); {
				constexpr uint8_t CURRENT_ECHOCHILDS = CURRENT_WISH + 1;
				auto& echochilds = current_wish.echochilds;
				auto& echochilds_ms_order = current_wish.echochilds_ms_order;

				const uint64_t echochilds_size = lua_objlen(L, CURRENT_ECHOCHILDS);
				echochilds_ms_order.reserve(echochilds_size);
				echochilds.resize(echochilds_size);
				echochild_count += echochilds_size;

				for(uint64_t j=1; j<=echochilds_size; j++) {
					lua_rawgeti(L, CURRENT_ECHOCHILDS, j);
					constexpr uint8_t CURRENT_ECHOCHILD = CURRENT_ECHOCHILDS + 1;

					auto& current_echochild = echochilds[j-1];
					current_echochild.dt = ( lua_rawgeti(L, CURRENT_ECHOCHILD, 1), lua_tonumber(L, -1) );

					lua_rawgeti(L, CURRENT_ECHOCHILD, 2);
					constexpr uint8_t CURRENT_ANODES = CURRENT_ECHOCHILD + 2;   // ···current_wishchild, dt, anodes
					auto& current_anodes = current_echochild.anodes;

					const uint64_t anodes_size = lua_objlen(L, CURRENT_ANODES);
					current_anodes.resize(anodes_size);

					for(uint64_t k=1; k<=anodes_size; k++) {
						lua_rawgeti(L, CURRENT_ANODES, k);
						constexpr uint8_t CURRENT_ANODE = CURRENT_ANODES + 1;
						auto& current_anode = current_anodes[k-1];

						current_anode.dt = ( lua_rawgeti(L, CURRENT_ANODE, 1), lua_tonumber(L, -1) );
						current_anode.degree = ( lua_rawgeti(L, CURRENT_ANODE, 2), lua_tonumber(L, -1) );
						current_anode.easetype = ( lua_rawgeti(L, CURRENT_ANODE, 3), lua_tonumber(L, -1) );
						lua_pop(L, 4);   // 3 Params + CURRENT_ANODE
					}

					// Set RCPs & Clean Up
					current_echochild.ms = ( lua_rawgeti(L, CURRENT_ECHOCHILD, 3), lua_tonumber(L, -1) );
					current_echochild.status = AUTO;

					echochilds_ms_order.push_back( &current_echochild );
					for(uint64_t ai = anodes_size-1; ai > 0; ai--)
						current_anodes[ai-1].rcp = 1.0 / (current_anodes[ai].dt - current_anodes[ai-1].dt);
					lua_pop(L, 4);   // 3 Params + CURRENT_ECHOCHILD
				}

				std::stable_sort(echochilds_ms_order.cbegin(), echochilds_ms_order.cend(), EMSRT);
				/* Before Tracker: EchoChilds */ {
					uint64_t ec_max_ms = ( *echochilds_ms_order.cend() )->ms + 470;
					if(Arf->before < ec_max_ms)
						Arf->before = ec_max_ms;
				}
			}
			lua_pop(L, 1);
		}
		lua_pop(L, 1);
	}


	// Echoset
	const uint64_t echoes_size = lua_objlen(L, ECHOES);
	for(uint64_t i=1; i<=echoes_size; i++) {
		lua_rawgeti(L, ECHOES, i);
		constexpr uint8_t CURRENT_ECHO = 7;
		const int32_t echo_ms = ( lua_rawgeti(L, CURRENT_ECHO, 1), lua_tonumber(L, -1) );
		const double echo_original_x = ( lua_rawgeti(L, CURRENT_ECHO, 2), lua_tonumber(L, -1) );
		const double echo_original_y = ( lua_rawgeti(L, CURRENT_ECHO, 3), lua_tonumber(L, -1) );
		lua_pop(L, 4);   // 3 Params + CURRENT_ECHO

		if(echo_ms>=0 && echo_ms<=512000) {
			const uint64_t k = (uint64_t)echo_ms * 127 + (uint64_t)(echo_original_x*1009.0) + (uint64_t)(echo_original_y*1013.0);
			echoset[k] = {
				.ms = (uint32_t)echo_ms,
				.c_dx = (float)((echo_original_x-8) * 112.5),
				.c_dy = (float)((echo_original_y-4) * 112.5),
				.status = AUTO
			};
		}
	}
	const uint64_t echo_count = echoset.size();

	// Echoes
	auto& echoes = Arf->echo;
	echoes.reserve(echo_count);
	for(const auto& pair: echoset)
		echoes.push_back(pair.second);
	std::sort(echoes.begin(), echoes.end(), [](const Arf3::Object& a, const Arf3::Object& b) {
		if(a.ms == b.ms) {
			if(a.c_dx == b.c_dx)
				return a.c_dy <= b.c_dy;
			else
				return a.c_dx < b.c_dx;
		}
		return a.ms < b.ms;
	});
	/* Before Tracker: Echoes */ {
		uint64_t echo_max_ms = echoes[echo_count-1].ms + 470;
		if(Arf->before < echo_max_ms)
			Arf->before = echo_max_ms;
	}


	// TaggedHints
	const uint64_t hint_count = hintset.size();
	tagged_hints.reserve(hint_count);
	for(const auto& pair: hintset)
		tagged_hints.push_back(pair.second);
	std::sort(tagged_hints.begin(), tagged_hints.end(), [](const HintWithSpecialTag& a, const HintWithSpecialTag& b) {
		if(a.ms == b.ms) {
			if(a.c_dx == b.c_dx)
				return a.c_dy <= b.c_dy;
			else
				return a.c_dx < b.c_dx;
		}
		return a.ms < b.ms;
	});

	// Hints
	auto& hints = Arf->hint;
	hints.reserve(hint_count);
	for(uint64_t i=0; i<hint_count; i++) {
		const auto& current_hint_t = tagged_hints[i];
		if(current_hint_t.special)
			Arf->special_hint = i;
		hints.push_back({
			.ms = current_hint_t.ms,
			.c_dx = current_hint_t.c_dx,
			.c_dy = current_hint_t.c_dy,
			.status = AUTO
		});
	}
	/* Before Tracker: Hints */ {
		uint64_t hint_max_ms = hints[hint_count-1].ms + 470;
		if(Arf->before < hint_max_ms)
			Arf->before = hint_max_ms;
	}


	// Index: Reserve
	auto& index = Arf->index;
	const auto last_index = Arf->before>>9;
	index.resize(last_index+1);
	for(auto& idx : index)
		idx.widx.reserve(1024), idx.hidx.reserve(1024), idx.eidx.reserve(1024);

	// Index: Insert
	for(uint64_t i=0; i<wishes_size; i++) {
		const auto& nodes = wishes[i].nodes;
		const auto init_group = nodes.cbegin()->ms >> 9, last_group = nodes.cend()->ms >> 9;
		for(uint64_t j=init_group; j<=last_group; j++)
			index[j].widx.push_back(i);
	}
	for(uint64_t i=0; i<hint_count; i++) {
		const auto hint_index = hints[i].ms>>9;
		if(hint_index > 0)
			index[hint_index-1].hidx.push_back(i);
		if(hint_index < last_index)
			index[hint_index+1].hidx.push_back(i);
		index[hint_index].hidx.push_back(i);
	}
	for(uint64_t i=0; i<echo_count; i++) {
		const auto echo_index = echoes[i].ms>>9;
		if(echo_index > 0)
			index[echo_index-1].eidx.push_back(i);
		if(echo_index < last_index)
			index[echo_index+1].eidx.push_back(i);
		index[echo_index].eidx.push_back(i);
	}

	// Index: Sort & Determine hgo_required
	for(auto& idx : index) {
		std::sort( idx.widx.cbegin(), idx.widx.cend() );
		std::sort( idx.hidx.cbegin(), idx.hidx.cend() );
		std::sort( idx.eidx.cbegin(), idx.eidx.cend() );
		const auto current_hidx_size = idx.hidx.size();
		if( current_hidx_size > Arf->hgo_required )
			Arf->hgo_required = current_hidx_size;
	}

	// Do Returns.
	Arf->wgo_required = ( lua_rawget(L, WGOREQUIRED), lua_tonumber(L, -1) );
	Arf->ego_required = ( lua_rawget(L, EGOREQUIRED), lua_tonumber(L, -1) );
	Arf->object_count = hint_count + echo_count + echochild_count;
	return lua_pushnumber(L, Arf->before), lua_pushnumber(L, Arf->object_count), lua_pushnumber(L, Arf->hgo_required), 3;
}
#endif