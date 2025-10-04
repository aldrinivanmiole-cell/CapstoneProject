extends Control
# QuestionHandler.gd - Handles different question types

var question_data: Dictionary = {}
var question_type: String = ""
var answer_widgets: Array = []

# Multiple Choice
func setup_multiple_choice(question: Dictionary):
	question_data = question
	question_type = "multiple_choice"
	
	var vbox = VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(vbox)
	
	var options = question.get("options", [])
	var button_group = ButtonGroup.new()
	
	for i in range(options.size()):
		var radio = CheckBox.new()
		radio.text = options[i]
		radio.button_group = button_group
		radio.custom_minimum_size = Vector2(0, 50)
		radio.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		vbox.add_child(radio)
		answer_widgets.append(radio)

func get_answer() -> String:
	match question_type:
		"multiple_choice", "yes_no":
			for widget in answer_widgets:
				if widget is CheckBox and widget.button_pressed:
					return widget.text
			return ""
		"text_input", "enumeration":
			if answer_widgets.size() > 0 and answer_widgets[0] is TextEdit:
				return answer_widgets[0].text.strip_edges()
			return ""
		_:
			return ""

# Yes/No Questions
func setup_yes_no(question: Dictionary):
	question_data = question
	question_type = "yes_no"
	
	var hbox = HBoxContainer.new()
	hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(hbox)
	
	var button_group = ButtonGroup.new()
	
	# Yes button
	var yes_button = CheckBox.new()
	yes_button.text = "Yes"
	yes_button.button_group = button_group
	yes_button.custom_minimum_size = Vector2(150, 60)
	hbox.add_child(yes_button)
	answer_widgets.append(yes_button)
	
	# Add spacing
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(50, 0)
	hbox.add_child(spacer)
	
	# No button
	var no_button = CheckBox.new()
	no_button.text = "No"
	no_button.button_group = button_group
	no_button.custom_minimum_size = Vector2(150, 60)
	hbox.add_child(no_button)
	answer_widgets.append(no_button)

# Text Input (for fill_in_blank, short_answer, identification)
func setup_text_input(question: Dictionary):
	question_data = question
	question_type = "text_input"
	
	var vbox = VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(vbox)
	
	var text_edit = TextEdit.new()
	text_edit.custom_minimum_size = Vector2(0, 150)
	text_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text_edit.wrap_mode = TextEdit.LINE_WRAPPING_WORD_SMART
	text_edit.placeholder_text = "Enter your answer here..."
	vbox.add_child(text_edit)
	answer_widgets.append(text_edit)
	
	# Add character counter
	var counter = Label.new()
	counter.text = "0 characters"
	vbox.add_child(counter)
	
	text_edit.text_changed.connect(func():
		counter.text = "%d characters" % text_edit.text.length()
	)

# Enumeration (multiple items)
func setup_enumeration(question: Dictionary):
	question_data = question
	question_type = "enumeration"
	
	var vbox = VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(vbox)
	
	var label = Label.new()
	label.text = "Enter each item on a new line:"
	vbox.add_child(label)
	
	var text_edit = TextEdit.new()
	text_edit.custom_minimum_size = Vector2(0, 200)
	text_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text_edit.wrap_mode = TextEdit.LINE_WRAPPING_WORD_SMART
	text_edit.placeholder_text = "Item 1\nItem 2\nItem 3\n..."
	vbox.add_child(text_edit)
	answer_widgets.append(text_edit)
	
	# Add line counter
	var counter = Label.new()
	counter.text = "0 items"
	vbox.add_child(counter)
	
	text_edit.text_changed.connect(func():
		var lines = text_edit.text.split("\n")
		var non_empty = 0
		for line in lines:
			if not line.strip_edges().is_empty():
				non_empty += 1
		counter.text = "%d items" % non_empty
	)
