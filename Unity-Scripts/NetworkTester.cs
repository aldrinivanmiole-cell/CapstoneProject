using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using TMPro;

public class NetworkTester : MonoBehaviour
{
    [Header("UI Elements")]
    public Button testButton;
    public TMP_Text resultText;
    
    [Header("Test URLs")]
    public string[] testUrls = {
        "https://www.google.com",
        "https://httpbin.org/get",
        "https://capstoneproject-jq2h.onrender.com"
    };

    void Start()
    {
        if (testButton != null)
            testButton.onClick.AddListener(RunNetworkTests);
            
        if (resultText != null)
            resultText.text = "Click Test Network to start...";
    }

    public void RunNetworkTests()
    {
        StartCoroutine(TestAllConnections());
    }

    IEnumerator TestAllConnections()
    {
        resultText.text = "Starting network tests...\n";
        
        // Test basic connectivity info
        resultText.text += $"Platform: {Application.platform}\n";
        resultText.text += $"Internet: {Application.internetReachability}\n";
        resultText.text += $"Unity Version: {Application.unityVersion}\n\n";

        foreach (string url in testUrls)
        {
            resultText.text += $"Testing: {url}\n";
            yield return StartCoroutine(TestSingleUrl(url));
            yield return new WaitForSeconds(1f); // Wait between tests
        }
        
        resultText.text += "\nAll tests complete!";
    }

    IEnumerator TestSingleUrl(string url)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = 10;
            
            // Add headers that might help
            request.SetRequestHeader("User-Agent", "Unity-Android-Test");
            
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                resultText.text += $"✓ SUCCESS (Code: {request.responseCode})\n";
            }
            else
            {
                resultText.text += $"✗ FAILED: {request.error}\n";
                resultText.text += $"  Code: {request.responseCode}\n";
                resultText.text += $"  Result: {request.result}\n";
            }
        }
    }
}
