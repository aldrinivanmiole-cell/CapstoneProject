extends Node
# DataManager.gd - Handles local data storage and offline capabilities

const SAVE_FILE_PATH = "user://save_data.dat"
const SESSION_FILE_PATH = "user://session.dat"
const CACHE_FILE_PATH = "user://cache.dat"

# Cache for offline data
var cached_subjects: Array = []
var cached_assignments: Dictionary = {}
var cached_leaderboards: Dictionary = {}
var temp_data: Dictionary = {}

func _ready():
	print("[DataManager] Initialized")
	print("[DataManager] Save path: ", OS.get_user_data_dir())
	_ensure_save_directory()

# Session Management

func save_session(session_data: Dictionary) -> bool:
	return _save_to_file(SESSION_FILE_PATH, session_data)

func load_session() -> Dictionary:
	return _load_from_file(SESSION_FILE_PATH)

func clear_session() -> void:
	_delete_file(SESSION_FILE_PATH)
	print("[DataManager] Session cleared")

# Settings Management

func save_setting(key: String, value: Variant) -> bool:
	var settings = _load_from_file(SAVE_FILE_PATH)
	settings[key] = value
	return _save_to_file(SAVE_FILE_PATH, settings)

func load_setting(key: String, default_value: Variant = null) -> Variant:
	var settings = _load_from_file(SAVE_FILE_PATH)
	return settings.get(key, default_value)

func get_all_settings() -> Dictionary:
	return _load_from_file(SAVE_FILE_PATH)

func clear_settings() -> void:
	_delete_file(SAVE_FILE_PATH)
	print("[DataManager] Settings cleared")

# Cache Management (for offline mode)

func cache_subjects(subjects: Array) -> void:
	cached_subjects = subjects.duplicate(true)
	var cache = _load_from_file(CACHE_FILE_PATH)
	cache["subjects"] = subjects
	_save_to_file(CACHE_FILE_PATH, cache)
	print("[DataManager] Cached %d subjects" % subjects.size())

func get_cached_subjects() -> Array:
	if cached_subjects.is_empty():
		var cache = _load_from_file(CACHE_FILE_PATH)
		cached_subjects = cache.get("subjects", [])
	return cached_subjects

func cache_assignments(subject: String, assignments: Array) -> void:
	cached_assignments[subject] = assignments.duplicate(true)
	var cache = _load_from_file(CACHE_FILE_PATH)
	if not cache.has("assignments"):
		cache["assignments"] = {}
	cache["assignments"][subject] = assignments
	_save_to_file(CACHE_FILE_PATH, cache)
	print("[DataManager] Cached %d assignments for %s" % [assignments.size(), subject])

func get_cached_assignments(subject: String) -> Array:
	if cached_assignments.has(subject):
		return cached_assignments[subject]
	
	var cache = _load_from_file(CACHE_FILE_PATH)
	if cache.has("assignments") and cache["assignments"].has(subject):
		var assignments = cache["assignments"][subject]
		cached_assignments[subject] = assignments
		return assignments
	
	return []

func cache_leaderboard(class_code: String, leaderboard: Array) -> void:
	cached_leaderboards[class_code] = leaderboard.duplicate(true)
	var cache = _load_from_file(CACHE_FILE_PATH)
	if not cache.has("leaderboards"):
		cache["leaderboards"] = {}
	cache["leaderboards"][class_code] = leaderboard
	_save_to_file(CACHE_FILE_PATH, cache)
	print("[DataManager] Cached leaderboard for %s" % class_code)

func get_cached_leaderboard(class_code: String) -> Array:
	if cached_leaderboards.has(class_code):
		return cached_leaderboards[class_code]
	
	var cache = _load_from_file(CACHE_FILE_PATH)
	if cache.has("leaderboards") and cache["leaderboards"].has(class_code):
		var leaderboard = cache["leaderboards"][class_code]
		cached_leaderboards[class_code] = leaderboard
		return leaderboard
	
	return []

func clear_cache() -> void:
	cached_subjects.clear()
	cached_assignments.clear()
	cached_leaderboards.clear()
	_delete_file(CACHE_FILE_PATH)
	print("[DataManager] Cache cleared")

# Temporary Data (for scene transitions)

func save_temp_data(key: String, value: Variant) -> void:
	temp_data[key] = value

func load_temp_data(key: String, default_value: Variant = null) -> Variant:
	return temp_data.get(key, default_value)

func clear_temp_data(key: String) -> void:
	temp_data.erase(key)

func clear_all_temp_data() -> void:
	temp_data.clear()

# Offline Queue Management (for submissions when offline)

func queue_submission(assignment_id: int, student_id: int, answers: Dictionary) -> void:
	var queue = load_setting("submission_queue", [])
	queue.append({
		"assignment_id": assignment_id,
		"student_id": student_id,
		"answers": answers,
		"timestamp": Time.get_unix_time_from_system()
	})
	save_setting("submission_queue", queue)
	print("[DataManager] Submission queued (offline)")

func get_submission_queue() -> Array:
	return load_setting("submission_queue", [])

func clear_submission(index: int) -> void:
	var queue = get_submission_queue()
	if index >= 0 and index < queue.size():
		queue.remove_at(index)
		save_setting("submission_queue", queue)

func clear_submission_queue() -> void:
	save_setting("submission_queue", [])
	print("[DataManager] Submission queue cleared")

# Internal File Operations

func _save_to_file(file_path: String, data: Dictionary) -> bool:
	var file = FileAccess.open(file_path, FileAccess.WRITE)
	if file == null:
		push_error("[DataManager] Failed to open file for writing: " + file_path)
		return false
	
	var json_string = JSON.stringify(data)
	file.store_string(json_string)
	file.close()
	return true

func _load_from_file(file_path: String) -> Dictionary:
	if not FileAccess.file_exists(file_path):
		return {}
	
	var file = FileAccess.open(file_path, FileAccess.READ)
	if file == null:
		push_error("[DataManager] Failed to open file for reading: " + file_path)
		return {}
	
	var json_string = file.get_as_text()
	file.close()
	
	if json_string.is_empty():
		return {}
	
	var json = JSON.new()
	var parse_result = json.parse(json_string)
	if parse_result != OK:
		push_error("[DataManager] Failed to parse JSON from file: " + file_path)
		return {}
	
	if json.data is Dictionary:
		return json.data
	
	return {}

func _delete_file(file_path: String) -> void:
	if FileAccess.file_exists(file_path):
		DirAccess.remove_absolute(file_path)

func _ensure_save_directory() -> void:
	var dir = DirAccess.open("user://")
	if dir == null:
		push_error("[DataManager] Failed to access user data directory")

# Utility Functions

func get_storage_size() -> int:
	var total_size = 0
	
	if FileAccess.file_exists(SAVE_FILE_PATH):
		var file = FileAccess.open(SAVE_FILE_PATH, FileAccess.READ)
		if file:
			total_size += file.get_length()
			file.close()
	
	if FileAccess.file_exists(SESSION_FILE_PATH):
		var file = FileAccess.open(SESSION_FILE_PATH, FileAccess.READ)
		if file:
			total_size += file.get_length()
			file.close()
	
	if FileAccess.file_exists(CACHE_FILE_PATH):
		var file = FileAccess.open(CACHE_FILE_PATH, FileAccess.READ)
		if file:
			total_size += file.get_length()
			file.close()
	
	return total_size

func clear_all_data() -> void:
	clear_session()
	clear_settings()
	clear_cache()
	clear_all_temp_data()
	print("[DataManager] All data cleared")
