"""
WSGI entry point for Render deployment
"""
import os
from app import app, api, SessionLocal, Teacher

# Set production environment
os.environ['RENDER'] = 'true'

# Create a simple health check route
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Classroom Management System is running'}

# Add key API endpoints to Flask app for production
@app.route('/api/classes')
def api_classes():
    """Get all classes - Flask wrapper for FastAPI endpoint"""
    from app import get_all_classes
    try:
        return get_all_classes()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/api/assignment/<int:assignment_id>')
def api_assignment(assignment_id):
    """Get assignment questions - Flask wrapper for FastAPI endpoint"""
    from app import get_assignment_for_game
    try:
        return get_assignment_for_game(assignment_id)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/api/submit/<int:assignment_id>', methods=['POST'])
def api_submit(assignment_id):
    """Submit assignment - Flask wrapper for FastAPI endpoint"""
    from app import submit_assignment_from_game
    from flask import request
    try:
        return submit_assignment_from_game(assignment_id, request.get_json())
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/api/student/register', methods=['POST'])
def api_student_register():
    """Student registration - Flask wrapper for FastAPI endpoint"""
    from app import register_student_for_game
    from flask import request
    try:
        return register_student_for_game(request.get_json())
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/api/student/login', methods=['POST'])
def api_student_login():
    """Student login - Flask wrapper for FastAPI endpoint"""
    from app import login_student
    from flask import request
    try:
        return login_student(request.get_json())
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/docs')
def api_docs():
    """API Documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Classroom Management API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #007cba; }
        </style>
    </head>
    <body>
        <h1>🎓 Classroom Management API</h1>
        <h2>Available Endpoints for Unity Games:</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/classes<br>
            <small>Get all available classes for students to join</small>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/assignment/{assignment_id}<br>
            <small>Get assignment questions formatted for Unity game</small>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/submit/{assignment_id}<br>
            <small>Submit assignment answers from Unity game</small>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/student/register<br>
            <small>Register new student from mobile game</small>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /api/student/login<br>
            <small>Student login with credentials</small>
        </div>
        
        <h2>Web Dashboard:</h2>
        <p><a href="/">📋 Teacher Dashboard</a> - Full web interface for teachers</p>
        
        <h2>System Health:</h2>
        <p><a href="/health">🏥 Health Check</a> - System status</p>
    </body>
    </html>
    """

# For debugging in production
@app.route('/debug/info')
def debug_info():
    """Debug information for production troubleshooting"""
    db = SessionLocal()
    try:
        teacher_count = db.query(Teacher).count()
        return {
            'status': 'ok',
            'environment': 'production' if os.environ.get('RENDER') else 'development',
            'port': os.environ.get('PORT', 'not set'),
            'database': 'connected',
            'teachers_count': teacher_count,
            'render_env': bool(os.environ.get('RENDER'))
        }
    except Exception as e:
        return {'status': 'error', 'database': 'failed', 'error': str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Production mode - Running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
