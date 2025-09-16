using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using UnityEngine.Networking;
using System.Collections;

public class GenderSelection : MonoBehaviour
{
    public Button boyButton;
    public Button girlButton;
    public Button submitButton;

    private string selectedGender = "";

    // Highlight colors
    public Color normalColor = Color.white;
    public Color selectedColor = Color.green;

    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public int studentId = 1;

    void Start()
    {
        // Add listeners
        boyButton.onClick.AddListener(() => SelectGender("Boy"));
        girlButton.onClick.AddListener(() => SelectGender("Girl"));
        submitButton.onClick.AddListener(OnSubmit);

        // Set initial button colors
        ResetButtonColors();
    }

    void SelectGender(string gender)
    {
        selectedGender = gender;
        ResetButtonColors();

        if (gender == "Boy")
            HighlightButton(boyButton);
        else if (gender == "Girl")
            HighlightButton(girlButton);

        // Send gender selection to Flask web app
        SendGenderSelectionToFlask(gender);
    }

    void HighlightButton(Button btn)
    {
        ColorBlock colors = btn.colors;
        colors.normalColor = selectedColor;
        btn.colors = colors;
    }

    void ResetButtonColors()
    {
        ColorBlock boyColors = boyButton.colors;
        boyColors.normalColor = normalColor;
        boyButton.colors = boyColors;

        ColorBlock girlColors = girlButton.colors;
        girlColors.normalColor = normalColor;
        girlButton.colors = girlColors;
    }

    void OnSubmit()
    {
        if (selectedGender != "")
        {
            // Store the selected gender locally
            PlayerPrefs.SetString("SelectedGender", selectedGender);

            // Send final selection to Flask web app
            SendGenderSubmissionToFlask(selectedGender);

            // Load the TitleScreen scene
            SceneManager.LoadScene("TitleScreen");
        }
        else
        {
            Debug.LogWarning("Please select a gender before submitting.");
        }
    }

    // Flask web app integration - Send gender selection
    private void SendGenderSelectionToFlask(string gender)
    {
        StartCoroutine(PostGenderSelectionToFlask(gender));
    }

    private IEnumerator PostGenderSelectionToFlask(string gender)
    {
        string url = flaskURL + "/api/gender_selection";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"selected_gender\":\"" + gender + "\",\"action\":\"selection\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    // Flask web app integration - Send final gender submission
    private void SendGenderSubmissionToFlask(string gender)
    {
        StartCoroutine(PostGenderSubmissionToFlask(gender));
    }

    private IEnumerator PostGenderSubmissionToFlask(string gender)
    {
        string url = flaskURL + "/api/gender_submission";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"final_gender\":\"" + gender + "\",\"action\":\"submit\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }
}
