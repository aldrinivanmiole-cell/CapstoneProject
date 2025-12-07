# Unity Implementation Guide - Enhanced Assignment Features

## 🎮 Overview
This guide will help you implement all 5 enhanced features in your Unity app:
1. ✅ Difficulty levels display
2. ✅ Hidden results until completion
3. ✅ Child-friendly confirmation dialog
4. ✅ Auto-save & progress recovery (using PlayerPrefs)
5. ✅ Smart navigation with difficulty-based restrictions

---

## 📋 Prerequisites

### Backend Setup:
1. Run the migration script:
```bash
cd CapstoneProject
python migrate_add_progress_table.py
```

2. Restart your Flask server to load new API endpoints

### Unity Setup:
- Unity 2020.3 or later
- JSON parsing library (Unity's built-in JsonUtility or Newtonsoft.Json)
- UI Toolkit or Legacy UI system

---

## 🗂️ Project Structure

Create these folders in your Unity project:
```
Assets/
├── Scripts/
│   ├── API/
│   │   ├── APIManager.cs
│   │   └── AssignmentAPI.cs
│   ├── Models/
│   │   ├── Question.cs
│   │   ├── AssignmentProgress.cs
│   │   └── DifficultyLevel.cs
│   ├── Managers/
│   │   ├── AssignmentManager.cs
│   │   ├── ProgressManager.cs
│   │   └── NavigationManager.cs
│   └── UI/
│       ├── QuestionDisplay.cs
│       ├── ConfirmationDialog.cs
│       └── NavigationDots.cs
└── Prefabs/
    ├── ConfirmationDialog.prefab
    ├── QuestionPanel.prefab
    └── NavigationDot.prefab
```

---

## 📝 Step-by-Step Implementation

### Step 1: Update Data Models

Create `Assets/Scripts/Models/Question.cs`:
```csharp
using System;
using System.Collections.Generic;

[Serializable]
public class Question
{
    public int id;
    public string question_text;
    public string question_type;
    public int points;
    public string help_video_url;
    public string difficulty; // NEW: "easy", "medium", "hard"
    public string[] options;
    public int correct_answer_index;
}

[Serializable]
public class QuestionListResponse
{
    public string status;
    public AssignmentInfo assignment;
    public List<Question> questions;
}

[Serializable]
public class AssignmentInfo
{
    public int id;
    public string title;
    public int total_points;
    public int question_count;
}
```

Create `Assets/Scripts/Models/DifficultyLevel.cs`:
```csharp
using UnityEngine;

public enum Difficulty
{
    Easy,
    Medium,
    Hard
}

public static class DifficultyHelper
{
    public static Difficulty ParseDifficulty(string difficultyString)
    {
        switch (difficultyString?.ToLower())
        {
            case "easy":
                return Difficulty.Easy;
            case "medium":
                return Difficulty.Medium;
            case "hard":
                return Difficulty.Hard;
            default:
                return Difficulty.Easy;
        }
    }

    public static Color GetDifficultyColor(Difficulty difficulty)
    {
        switch (difficulty)
        {
            case Difficulty.Easy:
                return new Color(0.2f, 0.8f, 0.2f); // Green
            case Difficulty.Medium:
                return new Color(1f, 0.8f, 0f); // Yellow
            case Difficulty.Hard:
                return new Color(1f, 0.2f, 0.2f); // Red
            default:
                return Color.white;
        }
    }

    public static string GetDifficultyEmoji(Difficulty difficulty)
    {
        switch (difficulty)
        {
            case Difficulty.Easy:
                return "😊";
            case Difficulty.Medium:
                return "🤔";
            case Difficulty.Hard:
                return "🔥";
            default:
                return "";
        }
    }

    public static string GetDifficultyText(Difficulty difficulty)
    {
        return difficulty.ToString() + " " + GetDifficultyEmoji(difficulty);
    }
}
```

Create `Assets/Scripts/Models/AssignmentProgress.cs`:
```csharp
using System;
using System.Collections.Generic;

[Serializable]
public class AssignmentProgress
{
    public int currentQuestionIndex;
    public Dictionary<int, string> answers; // questionId -> answer
    public List<int> lockedQuestions;
    public long timestamp;

    public AssignmentProgress()
    {
        currentQuestionIndex = 0;
        answers = new Dictionary<int, string>();
        lockedQuestions = new List<int>();
        timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
    }
}

[Serializable]
public class ProgressSaveRequest
{
    public int student_id;
    public int current_question_index;
    public Dictionary<string, string> answers; // questionId as string -> answer
    public int[] locked_questions;
}

[Serializable]
public class ProgressResponse
{
    public string status;
    public bool has_progress;
    public bool submitted;
    public string message;
    public ProgressData progress;
}

[Serializable]
public class ProgressData
{
    public int current_question_index;
    public Dictionary<string, string> answers;
    public int[] locked_questions;
    public string last_updated;
}
```

---

### Step 2: Create Progress Manager

Create `Assets/Scripts/Managers/ProgressManager.cs`:
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class ProgressManager : MonoBehaviour
{
    private const string PROGRESS_KEY_PREFIX = "assignment_progress_";
    
    public static ProgressManager Instance { get; private set; }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    // Save progress locally (PlayerPrefs)
    public void SaveProgressLocal(int assignmentId, int studentId, AssignmentProgress progress)
    {
        string key = GetProgressKey(assignmentId, studentId);
        string json = JsonUtility.ToJson(progress);
        PlayerPrefs.SetString(key, json);
        PlayerPrefs.Save();
        
        Debug.Log($"Progress saved locally for assignment {assignmentId}");
    }

    // Load progress from PlayerPrefs
    public AssignmentProgress LoadProgressLocal(int assignmentId, int studentId)
    {
        string key = GetProgressKey(assignmentId, studentId);
        
        if (PlayerPrefs.HasKey(key))
        {
            string json = PlayerPrefs.GetString(key);
            AssignmentProgress progress = JsonUtility.FromJson<AssignmentProgress>(json);
            Debug.Log($"Progress loaded from PlayerPrefs for assignment {assignmentId}");
            return progress;
        }
        
        return null;
    }

    // Clear progress after submission
    public void ClearProgress(int assignmentId, int studentId)
    {
        string key = GetProgressKey(assignmentId, studentId);
        PlayerPrefs.DeleteKey(key);
        PlayerPrefs.Save();
        
        Debug.Log($"Progress cleared for assignment {assignmentId}");
    }

    // Save progress to server
    public void SaveProgressServer(int assignmentId, int studentId, AssignmentProgress progress, System.Action<bool> callback)
    {
        StartCoroutine(AssignmentAPI.Instance.SaveProgress(assignmentId, studentId, progress, callback));
    }

    // Load progress from server
    public void LoadProgressServer(int assignmentId, int studentId, System.Action<ProgressResponse> callback)
    {
        StartCoroutine(AssignmentAPI.Instance.GetProgress(assignmentId, studentId, callback));
    }

    private string GetProgressKey(int assignmentId, int studentId)
    {
        return $"{PROGRESS_KEY_PREFIX}{assignmentId}_{studentId}";
    }
}
```

---

### Step 3: Create API Manager

Create `Assets/Scripts/API/AssignmentAPI.cs`:
```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using System.Text;

public class AssignmentAPI : MonoBehaviour
{
    public static AssignmentAPI Instance { get; private set; }
    
    private string baseURL = "http://your-server.com"; // CHANGE THIS

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    // Get assignment questions with difficulty
    public IEnumerator GetAssignment(int assignmentId, System.Action<QuestionListResponse> callback)
    {
        string url = $"{baseURL}/assignment/{assignmentId}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string json = request.downloadHandler.text;
                QuestionListResponse response = JsonUtility.FromJson<QuestionListResponse>(json);
                callback?.Invoke(response);
            }
            else
            {
                Debug.LogError($"Error getting assignment: {request.error}");
                callback?.Invoke(null);
            }
        }
    }

    // Save progress to server
    public IEnumerator SaveProgress(int assignmentId, int studentId, AssignmentProgress progress, System.Action<bool> callback)
    {
        string url = $"{baseURL}/assignment/{assignmentId}/save_progress";
        
        // Convert to server format
        ProgressSaveRequest saveRequest = new ProgressSaveRequest
        {
            student_id = studentId,
            current_question_index = progress.currentQuestionIndex,
            answers = progress.answers.ToDictionary(k => k.Key.ToString(), v => v.Value),
            locked_questions = progress.lockedQuestions.ToArray()
        };
        
        string jsonData = JsonUtility.ToJson(saveRequest);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();

            bool success = request.result == UnityWebRequest.Result.Success;
            if (success)
            {
                Debug.Log("Progress saved to server");
            }
            else
            {
                Debug.LogError($"Error saving progress: {request.error}");
            }
            
            callback?.Invoke(success);
        }
    }

    // Get progress from server
    public IEnumerator GetProgress(int assignmentId, int studentId, System.Action<ProgressResponse> callback)
    {
        string url = $"{baseURL}/assignment/{assignmentId}/get_progress?student_id={studentId}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string json = request.downloadHandler.text;
                ProgressResponse response = JsonUtility.FromJson<ProgressResponse>(json);
                callback?.Invoke(response);
            }
            else
            {
                Debug.LogError($"Error getting progress: {request.error}");
                callback?.Invoke(null);
            }
        }
    }

    // Submit assignment (clears progress automatically)
    public IEnumerator SubmitAssignment(int assignmentId, int studentId, Dictionary<int, string> answers, System.Action<bool, string> callback)
    {
        string url = $"{baseURL}/submit/{assignmentId}";
        
        // Convert answers dictionary to server format
        var answersDict = new Dictionary<string, string>();
        foreach (var kvp in answers)
        {
            answersDict[kvp.Key.ToString()] = kvp.Value;
        }
        
        var submitData = new
        {
            student_id = studentId,
            answers = answersDict
        };
        
        string jsonData = JsonUtility.ToJson(submitData);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Assignment submitted successfully");
                callback?.Invoke(true, request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"Error submitting assignment: {request.error}");
                callback?.Invoke(false, request.error);
            }
        }
    }
}
```

---

### Step 4: Create Assignment Manager with All Features

Create `Assets/Scripts/Managers/AssignmentManager.cs`:
```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;
using TMPro;

