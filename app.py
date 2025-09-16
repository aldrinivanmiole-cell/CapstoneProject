# Flask + FastAPI Combined Application
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, inspect, Boolean, DateTime, text
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os, re, json, random, string, threading, io
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
# Database setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "school.db")
DATABASE_URL = f"sqlite:///{db_path}"
os.makedirs(BASE_DIR, exist_ok=True)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper functions
def with_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return func(db, *args, **kwargs)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    return wrapper

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def handle_db_error(e, error_msg="Database error occurred"):
    print(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail=f"{error_msg}: {str(e)}")

def handle_not_found(item_name="Item"):
    raise HTTPException(status_code=404, detail=f"{item_name} not found")

def require_login():
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    return None

def success_response(data, message="Success"):
    return {"status": "success", "message": message, "data": data}

def error_response(message, status_code=400):
    raise HTTPException(status_code=status_code, detail=message)

# ---- API Access Guard ----
def api_guard(db):
    # Maintenance mode takes precedence
    try:
        if to_bool(get_setting(db, "access.maintenance_mode", "false")):
            msg = get_setting(db, "access.maintenance_message", "We'll be back shortly.")
            raise HTTPException(status_code=503, detail=msg)
        if not to_bool(get_setting(db, "access.enable_mobile_api", "true")):
            raise HTTPException(status_code=503, detail="Mobile API is disabled by admin")
    except HTTPException:
        raise

