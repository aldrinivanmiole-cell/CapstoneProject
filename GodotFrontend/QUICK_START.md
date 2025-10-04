# Quick Start Guide - Godot Educational Game

## For Developers

### First Time Setup (5 minutes)

1. **Install Godot**
   - Download Godot 4.2+ from https://godotengine.org/download
   - Extract and run the executable

2. **Open Project**
   - Launch Godot
   - Click "Import"
   - Navigate to `GodotFrontend/project.godot`
   - Click "Import & Edit"

3. **Configure Backend URL**
   ```gdscript
   # Edit: scripts/managers/APIManager.gd
   # Line ~6:
   var base_url: String = "https://capstoneproject-jq2h.onrender.com"
   # Or for local testing:
   # var base_url: String = "http://localhost:8001"
   ```

4. **Test in Editor**
   - Press F5 or click the Play button
   - Test with demo credentials or create new account

### Project Structure Overview

```
GodotFrontend/
├── scenes/           # Visual scenes (.tscn files)
├── scripts/          # Game logic (.gd files)
│   ├── managers/     # Global singletons (autoloaded)
│   ├── auth/         # Login/registration
│   ├── menu/         # Navigation screens
│   ├── game/         # Quiz/game logic
│   └── ui/           # Leaderboard, profile, etc.
└── assets/           # Graphics, sounds, fonts
```

### Key Files to Know

| File | Purpose |
|------|---------|
| `project.godot` | Project configuration |
| `scripts/managers/APIManager.gd` | All backend API calls |
| `scripts/managers/GameManager.gd` | Game state & navigation |
| `scripts/managers/DataManager.gd` | Local storage |
| `scenes/Main.tscn` | Entry point scene |

### Testing Workflow

1. **Run in Editor** (F5)
   - Quick testing
   - Debug console available
   - Hot reload support

2. **Export to Android**
   - Project → Export
   - Select Android preset
   - Click "Export Project"
   - Install APK on device

3. **Test Offline Mode**
   - Run app with internet
   - Load some data
   - Enable airplane mode
   - Verify cached data still works

## For Students (Using the App)

### First Time Use

1. **Install the App**
   - Download APK file
   - Enable "Install from Unknown Sources"
   - Install and open

2. **Create Account**
   - Tap "Create New Account"
   - Enter your name and email
   - Choose your grade level
   - Create a password (min 6 characters)

3. **Join a Class**
   - After registration, go to Profile
   - Tap "Join New Class"
   - Enter class code from your teacher
   - You'll see the class in your profile

4. **Take Assignments**
   - From main menu, tap "My Subjects"
   - Select a subject
   - Choose an assignment to complete
   - Answer questions and submit

5. **View Progress**
   - Check your points on main menu
   - View "Leaderboard" to see class rankings
   - View "Profile" to see enrolled classes

### Tips for Students

- ✅ Complete assignments on time for full points
- ✅ Review leaderboard to track your progress
- ✅ Take your time reading questions carefully
- ✅ You can join multiple classes
- ✅ Points accumulate across all assignments

### Common Issues

**"Cannot connect to server"**
- Check your internet connection
- Ask your teacher if the server is working

**"Invalid class code"**
- Double-check the code with your teacher
- Make sure there are no extra spaces

**"Login failed"**
- Verify your email and password
- Use "Forgot Password" if available

## For Teachers

### Setting Up for Students

1. **Provide Class Code**
   - Share your class code with students
   - Students enter this during registration or in Profile

2. **Create Assignments**
   - Use the web dashboard (not the app)
   - Create assignments with various question types
   - Students will see them in the app

3. **Monitor Progress**
   - Check web dashboard for student submissions
   - View leaderboard to see top performers
   - Grade essay/problem-solving questions

### Student Support

**If student can't register:**
- Verify class code is correct
- Check if student already has account (duplicate email)
- Ensure backend server is running

**If assignment doesn't appear:**
- Verify assignment is not archived
- Check student is enrolled in correct class
- Ask student to refresh (pull down to refresh)

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/student/register` | POST | Create student account |
| `/api/student/login` | POST | Student authentication |
| `/api/student/{id}/profile` | GET | Get student profile |
| `/api/student/subjects` | POST | Get enrolled subjects |
| `/api/student/assignments` | POST | Get assignments |
| `/api/submit/{id}` | POST | Submit assignment |
| `/api/leaderboard/{code}` | GET | Get class leaderboard |
| `/api/student/join-class` | POST | Join class with code |

## Development Roadmap

### Phase 1 - Core Features ✅
- [x] Authentication system
- [x] Subject browsing
- [x] Quiz/assignment system
- [x] Result display
- [x] Leaderboard
- [x] Profile management

### Phase 2 - Enhancements (Future)
- [ ] Offline quiz taking
- [ ] Push notifications
- [ ] Avatar customization
- [ ] Achievements/badges
- [ ] Study mode (review questions)
- [ ] Timer mode for timed quizzes
- [ ] Audio/video question support
- [ ] Multi-language support

### Phase 3 - Advanced Features (Future)
- [ ] AR/VR quiz modes
- [ ] Multiplayer quiz battles
- [ ] AI study assistant
- [ ] Parent portal integration
- [ ] Analytics dashboard in-app

## Contributing

To contribute to this project:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Test thoroughly
4. Commit changes (`git commit -m 'Add AmazingFeature'`)
5. Push to branch (`git push origin feature/AmazingFeature`)
6. Open Pull Request

## Support & Documentation

- **Full Documentation**: See `README.md`
- **Android Export**: See `ANDROID_EXPORT_GUIDE.md`
- **Backend API**: See main project `MOBILE_INTEGRATION.md`
- **Issues**: Report on GitHub issue tracker

---

**Happy Learning! 🎓📱**
