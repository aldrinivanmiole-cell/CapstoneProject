extends Control
# Main.gd - Entry point of the application

@onready var loading_label = $CenterContainer/VBox/LoadingLabel
@onready var progress_bar = $CenterContainer/VBox/ProgressBar

func _ready():
	print("[Main] Starting application")
	
	# Simulate loading
	await get_tree().create_timer(0.5).timeout
	progress_bar.value = 30
	
	loading_label.text = "Initializing..."
	await get_tree().create_timer(0.5).timeout
	progress_bar.value = 60
	
	loading_label.text = "Checking session..."
	await get_tree().create_timer(0.5).timeout
	progress_bar.value = 90
	
	# Check if user is logged in
	if GameManager.is_student_logged_in():
		loading_label.text = "Welcome back!"
		await get_tree().create_timer(0.5).timeout
		GameManager.change_scene("main_menu")
	else:
		loading_label.text = "Ready!"
		await get_tree().create_timer(0.5).timeout
		GameManager.change_scene("login")
