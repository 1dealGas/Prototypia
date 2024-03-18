// Aerials Input System Implementation for iOS
// #ifdef DM_PLATFORM_IOS
#include <includes.h>

/* C++ Structures */
// This is mainly a C++ module, and only use Objective-C syntaxes when interacting with iOS APIs.
double ArPosDiv = 1;
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
		// Process touches, set Params
		// Do Aerials Calls
		// Update Caches
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
	}
	else
		BCount--;
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	// UITouch *touch = [touches anyObject];
	// CGPoint location = [touch locationInView:self];
	// NSLog(@"Touch moved to location: %@", NSStringFromCGPoint(location));

	if(MCount == 0) {
		// Process touches, set Params

		// Do Aerials Calls

		// Update Caches
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
	}
	else
		MCount--;
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	NSLog(@"Touch ended");

	if(ECount == 0) {
		// Process touches, set Params

		// Do Aerials Calls

		// Update Caches
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
	}
	else
		ECount--;
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
	NSLog(@"Touch cancelled");

	if(ACount == 0) {
		// Process touches, set Params

		// Do Aerials Calls

		// Update Caches
		for(uint8_t i=0; i<10; i++) {
			ArtCaches[i].dx = ArTouches[i].dx;
			ArtCaches[i].dy = ArTouches[i].dy;
			ArtCaches[i].phase = ArTouches[i].phase;
		}
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

	// Inject UIView
	ArInput *AIview = [ [ArInput alloc] initWithFrame: self.view.bounds ];
	AIview.backgroundColor = [UIColor clearColor];
	AIview.userInteractionEnabled = YES;
	[self.view addSubview:AIview];

	// Calculate PosDiv
	const CGFloat width_ratio = self.view.bounds.size.width / 1800.0;
	const CGFloat height_ratio = self.view.bounds.size.height / 1080.0;
	ArPosDiv = (width_ratio < height_ratio) ? width_ratio : height_ratio ;
}

@end


// #endif