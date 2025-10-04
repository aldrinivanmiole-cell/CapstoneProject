extends Control
# RegisterController.gd - Controls the registration screen

@onready var name_input = $Panel/VBox/NameInput
@onready var email_input = $Panel/VBox/EmailInput
@onready var password_input = $Panel/VBox/PasswordInput
@onready var confirm_password_input = $Panel/VBox/ConfirmPasswordInput
@onready var grade_option = $Panel/VBox/GradeOption
@onready var register_button = $Panel/VBox/RegisterButton
@onready var back_button = $Panel/VBox/BackButton
@onready var message_label = $Panel/VBox/MessageLabel
@onready var loading_indicator = $Panel/VBox/LoadingIndicator

var is_processing = false

func _ready():
	print("[RegisterController] Ready")
	
	# Connect signals
	register_button.pressed.connect(_on_register_pressed)
	back_button.pressed.connect(_on_back_pressed)
	APIManager.register_completed.connect(_on_register_completed)
	APIManager.api_error.connect(_on_api_error)
	
	# Setup grade options
	_setup_grade_options()
	
	# Hide loading indicator
	if loading_indicator:
		loading_indicator.visible = false
	
	# Clear message
	if message_label:
		message_label.text = ""

func _setup_grade_options():
	if grade_option:
		grade_option.clear()
		for i in range(1, 13):
			grade_option.add_item("Grade %d" % i)
		grade_option.selected = 0

func _on_register_pressed():
	if is_processing:
		return
	
	var name = name_input.text.strip_edges()
	var email = email_input.text.strip_edges()
	var password = password_input.text
	var confirm_password = confirm_password_input.text
	var grade = grade_option.get_item_text(grade_option.selected)
	
	# Validation
	if name.is_empty():
		show_message("Please enter your name", true)
		return
	
	if email.is_empty():
		show_message("Please enter your email", true)
		return
	
	if not _is_valid_email(email):
		show_message("Please enter a valid email address", true)
		return
	
	if password.is_empty():
		show_message("Please enter a password", true)
		return
	
	if password.length() < 6:
		show_message("Password must be at least 6 characters", true)
		return
	
	if password != confirm_password:
		show_message("Passwords do not match", true)
		return
	
	# Start registration
	is_processing = true
	set_ui_enabled(false)
	show_message("Creating account...", false)
	
	if loading_indicator:
		loading_indicator.visible = true
	
	# Call API
	APIManager.register_student(name, email, password, grade)

func _on_back_pressed():
	if is_processing:
		return
	GameManager.change_scene("login")

func _on_register_completed(success: bool, data: Dictionary):
	is_processing = false
	set_ui_enabled(true)
	
	if loading_indicator:
		loading_indicator.visible = false
	
	if success:
		if data.get("status") == "success":
			show_message("Registration successful! Please login.", false)
			
			# Wait a moment then go to login
			await get_tree().create_timer(2.0).timeout
			GameManager.change_scene("login")
		else:
			var error_msg = data.get("message", "Registration failed")
			show_message(error_msg, true)
	else:
		var error_msg = data.get("error", "Registration failed. Please try again.")
		# Check for specific errors
		if "already exists" in error_msg.to_lower() or "duplicate" in error_msg.to_lower():
			show_message("Email already registered. Please login instead.", true)
		else:
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
	if name_input:
		name_input.editable = enabled
	if email_input:
		email_input.editable = enabled
	if password_input:
		password_input.editable = enabled
	if confirm_password_input:
		confirm_password_input.editable = enabled
	if grade_option:
		grade_option.disabled = not enabled
	if register_button:
		register_button.disabled = not enabled
	if back_button:
		back_button.disabled = not enabled

func _is_valid_email(email: String) -> bool:
	var regex = RegEx.new()
	regex.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
	return regex.search(email) != null
