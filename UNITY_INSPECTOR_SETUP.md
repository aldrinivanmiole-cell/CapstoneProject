# 📋 Unity Inspector Setup - Exact Configuration

## What You Need to Connect

After adding all UI elements to your scene, you need to **drag them into the MultipleChoiceManager script** in the Inspector.

---

## Find the MultipleChoiceManager Object

1. Look in your Hierarchy for the object that has the **MultipleChoiceManager** script
2. Common locations:
   - Canvas
   - GameManager
   - EventSystem
   - An empty GameObject called "Manager"
3. Click on it
4. In Inspector, find the **MultipleChoiceManager (Script)** component

---

## Inspector Fields - Complete List

### ✅ ALREADY FILLED (Don't Change):

#### Header: UI References
- **Question Text**: `QuestionText` (TMP_Text showing the question)
- **Progress Text**: `ProgressText` (shows "Question 1 out of 10")
- **Choice Buttons**: `ChoiceButton1`, `ChoiceButton2`, `ChoiceButton3`, `ChoiceButton4`
- **Finish Panel**: `FinishPanel` (panel that shows score at end)
- **Score Text**: `ScoreText` (text inside finish panel)

#### Header: Tutorial
- **Tutorial Button**: `TutorialButton` (opens tutorial link)

---

### ⭐ NEW - YOU NEED TO FILL THESE:

#### Header: Navigation Buttons - NEW!
| Field Name | Drag This GameObject |
|-----------|---------------------|
| **Previous Button** | `PreviousButton` |
| **Next Button** | `NextButton` |
| **Submit Button** | `SubmitButton` |

#### Header: Confirmation Dialog - NEW!
| Field Name | Drag This GameObject |
|-----------|---------------------|
| **Confirmation Dialog** | `ConfirmationDialog` (the panel) |
| **Confirmation Text** | `ConfirmationText` |
| **Confirm Yes Button** | `ConfirmYesButton` |
| **Confirm No Button** | `ConfirmNoButton` |

#### Header: Difficulty Badge - NEW!
| Field Name | Drag This GameObject |
|-----------|---------------------|
| **Difficulty Badge** | `DifficultyBadge` |

---

## Inspector Should Look Like This

```
┌─────────────────────────────────────────────┐
│ MultipleChoiceManager (Script)              │
│                                             │
│ ▼ UI References                             │
│   Question Text        ● QuestionText       │
│   Progress Text        ● ProgressText       │
│   Choice Buttons       Size: 4              │
│     Element 0          ● ChoiceButton1      │
│     Element 1          ● ChoiceButton2      │
│     Element 2          ● ChoiceButton3      │
│     Element 3          ● ChoiceButton4      │
│   Finish Panel         ● FinishPanel        │
│   Score Text           ● ScoreText          │
│                                             │
│ ▼ Navigation Buttons - NEW!                 │
│   Previous Button      ● PreviousButton ←   │
│   Next Button          ● NextButton     ←   │
│   Submit Button        ● SubmitButton   ←   │
│                                             │
│ ▼ Tutorial                                  │
│   Tutorial Button      ● TutorialButton     │
│                                             │
│ ▼ Confirmation Dialog - NEW!                │
│   Confirmation Dialog  ● ConfirmationDialog←│
│   Confirmation Text    ● ConfirmationText ← │
│   Confirm Yes Button   ● ConfirmYesButton ← │
│   Confirm No Button    ● ConfirmNoButton  ← │
│                                             │
│ ▼ Difficulty Badge - NEW!                   │
│   Difficulty Badge     ● DifficultyBadge  ← │
│                                             │
└─────────────────────────────────────────────┘

← Arrows show what YOU need to drag
```

---

## How to Drag and Drop

### Step-by-Step:

1. **Select** the GameObject with MultipleChoiceManager script in Hierarchy
2. **Look** at Inspector on the right
3. **Scroll down** to find the new fields (marked "NEW!")
4. For each empty field:
   - Find the corresponding GameObject in Hierarchy
   - **Click and hold** on it
   - **Drag** to the empty field in Inspector
   - **Release** mouse button
   - Field should now show the GameObject name

### Example: Connecting Previous Button

```
Hierarchy                    Inspector
─────────                   ──────────
Canvas                      Previous Button: [Empty]
├── PreviousButton  ←────→  Previous Button: ● PreviousButton
├── NextButton              
└── ...
```

**Steps:**
1. Click on PreviousButton in Hierarchy
2. Drag it to "Previous Button" field in Inspector
3. Release
4. ✅ Done!

---

## Verification Checklist

After connecting everything, verify:

### ✅ Navigation Buttons
- [ ] Previous Button field shows: `● PreviousButton`
- [ ] Next Button field shows: `● NextButton`
- [ ] Submit Button field shows: `● SubmitButton`

### ✅ Confirmation Dialog
- [ ] Confirmation Dialog field shows: `● ConfirmationDialog`
- [ ] Confirmation Text field shows: `● ConfirmationText`
- [ ] Confirm Yes Button field shows: `● ConfirmYesButton`
- [ ] Confirm No Button field shows: `● ConfirmNoButton`

### ✅ Difficulty Badge
- [ ] Difficulty Badge field shows: `● DifficultyBadge`

### ✅ Initial States
- [ ] ConfirmationDialog is **deactivated** in Hierarchy (grayed out)
- [ ] SubmitButton is **deactivated** in Hierarchy (grayed out)

---

## Common Mistakes

### ❌ Wrong: Dragging Text component instead of GameObject
```
Previous Button: ● Text (TMP)  ← WRONG!
```

**✅ Right: Drag the Button GameObject**
```
Previous Button: ● PreviousButton  ← CORRECT!
```

