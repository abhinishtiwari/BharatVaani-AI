"""
app.py

This is the central Flask web application for BharatVaani AI.

It connects the user interface (HTML/CSS/JS) with the backend NLP processing
pipeline (text normalization, language detection, and MarianMT translation).

Flow:
Browser -> POST /translate -> normalize_text -> detect_language -> translate_text -> JSON response -> Browser
"""

import sys
from flask import Flask, render_template, request, jsonify

# Ensure UTF-8 encoding for standard output and error on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


# Import custom modular components
from text_processor import normalize_text, MAX_INPUT_LENGTH
from language_detector import detect_language
from translator import translation_engine

# Initialize Flask application
app = Flask(__name__)


@app.route("/")
def render_homepage():
    """
    Serve the main user interface template (index.html).
    """
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def check_health_status():
    """
    Health check endpoint to verify server status.
    """
    return jsonify({
        "status": "healthy",
        "service": "BharatVaani AI",
        "version": "1.0.0"
    }), 200


@app.route("/detect-language", methods=["POST"])
def detect_input_language():
    """
    API Endpoint to detect the language (Hindi or English) of the provided text.
    """
    request_data = request.get_json()

    if not request_data or not isinstance(request_data, dict):
        return jsonify({
            "success": False,
            "error": "Invalid request format. Expected JSON payload."
        }), 400

    raw_input_text = request_data.get("text", "")

    try:
        cleaned_text = normalize_text(raw_input_text)
        detection_result = detect_language(cleaned_text)

        return jsonify({
            "success": True,
            "detected_language_code": detection_result["detected_language_code"],
            "language_name": detection_result["language_name"],
            "confidence_score": detection_result["confidence_score"]
        }), 200

    except ValueError as validation_error:
        return jsonify({
            "success": False,
            "error": str(validation_error)
        }), 400
    except Exception as server_error:
        return jsonify({
            "success": False,
            "error": f"An unexpected error occurred during language detection: {str(server_error)}"
        }), 500


@app.route("/translate", methods=["POST"])
def process_translation():
    """
    API Endpoint to process text translation request.

    Expects JSON body:
    {
        "text": "input sentence",
        "direction": "hi-en" or "en-hi"
    }
    """
    # Read the JSON data sent by the browser
    request_data = request.get_json()

    if not request_data or not isinstance(request_data, dict):
        return jsonify({
            "success": False,
            "error": "Invalid request payload. Please send valid JSON."
        }), 400

    # Extract user input text and translation direction
    raw_input_text = request_data.get("text", "")
    translation_direction = request_data.get("direction", "")

    # Validate translation direction presence
    if not translation_direction:
        return jsonify({
            "success": False,
            "error": "Please select a valid translation direction ('hi-en' or 'en-hi')."
        }), 400

    try:
        # Step 1: Normalize user text (trim whitespace, normalize Unicode)
        cleaned_text = normalize_text(raw_input_text)

        # Step 2: Automatically detect input language to verify or assist direction choice
        detection_result = detect_language(cleaned_text)

        # Step 3: Send normalized text to the translation engine
        translated_text = translation_engine.translate_text(
            cleaned_text,
            translation_direction
        )

        # Step 4: Return formatted JSON response to browser
        return jsonify({
            "success": True,
            "original_text": cleaned_text,
            "translated_text": translated_text,
            "translation_direction": translation_direction,
            "detected_language": detection_result["language_name"]
        }), 200

    except ValueError as validation_error:
        # Return 400 Bad Request for validation failures
        return jsonify({
            "success": False,
            "error": str(validation_error)
        }), 400

    except Exception as translation_error:
        # Return 500 Internal Server Error for translation failure
        error_message = str(translation_error)
        return jsonify({
            "success": False,
            "error": f"Failed to perform translation: {error_message}"
        }), 500




if __name__ == "__main__":
    print("Starting BharatVaani AI Server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


