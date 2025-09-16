# Mobile App Student Registration & Data Storage

## Overview
Students register through the Unity mobile app and their data is stored in the same SQLite database (`school.db`) used by the teacher dashboard. This creates a unified system where teachers can monitor student progress in real-time.

## Student Data Structure

### Enhanced Student Model
```python
class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Mobile App Specific Fields
    device_id = Column(String(255))        # Unique device identifier
    grade_level = Column(String(50))       # Student's grade level
    avatar_url = Column(String(500))       # Profile avatar image URL
    total_points = Column(Integer, default=0)  # Gamification points
    last_active = Column(DateTime)         # Last app activity
```

## API Endpoints for Mobile Integration

### 1. Student Registration
**Endpoint:** `POST /api/student/register`

**Unity C# Example:**
```csharp
[System.Serializable]
public class StudentRegistration
{
    public string name;
    public string email;
    public string class_code;
    public string device_id;
    public string grade_level;
    public string avatar_url;
}

public async void RegisterStudent()
{
    var registration = new StudentRegistration
    {
        name = "John Doe",
        email = "john.doe@school.com",
        class_code = "MATH101A",
        device_id = SystemInfo.deviceUniqueIdentifier,
        grade_level = "Grade 5",
        avatar_url = "https://example.com/avatars/student1.png"
    };
    
    string json = JsonUtility.ToJson(registration);
    
    using (UnityWebRequest request = UnityWebRequest.PostWwwForm("http://localhost:8001/api/student/register", ""))
    {
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.SetRequestHeader("Content-Type", "application/json");
        
        await request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            var response = JsonUtility.FromJson<RegistrationResponse>(request.downloadHandler.text);
            PlayerPrefs.SetInt("StudentID", response.student_id);
            PlayerPrefs.SetString("StudentName", response.student_name);
            PlayerPrefs.SetInt("TotalPoints", response.total_points);
        }
    }
}
```

### 2. Get Student Profile
**Endpoint:** `GET /api/student/{student_id}/profile`

**Unity C# Example:**
```csharp
public async void LoadStudentProfile(int studentId)
{
    using (UnityWebRequest request = UnityWebRequest.Get($"http://localhost:8001/api/student/{studentId}/profile"))
    {
        await request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            var profile = JsonUtility.FromJson<StudentProfile>(request.downloadHandler.text);
            
            // Update UI with student data
            nameText.text = profile.student.name;
            pointsText.text = $"Points: {profile.student.total_points}";
            gradeText.text = profile.student.grade_level;
            
            // Load avatar
            if (!string.IsNullOrEmpty(profile.student.avatar_url))
            {
                StartCoroutine(LoadAvatar(profile.student.avatar_url));
            }
        }
    }
}
```

### 3. Submit Assignment
**Endpoint:** `POST /api/submit/{assignment_id}`

**Unity C# Example:**
```csharp
[System.Serializable]
public class AssignmentSubmission
{
    public int student_id;
    public Dictionary<string, string> answers;
}

public async void SubmitAssignment(int assignmentId, Dictionary<string, string> answers)
{
    var submission = new AssignmentSubmission
    {
        student_id = PlayerPrefs.GetInt("StudentID"),
        answers = answers
    };
    
    string json = JsonUtility.ToJson(submission);
    
    using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"http://localhost:8001/api/submit/{assignmentId}", ""))
    {
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.SetRequestHeader("Content-Type", "application/json");
        
        await request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            var result = JsonUtility.FromJson<SubmissionResult>(request.downloadHandler.text);
            
            // Update points automatically added to database
            PlayerPrefs.SetInt("TotalPoints", PlayerPrefs.GetInt("TotalPoints") + result.results.score);
            
            // Show results to student
            ShowResults(result.results.score, result.results.total_points, result.results.grade);
        }
    }
}
```

### 4. Update Avatar
**Endpoint:** `PUT /api/student/{student_id}/avatar`

**Unity C# Example:**
```csharp
public async void UpdateAvatar(int studentId, string avatarUrl)
{
    var avatarData = new { avatar_url = avatarUrl };
    string json = JsonUtility.ToJson(avatarData);
    
    using (UnityWebRequest request = UnityWebRequest.Put($"http://localhost:8001/api/student/{studentId}/avatar", json))
    {
        request.SetRequestHeader("Content-Type", "application/json");
        await request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Avatar updated successfully");
        }
    }
}
```

## Data Storage Flow

1. **Student Registration (Mobile App)**
   ```
   Unity Game → POST /api/student/register → SQLite Database
   ```
   - Creates new Student record or updates existing one
   - Enrolls student in class using class_code
   - Returns student_id for local storage

2. **Assignment Completion (Mobile App)**
   ```
   Unity Game → POST /api/submit/{assignment_id} → SQLite Database
   ```
   - Saves assignment submission
   - Automatically updates student.total_points
   - Updates student.last_active timestamp

3. **Teacher Monitoring (Web Dashboard)**
   ```
   Web Dashboard → Read from SQLite Database → Real-time Student Data
   ```
   - Teachers see student registrations instantly
   - Monitor assignment completion and scores
   - View student activity and points

## Database Tables Involved

### Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_id VARCHAR(255),
    grade_level VARCHAR(50),
    avatar_url VARCHAR(500),
    total_points INTEGER DEFAULT 0,
    last_active DATETIME
);
```

### Enrollments Table
```sql
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    class_id INTEGER,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (class_id) REFERENCES classes (id)
);
```

### Assignment Submissions Table
```sql
CREATE TABLE assignment_submissions (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER,
    student_id INTEGER,
    score INTEGER,
    total_points INTEGER,
    answers_json TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments (id),
    FOREIGN KEY (student_id) REFERENCES students (id)
);
```

## Integration Benefits

1. **Unified Data**: All student data stored in one database
2. **Real-time Monitoring**: Teachers see student activity instantly
3. **Automatic Scoring**: Points calculated and stored automatically
4. **Gamification**: Student points encourage engagement
5. **Cross-platform**: Web dashboard and mobile app share same data
6. **Scalable**: Can handle multiple classes and thousands of students

## Security Considerations

- Device ID tracking for preventing duplicate registrations
- Email validation for student identity
- Class code verification for enrollment security
- Activity timestamp tracking for monitoring engagement

## Next Steps for Unity Integration

1. Implement the provided C# code in your Unity project
2. Test student registration with a valid class code
3. Create assignment taking interface using `/api/assignment/{id}` endpoint
4. Implement leaderboard using `/api/leaderboard/{class_code}` endpoint
5. Add avatar selection and profile management features
