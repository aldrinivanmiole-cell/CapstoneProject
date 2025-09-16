using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class OpenHint : MonoBehaviour
{
    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public int studentId = 1;

    // Call this from the button
    public void OpenYouTubeHint()
    {
        // Send hint access tracking to Flask web app
        SendHintAccessToFlask("YouTube", "https://www.youtube.com");
        
        Application.OpenURL("https://www.youtube.com");
    }

    // Or pass a custom URL
    public void OpenCustomURL(string url)
    {
        // Send custom hint access tracking to Flask web app
        SendHintAccessToFlask("Custom URL", url);
        
        Application.OpenURL(url);
    }

    // Flask web app integration - Send hint access tracking
    private void SendHintAccessToFlask(string hintType, string hintUrl)
    {
        StartCoroutine(PostHintAccessToFlask(hintType, hintUrl));
    }

    private IEnumerator PostHintAccessToFlask(string hintType, string hintUrl)
    {
        string url = flaskURL + "/api/hint_access";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"hint_type\":\"" + hintType + "\",\"hint_url\":\"" + hintUrl + "\",\"action\":\"hint_accessed\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }
}

