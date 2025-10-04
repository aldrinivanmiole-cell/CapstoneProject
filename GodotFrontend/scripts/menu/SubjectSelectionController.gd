extends Control
# SubjectSelectionController.gd - Displays subjects and assignments

@onready var subject_list = $Panel/VBox/ScrollContainer/SubjectList
@onready var back_button = $Panel/VBox/BackButton
@onready var refresh_button = $Panel/VBox/RefreshButton
@onready var loading_label = $Panel/VBox/LoadingLabel

var is_loading = false

func _ready():
	print("[SubjectSelectionController] Ready")
	
	# Connect signals
	back_button.pressed.connect(_on_back_pressed)
	refresh_button.pressed.connect(_load_subjects)
	APIManager.subjects_loaded.connect(_on_subjects_loaded)
	
	# Load subjects
	_load_subjects()

func _load_subjects():
	if is_loading:
		return
	
	is_loading = true
	loading_label.visible = true
	refresh_button.disabled = true
	
	# Clear list
	for child in subject_list.get_children():
		child.queue_free()
	
	# Request subjects from API
	APIManager.get_student_subjects(GameManager.student_id)

func _on_subjects_loaded(success: bool, data: Dictionary):
	is_loading = false
	loading_label.visible = false
	refresh_button.disabled = false
	
	if not success:
		_show_error("Failed to load subjects: " + data.get("error", "Unknown error"))
		return
	
	var subjects = data.get("subjects", [])
	
	if subjects.is_empty():
		_show_no_subjects()
		return
	
	# Display subjects
	for subject_data in subjects:
		var button = Button.new()
		button.text = subject_data.get("subject_name", "Unknown Subject")
		button.custom_minimum_size = Vector2(0, 80)
		button.pressed.connect(func(): _on_subject_selected(subject_data))
		subject_list.add_child(button)

func _on_subject_selected(subject_data: Dictionary):
	var subject_name = subject_data.get("subject_name", "")
	GameManager.set_current_subject(subject_name)
	
	# Load assignments for this subject
	GameManager.change_scene("quiz_game", {"subject": subject_name})

func _show_error(message: String):
	var label = Label.new()
	label.text = message
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subject_list.add_child(label)

func _show_no_subjects():
	var label = Label.new()
	label.text = "No subjects available. Please join a class first."
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subject_list.add_child(label)

func _on_back_pressed():
	GameManager.change_scene("main_menu")
