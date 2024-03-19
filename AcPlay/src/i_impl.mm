// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#include <includes.h>


/* C++ Data Structure */
struct ArTouch {
	double x = 0.0, y = 0.0;
	uint8_t phase = 2;   // Pressed:0, OnScreen:1, Released:2
};
std::unordered_map<void*, ArTouch> ArTouches;
ArTouch FirstTouch;
void* FtId = NULL;


/* Create a custom UIView to receive input events */
#import <UIKit/UIKit.h>
@interface ArInputView : UIView @end
@implementation ArInputView

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		void* id = (__bridge void*)touch;
		CGPoint location = [touch locationInView:self.view];
		ArTouch new_touch = {   // On UIKit (0,0) is the Left Top of the View
			900.0 + (location.x - CenterX) / PosDiv,
			540.0 + (3*CenterY - location.y) / PosDiv,
			0
		};
		if( ArTouch.empty() ) {
			FirstTouch = new_touch;
			FtId = id;
		}
		ArTouch.emplace(id, new_touch);
	}

	/* Judge & Do Haptics */
	jud jud_result;
	bool has_obj_judged = false;
	if(ArfBefore) {
		ab vf[10];
		uint8_t vfcount = 0;
		for(const auto& it : ArTouches) {
			if(it.second.phase < 2) {
				vf[vfcount].a = it.second.x;
				vf[vfcount].b = it.second.y;
				vfcount++;
			}
		}
		jud_result = JudgeArf(vf, vfcount, true, false);
		has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
		if(has_obj_judged && haptic_enabled) {
			UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
			if([haptic_player prepare])
				[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
		}
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, FirstTouch.x);
		lua_pushnumber(EngineLuaState, FirstTouch.y);
		lua_pushnumber(EngineLuaState, FirstTouch.phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
	}
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		void* id = (__bridge void*)touch;
		CGPoint location = [touch locationInView:self.view];
		ArTouches[id].x = 900.0 + (location.x - CenterX) / PosDiv;
		ArTouches[id].y = 540.0 + (3*CenterY - location.y) / PosDiv;
		ArTouches[id].phase = 1;
		if(id == FtId) {
			FirstTouch.x = ArTouches[id].x;
			FirstTouch.y = ArTouches[id].y;
			FirstTouch.phase = 1;
		}
	}

	/* Judge & Do Haptics */
	jud jud_result;
	bool has_obj_judged = false;
	if(ArfBefore) {
		ab vf[10];
		uint8_t vfcount = 0;
		for(const auto& it : ArTouches) {
			if(it.second.phase < 2) {
				vf[vfcount].a = it.second.x;
				vf[vfcount].b = it.second.y;
				vfcount++;
			}
		}
		jud_result = JudgeArf(vf, vfcount, false, false);
		has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
		if(has_obj_judged && haptic_enabled) {
			UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
			if([haptic_player prepare])
				[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
		}
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, FirstTouch.x);
		lua_pushnumber(EngineLuaState, FirstTouch.y);
		lua_pushnumber(EngineLuaState, FirstTouch.phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
	}
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		void* id = (__bridge void*)touch;
		ArTouch.erase(id);
		if(id == FtId) {
			CGPoint location = [touch locationInView:self.view];
			FirstTouch = {   // On UIKit (0,0) is the Left Top of the View
				900.0 + (location.x - CenterX) / PosDiv,
				540.0 + (3*CenterY - location.y) / PosDiv,
				2
			};
			FtId = NULL;
		}
	}

	/* Judge & Do Haptics */
	jud jud_result;
	bool has_obj_judged = false;
	if(ArfBefore) {
		ab vf[10];
		uint8_t vfcount = 0;
		for(const auto& it : ArTouches) {
			if(it.second.phase < 2) {
				vf[vfcount].a = it.second.x;
				vf[vfcount].b = it.second.y;
				vfcount++;
			}
		}
		jud_result = JudgeArf(vf, vfcount, false, true);
		has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
		if(has_obj_judged && haptic_enabled) {
			UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
			if([haptic_player prepare])
				[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
		}
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, FirstTouch.x);
		lua_pushnumber(EngineLuaState, FirstTouch.y);
		lua_pushnumber(EngineLuaState, FirstTouch.phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
	}
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	/* Process touches */
	for(UITouch *touch in touches) {
		void* id = (__bridge void*)touch;
		ArTouch.erase(id);
		if(id == FtId) {
			CGPoint location = [touch locationInView:self.view];
			FirstTouch = {   // On UIKit (0,0) is the Left Top of the View
				900.0 + (location.x - CenterX) / PosDiv,
				540.0 + (3*CenterY - location.y) / PosDiv,
				2
			};
			FtId = NULL;
		}
	}

	/* Judge & Do Haptics */
	jud jud_result;
	bool has_obj_judged = false;
	if(ArfBefore) {
		ab vf[10];
		uint8_t vfcount = 0;
		for(const auto& it : ArTouches) {
			if(it.second.phase < 2) {
				vf[vfcount].a = it.second.x;
				vf[vfcount].b = it.second.y;
				vfcount++;
			}
		}
		jud_result = JudgeArf(vf, vfcount, false, true);
		has_obj_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
		if(has_obj_judged && haptic_enabled) {
			UIImpactFeedbackGenerator *haptic_player = [[UIImpactFeedbackGenerator alloc] init];
			if([haptic_player prepare])
				[haptic_player impactOccurredWithStyle:UIImpactFeedbackStyleMedium];
		}
	}

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, FirstTouch.x);
		lua_pushnumber(EngineLuaState, FirstTouch.y);
		lua_pushnumber(EngineLuaState, FirstTouch.phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
	}
}

@end


/* Create a custom UIViewController that applies our custom UIView */
@interface ArInputViewController : UIViewController @end
@implementation ArInputViewController

- (void)loadView {
	ArInputView *v = [[ArInputView alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	v.backgroundColor = [UIColor clearColor];
	v.userInteractionEnabled = YES;
	self.view = v;
}

- (void)viewDidLayoutSubviews {
	[super viewDidLayoutSubviews];
	double WindowWthenDiv = self.view.window.bounds.size.width;
	double WindowHthenDiv = self.view.window.bounds.size.height;
	CenterX = WindowWthenDiv * 0.5;		CenterY = WindowHthenDiv * 0.5;
	WindowWthenDiv /= 1800.0;			WindowHthenDiv /= 1080.0;
	PosDiv = (WindowWthenDiv < WindowHthenDiv) ? WindowWthenDiv : WindowHthenDiv;
}

@end


/* Create a custom UIWindow class to ban KeyWindow related */
@interface ArInputWindow : UIWindow @end
@implementation ArInputWindow

- (BOOL)canBecomeKeyWindow {
	return NO;
}

@end


/* Create a Delegate class that applies our custom UIViewController */
@interface ArInputDelegate : UIResponder <UIApplicationDelegate>
@property(strong, nonatomic) UIWindow *w;
@end

@implementation ArInputDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
	self.w = [[ArInputWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	self.w.rootViewController = [[ArInputViewController alloc] init];
	self.w.backgroundColor = [UIColor clearColor];
	self.w.windowLevel = UIWindowLevelAlert;
	self.w.hidden = NO;
	return YES;
}

@end


/* Defold Binding */
ArInputDelegate* D = NULL;
void InputInit() {
	D = [[ArInputDelegate alloc] init];
	dmExtension::RegisteriOSUIApplicationDelegate(D);
}
void InputUninit() {
	dmExtension::UnregisteriOSUIApplicationDelegate(D);
	D = NULL;
}

#endif
