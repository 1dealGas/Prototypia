// Aerials Input System Implementation for iOS
#ifdef DM_PLATFORM_IOS

#pragma once
#include <includes.h>
#import <UIKit/UIKit.h>


/* Global Vars */
void* FtId;
inline void DoReleasedArf() {   // Must do this with mLock & bhLock unlocked
	if(ArfBefore) {
		dmSpinlock::Lock(&bhLock);		BlockedHints.clear();
		dmSpinlock::Unlock(&bhLock);	JudgeEnqueue( JudgeArf(false) );
	}
}


/* Window Size Listener */
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


/* Input Handler */
@interface ArInputWindow : UIWindow @end
@implementation ArInputWindow

- (BOOL)canBecomeKeyWindow {
	return NO;
}

- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
	/* Owing to reports that for a single touch the hitTest method might be
	 *   called for multiple times, we switched to let the hitTest return the
	 *   UIWindow itself, and process our touches in other methods.
	 */
	return self;
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
	/* In iOS, multiple "Pressed" touches in a single touch sample will only result
	 * to 1 touchBegan:withevent: call, so we don't need to filter duplicated Pressed
	 * event[s] here.
	 */
	dmSpinlock::Lock(&mLock);
	for(UITouch* t in touches) {
		const void* touch_id = (__bridge void*)t;
		CGPoint location = [t locationInView:nil];
		ab current_motion;
		   current_motion.a = 900.0 + ( location.x - CenterX ) * PosDnm;
		   current_motion.b = 540.0 + ( location.y - CenterY ) * PosDnm;
		Motions[touch_id] = current_motion;

		if(FtId == nullptr) {
			GUIEnqueue(current_motion.a, current_motion.b, 0);
			FtId = touch_id;
		}
	}
	dmSpinlock::Unlock(&mLock);

	if(ArfBefore)
		JudgeEnqueue( JudgeArf(true) );   // Now we decided to let Lua to call Haptic Feedbacks.
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
	dmSpinlock::Lock(&mLock);
	for(UITouch* t in touches) {
		const void* touch_id = (__bridge void*)t;
		CGPoint location = [t locationInView:nil];
		ab current_motion;
		   current_motion.a = 900.0 + ( location.x - CenterX ) * PosDnm;
		   current_motion.b = 540.0 + ( location.y - CenterY ) * PosDnm;
		Motions[touch_id] = current_motion;

		if(touch_id == FtId)
			GUIEnqueue(current_motion.a, current_motion.b, 1);
	}
	dmSpinlock::Unlock(&mLock);
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
	dmSpinlock::Lock(&mLock);
	for(UITouch* t in touches) {
		const void* touch_id = (__bridge void*)t;
		if( Motions.count(touch_id) )
			Motions.erase(touch_id);

		if(touch_id == FtId) {
			FtId = nullptr;
			CGPoint location = [t locationInView:nil];

			ab current_motion;
			   current_motion.a = 900.0 + ( location.x - CenterX ) * PosDnm;
			   current_motion.b = 540.0 + ( location.y - CenterY ) * PosDnm;
			GUIEnqueue(current_motion.a, current_motion.b, 2);
		}
	}
	dmSpinlock::Unlock(&mLock);
	DoReleasedArf();
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
	dmSpinlock::Lock(&mLock);
	for(UITouch* t in touches) {
		if( FtId == (__bridge void*)t ) {
			CGPoint location = [t locationInView:nil];
			ab current_motion;
			   current_motion.a = 900.0 + ( location.x - CenterX ) * PosDnm;
			   current_motion.b = 540.0 + ( location.y - CenterY ) * PosDnm;
			GUIEnqueue(current_motion.a, current_motion.b, 2);
		}
	}
	Motions.clear();
	dmSpinlock::Unlock(&mLock);

	DoReleasedArf();
	FtId = nullptr;
}

@end


/* Defold Binding */
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