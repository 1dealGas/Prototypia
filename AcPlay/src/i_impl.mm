// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#include <includes.h>
struct {
	double x = 0.0, y = 0.0;
	uint8_t phase = 2;   // Pressed:0, OnScreen:1, Released:2
} ArTouches[10];


/* A custom UIView to receive input events */
#import <UIKit/UIKit.h>
@interface ArInput : UIView @end
@implementation ArInput

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		CGPoint location = [touch locationInView:self.view];
		NSUInteger id = touch.touchIdentifier % 10;
		ArTouches[id].x = 900.0 + (location.x - CenterX) / PosDiv;
		ArTouches[id].y = 540.0 + (3*CenterY - location.y) / PosDiv;   // Remind (0,0) is at the left top of the UIView
		ArTouches[id].phase = 0;
	}

	/* Judge & Do Haptics */
	ab vf[10];
	uint8_t vfcount;
	for(uint8_t i=0; i<10; i++)
		if(ArTouches[i].phase < 2) {
			vf[vfcount].a = ArTouches[i].x;
			vf[vfcount].b = ArTouches[i].y;
			vfcount++;
		}
	const jud jud_result = JudgeArf(vf, vfcount, true, false);
	const bool has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
	if(has_obj_judged && haptic_enabled) {
		UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
		if([haptic_player prepare])
			[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 4, 0);
	}
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		CGPoint location = [touch locationInView:self.view];
		NSUInteger id = touch.touchIdentifier % 10;
		ArTouches[id].x = 900.0 + (location.x - CenterX) / PosDiv;
		ArTouches[id].y = 540.0 + (3*CenterY - location.y) / PosDiv;   // Remind (0,0) is at the left top of the UIView
		ArTouches[id].phase = 1;
	}

	/* Judge & Do Haptics */
	ab vf[10];
	uint8_t vfcount;
	for(uint8_t i=0; i<10; i++)
		if(ArTouches[i].phase < 2) {
			vf[vfcount].a = ArTouches[i].x;
			vf[vfcount].b = ArTouches[i].y;
			vfcount++;
		}
	const jud jud_result = JudgeArf(vf, vfcount, false, false);
	const bool has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
	if(has_obj_judged && haptic_enabled) {
		UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
		if([haptic_player prepare])
			[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 4, 0);
	}
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		CGPoint location = [touch locationInView:self.view];
		NSUInteger id = touch.touchIdentifier % 10;
		ArTouches[id].x = 900.0 + (location.x - CenterX) / PosDiv;
		ArTouches[id].y = 540.0 + (3*CenterY - location.y) / PosDiv;   // Remind (0,0) is at the left top of the UIView
		ArTouches[id].phase = 2;
	}

	/* Judge & Do Haptics */
	ab vf[10];
	uint8_t vfcount;
	for(uint8_t i=0; i<10; i++)
		if(ArTouches[i].phase < 2) {
			vf[vfcount].a = ArTouches[i].x;
			vf[vfcount].b = ArTouches[i].y;
			vfcount++;
		}
	const jud jud_result = JudgeArf(vf, vfcount, false, true);
	const bool has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
	if(has_obj_judged && haptic_enabled) {
		UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
		if([haptic_player prepare])
			[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 4, 0);
	}
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		CGPoint location = [touch locationInView:self.view];
		NSUInteger id = touch.touchIdentifier % 10;
		ArTouches[id].x = 900.0 + (location.x - CenterX) / PosDiv;
		ArTouches[id].y = 540.0 + (3*CenterY - location.y) / PosDiv;   // Remind (0,0) is at the left top of the UIView
		ArTouches[id].phase = 2;
	}

	/* Judge & Do Haptics */
	ab vf[10];
	uint8_t vfcount;
	for(uint8_t i=0; i<10; i++)
		if(ArTouches[i].phase < 2) {
			vf[vfcount].a = ArTouches[i].x;
			vf[vfcount].b = ArTouches[i].y;
			vfcount++;
		}
	const jud jud_result = JudgeArf(vf, vfcount, false, true);
	const bool has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
	if(has_obj_judged && haptic_enabled) {
		UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
		if([haptic_player prepare])
			[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 4, 0);
	}
}

@end


/* Register the custom UIView into ViewController */
#import "ViewController.h"
@interface ViewController () @end
@implementation ViewController

- (void)viewDidLoad {
	[super viewDidLoad];
	ArInput *AIview = [ [ArInput alloc] initWithFrame: self.view.bounds ];
	AIview.backgroundColor = [UIColor clearColor];
	AIview.userInteractionEnabled = YES;
	[self.view addSubview:AIview];
}

@end
#endif