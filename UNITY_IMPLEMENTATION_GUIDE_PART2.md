# Unity Implementation Guide - Part 2: UI Components

## Step 5: Create Confirmation Dialog

Create `Assets/Scripts/UI/ConfirmationDialog.cs`:
```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

public class ConfirmationDialog : MonoBehaviour
{
    [Header("UI References")]
    public GameObject dialogPanel;
    public TextMeshProUGUI titleText;
    public TextMeshProUGUI messageText;
    public Button confirmButton;
    public Button cancelButton;
    public TextMeshProUGUI confirmButtonText;
    public TextMeshProUGUI cancelButtonText;
    
    private Action onConfirmAction;
    private Action onCancelAction;

    void Start()
    {
        // Setup button listeners
        confirmButton.onClick.AddListener(OnConfirmClicked);
        cancelButton.onClick.AddListener(OnCancelClicked);
        
        // Hide by default
        Hide();
    }

    public void Show(string title, string message, Action onConfirm, Action onCancel = null)
    {
        titleText.text = title;
        messageText.text = message;
        onConfirmAction = onConfirm;
        onCancelAction = onCancel;
        
        // Set child-friendly button texts
        confirmButtonText.text = "Yes, I'm sure! ✓";
        cancelButtonText.text = "Let me think more";
        
        dialogPanel.SetActive(true);
        
        // Optional: Add animation
        AnimateIn();
    }

    public void Hide()
    {
        dialogPanel.SetActive(false);
        onConfirmAction = null;
        onCancelAction = null;
    }

    void OnConfirmClicked()
    {
        onConfirmAction?.Invoke();
        Hide();
    }

    void OnCancelClicked()
    {
        onCancelAction?.Invoke();
        Hide();
    }

    void AnimateIn()
    {
        // Optional: Add scale or fade animation
        dialogPanel.transform.localScale = Vector3.zero;
        LeanTween.scale(dialogPanel, Vector3.one, 0.3f).setEaseOutBack();
    }

    // Close dialog when ESC key is pressed
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape) && dialogPanel.activeSelf)
        {
            OnCancelClicked();
        }
    }
}
```

---

## Step 6: Create Navigation Dots

