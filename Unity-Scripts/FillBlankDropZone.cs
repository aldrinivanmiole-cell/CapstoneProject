using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using UnityEngine.Networking;
using System.Collections;

public class FillBlankDropZone : MonoBehaviour, IDropHandler, IPointerEnterHandler, IPointerExitHandler
{
    [Header("Drop Zone Configuration")]
    public GameStageManager attackController;
    public bool allowMultipleButtons = false;
    public bool autoTriggerOnDrop = true;
    public Vector2 buttonSpacing = new Vector2(120f, 0f);

    [Header("Flask Integration")]
    public string flaskServerUrl = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public bool sendToFlask = true;

    [Header("Visual Feedback")]
    public Color highlightColor = new Color(0.8f, 1f, 0.8f, 0.3f);
    public bool showDropFeedback = true;

    private Image backgroundImage;
    private Color originalColor;
    private List<DraggableAnswer> droppedButtons = new List<DraggableAnswer>();

    private void Start()
    {
        InitializeDropZone();
    }

    private void InitializeDropZone()
    {
        Debug.Log("=== DROP ZONE INITIALIZATION ===");

        // Auto-find GameStageManager if not assigned using the new Unity method
        if (attackController == null)
        {
            attackController = FindFirstObjectByType<GameStageManager>();
            if (attackController != null)
            {
                Debug.Log("GameStageManager found automatically!");
            }
            else
            {
                Debug.LogError("GameStageManager not found! Please assign it manually in the Inspector.");
            }
        }

        Debug.Log($"AttackController assigned: {attackController != null}");

        // Setup background image for receiving events
        backgroundImage = GetComponent<Image>();
        if (backgroundImage == null)
        {
            backgroundImage = gameObject.AddComponent<Image>();
            backgroundImage.color = new Color(1, 1, 1, 0.01f); // Nearly transparent but receives events
            Debug.Log("Added background Image component to DropZone");
        }
        originalColor = backgroundImage.color;

        // Ensure raycast target is enabled
        backgroundImage.raycastTarget = true;

        if (GetComponent<RectTransform>() == null)
        {
            Debug.LogError("DropZone must be on a UI GameObject with RectTransform!");
        }
    }

    public void OnPointerEnter(PointerEventData eventData)
    {
        if (showDropFeedback && eventData.pointerDrag != null)
        {
            backgroundImage.color = highlightColor;
            Debug.Log("Drop zone highlighted");
        }
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        if (showDropFeedback)
        {
            backgroundImage.color = originalColor;
            Debug.Log("Drop zone highlight removed");
        }
    }

    public void OnDrop(PointerEventData eventData)
    {
        Debug.Log("=== ON DROP TRIGGERED ===");

        // Remove highlight
        if (showDropFeedback)
        {
            backgroundImage.color = originalColor;
        }

        GameObject droppedObj = eventData.pointerDrag;
        Debug.Log($"Dropped object: {(droppedObj != null ? droppedObj.name : "NULL")}");

        // Try to find GameStageManager again if it's null using the new method
        if (attackController == null)
        {
            Debug.LogWarning("AttackController is null, trying to find it...");
            attackController = FindFirstObjectByType<GameStageManager>();
        }

        Debug.Log($"Attack controller: {(attackController != null ? attackController.name : "NULL")}");

        if (droppedObj == null)
        {
            Debug.LogError("No object was dropped!");
            return;
        }

        if (attackController == null)
        {
            Debug.LogError("GameStageManager not found! Make sure there's a GameStageManager in the scene and it's assigned to this DropZone.");
            return;
        }

        DraggableAnswer draggableAnswer = droppedObj.GetComponent<DraggableAnswer>();
        Button droppedButton = droppedObj.GetComponent<Button>();

        Debug.Log($"DraggableAnswer component: {draggableAnswer != null}");
        Debug.Log($"Button component: {droppedButton != null}");

        if (droppedButton == null)
        {
            Debug.LogError($"Dropped object '{droppedObj.name}' doesn't have a Button component!");
            return;
        }

        if (draggableAnswer == null)
        {
            Debug.LogError($"Dropped object '{droppedObj.name}' doesn't have a DraggableAnswer component!");
            return;
        }

        if (droppedButtons.Contains(draggableAnswer))
        {
            Debug.LogWarning("Button already in drop zone!");
            return;
        }

        // Clear existing buttons if only one allowed
        if (!allowMultipleButtons)
        {
            ClearDropZone();
        }

        // Add button to zone
        AddButtonToZone(draggableAnswer, droppedButton);

        // Trigger attack
        if (autoTriggerOnDrop)
        {
            string answer = GetButtonText(droppedButton);
            Debug.Log($"Triggering attack with answer: '{answer}'");

            if (!string.IsNullOrEmpty(answer))
            {
                attackController.TriggerAttackWithEnemy(answer);
            }
            else
            {
                Debug.LogError("Button text is empty!");
            }
        }
    }

