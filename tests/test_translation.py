"""
test_translation.py

Automated test suite verifying English to Hindi and Hindi to English translation accuracy,
common fixed expression mapping, post-processing refinement, and Devanagari validation rules.
"""

import unittest
from translator import translation_engine, contains_devanagari, EN_TO_HI, HI_TO_EN


class TestTranslation(unittest.TestCase):

    def test_contains_devanagari(self):
        """Verify Devanagari script detector helper function."""
        self.assertTrue(contains_devanagari("नमस्ते"))
        self.assertTrue(contains_devanagari("आप कैसे हैं?"))
        self.assertFalse(contains_devanagari("Hello"))
        self.assertFalse(contains_devanagari("Thank you"))

    def test_english_to_hindi_greetings(self):
        """Verify priority English to Hindi greetings and common expressions."""
        self.assertEqual(translation_engine.translate_text("Hello", EN_TO_HI), "नमस्ते")
        self.assertEqual(translation_engine.translate_text("hello", EN_TO_HI), "नमस्ते")
        self.assertEqual(translation_engine.translate_text("Hi", EN_TO_HI), "नमस्ते")
        self.assertEqual(translation_engine.translate_text("Good morning", EN_TO_HI), "सुप्रभात")
        self.assertEqual(translation_engine.translate_text("Good evening", EN_TO_HI), "शुभ संध्या")
        self.assertEqual(translation_engine.translate_text("Thank you", EN_TO_HI), "धन्यवाद")
        self.assertEqual(translation_engine.translate_text("Thanks", EN_TO_HI), "धन्यवाद")

    def test_english_to_hindi_sentences(self):
        """Verify arbitrary English sentence translations produce Devanagari Hindi text."""
        test_sentences = [
            "How are you?",
            "What is your name?",
            "My name is Abhinish.",
            "I am a student.",
            "Where are you going?",
            "I love India."
        ]

        for sentence in test_sentences:
            translated_hindi = translation_engine.translate_text(sentence, EN_TO_HI)
            self.assertTrue(
                contains_devanagari(translated_hindi),
                f"Translation for '{sentence}' failed to produce Hindi text. Result: '{translated_hindi}'"
            )
            # Verify result does not simply return original English string
            self.assertNotEqual(sentence.strip().lower(), translated_hindi.strip().lower())

    def test_hindi_to_english_phrases(self):
        """Verify Hindi to English translations produce valid English text."""
        test_phrases = [
            ("नमस्ते", "Hello"),
            ("धन्यवाद", "Thank you"),
            ("आप कैसे हैं?", "How are you?")
        ]

        for hindi_input, expected_part in test_phrases:
            translated_english = translation_engine.translate_text(hindi_input, HI_TO_EN)
            self.assertTrue(len(translated_english) > 0)
            self.assertFalse(contains_devanagari(translated_english))


if __name__ == "__main__":
    unittest.main()
