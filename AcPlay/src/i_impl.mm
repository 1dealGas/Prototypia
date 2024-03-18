// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#include <includes.h>
struct {
	double x = 0.0, y = 0.0;
	uint8_t phase = 2;   // Pressed:0, OnScreen:1, Released:2
} ArTouches[10];


/* Create a custom UIView to receive input events */
#import <UIKit/UIKit.h>
@interface ArInputView : UIView @end
@implementation ArInputView

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

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
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

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
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

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
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

	/* Do Lua Call: function I(gui_x, gui_y, gui_phase, special_hint_judged, play_hitsound) */
	if(EngineLuaState) {
		lua_getglobal(EngineLuaState, "I");
		lua_pushnumber(EngineLuaState, ArTouches[0].x);
		lua_pushnumber(EngineLuaState, ArTouches[0].y);
		lua_pushnumber(EngineLuaState, ArTouches[0].phase);
		lua_pushboolean(EngineLuaState, jud_result.special_hint_judged);
		lua_pushboolean(EngineLuaState, has_obj_judged && hitsound_enabled);
		lua_call(EngineLuaState, 5, 0);
	}
}

@end


/* Create a custom UIViewController that applies our custom UIView */
@interface ArInputViewController : UIViewController
@property(strong, nonatomic) ArInputView *v;
@end

@implementation ArInputViewController

- (void)loadView {
	self.v = [[ArInputView alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	self.v.backgroundColor = [UIColor clearColor];
	self.v.translatesAutoresizingMaskIntoConstraints = NO;
	self.v.userInteractionEnabled = YES;
	self.view = self.v;
}

- (void)viewDidLoad {   // Automatic Fullscreen
	[super viewDidLoad];
	[self.view.leadingAnchor constraintEqualToAnchor:self.view.superview.leadingAnchor].active = YES;
	[self.view.trailingAnchor constraintEqualToAnchor:self.view.superview.trailingAnchor].active = YES;
	[self.view.topAnchor constraintEqualToAnchor:self.view.superview.topAnchor].active = YES;
	[self.view.bottomAnchor constraintEqualToAnchor:self.view.superview.bottomAnchor].active = YES;
}

@end


/* Create a delegate class that applies our custom UIViewController */
@interface ArDelegate : UIResponder <UIApplicationDelegate>
@property(strong, nonatomic) UIWindow *w;
@end

@implementation ArDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
	self.w = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	self.w.rootViewController = [[ArInputViewController alloc] init];
	self.w.backgroundColor = [UIColor clearColor];
	self.w.windowLevel = UIWindowLevelAlert;
	[self.w makeKeyAndVisible];
	return YES;
}

@end


/* Defold Binding */
ArDelegate* D = NULL;
void InputInit() {
	D = [[ArDelegate alloc] init];
	dmExtension::RegisteriOSUIApplicationDelegate(D);
}
void InputUninit() {
	dmExtension::UnregisteriOSUIApplicationDelegate(D);
	D = NULL;
}

#endif