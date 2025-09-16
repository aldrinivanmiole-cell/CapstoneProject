using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;
using System.Collections;

public class DraggableAnswer : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
{
    [Header("Answer Settings")]
    public string answerText = "";
    public int correctBlankIndex = 0;

    [Header("Drag Settings")]
    public float dragAlpha = 0.6f;
    public bool returnOnInvalidDrop = true;

    [Header("Web App Connection")]
    public string flaskURL = "https://capstoneproject-jq2h.onrender.com"; // Production Flask server URL
    // For local development, change to: "http://127.0.0.1:5000"
    public int assignmentId = 1;
    public int studentId = 1;

    private RectTransform rectTransform;
    private CanvasGroup canvasGroup;
    private Vector2 originalPosition;
    private Transform originalParent;
    private Canvas parentCanvas;
    private bool isDroppedInZone = false;
    private float originalAlpha;
    private int originalSiblingIndex;

    private void Awake()
    {
        InitializeComponents();
    }

    private void InitializeComponents()
    {
        rectTransform = GetComponent<RectTransform>();
        canvasGroup = GetComponent<CanvasGroup>();

        // Add CanvasGroup if it doesn't exist
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }

        originalPosition = rectTransform.anchoredPosition;
        originalParent = transform.parent;
        originalAlpha = canvasGroup.alpha;
        originalSiblingIndex = transform.GetSiblingIndex();
        parentCanvas = GetComponentInParent<Canvas>();

        // Auto-detect answer text if not set
        if (string.IsNullOrEmpty(answerText))
        {
            TMP_Text tmpText = GetComponentInChildren<TMP_Text>();
            if (tmpText != null)
            {
                answerText = tmpText.text;
            }
            else
            {
                Text regularText = GetComponentInChildren<Text>();
                if (regularText != null)
                {
                    answerText = regularText.text;
                }
                else
                {
                    answerText = gameObject.name;
                }
            }
        }
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        // Prevent button click events during drag
        canvasGroup.blocksRaycasts = false;
        canvasGroup.alpha = dragAlpha;

        // Bring to front for better visibility
        transform.SetAsLastSibling();
        isDroppedInZone = false;

        // Add visual feedback
        transform.localScale = Vector3.one * 1.05f;
    }

    public void OnDrag(PointerEventData eventData)
    {
        if (parentCanvas != null)
        {
            // Account for canvas scale factor
            Vector2 deltaPosition = eventData.delta / parentCanvas.scaleFactor;
            rectTransform.anchoredPosition += deltaPosition;
        }
        else
        {
            rectTransform.anchoredPosition += eventData.delta;
        }
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        // Restore interaction and visual state
        canvasGroup.blocksRaycasts = true;
        canvasGroup.alpha = originalAlpha;
        transform.localScale = Vector3.one;

        // Check what we dropped on
        GameObject droppedOn = eventData.pointerCurrentRaycast.gameObject;
        
        if (droppedOn != null)
        {
            FillBlankDropZone dropZone = droppedOn.GetComponent<FillBlankDropZone>();
            if (dropZone != null)
            {
                HandleDrop(dropZone);
                return;
            }
        }

        // Check if dropped on a valid zone
        if (!isDroppedInZone && returnOnInvalidDrop)
        {
            ResetToOriginalPosition();
        }
    }

    private void HandleDrop(FillBlankDropZone dropZone)
    {
        // For now, accept any drop as valid - Flask will handle validation
        SetDroppedInZone(true);
        transform.SetParent(dropZone.transform);
        rectTransform.anchoredPosition = Vector2.zero;
        
        // Send to Flask web app - let Flask determine if correct
        SendAnswerToFlask(answerText, correctBlankIndex, true);
    }

    // Flask web app integration
    private void SendAnswerToFlask(string answer, int blankIndex, bool isCorrect)
    {
        StartCoroutine(PostAnswerToFlask(answer, blankIndex, isCorrect));
    }
    
    private IEnumerator PostAnswerToFlask(string answer, int blankIndex, bool isCorrect)
    {
        string url = flaskURL + "/api/submit_fill_blank";
        
        // Create JSON data for Flask
        string jsonData = "{\"answer\":\"" + answer + "\",\"blank_index\":" + blankIndex + ",\"is_correct\":" + isCorrect.ToString().ToLower() + "}";
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        request.Dispose();
    }

    public void SetDroppedInZone(bool dropped)
    {
        isDroppedInZone = dropped;
    }

    public void ResetToOriginalPosition()
    {
        if (originalParent != null)
        {
            transform.SetParent(originalParent);
            transform.SetSiblingIndex(originalSiblingIndex);
            rectTransform.anchoredPosition = originalPosition;
            canvasGroup.alpha = originalAlpha;
            transform.localScale = Vector3.one;
            isDroppedInZone = false;
        }
    }

    // Public method to check if this draggable is currently in a drop zone
    public bool IsInDropZone()
    {
        return isDroppedInZone;
    }

    // Method to get the original position
    public Vector2 GetOriginalPosition()
    {
        return originalPosition;
    }

    // Method to set which blank this answer belongs to
    public void SetCorrectBlank(int blankIndex)
    {
        correctBlankIndex = blankIndex;
    }

    // Method to check if correctly placed
    public bool IsCorrectlyPlaced()
    {
        return isDroppedInZone;
    }
}
