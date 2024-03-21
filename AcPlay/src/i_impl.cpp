// Aerials Input System Implementation for Android
#ifdef DM_PLATFORM_ANDROID

#pragma once
#include <includes.h>
#include <dmsdk/dlib/android.h>   // jni.h included


/* Global Vars */
size_t FtId;
double FtX, FtY;		uint8_t FtPhase;


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
	return 0;
}


/* Defold Binding */
void InputInit() {
	auto APP = (struct android_app*)dmGraphics::GetNativeAndroidApp();
	const ARect& WindowRect = APP -> contentRect;

	double WindowWthenDiv = WindowRect.right;
	double WindowHthenDiv = WindowRect.bottom;
	CenterX = WindowWthenDiv * 0.5;		CenterY = WindowHthenDiv * 0.5;
	WindowWthenDiv /= 1800.0;			WindowHthenDiv /= 1080.0;
	PosDnm = 1.0 / ( (WindowWthenDiv < WindowHthenDiv) ? WindowWthenDiv : WindowHthenDiv );

	OriginalListener = APP -> activity -> callbacks -> onNativeWindowResized;
	APP -> activity -> callbacks -> onNativeWindowResized = ArNativeWindowResized;
	APP -> onInputEvent = ArInputHandle;
}
void InputUninit(){}

#endif