"""
test_app.py

Pytest and Unittest compatible suite for testing BharatVaani AI application modules
and Flask API endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import backend modules to test
from text_processor import normalize_text, MAX_INPUT_LENGTH
from language_detector import detect_language, HINDI_LANGUAGE_CODE, ENGLISH_LANGUAGE_CODE, UNKNOWN_LANGUAGE_CODE
from translator import TranslationEngine, HINDI_TO_ENGLISH_DIRECTION, ENGLISH_TO_HINDI_DIRECTION
from app import app


# =====================================================================
# 1. Text Processor Unit Tests
# =====================================================================

class TestTextProcessor(unittest.TestCase):

    def test_normalize_text_valid_input(self):
        """Verify that text normalization trims spaces and cleans input."""
        input_text = "   नमस्ते   भारत  "
        expected_output = "नमस्ते भारत"
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_text_empty_input_raises_error(self):
        """Verify that empty string input raises a ValueError."""
        with self.assertRaises(ValueError):
            normalize_text("   ")

    def test_normalize_text_exceeds_max_length_raises_error(self):
        """Verify that text longer than MAX_INPUT_LENGTH raises a ValueError."""
        excessive_input_text = "a" * (MAX_INPUT_LENGTH + 1)
        with self.assertRaises(ValueError):
            normalize_text(excessive_input_text)


# =====================================================================
# 2. Language Detector Unit Tests
# =====================================================================

class TestLanguageDetector(unittest.TestCase):

    def test_detect_language_hindi(self):
        """Verify that Devanagari script is detected as Hindi."""
        hindi_text = "नमस्ते आप कैसे हैं?"
        result = detect_language(hindi_text)
        self.assertEqual(result["detected_language_code"], HINDI_LANGUAGE_CODE)
        self.assertEqual(result["language_name"], "Hindi")
        self.assertGreater(result["confidence_score"], 0.8)

    def test_detect_language_english(self):
        """Verify that Latin script is detected as English."""
        english_text = "Welcome to BharatVaani AI"
        result = detect_language(english_text)
        self.assertEqual(result["detected_language_code"], ENGLISH_LANGUAGE_CODE)
        self.assertEqual(result["language_name"], "English")
        self.assertGreater(result["confidence_score"], 0.8)

    def test_detect_language_numeric_or_unknown(self):
        """Verify that numbers or symbols return Unknown language code."""
        numeric_text = "123456 !!!"
        result = detect_language(numeric_text)
        self.assertEqual(result["detected_language_code"], UNKNOWN_LANGUAGE_CODE)
        self.assertEqual(result["language_name"], "Unknown")
        self.assertEqual(result["confidence_score"], 0.0)


# =====================================================================
# 3. Translator Engine Unit Tests
# =====================================================================

class TestTranslationEngine(unittest.TestCase):

    def test_translator_unsupported_direction_raises_error(self):
        """Verify that an invalid translation direction raises ValueError."""
        engine = TranslationEngine()
        with self.assertRaises(ValueError):
            engine.translate_text("hello", "fr-en")

    def test_post_process_hindi_translation(self):
        """Verify that Urdu/loanwords are converted to Standard Hindi."""
        from translator import post_process_hindi_translation
        self.assertEqual(post_process_hindi_translation("सलाम"), "नमस्ते")
        self.assertEqual(post_process_hindi_translation("शुक्रिया"), "धन्यवाद")

    @patch.object(TranslationEngine, 'translate_hindi_to_english')
    def test_translator_hindi_to_english_routing(self, mock_translate):
        """Verify that hi-en direction calls translate_hindi_to_english."""
        mock_translate.return_value = "Hello"
        engine = TranslationEngine()

        result = engine.translate_text("नमस्ते", HINDI_TO_ENGLISH_DIRECTION)
        self.assertEqual(result, "Hello")
        mock_translate.assert_called_once_with("नमस्ते")



# =====================================================================
# 4. Flask Application Integration Tests
# =====================================================================

class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        """Create Flask test client fixture for unittest."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_route(self):
        """Verify that GET / renders homepage successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BharatVaani", response.data)

    def test_health_check_route(self):
        """Verify that GET /health returns status 200 and healthy JSON."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")

    def test_detect_language_endpoint(self):
        """Verify POST /detect-language endpoint."""
        response = self.client.post(
            "/detect-language",
            json={"text": "नमस्ते भारत"}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["detected_language_code"], "hi")

    def test_translate_endpoint_invalid_payload(self):
        """Verify POST /translate returns 400 for empty or invalid payload."""
        response = self.client.post(
            "/translate",
            json={"text": "", "direction": "hi-en"}
        )
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("error", json_data)

    @patch('app.translation_engine.translate_text')
    def test_translate_endpoint_success(self, mock_translate_text):
        """Verify POST /translate returns successful translation response when mocked."""
        mock_translate_text.return_value = "Hello world"

        response = self.client.post(
            "/translate",
            json={
                "text": "नमस्ते दुनिया",
                "direction": "hi-en"
            }
        )

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["translated_text"], "Hello world")
        self.assertEqual(json_data["translation_direction"], "hi-en")


if __name__ == "__main__":
    unittest.main()