public class AssignmentManager : MonoBehaviour
{
    [Header("References")]
    public Transform questionContainer;
    public GameObject questionPrefab;
    public ConfirmationDialog confirmationDialog;
    public NavigationDots navigationDots;
    public TextMeshProUGUI saveStatusText;
    public Image saveStatusIcon;
    
    [Header("Navigation Buttons")]
    public Button previousButton;
    public Button nextButton;
    public Button finishButton;
    
    [Header("Settings")]
    public int assignmentId;
    public int studentId;
    
    private List<Question> questions = new List<Question>();
    private int currentQuestionIndex = 0;
    private Dictionary<int, string> userAnswers = new Dictionary<int, string>();
    private HashSet<int> lockedQuestions = new HashSet<int>();
    private Dictionary<int, Difficulty> questionDifficulties = new Dictionary<int, Difficulty>();
    private Dictionary<Difficulty, List<int>> difficultyRanges = new Dictionary<Difficulty, List<int>>();
    
    private GameObject[] questionObjects;
    private string pendingAnswer;
    private int pendingQuestionIndex;

    void Start()
    {
        // Initialize difficulty ranges
        difficultyRanges[Difficulty.Easy] = new List<int>();
        difficultyRanges[Difficulty.Medium] = new List<int>();
        difficultyRanges[Difficulty.Hard] = new List<int>();
        
        LoadAssignment();
    }

