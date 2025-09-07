# ==================== IMPORTS ====================
# Flask imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Database imports
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, inspect, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError

# Utility imports
import os
import re
import json
import random
import string
import threading
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import io

# ==================== DATABASE CONFIGURATION ====================
# Database setup and configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "school.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create database directory if it doesn't exist
os.makedirs(BASE_DIR, exist_ok=True)

# Database engine configuration with thread safety for Flask/FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# ==================== HELPER FUNCTIONS ====================
# Database session context manager for FastAPI
from functools import wraps

def with_db_session(func):
    """Decorator to handle database sessions automatically"""
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
    """Database session context manager for cleaner code"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

# Common error handlers
def handle_db_error(e, error_msg="Database error occurred"):
    """Handle database errors consistently"""
    print(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail=f"{error_msg}: {str(e)}")

def handle_not_found(item_name="Item"):
    """Handle not found errors consistently"""
    raise HTTPException(status_code=404, detail=f"{item_name} not found")

# Authentication helper for Flask routes
def require_login():
    """Check if user is logged in (Flask routes)"""
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    return None

# Response formatters
def success_response(data, message="Success"):
    """Standard success response format"""
    return {"status": "success", "message": message, "data": data}

def error_response(message, status_code=400):
    """Standard error response format"""
    raise HTTPException(status_code=status_code, detail=message)

# ==================== DATABASE MODELS ====================
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
    teacher = relationship("Teacher", back_populates="classes")
    assignments = relationship("Assignment", back_populates="class_", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="class_", cascade="all, delete-orphan")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    points = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
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
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
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

# Initialize database tables
print("\n=== Database Initialization ===")
if init_db():
    print("Database setup completed successfully")
else:
    print("Failed to initialize database")
    exit(1)

# Flask app setup

# ==================== APP INITIALIZATION ====================

# Flask app for web dashboard (Teachers)
app = Flask(__name__)
app.secret_key = 'dev-secret-key-replace-in-production'  # Replace with secure key in production

# FastAPI app for Unity/Android Game API
api = FastAPI(
    title="Classroom Game API",
    description="API for Unity turn-based game to communicate with classroom system",
    version="1.0.0"
)

# CORS middleware for FastAPI (allows Unity/Android to connect)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your game's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== FASTAPI ENDPOINTS FOR UNITY/ANDROID ====================
# API endpoints for Unity game and Android app communication

@api.get("/", summary="API Health Check")
def api_root():
    """Root endpoint to verify API is running"""
    return {
        "message": "Classroom Game API is running",
        "status": "active",
        "endpoints": {
            "classes": "/api/classes",
            "assignments": "/api/assignments/{class_id}",
            "assignment_detail": "/api/assignment/{assignment_id}",
            "submit": "/api/submit/{assignment_id}",
            "student_register": "/api/student/register",
            "leaderboard": "/api/leaderboard/{class_id}"
        }
    }

@api.get("/api/classes", summary="Get All Classes")
@with_db_session
def get_all_classes(db):
    """Get all available classes for students to join"""
    try:
        classes = db.query(Class).all()
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

@api.get("/api/class/{class_code}/assignments", summary="Get Assignments by Class Code")
@with_db_session
def get_assignments_by_code(db, class_code: str):
    """Get all assignments for a class using class code (easier for students)"""
    try:
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            handle_not_found("Class")
        
        assignments = db.query(Assignment).filter_by(class_id=class_.id).all()
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

@api.get("/api/assignment/{assignment_id}", summary="Get Assignment Questions")
def get_assignment_for_game(assignment_id: int):
    """Get assignment with questions formatted for Unity game"""
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
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

@api.post("/api/student/register", summary="Register Student for Mobile Game")
def register_student_for_game(student_data: dict):
    """Register a new student from the Unity mobile game"""
    db = SessionLocal()
    try:
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

@api.post("/api/student/simple-register", summary="Simple Student Registration (No Class)")
def simple_register_student(student_data: dict):
    """Register a new student without class enrollment"""
    db = SessionLocal()
    try:
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

@api.post("/api/student/login", summary="Student Login")
def login_student(login_data: dict):
    """Student login with email and password"""
    db = SessionLocal()
    try:
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

@api.post("/api/student/join-class", summary="Join Class with Code")
def join_class_with_code(join_data: dict):
    """Allow student to join a class using class code"""
    db = SessionLocal()
    try:
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
        
        return {
            "status": "success",
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

@api.post("/api/submit/{assignment_id}", summary="Submit Assignment Answers")
def submit_assignment_from_game(assignment_id: int, submission_data: dict):
    """Submit assignment answers from Unity game"""
    db = SessionLocal()
    try:
        student_id = submission_data.get("student_id")
        answers = submission_data.get("answers", {})
        
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID is required")
        
        # Check if assignment exists
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Check for existing submission
        existing_submission = db.query(AssignmentSubmission).filter_by(
            assignment_id=assignment_id, student_id=student_id
        ).first()
        if existing_submission:
            raise HTTPException(status_code=400, detail="Assignment already submitted")
        
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
            student.total_points += score
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

@api.get("/api/leaderboard/{class_code}", summary="Get Class Leaderboard")
def get_class_leaderboard(class_code: str):
    """Get leaderboard for turn-based game competition"""
    db = SessionLocal()
    try:
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

@api.get("/api/student/{student_id}/profile", summary="Get Student Profile for Mobile")
def get_student_profile(student_id: int):
    """Get student profile data for Unity mobile game"""
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

@api.put("/api/student/{student_id}/avatar", summary="Update Student Avatar")
def update_student_avatar(student_id: int, avatar_data: dict):
    """Update student avatar URL from mobile game"""
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

# ==================== UTILITY FUNCTIONS ====================

def generate_class_code(length=7):
    """Generate unique class code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        db = SessionLocal()
        try:
            existing = db.query(Class).filter_by(class_code=code).first()
            if not existing:
                return code
        finally:
            db.close()

