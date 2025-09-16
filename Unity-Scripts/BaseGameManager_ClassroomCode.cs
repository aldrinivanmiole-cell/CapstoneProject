using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using TMPro;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;

// Simple data classes for classroom integration
[System.Serializable]
public class QuizData
{
    public string title;
    public string class_name;
    public QuestionData[] questions;
}

[System.Serializable]
public class QuestionData
{
    public string question_text;
    public string question_type;
    public string[] options;
    public int correct_answer_index;
}

[System.Serializable]
public class StudentData
{
    public string name;
    public string email;
}

// ENHANCED BaseGameManager with Classroom Integration
// Copy this ENTIRE script to replace your existing BaseGameManager.cs
public abstract class BaseGameManager : MonoBehaviour
{
    [Header("Player & Enemy Transforms")]
    public RectTransform player;
    public RectTransform enemy1;
    public float attackOffset = 100f;
    public float movementSpeed = 2f;
    protected Vector2 originalPos;

    [Header("Player & Enemy Sprites")]
    public Sprite maleSprite;
    public Sprite femaleSprite;
    public Sprite[] enemySprites;
    public Image playerImage;
    public Image enemyImage;

    [Header("Player Speech UI")]
    public GameObject playerSpeechBubble;
    public TMP_Text playerSpeechText;

    [Header("Enemy Speech UI")]
    public GameObject enemySpeechBubble;
    public TMP_Text enemySpeechText;

    [Header("Progress UI")]
    public Slider progressBar;
    public TMP_Text textProgress;
    public GameObject resultPanel;

    [Header("Progress Dialogues")]
    [TextArea] public string dialogueAt0 = "Let's begin the challenge!";
    [TextArea] public string dialogueAt25 = "Good start, keep going!";
    [TextArea] public string dialogueAt50 = "Halfway there!";
    [TextArea] public string dialogueAt75 = "Almost done, stay focused!";
    [TextArea] public string dialogueAt100 = "Congratulations, you did it!";
    public TMP_Text dialogueText;

    [Header("Game Settings")]
    public float passingScorePercentage = 70f;
    public string currentQuestion = "Name 5 programming languages:";
    public bool clearAnswersAfterSubmission = true;
    public float clearDelay = 1f;
    public TMP_Text questionText;

    [Header("Classroom Integration")]
    public bool enableClassroomMode = true;
    public int assignmentId = -1; // Set this to load specific assignment
    public string serverURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public TMP_Text studentNameText;
    public TMP_Text assignmentInfoText;
    public TMP_Text classroomStatusText;

    // Protected variables (shared with child classes)
    protected float progress = 0f;
    protected float maxProgress = 100f;
    protected bool isProcessingAttack = false;
    protected HashSet<string> correctAnswers = new HashSet<string>();
    protected string currentUser = "aldrinivanmiole-cell";
    protected string sessionTime = "2025-09-02 23:01:38";
    
    // Classroom integration variables
    protected QuizData currentAssignment;
    protected bool isSubmittedToClassroom = false;
    protected List<string> gameAnswers = new List<string>();

    protected virtual void Start()
    {
        InitializeGame();
    }

    protected virtual void InitializeGame()
    {
        Debug.Log($"=== BASE GAME INITIALIZATION ===");
        Debug.Log($"Scene: {SceneManager.GetActiveScene().name}");
        Debug.Log($"User: {currentUser} | Session: {sessionTime} UTC");

        if (player != null)
        {
            originalPos = player.anchoredPosition;
        }
        else
        {
            originalPos = Vector2.zero;
        }

        if (resultPanel != null)
            resultPanel.SetActive(false);

        AssignPlayerSprite();
        AssignEnemySprite();
        InitializeTemporaryAnswers();

        UpdateUI();
        ShowDialogueForProgress();

        if (playerSpeechBubble) playerSpeechBubble.SetActive(false);
        if (enemySpeechBubble) enemySpeechBubble.SetActive(false);

        if (questionText != null)
        {
            questionText.text = currentQuestion;
        }

        // Setup classroom integration
        SetupClassroomIntegration();
    }

