using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using UnityEngine.Networking;
using System.Collections;

public class LoginManager : MonoBehaviour
{
    [Header("UI Elements")]
    public TMP_InputField usernameInput;
    public TMP_InputField passwordInput;
    public Button submitButton;
    public Button registerButton; // ✅ Add this in Inspector
    public TMP_Text messageText;

    [Header("Animation")]
    public Animator loginAnimator;

    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"

    void Start()
    {
        // Clear message at start
        if (messageText != null)
            messageText.text = "";

        // ✅ Assign button listeners in code
        submitButton.onClick.AddListener(OnSubmit);
        registerButton.onClick.AddListener(GoToRegisterScene);
    }

    void OnSubmit()
    {
        string username = usernameInput.text.Trim();
        string password = passwordInput.text;

        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
        {
            messageText.text = "Please fill in both fields.";
            return;
        }

        // Send login attempt to Flask web app
        StartCoroutine(AttemptLogin(username, password));
    }

    // Flask web app integration - Login authentication
    private IEnumerator AttemptLogin(string username, string password)
    {
        string url = flaskURL + "/api/login";
        
        // Create JSON data for Flask
        string jsonData = "{\"username\":\"" + username + "\",\"password\":\"" + password + "\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        messageText.text = "Logging in...";
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            // Parse response from Flask
            string responseText = request.downloadHandler.text;
            
            // Simple JSON parsing (you can use a proper JSON library if needed)
            if (responseText.Contains("\"success\":true"))
            {
                messageText.text = "Login Success!";
                
                // Store user info for session
                PlayerPrefs.SetString("LoggedInUser", username);
                PlayerPrefs.SetInt("IsLoggedIn", 1);
                
                if (loginAnimator != null)
                    loginAnimator.SetTrigger("PopOut");

                Invoke(nameof(LoadNextScene), 0.6f); // Match animation length
            }
            else
            {
                messageText.text = "Invalid username or password.";
                
                // Send failed login attempt to Flask
                SendLoginFailureToFlask(username);
            }
        }
        else
        {
            messageText.text = "Connection error. Please try again.";
            Debug.LogError($"Login request failed: {request.error}");
        }
        
        request.Dispose();
    }

    // Flask web app integration - Send failed login attempt
    private void SendLoginFailureToFlask(string username)
    {
        StartCoroutine(PostLoginFailureToFlask(username));
    }

    private IEnumerator PostLoginFailureToFlask(string username)
    {
        string url = flaskURL + "/api/login_failure";
        
        // Create JSON data for Flask
        string jsonData = "{\"username\":\"" + username + "\",\"action\":\"failed_login\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    void LoadNextScene()
    {
        SceneManager.LoadScene("titlescene"); // Replace with your real scene name
    }

    public void GoToRegisterScene()
    {
        // Send navigation tracking to Flask web app
        SendNavigationToFlask("register");
        
        SceneManager.LoadScene("register"); // ✅ Replace with actual Register scene name
    }

    // Flask web app integration - Send navigation tracking
    private void SendNavigationToFlask(string targetScene)
    {
        StartCoroutine(PostNavigationToFlask(targetScene));
    }

    private IEnumerator PostNavigationToFlask(string targetScene)
    {
        string url = flaskURL + "/api/navigation_event";
        
        // Create JSON data for Flask
        string jsonData = "{\"action\":\"go_to_register\",\"scene\":\"" + targetScene + "\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }
}
