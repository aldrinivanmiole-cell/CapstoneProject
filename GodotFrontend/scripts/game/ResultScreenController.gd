extends Control
# ResultScreenController.gd - Displays quiz results

@onready var score_label = $Panel/VBox/ScoreLabel
@onready var percentage_label = $Panel/VBox/PercentageLabel
@onready var grade_label = $Panel/VBox/GradeLabel
@onready var points_label = $Panel/VBox/PointsLabel
@onready var view_leaderboard_button = $Panel/VBox/ViewLeaderboardButton
@onready var retry_button = $Panel/VBox/RetryButton
@onready var main_menu_button = $Panel/VBox/MainMenuButton

func _ready():
	print("[ResultScreenController] Ready")
	
	# Connect buttons
	view_leaderboard_button.pressed.connect(_on_leaderboard_pressed)
	retry_button.pressed.connect(_on_retry_pressed)
	main_menu_button.pressed.connect(_on_main_menu_pressed)
	
	# Load and display results
	_display_results()

func _display_results():
	var results_data = DataManager.load_temp_data("quiz_results")
	
	if results_data.is_empty():
		push_error("[ResultScreenController] No results data found")
		_show_error()
		return
	
	# Parse results
	var results = results_data.get("results", {})
	var score = results.get("score", 0)
	var total = results.get("total_points", 0)
	var percentage = results.get("percentage", 0.0)
	var grade = results.get("grade", "F")
	var points_earned = results.get("points_earned", 0)
	
	# Update labels
	if score_label:
		score_label.text = "Score: %d/%d" % [score, total]
	
	if percentage_label:
		percentage_label.text = "%.1f%%" % percentage
		# Color code based on performance
		if percentage >= 90:
			percentage_label.modulate = Color.GREEN
		elif percentage >= 75:
			percentage_label.modulate = Color.YELLOW
		else:
			percentage_label.modulate = Color.RED
	
	if grade_label:
		grade_label.text = "Grade: %s" % grade
		# Color code grade
		if grade in ["A", "A+"]:
			grade_label.modulate = Color.GREEN
		elif grade in ["B", "B+"]:
			grade_label.modulate = Color.LIGHT_BLUE
		elif grade in ["C", "C+"]:
			grade_label.modulate = Color.YELLOW
		else:
			grade_label.modulate = Color.RED
	
	if points_label:
		points_label.text = "Points Earned: %d" % points_earned
	
	# Update GameManager with new points
	if points_earned > 0:
		GameManager.add_points(points_earned)
	
	# Play celebration or encouragement animation
	if percentage >= 75:
		_show_success_animation()
	else:
		_show_encouragement()

func _show_success_animation():
	# Could add particle effects, animations, etc.
	print("[ResultScreenController] Success! Great job!")

func _show_encouragement():
	# Could show motivational message
	print("[ResultScreenController] Keep trying! You can do better!")

func _show_error():
	if score_label:
		score_label.text = "Error loading results"
	# Hide other labels
	if percentage_label:
		percentage_label.visible = false
	if grade_label:
		grade_label.visible = false
	if points_label:
		points_label.visible = false

func _on_leaderboard_pressed():
	GameManager.change_scene("leaderboard")

func _on_retry_pressed():
	GameManager.change_scene("subject_selection")

func _on_main_menu_pressed():
	GameManager.change_scene("main_menu")