    private void AddButtonToZone(DraggableAnswer draggableAnswer, Button button)
    {
        Debug.Log($"Adding button '{button.name}' to drop zone");

        // Set as child of drop zone
        draggableAnswer.transform.SetParent(transform);

        // Position in drop zone
        PositionButtonInDropZone(draggableAnswer.GetComponent<RectTransform>());

        // Mark as dropped
        draggableAnswer.SetDroppedInZone(true);

        // Add to tracking list
        droppedButtons.Add(draggableAnswer);

        // Send zone status to Flask
        if (sendToFlask)
        {
            StartCoroutine(SendZoneStatusToFlask(droppedButtons.Count, true));
        }

        // Animate drop
        StartCoroutine(AnimateButtonDrop(draggableAnswer.transform));
    }

    private System.Collections.IEnumerator AnimateButtonDrop(Transform buttonTransform)
    {
        Vector3 originalScale = buttonTransform.localScale;

        float time = 0f;
        while (time < 0.3f)
        {
            time += Time.deltaTime;
            float scale = Mathf.Lerp(1.1f, 1f, time / 0.3f);
            buttonTransform.localScale = originalScale * scale;
            yield return null;
        }

        buttonTransform.localScale = originalScale;
    }

    private string GetButtonText(Button button)
    {
        // Try TMP_Text first
        TMP_Text tmpText = button.GetComponentInChildren<TMP_Text>();
        if (tmpText != null && !string.IsNullOrEmpty(tmpText.text))
        {
            return tmpText.text;
        }

        // Try regular Text
        Text regularText = button.GetComponentInChildren<Text>();
        if (regularText != null && !string.IsNullOrEmpty(regularText.text))
        {
            return regularText.text;
        }

        // Fallback to button name
        Debug.LogWarning($"No text found on button '{button.name}', using button name as answer");
        return button.name;
    }

    private void PositionButtonInDropZone(RectTransform buttonRect)
    {
        if (allowMultipleButtons)
        {
            int buttonIndex = droppedButtons.Count;
            Vector2 position = new Vector2(buttonIndex * buttonSpacing.x, buttonIndex * buttonSpacing.y);
            buttonRect.anchoredPosition = position;
        }
        else
        {
            // Center the button
            buttonRect.anchoredPosition = Vector2.zero;
        }
    }

    public void ClearDropZone()
    {
        Debug.Log($"Clearing drop zone with {droppedButtons.Count} buttons");

        for (int i = droppedButtons.Count - 1; i >= 0; i--)
        {
            if (droppedButtons[i] != null)
            {
                droppedButtons[i].ResetToOriginalPosition();
            }
        }
        droppedButtons.Clear();

        // Send cleared status to Flask
        if (sendToFlask)
        {
            StartCoroutine(SendZoneStatusToFlask(0, false));
        }
    }

    public List<Button> GetButtonsInZone()
    {
        List<Button> buttons = new List<Button>();
        foreach (var draggable in droppedButtons)
        {
            if (draggable != null)
            {
                Button btn = draggable.GetComponent<Button>();
                if (btn != null) buttons.Add(btn);
            }
        }
        return buttons;
    }

    public int GetButtonCount()
    {
        return droppedButtons.Count;
    }

    public bool HasButtons()
    {
        return droppedButtons.Count > 0;
    }

    public void TriggerAttackWithCurrentButtons()
    {
        if (attackController == null || droppedButtons.Count == 0) return;

        foreach (var draggable in droppedButtons)
        {
            Button btn = draggable.GetComponent<Button>();
            if (btn != null)
            {
                string answer = GetButtonText(btn);
                attackController.TriggerAttackWithEnemy(answer);
                
                // Send to Flask server
                if (sendToFlask)
                {
                    StartCoroutine(SendDropEventToFlask(answer, "zone_drop"));
                }
                break;
            }
        }
    }

    // Flask Integration Methods
    private IEnumerator SendDropEventToFlask(string answer, string eventType)
    {
        string jsonData = $"{{\"answer\":\"{answer}\", \"event_type\":\"{eventType}\", \"timestamp\":\"{System.DateTime.Now:yyyy-MM-dd HH:mm:ss}\"}}";
        
        using (UnityWebRequest request = new UnityWebRequest($"{flaskServerUrl}/api/drop-event", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"Successfully sent drop event to Flask: {answer}");
            }
            else
            {
                Debug.LogWarning($"Failed to send drop event to Flask: {request.error}");
            }
        }
    }

    private IEnumerator SendZoneStatusToFlask(int buttonCount, bool hasButtons)
    {
        string jsonData = $"{{\"button_count\":{buttonCount}, \"has_buttons\":{hasButtons.ToString().ToLower()}, \"timestamp\":\"{System.DateTime.Now:yyyy-MM-dd HH:mm:ss}\"}}";
        
        using (UnityWebRequest request = new UnityWebRequest($"{flaskServerUrl}/api/zone-status", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Successfully sent zone status to Flask");
            }
            else
            {
                Debug.LogWarning($"Failed to send zone status to Flask: {request.error}");
            }
        }
    }

    // Manual assignment method for testing
    [ContextMenu("Find GameStageManager")]
    public void FindGameStageManager()
    {
        attackController = FindFirstObjectByType<GameStageManager>();
        if (attackController != null)
        {
            Debug.Log($"Found GameStageManager: {attackController.name}");
        }
        else
        {
            Debug.LogError("GameStageManager not found in scene!");
        }
    }
}
