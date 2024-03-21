// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS
#include <includes.h>


/* Global Vars */
void* FtId;
double FtX, FtY;		uint8_t FtPhase;


/* UIViewController */
#import <UIKit/UIKit.h>
@interface ArInputViewController : UIViewController @end
@implementation ArInputViewController

- (void)viewDidLayoutSubviews {
	double WindowWthenDiv = self.view.bounds.size.width;
	double WindowHthenDiv = self.view.bounds.size.height;
	CenterX = WindowWthenDiv * 0.5;		CenterY = WindowHthenDiv * 0.5;
	WindowWthenDiv /= 1800.0;			WindowHthenDiv /= 1080.0;
	PosDnm = 1.0 / ( (WindowWthenDiv < WindowHthenDiv) ? WindowWthenDiv : WindowHthenDiv );
	[super viewDidLayoutSubviews];
}

@end


/* UIWindow */
@interface ArInputWindow : UIWindow @end
@implementation ArInputWindow

- (BOOL)canBecomeKeyWindow {
	return NO;
}

- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
	/* Owing to reports that for a single touch the hitTest method might be
	 *   called for multiple times, we switched to let the hitTest return the
	 *   UIWindow itself, and process our touches in the sendEvent method.
	 */
	return self;
}

- (void)sendEvent:(UIEvent *)event {
	/* First-Touch:
	 *     1 touch on the screen
	 *         Pressed -> Register
	 *         OnScreen -> if tid==FtId, Dispatch
	 *                     else Send (0,0,3)
	 *         Released -> if tid==FtId, Dispatch & Unregister
	 *                     else Send (0,0,3)
	 *
	 *     Multiple touches on the screen
	 *     -- for each touch, if tid==FtId, Tracks its status with FtX, FtY, FtPhase
	 *     -- if First-Touch registered, check FtPhase
	 *            Pressed -> (Impossible)
	 *            OnScreen -> Dispatch
	 *            Released -> Dispatch & Unregister
	 *     -- else:
	 *            Send (0,0,3)
	 *
	 */
	if(event.type == UIEventTypeTouches) {
		uint8_t HtCount = [event.allTouches count];
		if(HtCount == 1) {

			// Process Touch
			UITouch *touch = [event.allTouches anyObject];
			CGPoint location = [touch locationInView:nil];

			// Judge
			ab vf;
			vf.a = 900.0 + (location.x - CenterX) * PosDnm;
			vf.b = 540.0 + (3*CenterY - location.y) * PosDnm;
			bool pressed = (touch.phase == UITouchPhaseBegan);
			bool released = (touch.phase == UITouchPhaseEnded) || (touch.phase == UITouchPhaseCancelled);
			const jud r = JudgeArf(&vf, 1, pressed, released);

			// Process First-Touch Logics & Enqueue the Lua Call
			if(pressed) {
				FtId = (__bridge void*)touch;   // This is the only situation to register the First-Touch
				InputEnqueue(vf.a, vf.b, 0, r);
			}
			else {
				void* tid = (__bridge void*)touch;
				if(tid == FtId) {
					if(released) {
						InputEnqueue(vf.a, vf.b, 2, r);
						FtId = nullptr;
					}
					else
						InputEnqueue(vf.a, vf.b, 1, r);
				}
				else   // Non-First Touch, Send "Invalid" no matter OnScreen or Released
					InputEnqueue(0, 0, 3, r);
			}

		}
		else if(ArfBefore) {
			ab vf[10];
			uint8_t vfcount = 0;
			bool any_pressed = false, any_released = false;

			for(UITouch *touch in event.allTouches) {
				void* tid = (__bridge void*)touch;
				CGPoint location = [touch locationInView:nil];
				switch(touch.phase) {
					case UITouchPhaseBegan:   // Judge Info & Judge Vf
						any_pressed = true;
						vf[vfcount].a = 900.0 + (location.x - CenterX) * PosDnm;
						vf[vfcount].b = 540.0 + (3*CenterY - location.y) * PosDnm;
						vfcount++;
						break;

					case UITouchPhaseEnded:
					case UITouchPhaseCancelled:   // Judge Info & Ft
						any_released = true;
						if(tid == FtId) {
							FtX = 900.0 + (location.x - CenterX) * PosDnm;
							FtY = 540.0 + (3*CenterY - location.y) * PosDnm;
							FtPhase = 2;
						}
						break;

					default:   // Judge Vf & Ft
						vf[vfcount].a = 900.0 + (location.x - CenterX) * PosDnm;
						vf[vfcount].b = 540.0 + (3*CenterY - location.y) * PosDnm;
						if(tid == FtId) {
							FtX = vf[vfcount].a;
							FtY = vf[vfcount].b;
							FtPhase = 1;
						}
						vfcount++;
				}
			}

			const jud r = JudgeArf(vf, vfcount, any_pressed, any_released);
			if(FtId) {
				InputEnqueue(FtX, FtY, FtPhase, r);
				FtId = (FtPhase == 2) ? nullptr : FtId;
			}
			else
				InputEnqueue(0, 0, 3, r);
		}
		else {
			jud empty;
			for(UITouch *touch in event.allTouches)
				if( (__bridge void*)touch == FtId ) {
					CGPoint location = [touch locationInView:nil];
					FtX = 900.0 + (location.x - CenterX) * PosDnm;
					FtY = 540.0 + (3*CenterY - location.y) * PosDnm;
					switch(touch.phase) {
						case UITouchPhaseEnded:
						case UITouchPhaseCancelled:
							FtPhase = 2;
							break;
						default:
							FtPhase = 1;
					}
				}
			if(FtId) {
				InputEnqueue(FtX, FtY, FtPhase, empty);
				FtId = (FtPhase == 2) ? nullptr : FtId;
			}
			else
				InputEnqueue(0, 0, 3, empty);
		}
	}
}

@end


/* Delegate */
@interface ArInputDelegate : NSObject <UIApplicationDelegate> @end
@implementation ArInputDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
	self.window = [[ArInputWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	self.window.rootViewController = [[ArInputViewController alloc] init];
	self.window.backgroundColor = [UIColor clearColor];
	self.window.windowLevel = UIWindowLevelAlert + 5;
	self.window.hidden = NO;
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