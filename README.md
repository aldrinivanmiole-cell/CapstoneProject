# 🎓 Classroom Management System

A comprehensive classroom management system with web dashboard for teachers and API for Unity games.

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

### For Students (Unity Games)
- ✅ Register and join classes using class codes
- ✅ Take assignments through Unity games
- ✅ View scores and progress
- ✅ Leaderboards and gamification

## Technology Stack

- **Backend**: Flask + FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Deployment**: Render (Cloud)
- **Game Integration**: Unity C# scripts

## API Endpoints

### For Unity Games
- `GET /api/classes` - Get all available classes
- `GET /api/assignment/{id}` - Get assignment questions
- `POST /api/submit/{id}` - Submit assignment answers
- `POST /api/student/register` - Register new student
- `POST /api/student/login` - Student login

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
