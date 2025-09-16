#!/usr/bin/env python3
"""
Classroom Management System - Clean Version
Flask Dashboard + FastAPI Unity API - Essential features only
"""

# Core imports
from flask import Flask, render_template, request, redirect, url_for, session, flash
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import os, json, random, string, threading
from datetime import datetime

# =============================================================================
# DATABASE SETUP
# =============================================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///school.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =============================================================================
# DATABASE MODELS
# =============================================================================

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    classes = relationship("Class", back_populates="teacher")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    grade_level = Column(String(20), nullable=False)
    total_points = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    class_code = Column(String(10), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    is_archived = Column(Boolean, default=False)
    teacher = relationship("Teacher", back_populates="classes")
    assignments = relationship("Assignment", back_populates="class_")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    class_ = relationship("Class", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    points = Column(Integer, default=1)
    help_video_url = Column(String(500))
    assignment = relationship("Assignment", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question")
    correct_answers = relationship("CorrectAnswer", back_populates="question")

class QuestionOption(Base):
    __tablename__ = "question_options"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="options")

class CorrectAnswer(Base):
    __tablename__ = "correct_answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="correct_answers")

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    score = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

# =============================================================================
# FASTAPI UNITY ENDPOINTS
# =============================================================================

api = FastAPI(title="Classroom Management API", version="1.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@api.get("/", summary="API Health Check")
async def health_check():
    return {"status": "OK", "message": "Classroom Management API is running"}

@api.get("/classes", summary="Get All Classes")
async def get_classes():
    db = SessionLocal()
    try:
        classes = db.query(Class).filter_by(is_archived=False).all()
        return {
            "classes": [
                {
                    "id": cls.id,
                    "name": cls.name,
                    "description": cls.description,
                    "class_code": cls.class_code
                }
                for cls in classes
            ]
        }
    finally:
        db.close()

@api.get("/class/{class_code}/assignments", summary="Get Assignments by Class Code")
async def get_class_assignments(class_code: str):
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Class not found")
        
        assignments = db.query(Assignment).filter_by(class_id=class_.id, is_archived=False).all()
        return {
            "assignments": [
                {
                    "id": assignment.id,
                    "title": assignment.title,
                    "description": assignment.description,
                    "created_at": assignment.created_at.isoformat() if assignment.created_at else None
                }
                for assignment in assignments
            ]
        }
    finally:
        db.close()

@api.get("/assignment/{assignment_id}", summary="Get Assignment Questions")
async def get_assignment(assignment_id: int):
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment or assignment.is_archived:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        questions = []
        for question in assignment.questions:
            q_data = {
                "id": question.id,
                "text": question.question_text,
                "type": question.question_type,
                "points": question.points,
                "help_video_url": question.help_video_url
            }
            
            if question.question_type == "multiple_choice":
                q_data["options"] = [opt.option_text for opt in question.options]
            
            questions.append(q_data)
        
        return {
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "questions": questions
        }
    finally:
        db.close()

@api.post("/student/register", summary="Register Student for Mobile Game")
async def register_student(data: dict):
    db = SessionLocal()
    try:
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        name = data.get("name", "").strip()
        grade_level = data.get("grade_level", "").strip()
        class_code = data.get("class_code", "").strip().upper()
        
        if not all([email, password, name, grade_level, class_code]):
            raise HTTPException(status_code=400, detail="All fields are required")
        
        # Check if student exists
        if db.query(Student).filter_by(email=email).first():
            raise HTTPException(status_code=400, detail="Student already registered")
        
        # Verify class exists
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=400, detail="Invalid class code")
        
        # Create student
        student = Student(email=email, name=name, grade_level=grade_level)
        student.set_password(password)
        db.add(student)
        db.flush()
        
        # Enroll in class
        enrollment = Enrollment(student_id=student.id, class_id=class_.id)
        db.add(enrollment)
        db.commit()
        
        return {"success": True, "message": "Student registered successfully", "student_id": student.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        db.close()

@api.post("/student/login", summary="Student Login")
async def login_student(data: dict):
    db = SessionLocal()
    try:
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        student = db.query(Student).filter_by(email=email).first()
        if not student or not student.check_password(password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last active
        student.last_active = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "grade_level": student.grade_level,
                "total_points": student.total_points
            }
        }
    finally:
        db.close()

@api.post("/student/join-class", summary="Join Class with Code")
async def join_class(data: dict):
    db = SessionLocal()
    try:
        student_id = data.get("student_id")
        class_code = data.get("class_code", "").strip().upper()
        
        if not student_id or not class_code:
            raise HTTPException(status_code=400, detail="Student ID and class code required")
        
        # Verify student exists
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Verify class exists
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Invalid class code")
        
        # Check if already enrolled
        existing = db.query(Enrollment).filter_by(student_id=student_id, class_id=class_.id).first()
        if existing:
            return {"success": True, "message": "Already enrolled in this class"}
        
        # Create enrollment
        enrollment = Enrollment(student_id=student_id, class_id=class_.id)
        db.add(enrollment)
        db.commit()
        
        return {"success": True, "message": "Successfully joined class"}
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to join class")
    finally:
        db.close()

@api.post("/submit/{assignment_id}", summary="Submit Assignment Answers")
async def submit_assignment(assignment_id: int, data: dict):
    db = SessionLocal()
    try:
        student_id = data.get("student_id")
        answers = data.get("answers", [])
        
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID required")
        
        assignment = db.query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        # Calculate score
        score = 0
        total_points = 0
        
        for answer_data in answers:
            question_id = answer_data.get("question_id")
            student_answer = answer_data.get("answer", "").strip()
            
            question = db.query(Question).filter_by(id=question_id).first()
            if not question:
                continue
            
            total_points += question.points
            
            # Check if answer is correct
            correct_answers = [ca.answer_text.strip().lower() for ca in question.correct_answers]
            is_correct = student_answer.lower() in correct_answers
            
            if is_correct:
                score += question.points
            
            # Store individual answer
            student_ans = StudentAnswer(
                student_id=student_id,
                question_id=question_id,
                answer_text=student_answer,
                is_correct=is_correct
            )
            db.add(student_ans)
        
        # Store submission
        submission = AssignmentSubmission(
            student_id=student_id,
            assignment_id=assignment_id,
            score=score,
            total_points=total_points
        )
        db.add(submission)
        
        # Update student total points
        student = db.query(Student).filter_by(id=student_id).first()
        if student:
            student.total_points = (student.total_points or 0) + score
            student.last_active = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "score": score,
            "total_points": total_points,
            "percentage": round((score / total_points * 100) if total_points > 0 else 0, 2)
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Submission failed")
    finally:
        db.close()

@api.get("/leaderboard/{class_code}", summary="Get Class Leaderboard")
async def get_leaderboard(class_code: str):
    db = SessionLocal()
    try:
        class_ = db.query(Class).filter_by(class_code=class_code).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Get enrolled students with their total points
        enrollments = db.query(Enrollment).filter_by(class_id=class_.id).all()
        leaderboard = []
        
        for enrollment in enrollments:
            student = db.query(Student).filter_by(id=enrollment.student_id).first()
            if student:
                leaderboard.append({
                    "name": student.name,
                    "total_points": student.total_points or 0,
                    "grade_level": student.grade_level
                })
        
        # Sort by points (highest first)
        leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
        
        return {"leaderboard": leaderboard}
    finally:
        db.close()

@api.get("/student/{student_id}/profile", summary="Get Student Profile")
async def get_student_profile(student_id: int):
    db = SessionLocal()
    try:
        student = db.query(Student).filter_by(id=student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "grade_level": student.grade_level,
            "total_points": student.total_points or 0,
            "last_active": student.last_active.isoformat() if student.last_active else None
        }
    finally:
        db.close()

# =============================================================================
# FLASK TEACHER DASHBOARD
# =============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

@app.route("/")
def index():
    if not session.get("teacher_id"):
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
        teacher = db.query(Teacher).filter_by(id=session["teacher_id"]).first()
        classes = db.query(Class).filter_by(teacher_id=session["teacher_id"], is_archived=False).all()
        return render_template("dashboard.html", teacher=teacher, classes=classes)
    finally:
        db.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        db = SessionLocal()
        try:
            teacher = db.query(Teacher).filter_by(email=email).first()
            if teacher and teacher.check_password(password):
                session["teacher_id"] = teacher.id
                return redirect(url_for("index"))
            flash("Invalid email or password", "danger")
        finally:
            db.close()
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create_class", methods=["GET", "POST"])
def create_class():
    if not session.get("teacher_id"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        
        if not name:
            flash("Class name is required", "danger")
            return render_template("create_class.html")
        
        # Generate unique class code
        class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        db = SessionLocal()
        try:
            new_class = Class(
                name=name,
                description=description,
                class_code=class_code,
                teacher_id=session["teacher_id"]
            )
            db.add(new_class)
            db.commit()
            flash("Class created successfully!", "success")
            return redirect(url_for("index"))
        except Exception:
            db.rollback()
            flash("Error creating class", "danger")
        finally:
            db.close()
    
    return render_template("create_class.html")

@app.route("/create_assignment/<int:class_id>", methods=["GET", "POST"])
def create_assignment(class_id):
    if not session.get("teacher_id"):
        return redirect(url_for("login"))
    
    db = SessionLocal()
    try:
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
            except json.JSONDecodeError:
                flash("Invalid questions data", "danger")
                return render_template("create_assignment.html", class_=class_)
            
            assignment = Assignment(class_id=class_id, title=title, description=description)
            db.add(assignment)
            db.flush()
            
            for q in questions_data:
                q_text = q.get("text", "").strip()
                q_type = q.get("type")
                points = int(q.get("points", 1))
                help_video_url = q.get("help_video_url", "").strip()
                
                if not q_text or q_type not in ["multiple_choice", "identification", "enumeration", "problem_solving", "essay"]:
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
                
                # Handle question types
                if q_type == "multiple_choice":
                    options = q.get("options", [])
                    correct_answers = q.get("correct_answers", [])
                    for opt in options:
                        if opt.strip():
                            db.add(QuestionOption(question_id=question.id, option_text=opt.strip()))
                    for ans in correct_answers:
                        if ans.strip():
                            db.add(CorrectAnswer(question_id=question.id, answer_text=ans.strip()))
                
                elif q_type in ["identification", "problem_solving"]:
                    correct = q.get("correct_answer") or (q.get("correct_answers", []) and q.get("correct_answers")[0])
                    if correct and correct.strip():
                        db.add(CorrectAnswer(question_id=question.id, answer_text=correct.strip()))
                
                elif q_type == "enumeration":
                    correct_answers = q.get("correct_answers", [])
                    for ans in correct_answers:
                        if ans.strip():
                            db.add(CorrectAnswer(question_id=question.id, answer_text=ans.strip()))
            
            db.commit()
            flash("Assignment created successfully!", "success")
            return redirect(url_for("index"))
        
        return render_template("create_assignment.html", class_=class_)
    
    except Exception:
        db.rollback()
        flash("Error creating assignment", "danger")
        return redirect(url_for("index"))
    finally:
        db.close()

# Basic Admin Routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        db = SessionLocal()
        try:
            admin = db.query(Admin).filter_by(email=email).first()
            if admin and admin.check_password(password):
                session["admin_id"] = admin.id
                return redirect(url_for("admin_dashboard"))
            flash("Invalid admin credentials", "danger")
        finally:
            db.close()
    
    return render_template("admin_login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_id"):
        return redirect(url_for("admin_login"))
    
    db = SessionLocal()
    try:
        stats = {
            'teachers': db.query(Teacher).count(),
            'students': db.query(Student).count(),
            'classes': db.query(Class).count(),
            'assignments': db.query(Assignment).count()
        }
        return render_template("admin_dashboard.html", stats=stats)
    finally:
        db.close()

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))

# =============================================================================
# INITIALIZATION & DEPLOYMENT
# =============================================================================

def init_db():
    """Initialize database tables and seed default admin"""
    Base.metadata.create_all(bind=engine)
    
    # Seed default admin
    db = SessionLocal()
    try:
        if db.query(Admin).count() == 0:
            admin = Admin(email="admin@capstone.local")
            admin.set_password("Admin@12345")
            db.add(admin)
            db.commit()
            print("Default admin seeded: admin@capstone.local / Admin@12345")
    except Exception as e:
        print(f"Admin seeding error: {e}")
        db.rollback()
    finally:
        db.close()

def create_combined_app():
    """Create combined FastAPI + Flask app for production"""
    init_db()
    main_app = api
    main_app.mount("/dashboard", WSGIMiddleware(app))
    return main_app

# Development mode
if __name__ == "__main__":
    init_db()
    
    import uvicorn
    
    def run_flask():
        print("🌐 Flask Dashboard: http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    
    def run_fastapi():
        print("🎮 Unity API: http://localhost:8001")
        uvicorn.run(api, host="0.0.0.0", port=8001)
    
    print("🎓 CLASSROOM MANAGEMENT SYSTEM")
    print("📋 Teachers: http://localhost:5000")
    print("🎮 Unity: http://localhost:8001")
    
    flask_thread = threading.Thread(target=run_flask)
    fastapi_thread = threading.Thread(target=run_fastapi)
    
    flask_thread.start()
    fastapi_thread.start()
    
    flask_thread.join()
    fastapi_thread.join()

# Production (Render)
combined_app = create_combined_app()