    void LoadAssignment()
    {
        StartCoroutine(AssignmentAPI.Instance.GetAssignment(assignmentId, (response) =>
        {
            if (response != null && response.status == "success")
            {
                questions = response.questions;
                InitializeQuestions();
                LoadProgress();
            }
            else
            {
                Debug.LogError("Failed to load assignment");
            }
        }));
    }

    void InitializeQuestions()
    {
        questionObjects = new GameObject[questions.Count];
        
        for (int i = 0; i < questions.Count; i++)
        {
            Question q = questions[i];
            
            // Parse difficulty
            Difficulty diff = DifficultyHelper.ParseDifficulty(q.difficulty);
            questionDifficulties[i] = diff;
            difficultyRanges[diff].Add(i);
            
            // Create question UI
            GameObject questionObj = Instantiate(questionPrefab, questionContainer);
            questionObj.SetActive(false);
            questionObjects[i] = questionObj;
            
            // Setup question display
            QuestionDisplay display = questionObj.GetComponent<QuestionDisplay>();
            if (display != null)
            {
                display.Setup(q, i, OnAnswerSelected);
            }
        }
        
        // Setup navigation
        navigationDots.Initialize(questions.Count, OnNavigationDotClicked);
        
        // Show first question
        ShowQuestion(0);
    }

    void LoadProgress()
    {
        // Try loading from PlayerPrefs first (local)
        AssignmentProgress localProgress = ProgressManager.Instance.LoadProgressLocal(assignmentId, studentId);
        
        // Then try from server
        ProgressManager.Instance.LoadProgressServer(assignmentId, studentId, (response) =>
        {
            if (response != null && response.has_progress && !response.submitted)
            {
                // Use server progress if available
                RestoreProgress(response.progress);
            }
            else if (localProgress != null)
            {
                // Fallback to local progress
                RestoreProgressLocal(localProgress);
            }
            else
            {
                // No progress found, start fresh
                Debug.Log("No saved progress found, starting fresh");
            }
        });
    }

