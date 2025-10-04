extends Control
# QuizController.gd - Manages the quiz game flow

@onready var question_container = $Panel/VBox/QuestionContainer
@onready var question_text = $Panel/VBox/QuestionContainer/QuestionText
@onready var answer_container = $Panel/VBox/AnswerContainer
@onready var submit_button = $Panel/VBox/SubmitButton
@onready var progress_bar = $Panel/VBox/ProgressBar
@onready var progress_label = $Panel/VBox/ProgressLabel
@onready var timer_label = $Panel/VBox/TimerLabel
@onready var back_button = $Panel/VBox/BackButton

var current_question_index: int = 0
var questions: Array = []
var question_handlers: Array = []
var start_time: float = 0.0

func _ready():
	print("[QuizController] Ready")
	
	# Connect signals
	submit_button.pressed.connect(_on_submit_pressed)
	back_button.pressed.connect(_on_back_pressed)
	APIManager.assignment_submitted.connect(_on_assignment_submitted)
	
	# Load assignment data
	_load_assignment()
	
	# Start timer
	start_time = Time.get_ticks_msec() / 1000.0

func _process(_delta):
	# Update timer
	if timer_label:
		var elapsed = (Time.get_ticks_msec() / 1000.0) - start_time
		var minutes = int(elapsed / 60)
		var seconds = int(elapsed) % 60
		timer_label.text = "Time: %02d:%02d" % [minutes, seconds]

func _load_assignment():
	questions = GameManager.current_questions
	
	if questions.is_empty():
		push_error("[QuizController] No questions loaded")
		show_error_and_return("No questions available")
		return
	
	print("[QuizController] Loaded %d questions" % questions.size())
	
	# Display first question
	_display_question(0)

func _display_question(index: int):
	if index < 0 or index >= questions.size():
		return
	
	current_question_index = index
	var question = questions[index]
	
	# Update question text
	if question_text:
		question_text.text = "Q%d: %s" % [index + 1, question.get("question_text", "")]
	
	# Update progress
	_update_progress()
	
	# Clear previous answer container
	for child in answer_container.get_children():
		child.queue_free()
	question_handlers.clear()
	
	# Create appropriate question handler
	var handler = _create_question_handler(question)
	if handler:
		answer_container.add_child(handler)
		question_handlers.append(handler)

func _create_question_handler(question: Dictionary) -> Control:
	var question_type = question.get("question_type", "")
	var handler = null
	
	match question_type:
		"multiple_choice":
			handler = preload("res://scripts/game/QuestionHandler.gd").new()
			handler.setup_multiple_choice(question)
		"yes_no":
			handler = preload("res://scripts/game/QuestionHandler.gd").new()
			handler.setup_yes_no(question)
		"fill_in_blank", "short_answer", "identification":
			handler = preload("res://scripts/game/QuestionHandler.gd").new()
			handler.setup_text_input(question)
		"enumeration":
			handler = preload("res://scripts/game/QuestionHandler.gd").new()
			handler.setup_enumeration(question)
		_:
			push_warning("[QuizController] Unknown question type: " + question_type)
			handler = preload("res://scripts/game/QuestionHandler.gd").new()
			handler.setup_text_input(question)
	
	return handler

func _update_progress():
	var progress_percent = (float(current_question_index) / float(questions.size())) * 100.0
	
	if progress_bar:
		progress_bar.value = progress_percent
	
	if progress_label:
		progress_label.text = "Question %d/%d" % [current_question_index + 1, questions.size()]

func _on_submit_pressed():
	# Get current answer
	if question_handlers.is_empty():
		return
	
	var handler = question_handlers[0]
	var answer = handler.get_answer()
	
	# Validate answer
	if answer.is_empty():
		show_message("Please provide an answer")
		return
	
	# Save answer
	var question_id = questions[current_question_index].get("id", 0)
	GameManager.save_answer(question_id, answer)
	
	# Move to next question or finish
	if current_question_index < questions.size() - 1:
		_display_question(current_question_index + 1)
	else:
		_finish_quiz()

func _finish_quiz():
	# Confirm submission
	show_message("Submitting answers...")
	submit_button.disabled = true
	
	# Submit to API
	var answers = GameManager.get_current_answers()
	APIManager.submit_assignment(
		GameManager.current_assignment_id,
		GameManager.student_id,
		answers
	)

func _on_assignment_submitted(success: bool, data: Dictionary):
	if success:
		# Store results for result screen
		DataManager.save_temp_data("quiz_results", data)
		
		# Go to result screen
		GameManager.change_scene("result")
	else:
		show_message("Submission failed: " + data.get("error", "Unknown error"))
		submit_button.disabled = false

func _on_back_pressed():
	# Confirm before leaving
	var dialog = ConfirmationDialog.new()
	dialog.dialog_text = "Are you sure you want to leave? Your progress will be lost."
	dialog.confirmed.connect(func():
		GameManager.change_scene("subject_selection")
	)
	add_child(dialog)
	dialog.popup_centered()

func show_message(text: String):
	print("[QuizController] ", text)
	# Could add a toast notification here

func show_error_and_return(error: String):
	print("[QuizController] Error: ", error)
	await get_tree().create_timer(2.0).timeout
	GameManager.change_scene("subject_selection")
