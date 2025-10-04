# 🎓 Classroom Management System

A comprehensive classroom management system with web dashboard for teachers and mobile game integration for students.

## Features

### For Teachers (Web Dashboard)
- ✅ Create and manage classes with unique class codes
- ✅ Create assignments with multiple question types:
  - Multiple Choice
  - Yes/No Questions
  - Identification
  - Fill in the Blanks
  - Enumeration
  - Problem Solving
  - Essay Questions
- ✅ View student submissions and grades
- ✅ Monitor assignment progress
- ✅ Generate class reports
- ✅ Archive classes and restore later (hidden from Unity and student views)

### For Students (Mobile Games)
- ✅ Register and join classes using class codes
- ✅ Take assignments through mobile games (Unity or Godot)
- ✅ View scores and progress
- ✅ Leaderboards and gamification
- ✅ Offline mode with data caching

## Technology Stack

- **Backend**: Flask + FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Deployment**: Render (Cloud)
- **Mobile Game Clients**: 
  - Unity C# scripts (legacy)
  - **Godot 4.x** (new, recommended) - Complete mobile frontend
    - See `GodotFrontend/` directory for full implementation

## API Endpoints

### For Mobile Game Clients (Unity/Godot)
- `GET /api/classes` - Get all available classes
- `GET /api/assignment/{id}` - Get assignment questions
- `POST /api/submit/{id}` - Submit assignment answers
- `POST /api/student/register` - Register new student
- `POST /api/student/login` - Student login
- `POST /api/student/subjects` - Get student's enrolled subjects
- `POST /api/student/assignments` - Get assignments by subject
- `GET /api/leaderboard/{class_code}` - Get class leaderboard
- `GET /api/student/{id}/profile` - Get student profile
- See `MOBILE_INTEGRATION.md` for complete API documentation

### Web Dashboard
- `/` - Teacher dashboard
- `/login` - Teacher login
- `/register` - Teacher registration
- `/create_class` - Create new class
- `/create_assignment/{class_id}` - Create assignment

## Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   python app.py
   ```

3. **Access Application**
   - Teacher Dashboard: http://localhost:5000
   - Unity API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

4. **Default Admin Credentials**
    - Email: `admin@capstone.local`
    - Password: `Admin@12345`
    - You can override via environment variables before starting:
       ```powershell
       $env:ADMIN_EMAIL = "your.admin@example.com"
       $env:ADMIN_PASSWORD = "YourSecureP@ssw0rd"; python app.py
       ```
    - Admin URLs:
       - Login: `http://localhost:5000/admin/login`
       - Dashboard: `http://localhost:5000/admin`
       - Archived Classes: `http://localhost:5000/classes/archived`

## Production Deployment (Render)

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose branch: `main`
   - Settings will be auto-detected from `render.yaml`

3. **Configuration**
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python wsgi.py`

4. **Environment Variables** (automatically set by render.yaml)
   - `PORT`: 10000
   - `RENDER`: true
   - `PYTHON_VERSION`: 3.11.4
   - Optional (for default admin seeding):
     - `ADMIN_EMAIL`
     - `ADMIN_PASSWORD`

### After Deployment

Your app will be available at: `https://your-app-name.onrender.com`

**For Unity Games**: Update your Unity scripts to use the production URL:
```csharp
// Replace localhost URLs with your Render URL
string apiBaseUrl = "https://your-app-name.onrender.com";
```

## Unity Integration

### Update Your C# Scripts

Replace localhost URLs in your Unity scripts:

```csharp
// OLD (Development)
string apiUrl = "http://localhost:8001/api/assignment/" + assignmentId;

// NEW (Production)
string apiUrl = "https://your-app-name.onrender.com/api/assignment/" + assignmentId;
```

### Required Unity Scripts
- `BaseGameManager_ClassroomCode.cs`
- `DraggableAnswer.cs`
- `FillBlankDropZone.cs`
- `MultipleChoiceDragDropManager.cs`
- `LoginManager.cs`

## 🎮 Godot Frontend (NEW - Recommended)

A complete, production-ready Godot 4.x mobile educational game frontend is now available!