Create `Assets/Scripts/UI/NavigationDots.cs`:
```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;

public class NavigationDots : MonoBehaviour
{
    [Header("Prefab")]
    public GameObject dotPrefab;
    
    [Header("Container")]
    public Transform dotsContainer;
    
    [Header("Colors")]
    public Color defaultColor = Color.white;
    public Color answeredColor = new Color(0.82f, 0.93f, 0.95f); // Light blue
    public Color currentColor = new Color(0.05f, 0.79f, 0.94f); // Blue
    public Color lockedColor = new Color(0.7f, 0.7f, 0.7f); // Gray
    
    private List<NavigationDot> dots = new List<NavigationDot>();
    private System.Action<int> onDotClickedCallback;

    public void Initialize(int questionCount, System.Action<int> onDotClicked)
    {
        onDotClickedCallback = onDotClicked;
        
        // Clear existing dots
        foreach (Transform child in dotsContainer)
        {
            Destroy(child.gameObject);
        }
        dots.Clear();
        
        // Create dots
        for (int i = 0; i < questionCount; i++)
        {
            GameObject dotObj = Instantiate(dotPrefab, dotsContainer);
            NavigationDot dot = dotObj.GetComponent<NavigationDot>();
            
            if (dot == null)
            {
                dot = dotObj.AddComponent<NavigationDot>();
            }
            
            int index = i; // Capture for lambda
            dot.Initialize(i + 1, () => OnDotClicked(index));
            dots.Add(dot);
        }
    }

    public void UpdateNavigation(int currentIndex, List<int> answeredQuestionIds, List<int> lockedIndices)
    {
        HashSet<int> answeredSet = new HashSet<int>(answeredQuestionIds);
        HashSet<int> lockedSet = new HashSet<int>(lockedIndices);
        
        for (int i = 0; i < dots.Count; i++)
        {
            NavigationDot dot = dots[i];
            
            if (i == currentIndex)
            {
                // Current question
                dot.SetState(NavigationDotState.Current, currentColor);
            }
            else if (lockedSet.Contains(i))
            {
                // Locked question
                dot.SetState(NavigationDotState.Locked, lockedColor);
            }
            else if (answeredSet.Contains(i))
            {
                // Answered question
                dot.SetState(NavigationDotState.Answered, answeredColor);
            }
            else
            {
                // Default (not answered)
                dot.SetState(NavigationDotState.Default, defaultColor);
            }
        }
    }

    void OnDotClicked(int index)
    {
        onDotClickedCallback?.Invoke(index);
    }
}

public enum NavigationDotState
{
    Default,
    Answered,
    Current,
    Locked
}

public class NavigationDot : MonoBehaviour
{
    public TextMeshProUGUI numberText;
    public Image background;
    public Button button;
    public GameObject lockIcon;
    
    private int questionNumber;
    private System.Action onClickAction;
    private NavigationDotState currentState;

    void Awake()
    {
        if (numberText == null)
            numberText = GetComponentInChildren<TextMeshProUGUI>();
        if (background == null)
            background = GetComponent<Image>();
        if (button == null)
            button = GetComponent<Button>();
        if (lockIcon == null)
            lockIcon = transform.Find("LockIcon")?.gameObject;
    }

    public void Initialize(int number, System.Action onClick)
    {
        questionNumber = number;
        onClickAction = onClick;
        
        if (numberText != null)
            numberText.text = number.ToString();
        
        if (button != null)
            button.onClick.AddListener(OnClicked);
        
        if (lockIcon != null)
            lockIcon.SetActive(false);
    }

    public void SetState(NavigationDotState state, Color color)
    {
        currentState = state;
        
        if (background != null)
            background.color = color;
        
        if (button != null)
            button.interactable = state != NavigationDotState.Locked;
        
        if (lockIcon != null)
            lockIcon.SetActive(state == NavigationDotState.Locked);
        
        // Scale effect for current question
        if (state == NavigationDotState.Current)
        {
            transform.localScale = Vector3.one * 1.15f;
        }
        else
        {
            transform.localScale = Vector3.one;
        }
    }

    void OnClicked()
    {
        if (currentState != NavigationDotState.Locked)
        {
            onClickAction?.Invoke();
        }
    }
}
```

---

## Step 7: Create Question Display

