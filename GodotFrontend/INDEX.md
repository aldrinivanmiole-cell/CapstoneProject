# 🎮 Godot Frontend - Quick Navigation Index

Welcome to the Godot Mobile Educational Game! This index will help you quickly find what you need.

## 📚 Start Here

**New to the project?** Start with these in order:
1. [README.md](README.md) - Complete project overview and setup
2. [QUICK_START.md](QUICK_START.md) - Get running in 5 minutes
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the system design

## 🎯 By Role

### For Developers
- **Setting Up**: [README.md](README.md) → Setup Instructions
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) → System Design
- **API Integration**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) → Backend Connection
- **Android Build**: [ANDROID_EXPORT_GUIDE.md](ANDROID_EXPORT_GUIDE.md) → Mobile Export
- **Code Reference**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) → Complete Overview

### For Students (End Users)
- **First Time**: [QUICK_START.md](QUICK_START.md) → "For Students" section
- **Troubleshooting**: [QUICK_START.md](QUICK_START.md) → "Common Issues" section

### For Teachers
- **Student Setup**: [QUICK_START.md](QUICK_START.md) → "For Teachers" section
- **Backend Docs**: See main project `MOBILE_INTEGRATION.md`

## 📂 By Task

### Installation & Setup
→ [README.md § Getting Started](README.md#-getting-started)

### Understanding the Code
→ [ARCHITECTURE.md](ARCHITECTURE.md)
→ [PROJECT_SUMMARY.md § Key Features](PROJECT_SUMMARY.md#-key-features)

### Backend Integration
→ [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
→ [INTEGRATION_GUIDE.md § API Endpoints](INTEGRATION_GUIDE.md#api-endpoints-mapping)

### Building for Android
→ [ANDROID_EXPORT_GUIDE.md](ANDROID_EXPORT_GUIDE.md)
→ [README.md § Building for Android](README.md#-building-for-android)

### Troubleshooting
→ [README.md § Troubleshooting](README.md#-troubleshooting)
→ [INTEGRATION_GUIDE.md § Common Issues](INTEGRATION_GUIDE.md#common-issues--solutions)

### Customization
→ [PROJECT_SUMMARY.md § Code Quality](PROJECT_SUMMARY.md#code-quality)
→ [assets/ASSETS_README.md](assets/ASSETS_README.md)

## 🗂️ File Structure Guide

### Configuration Files
- `project.godot` - Godot project configuration
- `.gitignore` - Git ignore rules

### Core Scripts (Managers)
Located in `scripts/managers/`:
- `APIManager.gd` - All HTTP requests to backend
- `GameManager.gd` - Game state and navigation
- `DataManager.gd` - Local storage and caching

### Scene Files
Located in `scenes/`:
- `Main.tscn` - Entry point
- `auth/LoginScreen.tscn` - Student login
- `auth/RegisterScreen.tscn` - Registration
- `menu/MainMenu.tscn` - Main menu
- `menu/SubjectSelection.tscn` - Subject browser
- `game/QuizGame.tscn` - Quiz gameplay
- `game/ResultScreen.tscn` - Results display
- `ui/Leaderboard.tscn` - Rankings
- `ui/Profile.tscn` - Student profile

### Controller Scripts
Located in `scripts/[category]/`:
- `auth/LoginController.gd`
- `auth/RegisterController.gd`
- `menu/MainMenuController.gd`
- `menu/SubjectSelectionController.gd`
- `game/QuizController.gd`
- `game/QuestionHandler.gd`
- `game/ResultScreenController.gd`
- `ui/LeaderboardController.gd`
- `ui/ProfileController.gd`

### Documentation
All `.md` files in root directory

### Assets
Located in `assets/`:
- `icons/` - App icons
- `fonts/` - Custom fonts (empty)
- `sounds/` - Audio files (empty)

## 🔍 Quick Search

### "How do I...?"

**...set up the project?**
→ [README.md § Getting Started](README.md#-getting-started)

**...configure the backend URL?**
→ [README.md § Getting Started](README.md#-getting-started) step 2
→ Edit: `scripts/managers/APIManager.gd` line 6

**...test in the editor?**
→ Press F5 or click Play button

**...build for Android?**
→ [ANDROID_EXPORT_GUIDE.md](ANDROID_EXPORT_GUIDE.md)

**...understand the architecture?**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**...add a new scene?**
→ [README.md § Creating New Scenes](README.md#creating-new-scenes)

**...call an API endpoint?**
→ [INTEGRATION_GUIDE.md § Calling API Endpoints](INTEGRATION_GUIDE.md#calling-api-endpoints)

**...handle offline mode?**
→ [INTEGRATION_GUIDE.md § Offline to Online Sync](INTEGRATION_GUIDE.md#example-3-offline-to-online-sync)

**...customize the UI?**
→ [README.md § UI/UX Guidelines](README.md#-uiux-guidelines)

**...debug network issues?**
→ [INTEGRATION_GUIDE.md § Debugging Tips](INTEGRATION_GUIDE.md#debugging-tips)

**...deploy to production?**
→ [ANDROID_EXPORT_GUIDE.md § Release Build](ANDROID_EXPORT_GUIDE.md#release-build)

## 📊 Statistics

- **Total Files**: 32
- **Code Files**: 13 GDScript + 9 Scenes
- **Documentation**: 7 comprehensive guides
- **Total Lines**: ~2,500+ code lines
- **Project Size**: ~236KB
- **Estimated APK Size**: 30-40MB

## 🔗 Related Resources

### External Links
- [Godot Engine](https://godotengine.org) - Download Godot
- [Godot Docs](https://docs.godotengine.org/en/stable/) - Official documentation
- [GDScript Style Guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)

### Project Links
- Main README: `../README.md`
- Backend Integration: `../MOBILE_INTEGRATION.md`
- Unity Scripts: `../Unity-Scripts/`

## 🆘 Getting Help

1. **Check documentation** - Likely answered in docs above
2. **Test backend** - Visit `/docs` endpoint on server
3. **Check console** - Godot Output tab shows errors
4. **Review logs** - Backend logs on Render dashboard
5. **Report issues** - GitHub issues with "Godot" label

## 🚀 Quick Commands

```bash
# Open project in Godot Editor
godot project.godot

# Run in editor (keyboard shortcut)
F5

# View a specific scene
godot scenes/Main.tscn

# Export to Android (via GUI)
Project → Export → Android → Export Project
```

## 📋 Checklist

### First Time Setup
- [ ] Install Godot 4.2+
- [ ] Open `project.godot`
- [ ] Update `base_url` in `APIManager.gd`
- [ ] Press F5 to test
- [ ] Try login/register flow

### Before Deploying
- [ ] Test all features
- [ ] Update backend URL to production
- [ ] Configure Android export
- [ ] Build signed APK
- [ ] Test on real device
- [ ] Update app icon (optional)

### Regular Development
- [ ] Pull latest changes
- [ ] Test in editor
- [ ] Make changes
- [ ] Test again
- [ ] Commit to Git

## 📖 Documentation Map

```
README.md (10,000+ words)
├── Project Overview
├── Features
├── Getting Started
├── Manager Systems
├── Building for Android
├── Development Guide
├── UI/UX Guidelines
├── Troubleshooting
└── API Integration

QUICK_START.md (5,800+ words)
├── For Developers (5-min setup)
├── For Students (using the app)
└── For Teachers (student support)

INTEGRATION_GUIDE.md (11,000+ words)
├── Architecture Diagram
├── API Endpoints Mapping
├── Data Flow Examples
├── Request/Response Format
├── Error Handling
├── Security
├── Testing
├── Debugging
└── Performance

ANDROID_EXPORT_GUIDE.md (2,200+ words)
├── Setup Steps
├── Essential Settings
├── Keystore Signing
├── Testing
└── Common Issues

PROJECT_SUMMARY.md (11,000+ words)
├── What's Included
├── Project Structure
├── Features
├── Code Quality
├── Testing
└── Deployment

ARCHITECTURE.md (14,800+ words)
├── System Diagram
├── Data Flow
├── Component Interactions
├── Dependency Tree
└── Design Patterns

ASSETS_README.md (1,600+ words)
├── Icon Guide
├── Font Guide
├── Sound Guide
└── License Compliance
```

## 🎓 Learning Path

**Beginner** (Day 1)
1. Read [QUICK_START.md](QUICK_START.md)
2. Follow setup steps
3. Run in editor
4. Explore scenes

**Intermediate** (Day 2-3)
1. Read [README.md](README.md)
2. Study [ARCHITECTURE.md](ARCHITECTURE.md)
3. Review manager scripts
4. Modify a controller

**Advanced** (Day 4+)
1. Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Study API calls
3. Add new features
4. Build for Android

## 🎯 Common Workflows

### Adding a New Feature
1. Create scene file (`.tscn`)
2. Create controller script (`.gd`)
3. Add scene to `GameManager.SCENES`
4. Connect to API if needed
5. Test in editor
6. Update documentation

### Fixing a Bug
1. Identify bug location
2. Check console for errors
3. Review relevant controller
4. Test fix in editor
5. Verify on Android
6. Commit fix

### Updating UI
1. Open scene in Godot editor
2. Modify UI elements
3. Update controller if needed
4. Test in editor
5. Verify responsive design
6. Build and test on device

---

**Ready to Code? Start with [QUICK_START.md](QUICK_START.md)!** 🚀
