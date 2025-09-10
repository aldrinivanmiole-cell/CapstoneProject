using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;
using TMPro;

public class RegisterManager : MonoBehaviour
{
    [Header("API Configuration")]
    public string apiUrl = "https://capstoneproject-jq2h.onrender.com/api/student/register";

    [Header("Input Fields")]
    public TMP_InputField firstNameInput;
    public TMP_InputField lastNameInput;
    public TMP_InputField emailInput;
    public TMP_InputField passwordInput;
    public TMP_InputField confirmPasswordInput;

    [Header("UI Elements")]
    public Button submitButton;
    public Button loginButton;
    public TMP_Text messageText;

    void Start()
    {
        messageText.text = "";
        submitButton.onClick.AddListener(OnRegisterClick);
        if (loginButton != null)
            loginButton.onClick.AddListener(GoBackToLogin);
    }

    void OnRegisterClick()
    {
        string firstName = firstNameInput.text.Trim();
        string lastName = lastNameInput.text.Trim();
        string email = emailInput.text.Trim();
        string password = passwordInput.text;
        string confirmPassword = confirmPasswordInput.text;

        // Basic validation
        if (string.IsNullOrEmpty(firstName) || string.IsNullOrEmpty(lastName) ||
            string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password) || string.IsNullOrEmpty(confirmPassword))
        {
            ShowMessage("Please fill in all fields.", false);
            return;
        }

        if (password != confirmPassword)
        {
            ShowMessage("Passwords do not match.", false);
            return;
        }