    void RestoreProgress(ProgressData progressData)
    {
        currentQuestionIndex = progressData.current_question_index;
        
        // Restore answers
        foreach (var kvp in progressData.answers)
        {
            if (int.TryParse(kvp.Key, out int questionId))
            {
                userAnswers[questionId] = kvp.Value;
            }
        }
        
        // Restore locked questions
        if (progressData.locked_questions != null)
        {
            foreach (int index in progressData.locked_questions)
            {
                lockedQuestions.Add(index);
            }
        }
        
        ShowQuestion(currentQuestionIndex);
        navigationDots.UpdateNavigation(currentQuestionIndex, userAnswers.Keys.ToList(), lockedQuestions.ToList());
        
        ShowSaveStatus("Progress restored", true);
        Debug.Log($"Progress restored: Q{currentQuestionIndex + 1}, {userAnswers.Count} answers");
    }

    void RestoreProgressLocal(AssignmentProgress progress)
    {
        currentQuestionIndex = progress.currentQuestionIndex;
        userAnswers = new Dictionary<int, string>(progress.answers);
        lockedQuestions = new HashSet<int>(progress.lockedQuestions);
        
        ShowQuestion(currentQuestionIndex);
        navigationDots.UpdateNavigation(currentQuestionIndex, userAnswers.Keys.ToList(), lockedQuestions.ToList());
        
        ShowSaveStatus("Progress restored (local)", true);
    }

    void ShowQuestion(int index)
    {
        // Hide all questions
        foreach (GameObject obj in questionObjects)
        {
            obj.SetActive(false);
        }
        
        // Show current question
        if (index >= 0 && index < questionObjects.Length)
        {
            questionObjects[index].SetActive(true);
            currentQuestionIndex = index;
            
            // Update navigation buttons
            UpdateNavigationButtons();
            
            // Update navigation dots
            navigationDots.UpdateNavigation(currentQuestionIndex, userAnswers.Keys.ToList(), lockedQuestions.ToList());
        }
    }

    void UpdateNavigationButtons()
    {
        // Previous button
        Difficulty currentDiff = questionDifficulties[currentQuestionIndex];
        List<int> currentDiffQuestions = difficultyRanges[currentDiff];
        int positionInDiff = currentDiffQuestions.IndexOf(currentQuestionIndex);
        
        previousButton.interactable = positionInDiff > 0;
        
        // Next/Finish buttons
        bool isLastQuestion = currentQuestionIndex == questions.Count - 1;
        bool hasAnswer = userAnswers.ContainsKey(questions[currentQuestionIndex].id);
        
        nextButton.gameObject.SetActive(!isLastQuestion && hasAnswer);
        finishButton.gameObject.SetActive(isLastQuestion && hasAnswer);
    }

    public void OnAnswerSelected(int questionIndex, string answer)
    {
        // Store pending answer
        pendingAnswer = answer;
        pendingQuestionIndex = questionIndex;
        
        // Show confirmation dialog
        confirmationDialog.Show("Do you want to pick this answer? 🤔", 
            "Think carefully before you choose!", 
            OnConfirmAnswer, 
            OnCancelAnswer);
    }

    void OnConfirmAnswer()
    {
        int questionId = questions[pendingQuestionIndex].id;
        userAnswers[questionId] = pendingAnswer;
        
        // Lock previous difficulties if moving to new difficulty
        LockPreviousDifficulties(pendingQuestionIndex);
        
        // Save progress
        SaveProgress();
        
        // Update UI
        UpdateNavigationButtons();
        navigationDots.UpdateNavigation(currentQuestionIndex, userAnswers.Keys.ToList(), lockedQuestions.ToList());
        
        ShowSaveStatus("Progress saved", true);
    }

    void OnCancelAnswer()
    {
        // User cancelled, do nothing
        Debug.Log("Answer cancelled");
    }

    void LockPreviousDifficulties(int currentIndex)
    {
        Difficulty currentDiff = questionDifficulties[currentIndex];
        List<int> currentDiffQuestions = difficultyRanges[currentDiff];
        bool isLastInDifficulty = currentDiffQuestions.IndexOf(currentIndex) == currentDiffQuestions.Count - 1;
        
        if (isLastInDifficulty)
        {
            // Lock all questions in previous difficulties
            for (int i = 0; i < currentIndex; i++)
            {
                if (questionDifficulties[i] != currentDiff)
                {
                    lockedQuestions.Add(i);
                }
            }
        }
    }

