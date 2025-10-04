extends Control
# LeaderboardController.gd - Displays class leaderboard

@onready var class_selector = $Panel/VBox/ClassSelector
@onready var leaderboard_list = $Panel/VBox/ScrollContainer/LeaderboardList
@onready var refresh_button = $Panel/VBox/RefreshButton
@onready var back_button = $Panel/VBox/BackButton
@onready var loading_label = $Panel/VBox/LoadingLabel

var is_loading = false
var current_class_code = ""

func _ready():
	print("[LeaderboardController] Ready")
	
	# Connect signals
	refresh_button.pressed.connect(_on_refresh_pressed)
	back_button.pressed.connect(_on_back_pressed)
	class_selector.item_selected.connect(_on_class_selected)
	APIManager.leaderboard_loaded.connect(_on_leaderboard_loaded)
	
	# Setup class selector
	_setup_class_selector()

func _setup_class_selector():
	if not class_selector:
		return
	
	class_selector.clear()
	
	var classes = GameManager.enrolled_classes
	if classes.is_empty():
		class_selector.add_item("No classes enrolled")
		class_selector.disabled = true
		return
	
	for i in range(classes.size()):
		var class_data = classes[i]
		var class_name = class_data.get("name", "Unknown")
		var class_code = class_data.get("class_code", "")
		class_selector.add_item("%s (%s)" % [class_name, class_code])
	
	# Select first class and load its leaderboard
	if classes.size() > 0:
		class_selector.selected = 0
		current_class_code = classes[0].get("class_code", "")
		_load_leaderboard()

func _on_class_selected(index: int):
	var classes = GameManager.enrolled_classes
	if index >= 0 and index < classes.size():
		current_class_code = classes[index].get("class_code", "")
		_load_leaderboard()

func _on_refresh_pressed():
	_load_leaderboard()

func _load_leaderboard():
	if is_loading or current_class_code.is_empty():
		return
	
	is_loading = true
	loading_label.visible = true
	refresh_button.disabled = true
	
	# Clear list
	for child in leaderboard_list.get_children():
		child.queue_free()
	
	# Request leaderboard
	APIManager.get_leaderboard(current_class_code, 20)

func _on_leaderboard_loaded(success: bool, data: Dictionary):
	is_loading = false
	loading_label.visible = false
	refresh_button.disabled = false
	
	if not success:
		_show_error("Failed to load leaderboard: " + data.get("error", "Unknown error"))
		return
	
	var leaderboard = data.get("leaderboard", [])
	
	if leaderboard.is_empty():
		_show_empty()
		return
	
	# Display leaderboard entries
	for entry in leaderboard:
		var rank = entry.get("rank", 0)
		var name = entry.get("name", "Unknown")
		var points = entry.get("points", 0)
		var student_id = entry.get("student_id", 0)
		
		var panel = PanelContainer.new()
		panel.custom_minimum_size = Vector2(0, 70)
		
		var hbox = HBoxContainer.new()
		panel.add_child(hbox)
		
		# Rank
		var rank_label = Label.new()
		rank_label.text = "#%d" % rank
		rank_label.custom_minimum_size = Vector2(60, 0)
		rank_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		if rank <= 3:
			rank_label.modulate = _get_medal_color(rank)
		hbox.add_child(rank_label)
		
		# Name
		var name_label = Label.new()
		name_label.text = name
		name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		if student_id == GameManager.student_id:
			name_label.text += " (You)"
			name_label.modulate = Color.LIGHT_BLUE
		hbox.add_child(name_label)
		
		# Points
		var points_label = Label.new()
		points_label.text = "%d pts" % points
		points_label.custom_minimum_size = Vector2(100, 0)
		points_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		hbox.add_child(points_label)
		
		leaderboard_list.add_child(panel)

func _get_medal_color(rank: int) -> Color:
	match rank:
		1: return Color.GOLD
		2: return Color.SILVER
		3: return Color(0.8, 0.5, 0.2)  # Bronze
		_: return Color.WHITE

func _show_error(message: String):
	var label = Label.new()
	label.text = message
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	leaderboard_list.add_child(label)

func _show_empty():
	var label = Label.new()
	label.text = "No leaderboard data available"
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	leaderboard_list.add_child(label)

func _on_back_pressed():
	GameManager.change_scene("main_menu")
