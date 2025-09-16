using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;

public class NetworkTest : MonoBehaviour
{
    [Header("UI Elements")]
    public Button testButton;
    public TMP_Text resultText;

    void Start()
    {
        if (testButton != null)
            testButton.onClick.AddListener(RunNetworkTest);
    }

    public void RunNetworkTest()
    {
        StartCoroutine(TestConnections());
    }

    IEnumerator TestConnections()
    {
        resultText.text = "Testing network connections...\n";

        // Test 1: HTTPS to httpbin
        resultText.text += "1. Testing HTTPS (httpbin.org)...\n";
        using (UnityWebRequest request = UnityWebRequest.Get("https://httpbin.org/get"))
        {
            request.timeout = 10;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                resultText.text += "✓ HTTPS works!\n";
            }
            else
            {
                resultText.text += $"✗ HTTPS failed: {request.error}\n";
            }
        }

        yield return new WaitForSeconds(1f);

        // Test 2: HTTPS to Google
        resultText.text += "2. Testing HTTPS (google.com)...\n";
        using (UnityWebRequest request = UnityWebRequest.Get("https://www.google.com"))
        {
            request.timeout = 10;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                resultText.text += "✓ Google HTTPS works!\n";
            }
            else
            {
                resultText.text += $"✗ Google HTTPS failed: {request.error}\n";
            }
        }

        yield return new WaitForSeconds(1f);

        // Test 3: Your Render server (GET request)
        resultText.text += "3. Testing your Render server (GET)...\n";
        using (UnityWebRequest request = UnityWebRequest.Get("https://capstoneproject-unity.onrender.com"))
        {
            request.timeout = 15;
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success || request.responseCode == 404)
            {
                resultText.text += $"✓ Render server reachable! (Code: {request.responseCode})\n";
            }
            else
            {
                resultText.text += $"✗ Render server failed: {request.error}\n";
            }
        }

        yield return new WaitForSeconds(1f);

        // Test 4: Your Render API endpoint
        resultText.text += "4. Testing your API endpoint...\n";
        using (UnityWebRequest request = UnityWebRequest.Get("https://capstoneproject-unity.onrender.com/student/register"))
        {
            request.timeout = 15;
            yield return request.SendWebRequest();
            
            // For API endpoints, we expect a 405 (Method Not Allowed) for GET requests, which means it's working
            if (request.result == UnityWebRequest.Result.Success || request.responseCode == 405)
            {
                resultText.text += $"✓ API endpoint reachable! (Code: {request.responseCode})\n";
                if (request.responseCode == 405)
                {
                    resultText.text += "  (405 = Method Not Allowed for GET, this is correct!)\n";
                }
            }
            else
            {
                resultText.text += $"✗ API endpoint failed: {request.error} (Code: {request.responseCode})\n";
            }
        }

        yield return new WaitForSeconds(1f);

        // Test 5: POST request test to httpbin (which accepts POST)
        resultText.text += "5. Testing POST request to httpbin...\n";
        string testJson = "{\"test\": \"data\"}";
        using (UnityWebRequest request = new UnityWebRequest("https://httpbin.org/post", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(testJson);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = 15;
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                resultText.text += $"✓ POST request works! (Code: {request.responseCode})\n";
            }
            else
            {
                resultText.text += $"✗ POST request failed: {request.error} (Code: {request.responseCode})\n";
            }
        }

        yield return new WaitForSeconds(1f);

        // Test 6: POST request to your Render server
        resultText.text += "6. Testing POST to your Render server...\n";
        string studentJson = "{\"name\":\"Test User\",\"email\":\"test@test.com\",\"class_code\":\"2EK5QUY\",\"device_id\":\"test123\",\"grade_level\":\"Grade 1\",\"avatar_url\":\"\"}";
        using (UnityWebRequest request = new UnityWebRequest("https://capstoneproject-unity.onrender.com/student/register", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(studentJson);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Accept", "application/json");
            request.timeout = 30;
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                resultText.text += $"✓ POST to your server works! (Code: {request.responseCode})\n";
                resultText.text += $"  Response: {request.downloadHandler.text.Substring(0, System.Math.Min(100, request.downloadHandler.text.Length))}...\n";
            }
            else
            {
                resultText.text += $"✗ POST to your server failed: {request.error} (Code: {request.responseCode})\n";
                resultText.text += $"  Response: {request.downloadHandler.text}\n";
            }
        }

        resultText.text += "\nTest complete!";
    }
}