    void SaveProgress()
    {
        AssignmentProgress progress = new AssignmentProgress
        {
            currentQuestionIndex = currentQuestionIndex,
            answers = new Dictionary<int, string>(userAnswers),
            lockedQuestions = lockedQuestions.ToList()
        };
        
        // Save locally (instant)
        ProgressManager.Instance.SaveProgressLocal(assignmentId, studentId, progress);
        
        // Save to server (async)
        ProgressManager.Instance.SaveProgressServer(assignmentId, studentId, progress, (success) =>
        {
            if (success)
            {
                ShowSaveStatus("Saved to cloud", true);
            }
            else
            {
                ShowSaveStatus("Saved locally", false);
            }
        });
    }

    void ShowSaveStatus(string message, bool success)
    {
        saveStatusText.text = message;
        saveStatusIcon.color = success ? Color.green : Color.yellow;
        
        // Auto-hide after 2 seconds
        CancelInvoke("HideSaveStatus");
        Invoke("HideSaveStatus", 2f);
    }

    void HideSaveStatus()
    {
        saveStatusText.text = "";
    }

    public void OnPreviousButtonClicked()
    {
        Difficulty currentDiff = questionDifficulties[currentQuestionIndex];
        List<int> currentDiffQuestions = difficultyRanges[currentDiff];
        int positionInDiff = currentDiffQuestions.IndexOf(currentQuestionIndex);
        
        if (positionInDiff > 0)
        {
            int previousIndex = currentDiffQuestions[positionInDiff - 1];
            ShowQuestion(previousIndex);
        }
        else
        {
            ShowMessage("You cannot go back to previous difficulty level! 🔒");
        }
    }

    public void OnNextButtonClicked()
    {
        int questionId = questions[currentQuestionIndex].id;
        
        if (!userAnswers.ContainsKey(questionId))
        {
            ShowMessage("Please provide an answer before moving forward! 📝");
            return;
        }
        
        if (currentQuestionIndex < questions.Count - 1)
        {
            currentQuestionIndex++;
            ShowQuestion(currentQuestionIndex);
            LockPreviousDifficulties(currentQuestionIndex);
        }
    }

    public void OnFinishButtonClicked()
    {
        int answeredCount = userAnswers.Count;
        int totalQuestions = questions.Count;
        
        if (answeredCount < totalQuestions)
        {
            ShowConfirmSubmit($"You've only answered {answeredCount} out of {totalQuestions} questions. Submit anyway?");
        }
        else
        {
            SubmitAssignment();
        }
    }

    void ShowConfirmSubmit(string message)
    {
        confirmationDialog.Show("Submit Assignment?", message, SubmitAssignment, null);
    }

    void SubmitAssignment()
    {
        ShowSaveStatus("Submitting...", true);
        
        StartCoroutine(AssignmentAPI.Instance.SubmitAssignment(assignmentId, studentId, userAnswers, (success, response) =>
        {
            if (success)
            {
                // Clear progress
                ProgressManager.Instance.ClearProgress(assignmentId, studentId);
                
                // Show results
                ShowResults(response);
            }
            else
            {
                ShowMessage("Error submitting assignment. Please try again.");
            }
        }));
    }

    void OnNavigationDotClicked(int index)
    {
        if (lockedQuestions.Contains(index))
        {
            ShowMessage("This question is locked! You can only go back within the same difficulty level. 🔒");
            return;
        }
        
        Difficulty currentDiff = questionDifficulties[currentQuestionIndex];
        Difficulty targetDiff = questionDifficulties[index];
        
        if (currentDiff != targetDiff)
        {
            ShowMessage("You can only navigate within the same difficulty level! 🔒");
            return;
        }
        
        ShowQuestion(index);
    }

    void ShowMessage(string message)
    {
        // Implement your message display (e.g., Toast, Dialog, etc.)
        Debug.Log(message);
    }

    void ShowResults(string jsonResponse)
    {
        // Parse and display results
        // You can create a Results scene or panel for this
        Debug.Log("Assignment completed! Results: " + jsonResponse);
    }

    void OnApplicationPause(bool paused)
    {
        if (paused)
        {
            // Auto-save when app goes to background
            SaveProgress();
        }
    }

    void OnApplicationQuit()
    {
        // Auto-save when app closes
        SaveProgress();
    }
}
```

---

**(Continued in next message...)**
