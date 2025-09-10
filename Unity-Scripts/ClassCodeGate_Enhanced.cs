using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using UnityEngine.Networking;

// Enhanced ClassCodeGate with Classroom Integration
// Copy this ENTIRE script to replace your existing ClassCodeGate.cs
public class ClassCodeGate : MonoBehaviour
{
    [Header("Class Code UI")]
    public GameObject classCodePanel;
    public TMP_InputField classCodeInput;
    public Button submitButton;
    public Button skipButton; // New: Skip button for students already in classes

    [Header("Subjects UI")]
    public GameObject subjectButtonsContainer;

    [Header("Status Display")]
    public TMP_Text statusText;
    public TMP_Text studentNameText;
    public TMP_Text currentClassesText;

    [Header("Classroom Integration")]
    public bool enableClassroomMode = true;
    public string serverURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"

    private const string CLASS_CODE_KEY = "ClassCodeEntered";

    void Start()
    {
        SetupClassCodeGate();
    }

    void SetupClassCodeGate()
    {
        // Setup button listeners
        if (submitButton != null)
            submitButton.onClick.AddListener(SubmitClassCode);
        
        if (skipButton != null)
            skipButton.onClick.AddListener(SkipClassCode);

        if (enableClassroomMode)
        {
            SetupClassroomIntegration();
        }
        else
        {
            SetupLegacyMode();
        }
    }

    void SetupClassroomIntegration()
    {
        // Check if student is logged in
        if (!IsStudentLoggedIn())
        {
            UpdateStatus("Please login first to join classes", Color.red);
            ShowClassCodePanel(false);
            return;
        }

        // Get current student info
        string studentName = GetCurrentStudentName();
        ShowStudentInfo(studentName);

        // Check if student already has classes
        if (HasExistingClasses())
        {
            ShowExistingClasses();
            ShowSkipOption(true);
        }
        else
        {
            UpdateStatus("Enter a class code to join your first class", Color.blue);
            ShowSkipOption(false);
        }

        ShowClassCodePanel(true);
    }

    void SetupLegacyMode()
    {
        // Original behavior for backwards compatibility
        if (PlayerPrefs.HasKey(CLASS_CODE_KEY))
        {
            classCodePanel.SetActive(false);
            subjectButtonsContainer.SetActive(true);
        }
        else
        {
            classCodePanel.SetActive(true);
            subjectButtonsContainer.SetActive(false);
        }

        UpdateStatus("Legacy mode - Enter any class code", Color.gray);
    }

    void SubmitClassCode()
    {
        string enteredCode = classCodeInput.text.Trim().ToUpper();

        if (string.IsNullOrEmpty(enteredCode))
        {
            UpdateStatus("Please enter a valid class code", Color.red);
            return;
        }

        if (enteredCode.Length != 7) // Assuming class codes are 7 characters
        {
            UpdateStatus("Class code must be 7 characters", Color.red);
            return;
        }

        if (enableClassroomMode)
        {
            StartCoroutine(JoinClassWithAPI(enteredCode));
        }
        else
        {
            // Legacy mode - accept any code
            AcceptClassCode(enteredCode);
        }
    }

    IEnumerator JoinClassWithAPI(string classCode)
    {
        UpdateStatus("Joining class...", Color.yellow);
        
        if (submitButton != null) 
            submitButton.interactable = false;

        // Real Flask API call
        string url = serverURL + "/api/join_class";
        string jsonData = "{\"class_code\":\"" + classCode + "\",\"student_name\":\"Student\"}";
        
        UnityEngine.Networking.UnityWebRequest request = new UnityEngine.Networking.UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UnityEngine.Networking.UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new UnityEngine.Networking.DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        bool success = false;
        if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
        {
            success = true;
            Debug.Log("Successfully joined class: " + classCode);
        }
        else
        {
            Debug.LogError("Failed to join class: " + request.error);
        }
        
        request.Dispose();
        
        if (success)
        {
            UpdateStatus($"Successfully joined class: {classCode}!", Color.green);
            AcceptClassCode(classCode);
            
            // Refresh class display
            yield return new WaitForSeconds(1f);
            ShowExistingClasses();
            ShowSkipOption(true);
        }
        else
        {
            UpdateStatus($"Invalid class code: {classCode}", Color.red);
        }

        if (submitButton != null) 
            submitButton.interactable = true;

        // Clear input field
        if (classCodeInput != null)
            classCodeInput.text = "";
    }

