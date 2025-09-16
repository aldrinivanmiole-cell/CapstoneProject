using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;

public class MultipleChoiceDragDropManager : BaseGameManager
{
    [Header("Multiple Choice Components")]
    public List<Toggle> answerToggles = new List<Toggle>();
    public Button submitToggleButton;
    public TMP_Text multipleChoiceFeedbackText;

    [Header("Drag & Drop Components")]
    public List<Button> answerButtons = new List<Button>();
    public FillBlankDropZone dropZone;

    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public int studentId = 1;

    private bool hasMultipleChoiceComponents;
    private bool hasDragDropComponents;

    protected override void Start()
    {
        base.Start();
        DetectAndSetupComponents();
    }

    private void DetectAndSetupComponents()
    {
        hasMultipleChoiceComponents = (submitToggleButton != null || answerToggles.Count > 0);
        hasDragDropComponents = (dropZone != null || answerButtons.Count > 0);

        Debug.Log($"Scene Detection: MC={hasMultipleChoiceComponents}, DragDrop={hasDragDropComponents}");

        // Send component detection to Flask web app
        SendComponentDetectionToFlask(hasMultipleChoiceComponents, hasDragDropComponents);

        if (hasMultipleChoiceComponents)
        {
            SetupMultipleChoiceComponents();
        }

        if (hasDragDropComponents)
        {
            SetupDragAndDropComponents();
        }
    }

    private void SetupMultipleChoiceComponents()
    {
        Debug.Log("=== Setting up Multiple Choice components ===");

        if (submitToggleButton != null)
        {
            submitToggleButton.onClick.RemoveAllListeners();
            submitToggleButton.onClick.AddListener(SubmitToggleAnswers);
            submitToggleButton.interactable = true;
        }

        foreach (var toggle in answerToggles)
        {
            if (toggle != null)
            {
                toggle.interactable = true;
                
                // Add listener to track toggle selections
                toggle.onValueChanged.AddListener((bool isOn) => {
                    TMP_Text toggleText = toggle.GetComponentInChildren<TMP_Text>();
                    string toggleValue = toggleText != null ? toggleText.text : "Unknown";
                    SendToggleSelectionToFlask(toggleValue, isOn);
                });
            }
        }
    }

    private void SetupDragAndDropComponents()
    {
        Debug.Log("=== Setting up Drag & Drop components ===");

        foreach (var btn in answerButtons)
        {
            if (btn != null)
            {
                string btnText = GetButtonText(btn);
                btn.onClick.RemoveAllListeners();
                btn.onClick.AddListener(() => {
                    if (!isProcessingAttack)
                    {
                        // Send button click to Flask web app
                        SendDragDropSelectionToFlask(btnText);
                        TriggerAttackWithEnemy(btnText);
                    }
                });
                btn.interactable = true;
            }
        }
    }

    public void SubmitToggleAnswers()
    {
        if (!hasMultipleChoiceComponents)
        {
            Debug.LogError("SubmitToggleAnswers called but no multiple choice components!");
            return;
        }

        if (isProcessingAttack)
        {
            ShowMultipleChoiceFeedback("Please wait, processing...", false);
            return;
        }

        List<string> selectedAnswers = new List<string>();

        foreach (var toggle in answerToggles)
        {
            if (toggle != null && toggle.isOn)
            {
                TMP_Text toggleText = toggle.GetComponentInChildren<TMP_Text>();
                if (toggleText != null)
                {
                    selectedAnswers.Add(toggleText.text);
                }
            }
        }

        if (selectedAnswers.Count == 0)
        {
            Debug.LogWarning("No answers selected in multiple choice!");
            ShowMultipleChoiceFeedback("Please select at least one answer!", false);
            return;
        }

        float scorePercentage = CalculateMultipleChoiceScore(selectedAnswers);
        string allAnswers = string.Join(", ", selectedAnswers);

        // Send multiple choice submission to Flask web app
        SendMultipleChoiceSubmissionToFlask(allAnswers, scorePercentage, selectedAnswers.Count);

        StartCoroutine(HandleMultipleAnswerAttack(allAnswers, scorePercentage));
    }

    public void TriggerAttackWithEnemy(string answer)
    {
        if (!hasDragDropComponents)
        {
            Debug.LogError("TriggerAttackWithEnemy called but no drag drop components!");
            return;
        }

        if (!isProcessingAttack && enemy1 != null && player != null)
        {
            StartCoroutine(HandleSingleAnswerAttack(answer));
        }
    }

    // Flask web app integration - Send component detection
    private void SendComponentDetectionToFlask(bool hasMultipleChoice, bool hasDragDrop)
    {
        StartCoroutine(PostComponentDetectionToFlask(hasMultipleChoice, hasDragDrop));
    }