# ==================== FLASK ROUTES FOR TEACHERS ====================
# Web routes for teacher dashboard and classroom management

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
            
        classes = db.query(Class).filter_by(teacher_id=teacher.id).order_by(Class.created_at.desc()).all()
        return render_template("dashboard.html", teacher=teacher, classes=classes)
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
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["name"]
        section = request.form.get("section", "").strip()
        
        if not name:
            flash("Class name is required", "danger")
            return render_template("create_class.html")
        
        db = SessionLocal()
        try:
            new_class = Class(
                name=name,
                section=section if section else None,
                class_code=generate_class_code(),
                teacher_id=session["teacher_id"]
            )
            db.add(new_class)
            db.commit()
            
            flash(f"Class '{name}' created successfully!", "success")
            return redirect(url_for("index"))
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error creating class: {str(e)}")
            flash("An error occurred while creating the class", "danger")
        finally:
            db.close()
    
    return render_template("create_class.html")

@app.route("/create_assignment/<int:class_id>", methods=["GET", "POST"])
def create_assignment(class_id):
    """Dynamic quiz builder similar to Google Forms."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        # Ensure class belongs to current teacher
        class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
        if not class_:
            flash("Class not found", "danger")
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
            return redirect(url_for("index"))

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
    """View quiz details with all questions."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            flash("Assignment not found", "danger")
            return redirect(url_for("index"))
        
        # Check if teacher owns this quiz's class
        if assignment.class_.teacher_id != session["teacher_id"]:
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
    """Edit existing assignment."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment or assignment.class_.teacher_id != session["teacher_id"]:
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
    """Delete assignment."""
    if "teacher_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if assignment and assignment.class_.teacher_id == session["teacher_id"]:
            db.delete(assignment)
            db.commit()
            flash("Assignment deleted successfully", "success")
        else:
            flash("Assignment not found", "danger")
    except SQLAlchemyError as e:
        flash("Error deleting assignment", "danger")
    finally:
        db.close()
    return redirect(url_for("index"))

@app.route("/take_assignment/<int:assignment_id>", methods=["GET", "POST"])
def take_assignment(assignment_id):
    """Student interface to take assignment."""
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
    """Google Classroom style assignment monitoring page"""
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

# JMeter Test Endpoints (GET only)
@app.route("/test/register")
def test_register_get():
    """GET endpoint for JMeter testing - creates a test teacher"""
    import uuid
    test_id = str(uuid.uuid4())[:8]
    
    db = SessionLocal()
    try:
        new_teacher = Teacher(
            first_name=f"Test_{test_id}",
            last_name="Teacher",
            email=f"test_{test_id}@example.com"
        )
        new_teacher.set_password("password123")
        
        db.add(new_teacher)
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Test teacher created",
            "email": f"test_{test_id}@example.com",
            "password": "password123"
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.route("/test/login")
def test_login_get():
    """GET endpoint for JMeter testing - simulates login check"""
    db = SessionLocal()
    try:
        teacher_count = db.query(Teacher).count()
        if teacher_count > 0:
            latest_teacher = db.query(Teacher).order_by(Teacher.created_at.desc()).first()
            return {
                "status": "success", 
                "message": "Login test successful",
                "teacher_count": teacher_count,
                "latest_teacher": latest_teacher.email
            }
        else:
            return {"status": "error", "message": "No teachers found"}
    finally:
        db.close()

@app.route("/test/create_class")
def test_create_class_get():
    """GET endpoint for JMeter testing - creates a test class"""
    db = SessionLocal()
    try:
        # Get the latest teacher
        teacher = db.query(Teacher).order_by(Teacher.created_at.desc()).first()
        if not teacher:
            return {"status": "error", "message": "No teacher found"}
        
        import uuid
        test_id = str(uuid.uuid4())[:6]
        
        new_class = Class(
            name=f"Test Class {test_id}",
            section="A",
            class_code=generate_class_code(),
            teacher_id=teacher.id
        )
        db.add(new_class)
        db.commit()
        
        return {
            "status": "success",
            "message": "Test class created",
            "class_name": new_class.name,
            "class_code": new_class.class_code,
            "teacher": teacher.email
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.route("/test/status")
def test_status():
    """GET endpoint to check system status"""
    db = SessionLocal()
    try:
        teacher_count = db.query(Teacher).count()
        class_count = db.query(Class).count()
        quiz_count = db.query(Assignment).count()
        
        return {
            "status": "success",
            "database": "connected",
            "teachers": teacher_count,
            "classes": class_count,
            "quizzes": quiz_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# ==================== SERVER STARTUP ====================

def run_flask():
    """Run Flask web dashboard for teachers"""
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Starting Flask Web Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def run_fastapi():
    """Run FastAPI for Unity/Android game"""
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
        print("🚀 Running in production mode")
        # In production, run combined server
        port = int(os.environ.get("PORT", 10000))
        print(f"📋 Web Dashboard: Available on assigned port")
        print(f"🎮 Unity API: Same server, use /api/ endpoints")
        print(f"📖 API Docs: /docs")
        print("="*60 + "\n")
        
        # Run Flask (which includes FastAPI endpoints)
        app.run(host="0.0.0.0", port=port, debug=False)
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