### ❌ Wrong: Dragging the Panel instead of the Button
```
Confirm Yes Button: ● ConfirmationDialog  ← WRONG!
```

**✅ Right: Drag the Yes Button inside the Panel**
```
Confirm Yes Button: ● ConfirmYesButton  ← CORRECT!
```

### ❌ Wrong: Empty fields
```
Previous Button: [Empty]  ← Script won't work!
```

**✅ Right: All fields filled**
```
Previous Button: ● PreviousButton  ← Works!
```

---

## Testing After Setup

### Test 1: Click Play ▶️
- ✅ No errors in Console
- ✅ Questions load
- ✅ Previous button disabled on Question 1
- ✅ Next button enabled

### Test 2: Click an Answer
- ✅ Confirmation dialog appears
- ✅ Shows: "Do you want to pick this answer? 🤔"
- ✅ Two buttons: "Let me think more" and "Yes, I'm sure!"

### Test 3: Click "Yes, I'm sure!"
- ✅ Dialog closes
- ✅ Answer highlighted (light blue)
- ✅ Console shows: "✅ Progress saved: Question 1/10"

### Test 4: Click Next
- ✅ Moves to Question 2
- ✅ Previous button now enabled
- ✅ Difficulty badge updates

### Test 5: Click Previous
- ✅ Goes back to Question 1
- ✅ Previous answer still highlighted

---

## Complete Hierarchy Structure

Your final hierarchy should look like this:

```
Scene
└── Canvas
    ├── QuestionText (existing)
    ├── ProgressText (existing)
    ├── ChoiceButton1 (existing)
    ├── ChoiceButton2 (existing)
    ├── ChoiceButton3 (existing)
    ├── ChoiceButton4 (existing)
    ├── FinishPanel (existing)
    │   └── ScoreText (existing)
    ├── TutorialButton (existing)
    │
    ├── DifficultyBadge (NEW - TMP_Text)
    ├── PreviousButton (NEW - Button)
    ├── NextButton (NEW - Button)
    ├── SubmitButton (NEW - Button) [DEACTIVATED]
    │
    └── ConfirmationDialog (NEW - Panel) [DEACTIVATED]
        ├── ConfirmationText (NEW - TMP_Text)
        ├── ConfirmNoButton (NEW - Button)
        └── ConfirmYesButton (NEW - Button)
```

**Important Notes:**
- `[DEACTIVATED]` = Checkbox unchecked in Inspector
- Items are grayed out in Hierarchy when deactivated
- Script will activate them when needed

---

## Troubleshooting

### Issue: "Object reference not set to an instance of an object"
**Cause:** One or more fields in Inspector are empty  
**Solution:** Check all fields, make sure all have a blue circle (●) with GameObject name

### Issue: Buttons don't respond to clicks
**Cause:** Wrong GameObject dragged (e.g., Text instead of Button)  
**Solution:** Remove and re-drag the correct Button GameObject

### Issue: Dialog doesn't show when clicking answer
**Cause:** ConfirmationDialog or its children not connected  
**Solution:** Check all 4 confirmation dialog fields are filled

### Issue: Difficulty badge shows nothing
**Cause:** DifficultyBadge field empty  
**Solution:** Drag the DifficultyBadge TMP_Text GameObject to the field

### Issue: Previous/Next buttons always enabled
**Cause:** Navigation button fields empty  
**Solution:** Drag PreviousButton and NextButton GameObjects to their fields

---

## Script Fields Reference

Here's what each field does in the script:

### Navigation Buttons:
- **previousButton**: Goes to previous question (if not locked)
- **nextButton**: Goes to next question
- **submitButton**: Submits all answers and shows score (only on last question)

### Confirmation Dialog:
- **confirmationDialog**: The panel that appears when answer clicked
- **confirmationText**: Shows "Do you want to pick this answer?"
- **confirmYesButton**: Confirms the answer selection
- **confirmNoButton**: Cancels and lets student reconsider

### Difficulty Badge:
- **difficultyBadge**: Shows difficulty level with emoji and color

---

## Console Output Examples

When everything works correctly, you'll see:

### On Start:
```
✅ Progress loaded: Resuming at Question 1/10
```
OR
```
No saved progress found. Starting fresh.
```

### After Confirming Answer:
```
✅ History saved successfully
✅ Progress saved: Question 1/10
```

### On Submit:
```
Final Score: 8/10
✅ Score saved to PlayerPrefs: 80%
✅ Score saved successfully
```

---

## Final Check Before Testing

Run through this checklist:

### Inspector Setup:
- [ ] MultipleChoiceManager script found
- [ ] All original fields still filled (Question Text, etc.)
- [ ] Previous Button field filled
- [ ] Next Button field filled
- [ ] Submit Button field filled
- [ ] Confirmation Dialog field filled
- [ ] Confirmation Text field filled
- [ ] Confirm Yes Button field filled
- [ ] Confirm No Button field filled
- [ ] Difficulty Badge field filled

### Scene Setup:
- [ ] All buttons added to Hierarchy
- [ ] ConfirmationDialog is deactivated (grayed out)
- [ ] SubmitButton is deactivated (grayed out)
- [ ] All buttons positioned correctly
- [ ] Text is readable (not too small)

### Ready to Test:
- [ ] Press Play ▶️
- [ ] Check Console for errors
- [ ] Test clicking answers
- [ ] Test navigation
- [ ] Test confirmation dialog

---

## 🎉 Success!

If all fields are filled correctly:
✅ Script will work perfectly
✅ Buttons will be functional
✅ Dialog will appear when needed
✅ Progress will auto-save
✅ Navigation will lock correctly

**You're ready to test your enhanced Unity app!**

Build it to your Android device:
File → Build Settings → Android → Build and Run

**Good luck! 🚀**
