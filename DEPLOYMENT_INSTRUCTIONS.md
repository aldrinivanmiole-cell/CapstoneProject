# 🚀 Deployment Instructions

## 📋 Prerequisites
- GitHub account
- Render account (free tier available)
- Unity project with updated scripts

## 🌐 Deploy to Render

### Step 1: Deploy Flask App to Render

1. **Login to Render Dashboard**
   - Go to [render.com](https://render.com)
   - Login with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `CapstoneProject`
   - Select the repository from the list

3. **Configure Web Service**
   - **Name**: `capstone-classroom-system` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Root Directory**: Leave empty (uses root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`

4. **Environment Variables** (Optional)
   - Add any environment variables if needed
   - For basic deployment, none required

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your app will be available at: `https://your-app-name.onrender.com`

### Step 2: Update Unity Scripts

After successful deployment, you'll get a URL like: `https://capstone-classroom-system.onrender.com`

**Replace the placeholder URL in ALL Unity scripts:**

1. Open each Unity script file
2. Find the line: `public string flaskURL = "https://your-app-name.onrender.com";`
3. Replace `"https://your-app-name.onrender.com"` with your actual Render URL
4. Example: `public string flaskURL = "https://capstone-classroom-system.onrender.com";`

**Scripts to update:**
- BaseGameManager_ClassroomCode.cs (serverURL variable)
- ClassCodeGate_Enhanced.cs (serverURL variable)
- DraggableAnswer.cs (flaskURL variable)
- FillBlankDropZone.cs (flaskServerUrl variable)
- DynamicStagePanel.cs (flaskURL variable)
- GameStageManager.cs (flaskURL variable)
- GenderSelection.cs (flaskURL variable)
- GoToClassList.cs (flaskURL variable)
- GoToMainMenu.cs (flaskURL variable)
- InputFieldGameManager.cs (flaskURL variable)
- LoginManager.cs (flaskURL variable)
- MultipleChoiceDragDropManager.cs (flaskURL variable)
- OpenHint.cs (flaskURL variable)

### Step 3: Test Deployment

1. **Test Web Dashboard**
   - Visit your Render URL
   - Register a teacher account
   - Create a class and assignment
   - Verify all question types work (Multiple Choice, Fill in the Blank, Yes/No)

2. **Test Unity Integration**
   - Build your Unity project with updated scripts
   - Test in MuMu Player emulator
   - Verify student registration and class joining
   - Test all question types

## 🔧 Local Development

For local development, change URLs back to:
```csharp
public string flaskURL = "http://127.0.0.1:5000";
```

## 🐛 Troubleshooting

### Common Issues:

1. **Deployment Failed**
   - Check Render logs for errors
   - Verify all dependencies in requirements.txt
   - Ensure wsgi.py is properly configured

2. **Unity Can't Connect**
   - Verify the Render URL is correct
   - Check if the app is running (visit URL in browser)
   - Ensure HTTPS is used (not HTTP)

3. **Database Issues**
   - Render automatically creates SQLite database
   - Check Render logs for database initialization errors

4. **CORS Issues**
   - Flask app already has CORS configured
   - If issues persist, check Render logs

### Render Logs Access:
1. Go to your Render dashboard
2. Click on your web service
3. Go to "Logs" tab to see runtime logs

## 📱 MuMu Player Testing

1. Install MuMu Player emulator
2. Install your Unity APK in the emulator
3. Test complete workflow:
   - Student registration
   - Class joining with teacher's class code
   - Assignment completion
   - Score submission

## 🔄 Updates

To update your deployed app:
1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically redeploy

## 🎯 Production Ready Features

✅ **Implemented:**
- Complete yes/no question support
- Unity-Flask integration
- Teacher dashboard
- Student progress tracking
- Production WSGI configuration
- Render deployment setup

✅ **Question Types Supported:**
- Multiple Choice
- Fill in the Blank
- Yes/No questions

✅ **Unity Integration:**
- All game scripts connected to Flask
- Complete API endpoint coverage
- Production URL configuration
