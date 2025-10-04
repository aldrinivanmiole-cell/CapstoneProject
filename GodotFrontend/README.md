# Godot Mobile Educational Game Frontend

A complete Godot 4.x mobile educational game that connects to the Classroom Management System backend.

## 📱 Features

### Core Functionality
- ✅ **Student Authentication** - Login and registration with secure API integration
- ✅ **Subject Management** - Dynamic subject loading from backend classes
- ✅ **Assignment System** - Multiple question types support:
  - Multiple Choice
  - Yes/No Questions
  - Fill in the Blanks
  - Short Answer
  - Identification
  - Enumeration
- ✅ **Leaderboard** - Class rankings and progress tracking
- ✅ **Profile Management** - Student profile with points and avatar
- ✅ **Offline Support** - Local caching and queued submissions
- ✅ **Mobile Optimized** - Touch-friendly UI for Android devices

## 🏗️ Project Structure

```
GodotFrontend/
├── project.godot              # Godot project configuration
├── scenes/                    # Scene files (.tscn)
│   ├── Main.tscn             # Entry point/splash screen
│   ├── auth/
│   │   ├── LoginScreen.tscn
│   │   └── RegisterScreen.tscn
│   ├── menu/
│   │   ├── MainMenu.tscn
│   │   └── SubjectSelection.tscn
│   ├── game/
│   │   ├── QuizGame.tscn
│   │   └── ResultScreen.tscn
│   └── ui/
│       ├── Leaderboard.tscn
│       └── Profile.tscn
├── scripts/                   # GDScript files (.gd)
│   ├── Main.gd
│   ├── managers/             # Singleton managers (autoloaded)
│   │   ├── APIManager.gd    # Backend API communication
│   │   ├── GameManager.gd   # Game state & scene management
│   │   └── DataManager.gd   # Local data persistence
│   ├── auth/
│   │   ├── LoginController.gd
│   │   └── RegisterController.gd
│   ├── menu/
│   │   ├── MainMenuController.gd
│   │   └── SubjectSelectionController.gd
│   └── game/
│       ├── QuizController.gd
│       └── QuestionHandler.gd
└── assets/                   # Game assets
    ├── icons/               # App icons and UI icons
    ├── fonts/               # Custom fonts
    └── sounds/              # Audio files
```

## 🚀 Getting Started

