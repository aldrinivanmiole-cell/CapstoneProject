# Godot Frontend - Backend Integration Guide

This guide explains how the Godot mobile game connects to the FastAPI/Flask backend.

## Architecture Overview

```
┌─────────────────────────┐
│   Godot Mobile App      │
│   (Student Device)      │
└───────────┬─────────────┘
            │ HTTPS/API
            │
┌───────────▼─────────────┐
│   FastAPI Backend       │
│   (Render Cloud)        │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│   SQLite Database       │
│   (school.db)           │
└─────────────────────────┘
```

## API Endpoints Mapping

### Authentication & Registration

**Student Registration**
```
Godot: APIManager.register_student()
  ↓
Backend: POST /api/student/register
  ↓
Database: Creates Student record + Enrollment
```

**Student Login**
```
Godot: APIManager.login_student()
  ↓
Backend: POST /api/student/login
  ↓
Response: Student data + enrolled classes
  ↓
Godot: GameManager.login(data)
  ↓
DataManager: Saves session locally
```

### Data Loading

**Get Student Subjects**
```
Flow: MainMenu → SubjectSelection
  ↓
Godot: APIManager.get_student_subjects(student_id)
  ↓
Backend: POST /api/student/subjects
  ↓
Response: List of enrolled classes/subjects
  ↓
Godot: Displays subject buttons
DataManager: Caches for offline use
```

**Get Assignments by Subject**
```
Flow: SubjectSelection → QuizGame
  ↓
Godot: APIManager.get_student_assignments(student_id, subject)
  ↓
Backend: POST /api/student/assignments
  ↓
Response: Assignment list with questions
  ↓
Godot: GameManager.load_assignment(data)
       QuizController displays questions
```

### Assignment Submission

**Submit Quiz Answers**
```
Flow: QuizGame → Submit → ResultScreen
  ↓
Godot: APIManager.submit_assignment(assignment_id, student_id, answers)
  ↓
Backend: POST /api/submit/{assignment_id}
  ↓
Processing: 
  - Grades answers automatically
  - Calculates score & percentage
  - Updates student.total_points
  - Stores submission in database
  ↓
Response: Results with score, grade, points
  ↓
Godot: ResultScreenController displays results
       GameManager.add_points() updates local data
```

### Leaderboard & Profile

**Get Leaderboard**
```
Godot: APIManager.get_leaderboard(class_code)
  ↓
Backend: GET /api/leaderboard/{class_code}
  ↓
Response: Top students ranked by points
  ↓
Godot: LeaderboardController displays list
```

**Get/Update Profile**
```
Godot: APIManager.get_student_profile(student_id)
  ↓
Backend: GET /api/student/{student_id}/profile
  ↓
Response: Complete student data + classes
  ↓
Godot: ProfileController updates UI
```

## Data Flow Examples

### Example 1: First Time User Registration

1. **Student opens app** → `Main.tscn` checks session
2. **No session found** → Navigates to `LoginScreen.tscn`
3. **User taps "Register"** → Navigates to `RegisterScreen.tscn`
4. **User fills form** → Controller validates data
5. **Taps Register button** → `APIManager.register_student()`
6. **Backend creates account** → Returns success + student_id
7. **App saves student_id** → Via DataManager
8. **Navigates to Login** → User can now login

### Example 2: Taking a Quiz

1. **Student logs in** → Session restored, goes to `MainMenu.tscn`
2. **Taps "My Subjects"** → `SubjectSelection.tscn` loads
3. **API loads subjects** → `get_student_subjects()`
4. **Student selects Math** → `QuizGame.tscn` loads
5. **API loads assignments** → `get_student_assignments(Math)`
6. **Student answers Q1-Q10** → `QuizController` tracks answers
7. **Taps Submit** → `submit_assignment()` called
8. **Backend grades** → Calculates score automatically
9. **Returns results** → `ResultScreen.tscn` displays
10. **Points updated** → Reflected in profile

### Example 3: Offline to Online Sync

1. **Student is offline** → Network request fails
2. **APIManager emits error** → "Cannot connect to server"
3. **DataManager has cache** → Shows cached subjects/assignments
4. **Student takes quiz** → Answers saved locally
5. **Submit fails (offline)** → `queue_submission()` called
6. **Internet restored** → Next API call detects connection
7. **Process queue** → Submits pending submissions
8. **Updates profile** → Fresh data from server

## Backend URL Configuration

### Development (Local)
```gdscript
# In APIManager.gd
var base_url: String = "http://localhost:8001"
```

### Production (Render)
```gdscript
# In APIManager.gd
var base_url: String = "https://capstoneproject-jq2h.onrender.com"
```

**Important:** Always use HTTPS in production for security!

## Request/Response Format

### Sample Request: Login
```json
POST /api/student/login
Content-Type: application/json

{
  "email": "student@school.com",
  "password": "password123",
  "device_id": "abc123xyz456"
}
```

### Sample Response: Login Success
```json
{
  "status": "success",
  "student": {
    "id": 42,
    "name": "John Doe",
    "email": "student@school.com",
    "grade_level": "Grade 5",
    "total_points": 150
  },
  "classes": [
    {
      "id": 1,
      "name": "Mathematics",
      "section": "5-A",
      "class_code": "MATH101A",
      "teacher_name": "Ms. Smith"
    }
  ],
  "message": "Login successful"
}
```

### Sample Request: Submit Assignment
```json
POST /api/submit/5
Content-Type: application/json

{
  "student_id": 42,
  "answers": {
    "1": "Paris",
    "2": "Blue",
    "3": "42"
  }
}
```

