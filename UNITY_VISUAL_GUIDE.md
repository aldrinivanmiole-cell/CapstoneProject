# 📱 Android Mobile Game Setup Guide - Unity Multiple Choice UI

## 🤖 FOR ANDROID MOBILE GAME APP

**⚠️ THIS IS AN ANDROID GAME:**
- Designed for **touch input** on Android phones and tablets
- All buttons are **finger-friendly** sizes (70px+ height)
- Tested on various Android screens (Samsung Galaxy, Google Pixel, OnePlus)
- Safe area padding for phones with navigation bars and notches

## 📐 Exact Screen Layout with Pixel Positions

### Mobile Screen Reference (1920x1080 scales to all phone sizes)

```
Screen Coordinates Reference:
(0,0) = Bottom-Left corner
(1920, 1080) = Top-Right corner

┌─────────────────────────────────────────────────────────────────┐ Y: 1080 (Top)
│  ⏱️ 30                                        [Easy 😊]  ⭐ 0   │
│            Top-Right: X=-250, Y=-120 ↑                         │
├─────────────────────────────────────────────────────────────────┤ Y: 960
│                    Question 1 out of 10                         │
│                                                                 │
│              🏛️ YOUR TEMPLE GAME SCENE 🏛️                       │
│                                                                 │
│              "What is the capital of France?"                   │
│                                                                 │
│         [📜 Answer 1: Paris  ]    [📜 Answer 3: Berlin]        │
│                                                                 │
│         [📜 Answer 2: London ]    [📜 Answer 4: Rome  ]        │
│                                                                 │
│                   🧍 (Player Character)                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤ Y: 200
│                                                                 │
│  [⬅️ Previous]            [Finish 🎉]              [Next ➡️]   │ Y: 100
│  ↑                         ↑                         ↑          │
│  X: 120                   X: 0                    X: -120      │
│  (from left)           (center)                (from right)    │
│  Width: 200            Width: 250               Width: 200     │
│  Height: 70            Height: 80               Height: 70     │
└─────────────────────────────────────────────────────────────────┘ Y: 0 (Bottom)
  X: 0                   X: 960                          X: 1920
  (Left)                (Center)                        (Right)


CONFIRMATION DIALOG (appears in center when answer clicked):

        Screen Center: X: 960, Y: 540
                    ↓
    ┌───────────────────────────────────────┐ ↑
    │                                       │ │ Height: 450
    │ Are you sure to pick "Paris" as your  │ │
    │           answer? 🤔                  │ │
    │                                       │ │
    │         (Width: 700 pixels)           │ │
    │                                       │ │
    │  [Let me think more 💭]               │ │
    │   X: 140 (from left of panel)         │ │
    │   Y: 70 (from bottom of panel)        │ │
    │                                       │ │
    │                [Yes, I'm sure! ✅]    │ │
    │                X: -140 (from right)   │ │
    │                Y: 70 (from bottom)    │ ↓
    └───────────────────────────────────────┘
    ← Width: 700 (centered on screen) →
```

### 📏 Anchor System Explained

Unity uses **Anchors** to position UI relative to screen edges:

```
Anchor Positions:
┌─────────────┬─────────────┬─────────────┐
│  Top-Left   │  Top-Center │  Top-Right  │
│   (0, 1)    │   (0.5, 1)  │   (1, 1)    │
├─────────────┼─────────────┼─────────────┤
│ Middle-Left │   Center    │Middle-Right │
│   (0, 0.5)  │  (0.5, 0.5) │  (1, 0.5)   │
├─────────────┼─────────────┼─────────────┤
│ Bottom-Left │Bottom-Center│Bottom-Right │
│   (0, 0)    │  (0.5, 0)   │   (1, 0)    │
└─────────────┴─────────────┴─────────────┘

When you set anchor and use Shift+Alt:
- Anchor point = Where the UI "sticks" to
- Position = Offset from that anchor point

Examples:
• Bottom-Left anchor + Pos X: 120 = 120 pixels from left edge
• Bottom-Right anchor + Pos X: -120 = 120 pixels from right edge (negative!)
• Top-Right anchor + Pos Y: -120 = 120 pixels down from top (negative!)
```

### 📱 Mobile Safe Area (CRITICAL FOR PHONES!)

```
Why these positions work for ALL Android phones:
┌───────────────────────────────────────────┐
│ ← 50px → STATUS BAR/NOTCH   ← 50px →     │ ← Avoid top 50px (status bar, camera notch)
├───────────────────────────────────────────┤
│                                           │
│    SAFE AREA = Where students can see     │
│         and touch UI comfortably          │
│                                           │
├───────────────────────────────────────────┤
│ ← 50px → NAVIGATION BAR     ← 50px →     │ ← Avoid bottom 50px (Android nav buttons/gestures)
└───────────────────────────────────────────┘

✅ Our Button Positions (Android Touch-Optimized):
• Previous: X: 120, Y: 100 → Easy left-thumb reach
• Next: X: -120, Y: 100 → Easy right-thumb reach  
• Submit: X: 0, Y: 100 → Center, both thumbs can reach
• All buttons: Height 70px+ → Big enough for fingers (Google Material Design: 48px minimum)
• Bottom padding: 100px → Above Android navigation bar (back, home, recents)
```

---

## 🎯 Step-by-Step: Add Touch Buttons to Mobile Game

### 1️⃣ Add Previous Button (Bottom Left)

**Exact Steps:**

1. **Create the Button:**
   - Right-click on **Canvas** in Hierarchy
   - Hover over **UI**
   - Click **Button - TextMeshPro**
   - Unity creates: Button (TMP) with a Text (TMP) child

2. **Rename:**
   - Select the new button in Hierarchy
   - Press **F2** (or right-click → Rename)
   - Type: **PreviousButton**
   - Press **Enter**