Create `Assets/Scripts/UI/QuestionDisplay.cs`:
```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

public class QuestionDisplay : MonoBehaviour
{
    [Header("Question Info")]
    public TextMeshProUGUI questionNumberText;
    public TextMeshProUGUI questionText;
    public TextMeshProUGUI pointsText;
    public Image difficultyBadge;
    public TextMeshProUGUI difficultyText;
    
    [Header("Help Video")]
    public GameObject helpVideoPanel;
    public Button helpVideoButton;
    
    [Header("Answer Options")]
    public Transform optionsContainer;
    public GameObject optionButtonPrefab;
    public TMP_InputField inputField; // For text-based questions
    
    private Question question;
    private int questionIndex;
    private Action<int, string> onAnswerSelectedCallback;
    private Toggle[] optionToggles;

    public void Setup(Question q, int index, Action<int, string> onAnswerSelected)
    {
        question = q;
        questionIndex = index;
        onAnswerSelectedCallback = onAnswerSelected;
        
        // Display question info
        if (questionNumberText != null)
            questionNumberText.text = $"Question {index + 1}";
        
        if (questionText != null)
            questionText.text = q.question_text;
        
        if (pointsText != null)
            pointsText.text = $"{q.points} point{(q.points != 1 ? "s" : "")}";
        
        // Setup difficulty badge
        Difficulty diff = DifficultyHelper.ParseDifficulty(q.difficulty);
        if (difficultyBadge != null)
            difficultyBadge.color = DifficultyHelper.GetDifficultyColor(diff);
        
        if (difficultyText != null)
            difficultyText.text = DifficultyHelper.GetDifficultyText(diff);
        
        // Setup help video
        if (helpVideoPanel != null)
        {
            helpVideoPanel.SetActive(!string.IsNullOrEmpty(q.help_video_url));
            if (helpVideoButton != null && !string.IsNullOrEmpty(q.help_video_url))
            {
                helpVideoButton.onClick.AddListener(() => OpenHelpVideo(q.help_video_url));
            }
        }
        
        // Setup answer input based on question type
        SetupAnswerInput();
    }

    void SetupAnswerInput()
    {
        // Clear existing options
        foreach (Transform child in optionsContainer)
        {
            Destroy(child.gameObject);
        }
        
        switch (question.question_type)
        {
            case "multiple_choice":
            case "yes_no":
                SetupMultipleChoice();
                break;
            
            case "identification":
            case "problem_solving":
            case "enumeration":
                SetupTextInput();
                break;
            
            case "essay":
                SetupEssayInput();
                break;
            
            default:
                Debug.LogWarning($"Unknown question type: {question.question_type}");
                break;
        }
    }

    void SetupMultipleChoice()
    {
        if (inputField != null)
            inputField.gameObject.SetActive(false);
        
        optionsContainer.gameObject.SetActive(true);
        
        if (question.options == null || question.options.Length == 0)
        {
            Debug.LogError("No options provided for multiple choice question");
            return;
        }
        
        ToggleGroup toggleGroup = optionsContainer.GetComponent<ToggleGroup>();
        if (toggleGroup == null)
            toggleGroup = optionsContainer.gameObject.AddComponent<ToggleGroup>();
        
        optionToggles = new Toggle[question.options.Length];
        
        for (int i = 0; i < question.options.Length; i++)
        {
            GameObject optionObj = Instantiate(optionButtonPrefab, optionsContainer);
            
            Toggle toggle = optionObj.GetComponent<Toggle>();
            if (toggle == null)
                toggle = optionObj.AddComponent<Toggle>();
            
            toggle.group = toggleGroup;
            optionToggles[i] = toggle;
            
            TextMeshProUGUI optionText = optionObj.GetComponentInChildren<TextMeshProUGUI>();
            if (optionText != null)
                optionText.text = question.options[i];
            
            string answer = question.options[i];
            toggle.onValueChanged.AddListener((bool isOn) =>
            {
                if (isOn)
                {
                    OnAnswerSelected(answer);
                }
            });
            
            // Add hover effect
            AddHoverEffect(optionObj);
        }
    }

    void SetupTextInput()
    {
        optionsContainer.gameObject.SetActive(false);
        
        if (inputField != null)
        {
            inputField.gameObject.SetActive(true);
            inputField.contentType = TMP_InputField.ContentType.Standard;
            inputField.lineType = TMP_InputField.LineType.SingleLine;
            inputField.placeholder.GetComponent<TextMeshProUGUI>().text = "Enter your answer";
            
            inputField.onEndEdit.AddListener((string answer) =>
            {
                if (!string.IsNullOrEmpty(answer))
                {
                    OnAnswerSelected(answer);
                }
            });
        }
    }

    void SetupEssayInput()
    {
        optionsContainer.gameObject.SetActive(false);
        
        if (inputField != null)
        {
            inputField.gameObject.SetActive(true);
            inputField.contentType = TMP_InputField.ContentType.Standard;
            inputField.lineType = TMP_InputField.LineType.MultiLineNewline;
            inputField.placeholder.GetComponent<TextMeshProUGUI>().text = "Write your essay here...";
            
            inputField.onEndEdit.AddListener((string answer) =>
            {
                if (!string.IsNullOrEmpty(answer))
                {
                    OnAnswerSelected(answer);
                }
            });
        }
    }

    void OnAnswerSelected(string answer)
    {
        onAnswerSelectedCallback?.Invoke(questionIndex, answer);
    }

    void OpenHelpVideo(string url)
    {
        Application.OpenURL(url);
    }

    void AddHoverEffect(GameObject optionObj)
    {
        // Add hover animation (optional)
        EventTrigger trigger = optionObj.GetComponent<EventTrigger>();
        if (trigger == null)
            trigger = optionObj.AddComponent<EventTrigger>();
        
        // Pointer enter
        EventTrigger.Entry pointerEnter = new EventTrigger.Entry();
        pointerEnter.eventID = EventTriggerType.PointerEnter;
        pointerEnter.callback.AddListener((data) =>
        {
            LeanTween.scale(optionObj, Vector3.one * 1.05f, 0.2f).setEaseOutBack();
        });
        trigger.triggers.Add(pointerEnter);
        
        // Pointer exit
        EventTrigger.Entry pointerExit = new EventTrigger.Entry();
        pointerExit.eventID = EventTriggerType.PointerExit;
        pointerExit.callback.AddListener((data) =>
        {
            LeanTween.scale(optionObj, Vector3.one, 0.2f);
        });
        trigger.triggers.Add(pointerExit);
    }
}
```