    private IEnumerator PostComponentDetectionToFlask(bool hasMultipleChoice, bool hasDragDrop)
    {
        string url = flaskURL + "/api/game_component_detection";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"has_multiple_choice\":" + hasMultipleChoice.ToString().ToLower() + ",\"has_drag_drop\":" + hasDragDrop.ToString().ToLower() + ",\"game_type\":\"mixed_mode\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    // Flask web app integration - Send toggle selection
    private void SendToggleSelectionToFlask(string toggleValue, bool isSelected)
    {
        StartCoroutine(PostToggleSelectionToFlask(toggleValue, isSelected));
    }

    private IEnumerator PostToggleSelectionToFlask(string toggleValue, bool isSelected)
    {
        string url = flaskURL + "/api/toggle_selection";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"toggle_value\":\"" + toggleValue + "\",\"is_selected\":" + isSelected.ToString().ToLower() + ",\"action\":\"toggle_change\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    // Flask web app integration - Send drag drop selection
    private void SendDragDropSelectionToFlask(string buttonText)
    {
        StartCoroutine(PostDragDropSelectionToFlask(buttonText));
    }

    private IEnumerator PostDragDropSelectionToFlask(string buttonText)
    {
        string url = flaskURL + "/api/dragdrop_selection";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"selected_button\":\"" + buttonText + "\",\"action\":\"button_click\"}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    // Flask web app integration - Send multiple choice submission
    private void SendMultipleChoiceSubmissionToFlask(string allAnswers, float scorePercentage, int answerCount)
    {
        StartCoroutine(PostMultipleChoiceSubmissionToFlask(allAnswers, scorePercentage, answerCount));
    }

    private IEnumerator PostMultipleChoiceSubmissionToFlask(string allAnswers, float scorePercentage, int answerCount)
    {
        string url = flaskURL + "/api/multiple_choice_submission";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"all_answers\":\"" + allAnswers + "\",\"score_percentage\":" + scorePercentage + ",\"answer_count\":" + answerCount + ",\"is_correct\":" + (scorePercentage >= passingScorePercentage).ToString().ToLower() + "}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    private float CalculateMultipleChoiceScore(List<string> selectedAnswers)
    {
        if (selectedAnswers.Count == 0) return 0f;

        int correctCount = 0;
        foreach (string answer in selectedAnswers)
        {
            if (correctAnswers.Contains(answer.ToLower()))
            {
                correctCount++;
            }
        }

        return (float)correctCount / selectedAnswers.Count * 100f;
    }

    private void ShowMultipleChoiceFeedback(string message, bool isPositive)
    {
        if (multipleChoiceFeedbackText != null)
        {
            multipleChoiceFeedbackText.text = message;
            multipleChoiceFeedbackText.color = isPositive ? Color.green : Color.red;
        }
    }

    private IEnumerator HandleSingleAnswerAttack(string answer)
    {
        if (enemy1 == null || isProcessingAttack || player == null) yield break;

        isProcessingAttack = true;

        Vector2 targetPos = new Vector2(enemy1.anchoredPosition.x - attackOffset, enemy1.anchoredPosition.y);
        yield return StartCoroutine(MovePlayerTo(targetPos));

        yield return StartCoroutine(ShowSpeechBubble(playerSpeechBubble, playerSpeechText, $"I choose: {answer}", 1.5f));

        bool isCorrect = correctAnswers.Contains(answer.ToLower());
        string resultText = isCorrect ? "Correct! Well done!" : "Wrong! Try again!";

        yield return StartCoroutine(ShowSpeechBubble(enemySpeechBubble, enemySpeechText, resultText, 2f));

        yield return StartCoroutine(MovePlayerTo(originalPos));

        if (isCorrect)
        {
            AddProgress(25f);
        }

        // Send single answer result to Flask web app
        SendSingleAnswerResultToFlask(answer, isCorrect);

        if (clearAnswersAfterSubmission && dropZone != null)
        {
            yield return new WaitForSeconds(clearDelay);
            dropZone.ClearDropZone();
        }

        isProcessingAttack = false;
    }

    // Flask web app integration - Send single answer result
    private void SendSingleAnswerResultToFlask(string answer, bool isCorrect)
    {
        StartCoroutine(PostSingleAnswerResultToFlask(answer, isCorrect));
    }

    private IEnumerator PostSingleAnswerResultToFlask(string answer, bool isCorrect)
    {
        string url = flaskURL + "/api/single_answer_result";
        
        // Create JSON data for Flask
        string jsonData = "{\"student_id\":" + studentId + ",\"answer\":\"" + answer + "\",\"is_correct\":" + isCorrect.ToString().ToLower() + ",\"progress_added\":" + (isCorrect ? 25 : 0) + "}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    private IEnumerator HandleMultipleAnswerAttack(string answers, float scorePercentage)
    {
        if (enemy1 == null || isProcessingAttack || player == null) yield break;

        isProcessingAttack = true;

        Vector2 targetPos = new Vector2(enemy1.anchoredPosition.x - attackOffset, enemy1.anchoredPosition.y);
        yield return StartCoroutine(MovePlayerTo(targetPos));

        yield return StartCoroutine(ShowSpeechBubble(playerSpeechBubble, playerSpeechText, $"My answers: {answers}", 2f));

        bool isCorrect = scorePercentage >= passingScorePercentage;
        string resultText = isCorrect ?
            $"Excellent! {scorePercentage:F0}% correct!" :
            $"Try harder! Only {scorePercentage:F0}% correct.";

        yield return StartCoroutine(ShowSpeechBubble(enemySpeechBubble, enemySpeechText, resultText, 2f));

        yield return StartCoroutine(MovePlayerTo(originalPos));

        if (isCorrect)
        {
            AddProgress(25f);
            if (hasMultipleChoiceComponents)
            {
                ShowMultipleChoiceFeedback($"Success! +25 progress. Score: {scorePercentage:F0}%", true);
            }
        }
        else
        {
            AddProgress(10f);
            if (hasMultipleChoiceComponents)
            {
                ShowMultipleChoiceFeedback($"Keep trying! +10 progress. Score: {scorePercentage:F0}%", false);
            }
        }

        if (clearAnswersAfterSubmission && hasMultipleChoiceComponents)
        {
            yield return new WaitForSeconds(clearDelay);
            foreach (var toggle in answerToggles)
            {
                if (toggle != null) toggle.isOn = false;
            }
        }

        isProcessingAttack = false;
    }
}
