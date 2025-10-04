extends Control
# LoginController.gd - Controls the login screen

@onready var email_input = $WoodenFrame/Panel/VBox/EmailInput
@onready var password_input = $WoodenFrame/Panel/VBox/PasswordInput
@onready var login_button = $WoodenFrame/Panel/VBox/LoginButton
@onready var register_button = $WoodenFrame/Panel/VBox/RegisterButton
@onready var message_label = $WoodenFrame/Panel/VBox/MessageLabel
@onready var loading_indicator = $WoodenFrame/Panel/VBox/LoadingIndicator

var is_processing = false

func _ready():
	print("[LoginController] Ready")
	
	# Connect signals
	login_button.pressed.connect(_on_login_pressed)
	register_button.pressed.connect(_on_register_pressed)
	APIManager.login_completed.connect(_on_login_completed)
	APIManager.api_error.connect(_on_api_error)
	
	# Hide loading indicator
	if loading_indicator:
		loading_indicator.visible = false
	
	# Clear message
	if message_label:
		message_label.text = ""
	
	# Auto-login if session exists and user is logged in
	if GameManager.is_student_logged_in():
		show_message("Welcome back, " + GameManager.student_name + "!", false)
		await get_tree().create_timer(1.0).timeout
		GameManager.change_scene("main_menu")

func _on_login_pressed():
	if is_processing:
		return
	
	var email = email_input.text.strip_edges()
	var password = password_input.text
	
	# Validation
	if email.is_empty() or password.is_empty():
		show_message("Please enter both email and password", true)
		return
	
	if not _is_valid_email(email):
		show_message("Please enter a valid email address", true)
		return
	
	# Start login
	is_processing = true
	set_ui_enabled(false)
	show_message("Logging in...", false)
	
	if loading_indicator:
		loading_indicator.visible = true
	
	# Call API
	APIManager.login_student(email, password)

func _on_register_pressed():
	if is_processing:
		return
	GameManager.change_scene("register")

func _on_login_completed(success: bool, data: Dictionary):
	is_processing = false
	set_ui_enabled(true)
	
	if loading_indicator:
		loading_indicator.visible = false
	
	if success:
		if data.get("status") == "success":
			show_message("Login successful!", false)
			
			# Update GameManager with student data
			GameManager.login(data)
			
			# Wait a moment then transition
			await get_tree().create_timer(1.0).timeout
			GameManager.change_scene("main_menu")
		else:
			var error_msg = data.get("message", "Login failed")
			show_message(error_msg, true)
	else:
		var error_msg = data.get("error", "Login failed. Please try again.")
		show_message(error_msg, true)

func _on_api_error(error_message: String):
	if is_processing:
		is_processing = false
		set_ui_enabled(true)
		
		if loading_indicator:
			loading_indicator.visible = false
		
		show_message("Error: " + error_message, true)

func show_message(text: String, is_error: bool):
	if message_label:
		message_label.text = text
		if is_error:
			message_label.modulate = Color.RED
		else:
			message_label.modulate = Color.WHITE

func set_ui_enabled(enabled: bool):
	if email_input:
		email_input.editable = enabled
	if password_input:
		password_input.editable = enabled
	if login_button:
		login_button.disabled = not enabled
	if register_button:
		register_button.disabled = not enabled

func _is_valid_email(email: String) -> bool:
	var regex = RegEx.new()
	regex.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
	return regex.search(email) != null

# Handle Enter key press
func _input(event):
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_ENTER and not is_processing:
			_on_login_pressed()