---

## Step 8: Create Unity Prefabs

### Confirmation Dialog Prefab:
1. Create a new Canvas GameObject
2. Add Panel child (Background with blur/dark overlay)
3. Add Dialog Panel child with:
   - Header (Gradient background, emoji icon, title text)
   - Body (Message text)
   - Footer with 2 buttons:
     - Cancel Button: "Let me think more"
     - Confirm Button: "Yes, I'm sure!"
4. Attach `ConfirmationDialog` script
5. Assign all references
6. Save as `ConfirmationDialog.prefab`

### Navigation Dot Prefab:
1. Create Button GameObject
2. Add:
   - Circular background Image
   - TextMeshPro number in center
   - Lock icon Image (initially hidden)
3. Attach `NavigationDot` script
4. Assign all references
5. Save as `NavigationDot.prefab`

### Question Panel Prefab:
1. Create Panel GameObject
2. Add:
   - Question header (number, difficulty badge, points)
   - Question text
   - Help video button (optional)
   - Options container (for multiple choice)
   - Input field (for text questions)
3. Attach `QuestionDisplay` script
4. Assign all references
5. Save as `QuestionPanel.prefab`

---

## Step 9: Scene Setup

### Main Assignment Scene:
```
Canvas
├── AssignmentHeader
│   ├── TitleText
│   └── ClassNameText
├── NavigationPanel (Left Side)
│   ├── NavigationTitle
│   ├── DotsContainer (Vertical Layout Group)
│   ├── DifficultyLegend
│   └── SaveStatusPanel
│       ├── SaveIcon (Image)
│       └── SaveStatusText
├── QuestionsContainer (Center)
│   └── (Questions instantiated here)
├── NavigationButtons (Bottom)
│   ├── PreviousButton
│   ├── NextButton
│   └── FinishButton
└── ConfirmationDialog (Initially hidden)
```

### Assign to AssignmentManager:
```csharp
// In Inspector:
- questionContainer: QuestionsContainer transform
- questionPrefab: QuestionPanel prefab
- confirmationDialog: ConfirmationDialog component
- navigationDots: NavigationDots component
- saveStatusText: SaveStatusText
- saveStatusIcon: SaveIcon image
- previousButton: PreviousButton
- nextButton: NextButton
- finishButton: FinishButton
- assignmentId: (Set via code or inspector)
- studentId: (Set via code or inspector)
```

---

## Step 10: Testing Checklist

### Unit Tests:
- [ ] API endpoints respond correctly
- [ ] Progress saves to PlayerPrefs
- [ ] Progress saves to server
- [ ] Progress loads from PlayerPrefs
- [ ] Progress loads from server
- [ ] Difficulty parsing works
- [ ] Navigation locks work correctly

