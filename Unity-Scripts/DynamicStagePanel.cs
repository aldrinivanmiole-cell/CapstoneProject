using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using TMPro;
using UnityEngine.Networking;
using System.Collections;

public class DynamicStagePanel_TMP : MonoBehaviour
{
    [Header("Subject Buttons")]
    public Button mathButton;
    public Button scienceButton;
    public Button englishButton;
    public Button peButton;
    public Button artButton;

    [Header("Stage Panel")]
    public GameObject stagePanel;
    public TMP_Text titleText;
    public Button stageButton1;
    public Button stageButton2;
    public Button stageButton3;
    public Button backButton;

    [Header("Flask Integration")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public bool sendToFlask = true;

    private string currentSubject;

    void Start()
    {
        stagePanel.SetActive(false);

        mathButton.onClick.AddListener(() => ShowStages("Math"));
        scienceButton.onClick.AddListener(() => ShowStages("Science"));
        englishButton.onClick.AddListener(() => ShowStages("English"));
        peButton.onClick.AddListener(() => ShowStages("PE"));
        artButton.onClick.AddListener(() => ShowStages("Art"));

        backButton.onClick.AddListener(HidePanel);

        stageButton1.onClick.AddListener(() => LoadStage("Stage1"));

        // Lock stage 2 and 3 at start
        SetButtonState(stageButton2, false);
        SetButtonState(stageButton3, false);
    }

    void ShowStages(string subject)
    {
        currentSubject = subject;
        stagePanel.SetActive(true);
        titleText.text = subject + " Stages";

        // Send subject selection to Flask
        if (sendToFlask)
        {
            StartCoroutine(SendSubjectSelectionToFlask(subject));
        }
    }

    void HidePanel()
    {
        stagePanel.SetActive(false);
    }

    void LoadStage(string stageID)
    {
        Debug.Log($"Loading {currentSubject} - {stageID}");
        
        // Send stage selection to Flask
        if (sendToFlask)
        {
            StartCoroutine(SendStageSelectionToFlask(currentSubject, stageID));
        }

        SceneManager.LoadScene("GameplayScene");

        // Simulate unlocking next stage (you can change this logic as needed)
        if (stageID == "Stage1")
        {
            SetButtonState(stageButton2, true);
        }
        else if (stageID == "Stage2")
        {
            SetButtonState(stageButton3, true);
        }
    }

    void SetButtonState(Button btn, bool active)
    {
        btn.interactable = active;
        CanvasGroup cg = btn.GetComponent<CanvasGroup>();
        if (cg == null) cg = btn.gameObject.AddComponent<CanvasGroup>();
        cg.alpha = active ? 1f : 0.5f;
        cg.blocksRaycasts = active;
    }

    // Flask Integration Methods
    private IEnumerator SendSubjectSelectionToFlask(string subject)
    {
        string jsonData = "{\"subject\":\"" + subject + "\",\"action\":\"subject_selected\",\"timestamp\":\"" + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "\"}";
        
        UnityWebRequest request = new UnityWebRequest(flaskURL + "/api/subject_selection", "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Successfully sent subject selection to Flask: " + subject);
        }
        else
        {
            Debug.LogWarning("Failed to send subject selection to Flask: " + request.error);
        }
        
        request.Dispose();
    }

    private IEnumerator SendStageSelectionToFlask(string subject, string stage)
    {
        string jsonData = "{\"subject\":\"" + subject + "\",\"stage\":\"" + stage + "\",\"action\":\"stage_selected\",\"timestamp\":\"" + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "\"}";
        
        UnityWebRequest request = new UnityWebRequest(flaskURL + "/api/stage_selection", "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Successfully sent stage selection to Flask: " + subject + " - " + stage);
        }
        else
        {
            Debug.LogWarning("Failed to send stage selection to Flask: " + request.error);
        }
        
        request.Dispose();
    }
}
