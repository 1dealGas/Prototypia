// Aerials Input System Implementation for Android
#ifdef DM_PLATFORM_ANDROID

#pragma once
#include <includes.h>
#include <dmsdk/dlib/android.h>   // jni.h included


/* Globals */
void* FtId;
uint8_t PendingPressed;
inline void DoReleasedArf() {   // Must do this with mLock & bhLock unlocked
	if(ArfBefore) {
		dmSpinlock::Lock(&bhLock);		BlockedHints.clear();
		dmSpinlock::Unlock(&bhLock);	JudgeEnqueue( JudgeArf(false) );
	}
}


/* Window Size Listener */
#include <android/native_window.h>
static void(*OriginalListener)(ANativeActivity*, ANativeWindow*) = nullptr;
static void ArNativeWindowResized(ANativeActivity* A, ANativeWindow* W) {
	double WindowWthenDiv = ANativeWindow_getWidth(W);
	double WindowHthenDiv = ANativeWindow_getHeight(W);

	CenterX = WindowWthenDiv * 0.5;		CenterY = WindowHthenDiv * 0.5;
	WindowWthenDiv /= 1800.0;			WindowHthenDiv /= 1080.0;
	PosDnm = 1.0 / ( (WindowWthenDiv < WindowHthenDiv) ? WindowWthenDiv : WindowHthenDiv );

	if(OriginalListener)   // The "Defensive Programming"
		OriginalListener(A, W);
}


/* Input Handler */
#include <android/input.h>
static int32_t ArInputHandle(struct android_app* A, AInputEvent* E) {
	if( AInputEvent_getSource(E) == AINPUT_SOURCE_TOUCHSCREEN ) {

		// Manage Motions
		if( PendingPressed == 0 ) {
			const auto pointer_count = AMotionEvent_getPointerCount(E);
			dmSpinlock::Lock(&mLock);

			// Loop I: Diff Pointers
			for( uint8_t i = 0; i < pointer_count; i++ )
				if( Motions.count( (void*)AMotionEvent_getPointerId(E,i) ) == 0 )
					PendingPressed++;

			// Loop II: Modify Pointers
			Motions.clear();
			for( uint8_t i = 0; i < pointer_count; i++ ) {
				const auto pointer_id = (void*)AMotionEvent_getPointerId(E,i);
				ab current_motion;
				   current_motion.a = 900.0 + ( AMotionEvent_getX(E,i) - CenterX ) * PosDnm;
				   current_motion.b = 540.0 + ( AMotionEvent_getY(E,i) - CenterY ) * PosDnm;
				Motions[pointer_id] = current_motion;
			}

			dmSpinlock::Unlock(&mLock);
			if( PendingPressed > 0  &&  ArfBefore )
				JudgeEnqueue( JudgeArf(true) );
		}

		// Do Phase-Related Stuff
		/* When PendingPressed > 0, it's reasonable to suppose that the event dispatching for the current
		 *      touch sample hasn't been done, and we don't need to update Motions in this situation.
		 */
		const auto idx_and_phase	= AMotionEvent_getAction(E);		/* Higher 8bits -> Pointer index */
		const auto pointer_id		= (void*)AMotionEvent_getPointerId( E, (idx_and_phase & 0xff00) >> 8 );
		switch(idx_and_phase & 0xff) {   /* Lower 8bits -> Phase */
			case AMOTION_EVENT_ACTION_DOWN:				// No break here
				dmSpinlock::Lock(&mLock);
				{
					const auto& motion_xy = Motions[pointer_id];
					GUIEnqueue(motion_xy.a, motion_xy.b, 0);
				}
				dmSpinlock::Unlock(&mLock);
				FtId = pointer_id;

			case AMOTION_EVENT_ACTION_POINTER_DOWN:
				PendingPressed--;
				break;

			case AMOTION_EVENT_ACTION_MOVE:
				if(pointer_id == FtId) {
					dmSpinlock::Lock(&mLock);
					const auto& motion_xy = Motions[pointer_id];
					GUIEnqueue(motion_xy.a, motion_xy.b, 1);
					dmSpinlock::Unlock(&mLock);
				}
				break;

			case AMOTION_EVENT_ACTION_UP:
				dmSpinlock::Lock(&mLock);
				{
					const auto& motion_xy = Motions[pointer_id];
					GUIEnqueue(motion_xy.a, motion_xy.b, 2);
				}
				Motions.erase(pointer_id);
				dmSpinlock::Unlock(&mLock);

				DoReleasedArf();
				FtId = nullptr;
				break;

			case AMOTION_EVENT_ACTION_POINTER_UP:
				dmSpinlock::Lock(&mLock);
				Motions.erase(pointer_id);
				dmSpinlock::Unlock(&mLock);

				DoReleasedArf();
				break;

			case AMOTION_EVENT_ACTION_CANCEL:
				dmSpinlock::Lock(&mLock);
				if( Motions.count(pointer_id) ) {
					const auto& motion_xy = Motions[pointer_id];
					GUIEnqueue(motion_xy.a, motion_xy.b, 2);
				}
				Motions.clear();
				dmSpinlock::Unlock(&mLock);

				FtId = nullptr;
				DoReleasedArf();
				PendingPressed = 0;

			default:;   // break omitted here
		}
	}
	return 1;   // Return 1 if handled the event, 0 for any default dispatching)
}


/* Defold Binding */
void InputInit() {
	auto APP = (struct android_app*)dmGraphics::GetNativeAndroidApp();
	OriginalListener = APP -> activity -> callbacks -> onNativeWindowResized;
	APP -> activity -> callbacks -> onNativeWindowResized = ArNativeWindowResized;
	APP -> onInputEvent = ArInputHandle;

	// Window Params Acquisition
	const auto Window = APP -> window;
	double WindowWthenDiv = ANativeWindow_getWidth(Window);
	double WindowHthenDiv = ANativeWindow_getHeight(Window);

	// Initial Window Adaptation
	CenterX = WindowWthenDiv * 0.5;		CenterY = WindowHthenDiv * 0.5;
	WindowWthenDiv /= 1800.0;			WindowHthenDiv /= 1080.0;
	PosDnm = 1.0 / ( (WindowWthenDiv < WindowHthenDiv) ? WindowWthenDiv : WindowHthenDiv );
}

#endif