    protected void SetupClassroomIntegration()
    {
        if (!enableClassroomMode) 
        {
            UpdateClassroomStatus("Classroom Mode Disabled", Color.gray);
            return;
        }
        
        // Show server URL configuration
        Debug.Log($"Classroom Integration - Server URL: {serverURL}");
        UpdateClassroomStatus($"Practice Mode - Server: {serverURL}", Color.gray);
        Debug.Log("Classroom integration ready. Add ClassroomAPIManager script for full functionality.");
    }

    protected void LoadClassroomAssignment()
    {
        // Real Flask API call to load assignment
        StartCoroutine(LoadAssignmentFromFlask());
    }
    
    private IEnumerator LoadAssignmentFromFlask()
    {
        UpdateClassroomStatus("Loading assignment...", Color.yellow);
        
        string url = serverURL + "/api/get_assignment";
        UnityWebRequest request = UnityWebRequest.Get(url);
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            try
            {
                string jsonResponse = request.downloadHandler.text;
                QuizData assignment = JsonUtility.FromJson<QuizData>(jsonResponse);
                OnAssignmentLoaded(true, assignment, "Assignment loaded successfully");
            }
            catch (System.Exception e)
            {
                Debug.LogError("Failed to parse assignment data: " + e.Message);
                OnAssignmentLoaded(false, null, "Failed to parse assignment data");
            }
        }
        else
        {
            Debug.LogError("Failed to load assignment: " + request.error);
            OnAssignmentLoaded(false, null, "Failed to load assignment: " + request.error);
        }
        
