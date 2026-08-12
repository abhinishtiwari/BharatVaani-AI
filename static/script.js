/*
script.js

Handles frontend interactions and HTTP communication between the HTML interface
and the Flask backend (/translate and /detect-language endpoints).

No external API dependencies or heavy JS frameworks are used.
*/

// Execute script after DOM content is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    
    // DOM Element References
    const inputTextElement = document.getElementById("inputText");
    const translationDirectionElement = document.getElementById("translationDirection");
    const translateButtonElement = document.getElementById("translateButton");
    const swapDirectionButtonElement = document.getElementById("swapDirectionButton");
    const clearTextButtonElement = document.getElementById("clearTextButton");
    const copyTextButtonElement = document.getElementById("copyTextButton");
    
    const translatedTextElement = document.getElementById("translatedText");
    const currentCharCountElement = document.getElementById("currentCharCount");
    const detectedLanguageBadgeElement = document.getElementById("detectedLanguageBadge");
    const outputLanguageBadgeElement = document.getElementById("outputLanguageBadge");
    const statusIndicatorElement = document.getElementById("statusIndicator");
    const sampleChipElements = document.querySelectorAll(".sample-chip");

    /**
     * Updates character counter as user types into the input text area.
     */
    function updateCharacterCount() {
        const inputText = inputTextElement.value;
        const currentLength = inputText.length;
        currentCharCountElement.textContent = currentLength;
    }

    /**
     * Automatically calls language detection API when input text changes.
     */
    async function triggerLanguageDetection() {
        const inputText = inputTextElement.value.trim();

        if (inputText.length === 0) {
            detectedLanguageBadgeElement.textContent = "Auto-detecting script...";
            return;
        }

        try {
            const response = await fetch("/detect-language", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: inputText
                })
            });

            const responseData = await response.json();

            if (responseData.success) {
                const detectedLanguageName = responseData.language_name;
                const confidenceScore = Math.round(responseData.confidence_score * 100);
                detectedLanguageBadgeElement.textContent = `Detected: ${detectedLanguageName} (${confidenceScore}%)`;

                // Automatically adjust direction dropdown if confidently detected
                if (responseData.detected_language_code === "hi") {
                    translationDirectionElement.value = "hi-en";
                    outputLanguageBadgeElement.textContent = "Target: English";
                } else if (responseData.detected_language_code === "en") {
                    translationDirectionElement.value = "en-hi";
                    outputLanguageBadgeElement.textContent = "Target: Hindi";
                }
            }
        } catch (error) {
            console.error("Language detection error:", error);
        }
    }


    /**
     * Sends input text and selected translation direction to the Flask server.
     */
    async function executeTranslation() {
        const inputText = inputTextElement.value.trim();
        const translationDirection = translationDirectionElement.value;

        // Input validation before calling server
        if (!inputText) {
            statusIndicatorElement.textContent = "Please enter text before translating.";
            translatedTextElement.innerHTML = `<span class="placeholder-text">Please enter some text above to translate.</span>`;
            return;
        }

        // Show loading state on button and status
        statusIndicatorElement.textContent = "Translating with MarianMT Neural Model...";
        translateButtonElement.disabled = true;

        try {
            // POST request directly connected to Flask /translate route
            const response = await fetch("/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: inputText,
                    direction: translationDirection
                })
            });

            const translationResponseData = await response.json();

            if (response.ok && translationResponseData.success) {
                // Render translated text
                translatedTextElement.textContent = translationResponseData.translated_text;
                statusIndicatorElement.textContent = "Translation Complete";
            } else {
                // Render error message from backend
                const errorMessage = translationResponseData.error || "Translation failed.";
                translatedTextElement.textContent = `Error: ${errorMessage}`;
                statusIndicatorElement.textContent = "Error occurred";
            }
        } catch (error) {
            console.error("Translation request failed:", error);
            translatedTextElement.textContent = "Network error: Unable to reach Flask backend server.";
            statusIndicatorElement.textContent = "Network Error";
        } finally {
            translateButtonElement.disabled = false;
        }
    }

    /**
     * Swaps translation direction and target labels.
     */
    function swapTranslationDirection() {
        if (translationDirectionElement.value === "hi-en") {
            translationDirectionElement.value = "en-hi";
            outputLanguageBadgeElement.textContent = "Target: Hindi";
        } else {
            translationDirectionElement.value = "hi-en";
            outputLanguageBadgeElement.textContent = "Target: English";
        }

        // If there is existing translation text, swap input and translated text
        const currentTranslation = translatedTextElement.textContent;
        if (currentTranslation && !currentTranslation.includes("will appear here") && !currentTranslation.includes("Error:")) {
            inputTextElement.value = currentTranslation;
            updateCharacterCount();
            executeTranslation();
        }
    }

    /**
     * Copies translation result to system clipboard.
     */
    async function copyTranslationToClipboard() {
        const textToCopy = translatedTextElement.textContent;
        if (!textToCopy || textToCopy.includes("will appear here")) {
            return;
        }

        try {
            await navigator.clipboard.writeText(textToCopy);
            copyTextButtonElement.textContent = "Copied!";
            setTimeout(() => {
                copyTextButtonElement.textContent = "Copy Translation";
            }, 2000);
        } catch (err) {
            console.error("Clipboard copy failed:", err);
        }
    }

    // Event Listeners setup
    inputTextElement.addEventListener("input", function () {
        updateCharacterCount();
        triggerLanguageDetection();
    });

    translateButtonElement.addEventListener("click", executeTranslation);
    swapDirectionButtonElement.addEventListener("click", swapTranslationDirection);
    
    translationDirectionElement.addEventListener("change", function () {
        if (translationDirectionElement.value === "hi-en") {
            outputLanguageBadgeElement.textContent = "Target: English";
        } else {
            outputLanguageBadgeElement.textContent = "Target: Hindi";
        }
    });

    
    clearTextButtonElement.addEventListener("click", function () {
        inputTextElement.value = "";
        translatedTextElement.innerHTML = `<span class="placeholder-text">Translation will appear here in real-time...</span>`;
        updateCharacterCount();
        detectedLanguageBadgeElement.textContent = "Auto-detecting script...";
        statusIndicatorElement.textContent = "Cleared";
    });

    copyTextButtonElement.addEventListener("click", copyTranslationToClipboard);

    // Bind Sample Chip Buttons for quick testing
    sampleChipElements.forEach(function (chipButton) {
        chipButton.addEventListener("click", function () {
            const sampleText = chipButton.getAttribute("data-text");
            const sampleDirection = chipButton.getAttribute("data-direction");

            inputTextElement.value = sampleText;
            translationDirectionElement.value = sampleDirection;

            updateCharacterCount();
            triggerLanguageDetection();
            executeTranslation();
        });
    });

});
