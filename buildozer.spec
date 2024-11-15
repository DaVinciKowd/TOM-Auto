[app]
title = EyeDetectionApp
package.name = eyedetection
package.domain = org.avo
source.dir = .
source.include_exts = py

version = 0.1

requirements = python3,kivy,opencv-python-headless,cvzone

# Optional, use to restrict permissions
android.permissions = CAMERA, VIBRATE

# (str) The filename of the main entry point.
entrypoint = kivy.py

orientation = portrait

# (str) Supported screen sizes
android.screen_presplash = presplash.png
android.fullscreen = 1

# Python-for-Android distribution
android.archs = arm64-v8a, armeabi-v7a