### Why Godot?
- ✅ **Open Source** - No licensing fees
- ✅ **Lightweight** - Smaller APK size (~30MB vs Unity's 100MB+)
- ✅ **Modern UI** - Built-in responsive design
- ✅ **Better Performance** - Native mobile optimization
- ✅ **Complete Solution** - All features implemented out-of-the-box

### Quick Start

1. **Open Godot Project**
   ```bash
   # Download Godot 4.2+ from https://godotengine.org
   # Open: GodotFrontend/project.godot
   ```

2. **Configure Backend URL**
   ```gdscript
   # Edit: GodotFrontend/scripts/managers/APIManager.gd
   var base_url: String = "https://your-app-name.onrender.com"
   ```

3. **Test in Editor** (F5)
   - Login/Registration flows
   - Subject browsing
   - Quiz taking
   - Leaderboard viewing

4. **Export to Android**
   - Project → Export → Android
   - Configure package name and permissions
   - Build APK
   - Install on device

### Features Included

**📱 Complete Mobile Experience:**
- Student authentication (login/register)
- Dynamic subject loading
- Multiple question types handler
- Real-time scoring and results
- Class leaderboard
- Student profile management
- Offline mode with caching
- Session persistence

**🎨 Professional UI:**
- Mobile-optimized layouts
- Touch-friendly controls
- Responsive design
- Loading indicators
- Error handling
- Smooth transitions

**🔧 Developer-Friendly:**
- Clean, documented code
- Modular architecture
- Singleton managers (autoloaded)
- Easy to customize
- Comprehensive guides

### Documentation

| Document | Description |
|----------|-------------|
| `GodotFrontend/README.md` | Complete project documentation |
| `GodotFrontend/QUICK_START.md` | Fast setup guide |
| `GodotFrontend/INTEGRATION_GUIDE.md` | Backend API integration details |
| `GodotFrontend/ANDROID_EXPORT_GUIDE.md` | Android build instructions |

### Project Structure
```
GodotFrontend/
├── scenes/              # Visual scenes
│   ├── auth/           # Login, Register
│   ├── menu/           # Main menu, Subject selection
│   ├── game/           # Quiz game, Results
│   └── ui/             # Leaderboard, Profile
├── scripts/
│   ├── managers/       # Core singletons
│   │   ├── APIManager.gd      # All API calls
│   │   ├── GameManager.gd     # Game state
│   │   └── DataManager.gd     # Local storage
│   ├── auth/           # Authentication logic
│   ├── menu/           # Menu controllers
│   ├── game/           # Quiz logic
│   └── ui/             # UI controllers
└── assets/             # Icons, fonts, sounds
```

### Key Files

**Core Managers (Auto-loaded):**
- `APIManager.gd` - All backend HTTP requests
- `GameManager.gd` - Scene navigation, student data
- `DataManager.gd` - Local caching, offline support

**Controllers:**
- `LoginController.gd` - Handles login screen
- `RegisterController.gd` - Handles registration
- `QuizController.gd` - Manages quiz gameplay
- `QuestionHandler.gd` - Renders different question types
- `LeaderboardController.gd` - Shows rankings
- `ProfileController.gd` - Profile management

### API Integration

The Godot frontend connects to all backend endpoints:

```gdscript
// Example: Login a student
APIManager.login_student(email, password)
await APIManager.login_completed
// GameManager automatically updates with student data

// Example: Load assignments
APIManager.get_student_assignments(student_id, "Mathematics")
await APIManager.assignments_loaded
// Display assignments in UI

// Example: Submit quiz
APIManager.submit_assignment(assignment_id, student_id, answers)
await APIManager.assignment_submitted
// Show results screen
```

### Mobile Testing

**In Godot Editor:**
- Enable touch emulation (automatic)
- Press F5 to run
- Click to simulate touch

**On Android Device:**
1. Export APK from Godot
2. Enable "Install from Unknown Sources"
3. Install APK
4. Test complete workflow

**Recommended Testing Flow:**
1. ✅ Register new student
2. ✅ Login with credentials
3. ✅ View subjects
4. ✅ Take quiz
5. ✅ Submit and see results
6. ✅ Check leaderboard
7. ✅ Update profile
8. ✅ Logout and re-login

### Migration from Unity

If you're currently using Unity:

1. **Both can coexist** - Keep Unity while testing Godot
2. **Same backend** - No changes needed to server
3. **Same database** - All student data compatible
4. **Test thoroughly** - Verify all features work
5. **Gradual rollout** - Deploy to small group first

### Advantages vs Unity

| Feature | Unity | Godot |
|---------|-------|-------|
| License | Free (with splash) | Fully open source |
| APK Size | ~100-150MB | ~30-40MB |
| Build Time | 5-10 minutes | 1-2 minutes |
| Learning Curve | Moderate-High | Moderate |
| Documentation | Extensive | Growing |
| Community | Very Large | Large |
| Mobile Performance | Good | Excellent |
| Code Language | C# | GDScript (Python-like) |

### Support

For Godot frontend issues:
1. Check `GodotFrontend/README.md` for setup
2. Review `INTEGRATION_GUIDE.md` for API details
3. Test backend endpoints at `/docs`
4. Report issues with "Godot" label on GitHub

## Unity Integration (Legacy)

## Testing

### Health Check
- Production: `https://your-app-name.onrender.com/health`
- Development: `http://localhost:5000/health`

### API Documentation
- Production: `https://your-app-name.onrender.com/docs`
- Development: `http://localhost:8001/docs`

## MuMu Player Testing

1. **Get Production URL** from Render
2. **Update Unity Scripts** with production URL
3. **Build APK** with updated URLs
4. **Install in MuMu Player**
5. **Test**: Registration → Login → Join Class → Take Assignment

## Question Types Supported

- ✅ **Multiple Choice**: Radio buttons with correct answer marking
- ✅ **Yes/No**: Simple binary choice questions
- ✅ **Identification**: Text input with exact match checking
- ✅ **Fill in the Blanks**: Multiple blank fields with pipe-separated answers
- ✅ **Enumeration**: List-based answers with partial credit
- ✅ **Problem Solving**: Step-by-step solution entry
- ✅ **Essay**: Manual grading by teachers

## Support

For issues or questions:
1. Check the `/health` endpoint for system status
2. View `/debug/info` for system information
3. Check Render logs for error details

## 🚀 Quick Deployment Guide

### 1. Deploy to Render
- Go to [Render Dashboard](https://dashboard.render.com/)
- Create new Web Service from GitHub repo
- Use build command: `pip install -r requirements.txt`
- Use start command: `gunicorn wsgi:app`

### 2. Update Unity Scripts
After deployment, replace `"https://your-app-name.onrender.com"` with your actual Render URL in these files:
- BaseGameManager_ClassroomCode.cs (serverURL)
- ClassCodeGate_Enhanced.cs (serverURL)
- DraggableAnswer.cs (flaskURL)
- FillBlankDropZone.cs (flaskServerUrl)
- All other Unity scripts with flaskURL

### 3. Test in MuMu Player
- Build Unity APK with production URLs
- Install in MuMu Player emulator
- Test complete student workflow

📖 **For detailed deployment instructions, see [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)**

## License

This project is licensed under the MIT License.
