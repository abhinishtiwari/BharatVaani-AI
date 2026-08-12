"""
language_detector.py

This file handles language identification for BharatVaani AI.

It examines the character set of the input string to determine whether
the text is written in Hindi (Devanagari script) or English (Latin script).

No external APIs are used for language detection.
"""

# Explicit language identifier constants
HINDI_LANGUAGE_CODE = "hi"
ENGLISH_LANGUAGE_CODE = "en"
UNKNOWN_LANGUAGE_CODE = "unknown"

# Devanagari script Unicode character boundaries
DEVANAGARI_UNICODE_START = 0x0900
DEVANAGARI_UNICODE_END = 0x097F


def detect_language(input_text):
    """
    Detect whether input_text is Hindi or English based on script character analysis.

    Args:
        input_text (str): Cleaned input string.

    Returns:
        dict: A dictionary containing language, detected_language_code, confidence_score, and language_name.
    """
    if not input_text or not isinstance(input_text, str):
        return {
            "language": UNKNOWN_LANGUAGE_CODE,
            "detected_language_code": UNKNOWN_LANGUAGE_CODE,
            "confidence_score": 0.0,
            "language_name": "Unknown"
        }

    devanagari_character_count = 0
    latin_character_count = 0
    total_alphabetic_character_count = 0

    # Iterate through each character to determine script ownership
    for character in input_text:
        character_code = ord(character)

        # Check if character belongs to Devanagari block (Hindi script)
        if DEVANAGARI_UNICODE_START <= character_code <= DEVANAGARI_UNICODE_END:
            devanagari_character_count += 1
            total_alphabetic_character_count += 1

        # Check if character is a standard Latin letter (English script)
        elif character.isalpha():
            latin_character_count += 1
            total_alphabetic_character_count += 1

    # If no alphabetic characters were found (e.g. only numbers or punctuation)
    if total_alphabetic_character_count == 0:
        return {
            "language": UNKNOWN_LANGUAGE_CODE,
            "detected_language_code": UNKNOWN_LANGUAGE_CODE,
            "confidence_score": 0.0,
            "language_name": "Unknown"
        }

    # Calculate proportion of Devanagari characters vs Latin characters
    hindi_ratio = devanagari_character_count / total_alphabetic_character_count
    english_ratio = latin_character_count / total_alphabetic_character_count

    # Determine dominant language based on character frequency ratio
    if hindi_ratio > english_ratio:
        return {
            "language": HINDI_LANGUAGE_CODE,
            "detected_language_code": HINDI_LANGUAGE_CODE,
            "confidence_score": round(hindi_ratio, 2),
            "language_name": "Hindi"
        }
    else:
        return {
            "language": ENGLISH_LANGUAGE_CODE,
            "detected_language_code": ENGLISH_LANGUAGE_CODE,
            "confidence_score": round(english_ratio, 2),
            "language_name": "English"
        }
