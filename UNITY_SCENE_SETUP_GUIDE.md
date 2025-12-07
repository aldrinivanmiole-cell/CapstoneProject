# 🎮 Unity Scene Setup Guide - Add New UI Elements

## What We Changed

Your `MultipleChoiceManager.cs` now has **5 NEW features**:
1. ✅ **Difficulty badges** (Easy 😊, Medium 🤔, Hard 🔥)
2. ✅ **Previous/Next buttons** for navigation
3. ✅ **Confirmation dialog** ("Do you want to pick this answer? 🤔")
4. ✅ **Auto-save progress** (resume after app close)
5. ✅ **Locked navigation** (can't go back to previous difficulty)

---

## 🛠️ How to Add UI Elements to Your Scene

### Step 1: Open Your Multiple Choice Scene

1. Open Unity
2. Go to **Scenes** folder
3. Open your multiple choice scene (looks like the Indiana Jones scene in your screenshot)

---

### Step 2: Add Navigation Buttons

#### A. Add "Previous" Button

1. Right-click in Hierarchy → **UI** → **Button - TextMeshPro**
2. Rename it to **"PreviousButton"**
3. Position it at **bottom-left corner** of screen
4. Change text to: **"← Previous"**
5. Set font size: **32**

#### B. Add "Next" Button

1. Right-click in Hierarchy → **UI** → **Button - TextMeshPro**
2. Rename it to **"NextButton"**
3. Position it at **bottom-right corner** of screen
4. Change text to: **"Next →"**
5. Set font size: **32**

#### C. Add "Submit" Button

1. Right-click in Hierarchy → **UI** → **Button - TextMeshPro**
2. Rename it to **"SubmitButton"**
3. Position it at **bottom-center** of screen
4. Change text to: **"Finish! 🎉"**
5. Set font size: **36**
6. Change button color to **green** (Image component)

---

### Step 3: Add Difficulty Badge

1. Right-click in Hierarchy → **UI** → **Text - TextMeshPro**
2. Rename it to **"DifficultyBadge"**
3. Position it at **top-right corner** of question panel
4. Default text: **"Easy 😊"**
5. Font size: **28**
6. Enable **Best Fit** (auto-resize)

---

### Step 4: Create Confirmation Dialog Panel

#### A. Create Panel Background

1. Right-click in Hierarchy → **UI** → **Panel**
2. Rename to **"ConfirmationDialog"**
3. Set **Anchor**: Center
4. Set **Width**: 500, **Height**: 300
5. Set background color: Semi-transparent black `RGBA(0, 0, 0, 200)`

#### B. Add Dialog Title Text

1. Right-click on ConfirmationDialog → **UI** → **Text - TextMeshPro**
2. Rename to **"ConfirmationText"**
3. Text: **"Do you want to pick this answer? 🤔"**
4. Font size: **32**
5. Alignment: **Center**
6. Color: **White**

#### C. Add "No" Button (Let me think more)

1. Right-click on ConfirmationDialog → **UI** → **Button - TextMeshPro**
2. Rename to **"ConfirmNoButton"**
3. Text: **"Let me think more 💭"**
4. Position: **Left side** of panel
5. Color: **Gray/Blue**
6. Font size: **28**

#### D. Add "Yes" Button (I'm sure)

1. Right-click on ConfirmationDialog → **UI** → **Button - TextMeshPro**
2. Rename to **"ConfirmYesButton"**
3. Text: **"Yes, I'm sure! ✅"**
4. Position: **Right side** of panel
5. Color: **Green**
6. Font size: **28**

#### E. Hide Dialog Initially

1. Select **ConfirmationDialog** in Hierarchy
2. **Uncheck** the checkbox at top-left of Inspector (deactivate it)
3. It will show as grayed out - this is correct!

---

### Step 5: Connect Everything to MultipleChoiceManager

1. Find your **MultipleChoiceManager** GameObject in Hierarchy
2. Click on it
3. In Inspector, you'll see the script with new fields:

#### Drag and Drop These:

| Field in Inspector | Drag This GameObject |
|-------------------|---------------------|
| **Previous Button** | PreviousButton |
| **Next Button** | NextButton |
| **Submit Button** | SubmitButton |
| **Confirmation Dialog** | ConfirmationDialog (the panel) |
| **Confirmation Text** | ConfirmationText |
| **Confirm Yes Button** | ConfirmYesButton |
| **Confirm No Button** | ConfirmNoButton |
| **Difficulty Badge** | DifficultyBadge |

---

## 📐 Recommended Layout

```
┌──────────────────────────────────────────────────┐
│  Timer: 30    Question 1 of 10        Easy 😊    │  ← Add DifficultyBadge here
├──────────────────────────────────────────────────┤
│                                                   │
│  Question Appears Here                           │
│                                                   │
│  [Answer 1]  [Answer 3]                          │
│  [Answer 2]  [Answer 4]                          │
│                                                   │
│                                                   │
├──────────────────────────────────────────────────┤
│  [← Previous]              [Next →]              │  ← Navigation buttons
│              [Finish! 🎉]                         │  ← Submit (only on last Q)
└──────────────────────────────────────────────────┘

When answer clicked, dialog appears:
┌──────────────────────────────────┐
│  Do you want to pick this        │
│  answer? 🤔                       │
│                                  │
│  [Let me think more 💭]          │
│  [Yes, I'm sure! ✅]             │
└──────────────────────────────────┘
```

---

## 🎨 Styling Tips

### Button Colors:
- **Previous/Next**: Light blue `#4A9EFF`
- **Submit**: Green `#4CAF50`
- **Confirm Yes**: Bright green `#00C853`
- **Confirm No**: Light gray `#78909C`

### Text Sizes:
- Question text: **36**
- Answer buttons: **28**
- Navigation buttons: **32**
- Difficulty badge: **28**
- Dialog text: **32**

### Emojis to Use:
- Easy: 😊
- Medium: 🤔
- Hard: 🔥
- Confirm Yes: ✅
- Confirm No: 💭
- Submit: 🎉

---

## 🧪 Testing Steps

### Test 1: Basic Navigation
1. Play scene
2. Answer first question → See confirmation dialog
3. Click "Yes, I'm sure!" → Answer saved
4. Click "Next →" → Go to Question 2
5. Click "← Previous" → Go back to Question 1
6. ✅ Should see your previously selected answer highlighted

### Test 2: Difficulty Locking
1. Answer Questions 1-3 (Easy)
2. Move to Question 4 (Medium)
3. Try clicking "← Previous"
4. ✅ Button should be disabled/grayed out (Questions 1-3 now locked)

### Test 3: Auto-Save Progress
1. Answer Questions 1-5
2. Press **Home button** on phone (or Stop in Unity)
3. Reopen app / Play again
4. ✅ Should resume at Question 5 with all previous answers intact

### Test 4: Confirmation Dialog
1. Play the scene
2. Click on **any answer button** (Answer 1, 2, 3, or 4)
3. ✅ Confirmation panel should **immediately appear** covering the screen
4. ✅ Shows message: **"Are you sure to pick "[Answer Text]" as your answer? 🤔"**
5. ✅ Message includes the actual answer text you clicked
5. ✅ Two buttons visible: "Let me think more 💭" and "Yes, I'm sure! ✅"
6. Click "Let me think more 💭"
7. ✅ Dialog closes, returns to question, NO answer saved
8. Click another answer button
9. ✅ Dialog appears again
10. Click "Yes, I'm sure! ✅"
11. ✅ Dialog closes, answer saved and highlighted in light blue

### Test 5: Submit and Results
1. Complete all questions
2. On last question, "Finish! 🎉" button appears
3. Click it
4. ✅ Score panel shows total score
5. ✅ Progress cleared (reopen app = fresh start)

---

## 🔧 Common Issues

### Issue: Buttons not working
**Solution:** Make sure you dragged the buttons into the Inspector fields

### Issue: Dialog doesn't show
**Solution:** Check that ConfirmationDialog is deactivated initially (grayed out in Hierarchy)

### Issue: Can't go back even within same difficulty
**Solution:** Make sure difficulty values in database are lowercase: "easy", "medium", "hard"

### Issue: Progress not saving
**Solution:** Check that you have this in Start():
```csharp
saveKey = $"assignment_progress_{assignmentId}_{studentId}";
```

### Issue: All questions show "Easy"
**Solution:** Run the migration script in your Flask project:
```bash
python migrate_add_difficulty.py
```

---

## 📱 Mobile-Specific Tips

### Touch-Friendly Buttons:
- Minimum button size: **100x100 pixels**
- Space between buttons: **20 pixels**
- Use larger fonts: **32+**

### Safe Area:
Position buttons **50 pixels** from screen edges to avoid:
- iPhone notch
- Android navigation bar
- Curved screen edges

### Portrait Mode:
```
Stack buttons vertically:
┌──────────┐
│ Previous │
│   Next   │
│  Submit  │
└──────────┘
```

### Landscape Mode:
```
Spread buttons horizontally:
[Previous]  [Next]  [Submit]
```

---

## ✅ Checklist

Before finishing:
- [ ] Previous button added and connected
- [ ] Next button added and connected
- [ ] Submit button added and connected
- [ ] Difficulty badge added and connected
- [ ] Confirmation dialog panel created
- [ ] Confirmation text added
- [ ] "Yes" button added
- [ ] "No" button added
- [ ] All references dragged to Inspector
- [ ] Dialog initially deactivated
- [ ] Tested navigation
- [ ] Tested difficulty locking
- [ ] Tested auto-save
- [ ] Tested confirmation dialog
- [ ] Tested submit and score

---

## 🎯 What Happens Now

### When Student Uses App:

1. **Opens Assignment**
   - Questions load from server
   - Previous progress restored (if exists)

2. **Answers Question 1 (Easy)**
   - Clicks answer → Dialog appears
   - Confirms → Answer saved to PlayerPrefs
   - Can navigate freely within Easy questions

3. **Moves to Question 4 (Medium)**
   - Easy questions (1-3) become locked 🔒
   - Can only navigate Questions 4-6
   - Cannot go back to 1-3

4. **Closes App (Home Button)**
   - Progress auto-saved to PlayerPrefs
   - Current question: 4
   - All answers: saved

5. **Reopens App Later**
   - Progress restored
   - Resumes at Question 4
   - All previous answers intact

6. **Completes All Questions**
   - Clicks "Finish! 🎉"
   - Score calculated
   - Results shown
   - Progress cleared

---

## 🚀 Ready to Test!

Your Unity app now matches the web version with:
✅ Difficulty levels with color badges
✅ Navigation buttons (Previous/Next)
✅ Confirmation dialog (child-friendly)
✅ Auto-save progress (resume after close)
✅ Smart locking (can't revisit previous difficulty)

**Next Steps:**
1. Add UI elements to your scene (15 minutes)
2. Connect them in Inspector (5 minutes)
3. Test thoroughly (10 minutes)
4. Deploy to device and test real usage

**Good luck! 🎉**