### Integration Tests:
- [ ] Start assignment → see first question
- [ ] Answer question → confirmation appears
- [ ] Confirm answer → answer saved
- [ ] Navigate forward → next question shows
- [ ] Navigate back (same difficulty) → works
- [ ] Navigate back (different difficulty) → blocked
- [ ] Close app → progress saved
- [ ] Reopen app → progress restored
- [ ] Complete assignment → results shown
- [ ] Progress cleared after submission

### UI Tests:
- [ ] Difficulty badges show correct colors
- [ ] Navigation dots update correctly
- [ ] Locked dots are grayed out
- [ ] Current dot is highlighted
- [ ] Confirmation dialog is child-friendly
- [ ] Save status indicator updates
- [ ] Buttons enable/disable appropriately

---

## Step 11: Configuration

### Update APIManager base URL:
```csharp
// In AssignmentAPI.cs, line 8:
private string baseURL = "http://your-actual-server.com";
// OR
private string baseURL = "https://your-domain.com";
```

### Test with different environments:
```csharp
#if UNITY_EDITOR
    private string baseURL = "http://localhost:5000"; // Local testing
#elif DEVELOPMENT_BUILD
    private string baseURL = "http://staging-server.com"; // Staging
#else
    private string baseURL = "https://production-server.com"; // Production
#endif
```

---

## 🎨 Styling Recommendations

### Colors:
- **Easy Badge:** RGB(51, 204, 51) - Green
- **Medium Badge:** RGB(255, 204, 0) - Yellow/Orange
- **Hard Badge:** RGB(255, 51, 51) - Red
- **Current Dot:** RGB(13, 202, 240) - Cyan
- **Answered Dot:** RGB(209, 236, 241) - Light Cyan
- **Locked Dot:** RGB(180, 180, 180) - Gray

### Fonts:
- **Headers:** Bold, 24-32pt
- **Question Text:** Regular, 18-22pt
- **Options:** Regular, 16-18pt
- **Button Text:** Bold, 16-18pt

### Animations:
- Dialog fade in: 0.3s ease-out-back
- Dot scale on current: 1.15x
- Button hover: 1.05x scale
- Save status fade: 2s delay

---

## 🐛 Troubleshooting

### Progress not saving:
1. Check PlayerPrefs path: `PlayerPrefs.GetString("assignment_progress_1_1")`
2. Verify server API is running
3. Check console for errors
4. Ensure student ID is set

### Navigation not locking:
1. Verify difficulty strings match: "easy", "medium", "hard"
2. Check `difficultyRanges` dictionary population
3. Debug `LockPreviousDifficulties` method
4. Ensure questions are properly indexed

### Confirmation not appearing:
1. Check dialog GameObject is in scene
2. Verify dialog panel is initially inactive
3. Ensure callback is set before `Show()`
4. Check Canvas render mode

---

## 📱 Platform-Specific Notes

### Android:
- Use persistent data path for saves
- Handle back button for dialog cancel
- Test with different screen sizes
- Optimize for touch input

### iOS:
- Ensure PlayerPrefs permissions
- Test on different device sizes
- Handle safe areas properly
- Test with poor network

### WebGL:
- Use IndexedDB for persistence
- Handle browser close events
- Test localStorage availability
- CORS configuration needed

---

## ✅ Final Checklist

Before deploying to production:
- [ ] All API endpoints tested
- [ ] Progress save/load works offline
- [ ] Progress save/load works online
- [ ] Server fallback to PlayerPrefs works
- [ ] All difficulty levels display correctly
- [ ] Navigation restrictions enforced
- [ ] Confirmation dialog is child-friendly
- [ ] App pause/resume saves progress
- [ ] Results show after completion
- [ ] Progress cleared after submission
- [ ] Error handling implemented
- [ ] Loading indicators present
- [ ] Tested on target devices
- [ ] Performance is acceptable
- [ ] UI is responsive

---

**🎉 You're all set! The Unity app now has all 5 enhanced features!**
