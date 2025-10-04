extends Node
# APIManager.gd - Handles all HTTP requests to the backend API

# API Configuration
var base_url: String = "https://capstoneproject-jq2h.onrender.com"
var api_timeout: float = 30.0

# Request tracking
var active_requests: Array = []

# Signals for API responses
signal login_completed(success: bool, data: Dictionary)
signal register_completed(success: bool, data: Dictionary)
signal profile_loaded(success: bool, data: Dictionary)
signal subjects_loaded(success: bool, data: Dictionary)
signal assignments_loaded(success: bool, data: Dictionary)
signal assignment_submitted(success: bool, data: Dictionary)
signal leaderboard_loaded(success: bool, data: Dictionary)
signal avatar_updated(success: bool, data: Dictionary)
signal join_class_completed(success: bool, data: Dictionary)
signal api_error(error_message: String)

# Error messages
enum ErrorType {
	NETWORK_ERROR,
	TIMEOUT_ERROR,
	PARSE_ERROR,
	SERVER_ERROR,
	MAINTENANCE_MODE
}

func _ready():
	print("[APIManager] Initialized with base URL: ", base_url)

# Student Login
func login_student(email: String, password: String, device_id: String = "") -> void:
	var endpoint = "/api/student/login"
	var data = {
		"email": email,
		"password": password,
		"device_id": device_id if device_id else OS.get_unique_id()
	}
	
	_make_post_request(endpoint, data, func(success, response):
		login_completed.emit(success, response)
	)

# Student Registration
func register_student(name: String, email: String, password: String, grade_level: String = "Grade 1", avatar_url: String = "") -> void:
	var endpoint = "/api/student/register"
	var data = {
		"name": name,
		"email": email,
		"password": password,
		"device_id": OS.get_unique_id(),
		"grade_level": grade_level,
		"avatar_url": avatar_url
	}
	
	_make_post_request(endpoint, data, func(success, response):
		register_completed.emit(success, response)
	)

# Join Class with Code
func join_class(student_id: int, class_code: String) -> void:
	var endpoint = "/api/student/join-class"
	var data = {
		"student_id": student_id,
		"class_code": class_code
	}
	
	_make_post_request(endpoint, data, func(success, response):
		join_class_completed.emit(success, response)
	)

# Get Student Profile
func get_student_profile(student_id: int) -> void:
	var endpoint = "/api/student/%d/profile" % student_id
	
	_make_get_request(endpoint, func(success, response):
		profile_loaded.emit(success, response)
	)

# Get Student Subjects
func get_student_subjects(student_id: int) -> void:
	var endpoint = "/api/student/subjects"
	var data = {
		"student_id": student_id
	}
	
	_make_post_request(endpoint, data, func(success, response):
		subjects_loaded.emit(success, response)
	)

# Get Assignments by Subject
func get_student_assignments(student_id: int, subject: String) -> void:
	var endpoint = "/api/student/assignments"
	var data = {
		"student_id": student_id,
		"subject": subject
	}
	
	_make_post_request(endpoint, data, func(success, response):
		assignments_loaded.emit(success, response)
	)

# Submit Assignment
func submit_assignment(assignment_id: int, student_id: int, answers: Dictionary) -> void:
	var endpoint = "/api/submit/%d" % assignment_id
	var data = {
		"student_id": student_id,
		"answers": answers
	}
	
	_make_post_request(endpoint, data, func(success, response):
		assignment_submitted.emit(success, response)
	)

# Get Leaderboard
func get_leaderboard(class_code: String, top_n: int = 10) -> void:
	var endpoint = "/api/leaderboard/%s?top_n=%d" % [class_code, top_n]
	
	_make_get_request(endpoint, func(success, response):
		leaderboard_loaded.emit(success, response)
	)

# Update Avatar
func update_avatar(student_id: int, avatar_url: String) -> void:
	var endpoint = "/api/student/%d/avatar" % student_id
	var data = {
		"avatar_url": avatar_url
	}
	
	_make_put_request(endpoint, data, func(success, response):
		avatar_updated.emit(success, response)
	)

# Internal HTTP Methods

func _make_get_request(endpoint: String, callback: Callable) -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	active_requests.append(http_request)
	
	var url = base_url + endpoint
	print("[APIManager] GET: ", url)
	
	http_request.timeout = api_timeout
	http_request.request_completed.connect(func(result, response_code, headers, body):
		_on_request_completed(http_request, result, response_code, headers, body, callback)
	)
	
	var error = http_request.request(url, [], HTTPClient.METHOD_GET)
	if error != OK:
		_handle_request_error(http_request, "Failed to make GET request", callback)

