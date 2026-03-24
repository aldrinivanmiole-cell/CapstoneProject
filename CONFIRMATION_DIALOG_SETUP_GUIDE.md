# Confirmation Dialog Panel Setup Guide (Android Mobile Game)

This guide will help you add a confirmation dialog panel to your Unity mobile app for Android. Follow each step exactly for best results.

---

## 1. Create the Confirmation Panel

1. In the **Hierarchy**, right-click on `Canvas`.
2. Go to **UI > Panel**.
3. Rename the new panel to `confirmationdialog` (press F2, type, Enter).

---

## 2. Set Panel Position and Size

1. Select `confirmationdialog` in the Hierarchy.
2. In the **Inspector**, under **Rect Transform**:
   - Set **Anchor Presets** to center (hold Shift+Alt, click center square).
   - Set **Pos X**: `0`
   - Set **Pos Y**: `0`
   - Set **Width**: `700`
   - Set **Height**: `350`

---

## 3. Style the Panel

1. In **Image** component:
   - Set **Color** to white with 80% opacity (A=204).
   - Optionally, set a rounded sprite for a softer look.

---

## 4. Add Confirmation Text

1. Right-click on `confirmationdialog` in Hierarchy.
2. Go to **UI > Text - TextMeshPro**.
3. Rename to `ConfirmationText`.
4. In **Rect Transform**:
   - Anchor: center
   - Pos X: `0`, Pos Y: `60`
   - Width: `600`, Height: `100`
5. In **TextMeshPro** component:
   - Text: `Are you sure to pick "Apple" as your answer? 🤔`
   - Font Size: `36`
   - Alignment: Center
   - Color: Black
   - Enable Auto Size (Best Fit)

---

## 5. Add Buttons (Yes/No)

1. Right-click on `confirmationdialog` in Hierarchy.
2. Go to **UI > Button - TextMeshPro** (do this twice).
3. Rename to `ConfirmYesButton` and `ConfirmNoButton`.

### ConfirmYesButton
- Rect Transform: Anchor center, Pos X: `140`, Pos Y: `-70`, Width: `180`, Height: `70`
- Text: `Yes, I'm Sure!`
- Color: Green (`#4CAF50`)

### ConfirmNoButton
- Rect Transform: Anchor center, Pos X: `-140`, Pos Y: `-70`, Width: `180`, Height: `70`
- Text: `No, Let Me Think`
- Color: Gray (`#B0B0B0`)

---

## 6. Hide Panel Initially

1. Select `confirmationdialog` in Hierarchy.
2. In **Inspector**, uncheck the checkbox at the very top (disables the panel).
3. Panel and children should turn gray/italic in Hierarchy.

---

## 7. Connect to Script

1. In **Inspector**, select your main script (e.g., `MultipleChoiceManager`).
2. Drag these objects from Hierarchy to the script fields:
   - `confirmationdialog` (Panel)
   - `ConfirmationText` (TextMeshPro)
   - `ConfirmYesButton` (Button)
   - `ConfirmNoButton` (Button)

---

## 8. Test in Play Mode

1. Press **Play** in Unity.
2. Click an answer choice.
3. Confirmation dialog should appear with the selected answer text.
4. Test Yes/No buttons for correct behavior.

---

## ✅ Done!

Your confirmation dialog is now set up for Android mobile game use.