        request.Dispose();
    }

    protected void OnAssignmentLoaded(bool success, QuizData assignment, string message)
    {
        if (success)
        {
            currentAssignment = assignment;
            
            // Update the game question with assignment question
            if (assignment.questions != null && assignment.questions.Length > 0)
            {
                currentQuestion = assignment.questions[0].question_text;
                if (questionText != null)
                    questionText.text = currentQuestion;
            }
            
            if (assignmentInfoText != null)
                assignmentInfoText.text = $"Assignment: {assignment.title}\nClass: {assignment.class_name}";
            
            UpdateClassroomStatus("Assignment loaded - Ready to play!", Color.green);
        }
        else
        {
            UpdateClassroomStatus($"Failed to load assignment: {message}", Color.red);
        }
    }

    protected void SubmitToClassroom(int gameScore)
    {
        if (!enableClassroomMode || currentAssignment == null || isSubmittedToClassroom)
            return;
        
        // Real Flask API submission
        StartCoroutine(SubmitScoreToFlask(gameScore));
    }
    
    private IEnumerator SubmitScoreToFlask(int gameScore)
    {
        UpdateClassroomStatus("Submitting to classroom...", Color.yellow);
        
        string url = serverURL + "/api/submit_score";
        string jsonData = "{\"score\":" + gameScore + ",\"assignment_id\":1,\"student_id\":1}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            OnSubmissionComplete(true, "Successfully submitted to classroom!");
        }
        else
        {
            OnSubmissionComplete(false, "Failed to submit: " + request.error);
        }
        
        request.Dispose();
    }

    protected void OnSubmissionComplete(bool success, string message)
    {
        if (success)
        {
            isSubmittedToClassroom = true;
            UpdateClassroomStatus("Successfully submitted to classroom!", Color.green);
            PlayerPrefs.SetString("SubmittedToClassroom", "true");
            PlayerPrefs.Save();
        }
        else
        {
            UpdateClassroomStatus($"Submission failed: {message}", Color.red);
        }
    }

    protected void UpdateClassroomStatus(string message, Color color)
    {
        if (classroomStatusText != null)
        {
            classroomStatusText.text = message;
            classroomStatusText.color = color;
        }
        Debug.Log($"Classroom: {message}");
    }

    // Original BaseGameManager Methods (keep all your existing methods)
    protected void InitializeTemporaryAnswers()
    {
        correctAnswers.Clear();

        string[] programmingLanguages = {
            "python", "javascript", "c#", "java", "c++",
            "ruby", "go", "swift", "php", "kotlin",
            "typescript", "rust", "dart", "scala", "perl",
            "html", "css", "sql", "r", "matlab",
            "c", "objective-c", "shell", "powershell", "bash",
            "vb.net", "f#", "haskell", "lua", "assembly",
            "cobol", "fortran", "pascal", "delphi", "prolog"
        };

        foreach (string lang in programmingLanguages)
        {
            correctAnswers.Add(lang.ToLower());
        }

        Debug.Log($"Loaded {correctAnswers.Count} temporary correct answers");
    }

    protected void AssignPlayerSprite()
    {
        try
        {
            string gender = PlayerPrefs.GetString("PlayerGender", "Male");
            Sprite chosenSprite = (gender.ToLower() == "female" && femaleSprite != null) ? femaleSprite : maleSprite;

            if (playerImage && chosenSprite)
            {
                playerImage.sprite = chosenSprite;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"Could not assign player sprite: {e.Message}");
        }
    }

    protected void AssignEnemySprite()
    {
        try
        {
            if (enemySprites != null && enemySprites.Length > 0 && enemyImage)
            {
                int randomIndex = Random.Range(0, enemySprites.Length);
                enemyImage.sprite = enemySprites[randomIndex];
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"Could not assign enemy sprite: {e.Message}");
        }
    }

    protected void AddProgress(float value)
    {
        progress += value;
        if (progress > maxProgress) progress = maxProgress;

        UpdateUI();
        ShowDialogueForProgress();

        if (progress >= maxProgress)
            StartCoroutine(ShowResultThenNextScene());
    }

    protected void UpdateUI()
    {
        if (progressBar != null)
            progressBar.value = progress / maxProgress;

        if (textProgress != null)
            textProgress.text = Mathf.RoundToInt((progress / maxProgress) * 100f) + "%";
    }

    protected void ShowDialogueForProgress()
    {
        if (dialogueText == null) return;

        string dialogue = dialogueAt0;

        if (progress >= 100) dialogue = dialogueAt100;
        else if (progress >= 75) dialogue = dialogueAt75;
        else if (progress >= 50) dialogue = dialogueAt50;
        else if (progress >= 25) dialogue = dialogueAt25;

        dialogueText.text = dialogue;
    }

    protected IEnumerator ShowResultThenNextScene()
    {
        if (resultPanel != null) resultPanel.SetActive(true);

        int score = Mathf.RoundToInt((progress / maxProgress) * 100f);
        PlayerPrefs.SetInt("PlayerScore", score);
        PlayerPrefs.SetString("LastPlayedBy", currentUser);
        PlayerPrefs.SetString("LastPlayedTime", sessionTime);
        PlayerPrefs.Save();

        // Submit to classroom if enabled
        if (enableClassroomMode && currentAssignment != null && !isSubmittedToClassroom)
        {
            SubmitToClassroom(score);
            // Wait a bit for submission to complete
            yield return new WaitForSeconds(3f);
        }

        yield return new WaitForSeconds(2f);

        try
        {
            SceneManager.LoadScene("gameresult");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Could not load gameresult scene: {e.Message}");
        }
    }

    protected IEnumerator MovePlayerTo(Vector2 targetPosition)
    {
        if (player == null) yield break;

        Vector2 startPos = player.anchoredPosition;
        float journey = 0f;
        float distance = Vector2.Distance(startPos, targetPosition);

        if (distance < 0.1f) yield break;

        while (journey <= 1f)
        {
            journey += Time.deltaTime * movementSpeed;
            Vector2 newPos = Vector2.Lerp(startPos, targetPosition, journey);

            if (player != null)
            {
                player.anchoredPosition = newPos;
            }
            yield return null;
        }

        if (player != null)
        {
            player.anchoredPosition = targetPosition;
        }
    }

    protected IEnumerator ShowSpeechBubble(GameObject bubble, TMP_Text text, string message, float duration)
    {
        if (bubble && text)
        {
            text.text = message;
            bubble.SetActive(true);
            yield return new WaitForSeconds(duration);
            bubble.SetActive(false);
        }
    }

    protected string GetButtonText(Button button)
    {
        if (button == null) return "Unknown";

        TMP_Text tmpText = button.GetComponentInChildren<TMP_Text>();
        if (tmpText != null) return tmpText.text;

        Text regularText = button.GetComponentInChildren<Text>();
        if (regularText != null) return regularText.text;

        return button.name;
    }
}
