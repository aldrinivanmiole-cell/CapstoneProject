extends Node
# GameManager.gd - Manages game state, student data, and scene transitions

# Student data
var student_id: int = -1
var student_name: String = ""
var student_email: String = ""
var student_grade: String = ""
var student_points: int = 0
var student_avatar: String = ""
var enrolled_classes: Array = []

# Current session data
var current_subject: String = ""
var current_assignment: Dictionary = {}
var current_assignment_id: int = -1
var current_questions: Array = []
var current_answers: Dictionary = {}

# Game state
var is_logged_in: bool = false
var selected_class_code: String = ""

# Scene paths
const SCENES = {
	"main": "res://scenes/Main.tscn",
	"login": "res://scenes/auth/LoginScreen.tscn",
	"register": "res://scenes/auth/RegisterScreen.tscn",
	"main_menu": "res://scenes/menu/MainMenu.tscn",
	"subject_selection": "res://scenes/menu/SubjectSelection.tscn",
	"quiz_game": "res://scenes/game/QuizGame.tscn",
	"result": "res://scenes/game/ResultScreen.tscn",
	"leaderboard": "res://scenes/ui/Leaderboard.tscn",
	"profile": "res://scenes/ui/Profile.tscn"
}

# Signals
signal student_data_updated()
signal scene_transition_started(scene_name: String)
signal scene_transition_completed(scene_name: String)

func _ready():
	print("[GameManager] Initialized")
	# Try to load saved session
	_load_session()

# Session Management

func login(student_data: Dictionary) -> void:
	if student_data.has("student"):
		var data = student_data["student"]
		student_id = data.get("id", -1)
		student_name = data.get("name", "")
		student_email = data.get("email", "")
		student_grade = data.get("grade_level", "Grade 1")
		student_points = data.get("total_points", 0)
		student_avatar = data.get("avatar_url", "")
		
		if student_data.has("classes"):
			enrolled_classes = student_data["classes"]
		
		is_logged_in = true
		_save_session()
		student_data_updated.emit()
		print("[GameManager] Student logged in: ", student_name)

func logout() -> void:
	student_id = -1
	student_name = ""
	student_email = ""
	student_grade = ""
	student_points = 0
	student_avatar = ""
	enrolled_classes.clear()
	is_logged_in = false
	
	current_subject = ""
	current_assignment.clear()
	current_questions.clear()
	current_answers.clear()
	
	DataManager.clear_session()
	print("[GameManager] Student logged out")
	
	change_scene("login")

func update_profile(profile_data: Dictionary) -> void:
	if profile_data.has("student"):
		var data = profile_data["student"]
		student_name = data.get("name", student_name)
		student_email = data.get("email", student_email)
		student_grade = data.get("grade_level", student_grade)
		student_points = data.get("total_points", student_points)
		student_avatar = data.get("avatar_url", student_avatar)
		
		if profile_data.has("classes"):
			enrolled_classes = profile_data["classes"]
		
		_save_session()
		student_data_updated.emit()

func _save_session() -> void:
	var session_data = {
		"student_id": student_id,
		"student_name": student_name,
		"student_email": student_email,
		"student_grade": student_grade,
		"student_points": student_points,
		"student_avatar": student_avatar,
		"enrolled_classes": enrolled_classes
	}
	DataManager.save_session(session_data)

func _load_session() -> void:
	var session_data = DataManager.load_session()
	if session_data.is_empty():
		return
	
	student_id = session_data.get("student_id", -1)
	if student_id > 0:
		student_name = session_data.get("student_name", "")
		student_email = session_data.get("student_email", "")
		student_grade = session_data.get("student_grade", "")
		student_points = session_data.get("student_points", 0)
		student_avatar = session_data.get("student_avatar", "")
		enrolled_classes = session_data.get("enrolled_classes", [])
		is_logged_in = true
		student_data_updated.emit()
		print("[GameManager] Session restored for: ", student_name)

# Assignment Management

func load_assignment(assignment_data: Dictionary) -> void:
	current_assignment = assignment_data
	current_assignment_id = assignment_data.get("id", -1)
	current_questions = assignment_data.get("questions", [])
	current_answers.clear()
	print("[GameManager] Assignment loaded: ", assignment_data.get("title", "Unknown"))

func save_answer(question_id: int, answer: String) -> void:
	current_answers[str(question_id)] = answer
	print("[GameManager] Answer saved for question ", question_id)

func get_current_answers() -> Dictionary:
	return current_answers

func clear_answers() -> void:
	current_answers.clear()

func get_assignment_progress() -> float:
	if current_questions.is_empty():
		return 0.0
	var answered = 0
	for question in current_questions:
		var q_id = str(question.get("id", 0))
		if current_answers.has(q_id) and current_answers[q_id] != "":
			answered += 1
	return float(answered) / float(current_questions.size()) * 100.0

# Subject Management

func set_current_subject(subject: String) -> void:
	current_subject = subject
	print("[GameManager] Current subject set to: ", subject)

func get_current_subject() -> String:
	return current_subject

# Scene Management

func change_scene(scene_key: String, params: Dictionary = {}) -> void:
	if not SCENES.has(scene_key):
		push_error("[GameManager] Scene key not found: " + scene_key)
		return
	
	var scene_path = SCENES[scene_key]
	print("[GameManager] Changing scene to: ", scene_path)
	
	scene_transition_started.emit(scene_key)
	
	# Store any parameters for the next scene
	if not params.is_empty():
		DataManager.save_temp_data("scene_params", params)
	
	# Change scene
	var error = get_tree().change_scene_to_file(scene_path)
	if error != OK:
		push_error("[GameManager] Failed to change scene: " + str(error))
	else:
		scene_transition_completed.emit(scene_key)

func get_scene_params() -> Dictionary:
	var params = DataManager.load_temp_data("scene_params")
	DataManager.clear_temp_data("scene_params")
	return params

func reload_current_scene() -> void:
	get_tree().reload_current_scene()

# Utility Functions

func get_student_info() -> Dictionary:
	return {
		"id": student_id,
		"name": student_name,
		"email": student_email,
		"grade": student_grade,
		"points": student_points,
		"avatar": student_avatar,
		"classes": enrolled_classes
	}

func is_student_logged_in() -> bool:
	return is_logged_in and student_id > 0

func add_points(points: int) -> void:
	student_points += points
	_save_session()
	student_data_updated.emit()

func get_class_by_code(class_code: String) -> Dictionary:
	for class_data in enrolled_classes:
		if class_data.get("class_code", "") == class_code:
			return class_data
	return {}

# Debug
func print_student_info() -> void:
	print("=== Student Info ===")
	print("ID: ", student_id)
	print("Name: ", student_name)
	print("Email: ", student_email)
	print("Grade: ", student_grade)
	print("Points: ", student_points)
	print("Classes: ", enrolled_classes.size())
	print("==================")