### Prerequisites
- **Godot Engine 4.2+** ([Download](https://godotengine.org/download))
- Active internet connection for API calls
- Backend server running (see main README.md)

### Setup Instructions

1. **Open the Project**
   - Launch Godot Engine
   - Click "Import"
   - Navigate to `GodotFrontend/project.godot`
   - Click "Import & Edit"

2. **Configure Backend URL**
   - Open `scripts/managers/APIManager.gd`
   - Update `base_url` with your backend URL:
     ```gdscript
     var base_url: String = "https://your-app-name.onrender.com"
     # For local testing: "http://localhost:8001"
     ```

3. **Test in Editor**
   - Press F5 or click "Run Project"
   - Test login/registration flows
   - Verify API connectivity

## 🎮 Manager Systems

### APIManager (Singleton)
Handles all HTTP requests to the backend. Auto-loaded globally.

**Key Methods:**
```gdscript
APIManager.login_student(email, password, device_id)
APIManager.register_student(name, email, password, grade_level, avatar_url)
APIManager.get_student_profile(student_id)
APIManager.get_student_subjects(student_id)
APIManager.get_student_assignments(student_id, subject)
APIManager.submit_assignment(assignment_id, student_id, answers)
APIManager.get_leaderboard(class_code, top_n)
APIManager.update_avatar(student_id, avatar_url)
```

**Signals:**
```gdscript
signal login_completed(success: bool, data: Dictionary)
signal register_completed(success: bool, data: Dictionary)
signal profile_loaded(success: bool, data: Dictionary)
signal subjects_loaded(success: bool, data: Dictionary)
signal assignments_loaded(success: bool, data: Dictionary)
signal assignment_submitted(success: bool, data: Dictionary)
signal leaderboard_loaded(success: bool, data: Dictionary)
signal api_error(error_message: String)
```

### GameManager (Singleton)
Manages game state, student data, and scene transitions. Auto-loaded globally.

**Key Properties:**
```gdscript
var student_id: int
var student_name: String
var student_email: String
var student_points: int
var enrolled_classes: Array
var current_subject: String
var current_questions: Array
```

**Key Methods:**
```gdscript
GameManager.login(student_data)
GameManager.logout()
GameManager.change_scene(scene_key, params)
GameManager.load_assignment(assignment_data)
GameManager.save_answer(question_id, answer)
GameManager.get_student_info()
```

### DataManager (Singleton)
Handles local data storage and offline capabilities. Auto-loaded globally.

**Key Methods:**
```gdscript
DataManager.save_session(session_data)
DataManager.load_session()
DataManager.cache_subjects(subjects)
DataManager.cache_assignments(subject, assignments)
DataManager.queue_submission(assignment_id, student_id, answers)
DataManager.clear_all_data()
```

## 📲 Building for Android

### 1. Install Android Build Template
- In Godot: Project → Install Android Build Template

### 2. Configure Export Settings
- Go to Project → Export
- Add Android preset
- Configure settings:
  - **Package Name**: `com.yourschool.classroomgame`
  - **Min SDK**: 21 (Android 5.0)
  - **Target SDK**: 33 (Android 13)
  - **Permissions**: Internet, Access Network State

### 3. Export APK
- Select Android preset
- Click "Export Project"
- Choose output location
- Build APK

### 4. Test on Device
- Enable USB Debugging on Android device
- Connect device
- Use "One-Click Deploy" in Godot

## 🔧 Development Guide

### Creating New Scenes

1. **Create Scene File** (`scenes/yourscene/YourScene.tscn`)
2. **Create Controller Script** (`scripts/yourscene/YourSceneController.gd`)
3. **Add Scene to GameManager**:
   ```gdscript
   const SCENES = {
       "your_scene": "res://scenes/yourscene/YourScene.tscn"
   }
   ```

### Calling API Endpoints

```gdscript
# Connect to signal first
APIManager.some_api_completed.connect(_on_api_response)

# Make API call
APIManager.some_api_call(params)

# Handle response
func _on_api_response(success: bool, data: Dictionary):
    if success:
        print("Success: ", data)
    else:
        print("Error: ", data.get("error"))
```

### Scene Transitions

```gdscript
# Simple transition
GameManager.change_scene("main_menu")

# With parameters
GameManager.change_scene("quiz_game", {"subject": "Mathematics"})

# In target scene, retrieve parameters
func _ready():
    var params = GameManager.get_scene_params()
    var subject = params.get("subject", "")
```

### Local Data Storage

```gdscript
# Save setting
DataManager.save_setting("music_volume", 0.8)

# Load setting
var volume = DataManager.load_setting("music_volume", 1.0)

# Cache data for offline
DataManager.cache_subjects(subjects_array)

# Get cached data
var subjects = DataManager.get_cached_subjects()
```

## 🎨 UI/UX Guidelines

### Mobile Touch Targets
- **Minimum button size**: 60x60 pixels
- **Recommended spacing**: 20 pixels between elements
- **Safe area margins**: 50 pixels from screen edges

### Screen Orientations
- **Portrait mode** (default): 1080x1920
- Landscape support optional for specific screens

### Color Scheme
- **Background**: Dark blue/gray (#333344)
- **Panels**: Lighter gray (#3A3F50)
- **Primary buttons**: Blue (#4A90E2)
- **Success**: Green (#67C23A)
- **Error**: Red (#F56C6C)

## 🧪 Testing

### Manual Testing Checklist
- [ ] Registration with valid data
- [ ] Login with correct credentials
- [ ] Login with incorrect credentials
- [ ] Subject list loading
- [ ] Assignment loading for each subject
- [ ] Answering all question types
- [ ] Submission and result display
- [ ] Leaderboard display
- [ ] Profile update
- [ ] Logout and session persistence
- [ ] Offline mode (airplane mode)

### Network Error Simulation
1. Enable airplane mode on device
2. Attempt API calls
3. Verify error messages
4. Re-enable network
5. Verify cached data still available

## 🐛 Troubleshooting

### "Cannot connect to server"
- Verify `base_url` in APIManager.gd
- Check internet connection
- Ensure backend server is running
- Try using IP address instead of domain for local testing

### "Scene not found" errors
- Verify scene paths in GameManager.SCENES
- Ensure all scene files exist
- Check for typos in scene names

### Android export fails
- Install Android SDK properly
- Check Java JDK version (11 recommended)
- Verify export template is installed
- Check console for specific errors

### UI elements not responsive
- Ensure layout_mode is set correctly
- Check anchors and size flags
- Test with different screen resolutions
- Verify touch input is enabled

## 📚 Backend Integration

This project connects to the Classroom Management System backend. API endpoints used:

- `POST /api/student/register` - Student registration
- `POST /api/student/login` - Student authentication
- `GET /api/student/{id}/profile` - Get profile data
- `POST /api/student/subjects` - Get enrolled subjects
- `POST /api/student/assignments` - Get assignments by subject
- `POST /api/submit/{id}` - Submit assignment answers
- `GET /api/leaderboard/{class_code}` - Get class rankings
- `PUT /api/student/{id}/avatar` - Update avatar

See `MOBILE_INTEGRATION.md` in the root directory for detailed API documentation.

## 🔐 Security Notes

- Student passwords are sent securely over HTTPS
- Session data is stored locally using Godot's encrypted file access
- Device ID is used to prevent duplicate registrations
- No sensitive data is logged to console in production builds

## 📄 License

This project is part of the Classroom Management System.
Licensed under the MIT License.

## 🤝 Contributing

1. Create feature branch from `main`
2. Make changes and test thoroughly
3. Ensure code follows GDScript style guide
4. Submit pull request with description

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review backend API documentation
- Contact development team

---

**Version**: 1.0.0  
**Godot Version**: 4.2+  
**Target Platform**: Android 5.0+  
**Backend Compatibility**: Flask/FastAPI Classroom Management System
