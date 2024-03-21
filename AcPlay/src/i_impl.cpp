// Aerials Input System Implementation for Android
#ifdef DM_PLATFORM_ANDROID
#include <includes.h>
#include <dmsdk/dlib/android.h>   // jni.h included


/* Global Vars */
size_t FtId;
double FtX, FtY;		uint8_t FtPhase;


/* Window Size Listener */
#include <android/window.h>
static void ArNativeWindowResized(ANativeActivity* na, ANativeWindow* w) {

}


/* Input Handler */
#include <android/input.h>
static int32_t ArInputEvent(struct android_app* app, AInputEvent* event) {
	return 0;
}


/* Defold Binding */
void InputInit() {
	auto APP = (struct android_app*)dmGraphics::GetNativeAndroidApp();
	APP->activity->callbacks->onNativeWindowResized = ArNativeWindowResized;
	APP->onInputEvent = ArInputEvent;
}
void InputUninit() {}
#endif