        // Start registration
        ShowMessage("Registering student...", true);
        submitButton.interactable = false;
        StartCoroutine(RegisterStudent(firstName, lastName, email));
    }

    IEnumerator RegisterStudent(string firstName, string lastName, string email)
    {
        // Check Unity Editor connectivity first
        Debug.Log($"=== UNITY EDITOR NETWORK TEST ===");
        Debug.Log($"Platform: {Application.platform}");
        Debug.Log($"Internet Reachability: {Application.internetReachability}");
        Debug.Log($"Unity Version: {Application.unityVersion}");
        Debug.Log($"Is Editor: {Application.isEditor}");

        // Prepare data for the API
        var studentData = new StudentRegistrationData
        {
            name = $"{firstName} {lastName}",
            email = email,
            class_code = "2EK5QUY",
            device_id = SystemInfo.deviceUniqueIdentifier,
            grade_level = "Grade 1",
            avatar_url = ""
        };

        string jsonData = JsonUtility.ToJson(studentData);
        Debug.Log($"Sending registration data: {jsonData}");

        // Test basic connectivity first
        Debug.Log("Testing basic connectivity to Google...");
        using (UnityWebRequest testRequest = UnityWebRequest.Get("https://www.google.com"))
        {
            testRequest.timeout = 10;
            yield return testRequest.SendWebRequest();

            Debug.Log($"Google test result: {testRequest.result}");
            Debug.Log($"Google test error: {testRequest.error}");
            Debug.Log($"Google response code: {testRequest.responseCode}");

            if (testRequest.result != UnityWebRequest.Result.Success)
            {
                ShowMessage($"Basic connectivity failed: {testRequest.error}", false);
                submitButton.interactable = true;
                yield break;
            }
        }

        Debug.Log("Basic connectivity OK, testing your server...");

        // Create UnityWebRequest for HTTPS POST
        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
        {
            // Convert JSON string to bytes
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            
            // Set up request
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            // Set headers for JSON
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Accept", "application/json");
            
            // Unity Editor specific settings - more permissive
            request.timeout = 60;
            request.redirectLimit = 10;
            
            // Unity Editor often has certificate issues, try to handle them
            if (Application.isEditor)
            {
                request.certificateHandler = new AcceptAllCertificates();
            }

            Debug.Log($"=== SENDING REQUEST ===");
            Debug.Log($"URL: {apiUrl}");
            Debug.Log($"Method: POST");
            Debug.Log($"Content-Type: application/json");
            Debug.Log($"JSON Data: {jsonData}");

            // Send the request and wait for response
            yield return request.SendWebRequest();

            // Re-enable button
            submitButton.interactable = true;

            Debug.Log($"=== REQUEST COMPLETE ===");
            Debug.Log($"Result: {request.result}");
            Debug.Log($"Response Code: {request.responseCode}");
            Debug.Log($"Error: {request.error}");
            Debug.Log($"Response Headers: {request.GetResponseHeaders()}");
            Debug.Log($"Response Body: {request.downloadHandler.text}");

            // Handle response
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"SUCCESS! Response received: {request.downloadHandler.text}");
                
                try
                {
                    var response = JsonUtility.FromJson<RegistrationResponse>(request.downloadHandler.text);
                    
                    if (response.status == "success")
                    {
                        // Save student data locally
                        PlayerPrefs.SetInt("StudentID", response.student_id);
                        PlayerPrefs.SetString("StudentName", response.student_name);
                        PlayerPrefs.SetInt("TotalPoints", response.total_points);
                        PlayerPrefs.Save();

                        ShowMessage($"Registration successful! Welcome {response.student_name}!", true);
                        
                        // Clear form
                        ClearForm();
                        
                        Debug.Log($"Student registered successfully: ID={response.student_id}, Name={response.student_name}");
                    }
                    else
                    {
                        ShowMessage("Registration failed. Please try again.", false);
                        Debug.LogError($"Registration failed: {response.status}");
                    }
                }
                catch (Exception e)
                {
                    ShowMessage("Error processing server response.", false);
                    Debug.LogError($"JSON parsing error: {e.Message}");
                    Debug.LogError($"Raw response: {request.downloadHandler.text}");
                }
            }
            else
            {
                // Handle different types of errors
                string errorMsg = "Registration failed";
                
                if (request.result == UnityWebRequest.Result.ConnectionError)
                {
                    errorMsg = "Cannot connect to server. Check your internet connection.";
                    Debug.LogError("CONNECTION ERROR - Possible causes:");
                    Debug.LogError("1. No internet connection");
                    Debug.LogError("2. Firewall blocking Unity Editor");
                    Debug.LogError("3. Corporate proxy settings");
                    Debug.LogError("4. Server is down");
                }
                else if (request.result == UnityWebRequest.Result.ProtocolError)
                {
                    errorMsg = $"Server error (Code: {request.responseCode})";
                    Debug.LogError($"PROTOCOL ERROR: HTTP {request.responseCode}");
                    Debug.LogError($"Response: {request.downloadHandler.text}");
                }
                else if (request.result == UnityWebRequest.Result.DataProcessingError)
                {
                    errorMsg = "Data processing error";
                    Debug.LogError("DATA PROCESSING ERROR");
                }

                ShowMessage(errorMsg, false);
                Debug.LogError($"Request failed: {request.error} (Result: {request.result}, Code: {request.responseCode})");
            }
        }
    }

    void ShowMessage(string message, bool isSuccess)
    {
        messageText.text = message;
        messageText.color = isSuccess ? Color.green : Color.red;
    }

    void ClearForm()
    {
        firstNameInput.text = "";
        lastNameInput.text = "";
        emailInput.text = "";
        passwordInput.text = "";
        confirmPasswordInput.text = "";
    }

    public void GoBackToLogin()
    {
        SceneManager.LoadScene("login");
    }
}

// Data classes for JSON serialization
[System.Serializable]
public class StudentRegistrationData
{
    public string name;
    public string email;
    public string class_code;
    public string device_id;
    public string grade_level;
    public string avatar_url;
}

[System.Serializable]
public class RegistrationResponse
{
    public string status;
    public int student_id;
    public string student_name;
    public int total_points;
}

// Certificate handler for Unity Editor HTTPS issues
public class AcceptAllCertificates : CertificateHandler
{
    protected override bool ValidateCertificate(byte[] certificateData)
    {
        // Accept all certificates in Unity Editor for testing
        return true;
    }
}