# Database Models
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    classes = relationship("Class", back_populates="teacher", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # This will act as the subject
    section = Column(String(50))
    class_code = Column(String(7), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    # Archive support
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime)
    teacher = relationship("Teacher", back_populates="classes")
    assignments = relationship("Assignment", back_populates="class_", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="class_", cascade="all, delete-orphan")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    due_date = Column(DateTime)
    points = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Archive support
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime)
    class_ = relationship("Class", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # multiple_choice, essay, short_answer
    points = Column(Integer, default=1)
    help_video_url = Column(String(255))  # YouTube or other video URL
    assignment = relationship("Assignment", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    correct_answers = relationship("CorrectAnswer", back_populates="question", cascade="all, delete-orphan")

class QuestionOption(Base):
    __tablename__ = "question_options"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    question = relationship("Question", back_populates="options")

class CorrectAnswer(Base):
    __tablename__ = "correct_answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="correct_answers")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255))  # Store hashed password
    device_id = Column(String(255))  # Unique device identifier for mobile app
    grade_level = Column(String(20))  # e.g., "Grade 1", "Grade 2", etc.
    avatar_url = Column(String(500))  # Profile picture for gamification
    total_points = Column(Integer, default=0)  # Gamification points
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="enrollments")
    class_ = relationship("Class", back_populates="enrollments")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    answers_json = Column(Text)  # Store answers as JSON
    assignment = relationship("Assignment")
    student = relationship("Student")

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("assignment_submissions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(Text)
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    submission = relationship("AssignmentSubmission")
    question = relationship("Question")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

# Global application settings managed by Admin
class AppSetting(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully - tables created")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")
        
        # Test database connection with a simple query
        db = SessionLocal()
        try:
            test_query = db.query(Teacher).count()
            print(f"Database connection test successful - Found {test_query} teachers")
            return True
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            return False
        finally:
            db.close()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def upgrade_schema():
    try:
        insp = inspect(engine)
        class_cols = {c['name'] for c in insp.get_columns('classes')}
        assign_cols = {c['name'] for c in insp.get_columns('assignments')}
        with engine.begin() as conn:
            if 'is_archived' not in class_cols:
                conn.execute(text("ALTER TABLE classes ADD COLUMN is_archived BOOLEAN DEFAULT 0"))
                print("Added column classes.is_archived")
            if 'archived_at' not in class_cols:
                conn.execute(text("ALTER TABLE classes ADD COLUMN archived_at DATETIME"))
                print("Added column classes.archived_at")
            if 'is_archived' not in assign_cols:
                conn.execute(text("ALTER TABLE assignments ADD COLUMN is_archived BOOLEAN DEFAULT 0"))
                print("Added column assignments.is_archived")
            if 'archived_at' not in assign_cols:
                conn.execute(text("ALTER TABLE assignments ADD COLUMN archived_at DATETIME"))
                print("Added column assignments.archived_at")
        # Ensure admins and app_settings tables exist
        Base.metadata.create_all(bind=engine, tables=[Admin.__table__, AppSetting.__table__])
    except Exception as e:
        print(f"Schema upgrade check failed or not needed: {e}")

# Initialize database tables
print("\n=== Database Initialization ===")
if init_db():
    print("Database setup completed successfully")
else:
    print("Failed to initialize database")
    exit(1)

# Ensure new columns exist (SQLite simple upgrade)
upgrade_schema()

def seed_default_admin():
    db = SessionLocal()
    try:
        print("Checking for existing admin accounts...")
        existing = db.query(Admin).count()
        print(f"Found {existing} existing admin accounts")
        
        if existing == 0:
            email = os.environ.get("ADMIN_EMAIL", "admin@capstone.local").strip()
            password = os.environ.get("ADMIN_PASSWORD", "Admin@12345").strip()
            print(f"Creating default admin with email: {email}")
            
            admin = Admin(email=email)
            admin.set_password(password)
            db.add(admin)
            db.commit()
            print(f"Successfully seeded default admin: {email}")
        else:
            print("Admin account already exists, skipping seed")
            
        # Verify admin was created/exists
        admin_check = db.query(Admin).first()
        if admin_check:
            print(f"Admin verification successful: {admin_check.email}")
        else:
            print("ERROR: No admin found after seeding!")
            
    except Exception as e:
        print(f"Admin seeding error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

# Seed admin once
seed_default_admin()

# ---- Settings Helpers ----
DEFAULT_SETTINGS = {
    # Game Rules
    "game.allow_multiple_submissions": "false",
    "game.points_multiplier": "1.0",
    "game.leaderboard_size": "10",
    # UI
    "ui.site_title": "Classroom",
    "ui.brand_color": "#667eea",
    # Access Controls
    "access.enable_registration": "true",
    "access.enable_mobile_api": "true",
    "access.maintenance_mode": "false",
    "access.maintenance_message": "We'll be back shortly.",
}

def to_bool(val: str) -> bool:
    return str(val).lower() in ["1", "true", "yes", "on"]

def get_setting(db, key: str, default: str | None = None) -> str:
    s = db.query(AppSetting).filter_by(key=key).first()
    if s:
        return s.value
    val = DEFAULT_SETTINGS.get(key) if default is None else default
    return val if isinstance(val, str) else str(val)

def set_setting(db, key: str, value: str):
    s = db.query(AppSetting).filter_by(key=key).first()
    if s:
        s.value = value
        s.updated_at = datetime.utcnow()
    else:
        s = AppSetting(key=key, value=value, updated_at=datetime.utcnow())
        db.add(s)
    db.commit()

def get_settings_map() -> dict:
    db = SessionLocal()
    try:
        settings = {k: DEFAULT_SETTINGS.get(k, "") for k in DEFAULT_SETTINGS.keys()}
        for row in db.query(AppSetting).all():
            settings[getattr(row, 'key')] = getattr(row, 'value')
        return settings
    finally:
        db.close()

# App Initialization
app = Flask(__name__)
app.secret_key = 'dev-secret-key-replace-in-production'
api = FastAPI(title="Classroom Game API", description="API for Unity turn-based game", version="1.0.0")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Expose settings to all templates (after app is created)
@app.context_processor
def inject_settings():
    settings = get_settings_map()
    return {
        "app_settings": settings,
        "SITE_TITLE": settings.get("ui.site_title", "Classroom"),
        "BRAND_COLOR": settings.get("ui.brand_color", "#667eea"),
    }

# Redirect /admin* to /dashboard/admin* since Flask app is mounted under /dashboard in production
@api.get("/admin")
def admin_root_redirect():
    return RedirectResponse(url="/dashboard/admin", status_code=307)

@api.get("/admin/login")
def admin_login_redirect():
    return RedirectResponse(url="/dashboard/admin/login", status_code=307)

@api.get("/admin/{path:path}")
def admin_wildcard_redirect(path: str):
    target = f"/dashboard/admin/{path}"
    return RedirectResponse(url=target, status_code=307)

# FastAPI Endpoints (Unity/Android)
@api.get("/", summary="API Health Check")
def api_root():
    return {
        "message": "Classroom Game API is running",
        "status": "active",
        "version": "2.0.0-fastapi-first",
        "deployment_time": "2025-09-10T02:55:00Z",
        "endpoints": {
            "classes": "/classes",
            "assignments": "/class/{class_code}/assignments",
            "assignment_detail": "/assignment/{assignment_id}",
            "submit": "/submit/{assignment_id}",
            "student_register": "/student/register",
            "student_login": "/student/login",
            "student_subjects": "/student/subjects",
            "student_assignments": "/student/assignments",
            "leaderboard": "/leaderboard/{class_code}"
        }
    }

@api.get("/classes", summary="Get All Classes")
@with_db_session
def get_all_classes(db):
    try:
        classes = db.query(Class).filter_by(is_archived=False).all()
        return success_response([
            {
                "id": c.id,
                "name": c.name,
                "section": c.section,
                "class_code": c.class_code,
                "teacher_name": c.teacher.full_name if c.teacher else "Unknown"
            } for c in classes
        ])
    except Exception as e:
        handle_db_error(e)

@api.get("/class/{class_code}/assignments", summary="Get Assignments by Class Code")
@with_db_session
def get_assignments_by_code(db, class_code: str):
    try:
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            handle_not_found("Class")
        if class_.is_archived:
            return success_response({
                "class_info": {
                    "name": class_.name,
                    "section": class_.section,
                    "teacher": class_.teacher.full_name
                },
                "assignments": []
            })

        assignments = db.query(Assignment).filter_by(class_id=class_.id, is_archived=False).all()
        return success_response({
            "class_info": {
                "name": class_.name,
                "section": class_.section,
                "teacher": class_.teacher.full_name
            },
            "assignments": [
                {
                    "id": q.id,
                    "title": q.title,
                    "description": q.description,
                    "points": q.points,
                    "question_count": len(q.questions)
                } for q in assignments
            ]
        })
    except HTTPException:
        raise
    except Exception as e:
        handle_db_error(e)

@api.get("/assignment/{assignment_id}", summary="Get Assignment Questions")
def get_assignment_for_game(assignment_id: int):

    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if assignment.is_archived or assignment.class_.is_archived:
            raise HTTPException(status_code=403, detail="Assignment is archived")
        
        questions = db.query(Question).filter_by(assignment_id=assignment_id).all()
        question_list = []
        
        for q in questions:
            q_data = {
                "id": q.id,
                "question_text": q.question_text,  # Unity expects question_text, not text
                "question_type": q.question_type,  # Unity expects question_type, not type
                "points": q.points,
                "help_video_url": q.help_video_url
            }
            
            # Add options for multiple choice and yes_no questions
            if q.question_type == "multiple_choice":
                options = db.query(QuestionOption).filter_by(question_id=q.id).all()
                correct_answers = db.query(CorrectAnswer).filter_by(question_id=q.id).all()
                correct_texts = [ca.answer_text for ca in correct_answers]
                
                # Unity expects: options as string array, correct_answer_index as int
                q_data["options"] = [opt.option_text for opt in options]
                # Find the index of the first correct answer
                q_data["correct_answer_index"] = 0
                for i, opt in enumerate(options):
                    if opt.option_text in correct_texts:
                        q_data["correct_answer_index"] = i
                        break
                        
            elif q.question_type == "yes_no":
                options = db.query(QuestionOption).filter_by(question_id=q.id).all()
                correct_answer = db.query(CorrectAnswer).filter_by(question_id=q.id).first()
                
                # Unity expects: options as string array, correct_answer_index as int
                q_data["options"] = [opt.option_text for opt in options]
                # Find the index of the correct answer (Yes=0, No=1)
                q_data["correct_answer_index"] = 0
                if correct_answer:
                    for i, opt in enumerate(options):
                        if opt.option_text == correct_answer.answer_text:
                            q_data["correct_answer_index"] = i
                            break
            
            question_list.append(q_data)
        
        return {
            "status": "success",
            "assignment": {
                "id": assignment.id,
                "title": assignment.title,
                "description": assignment.description,
                "total_points": sum(q.points for q in questions),
                "question_count": len(questions)
            },
            "questions": question_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/register", summary="Register Student for Mobile Game")
def register_student_for_game(student_data: dict):
    db = SessionLocal()
    try:
        api_guard(db)
        name = student_data.get("name", "").strip()
        email = student_data.get("email", "").strip()
        class_code = student_data.get("class_code", "").strip()
        device_id = student_data.get("device_id", "").strip()
        grade_level = student_data.get("grade_level", "").strip()
        avatar_url = student_data.get("avatar_url", "").strip()
        
        if not all([name, email, class_code]):
            raise HTTPException(status_code=400, detail="Name, email, and class code are required")
        
        # Check if class exists
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Invalid class code")
        
        # Check if student already exists
        existing_student = db.query(Student).filter_by(email=email).first()
        if existing_student:
            # Update device_id and last_active for existing student
            existing_student.device_id = device_id
            existing_student.last_active = datetime.utcnow()
            if grade_level:
                existing_student.grade_level = grade_level
            if avatar_url:
                existing_student.avatar_url = avatar_url
                
            # Check if already enrolled
            existing_enrollment = db.query(Enrollment).filter_by(
                student_id=existing_student.id, class_id=class_.id
            ).first()
            if not existing_enrollment:
                # Enroll existing student in new class
                enrollment = Enrollment(student_id=existing_student.id, class_id=class_.id)
                db.add(enrollment)
            
            db.commit()
            return {
                "status": "success",
                "student_id": existing_student.id,
                "student_name": existing_student.name,
                "class_name": class_.name,
                "total_points": existing_student.total_points,
                "message": "Student enrolled successfully"
            }
        
        # Create new student
        new_student = Student(
            name=name, 
            email=email,
            device_id=device_id,
            grade_level=grade_level,
            avatar_url=avatar_url,
            total_points=0,
            last_active=datetime.utcnow()
        )
        db.add(new_student)
        db.flush()  # Get student ID
        
        # Enroll in class
        enrollment = Enrollment(student_id=new_student.id, class_id=class_.id)
        db.add(enrollment)
        db.commit()
        
        return {
            "status": "success",
            "student_id": new_student.id,
            "student_name": new_student.name,
            "class_name": class_.name,
            "total_points": new_student.total_points,
            "message": "Student registered and enrolled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/simple-register", summary="Simple Student Registration (No Class)")
def simple_register_student(student_data: dict):
    db = SessionLocal()
    try:
        api_guard(db)
        name = student_data.get("name", "").strip()
        email = student_data.get("email", "").strip()
        password = student_data.get("password", "").strip()
        device_id = student_data.get("device_id", "").strip()
        grade_level = student_data.get("grade_level", "Grade 1").strip()
        
        if not all([name, email, password]):
            raise HTTPException(status_code=400, detail="Name, email, and password are required")
        
        # Check if student already exists
        existing_student = db.query(Student).filter_by(email=email).first()
        if existing_student:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create new student (NO CLASS ENROLLMENT)
        new_student = Student(
            name=name,
            email=email,
            device_id=device_id,
            grade_level=grade_level,
            total_points=0,
            last_active=datetime.utcnow()
        )
        
        # Set password hash
        new_student.set_password(password)
        
        db.add(new_student)
        db.commit()
        
        return {
            "status": "success",
            "student_id": new_student.id,
            "student_name": new_student.name,
            "message": "Student account created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/login", summary="Student Login")
def login_student(login_data: dict):
    db = SessionLocal()
    try:
        api_guard(db)
        email = login_data.get("email", "").strip()
        password = login_data.get("password", "").strip()
        device_id = login_data.get("device_id", "").strip()
        
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Find student by email
        student = db.query(Student).filter_by(email=email).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student account not found")
        
        # Verify password
        if not student.check_password(password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last active and device ID
        student.last_active = datetime.utcnow()
        if device_id:
            student.device_id = device_id
        
        # Get enrolled classes
        enrollments = db.query(Enrollment).filter_by(student_id=student.id).all()
        classes = []
        for enrollment in enrollments:
            class_ = db.query(Class).filter_by(id=enrollment.class_id).first()
            if class_:
                teacher = db.query(Teacher).filter_by(id=class_.teacher_id).first()
                classes.append({
                    "id": class_.id,
                    "name": class_.name,
                    "section": class_.section,
                    "class_code": class_.class_code,
                    "teacher_name": f"{teacher.first_name} {teacher.last_name}" if teacher else "Unknown"
                })
        
        db.commit()
        
        return {
            "status": "success",
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "grade_level": student.grade_level or "Grade 1",
                "total_points": student.total_points or 0,
                "classes": classes
            },
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/join-class", summary="Join Class with Code")
def join_class_with_code(join_data: dict):
    db = SessionLocal()
    try:
        api_guard(db)
        student_id = join_data.get("student_id")
        class_code = join_data.get("class_code", "").strip().upper()
        
        if not all([student_id, class_code]):
            raise HTTPException(status_code=400, detail="Student ID and class code are required")
        
        # Check if student exists
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if class exists
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Invalid class code")
        if class_.is_archived:
            raise HTTPException(status_code=400, detail="Class is archived and cannot be joined")
        
        # Check if already enrolled
        existing_enrollment = db.query(Enrollment).filter_by(
            student_id=student_id, class_id=class_.id
        ).first()
        if existing_enrollment:
            raise HTTPException(status_code=400, detail="Student already enrolled in this class")
        
        # Enroll student in class
        enrollment = Enrollment(student_id=student_id, class_id=class_.id)
        db.add(enrollment)
        db.commit()
        
        # Determine gameplay type based on subject name (can be customized)
        gameplay_type = determine_gameplay_type(class_.name)
        
        return {
            "status": "success",
            "subject": class_.name,  # Unity expects 'subject' field - this is now dynamic
            "gameplay_type": gameplay_type,  # Unity expects 'gameplay_type' field
            "class_info": {
                "id": class_.id,
                "name": class_.name,
                "section": class_.section,
                "class_code": class_.class_code
            },
            "message": f"Successfully joined {class_.name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/submit/{assignment_id}", summary="Submit Assignment Answers")
def submit_assignment_from_game(assignment_id: int, submission_data: dict):
    db = SessionLocal()
    try:
        api_guard(db)
        student_id = submission_data.get("student_id")
        answers = submission_data.get("answers", {})
        
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID is required")
        
        # Check if assignment exists
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if assignment.is_archived or assignment.class_.is_archived:
            raise HTTPException(status_code=403, detail="Assignment is archived")
        
        # Check for existing submission
        existing_submission = db.query(AssignmentSubmission).filter_by(
            assignment_id=assignment_id, student_id=student_id
        ).first()
        allow_multi = to_bool(get_setting(db, "game.allow_multiple_submissions", "false"))
        if existing_submission and not allow_multi:
            raise HTTPException(status_code=400, detail="Assignment already submitted")
        if existing_submission and allow_multi:
            db.delete(existing_submission)
            db.flush()
        
        # Calculate score
        score = 0
        total_points = 0
        detailed_results = []
        
        for question in assignment.questions:
            total_points += question.points
            answer = answers.get(str(question.id), "")
            is_correct = False
            points_earned = 0
            
            if answer:
                if question.question_type == "multiple_choice":
                    correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                    if any(ca.answer_text == answer for ca in correct_answers):
                        is_correct = True
                        points_earned = question.points
                
                elif question.question_type in ["identification", "problem_solving"]:
                    correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                    if correct_answer and answer.lower().strip() == correct_answer.answer_text.lower().strip():
                        is_correct = True
                        points_earned = question.points
                
                elif question.question_type == "fill_in_the_blanks":
                    correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                    # For fill in the blanks, check if all blanks are filled correctly
                    if correct_answers:
                        answer_parts = [part.strip().lower() for part in answer.split('|')]
                        correct_parts = [ca.answer_text.strip().lower() for ca in correct_answers]
                        if len(answer_parts) == len(correct_parts) and all(a == c for a, c in zip(answer_parts, correct_parts)):
                            is_correct = True
                            points_earned = question.points
                
                elif question.question_type == "enumeration":
                    correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                    if any(ca.answer_text.lower().strip() == answer.lower().strip() for ca in correct_answers):
                        is_correct = True
                        points_earned = question.points
                
                elif question.question_type == "yes_no":
                    correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                    if correct_answer and answer.strip() == correct_answer.answer_text.strip():
                        is_correct = True
                        points_earned = question.points
            
            score += points_earned
            detailed_results.append({
                "question_id": question.id,
                "answer": answer,
                "correct": is_correct,
                "points_earned": points_earned,
                "max_points": question.points
            })
        
        # Save submission
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student_id,
            score=score,
            total_points=total_points,
            answers_json=json.dumps(answers)
        )
        db.add(submission)
        
        # Update student points and last activity
        student = db.query(Student).filter_by(id=student_id).first()
        if student:
            try:
                multiplier = float(get_setting(db, "game.points_multiplier", "1.0"))
            except Exception:
                multiplier = 1.0
            added = int(round(score * multiplier))
            student.total_points = (student.total_points or 0) + added
            student.last_active = datetime.utcnow()
        
        db.commit()
        
        # Calculate performance metrics for game
        percentage = (score / total_points * 100) if total_points > 0 else 0
        grade = "A" if percentage >= 90 else "B" if percentage >= 80 else "C" if percentage >= 70 else "D" if percentage >= 60 else "F"
        
        return {
            "status": "success",
            "results": {
                "score": score,
                "total_points": total_points,
                "percentage": round(percentage, 2),
                "grade": grade,
                "submission_id": submission.id
            },
            "detailed_results": detailed_results
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.get("/leaderboard/{class_code}", summary="Get Class Leaderboard")
def get_class_leaderboard(class_code: str):
    db = SessionLocal()
    try:
        api_guard(db)
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Get all assignment submissions for this class
        submissions = db.query(AssignmentSubmission).join(Assignment).filter(Assignment.class_id == class_.id).all()
        
        # Calculate student scores
        student_scores = {}
        for submission in submissions:
            student_id = submission.student_id
            if student_id not in student_scores:
                student = db.query(Student).filter_by(id=student_id).first()
                student_scores[student_id] = {
                    "name": student.name if student else "Unknown",
                    "total_score": 0,
                    "total_possible": 0,
                    "assignments_completed": 0
                }
            
            student_scores[student_id]["total_score"] += submission.score
            student_scores[student_id]["total_possible"] += submission.total_points
            student_scores[student_id]["assignments_completed"] += 1
        
        # Sort by total score
        leaderboard = []
        for student_id, data in student_scores.items():
            percentage = (data["total_score"] / data["total_possible"] * 100) if data["total_possible"] > 0 else 0
            leaderboard.append({
                "student_id": student_id,
                "name": data["name"],
                "total_score": data["total_score"],
                "total_possible": data["total_possible"],
                "percentage": round(percentage, 2),
                "assignments_completed": data["assignments_completed"]
            })
        
        leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
        try:
            top_n = int(get_setting(db, "game.leaderboard_size", "10"))
        except Exception:
            top_n = 10
        leaderboard = leaderboard[:max(1, top_n)]
        
        # Add rankings
        for i, student in enumerate(leaderboard):
            student["rank"] = i + 1
        
        return {
            "status": "success",
            "class_info": {
                "name": class_.name,
                "section": class_.section,
                "code": class_.class_code
            },
            "leaderboard": leaderboard
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.get("/student/{student_id}/profile", summary="Get Student Profile for Mobile")
def get_student_profile(student_id: int):

    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get enrolled classes
        enrollments = db.query(Enrollment).filter_by(student_id=student_id).all()
        classes = []
        for enrollment in enrollments:
            class_ = db.query(Class).filter_by(id=enrollment.class_id).first()
            if class_:
                # Count completed assignments
                completed_assignments = db.query(AssignmentSubmission).join(Assignment).filter(
                    Assignment.class_id == class_.id,
                    AssignmentSubmission.student_id == student_id
                ).count()
                
                # Count total assignments
                total_assignments = db.query(Assignment).filter_by(class_id=class_.id).count()
                
                classes.append({
                    "id": class_.id,
                    "name": class_.name,
                    "section": class_.section,
                    "class_code": class_.class_code,
                    "teacher_name": class_.teacher_name,
                    "completed_assignments": completed_assignments,
                    "total_assignments": total_assignments
                })
        
        return {
            "status": "success",
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "device_id": student.device_id,
                "grade_level": student.grade_level,
                "avatar_url": student.avatar_url,
                "total_points": student.total_points,
                "last_active": student.last_active.isoformat() if student.last_active else None,
                "classes": classes
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.put("/student/{student_id}/avatar", summary="Update Student Avatar")
def update_student_avatar(student_id: int, avatar_data: dict):

    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        avatar_url = avatar_data.get("avatar_url", "").strip()
        if not avatar_url:
            raise HTTPException(status_code=400, detail="Avatar URL is required")
        
        student.avatar_url = avatar_url
        student.last_active = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "message": "Avatar updated successfully",
            "avatar_url": student.avatar_url
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/subjects", summary="Get Student's Enrolled Subjects")
def get_student_subjects(request_data: dict):
    """
    Get all subjects (classes) that a student is enrolled in.
    Expected payload: {"student_id": 123}
    Returns: {"subjects": [{"subject_name": "Mathematics", "gameplay_type": "MultipleChoice"}, ...]}
    """
    db = SessionLocal()
    try:
        # Validate input
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Request must be a JSON object")
        
        student_id = request_data.get("student_id")
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id is required")
        
        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="student_id must be a valid integer")
        
        # Verify student exists
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get all classes the student is enrolled in
        enrollments = db.query(Enrollment).filter_by(student_id=student_id).all()
        
        subjects = []
        processed_class_names = set()  # Avoid duplicates if student is enrolled multiple times
        
        for enrollment in enrollments:
            class_ = db.query(Class).filter_by(id=enrollment.class_id).first()
            if class_ and (not bool(class_.is_archived)) and class_.name not in processed_class_names:
                # Determine gameplay type based on subject name (dynamic)
                gameplay_type = determine_gameplay_type(class_.name)
                
                subjects.append({
                    "subject_name": class_.name,
                    "gameplay_type": gameplay_type
                })
                processed_class_names.add(class_.name)
        
        # Sort subjects alphabetically for consistent output
        subjects.sort(key=lambda x: x["subject_name"])
        
        return {
            "subjects": subjects
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

@api.post("/student/assignments", summary="Get Student Assignments by Subject")
def get_student_assignments_by_subject(request_data: dict):
    """
    Get all assignments for a student in a specific subject.
    Expected payload: {"student_id": 123, "subject": "Mathematics"}
    Returns: {"assignments": [{"assignment_id": 1, "title": "Basic Algebra Quiz", "questions": [...], "due_date": "2025-09-20"}, ...]}
    """
    db = SessionLocal()
    try:
        # Validate input
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Request must be a JSON object")
        
        student_id = request_data.get("student_id")
        subject = request_data.get("subject", "").strip()
        
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id is required")
        if not subject:
            raise HTTPException(status_code=400, detail="subject is required")
        
        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="student_id must be a valid integer")
        
        # Verify student exists
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Find classes where the student is enrolled that match the subject (flexible match)
        enrollments = db.query(Enrollment).filter_by(student_id=student_id).all()
        
        matching_class_ids = []
        for enrollment in enrollments:
            class_ = db.query(Class).filter_by(id=enrollment.class_id).first()
            if class_ and (not bool(class_.is_archived)) and _subjects_match(str(class_.name), subject):
                matching_class_ids.append(class_.id)
        
        if not matching_class_ids:
            # Return empty assignments if student isn't enrolled in this subject
            return {"assignments": []}
        
        # Get all assignments from matching classes
        assignments = db.query(Assignment).filter(Assignment.class_id.in_(matching_class_ids), Assignment.is_archived == False).all()
        
        assignment_list = []
        for assignment in assignments:
            # Get questions for this assignment
            questions = db.query(Question).filter_by(assignment_id=assignment.id).all()
            
            question_list = []
            for q in questions:
                q_data = {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "points": q.points,
                    "help_video_url": q.help_video_url
                }
                
                # Add options for multiple choice and yes_no questions
                if q.question_type == "multiple_choice":
                    options = db.query(QuestionOption).filter_by(question_id=q.id).all()
                    correct_answers = db.query(CorrectAnswer).filter_by(question_id=q.id).all()
                    correct_texts = [ca.answer_text for ca in correct_answers]
                    
                    q_data["options"] = [opt.option_text for opt in options]
                    q_data["correct_answer_index"] = 0
                    for i, opt in enumerate(options):
                        if opt.option_text in correct_texts:
                            q_data["correct_answer_index"] = i
                            break
                            
                elif q.question_type == "yes_no":
                    options = db.query(QuestionOption).filter_by(question_id=q.id).all()
                    correct_answer = db.query(CorrectAnswer).filter_by(question_id=q.id).first()
                    
                    q_data["options"] = [opt.option_text for opt in options]
                    q_data["correct_answer_index"] = 0
                    if correct_answer:
                        for i, opt in enumerate(options):
                            if opt.option_text == correct_answer.answer_text:
                                q_data["correct_answer_index"] = i
                                break
                
                elif q.question_type in ["short_answer", "essay", "enumeration", "fill_in_blank"]:
                    # For text-based questions, include correct answers
                    correct_answers = db.query(CorrectAnswer).filter_by(question_id=q.id).all()
                    q_data["correct_answers"] = [ca.answer_text for ca in correct_answers]
                
                question_list.append(q_data)
            
            # Determine gameplay type for this subject/assignment for Unity convenience
            gameplay_type = determine_gameplay_type(subject)

            # Full structure (includes questions) with Unity-friendly aliases
            assignment_list.append({
                "assignment_id": assignment.id,
                "id": assignment.id,  # duplicate for Unity
                "title": assignment.title,
                "assignment_title": assignment.title,  # Unity-friendly duplicate
                "description": assignment.description,
                "content": assignment.description,  # Unity-friendly duplicate
                "assignment_content": assignment.description,  # Unity-friendly duplicate
                "assignment_type": gameplay_type,
                "type": gameplay_type,
                "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                "points": assignment.points,
                "total_questions": len(question_list),
                "total_points": sum(q.points for q in questions),
                "questions": question_list
            })
        
        # Sort assignments by due date (upcoming first) and then by creation date
        assignment_list.sort(key=lambda x: (x["due_date"] or "9999-12-31", x["assignment_id"]))
        
        return {"assignments": assignment_list}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

# --- Aliases/GET variant for Unity clients ---
@api.get("/student/assignments", summary="Get Student Assignments by Subject (GET)")
def get_student_assignments_by_subject_get(student_id: int, subject: str):
    return get_student_assignments_by_subject({
        "student_id": student_id,
        "subject": subject
    })

@api.post("/api/student/assignments", summary="Alias: POST /api/student/assignments")
def get_student_assignments_by_subject_api_alias(payload: dict):
    return get_student_assignments_by_subject(payload)

@api.get("/api/get_active_assignments", summary="Alias: GET active assignments")
def get_active_assignments_alias(student_id: int, subject: str):
    return get_student_assignments_by_subject({
        "student_id": student_id,
        "subject": subject
    })

@api.post("/api/navigation_event", summary="Track Student Navigation Events")
def track_navigation_event(event_data: dict):
    """
    Track student navigation and activity events from Unity game.
    This endpoint logs student interactions for analytics and progress tracking.
    """
    try:
        # Extract event data
        student_id = event_data.get("student_id")
        event_type = event_data.get("event_type", "").strip()
        scene_name = event_data.get("scene_name", "").strip()
        subject_name = event_data.get("subject_name", "").strip()
        class_code = event_data.get("class_code", "").strip()
        timestamp = event_data.get("timestamp", datetime.utcnow().isoformat())
        additional_data = event_data.get("additional_data", {})
        
        # Log the navigation event
        print(f"🎮 Navigation Event: Student {student_id} - {event_type}")
        print(f"   Scene: {scene_name}, Subject: {subject_name}, Class: {class_code}")
        print(f"   Timestamp: {timestamp}")
        if additional_data:
            print(f"   Additional Data: {additional_data}")
        
        # Update student's last activity if student_id is provided
        if student_id:
            db = SessionLocal()
            try:
                student = db.query(Student).filter_by(id=student_id).first()
                if student:
                    student.last_active = datetime.utcnow()
                    db.commit()
                    print(f"   ✓ Updated last_active for student {student_id}")
                else:
                    print(f"   ⚠️ Student {student_id} not found in database")
            except Exception as e:
                print(f"   ❌ Error updating student activity: {str(e)}")
                db.rollback()
            finally:
                db.close()
        
        # Return success response
        return {
            "status": "success",
            "message": "Navigation event tracked successfully",
            "event_type": event_type,
            "timestamp": timestamp
        }
        
    except Exception as e:
        print(f"❌ Error tracking navigation event: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to track navigation event: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

# Utility Functions
def generate_class_code(length=7):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        db = SessionLocal()
        try:
            existing = db.query(Class).filter_by(class_code=code).first()
            if not existing:
                return code
        finally:
            db.close()

def determine_gameplay_type(subject_name):
    """
    Intelligently determine gameplay type based on subject name.
    This function is fully dynamic and can handle various subject naming conventions.
    """
    if not subject_name:
        return "MultipleChoice"  # Default fallback
    
    subject = subject_name.lower().strip()
    
    # Math-related subjects - Best for MultipleChoice with clear right/wrong answers
    if any(keyword in subject for keyword in [
        'math', 'mathematics', 'algebra', 'geometry', 'calculus', 'arithmetic',
        'statistics', 'trigonometry', 'pre-calc', 'pre-algebra', 'numerical'
    ]):
        return "MultipleChoice"
    
    # Science-related subjects - Good for MultipleChoice with factual questions
    elif any(keyword in subject for keyword in [
        'science', 'biology', 'chemistry', 'physics', 'lab', 'laboratory',
        'environmental', 'earth science', 'anatomy', 'botany', 'zoology'
    ]):
        return "MultipleChoice"
    
    # Computer Science/Technology - Good for MultipleChoice
    elif any(keyword in subject for keyword in [
        'computer', 'programming', 'coding', 'technology', 'it', 'software',
        'web design', 'robotics', 'digital'
    ]):
        return "MultipleChoice"
    
    # Language/English subjects - Better for FillInBlank for vocabulary and grammar
    elif any(keyword in subject for keyword in [
        'english', 'language', 'literature', 'reading', 'writing', 'grammar',
        'vocabulary', 'spelling', 'composition', 'linguistics'
    ]):
        return "FillInBlank"
    
    # Foreign Languages - Good for FillInBlank
    elif any(keyword in subject for keyword in [
        'spanish', 'french', 'german', 'chinese', 'japanese', 'latin',
        'foreign language', 'esl', 'mandarin'
    ]):
        return "FillInBlank"
    
    # History/Social Studies - Good for Enumeration (listing events, facts, etc.)
    elif any(keyword in subject for keyword in [
        'history', 'social', 'geography', 'civics', 'government', 'economics',
        'world history', 'american history', 'political', 'anthropology'
    ]):
        return "Enumeration"
    
    # Physical Education/Health - Simple YesNo questions work well
    elif any(keyword in subject for keyword in [
        'pe', 'physical', 'health', 'sports', 'fitness', 'nutrition',
        'wellness', 'exercise', 'athletics'
    ]):
        return "YesNo"
    
    # Arts subjects - Creative subjects can use MultipleChoice for theory
    elif any(keyword in subject for keyword in [
        'art', 'music', 'drama', 'theater', 'creative', 'painting',
        'sculpture', 'band', 'choir', 'orchestra', 'visual arts'
    ]):
        return "MultipleChoice"
    
    # Business/Economics - Good for MultipleChoice
    elif any(keyword in subject for keyword in [
        'business', 'accounting', 'finance', 'marketing', 'management',
        'entrepreneurship', 'economics'
    ]):
        return "MultipleChoice"
    
    # Psychology/Philosophy - Can use Enumeration for complex concepts
    elif any(keyword in subject for keyword in [
        'psychology', 'philosophy', 'sociology', 'ethics'
    ]):
        return "Enumeration"
    
    # Default to MultipleChoice for unknown subjects
    else:
        return "MultipleChoice"

# --- Subject Matching Helpers (Unity compatibility) ---
def _normalize_subject_name(name: str) -> str:
    if not name:
        return ""
    s = name.strip().lower()
    if any(k in s for k in ["math", "algebra", "geometry", "calc", "arithmetic", "trig", "statistics"]):
        return "math"
    if any(k in s for k in ["sci", "science", "biology", "chemistry", "physics", "earth science", "anatomy", "botany", "zoology"]):
        return "science"
    if any(k in s for k in ["eng", "english", "language", "literature", "grammar", "vocab", "spelling"]):
        return "english"
    if any(k in s for k in ["pe", "physical education", "physical", "health", "fitness", "sports"]):
        return "pe"
    if "art" in s or any(k in s for k in ["visual arts", "painting", "music", "drama", "theater"]):
        return "art"
    return s

def _subjects_match(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return _normalize_subject_name(a) == _normalize_subject_name(b)

# Flask Routes (Teacher Dashboard)

@app.route("/")
def index():
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter_by(id=session["teacher_id"]).first()
        if not teacher:
            session.clear()
            return redirect(url_for("login"))
            
        classes = db.query(Class).filter_by(teacher_id=teacher.id, is_archived=False).order_by(Class.created_at.desc()).all()
        archived_count = db.query(Class).filter_by(teacher_id=teacher.id, is_archived=True).count()
        return render_template("dashboard.html", teacher=teacher, classes=classes, archived_count=archived_count)
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        flash("An error occurred while loading your classes. Please try again.", "danger")
        return redirect(url_for("login"))
    finally:
        db.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if "teacher_id" in session:
        return redirect(url_for("index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        # Basic validation
        if not email or not password:
            flash("Please enter both email and password", "danger")
            return render_template("login.html")
        
        db = SessionLocal()
        try:
            teacher = db.query(Teacher).filter_by(email=email).first()
            if not teacher:
                flash("No account found with that email.", "warning")
            elif not teacher.check_password(password):
                flash("Incorrect password. Please try again.", "danger")
            else:
                session["teacher_id"] = teacher.id
                session["name"] = teacher.full_name
                return redirect(url_for("index"))
        except SQLAlchemyError as e:
            print(f"Login error: {str(e)}")  # Log the error
            flash("An error occurred. Please try again.", "danger")
        finally:
            db.close()
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "teacher_id" in session:
        return redirect(url_for("index"))
    # Respect admin setting to disable teacher self-registration
    db = SessionLocal()
    try:
        if not to_bool(get_setting(db, "access.enable_registration", "true")):
            flash("Teacher registration is currently disabled by admin.", "warning")
            return redirect(url_for("login"))
    finally:
        db.close()
        
    if request.method == "POST":
        try:
            # Clean up the input data
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            
            # Remove any JMeter variables that didn't get replaced
            first_name = first_name.replace("${__threadNum}", "").replace("${threadNum}", "").replace("${_threadNum}", "")
            last_name = last_name.replace("${__threadNum}", "").replace("${threadNum}", "").replace("${_threadNum}", "")
            email = email.replace("${__threadNum}", "").replace("${threadNum}", "").replace("${_threadNum}", "")
            
            # Basic validation
            if not all([first_name, last_name, email, password, confirm_password]):
                flash("All fields are required", "danger")
                return render_template("register.html")
            
            if password != confirm_password:
                flash("Passwords do not match", "danger")
                return render_template("register.html")
            
            # Create database session
            db = SessionLocal()
            try:
                # Check for existing user
                existing_user = db.query(Teacher).filter_by(email=email).first()
                if existing_user:
                    flash("Email already registered", "danger")
                    return render_template("register.html")
                
                # Create new teacher
                new_teacher = Teacher(
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                new_teacher.set_password(password)
                
                db.add(new_teacher)
                db.commit()
                
                flash("Registration successful! Please login.", "success")
                return redirect(url_for("login"))
                    
            except Exception as e:
                db.rollback()
                flash("An error occurred during registration", "danger")
                return render_template("register.html")
            finally:
                db.close()
                
        except Exception as e:
            flash("An error occurred during registration", "danger")
            return render_template("register.html")
            
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    # Allow teachers or admins to create a class
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        section = request.form.get("section", "").strip()
        target_teacher_id = session.get("teacher_id")

        # Admin can choose a teacher owner for the class
        if session.get("admin_id"):
            try:
                target_teacher_id = int(request.form.get("teacher_id"))
            except (TypeError, ValueError):
                target_teacher_id = None

        if not name:
            flash("Class name is required", "danger")
            # For admin, we need the list of teachers to render form
            db = SessionLocal()
            try:
                teachers = db.query(Teacher).order_by(Teacher.first_name.asc()).all()
            finally:
                db.close()
            return render_template("create_class.html", teachers=teachers)

        if not target_teacher_id:
            flash("A teacher must be selected for the class", "danger")
            db = SessionLocal()
            try:
                teachers = db.query(Teacher).order_by(Teacher.first_name.asc()).all()
            finally:
                db.close()
            return render_template("create_class.html", teachers=teachers)

        db = SessionLocal()
        try:
            new_class = Class(
                name=name,
                section=section if section else None,
                class_code=generate_class_code(),
                teacher_id=target_teacher_id
            )
            db.add(new_class)
            db.commit()
            flash(f"Class '{name}' created successfully!", "success")
            # Admin goes back to admin classes, teacher back to dashboard
            if session.get("admin_id"):
                return redirect(url_for("admin_classes"))
            return redirect(url_for("index"))
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating class: {str(e)}")
            flash("An error occurred while creating the class", "danger")
        finally:
            db.close()

    # GET - teachers list for admin form
    db = SessionLocal()
    try:
        teachers = db.query(Teacher).order_by(Teacher.first_name.asc()).all()
    finally:
        db.close()
    return render_template("create_class.html", teachers=teachers)

@app.route("/classes/archived")
def archived_classes():
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        if session.get("admin_id"):
            classes = db.query(Class).filter_by(is_archived=True).order_by(Class.archived_at.desc().nullslast()).all()
        else:
            classes = db.query(Class).filter_by(teacher_id=session["teacher_id"], is_archived=True).order_by(Class.archived_at.desc().nullslast()).all()
        return render_template("archived_classes.html", classes=classes)
    finally:
        db.close()

@app.route("/class/<int:class_id>/archive", methods=["POST"]) 
def archive_class(class_id):
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        if session.get("admin_id"):
            class_ = db.query(Class).filter_by(id=class_id).first()
        else:
            class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("index"))
        class_.is_archived = True
        class_.archived_at = datetime.utcnow()
        for a in db.query(Assignment).filter_by(class_id=class_.id).all():
            a.is_archived = True
            a.archived_at = datetime.utcnow()
        db.commit()
        flash("Class archived", "success")
    except SQLAlchemyError:
        db.rollback()
        flash("Failed to archive class", "danger")
    finally:
        db.close()
    return redirect(url_for("archived_classes"))

@app.route("/class/<int:class_id>/restore", methods=["POST"]) 
def restore_class(class_id):
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        if session.get("admin_id"):
            class_ = db.query(Class).filter_by(id=class_id).first()
        else:
            class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("archived_classes"))
        class_.is_archived = False
        class_.archived_at = None
        for a in db.query(Assignment).filter_by(class_id=class_.id).all():
            a.is_archived = False
            a.archived_at = None
        db.commit()
        flash("Class restored", "success")
    except SQLAlchemyError:
        db.rollback()
        flash("Failed to restore class", "danger")
    finally:
        db.close()
    return redirect(url_for("archived_classes"))

# --- Admin: Teacher Management ---
@app.route("/admin/teachers", methods=["GET", "POST"])
def admin_teachers():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        error = None
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            if not all([first_name, last_name, email, password]):
                error = "All fields are required"
            elif db.query(Teacher).filter_by(email=email).first():
                error = "Email already in use"
            else:
                t = Teacher(first_name=first_name, last_name=last_name, email=email)
                t.set_password(password)
                db.add(t)
                db.commit()
                flash("Teacher created", "success")
                return redirect(url_for("admin_teachers"))
        teachers = db.query(Teacher).order_by(Teacher.created_at.desc()).all()
        return render_template("admin_teachers.html", teachers=teachers, error=error)
    finally:
        db.close()

@app.route("/admin/teacher/<int:teacher_id>/edit", methods=["GET", "POST"])
def admin_edit_teacher(teacher_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter_by(id=teacher_id).first()
        if not teacher:
            flash("Teacher not found", "danger")
            return redirect(url_for("admin_teachers"))
        
        error = None
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            
            if not all([first_name, last_name, email]):
                error = "First name, last name, and email are required"
            elif email != teacher.email and db.query(Teacher).filter_by(email=email).first():
                error = "Email already in use by another teacher"
            else:
                teacher.first_name = first_name
                teacher.last_name = last_name
                teacher.email = email
                if password:  # Only update password if provided
                    teacher.set_password(password)
                db.commit()
                flash("Teacher updated successfully", "success")
                return redirect(url_for("admin_teachers"))
        
        return render_template("admin_edit_teacher.html", teacher=teacher, error=error)
    finally:
        db.close()

@app.route("/admin/teacher/<int:teacher_id>/delete", methods=["POST"])
def admin_delete_teacher(teacher_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter_by(id=teacher_id).first()
        if not teacher:
            flash("Teacher not found", "danger")
            return redirect(url_for("admin_teachers"))
        # Prevent deleting if teacher has classes to avoid unintended cascade
        has_classes = db.query(Class).filter_by(teacher_id=teacher.id).count() > 0
        if has_classes:
            flash("Cannot delete teacher with existing classes. Reassign or delete classes first.", "warning")
            return redirect(url_for("admin_teachers"))
        db.delete(teacher)
        db.commit()
        flash("Teacher deleted", "success")
        return redirect(url_for("admin_teachers"))
    finally:
        db.close()

# --- Admin: Class Management ---
@app.route("/admin/classes")
def admin_classes():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        classes = db.query(Class).order_by(Class.created_at.desc()).all()
        # Prefetch teachers
        teacher_map = {t.id: t for t in db.query(Teacher).all()}
        return render_template("admin_classes.html", classes=classes, teacher_map=teacher_map)
    finally:
        db.close()

@app.route("/admin/classes/create", methods=["GET", "POST"])
def admin_create_class():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            section = request.form.get("section", "").strip()
            teacher_id = request.form.get("teacher_id", "").strip()
            if not name or not teacher_id:
                flash("Class name and teacher are required", "danger")
            else:
                try:
                    teacher_id_int = int(teacher_id)
                except (TypeError, ValueError):
                    teacher_id_int = None
                teacher = db.query(Teacher).filter_by(id=teacher_id_int).first() if teacher_id_int else None
                if not teacher:
                    flash("Selected teacher not found", "danger")
                else:
                    new_class = Class(
                        name=name,
                        section=section if section else None,
                        class_code=generate_class_code(),
                        teacher_id=teacher.id
                    )
                    db.add(new_class)
                    db.commit()
                    flash("Class created", "success")
                    return redirect(url_for("admin_classes"))
        teachers = db.query(Teacher).order_by(Teacher.first_name.asc()).all()
        return render_template("admin_create_class.html", teachers=teachers)
    finally:
        db.close()

@app.route("/admin/class/<int:class_id>/edit", methods=["GET", "POST"])
def admin_edit_class(class_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(id=class_id).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("admin_classes"))
        
        error = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            section = request.form.get("section", "").strip()
            teacher_id = request.form.get("teacher_id", "").strip()
            
            if not name or not teacher_id:
                error = "Class name and teacher are required"
            else:
                try:
                    teacher_id_int = int(teacher_id)
                except (TypeError, ValueError):
                    teacher_id_int = None
                teacher = db.query(Teacher).filter_by(id=teacher_id_int).first() if teacher_id_int else None
                if not teacher:
                    error = "Selected teacher not found"
                else:
                    class_.name = name
                    class_.section = section if section else None
                    class_.teacher_id = teacher.id
                    db.commit()
                    flash("Class updated successfully", "success")
                    return redirect(url_for("admin_classes"))
        
        teachers = db.query(Teacher).order_by(Teacher.first_name.asc()).all()
        return render_template("admin_edit_class.html", class_=class_, teachers=teachers, error=error)
    finally:
        db.close()

@app.route("/admin/class/<int:class_id>/delete", methods=["POST"])
def admin_delete_class(class_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(id=class_id).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("admin_classes"))
        
        # Delete all related data safely
        assignments = db.query(Assignment).filter_by(class_id=class_.id).all()
        for assignment in assignments:
            # Delete answers -> submissions
            subq_submissions = db.query(AssignmentSubmission.id).filter(
                AssignmentSubmission.assignment_id == assignment.id
            ).subquery()
            db.query(StudentAnswer).filter(
                StudentAnswer.submission_id.in_(subq_submissions)
            ).delete(synchronize_session=False)
            db.query(AssignmentSubmission).filter(
                AssignmentSubmission.assignment_id == assignment.id
            ).delete(synchronize_session=False)

            # Delete question children -> questions
            q_ids = db.query(Question.id).filter(
                Question.assignment_id == assignment.id
            ).subquery()
            db.query(QuestionOption).filter(
                QuestionOption.question_id.in_(q_ids)
            ).delete(synchronize_session=False)
            db.query(CorrectAnswer).filter(
                CorrectAnswer.question_id.in_(q_ids)
            ).delete(synchronize_session=False)
            db.query(Question).filter(
                Question.assignment_id == assignment.id
            ).delete(synchronize_session=False)

            # Delete assignment last
            db.delete(assignment)

        # Delete enrollments of this class
        db.query(Enrollment).filter_by(class_id=class_.id).delete(synchronize_session=False)

        # Delete the class
        db.delete(class_)
        db.commit()
        flash("Class and related data deleted successfully", "success")
        return redirect(url_for("admin_classes"))
    except Exception as e:
        db.rollback()
        flash(f"Error deleting class: {str(e)}", "danger")
        return redirect(url_for("admin_classes"))
    finally:
        db.close()

# --- Admin Authentication & Dashboard ---
def require_admin():
    if not session.get("admin_id"):
        return redirect(url_for("admin_login"))
    return None

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    try:
        print(f"Admin login accessed - Method: {request.method}")
        if session.get("admin_id"):
            print("Admin already logged in, redirecting to dashboard")
            return redirect(url_for("admin_dashboard"))
        
        error = None
        if request.method == "POST":
            print("Processing admin login POST")
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            print(f"Login attempt for email: {email}")
            
            if not email or not password:
                error = "Email and password are required"
                print("Missing email or password")
            else:
                db = SessionLocal()
                try:
                    print("Querying for admin user")
                    admin = db.query(Admin).filter_by(email=email).first()
                    if not admin:
                        print(f"No admin found with email: {email}")
                        error = "Invalid email or password"
                    elif not admin.check_password(password):
                        print("Password check failed")
                        error = "Invalid email or password"
                    else:
                        print("Admin login successful")
                        session["admin_id"] = admin.id
                        session["admin_email"] = admin.email
                        flash("Welcome, Admin!", "success")
                        return redirect(url_for("admin_dashboard"))
                except Exception as e:
                    print(f"Database error during admin login: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    error = "Login failed. Please try again."
                finally:
                    db.close()
        
        print("Rendering admin login template")
        return render_template("admin_login.html", error=error)
    except Exception as e:
        print(f"Critical error in admin_login route: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Admin login error: {str(e)}", 500

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    flash("Logged out", "success")
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_dashboard():
    try:
        print("Admin dashboard accessed")
        if require_admin():
            print("Admin authentication failed, redirecting to login")
            return require_admin()
        
        print("Creating database session")
        db = SessionLocal()
        try:
            print("Querying teacher count")
            teacher_count = db.query(Teacher).count()
            print(f"Teacher count: {teacher_count}")
            
            print("Querying student count")
            student_count = db.query(Student).count()
            print(f"Student count: {student_count}")
            
            print("Querying class count")
            class_count = db.query(Class).filter_by(is_archived=False).count()
            print(f"Class count: {class_count}")
            
            print("Querying enrollment count")
            enrollment_count = db.query(Enrollment).count()
            print(f"Enrollment count: {enrollment_count}")
            
            # Get recent classes with proper error handling
            print("Querying recent classes")
            try:
                classes = db.query(Class).options(joinedload(Class.teacher)).filter_by(is_archived=False).order_by(Class.id.desc()).limit(10).all()
                print(f"Found {len(classes)} recent classes")
            except Exception as class_error:
                print(f"Error loading classes: {class_error}")
                import traceback
                traceback.print_exc()
                classes = []
            
            print("Rendering admin dashboard template")
            return render_template("admin_dashboard.html", 
                                   teacher_count=teacher_count, 
                                   student_count=student_count,
                                   class_count=class_count,
                                   enrollment_count=enrollment_count,
                                   classes=classes)
        except Exception as e:
            print(f"Database error in admin dashboard: {str(e)}")
            import traceback
            traceback.print_exc()
            db.rollback()
            print("Rendering dashboard with fallback values")
            return render_template("admin_dashboard.html", 
                                   teacher_count=0, 
                                   student_count=0,
                                   class_count=0,
                                   enrollment_count=0,
                                   classes=[])
        finally:
            print("Closing database session")
            db.close()
    except Exception as e:
        print(f"Critical error in admin_dashboard route: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Admin dashboard error: {str(e)}", 500

@app.route("/admin/create", methods=["GET", "POST"])
def admin_create():
    db = SessionLocal()
    try:
        existing_count = db.query(Admin).count()
        if existing_count > 0 and not session.get("admin_id"):
            flash("Admin already exists. Please login.", "danger")
            return redirect(url_for("admin_login"))
        error = None
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            confirm = request.form.get("confirm_password", "").strip()
            if not email or not password:
                error = "Email and password are required"
            elif password != confirm:
                error = "Passwords do not match"
            elif db.query(Admin).filter_by(email=email).first():
                error = "Email already in use"
            else:
                admin = Admin(email=email)
                admin.set_password(password)
                db.add(admin)
                db.commit()
                flash("Admin account created. Please login.", "success")
                return redirect(url_for("admin_login"))
        return render_template("admin_create.html", error=error)
    finally:
        db.close()

# --- Admin: Student Management ---
@app.route("/admin/students", methods=["GET", "POST"])
def admin_students():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        error = None
        if request.method == "POST":
            # Align with current Student model fields
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            grade_level = request.form.get("grade_level", "").strip()

            if not name or not email:
                error = "Name and email are required"
            elif db.query(Student).filter_by(email=email).first():
                error = "Email already exists"
            else:
                student = Student(
                    name=name,
                    email=email,
                    grade_level=grade_level if grade_level else None,
                    total_points=0,
                    last_active=datetime.utcnow()
                )
                db.add(student)
                db.commit()
                flash("Student created successfully", "success")
                return redirect(url_for("admin_students"))

        students = db.query(Student).order_by(Student.created_at.desc()).all()
        return render_template("admin_students.html", students=students, error=error)
    finally:
        db.close()

@app.route("/admin/student/<int:student_id>/edit", methods=["GET", "POST"])
def admin_edit_student(student_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            flash("Student not found", "danger")
            return redirect(url_for("admin_students"))
        
        error = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            grade_level = request.form.get("grade_level", "").strip()
            avatar_url = request.form.get("avatar_url", "").strip()

            if not name or not email:
                error = "Name and email are required"
            elif email != student.email and db.query(Student).filter_by(email=email).first():
                error = "Email already in use by another student"
            else:
                student.name = name
                student.email = email
                student.grade_level = grade_level if grade_level else None
                student.avatar_url = avatar_url if avatar_url else None
                db.commit()
                flash("Student updated successfully", "success")
                return redirect(url_for("admin_students"))

        return render_template("admin_edit_student.html", student=student, error=error)
    finally:
        db.close()

@app.route("/admin/student/<int:student_id>/delete", methods=["POST"])
def admin_delete_student(student_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            flash("Student not found", "danger")
            return redirect(url_for("admin_students"))
        
        # Check if student has submissions or enrollments
        has_submissions = db.query(AssignmentSubmission).filter_by(student_id=student.id).count() > 0
        has_enrollments = db.query(Enrollment).filter_by(student_id=student.id).count() > 0
        
        if has_submissions or has_enrollments:
            flash("Cannot delete student with existing submissions or enrollments. Remove those first.", "warning")
            return redirect(url_for("admin_students"))
        
        db.delete(student)
        db.commit()
        flash("Student deleted successfully", "success")
        return redirect(url_for("admin_students"))
    finally:
        db.close()

# --- Admin: Enrollment Management ---
@app.route("/admin/enrollments")
def admin_enrollments():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        # Fix the query to use enrolled_at field and correct student field
        enrollments = db.query(Enrollment).options(
            joinedload(Enrollment.student),
            joinedload(Enrollment.class_).joinedload(Class.teacher)
        ).order_by(Enrollment.enrolled_at.desc()).all()
        
        students = db.query(Student).order_by(Student.name.asc()).all()
        classes = db.query(Class).filter_by(is_archived=False).order_by(Class.name.asc()).all()
        return render_template("admin_enrollments.html", enrollments=enrollments, students=students, classes=classes)
    except Exception as e:
        flash(f"Error loading enrollments: {str(e)}", "danger")
        return redirect(url_for("admin_dashboard"))
    finally:
        db.close()

@app.route("/admin/enrollments/create", methods=["POST"])
def admin_create_enrollment():
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        student_id = request.form.get("student_id", "").strip()
        class_id = request.form.get("class_id", "").strip()
        
        if not student_id or not class_id:
            flash("Student and class are required", "danger")
            return redirect(url_for("admin_enrollments"))
        
        try:
            student_id_int = int(student_id)
            class_id_int = int(class_id)
        except (TypeError, ValueError):
            flash("Invalid student or class selection", "danger")
            return redirect(url_for("admin_enrollments"))
        
        student = db.query(Student).filter_by(id=student_id_int).first()
        class_ = db.query(Class).filter_by(id=class_id_int).first()
        
        if not student or not class_:
            flash("Selected student or class not found", "danger")
            return redirect(url_for("admin_enrollments"))
        
        # Check if already enrolled
        existing = db.query(Enrollment).filter_by(student_id=student.id, class_id=class_.id).first()
        if existing:
            flash("Student is already enrolled in this class", "warning")
            return redirect(url_for("admin_enrollments"))
        
        enrollment = Enrollment(student_id=student.id, class_id=class_.id)
        db.add(enrollment)
        db.commit()
        flash("Student enrolled successfully", "success")
        return redirect(url_for("admin_enrollments"))
    finally:
        db.close()

@app.route("/admin/enrollment/<int:enrollment_id>/delete", methods=["POST"])
def admin_delete_enrollment(enrollment_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        enrollment = db.query(Enrollment).filter_by(id=enrollment_id).first()
        if not enrollment:
            flash("Enrollment not found", "danger")
            return redirect(url_for("admin_enrollments"))
        
        db.delete(enrollment)
        db.commit()
        flash("Enrollment removed successfully", "success")
        return redirect(url_for("admin_enrollments"))
    finally:
        db.close()

@app.route("/admin/enrollment/<int:enrollment_id>/edit", methods=["GET", "POST"])
def admin_edit_enrollment(enrollment_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        enrollment = db.query(Enrollment).options(
            joinedload(Enrollment.student),
            joinedload(Enrollment.class_)
        ).filter_by(id=enrollment_id).first()
        
        if not enrollment:
            flash("Enrollment not found", "danger")
            return redirect(url_for("admin_enrollments"))
        
        if request.method == "POST":
            student_id = request.form.get("student_id", "").strip()
            class_id = request.form.get("class_id", "").strip()
            
            if not student_id or not class_id:
                flash("Student and class are required", "danger")
                return render_template("admin_edit_enrollment.html", enrollment=enrollment)
            
            try:
                student_id_int = int(student_id)
                class_id_int = int(class_id)
            except (TypeError, ValueError):
                flash("Invalid student or class selection", "danger")
                return render_template("admin_edit_enrollment.html", enrollment=enrollment)
            
            student = db.query(Student).filter_by(id=student_id_int).first()
            class_ = db.query(Class).filter_by(id=class_id_int).first()
            
            if not student or not class_:
                flash("Selected student or class not found", "danger")
                return render_template("admin_edit_enrollment.html", enrollment=enrollment)
            
            # Check if already enrolled (except current enrollment)
            existing = db.query(Enrollment).filter_by(student_id=student.id, class_id=class_.id).filter(Enrollment.id != enrollment.id).first()
            if existing:
                flash("Student is already enrolled in this class", "warning")
                return render_template("admin_edit_enrollment.html", enrollment=enrollment)
            
            enrollment.student_id = student.id
            enrollment.class_id = class_.id
            db.commit()
            flash("Enrollment updated successfully", "success")
            return redirect(url_for("admin_enrollments"))
        
        students = db.query(Student).order_by(Student.name.asc()).all()
        classes = db.query(Class).filter_by(is_archived=False).order_by(Class.name.asc()).all()
        return render_template("admin_edit_enrollment.html", enrollment=enrollment, students=students, classes=classes)
    except Exception as e:
        flash(f"Error editing enrollment: {str(e)}", "danger")
        return redirect(url_for("admin_enrollments"))
    finally:
        db.close()

@app.route("/create_assignment/<int:class_id>", methods=["GET", "POST"])
def create_assignment(class_id):
    # Allow admin as well
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        # Ensure class belongs to current teacher, or allow admin
        if session.get("admin_id"):
            class_ = db.query(Class).filter_by(id=class_id).first()
        else:
            class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
        if not class_:
            flash("Class not found", "danger")
            # Admin returns to assignments list for this class
            if session.get("admin_id"):
                return redirect(url_for("admin_class_assignments", class_id=class_id))
            return redirect(url_for("index"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            questions_json = request.form.get("questions", "[]")

            if not title:
                flash("Assignment title is required", "danger")
                return render_template("create_assignment.html", class_=class_)

            try:
                questions_data = json.loads(questions_json)
            except json.JSONDecodeError as e:
                flash("Invalid questions data", "danger")
                return render_template("create_assignment.html", class_=class_)

            assignment = Assignment(class_id=class_id, title=title, description=description)
            db.add(assignment)
            db.flush()  # get assignment.id

            for q in questions_data:
                q_text = q.get("text", "").strip()
                q_type = q.get("type")
                points = int(q.get("points", 1))
                help_video_url = q.get("help_video_url", "").strip()

                if not q_text or q_type not in ["multiple_choice", "identification", "enumeration", "problem_solving", "essay"]:
                    continue  # skip invalid question

                question = Question(
                    assignment_id=assignment.id,
                    question_text=q_text,
                    question_type=q_type,
                    points=points,
                    help_video_url=help_video_url
                )
                db.add(question)
                db.flush()

                # Handle specific types
                if q_type == "multiple_choice":
                    options = q.get("options", [])
                    correct_answers = q.get("correct_answers", [])
                    for opt in options:
                        db.add(QuestionOption(question_id=question.id, option_text=opt))
                    for ans in correct_answers:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=ans))

                elif q_type == "identification":
                    correct = q.get("correct_answer", "")
                    if correct:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=correct))

                elif q_type == "enumeration":
                    correct_answers = q.get("correct_answers", [])
                    for ans in correct_answers:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=ans))

                elif q_type == "problem_solving":
                    correct = q.get("correct_answer", "")
                    if correct:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=correct))

                # essay: no correct answer

            db.commit()
            flash("Assignment created successfully!", "success")
            if session.get("admin_id"):
                return redirect(url_for("admin_class_assignments", class_id=class_id))
            return redirect(url_for("index"))

        # GET
        return render_template("create_assignment.html", class_=class_)

    except SQLAlchemyError as e:
        db.rollback()
        flash("An error occurred while creating the assignment", "danger")
        return redirect(url_for("index"))
    except Exception as e:
        db.rollback()
        flash("An error occurred while creating the assignment", "danger")
        return redirect(url_for("index"))
    finally:
        db.close()

@app.route("/view_assignment/<int:assignment_id>")
def view_assignment(assignment_id):
    # Allow admin as well
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        
        # Check if teacher owns this quiz's class
        if not session.get("admin_id") and assignment.class_.teacher_id != session["teacher_id"]:
            flash("Access denied", "danger")
            return redirect(url_for("index"))
        
        questions = db.query(Question).filter_by(assignment_id=assignment_id).all()
        
        # Load options and correct answers for each question
        for question in questions:
            question.options = db.query(QuestionOption).filter_by(question_id=question.id).all()
            question.correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
        
        return render_template("view_assignment.html", assignment=assignment, questions=questions)
    
    except SQLAlchemyError as e:
        flash("Error loading assignment", "danger")
        return redirect(url_for("index"))
    finally:
        db.close()

@app.route("/edit_assignment/<int:assignment_id>", methods=["GET", "POST"])
def edit_assignment(assignment_id):
    # Allow admin as well
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment or (not session.get("admin_id") and assignment.class_.teacher_id != session["teacher_id"]):
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            questions_json = request.form.get("questions", "[]")
            
            if not title:
                flash("Assignment title is required", "danger")
                return render_template("edit_assignment.html", assignment=assignment)
            
            try:
                questions_data = json.loads(questions_json)
            except json.JSONDecodeError:
                flash("Invalid questions data", "danger")
                return render_template("edit_assignment.html", assignment=assignment)
            
            # Update quiz details
            assignment.title = title
            assignment.description = description
            
            # Delete existing questions and rebuild
            db.query(Question).filter_by(assignment_id=assignment.id).delete()
            db.flush()
                
            # Add updated questions
            for q in questions_data:
                q_text = q.get("text", "").strip()
                q_type = q.get("type")
                points = int(q.get("points", 1))
                help_video_url = q.get("help_video_url", "").strip()
                
                if not q_text or q_type not in ["multiple_choice", "enumeration", "problem_solving", "essay"]:
                    continue
                
                question = Question(
                    assignment_id=assignment.id,
                    question_text=q_text,
                    question_type=q_type,
                    points=points,
                    help_video_url=help_video_url
                )
                db.add(question)
                db.flush()
                
                # Handle specific types (same logic as create_assignment)
                if q_type == "multiple_choice":
                    options = q.get("options", [])
                    correct_answers = q.get("correct_answers", [])
                    for opt in options:
                        db.add(QuestionOption(question_id=question.id, option_text=opt))
                    for ans in correct_answers:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=ans))
                elif q_type == "enumeration":
                    correct_answers = q.get("correct_answers", [])
                    for ans in correct_answers:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=ans))
                elif q_type == "problem_solving":
                    correct = q.get("correct_answer", "")
                    if correct:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=correct))
                elif q_type == "identification":
                    correct = q.get("correct_answer", "")
                    if correct:
                        db.add(CorrectAnswer(question_id=question.id, answer_text=correct))

            db.commit()
            flash("Assignment updated successfully!", "success")
            # Admin back to admin list
            if session.get("admin_id"):
                return redirect(url_for("admin_class_assignments", class_id=assignment.class_id))
            return redirect(url_for("view_assignment", assignment_id=assignment.id))
        
        # GET request - load existing quiz data
        questions = db.query(Question).filter_by(assignment_id=assignment_id).all()
        assignment_data = []
        
        for question in questions:
            q_data = {
                "text": question.question_text,
                "type": question.question_type,
                "points": question.points,
                "help_video_url": question.help_video_url or ""
            }
            
            if question.question_type == "multiple_choice":
                options = db.query(QuestionOption).filter_by(question_id=question.id).all()
                correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                q_data["options"] = [opt.option_text for opt in options]
                q_data["correct_answers"] = [ans.answer_text for ans in correct_answers]
            elif question.question_type == "enumeration":
                correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                q_data["correct_answers"] = [ans.answer_text for ans in correct_answers]
            elif question.question_type == "problem_solving":
                correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                q_data["correct_answer"] = correct_answer.answer_text if correct_answer else ""
            elif question.question_type == "identification":
                correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                q_data["correct_answer"] = correct_answer.answer_text if correct_answer else ""
            elif question.question_type == "fill_in_the_blanks":
                correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                q_data["correct_answers"] = [ans.answer_text for ans in correct_answers]
            elif question.question_type == "yes_no":
                options = db.query(QuestionOption).filter_by(question_id=question.id).all()
                correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                q_data["options"] = [opt.option_text for opt in options]
                q_data["correct_answers"] = [correct_answer.answer_text] if correct_answer else []
            
            assignment_data.append(q_data)

        return render_template("edit_assignment.html", assignment=assignment, assignment_data=json.dumps(assignment_data))

    except SQLAlchemyError as e:
        db.rollback()
        flash("Error loading assignment", "danger")
        return redirect(url_for("index"))
    finally:
        db.close()

@app.route("/delete_assignment/<int:assignment_id>")
def delete_assignment(assignment_id):
    # Allow admin as well
    if not session.get("teacher_id") and not session.get("admin_id"):
        return redirect(url_for("login"))

    assignment = None
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            flash("Assignment not found", "danger")
        elif session.get("admin_id") or assignment.class_.teacher_id == session["teacher_id"]:
            # Delete related records in proper order
            # 1. Delete student answers through submissions
            submissions = db.query(AssignmentSubmission).filter_by(assignment_id=assignment.id).all()
            for submission in submissions:
                db.query(StudentAnswer).filter_by(submission_id=submission.id).delete()
            # 2. Delete assignment submissions
            db.query(AssignmentSubmission).filter_by(assignment_id=assignment.id).delete()
            # 3. Delete correct answers
            questions = db.query(Question).filter_by(assignment_id=assignment.id).all()
            for question in questions:
                db.query(CorrectAnswer).filter_by(question_id=question.id).delete()
                db.query(QuestionOption).filter_by(question_id=question.id).delete()
            # 4. Delete questions
            db.query(Question).filter_by(assignment_id=assignment.id).delete()
            # 5. Finally delete the assignment
            db.delete(assignment)
            db.commit()
            flash("Assignment deleted successfully", "success")
        else:
            flash("You don't have permission to delete this assignment", "danger")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting assignment: {str(e)}", "danger")
    finally:
        db.close()
    
    if session.get("admin_id") and assignment:
        return redirect(url_for("admin_class_assignments", class_id=assignment.class_id))
    return redirect(url_for("index"))

# --- Admin: Assignments list per class ---
@app.route("/admin/class/<int:class_id>/assignments")
def admin_class_assignments(class_id):
    if require_admin():
        return require_admin()
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(id=class_id).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("admin_classes"))
        assignments = db.query(Assignment).filter_by(class_id=class_id).order_by(Assignment.created_at.desc()).all()
        return render_template("admin_class_assignments.html", class_=class_, assignments=assignments)
    finally:
        db.close()

@app.route("/take_assignment/<int:assignment_id>", methods=["GET", "POST"])
def take_assignment(assignment_id):

    # Assume student_id is stored in session (from mobile game or web login)
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in as a student to take the assignment.", "danger")
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        # Prevent retake
        existing_submission = db.query(AssignmentSubmission).filter_by(assignment_id=assignment_id, student_id=student_id).first()
        if existing_submission:
            flash("You have already submitted this assignment. Retakes are not allowed.", "warning")
            return redirect(url_for("view_assignment", assignment_id=assignment_id))

        if request.method == "POST":
            # Process quiz submission
            student_name = request.form.get("student_name", "Anonymous")
            answers = {}
            score = 0
            total_points = 0
            
            for question in assignment.questions:
                total_points += question.points
                answer_key = f"question_{question.id}"
                student_answer = request.form.get(answer_key, "").strip()
                
                if student_answer:
                    is_correct = False
                    points_earned = 0
                    
                    if question.question_type == "multiple_choice":
                        correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                        if any(ans.answer_text == student_answer for ans in correct_answers):
                            is_correct = True
                            points_earned = question.points
                    
                    elif question.question_type == "enumeration":
                        correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                        correct_texts = [ans.answer_text.lower().strip() for ans in correct_answers]
                        if student_answer.lower().strip() in correct_texts:
                            is_correct = True
                            points_earned = question.points
                    
                    elif question.question_type == "problem_solving":
                        correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                        if correct_answer and student_answer.lower().strip() == correct_answer.answer_text.lower().strip():
                            is_correct = True
                            points_earned = question.points
                    
                    elif question.question_type == "identification":
                        correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                        if correct_answer and student_answer.lower().strip() == correct_answer.answer_text.lower().strip():
                            is_correct = True
                            points_earned = question.points
                    
                    elif question.question_type == "fill_in_the_blanks":
                        correct_answers = db.query(CorrectAnswer).filter_by(question_id=question.id).all()
                        # For fill in the blanks, student answer should be separated by |
                        if correct_answers:
                            answer_parts = [part.strip().lower() for part in student_answer.split('|')]
                            correct_parts = [ca.answer_text.strip().lower() for ca in correct_answers]
                            if len(answer_parts) == len(correct_parts) and all(a == c for a, c in zip(answer_parts, correct_parts)):
                                is_correct = True
                                points_earned = question.points
                    
                    elif question.question_type == "essay":
                        # Essays require manual grading
                        points_earned = 0
                        is_correct = None  # Pending grading
                    
                    elif question.question_type == "yes_no":
                        correct_answer = db.query(CorrectAnswer).filter_by(question_id=question.id).first()
                        if correct_answer and student_answer.strip() == correct_answer.answer_text.strip():
                            is_correct = True
                            points_earned = question.points
                    
                    score += points_earned
                    answers[question.id] = {
                        'answer': student_answer,
                        'correct': is_correct,
                        'points': points_earned
                    }
            
            # Save submission
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=student_id,
                score=score,
                total_points=total_points,
                answers_json=json.dumps(answers)
            )
            db.add(submission)
            db.commit()
            flash("Quiz submitted successfully!", "success")
            return redirect(url_for("assignment_results", assignment_id=assignment_id))
        
        # GET request - show quiz form
        questions = db.query(Question).filter_by(assignment_id=assignment_id).all()
        
        # Load options for multiple choice questions
        for question in questions:
            if question.question_type == "multiple_choice":
                question.options = db.query(QuestionOption).filter_by(question_id=question.id).all()

        if request.method == "GET":
            # Shuffle options for multiple choice questions
            for question in questions:
                if question.question_type == "multiple_choice":
                    random.shuffle(question.options)

        return render_template("take_assignment.html", assignment=assignment, questions=questions)

    except SQLAlchemyError as e:
        flash("Error loading assignment", "danger")
        return redirect(url_for("login"))
    finally:
        db.close()

@app.route("/class/<int:class_id>/info")
def class_info(class_id):
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
        if not class_:
            flash("Class not found", "danger")
            return redirect(url_for("index"))
        
        students = [enrollment.student for enrollment in class_.enrollments]
        assignments = class_.assignments
        
        # Calculate progress for each assignment
        assignment_stats = []
        for assignment in assignments:
            submissions = db.query(AssignmentSubmission).filter_by(assignment_id=assignment.id).all()
            total_students = len(students)
            submitted_count = len(submissions)
            
            # Calculate average score
            scores = [sub.score for sub in submissions if sub.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            total_points = sum(q.points for q in assignment.questions)
            avg_percentage = (avg_score / total_points * 100) if total_points > 0 else 0
            
            assignment_stats.append({
                'assignment': assignment,
                'total_students': total_students,
                'submitted_count': submitted_count,
                'completion_rate': (submitted_count / total_students * 100) if total_students > 0 else 0,
                'avg_score': avg_score,
                'avg_percentage': avg_percentage,
                'submissions': submissions
            })
        
        # Student progress overview
        student_progress = []
        for student in students:
            student_submissions = db.query(AssignmentSubmission).join(Assignment).filter(
                AssignmentSubmission.student_id == student.id,
                Assignment.class_id == class_id
            ).all()
            
            total_assignments = len(assignments)
            completed_assignments = len(student_submissions)
            completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
            
            # Calculate average grade
            scores = [sub.score for sub in student_submissions if sub.score is not None]
            if scores:
                total_points = []
                for sub in student_submissions:
                    if sub.score is not None:
                        assignment_total = sum(q.points for q in sub.assignment.questions)
                        total_points.append(assignment_total)
                avg_percentage = (sum(scores) / sum(total_points) * 100) if total_points else 0
            else:
                avg_percentage = 0
            
            student_progress.append({
                'student': student,
                'total_assignments': total_assignments,
                'completed_assignments': completed_assignments,
                'completion_rate': completion_rate,
                'avg_percentage': avg_percentage,
                'recent_submissions': student_submissions[-3:] if student_submissions else []
            })
        
        return render_template("class_info.html", 
                             class_=class_, 
                             students=students, 
                             assignments=assignments,
                             assignment_stats=assignment_stats,
                             student_progress=student_progress)
    finally:
        db.close()

@app.route("/assignment/<int:assignment_id>/monitor")
def assignment_monitor(assignment_id):

    if "teacher_id" not in session:
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment or assignment.class_.teacher_id != session["teacher_id"]:
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        
        students = [enrollment.student for enrollment in assignment.class_.enrollments]
        submissions = db.query(AssignmentSubmission).filter_by(assignment_id=assignment_id).all()
        
        # Create submission lookup
        submission_lookup = {sub.student_id: sub for sub in submissions}
        
        # Student results with detailed breakdown
        student_results = []
        for student in students:
            submission = submission_lookup.get(student.id)
            if submission:
                # Calculate question breakdown
                question_breakdown = []
                for question in assignment.questions:
                    answer = db.query(StudentAnswer).filter_by(
                        submission_id=submission.id,
                        question_id=question.id
                    ).first()
                    
                    question_breakdown.append({
                        'question': question,
                        'answer': answer,
                        'correct': answer.is_correct if answer else None,
                        'points_earned': answer.points_earned if answer else 0
                    })
                
                total_points = sum(q.points for q in assignment.questions)
                percentage = (submission.score / total_points * 100) if total_points > 0 else 0
                
                student_results.append({
                    'student': student,
                    'submission': submission,
                    'percentage': percentage,
                    'question_breakdown': question_breakdown,
                    'status': 'submitted',
                    'submitted_at': submission.submitted_at
                })
            else:
                student_results.append({
                    'student': student,
                    'submission': None,
                    'percentage': 0,
                    'question_breakdown': [],
                    'status': 'not_submitted',
                    'submitted_at': None
                })
        
        # Sort by score descending, then by name
        student_results.sort(key=lambda x: (-x['percentage'], x['student'].name))
        
        # Assignment statistics
        total_students = len(students)
        submitted_count = len(submissions)
        scores = [sub.score for sub in submissions if sub.score is not None]
        total_points = sum(q.points for q in assignment.questions)
        
        stats = {
            'total_students': total_students,
            'submitted_count': submitted_count,
            'completion_rate': (submitted_count / total_students * 100) if total_students > 0 else 0,
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'avg_percentage': (sum(scores) / len(scores) / total_points * 100) if scores and total_points > 0 else 0,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'total_points': total_points
        }
        
        return render_template("assignment_monitor.html", 
                             assignment=assignment,
                             student_results=student_results,
                             stats=stats)
    finally:
        db.close()

@app.route("/assignment_results/<int:assignment_id>")
def assignment_results(assignment_id):
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment or assignment.class_.teacher_id != session["teacher_id"]:
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        
        # Get submissions with student information
        submissions = db.query(AssignmentSubmission).filter_by(assignment_id=assignment_id).all()
        
        # Add student information to each submission
        for submission in submissions:
            submission.student = db.query(Student).filter_by(id=submission.student_id).first()
        
        return render_template("assignment_results_teacher.html", assignment=assignment, submissions=submissions)
    finally:
        db.close()

# Server Startup

# Combined ASGI application for production
def create_combined_app():
    print("Creating combined app...")
    
    # Initialize database and tables
    print("Initializing database...")
    init_db()
    
    # Ensure tables are created
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database table creation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Seed admin data
    print("Seeding admin data...")
    seed_default_admin()
    
    # FastAPI is the main app
    main_app = api  # Use our existing FastAPI app
    print("FastAPI app initialized")
    
    # Mount Flask for web dashboard at a sub-path 
    main_app.mount("/dashboard", WSGIMiddleware(app))
    print("Flask app mounted on FastAPI at /dashboard")
    
    return main_app

# Add a simple admin test route
@app.route("/admin/test")
def admin_test():
    return "Admin route is working!", 200

# Create the combined app instance for production deployment
combined_app = create_combined_app()

def run_flask():

    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Starting Flask Web Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def run_fastapi():

    port = int(os.environ.get("PORT", 8001))
    print(f"🎮 Starting FastAPI Game API on http://localhost:{port}")
    print(f"📚 API Documentation available at http://localhost:{port}/docs")
    uvicorn.run(api, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 CLASSROOM MANAGEMENT SYSTEM")
    print("="*60)
    
    # Check if running in production (Render sets this environment variable)
    if os.environ.get("RENDER") or os.environ.get("PORT"):
        print("🚀 Running in production mode (FastAPI main)")
        # In production, run combined server
        port = int(os.environ.get("PORT", 10000))
        print(f"🎮 Unity API: Available at root /")
        print(f"📋 Web Dashboard: Available at /dashboard/")
        print(f"📖 API Docs: /docs")
        print("="*60 + "\n")
        
        # Create and run combined application
        combined_app = create_combined_app()
        uvicorn.run(combined_app, host="0.0.0.0", port=port, log_level="info")
    else:
        print("� Running in development mode")
        print("�📋 Teachers: Use web dashboard at http://localhost:5000")
        print("🎮 Unity Game: Connect to API at http://localhost:8001")
        print("📖 API Docs: http://localhost:8001/docs")
        print("="*60 + "\n")
        
        # Start both servers in separate threads
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        
        flask_thread.start()
        fastapi_thread.start()
        
        try:
            # Keep main thread alive
            flask_thread.join()
            fastapi_thread.join()
        except KeyboardInterrupt:
            print("\n👋 Shutting down servers...")
            print("Goodbye!")
