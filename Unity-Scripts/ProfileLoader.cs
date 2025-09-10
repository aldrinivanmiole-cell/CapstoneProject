using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;
using System.Collections;

[System.Serializable]
public class StudentProfile
{
    public int id;
    public string name;
    public string email;
    public string gender;
    public string grade_level;
    public string class_name;
}

public class ProfileLoader : MonoBehaviour
{
    [Header("Profile UI")]
    public Image avatarImage;
    public Sprite Mavatar;
    public Sprite Favatar;

    public TMP_Text studentNameText;
    public TMP_Text gradeLevelText;
    public TMP_Text classNameText;
    
    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public bool useWebAppData = true; // Toggle between web app and local data
    public int studentId = 1; // Set this to load specific student profile
    
    [Header("Loading UI")]
    public GameObject loadingPanel;
    public TMP_Text statusText;

    void Start()
    {
        if (useWebAppData)
        {
            LoadProfileFromWebApp();
        }
        else
        {
            LoadProfileFromPlayerPrefs();
        }
    }

    void LoadProfileFromWebApp()
    {
        StartCoroutine(LoadStudentProfileFromFlask());
    }
    
    private IEnumerator LoadStudentProfileFromFlask()
    {
        UpdateStatus("Loading student profile...", Color.yellow);
        
        string url = flaskURL + "/api/get_student_profile/" + studentId;
        UnityWebRequest request = UnityWebRequest.Get(url);
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            try
            {
                string jsonResponse = request.downloadHandler.text;
                StudentProfile profile = JsonUtility.FromJson<StudentProfile>(jsonResponse);
                ApplyProfile(profile);
                UpdateStatus("Profile loaded successfully!", Color.green);
                
                // Hide status after 2 seconds
                StartCoroutine(HideStatusAfterDelay(2f));
            }
            catch (System.Exception e)
            {
                Debug.LogError("Failed to parse profile data: " + e.Message);
                UpdateStatus("Failed to load profile", Color.red);
                // Fallback to local data
                LoadProfileFromPlayerPrefs();
            }
        }
        else
        {
            Debug.LogError("Failed to load profile: " + request.error);
            UpdateStatus("Connection failed - Using local data", Color.orange);
            // Fallback to local data
            LoadProfileFromPlayerPrefs();
        }
        
        request.Dispose();
    }
    
    void ApplyProfile(StudentProfile profile)
    {
        // Set avatar based on gender
        if (profile.gender.ToLower() == "female" && Favatar != null)
        {
            avatarImage.sprite = Favatar;
        }
        else if (Mavatar != null)
        {
            avatarImage.sprite = Mavatar;
        }

        // Set profile information
        if (studentNameText) studentNameText.text = profile.name;
        if (gradeLevelText) gradeLevelText.text = profile.grade_level;
        if (classNameText) classNameText.text = profile.class_name;
        
        // Save to PlayerPrefs for offline use
        PlayerPrefs.SetString("StudentName", profile.name);
        PlayerPrefs.SetString("SelectedGender", profile.gender);
        PlayerPrefs.SetString("GradeLevel", profile.grade_level);
        PlayerPrefs.SetString("ClassName", profile.class_name);
        PlayerPrefs.SetInt("StudentId", profile.id);
        PlayerPrefs.Save();
        
        Debug.Log($"Profile loaded: {profile.name} ({profile.gender}) - {profile.grade_level} in {profile.class_name}");
    }

    void LoadProfileFromPlayerPrefs()
    {
        UpdateStatus("Loading local profile...", Color.blue);
        
        // Load from PlayerPrefs (fallback/offline mode)
        string gender = PlayerPrefs.GetString("SelectedGender", "Male");
        string studentName = PlayerPrefs.GetString("StudentName", "Juan Dela Cruz");
        string gradeLevel = PlayerPrefs.GetString("GradeLevel", "Grade 7");
        string className = PlayerPrefs.GetString("ClassName", "Sample Class");

        // Set avatar based on gender
        if (gender.ToLower() == "female" && Favatar != null)
        {
            avatarImage.sprite = Favatar;
        }
        else if (Mavatar != null)
        {
            avatarImage.sprite = Mavatar;
        }

        // Set profile information
        if (studentNameText) studentNameText.text = studentName;
        if (gradeLevelText) gradeLevelText.text = gradeLevel;
        if (classNameText) classNameText.text = className;
        
        UpdateStatus("Local profile loaded", Color.green);
        
        // Hide status after 1 second
        StartCoroutine(HideStatusAfterDelay(1f));
        
        Debug.Log($"Local profile loaded: {studentName} ({gender}) - {gradeLevel}");
    }
    
    private IEnumerator HideStatusAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        if (loadingPanel) loadingPanel.SetActive(false);
    }
    
    void UpdateStatus(string message, Color color)
    {
        if (statusText)
        {
            statusText.text = message;
            statusText.color = color;
        }
        
        if (loadingPanel) loadingPanel.SetActive(true);
        
        Debug.Log($"ProfileLoader: {message}");
    }
    
    // Public method to refresh profile (can be called from buttons)
    public void RefreshProfile()
    {
        if (useWebAppData)
        {
            LoadProfileFromWebApp();
        }
        else
        {
            LoadProfileFromPlayerPrefs();
        }
    }
    
    // Public method to toggle data source
    public void ToggleDataSource()
    {
        useWebAppData = !useWebAppData;
        RefreshProfile();
    }
}