    bool SimulateClassJoin(string classCode)
    {
        // Simulate some valid class codes for testing
        string[] validCodes = { "CS101A1", "MATH202", "ENG301B", "PHYS101", "CHEM205" };
        
        foreach (string validCode in validCodes)
        {
            if (classCode.Equals(validCode, System.StringComparison.OrdinalIgnoreCase))
            {
                // Save the joined class
                string existingClasses = PlayerPrefs.GetString("JoinedClasses", "");
                if (!existingClasses.Contains(classCode))
                {
                    existingClasses += (existingClasses.Length > 0 ? "," : "") + classCode;
                    PlayerPrefs.SetString("JoinedClasses", existingClasses);
                    PlayerPrefs.Save();
                }
                return true;
            }
        }
        
        return false;
    }

    void AcceptClassCode(string classCode)
    {
        Debug.Log("Class code accepted: " + classCode);

        // Remember for future sessions
        PlayerPrefs.SetInt(CLASS_CODE_KEY, 1);
        PlayerPrefs.SetString("LastClassCode", classCode);
        PlayerPrefs.Save();

        // Don't automatically transition - let student join more classes or skip
        UpdateStatus("Class joined! Enter another code or continue to subjects", Color.green);
    }

    void SkipClassCode()
    {
        if (enableClassroomMode && !HasExistingClasses())
        {
            UpdateStatus("You need to join at least one class first", Color.red);
            return;
        }

        // Transition to subjects
        TransitionToSubjects();
    }

    void TransitionToSubjects()
    {
        UpdateStatus("Continuing to subjects...", Color.green);
        
        if (classCodePanel != null)
            classCodePanel.SetActive(false);
        
        if (subjectButtonsContainer != null)
            subjectButtonsContainer.SetActive(true);
    }

    // Helper Methods
    bool IsStudentLoggedIn()
    {
        // TODO: Replace with actual check when ClassroomAPIManager is available
        // For now, check if we have a student name saved
        return !string.IsNullOrEmpty(PlayerPrefs.GetString("StudentName", ""));
    }

    string GetCurrentStudentName()
    {
        // TODO: Replace with actual API call when ClassroomAPIManager is available
        return PlayerPrefs.GetString("StudentName", "Guest Student");
    }

    bool HasExistingClasses()
    {
        // Check if student has joined any classes
        string joinedClasses = PlayerPrefs.GetString("JoinedClasses", "");
        return !string.IsNullOrEmpty(joinedClasses);
    }

    void ShowExistingClasses()
    {
        string joinedClasses = PlayerPrefs.GetString("JoinedClasses", "");
        
        if (!string.IsNullOrEmpty(joinedClasses))
        {
            string[] classes = joinedClasses.Split(',');
            string classDisplay = "Your Classes:\n";
            
            foreach (string classCode in classes)
            {
                classDisplay += $"• {classCode}\n";
            }
            
            if (currentClassesText != null)
                currentClassesText.text = classDisplay;
                
            UpdateStatus($"You are in {classes.Length} class(es)", Color.green);
        }
    }

    void ShowStudentInfo(string studentName)
    {
        if (studentNameText != null)
            studentNameText.text = $"Student: {studentName}";
    }

    void ShowClassCodePanel(bool show)
    {
        if (classCodePanel != null)
            classCodePanel.SetActive(show);
    }

    void ShowSkipOption(bool show)
    {
        if (skipButton != null)
            skipButton.gameObject.SetActive(show);
    }

    void UpdateStatus(string message, Color color)
    {
        if (statusText != null)
        {
            statusText.text = message;
            statusText.color = color;
        }
        
        Debug.Log($"ClassCodeGate: {message}");
    }

    // Public methods for external access
    public void SetServerURL(string url)
    {
        serverURL = url;
    }

    public void SetStudentName(string name)
    {
        PlayerPrefs.SetString("StudentName", name);
        PlayerPrefs.Save();
    }

    public string[] GetJoinedClasses()
    {
        string joinedClasses = PlayerPrefs.GetString("JoinedClasses", "");
        if (string.IsNullOrEmpty(joinedClasses))
            return new string[0];
        
        return joinedClasses.Split(',');
    }

    public void ClearClassData()
    {
        PlayerPrefs.DeleteKey(CLASS_CODE_KEY);
        PlayerPrefs.DeleteKey("JoinedClasses");
        PlayerPrefs.DeleteKey("LastClassCode");
        PlayerPrefs.Save();
        
        // Reset UI
        SetupClassCodeGate();
    }
}
