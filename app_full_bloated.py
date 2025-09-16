#!/usr/bin/env python3
"""
Classroom Management System - Streamlined Version
Combines Flask web dashboard + FastAPI Unity endpoints
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.wsgi import WSGIMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from werkzeug.security import generate_password_hash, check_password_hash

# =============================================================================
# DATABASE SETUP
# =============================================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///school.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
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
    class_ = relationship("Class", back_populates="assignments")
    questions = relationship("Question", back_populates="assignment")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, identification, etc.
    points = Column(Integer, default=1)
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

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

# =============================================================================
# FLASK WEB DASHBOARD
# =============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# TEACHER ROUTES
@app.route("/")
def index():
    if not session.get("teacher_id"):
        return redirect(url_for("login"))
    
    db = SessionLocal()
    teacher = db.query(Teacher).filter_by(id=session["teacher_id"]).first()
    classes = db.query(Class).filter_by(teacher_id=session["teacher_id"], is_archived=False).all()
    db.close()
    
    return render_template("dashboard.html", teacher=teacher, classes=classes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        db = SessionLocal()
        teacher = db.query(Teacher).filter_by(email=email).first()
        db.close()
        
        if teacher and teacher.check_password(password):
            session["teacher_id"] = teacher.id
            return redirect(url_for("index"))
        
        flash("Invalid email or password", "danger")
    
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
        import random, string
        class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        db = SessionLocal()
        new_class = Class(
            name=name,
            description=description,
            class_code=class_code,
            teacher_id=session["teacher_id"]
        )
        db.add(new_class)
        db.commit()
        db.close()
        
        flash("Class created successfully!", "success")
        return redirect(url_for("index"))
    
    return render_template("create_class.html")

@app.route("/create_assignment/<int:class_id>", methods=["GET", "POST"])
def create_assignment(class_id):
    if not session.get("teacher_id"):
        return redirect(url_for("login"))
    
    db = SessionLocal()
    class_ = db.query(Class).filter_by(id=class_id, teacher_id=session["teacher_id"]).first()
    if not class_:
        db.close()
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
            
            if not q_text or q_type not in ["multiple_choice", "identification", "enumeration", "problem_solving", "essay"]:
                continue
            
            question = Question(
                assignment_id=assignment.id,
                question_text=q_text,
                question_type=q_type,
                points=points
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
        db.close()
        flash("Assignment created successfully!", "success")
        return redirect(url_for("index"))
    
    db.close()
    return render_template("create_assignment.html", class_=class_)

# ADMIN ROUTES (Basic)
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        db = SessionLocal()
        admin = db.query(Admin).filter_by(email=email).first()
        db.close()
        
        if admin and admin.check_password(password):
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))
        
        flash("Invalid admin credentials", "danger")
    
    return render_template("admin_login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_id"):
        return redirect(url_for("admin_login"))
    
    db = SessionLocal()
    stats = {
        'teachers': db.query(Teacher).count(),
        'students': db.query(Student).count(),
        'classes': db.query(Class).count(),
        'assignments': db.query(Assignment).count()
    }
    db.close()
    
    return render_template("admin_dashboard.html", stats=stats)

# =============================================================================
# FASTAPI UNITY ENDPOINTS
# =============================================================================

api = FastAPI(title="Classroom Management API", version="1.0.0")

def get_api_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api.get("/")
async def api_health():
    return {"status": "ok", "service": "classroom-api"}

@api.post("/auth/student/login")
async def student_login(data: dict, db: Session = Depends(get_api_db)):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    student = db.query(Student).filter_by(email=email).first()
    if not student or not student.check_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
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

@api.get("/student/{student_id}/classes")
async def get_student_classes(student_id: int, db: Session = Depends(get_api_db)):
    enrollments = db.query(Enrollment).filter_by(student_id=student_id).all()
    classes = []
    
    for enrollment in enrollments:
        class_ = db.query(Class).filter_by(id=enrollment.class_id).first()
        if class_ and not class_.is_archived:
            classes.append({
                "id": class_.id,
                "name": class_.name,
                "description": class_.description,
                "class_code": class_.class_code
            })
    
    return {"classes": classes}

@api.get("/class/{class_id}/assignments")
async def get_class_assignments(class_id: int, db: Session = Depends(get_api_db)):
    assignments = db.query(Assignment).filter_by(class_id=class_id).all()
    result = []
    
    for assignment in assignments:
        questions = []
        for question in assignment.questions:
            q_data = {
                "id": question.id,
                "text": question.question_text,
                "type": question.question_type,
                "points": question.points
            }
            
            if question.question_type == "multiple_choice":
                q_data["options"] = [opt.option_text for opt in question.options]
            
            questions.append(q_data)
        
        result.append({
            "id": assignment.id,
            "title": assignment.title,
            "description": assignment.description,
            "questions": questions
        })
    
    return {"assignments": result}

@api.post("/assignment/{assignment_id}/submit")
async def submit_assignment(assignment_id: int, data: dict, db: Session = Depends(get_api_db)):
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
    
    for answer in answers:
        question_id = answer.get("question_id")
        student_answer = answer.get("answer", "").strip()
        
        question = db.query(Question).filter_by(id=question_id).first()
        if not question:
            continue
        
        total_points += question.points
        
        # Check if answer is correct
        correct_answers = [ca.answer_text for ca in question.correct_answers]
        if student_answer in correct_answers:
            score += question.points
    
    # Save submission
    submission = AssignmentSubmission(
        student_id=student_id,
        assignment_id=assignment_id,
        score=score,
        total_points=total_points
    )
    db.add(submission)
    db.commit()
    
    return {
        "success": True,
        "score": score,
        "total_points": total_points,
        "percentage": round((score / total_points * 100) if total_points > 0 else 0, 2)
    }

# =============================================================================
# INITIALIZATION & DEPLOYMENT
# =============================================================================

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Seed default admin
    db = SessionLocal()
    if db.query(Admin).count() == 0:
        admin = Admin(email="admin@capstone.local")
        admin.set_password("Admin@12345")
        db.add(admin)
        db.commit()
    db.close()

def create_combined_app():
    init_db()
    main_app = api
    main_app.mount("/dashboard", WSGIMiddleware(app))
    return main_app

# For development
if __name__ == "__main__":
    init_db()
    
    import uvicorn
    import threading
    
    def run_flask():
        app.run(host="0.0.0.0", port=5000, debug=False)
    
    def run_fastapi():
        uvicorn.run(api, host="0.0.0.0", port=8001)
    
    print("🎓 CLASSROOM MANAGEMENT SYSTEM")
    print("📋 Teachers: http://localhost:5000")
    print("🎮 Unity API: http://localhost:8001")
    
    flask_thread = threading.Thread(target=run_flask)
    fastapi_thread = threading.Thread(target=run_fastapi)
    
    flask_thread.start()
    fastapi_thread.start()
    
    flask_thread.join()
    fastapi_thread.join()

# For production (Render)
combined_app = create_combined_app()