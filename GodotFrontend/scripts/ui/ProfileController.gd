extends Control
# ProfileController.gd - Displays and manages student profile

@onready var name_label = $Panel/VBox/ProfileSection/NameLabel
@onready var email_label = $Panel/VBox/ProfileSection/EmailLabel
@onready var grade_label = $Panel/VBox/ProfileSection/GradeLabel
@onready var points_label = $Panel/VBox/ProfileSection/PointsLabel
@onready var classes_list = $Panel/VBox/ClassesSection/ScrollContainer/ClassesList
@onready var join_class_button = $Panel/VBox/JoinClassButton
@onready var refresh_button = $Panel/VBox/RefreshButton
@onready var back_button = $Panel/VBox/BackButton
@onready var loading_label = $Panel/VBox/LoadingLabel

var is_loading = false

func _ready():
	print("[ProfileController] Ready")
	
	# Connect signals
	join_class_button.pressed.connect(_on_join_class_pressed)
	refresh_button.pressed.connect(_on_refresh_pressed)
	back_button.pressed.connect(_on_back_pressed)
	APIManager.profile_loaded.connect(_on_profile_loaded)
	APIManager.join_class_completed.connect(_on_join_class_completed)
	GameManager.student_data_updated.connect(_update_ui)
	
	# Display current data
	_update_ui()

func _update_ui():
	# Update profile info
	if name_label:
		name_label.text = "Name: %s" % GameManager.student_name
	
	if email_label:
		email_label.text = "Email: %s" % GameManager.student_email
	
	if grade_label:
		grade_label.text = "Grade: %s" % GameManager.student_grade
	
	if points_label:
		points_label.text = "Total Points: %d" % GameManager.student_points
	
	# Update classes list
	_update_classes_list()

func _update_classes_list():
	if not classes_list:
		return
	
	# Clear list
	for child in classes_list.get_children():
		child.queue_free()
	
	var classes = GameManager.enrolled_classes
	if classes.is_empty():
		var label = Label.new()
		label.text = "No classes enrolled yet"
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		classes_list.add_child(label)
		return
	
	# Display classes
	for class_data in classes:
		var panel = PanelContainer.new()
		panel.custom_minimum_size = Vector2(0, 80)
		
		var vbox = VBoxContainer.new()
		panel.add_child(vbox)
		
		# Class name
		var name_lbl = Label.new()
		name_lbl.text = class_data.get("name", "Unknown Class")
		vbox.add_child(name_lbl)
		
		# Class details
		var details_lbl = Label.new()
		details_lbl.text = "Section: %s | Code: %s" % [
			class_data.get("section", "N/A"),
			class_data.get("class_code", "N/A")
		]
		vbox.add_child(details_lbl)
		
		# Teacher
		var teacher_lbl = Label.new()
		teacher_lbl.text = "Teacher: %s" % class_data.get("teacher_name", "Unknown")
		vbox.add_child(teacher_lbl)
		
		classes_list.add_child(panel)

func _on_refresh_pressed():
	if is_loading:
		return
	
	is_loading = true
	loading_label.visible = true
	refresh_button.disabled = true
	
	APIManager.get_student_profile(GameManager.student_id)

func _on_profile_loaded(success: bool, data: Dictionary):
	is_loading = false
	loading_label.visible = false
	refresh_button.disabled = false
	
	if success:
		GameManager.update_profile(data)
	else:
		_show_message("Failed to refresh profile", true)

func _on_join_class_pressed():
	# Show join class dialog
	var dialog = AcceptDialog.new()
	dialog.title = "Join Class"
	dialog.dialog_text = "Enter Class Code:"
	
	var input = LineEdit.new()
	input.placeholder_text = "MATH101A"
	dialog.add_child(input)
	
	dialog.confirmed.connect(func():
		var class_code = input.text.strip_edges()
		if not class_code.is_empty():
			_join_class(class_code)
	)
	
	add_child(dialog)
	dialog.popup_centered()

func _join_class(class_code: String):
	APIManager.join_class(GameManager.student_id, class_code)

func _on_join_class_completed(success: bool, data: Dictionary):
	if success:
		_show_message("Successfully joined class!", false)
		# Refresh profile to get updated classes
		await get_tree().create_timer(1.0).timeout
		_on_refresh_pressed()
	else:
		var error = data.get("error", "Failed to join class")
		_show_message(error, true)

func _show_message(text: String, is_error: bool):
	var label = loading_label if loading_label else null
	if label:
		label.text = text
		label.modulate = Color.RED if is_error else Color.WHITE
		label.visible = true
		await get_tree().create_timer(3.0).timeout
		label.visible = false

func _on_back_pressed():
	GameManager.change_scene("main_menu")
