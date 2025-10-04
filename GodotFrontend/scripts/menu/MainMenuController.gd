extends Control
# MainMenuController.gd - Controls the main menu

@onready var welcome_label = $Panel/VBox/WelcomeLabel
@onready var points_label = $Panel/VBox/PointsLabel
@onready var subjects_button = $Panel/VBox/SubjectsButton
@onready var leaderboard_button = $Panel/VBox/LeaderboardButton
@onready var profile_button = $Panel/VBox/ProfileButton
@onready var logout_button = $Panel/VBox/LogoutButton

func _ready():
	print("[MainMenuController] Ready")
	
	# Update UI with student info
	_update_ui()
	
	# Connect buttons
	subjects_button.pressed.connect(_on_subjects_pressed)
	leaderboard_button.pressed.connect(_on_leaderboard_pressed)
	profile_button.pressed.connect(_on_profile_pressed)
	logout_button.pressed.connect(_on_logout_pressed)
	
	# Listen for student data updates
	GameManager.student_data_updated.connect(_update_ui)

func _update_ui():
	if welcome_label:
		welcome_label.text = "Welcome, %s!" % GameManager.student_name
	
	if points_label:
		points_label.text = "Points: %d" % GameManager.student_points

func _on_subjects_pressed():
	GameManager.change_scene("subject_selection")

func _on_leaderboard_pressed():
	GameManager.change_scene("leaderboard")

func _on_profile_pressed():
	GameManager.change_scene("profile")

func _on_logout_pressed():
	var dialog = ConfirmationDialog.new()
	dialog.dialog_text = "Are you sure you want to logout?"
	dialog.confirmed.connect(func():
		GameManager.logout()
	)
	add_child(dialog)
	dialog.popup_centered()