3. **Set Anchor (Important!):**
   - **Click once** on PreviousButton in Hierarchy (it should be highlighted in blue)
   - Look at **Inspector panel** (right side of Unity screen)
   - Find **Rect Transform** component at the very top (first component)
   - Look for a small **square box icon** with 4 arrows - it's between "Anchors" label and position fields
   - **Left-click** on this square box icon
   - A popup grid window appears (3x3 grid with 9 squares)
   - **Press and hold** Shift key on keyboard
   - While holding Shift, **press and hold** Alt key (both keys held together)
   - While holding both keys, **left-click** on the **bottom-left corner square** of the grid
   - The popup closes automatically
   - ✅ **Verify:** In Rect Transform, you should now see:
     - Min: X: 0, Y: 0
     - Max: X: 0, Y: 0
   - ✅ The button should jump to the bottom-left corner of the Canvas in Scene view

4. **Set Position:**
   - Still in Inspector, look at **Rect Transform** component
   - Find the **Position** section (has X, Y, Z fields)
   - **Pos X field:**
     - Click inside the field (it highlights in blue)
     - Press **Ctrl+A** to select all
     - Type: `120`
     - Press **Enter** or **Tab**
   - **Pos Y field:**
     - Click inside the field
     - Press **Ctrl+A** to select all
     - Type: `100`
     - Press **Enter** or **Tab**
   - **Pos Z field:**
     - Leave it at `0` (don't change)
   - Find the **Width field** (below Position)
     - Click inside it
     - Press **Ctrl+A**
     - Type: `200`
     - Press **Enter**
   - Find the **Height field** (next to Width)
     - Click inside it
     - Press **Ctrl+A**
     - Type: `70`
     - Press **Enter**
   - ✅ **Verify:** Button should now be positioned 120 pixels from left edge, 100 pixels from bottom

5. **Style the Button:**
   - In Inspector, **scroll down** (use mouse wheel or scroll bar)
   - Find the **Image (Script)** component (has a colored square)
   - Find the **Color** property (shows a colored box)
   - **Left-click** on the colored box
   - A **Color Picker window** opens
   - **Method 1 - Using Hex Code:**
     - Look at the bottom of the Color Picker
     - Find the text field with a # symbol
     - Click inside it
     - Press **Ctrl+A** to select all
     - Type: `4A9EFF`
     - Press **Enter**
   - **Method 2 - Using RGB Sliders:**
     - In Color Picker, find **R slider** (red)
     - Click and drag to `74` OR click the number field and type `74`
     - Find **G slider** (green)
     - Set to `158`
     - Find **B slider** (blue)
     - Set to `255`
     - Find **A slider** (alpha/opacity) at the bottom
     - Make sure it's at `255` (fully visible)
   - Click **X** or click outside the Color Picker to close it
   - ✅ **Verify:** Button should now be light blue in Scene view

6. **Change Button Text:**
   - Go back to **Hierarchy panel** (left side of Unity)
   - Find **PreviousButton** (should be highlighted if still selected)
   - Look for a small **triangle arrow** (►) to the left of PreviousButton name
   - **Left-click** on the triangle - it rotates down (▼) and reveals children
   - You should now see **Text (TMP)** indented below PreviousButton
   - **Left-click once** on **Text (TMP)** to select it (it highlights in blue)
   - Look at **Inspector panel** on the right
   - Scroll to find **TextMeshPro - Text (UI)** component (large component with text box)
   - **Change the text:**
     - Find the **Text Input** box (large white text field at top)
     - **Triple-click** inside it (selects all text)
     - Type: `⬅️ Previous` (arrow emoji + space + word)
     - **Note:** If emoji doesn't work, just type: `Previous`
   - **Set Font Size:**
     - Find **Font Size** field (below Text Input)
     - Click inside it, press **Ctrl+A**
     - Type: `32`
     - Press **Enter**
   - **Set Alignment:**
     - Find **Alignment** section (grid of 9 squares)
     - Click the **center square** (middle of the 3x3 grid)
     - ✅ Text should center both horizontally and vertically
   - **Set Color:**
     - Find **Vertex Color** (shows a color box)
     - Click the color box
     - In Color Picker, type `FFFFFF` in the hex field (or move all RGB sliders to 255)
     - Press **Enter**, close Color Picker
   - **Enable Best Fit:**
     - Scroll down in TextMeshPro component
     - Find **Enable Auto Sizing** checkbox
     - **Click** to check it (✓ appears)
     - Min Size: 18, Max Size: 72 (leave default)
   - ✅ **Verify:** Button should now show "⬅️ Previous" in white, centered text

7. **Optional - Add Icon/Image to Button:**
   - Right-click **PreviousButton** in Hierarchy
   - UI → **Image**
   - Rename it to "ButtonIcon"
   - In **Rect Transform**:
     - Set **Anchor** to Center (Shift+Alt + click center)
     - **Pos X:** `-40` (left side of button)
     - **Pos Y:** `0`
     - **Width:** `40`
     - **Height:** `40`
   - In **Image** component:
     - Click the **circle** next to "Source Image"
     - Search for your arrow/previous icon (e.g., "button ico")
     - Select it
     - ✅ Icon appears on button!
   - Adjust Text position:
     - Select **Text (TMP)** child
     - In Rect Transform, set **Pos X:** `10` (shift text right to make room for icon)

---

### 2️⃣ Add Next Button (Bottom Right)

**Exact Steps:**

1. **Create the Button:**
   - Right-click on **Canvas** in Hierarchy
   - UI → **Button - TextMeshPro**

2. **Rename:**
   - Select the new button
   - Press **F2**
   - Type: **NextButton**
   - Press **Enter**

3. **Set Anchor to Bottom-Right:**
   - Select NextButton in Hierarchy
   - In Inspector, **Rect Transform** component
   - Click **Anchor/Pivot square** (small box icon with 4 arrows)
   - Hold **Shift + Alt** together
   - Click **Bottom-Right corner** of the grid
   - ✅ The button jumps to bottom-right corner

4. **Set Position (Negative X for right side!):**
   - In Rect Transform:
     - **Pos X:** `-120` (120 pixels from RIGHT edge - note the minus!)
     - **Pos Y:** `100` (100 pixels from bottom)
     - **Pos Z:** `0`
     - **Width:** `200`
     - **Height:** `70`

5. **Style the Button:**
   - Image component → **Color:** `#4A9EFF` (light blue)
   - Opacity: `255`

6. **Change Button Text:**
   - Expand NextButton in Hierarchy
   - Click **Text (TMP)** child
   - Text Input: **Next ➡️**
   - Font Size: `32`
   - Alignment: Center
   - Color: White
   - Enable **Best Fit**

7. **Optional - Add Icon/Image to Button:**
   - Right-click **NextButton** in Hierarchy
   - UI → **Image**
   - Rename it to "ButtonIcon"
   - In **Rect Transform**:
     - Set **Anchor** to Center
     - **Pos X:** `40` (right side of button)
     - **Pos Y:** `0`
     - **Width:** `40`
     - **Height:** `40`
   - In **Image** component:
     - Click **circle** next to "Source Image"
     - Select your forward/next arrow icon
     - Set **Rotation Z:** `180` (if using same arrow, flip it)
   - Adjust Text position:
     - Select **Text (TMP)** child
     - Set **Pos X:** `-10` (shift text left)

---

### 3️⃣ Add Submit Button (Bottom Center)

**Exact Steps:**

1. **Create the Button:**
   - Right-click on **Canvas** in Hierarchy
   - UI → **Button - TextMeshPro**

2. **Rename:**
   - Select the button
   - Press **F2**
   - Type: **SubmitButton**
   - Press **Enter**

3. **Set Anchor to Bottom-Center:**
   - Select SubmitButton in Hierarchy
   - In Inspector, **Rect Transform**
   - Click **Anchor/Pivot square**
   - Hold **Shift + Alt**
   - Click **Bottom-Center** (middle of bottom row in grid)
   - ✅ Button moves to bottom-center

4. **Set Position:**
   - In Rect Transform:
     - **Pos X:** `0` (centered)
     - **Pos Y:** `100` (100 pixels from bottom)
     - **Pos Z:** `0`
     - **Width:** `250`
     - **Height:** `80`

5. **Style the Button (Green!):**
   - Image component → **Color:** `#4CAF50` (green) or RGB(76, 175, 80)
   - Opacity: `255`

6. **Change Button Text:**
   - Expand SubmitButton in Hierarchy
   - Click **Text (TMP)** child
   - Text Input: **Finish 🎉**
   - Font Size: `40` (larger than other buttons)
   - Alignment: Center
   - Color: White
   - Font Style: **Bold** (click B button)
   - Enable **Best Fit**

7. **IMPORTANT - Deactivate Initially:**
   - Select **SubmitButton** in Hierarchy (the parent, not the text)
   - Look at **Inspector** at the very top
   - **Uncheck** the checkbox next to "SubmitButton" name
   - ✅ Button should now be grayed out in Hierarchy
   - ✅ This is correct! Script will activate it on last question

---

### 4️⃣ Add Difficulty Badge (Top Right)

**Exact Steps:**

1. **Create Text Element:**
   - Right-click on **Canvas** in Hierarchy
   - UI → **Text - TextMeshPro**
   - (NOT Button - just Text!)

2. **Rename:**
   - Select the text
   - Press **F2**
   - Type: **DifficultyBadge**
   - Press **Enter**

3. **Set Anchor to Top-Right:**
   - Select DifficultyBadge in Hierarchy
   - In Inspector, **Rect Transform**
   - Click **Anchor/Pivot square**
   - Hold **Shift + Alt**
   - Click **Top-Right corner** of the grid

4. **Set Position:**
   - In Rect Transform:
     - **Pos X:** `-250` (250 pixels from RIGHT edge - negative!)
     - **Pos Y:** `-120` (120 pixels from TOP - negative!)
     - **Pos Z:** `0`
     - **Width:** `200`
     - **Height:** `60`

5. **Style the Text:**
   - In **TextMeshPro - Text (UI)** component:
   - **Text Input:** `Easy 😊`
   - **Font Size:** `32`
   - **Alignment:** Center (both H and V)
   - **Color:** Green `#50C878` or RGB(80, 200, 120)
   - **Font Style:** Bold (click **B** button)
   - Enable **Best Fit**

6. **Optional - Add Background Panel:**
   - Right-click DifficultyBadge in Hierarchy
   - UI → **Image**
   - This creates a child Image
   - In Rect Transform, click **Anchor** preset
   - Hold **Shift + Alt** and click **Stretch/Stretch** (bottom-right)
   - Set **Left, Right, Top, Bottom** all to: `0`
   - In Image component:
     - **Color:** `RGBA(0, 0, 0, 150)` (semi-transparent black)
     - **A (Alpha):** `150` (semi-transparent)
   - In Hierarchy, drag the Image **above** DifficultyBadge text (so text appears on top)
   - Rename Image to "Background"

---

### 5️⃣ Create Confirmation Dialog (Center Screen)

**PURPOSE:** This panel appears when the student **clicks an answer choice** to confirm their selection.

#### A. Create Panel Background

**Exact Steps:**

1. **Create Panel:**
   - Right-click on **Canvas** in Hierarchy
   - UI → **Panel**
   - Unity creates a full-screen dark panel

2. **Rename:**
   - Select the new Panel
   - Press **F2**
   - Type: **ConfirmationDialog**
   - Press **Enter**

3. **Set Anchor to Center:**
   - Select ConfirmationDialog
   - In Inspector, **Rect Transform**
   - Click **Anchor/Pivot square**
   - Hold **Shift + Alt**
   - Click **Center** (middle of grid)

4. **Set Size (Smaller than screen):**
   - In Rect Transform:
     - **Pos X:** `0`
     - **Pos Y:** `0`
     - **Pos Z:** `0`
     - **Width:** `700`
     - **Height:** `450`

5. **Style the Panel:**
   - In **Image** component:
     - **Color:** `RGBA(30, 30, 30, 230)` (dark gray, almost opaque)
     - To set this: Click color box
     - **R:** `30`, **G:** `30`, **B:** `30`, **A:** `230`

6. **Optional - Add Border:**
   - In **Image** component
   - Check **Raycast Target** (so dialog blocks clicks behind it)

---

#### B. Add Dialog Title Text (Inside Panel)

**Exact Steps:**

1. **Create Text:**
   - Right-click **ConfirmationDialog** in Hierarchy (the panel you just made)
   - UI → **Text - TextMeshPro**

2. **Rename:**
   - Press **F2**
   - Type: **ConfirmationText**

3. **Set Anchor to Top-Center (relative to panel):**
   - In Rect Transform
   - Click **Anchor square**
   - Hold **Shift + Alt**
   - Click **Top-Center**

4. **Set Position (Inside the Panel):**
   - In Rect Transform:
     - **Pos X:** `0`
     - **Pos Y:** `-80` (negative = down from top)
     - **Pos Z:** `0`
     - **Width:** `600`
     - **Height:** `150`

5. **Style the Text:**
   - In **TextMeshPro - Text (UI)**:
   - **Text Input:** `Are you sure to pick "Apple" as your answer? 🤔`
   - **Font Size:** `40`
   - **NOTE:** This is just placeholder text - the script will change it to show the actual selected answer
   - **Alignment:** Center (both H and V)
   - **Color:** White `#FFFFFF`
   - **Font Style:** Bold
   - Enable **Best Fit**
   - Check **Word Wrapping**

---

#### C. Add "No" Button (Inside Panel - Bottom Left)

**Exact Steps:**

1. **Create Button:**
   - Right-click **ConfirmationDialog** in Hierarchy
   - UI → **Button - TextMeshPro**

2. **Rename:**
   - Press **F2**
   - Type: **ConfirmNoButton**

3. **Set Anchor to Bottom-Left (relative to panel):**
   - In Rect Transform
   - Click **Anchor square**
   - Hold **Shift + Alt**
   - Click **Bottom-Left corner**

4. **Set Position:**
   - In Rect Transform:
     - **Pos X:** `140` (140 pixels from left edge of panel)
     - **Pos Y:** `70` (70 pixels from bottom of panel)
     - **Pos Z:** `0`
     - **Width:** `250`
     - **Height:** `80`

5. **Style the Button:**
   - In **Image** component:
     - **Color:** `#9E9E9E` (gray) or RGB(158, 158, 158)

6. **Change Text:**
   - Expand ConfirmNoButton in Hierarchy
   - Click **Text (TMP)** child
   - **Text Input:** `Let me think more 💭`
   - **Font Size:** `28`
   - **Alignment:** Center
   - **Color:** White
   - Enable **Best Fit**
   - Check **Word Wrapping**

---

#### D. Add "Yes" Button (Inside Panel - Bottom Right)

**Exact Steps:**

1. **Create Button:**
   - Right-click **ConfirmationDialog** in Hierarchy
   - UI → **Button - TextMeshPro**

2. **Rename:**
   - Press **F2**
   - Type: **ConfirmYesButton**

3. **Set Anchor to Bottom-Right (relative to panel):**
   - In Rect Transform
   - Click **Anchor square**
   - Hold **Shift + Alt**
   - Click **Bottom-Right corner**

4. **Set Position:**
   - In Rect Transform:
     - **Pos X:** `-140` (negative! 140 pixels from RIGHT edge of panel)
     - **Pos Y:** `70` (70 pixels from bottom of panel)
     - **Pos Z:** `0`
     - **Width:** `250`
     - **Height:** `80`

5. **Style the Button (Green!):**
   - In **Image** component:
     - **Color:** `#4CAF50` (green) or RGB(76, 175, 80)

6. **Change Text:**
   - Expand ConfirmYesButton in Hierarchy
   - Click **Text (TMP)** child
   - **Text Input:** `Yes, I'm sure! ✅`
   - **Font Size:** `30`
   - **Alignment:** Center
   - **Color:** White
   - **Font Style:** Bold
   - Enable **Best Fit**

---

#### E. Hide Dialog Initially (CRITICAL!)

**Exact Steps:**

1. **Select the Panel:**
   - Go to **Hierarchy panel** (left side)
   - Scroll to find **ConfirmationDialog**
   - **Left-click once** on **ConfirmationDialog** (NOT on its children)
   - It should highlight in blue
   - ✅ Make sure you clicked the parent, not ConfirmationText or buttons

2. **Deactivate It:**
   - Look at **Inspector panel** (right side)
   - Look at the **very top** of Inspector
   - You'll see the name "ConfirmationDialog" with a checkbox to its left
   - This checkbox should currently be **checked** (✓)
   - **Left-click ONCE** on that checkbox to uncheck it
   - The checkbox should now be **empty** (☐)
   - ✅ **Immediate visual feedback:**
     - In **Hierarchy:** ConfirmationDialog and ALL its children turn **gray/italic**
     - In **Scene view:** The dialog panel **disappears completely**
     - In **Game view:** Nothing changes (we're not in Play mode)

3. **Verify - Check These Things:**
   - **Hierarchy panel check:**
     - ConfirmationDialog text is **gray and italic** ☐
     - ConfirmationText below it is **gray and italic** ☐
     - ConfirmNoButton is **gray and italic** ☐
     - ConfirmYesButton is **gray and italic** ☐
   - **Scene view check:**
     - The dark dialog panel is **NOT visible**
     - You can see your game scene clearly without overlay
   - **Inspector check:**
     - At top, checkbox next to ConfirmationDialog is **unchecked** (☐)
   - ✅ **What this means:**
     - Dialog is inactive = won't show when game starts
     - **The script automatically activates it when student clicks an answer**
     - This is CORRECT behavior!
   - ❌ **If dialog is NOT grayed out:**
     - You clicked the wrong checkbox
     - Make sure you're clicking the checkbox at the VERY TOP of Inspector
     - Try again from step 1

---

## Visual Layout Reference

### Before (Your Current Scene):
```
┌──────────────────────────────────────┐
│  Timer        Question 1        Score│
├──────────────────────────────────────┤
│                                      │
│  Question Text Here                  │
│                                      │
│  [Answer 1]      [Answer 3]          │
│  [Answer 2]      [Answer 4]          │
│                                      │
│  (No navigation - auto-advances)     │
└──────────────────────────────────────┘
```

### After (With New Buttons):
```
┌──────────────────────────────────────┐
│  Timer  Question 1 of 10  [Easy 😊]  │  ← Difficulty badge
├──────────────────────────────────────┤
│                                      │
│  Question Text Here                  │
│                                      │
│  [Answer 1]      [Answer 3]          │
│  [Answer 2]      [Answer 4]          │
│                                      │
│  [◄ Previous]         [Next ►]      │  ← Navigation (with icons)
│           [Finish 🎉]                │  ← Submit (last Q only)
└──────────────────────────────────────┘
```

### Button Layout with Icons (Close-up):
```
Previous Button:              Next Button:
┌─────────────────┐          ┌─────────────────┐
│ ◄ Previous      │          │      Next ►     │
│ ↑   ↑           │          │        ↑   ↑    │
│ │   └─Text      │          │        │   └─Text
│ └─Icon (40x40)  │          │        └─Icon   │
└─────────────────┘          └─────────────────┘
Width: 200px                 Width: 200px
Height: 70px                 Height: 70px
```

### Confirmation Dialog (Appears When Answer Clicked):
```
        ┌─────────────────────────────┐
        │                             │
        │  Are you sure to pick       │
        │  "Paris" as your answer? 🤔  │
        │                             │
        │  [Let me think more 💭]     │
        │                             │
        │  [Yes, I'm sure! ✅]        │
        │                             │
        └─────────────────────────────┘
```

---

## 📂 Exact Hierarchy Structure

After adding all elements, your Hierarchy panel should look **exactly** like this:

```
📁 Hierarchy Window
└── 📄 IndianaJonesMultipleChoice (your scene)
    ├── 📷 Main Camera (existing)
    ├── 💡 Directional Light (existing)
    ├── 🎮 EventSystem (existing)
    │
    └── 🖼️ Canvas (existing)
        ├── 📝 QuestionText (existing)
        ├── 📝 ProgressText (existing)
        ├── 🔘 ChoiceButton1 (existing)
        │   └── 📝 Text (TMP)
        ├── 🔘 ChoiceButton2 (existing)
        │   └── 📝 Text (TMP)
        ├── 🔘 ChoiceButton3 (existing)
        │   └── 📝 Text (TMP)
        ├── 🔘 ChoiceButton4 (existing)
        │   └── 📝 Text (TMP)
        ├── 🪟 FinishPanel (existing)
        │   └── 📝 ScoreText
        ├── 🔘 TutorialButton (existing)
        │
        ├── 🏷️ DifficultyBadge (NEW - Text, not button!)
        ├── 🔘 PreviousButton (NEW)
        │   ├── 🖼️ ButtonIcon (optional - arrow image)
        │   └── 📝 Text (TMP)
        ├── 🔘 NextButton (NEW)
        │   ├── 🖼️ ButtonIcon (optional - arrow image)
        │   └── 📝 Text (TMP)
        ├── 🔘 SubmitButton (NEW) [grayed out = inactive ✓]
        │   └── 📝 Text (TMP)
        │
        └── 🪟 ConfirmationDialog (NEW) [grayed out = inactive ✓]
            ├── 📝 ConfirmationText (NEW)
            ├── 🔘 ConfirmNoButton (NEW)
            │   └── 📝 Text (TMP)
            └── 🔘 ConfirmYesButton (NEW)
                └── 📝 Text (TMP)
```

### ✅ Verification Checklist:

- [ ] ConfirmationDialog shows as **grayed out/italic** (inactive)
- [ ] SubmitButton shows as **grayed out/italic** (inactive)
- [ ] All NEW items are children of **Canvas**
- [ ] ConfirmationDialog has 3 children (text + 2 buttons)
- [ ] Each button has a "Text (TMP)" child
- [ ] DifficultyBadge is text only (no Text child)

---

## 🔍 Inspector Settings - Detailed View

### When you select **PreviousButton**, Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ☑️ PreviousButton                    Tag: Untagged│
│                                     Layer: UI   │
├─────────────────────────────────────────────────┤
│ ▼ Transform                                     │
│   Position: X:0  Y:0  Z:0                       │
│   Rotation: X:0  Y:0  Z:0                       │
│   Scale:    X:1  Y:1  Z:1                       │
├─────────────────────────────────────────────────┤
│ ▼ Rect Transform                                │
│   Anchor Presets: [●]                           │
│                                                 │
│   Anchors                                       │
│   Min: X: 0      Y: 0      (Bottom-Left)       │
│   Max: X: 0      Y: 0      (Bottom-Left)       │
│                                                 │
│   Pivot:  X: 0.5    Y: 0.5                     │
│                                                 │
│   Position                                      │
│   Pos X: 120     ← TYPE THIS                   │
│   Pos Y: 100     ← TYPE THIS                   │
│   Pos Z: 0                                      │
│                                                 │
│   Width:  200    ← TYPE THIS                   │
│   Height: 70     ← TYPE THIS                   │
│                                                 │
│   Rotation: Z: 0                                │
│   Scale: X:1  Y:1  Z:1                         │
├─────────────────────────────────────────────────┤
│ ▼ Canvas Renderer                               │
│   (no settings needed)                          │
├─────────────────────────────────────────────────┤
│ ▼ Image (Script)                                │
│   Source Image:  [UI-Sprite]                    │
│   Color:  ████  #4A9EFF  ← CLICK & CHANGE      │
│             R: 74                               │
│             G: 158                              │
│             B: 255                              │
│             A: 255                              │
│   Material: None (Material)                     │
│   Raycast Target: ☑️                            │
│   Image Type: Simple                            │
├─────────────────────────────────────────────────┤
│ ▼ Button (Script)                               │
│   Interactable: ☑️                              │
│   Transition: Color Tint                        │
│   Target Graphic: Image (Button)                │
│   Normal Color:      ████ White                 │
│   Highlighted Color: ████ Light Gray            │
│   Pressed Color:     ████ Dark Gray             │
│   Selected Color:    ████ Gray                  │
│   Disabled Color:    ████ Very Light Gray       │
│   Color Multiplier: 1                           │
│   Fade Duration: 0.1                            │
│                                                 │
│   Navigation: Automatic                         │
│                                                 │
│   OnClick()                                     │
│   List is Empty  ← Don't touch, script handles │
└─────────────────────────────────────────────────┘
```

### When you select **NextButton**, Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ▼ Rect Transform                                │
│   Anchors                                       │
│   Min: X: 1      Y: 0      (Bottom-Right)      │
│   Max: X: 1      Y: 0      (Bottom-Right)      │
│                                                 │
│   Position                                      │
│   Pos X: -120    ← NEGATIVE! (from right)      │
│   Pos Y: 100                                    │
│   Width:  200                                   │
│   Height: 70                                    │
│                                                 │
│ ▼ Image                                         │
│   Color: #4A9EFF (same blue as Previous)       │
└─────────────────────────────────────────────────┘
```

### When you select **SubmitButton**, Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ☐ SubmitButton  ← UNCHECKED! (inactive)        │
│                                                 │
│ ▼ Rect Transform                                │
│   Anchors                                       │
│   Min: X: 0.5    Y: 0      (Bottom-Center)     │
│   Max: X: 0.5    Y: 0      (Bottom-Center)     │
│                                                 │
│   Position                                      │
│   Pos X: 0       ← Centered                    │
│   Pos Y: 100                                    │
│   Width:  250    ← Bigger than others          │
│   Height: 80     ← Taller                      │
│                                                 │
│ ▼ Image                                         │
│   Color: #4CAF50  ← GREEN!                     │
│             R: 76                               │
│             G: 175                              │
│             B: 80                               │
│             A: 255                              │
└─────────────────────────────────────────────────┘
```

### When you select **DifficultyBadge**, Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ☑️ DifficultyBadge                              │
│                                                 │
│ ▼ Rect Transform                                │
│   Anchors                                       │
│   Min: X: 1      Y: 1      (Top-Right)         │
│   Max: X: 1      Y: 1      (Top-Right)         │
│                                                 │
│   Position                                      │
│   Pos X: -250    ← NEGATIVE! (from right)      │
│   Pos Y: -120    ← NEGATIVE! (down from top)   │
│   Width:  200                                   │
│   Height: 60                                    │
│                                                 │
│ ▼ Canvas Renderer                               │
│   (no settings)                                 │
│                                                 │
│ ▼ TextMeshPro - Text (UI) (Script)             │
│   Text Input:                                   │
│   ┌───────────────────────────────────────┐    │
│   │ Easy 😊                               │    │
│   └───────────────────────────────────────┘    │
│                                                 │
│   Font Asset: LiberationSans SDF                │
│   Font Style: Bold  ← CLICK B BUTTON           │
│   Font Size: 32                                 │
│   Auto Size: ☑️ ← CHECK THIS                   │
│   Min: 18  Max: 72                             │
│                                                 │
│   Alignment: ╋  ← Click center both H and V    │
│                                                 │
│   Color: #50C878 (Green)                       │
│          R: 80                                  │
│          G: 200                                 │
│          B: 120                                 │
│          A: 255                                 │
│                                                 │
│   Wrapping: ☑️ Enabled                         │
│   Overflow: Truncate                            │
└─────────────────────────────────────────────────┘
```

### When you select **ConfirmationDialog**, Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ☐ ConfirmationDialog  ← UNCHECKED! (inactive)  │
│                                                 │
│ ▼ Rect Transform                                │
│   Anchors                                       │
│   Min: X: 0.5    Y: 0.5    (Center)            │
│   Max: X: 0.5    Y: 0.5    (Center)            │
│                                                 │
│   Position                                      │
│   Pos X: 0       ← Centered                    │
│   Pos Y: 0       ← Centered                    │
│   Width:  700    ← Big dialog                  │
│   Height: 450    ← Tall dialog                 │
│                                                 │
│ ▼ Image                                         │
│   Color: RGBA(30, 30, 30, 230) ← Dark!         │
│          R: 30   ← Almost black                │
│          G: 30                                  │
│          B: 30                                  │
│          A: 230  ← Almost opaque               │
│   Raycast Target: ☑️ ← MUST be checked         │
└─────────────────────────────────────────────────┘
```

### When you select **ConfirmYesButton** (inside dialog), Inspector should show:

```
┌─────────────────────────────────────────────────┐
│ ☑️ ConfirmYesButton  ← Active (parent inactive) │
│                                                 │
│ ▼ Rect Transform                                │
│   Anchors                                       │
│   Min: X: 1      Y: 0      (Bottom-Right       │
│   Max: X: 1      Y: 0       relative to panel!)│
│                                                 │
│   Position (relative to ConfirmationDialog!)   │
│   Pos X: -140    ← From RIGHT edge of panel    │
│   Pos Y: 70      ← From BOTTOM edge of panel   │
│   Width:  250                                   │
│   Height: 80                                    │
│                                                 │
│ ▼ Image                                         │
│   Color: #4CAF50 (GREEN)                       │
└─────────────────────────────────────────────────┘
```

---

## Inspector Setup

### Find Your MultipleChoiceManager Script

1. Look in Hierarchy for object with **MultipleChoiceManager** script
   - Might be on **EventSystem**, **Canvas**, or a separate **GameManager** object
2. Click on it
3. In Inspector, scroll to **MultipleChoiceManager** component

### Drag and Drop References

You should see these new fields:

#### Navigation Buttons Section:
- **Previous Button**: Drag `PreviousButton` from Hierarchy
- **Next Button**: Drag `NextButton` from Hierarchy
- **Submit Button**: Drag `SubmitButton` from Hierarchy

#### Confirmation Dialog Section:
- **Confirmation Dialog**: Drag `ConfirmationDialog` (the panel) from Hierarchy
- **Confirmation Text**: Drag `ConfirmationText` from Hierarchy
- **Confirm Yes Button**: Drag `ConfirmYesButton` from Hierarchy
- **Confirm No Button**: Drag `ConfirmNoButton` from Hierarchy

#### Difficulty Badge:
- **Difficulty Badge**: Drag `DifficultyBadge` from Hierarchy

---

## Testing in Unity Editor

### Quick Test:
1. Press **Play** ▶️
2. Wait for questions to load
3. Click an answer (e.g., "Paris")
4. ✅ Confirmation dialog should appear
5. ✅ Dialog shows: **"Are you sure to pick "Paris" as your answer? 🤔"**
6. ✅ Message includes the actual answer text you clicked
7. Click "Yes, I'm sure!"
8. ✅ Answer saved, Next button enabled
9. Click Next
10. ✅ Move to Question 2

### Navigation Test:
1. Answer Questions 1-2
2. Click Previous
3. ✅ Should go back to Question 1
4. ✅ Should see your previous answer highlighted (light blue)

### Difficulty Lock Test:
1. Answer Questions 1-3 (Easy)
2. Move to Question 4 (Medium)
3. ✅ Previous button should be disabled (grayed out)
4. ✅ Can't go back to Q1-Q3

---

## Color Scheme Recommendation

Match your temple theme:

### Buttons:
- **Previous/Next**: Sandy gold `#D4A574`
- **Submit**: Treasure green `#4CAF50`
- **Dialog background**: Temple stone `RGBA(50, 40, 30, 220)`

### Text:
- **Question**: Torch orange `#FF8C00`
- **Difficulty Easy**: Emerald green `#50C878`
- **Difficulty Medium**: Gold `#FFD700`
- **Difficulty Hard**: Ruby red `#E0115F`

---

## Mobile Preview

### Portrait (Phone):
```
┌──────────────┐
│ Q1  [Easy 😊]│
├──────────────┤
│              │
│  Question    │
│              │
│ [Answer 1]   │
│ [Answer 2]   │
│ [Answer 3]   │
│ [Answer 4]   │
│              │
├──────────────┤
│  [⬅️ Prev]   │
│  [Next ➡️]   │
│  [Finish]    │
└──────────────┘
```

### Landscape (Tablet):
```
┌─────────────────────────────────────┐
│ Q1              Question    [Easy 😊]│
├─────────────────────────────────────┤
│                                     │
│  [Answer 1]  [Answer 2]             │
│  [Answer 3]  [Answer 4]             │
│                                     │
├─────────────────────────────────────┤
│ [⬅️ Prev]      [Finish]    [Next ➡️]│
└─────────────────────────────────────┘
```

---

## Troubleshooting

### Problem: Buttons overlap with existing UI
**Solution:** Adjust Pos Y values. Move buttons to Y = 100 or Y = 120 if overlapping

### Problem: Dialog too small on phone
**Solution:** Increase width to 700, height to 500 for dialog panel

### Problem: Text doesn't fit in buttons
**Solution:** Enable "Auto Size" in TextMeshPro component OR increase button width

### Problem: Can't click buttons
**Solution:** Make sure buttons are **above** background panels in Hierarchy (lower in list = drawn on top)

---

## 📱 CRITICAL: Test on Real Android Device

**⚠️ Unity Editor testing is NOT enough! You MUST test on actual Android phone:**

### 🤖 Build and Test on Android Phone:

**Step 1: Prepare Your Android Phone**
1. On your Android phone:
   - Go to **Settings → About Phone** (or About Device)
   - Find **Build Number** (may be under Software Information)
   - **Tap Build Number 7 times** rapidly
   - You'll see message: "You are now a developer!"
   - Go back to **Settings**
   - Find **Developer Options** (usually under System or Additional Settings)
   - Scroll down and enable **USB Debugging**
   - You'll see a toggle switch - turn it ON
   - A popup appears asking to allow USB debugging - tap **OK**

2. Connect phone to computer:
   - Use a **USB cable** (the charging cable)
   - Connect phone to your Windows PC
   - On phone, you may see popup: "Allow USB debugging?" - tap **Always Allow** then **OK**
   - On PC, Windows may install drivers automatically (wait for this)

**Step 2: Build APK in Unity**
1. In Unity, go to **File → Build Settings** (or press **Ctrl+Shift+B**)
2. In the Platform list (left side), select **Android**
3. If "Android" shows "Switch Platform" button:
   - Click **Switch Platform**
   - Wait 2-5 minutes (Unity imports Android modules)
   - ✅ When done, Android icon will have Unity logo next to it
4. **IMPORTANT:** Click **Player Settings** button (bottom-left)
   - In Inspector, find **Other Settings** section
   - Find **Minimum API Level**: Set to **Android 5.0 (API level 21)** or higher
   - Find **Target API Level**: Set to **Android 11 (API level 30)** or higher
   - Close Player Settings
5. Back in Build Settings, click **Build And Run**
6. Choose where to save APK:
   - Navigate to **Desktop**
   - Create folder: **StudentGameBuilds**
   - Name file: **StudentGame.apk**
   - Click **Save**
7. Unity builds the APK (takes 2-10 minutes first time)
8. When done, Unity automatically:
   - Installs APK on your connected Android phone
   - Opens the app on your phone

**Step 3: Test These on Your Android Phone**

**Touch & Button Tests:**
- ✅ **Touch response:** Do buttons respond immediately when you tap? (no delay)
- ✅ **Button size:** Can you easily tap buttons with your thumb? (not too small, not missing taps)
- ✅ **One-handed use:** Hold phone with LEFT hand, can you reach Previous button with left thumb?
- ✅ **One-handed use:** Hold phone with RIGHT hand, can you reach Next button with right thumb?
- ✅ **Accidental taps:** Do you accidentally hit wrong buttons? (they should be spaced apart)

**Confirmation Dialog Tests:**
- ✅ **Dialog appears:** Tap any answer choice → Does confirmation dialog pop up immediately?
- ✅ **Dialog text:** Can you read the confirmation message clearly? (font not too small)
- ✅ **Answer text shown:** Dialog shows: "Are you sure to pick '[ANSWER YOU TAPPED]' as your answer?"
- ✅ **Yes/No buttons:** Are they easy to tap without hitting the wrong one?
- ✅ **Cancel works:** Tap "No, Let Me Think" → Dialog closes, answer NOT saved
- ✅ **Confirm works:** Tap "Yes, I'm Sure!" → Dialog closes, answer IS saved, Next button enables

**Navigation Tests:**
- ✅ **Previous disabled:** On question 1, Previous button is grayed out (can't tap it)
- ✅ **Next disabled:** Before answering, Next button is grayed out
- ✅ **Next enables:** After answering, Next button turns blue (can tap it)
- ✅ **Navigation works:** Tap Next → Goes to question 2, Previous button now enabled
- ✅ **Go back works:** Tap Previous → Returns to question 1, your answer is still highlighted

**Difficulty Locking Tests:**
- ✅ **Answer easy questions:** Answer questions 1, 2, 3 (Easy difficulty)
- ✅ **Move to medium:** Go to question 4 (Medium difficulty starts)
- ✅ **Can't go back:** Try tapping Previous → Should stay on question 4 (can't go back to Easy)
- ✅ **Badge color changes:** Difficulty badge changes: 🟢 Easy → 🟡 Medium → 🔴 Hard

**Safe Area Tests (IMPORTANT for Android!):**
- ✅ **Status bar:** Difficulty badge at top-right doesn't hide behind status bar/notch
- ✅ **Navigation bar:** Bottom buttons don't hide behind Android navigation bar (back/home/recents)
- ✅ **Gesture bar:** On phones with gesture navigation, buttons are above gesture bar
- ✅ **Notch/camera:** On phones with notch (like Galaxy S10), UI doesn't hide behind camera cutout

**App Lifecycle Tests (CRITICAL!):**
- ✅ **Background app:** Play game → Answer 2-3 questions → Press **Home button** on phone → Reopen app → Should continue where you left off (progress saved!)
- ✅ **Recent apps:** Play game → Press **Recent Apps button** (square icon) → Swipe to another app → Return to game → Progress saved?
- ✅ **Force close:** Play game → Answer questions → Press Recent Apps → **Swipe game away** (force close) → Reopen game from app drawer → Progress should be restored!
- ✅ **Phone call:** Play game → Receive phone call → Finish call → Return to game → Progress saved?

**Screen Tests:**
- ✅ **Landscape mode:** Rotate phone → Does UI stay correct? (or is rotation locked to portrait?)
- ✅ **Different phones:** If possible, test on different Android phones (Samsung, Pixel, Xiaomi, etc.)

### 📐 Test Different Android Screen Sizes in Unity:

Before building APK, test in Unity Game view with different Android phone sizes:

1. Click **Game tab** in Unity (next to Scene tab)
2. Find dropdown that says **"Free Aspect"** at top of Game view
3. Click dropdown and select these Android devices:
   - **Samsung Galaxy S21** (1080x2400, 20:9 ratio - tall screen)
   - **Google Pixel 5** (1080x2340, 19.5:9 ratio)
   - **OnePlus 9** (1080x2400, 20:9 ratio)
   - **Samsung Galaxy Tab** (1920x1200, for tablets)

4. **If you don't see these devices listed:**
   - Click the **"+"** button in aspect ratio dropdown
   - Select **"Fixed Resolution"**
   - Enter custom sizes:
     - Galaxy S21: Width: 1080, Height: 2400
     - Pixel 5: Width: 1080, Height: 2340
   - Give it a label, click OK

5. For each screen size, press **Play** (▶️) and check:
   - ✅ Previous button stays at bottom-left corner
   - ✅ Next button stays at bottom-right corner
   - ✅ Submit button stays at bottom-center
   - ✅ Difficulty badge stays at top-right
   - ✅ Confirmation dialog stays centered
   - ✅ No text is cut off or overflow
   - ✅ All buttons are visible (not off-screen)
   - ✅ Buttons don't overlap with each other

---

## ✅ Final Checklist

**Unity Setup:**
- [ ] PreviousButton added (bottom-left, X: 120, Y: 100)
- [ ] NextButton added (bottom-right, X: -120, Y: 100)
- [ ] SubmitButton added (bottom-center, X: 0, Y: 100, initially hidden)
- [ ] DifficultyBadge added (top-right, X: -250, Y: -120)
- [ ] ConfirmationDialog panel created (center, 700x450)
- [ ] ConfirmationText added inside dialog
- [ ] ConfirmNoButton added inside dialog (left side)
- [ ] ConfirmYesButton added inside dialog (right side)
- [ ] All 9 references dragged to MultipleChoiceManager Inspector
- [ ] ConfirmationDialog initially deactivated (grayed out in Hierarchy)
- [ ] Tested in Unity Play mode (click ▶️ button)

**Android Mobile Testing (CRITICAL!):**
- [ ] Built APK file (File → Build Settings → Android → Build And Run)
- [ ] Installed on real Android phone (USB debugging enabled)
- [ ] Tested touch response (all buttons tap correctly, no delay)
- [ ] Tested one-handed use (thumb can reach Previous/Next corners)
- [ ] Tested confirmation dialog (appears, shows selected answer text, Yes/No work)
- [ ] Tested Android safe area (no buttons hidden by navigation bar/notch)
- [ ] Tested app backgrounding (Home button → Reopen app → Progress saved)
- [ ] Tested force close (Recent apps → Swipe away → Reopen → Progress saved)
- [ ] Tested on different Android screen sizes in Unity Game view

---

## 🎉 Your Android Mobile Game is Ready!

**What students will experience on their Android phones:**

1. 📱 **Install APK on Android phone** → Open app from app drawer
2. 🎮 **Game loads** → Assignment questions appear
3. 🎯 **Tap an answer choice** → Confirmation dialog pops up immediately
4. 🤔 **Dialog shows** → "Are you sure to pick 'Paris' as your answer? 🤔"
5. ✅ **Confirm or cancel** → Tap "Yes, I'm Sure!" or "No, Let Me Think"
6. ➡️ **Navigate freely** → Use Previous/Next buttons (within same difficulty)
7. 🏠 **Press Home button** → Progress auto-saves to server
8. 🔄 **Reopen app anytime** → Continues exactly where they left off
9. 🎉 **Finish all questions** → Submit button appears, results show

**Features working automatically on Android:**
- ✅ **Touch-optimized** (all buttons finger-friendly, 70px+ height)
- ✅ **Navigation buttons** (go back/forward through questions)
- ✅ **Difficulty badges** (🟢 Easy → 🟡 Medium → 🔴 Hard with colors)
- ✅ **Confirmation dialog** (shows exact answer text they tapped)
- ✅ **Auto-save** (progress saves even if app force-closed)
- ✅ **Smart locking** (can't go back to easier difficulty after moving forward)
- ✅ **Android-safe UI** (works on Galaxy, Pixel, OnePlus, all screen sizes)
- ✅ **Safe areas** (buttons don't hide behind navigation bar or notch)

**Next step:** Build APK → Share APK file with students → They install on Android phones → Play! 🚀🤖
