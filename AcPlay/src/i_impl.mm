// Aerials Input System Implementation for iOS
// #ifdef DM_PLATFORM_IOS
#include <includes.h>

/* C++ Structures */
// This is mainly a C++ module, and only use Objective-C syntaxes when interacting with iOS APIs.
struct { double dx = 0.0, dy = 0.0; uint8_t phase = 0; } ArTouches[10], ArtCaches[10];
uint8_t BCount, MCount, ECount, ACount;   // A: Abandon


/* Taptic Engine Stuff */


/* A custom UIView to receive input events */
#import <UIKit/UIKit.h>
@interface ArInput : UIView @end
@implementation ArInput

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	// UITouch *touch = [touches anyObject];
	// CGPoint location = [touch locationInView:self];
	// NSLog(@"Touch began at location: %@", NSStringFromCGPoint(location));

	/* Since UIResponsor calls the listener on every finger/thumb,
	 * We use a counter to filter redundant event calls,
	 * and iterate the whole "event.touches" list.
	 */
	if(BCount == 0) {
		/* Process touches, set Params */
		ab vf[10];

		/* Do Aerials Calls */
		const jud jud_result = JudgeArf(vf, BCount, true, false);
		const bool has_hint_judged = (bool)(jud_result.early+jud_result.hit+jud_result.late);
		if(has_hint_judged && haptic_enabled) {

		}
		
		// Lua Function I(gui_x, gui_y, gui_phase, play_hitsound)
		if(EngineLuaState) {
			lua_getglobal(EngineLuaState, "I");
			lua_pushnumber(EngineLuaState, 0);
			lua_pushnumber(EngineLuaState, 0);
			lua_pushnumber(EngineLuaState, 0);
			lua_pushboolean(EngineLuaState, has_hint_judged && hitsound_enabled);
			lua_pcall(EngineLuaState, 4, 0);
		}
		

		/* Update Caches */
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
		BCount--;
	}
	else
		BCount--;
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	// UITouch *touch = [touches anyObject];
	// CGPoint location = [touch locationInView:self];
	// NSLog(@"Touch moved to location: %@", NSStringFromCGPoint(location));

	if(MCount == 0) {
		/* Process touches, set Params */

		/* Do Aerials Calls */

		/* Update Caches */
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
		MCount--;
	}
	else
		MCount--;
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	NSLog(@"Touch ended");

	if(ECount == 0) {
		/* Process touches, set Params */

		/* Do Aerials Calls */

		/* Update Caches */
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
		ECount--;
	}
	else
		ECount--;
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	NSLog(@"Touch cancelled");

	if(ACount == 0) {
		/* Process touches, set Params */

		/* Do Aerials Calls */

		/* Update Caches */
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
		ACount--;
	}
	else
		ACount--;
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


// #endif