func _make_post_request(endpoint: String, data: Dictionary, callback: Callable) -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	active_requests.append(http_request)
	
	var url = base_url + endpoint
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json", "Accept: application/json"]
	
	print("[APIManager] POST: ", url)
	print("[APIManager] Data: ", json_data)
	
	http_request.timeout = api_timeout
	http_request.request_completed.connect(func(result, response_code, headers_response, body):
		_on_request_completed(http_request, result, response_code, headers_response, body, callback)
	)
	
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, json_data)
	if error != OK:
		_handle_request_error(http_request, "Failed to make POST request", callback)

func _make_put_request(endpoint: String, data: Dictionary, callback: Callable) -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	active_requests.append(http_request)
	
	var url = base_url + endpoint
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	
	print("[APIManager] PUT: ", url)
	
	http_request.timeout = api_timeout
	http_request.request_completed.connect(func(result, response_code, headers_response, body):
		_on_request_completed(http_request, result, response_code, headers_response, body, callback)
	)
	
	var error = http_request.request(url, headers, HTTPClient.METHOD_PUT, json_data)
	if error != OK:
		_handle_request_error(http_request, "Failed to make PUT request", callback)

func _on_request_completed(http_request: HTTPRequest, result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray, callback: Callable) -> void:
	_cleanup_request(http_request)
	
	print("[APIManager] Response Code: ", response_code)
	
	# Handle network errors
	if result != HTTPRequest.RESULT_SUCCESS:
		var error_msg = _get_error_message(result)
		print("[APIManager] Request failed: ", error_msg)
		api_error.emit(error_msg)
		callback.call(false, {"error": error_msg})
		return
	
	# Handle HTTP errors
	if response_code >= 400:
		var error_msg = "Server error: %d" % response_code
		if response_code == 503:
			error_msg = "Service unavailable (maintenance mode or disabled)"
		elif response_code == 404:
			error_msg = "Resource not found"
		elif response_code == 401:
			error_msg = "Unauthorized - Invalid credentials"
		
		print("[APIManager] HTTP Error: ", error_msg)
		
		# Try to parse error details from body
		var body_text = body.get_string_from_utf8()
		if body_text:
			var json = JSON.new()
			var parse_result = json.parse(body_text)
			if parse_result == OK:
				var data = json.data
				if data is Dictionary and data.has("detail"):
					error_msg = data["detail"]
		
		api_error.emit(error_msg)
		callback.call(false, {"error": error_msg, "code": response_code})
		return
	
	# Parse successful response
	var body_text = body.get_string_from_utf8()
	print("[APIManager] Response: ", body_text.substr(0, min(500, body_text.length())))
	
	var json = JSON.new()
	var parse_result = json.parse(body_text)
	
	if parse_result != OK:
		print("[APIManager] JSON parse error: ", json.get_error_message())
		api_error.emit("Failed to parse server response")
		callback.call(false, {"error": "Failed to parse response"})
		return
	
	var data = json.data
	if data is Dictionary:
		callback.call(true, data)
	else:
		callback.call(false, {"error": "Invalid response format"})

func _handle_request_error(http_request: HTTPRequest, error_msg: String, callback: Callable) -> void:
	_cleanup_request(http_request)
	print("[APIManager] Request Error: ", error_msg)
	api_error.emit(error_msg)
	callback.call(false, {"error": error_msg})

func _cleanup_request(http_request: HTTPRequest) -> void:
	active_requests.erase(http_request)
	http_request.queue_free()

func _get_error_message(result: int) -> String:
	match result:
		HTTPRequest.RESULT_CANT_CONNECT:
			return "Cannot connect to server. Check your internet connection."
		HTTPRequest.RESULT_CANT_RESOLVE:
			return "Cannot resolve server address. Check your internet connection."
		HTTPRequest.RESULT_CONNECTION_ERROR:
			return "Connection error. Please try again."
		HTTPRequest.RESULT_SSL_HANDSHAKE_ERROR:
			return "SSL handshake error. Check server certificate."
		HTTPRequest.RESULT_NO_RESPONSE:
			return "No response from server. Please try again."
		HTTPRequest.RESULT_TIMEOUT:
			return "Request timeout. Server is taking too long to respond."
		_:
			return "Unknown network error (%d)" % result

# Cancel all active requests
func cancel_all_requests() -> void:
	for request in active_requests:
		request.cancel_request()
		request.queue_free()
	active_requests.clear()
