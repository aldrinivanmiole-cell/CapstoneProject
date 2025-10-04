# Android Export Configuration Guide

This file provides a template for configuring Android exports in Godot.

## Setup Steps:

1. **Install Android Build Template**
   - In Godot: Project → Install Android Build Template

2. **Configure Export Preset**
   - Go to: Project → Export
   - Click "Add..." and select "Android"
   - Configure the following settings:

### Essential Settings:

**Package:**
- Unique Name: `com.yourschool.classroomgame`
- Name: `Classroom Game`
- Signed: true (for release builds)

**Permissions:**
- Internet: ON
- Access Network State: ON

**Screen:**
- Orientation: Portrait
- Support Small: ON
- Support Normal: ON
- Support Large: ON
- Support Xlarge: ON

**Version:**
- Code: 1 (increment for each release)
- Name: "1.0.0"

**Architectures:**
- armeabi-v7a: ON
- arm64-v8a: ON
- x86: OFF (optional)
- x86_64: OFF (optional)

**Min SDK:** 21 (Android 5.0)
**Target SDK:** 33 (Android 13)

### Keystore for Signing (Production):

For production builds, you need a keystore:

```bash
# Generate keystore
keytool -genkey -v -keystore classroom_game.keystore -alias classroom -keyalg RSA -keysize 2048 -validity 10000

# In Godot Export Settings:
# - Debug Keystore: path/to/classroom_game.keystore
# - Debug Keystore User: classroom
# - Debug Keystore Password: [your_password]
# - Release Keystore: [same as debug for now]
# - Release Keystore User: classroom
# - Release Keystore Password: [your_password]
```

### Testing:

**Debug Build:**
1. Select Android preset
2. Click "Export Project"
3. Save as `classroom_game_debug.apk`
4. Install on device via USB or drag-drop to emulator

**Release Build:**
1. Configure release keystore
2. Export with "Export With Debug" disabled
3. Test thoroughly before publishing

## Common Issues:

**"Could not find SDK":**
- Install Android SDK via Android Studio
- In Godot: Editor → Editor Settings → Export → Android
- Set SDK path (e.g., `C:\Users\YourName\AppData\Local\Android\Sdk`)

**"Build failed":**
- Ensure Java JDK 11 is installed
- Check console for specific error messages
- Verify all required Android build tools are installed

**"App crashes on startup":**
- Check logcat for error messages
- Verify minimum SDK version compatibility
- Ensure all required permissions are set