### Sample Response: Submission Result
```json
{
  "status": "success",
  "results": {
    "score": 25,
    "total_points": 30,
    "percentage": 83.3,
    "grade": "B",
    "points_earned": 25,
    "correct_count": 2,
    "incorrect_count": 1
  }
}
```

## Error Handling

### Network Errors
```gdscript
# In any controller
APIManager.api_error.connect(_on_api_error)

func _on_api_error(error_message: String):
    # Display user-friendly message
    show_message("Network error: " + error_message)
    
    # Try to use cached data
    var cached_data = DataManager.get_cached_subjects()
    if not cached_data.is_empty():
        display_cached_data(cached_data)
```

### HTTP Errors
- **400**: Bad request - Check data format
- **401**: Unauthorized - Invalid credentials
- **404**: Not found - Resource doesn't exist
- **503**: Service unavailable - Maintenance mode or API disabled

### Godot HTTP Result Codes
```gdscript
match result:
    HTTPRequest.RESULT_SUCCESS:
        # Request successful
    HTTPRequest.RESULT_CANT_CONNECT:
        # No internet or server down
    HTTPRequest.RESULT_TIMEOUT:
        # Request took too long
    HTTPRequest.RESULT_SSL_HANDSHAKE_ERROR:
        # HTTPS certificate issue
```

## Security Considerations

### 1. HTTPS Only in Production
- All API calls use HTTPS
- Protects passwords and sensitive data
- Prevents man-in-the-middle attacks

### 2. Password Security
- Passwords never stored in Godot app
- Only sent during login/registration
- Backend hashes passwords with bcrypt

### 3. Session Management
- Session data stored in encrypted file
- Device ID used for tracking
- Auto-logout after inactivity (future feature)

### 4. Data Validation
- All inputs validated before sending
- Email format checked
- Password length enforced
- SQL injection not possible (using ORM)

## Testing API Integration

### Using Godot Editor
```gdscript
# In any script
func test_api():
    APIManager.login_student("test@school.com", "password123")
    await APIManager.login_completed
    print("Login test complete")
```

### Using Backend Docs
- Visit: `https://your-backend.onrender.com/docs`
- Interactive API testing interface
- Try endpoints before implementing in Godot

### Using curl
```bash
# Test login endpoint
curl -X POST https://your-backend.onrender.com/api/student/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@school.com","password":"test123"}'
```

## Debugging Tips

### 1. Enable Debug Logging
```gdscript
# In APIManager.gd
print("[APIManager] POST: ", url)
print("[APIManager] Data: ", json_data)
print("[APIManager] Response: ", body_text)
```

### 2. Check Backend Logs
- Go to Render Dashboard
- View Logs tab
- Look for errors or request details

### 3. Test Backend Separately
- Use the web dashboard
- Verify data exists in database
- Confirm endpoints work via browser

### 4. Network Inspector
```gdscript
# Monitor all requests
APIManager.api_error.connect(func(err):
    push_error("API Error: " + err)
)
```

## Common Issues & Solutions

### "Cannot connect to server"
**Solution:**
- Check internet connection
- Verify `base_url` is correct
- Ensure backend is running (visit URL in browser)
- Check for firewall blocking

### "Invalid response format"
**Solution:**
- Backend might be down
- API endpoint changed
- Check response body in logs
- Verify Content-Type headers

### "Student not found"
**Solution:**
- Student might not be registered
- Database might be reset
- Check student_id in session

### Data not updating
**Solution:**
- Clear cache: `DataManager.clear_cache()`
- Logout and login again
- Check if using cached vs live data

## Performance Optimization

### 1. Caching Strategy
```gdscript
# Cache responses for offline use
DataManager.cache_subjects(subjects)
DataManager.cache_assignments(subject, assignments)

# Use cached data when offline
if not is_online:
    var cached = DataManager.get_cached_subjects()
    if not cached.is_empty():
        display_subjects(cached)
```

### 2. Request Batching
- Load all data needed for a screen at once
- Avoid multiple sequential API calls
- Use combined endpoints when available

### 3. Timeout Management
```gdscript
# In APIManager.gd
var api_timeout: float = 30.0  # Seconds

# Adjust based on network quality
if is_slow_connection():
    api_timeout = 60.0
```

## Future Enhancements

### Planned Features
- [ ] WebSocket for real-time updates
- [ ] Push notifications for new assignments
- [ ] Batch submission sync
- [ ] Offline quiz mode with later sync
- [ ] Avatar upload/download
- [ ] Chat with teacher (future)

### API Changes Needed
- Add WebSocket endpoint for live updates
- File upload endpoint for avatars
- Batch operations endpoint
- Notification service integration

---

## Quick Reference Card

| Feature | Endpoint | Godot Method |
|---------|----------|--------------|
| Register | `POST /api/student/register` | `APIManager.register_student()` |
| Login | `POST /api/student/login` | `APIManager.login_student()` |
| Get Profile | `GET /api/student/{id}/profile` | `APIManager.get_student_profile()` |
| Get Subjects | `POST /api/student/subjects` | `APIManager.get_student_subjects()` |
| Get Assignments | `POST /api/student/assignments` | `APIManager.get_student_assignments()` |
| Submit Quiz | `POST /api/submit/{id}` | `APIManager.submit_assignment()` |
| Leaderboard | `GET /api/leaderboard/{code}` | `APIManager.get_leaderboard()` |
| Join Class | `POST /api/student/join-class` | `APIManager.join_class()` |
| Update Avatar | `PUT /api/student/{id}/avatar` | `APIManager.update_avatar()` |

---

**Need Help?**
- Check main README.md for setup
- Review MOBILE_INTEGRATION.md for API details
- Test endpoints at `/docs` on backend
- Report issues on GitHub
