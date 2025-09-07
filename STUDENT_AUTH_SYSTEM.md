# Complete Student Registration & Login System

## Overview
This system allows students to:
1. **Register** their account (without joining any class)
2. **Login** with email/password
3. **Join classes** using class codes OR teachers can manually add them

## Unity Scripts

### 1. Registration Script (`Unity_SimpleStudentRegister.cs`)
**Purpose:** Create student accounts without class enrollment

**Features:**
- First Name, Last Name, Email, Password inputs
- Password confirmation validation
- Device ID tracking
- Automatic redirect to login after successful registration

**API Endpoint:** `POST /api/student/simple-register`

### 2. Login Script (`Unity_EnhancedLogin.cs`)
**Purpose:** Authenticate students and load their profile

**Features:**
- Email/password authentication
- Save student data locally (PlayerPrefs)
- Load enrolled classes information
- Secure password verification

**API Endpoint:** `POST /api/student/login`

### 3. Class Join Script (`Unity_ClassJoinManager.cs`)
**Purpose:** Allow students to join classes using class codes

**Features:**
- Enter class code to join
- Display current enrolled classes
- Validation and error handling

**API Endpoint:** `POST /api/student/join-class`

## Backend API Endpoints

### 1. Simple Registration
```
POST /api/student/simple-register
```
**Request:**
```json
{
    "name": "John Doe",
    "email": "john.doe@test.com",
    "password": "password123",
    "device_id": "unique-device-id",
    "grade_level": "Grade 1"
}
```

**Response:**
```json
{
    "status": "success",
    "student_id": 1,
    "student_name": "John Doe",
    "message": "Student account created successfully"
}
```

### 2. Student Login
```
POST /api/student/login
```
**Request:**
```json
{
    "email": "john.doe@test.com",
    "password": "password123",
    "device_id": "unique-device-id"
}
```

**Response:**
```json
{
    "status": "success",
    "student": {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@test.com",
        "grade_level": "Grade 1",
        "total_points": 0,
        "classes": [
            {
                "id": 1,
                "name": "Mathematics",
                "section": "Grade 1 - PEARL",
                "class_code": "2EK5QUY",
                "teacher_name": "Jane Smith"
            }
        ]
    },
    "message": "Login successful"
}
```

### 3. Join Class
```
POST /api/student/join-class
```
**Request:**
```json
{
    "student_id": 1,
    "class_code": "2EK5QUY"
}
```

**Response:**
```json
{
    "status": "success",
    "class_info": {
        "id": 1,
        "name": "Mathematics",
        "section": "Grade 1 - PEARL",
        "class_code": "2EK5QUY"
    },
    "message": "Successfully joined Mathematics"
}
```

## Database Changes

### Enhanced Student Model
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255),           -- NEW: Secure password storage
    device_id VARCHAR(255),
    grade_level VARCHAR(20),
    avatar_url VARCHAR(500),
    total_points INTEGER DEFAULT 0,
    last_active DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Unity Setup Instructions

### Scene 1: Register Scene
1. Add `Unity_SimpleStudentRegister.cs` to a GameObject
2. Create UI elements:
   - First Name Input (TMP_InputField)
   - Last Name Input (TMP_InputField)
   - Email Input (TMP_InputField)
   - Password Input (TMP_InputField)
   - Confirm Password Input (TMP_InputField)
   - Submit Button
   - Back to Login Button
   - Message Text (TMP_Text)
3. Assign all elements in the Inspector

### Scene 2: Login Scene
1. Add `Unity_EnhancedLogin.cs` to a GameObject
2. Create UI elements:
   - Email Input (TMP_InputField)
   - Password Input (TMP_InputField)
   - Login Button
   - Register Button
   - Message Text (TMP_Text)
   - Login Animator (optional)
3. Assign all elements in the Inspector

### Scene 3: Class Join Scene (Optional)
1. Add `Unity_ClassJoinManager.cs` to a GameObject
2. Create UI elements:
   - Class Code Input (TMP_InputField)
   - Join Button
   - Back Button
   - Message Text (TMP_Text)
   - Student Info Text (TMP_Text)
   - Class List Parent (Transform for displaying enrolled classes)

## Testing Steps

### Step 1: Test Registration
1. Run Unity register scene
2. Fill form:
   - First Name: `John`
   - Last Name: `Doe`
   - Email: `john.doe@test.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click Submit
4. Should show "Account created successfully!"

### Step 2: Verify in Database
Run this command to check if student was created:
```python
python -c "from app import SessionLocal, Student; db = SessionLocal(); students = db.query(Student).all(); [print(f'ID: {s.id} | Name: {s.name} | Email: {s.email}') for s in students]; db.close()"
```

### Step 3: Test Login
1. Run Unity login scene
2. Use the same credentials from registration
3. Should show "Login successful!" and redirect to game

### Step 4: Test Class Joining
1. Use class code: `2EK5QUY` (existing in database)
2. Should show "Successfully joined Mathematics!"

### Step 5: Verify in Teacher Dashboard
1. Go to http://localhost:5000
2. Login as teacher
3. Check class info - student should appear in the students list

## Security Features

✅ **Password Hashing:** Uses Werkzeug's secure password hashing
✅ **Input Validation:** Server-side validation for all fields
✅ **Device Tracking:** Unique device ID for security
✅ **Email Uniqueness:** Prevents duplicate accounts
✅ **Class Code Validation:** Ensures valid class enrollment

## Benefits of This System

1. **Separation of Concerns:** Registration ≠ Class Enrollment
2. **Teacher Control:** Teachers can see all students, decide who to manually add
3. **Student Choice:** Students can join classes they want using codes
4. **Security:** Proper authentication and password protection
5. **Flexibility:** Students can be in multiple classes
6. **Data Integrity:** All student data stored in central database

## Next Steps

1. **Test the registration flow** in Unity
2. **Verify students appear** in teacher dashboard
3. **Test login authentication**
4. **Implement class joining** functionality
5. **Add assignment taking** features for enrolled students
