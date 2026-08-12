"""
text_processor.py

This file contains text normalization and validation utilities for BharatVaani AI.

Before passing human input to natural language processing models, the text
must be cleaned, stripped of extra spaces, and checked against reasonable length limits.

This ensures consistent NLP results and prevents memory errors on long strings.
"""

import unicodedata

# Maximum number of characters accepted in a single translation request
MAX_INPUT_LENGTH = 1000

# Minimum number of characters required for processing
MIN_INPUT_LENGTH = 1


def normalize_text(input_text):
    """
    Clean and normalize user-provided text for NLP processing.

    Args:
        input_text (str): The raw text entered by the user.

    Returns:
        str: Normalized text with consistent Unicode formatting and clean whitespace.

    Raises:
        ValueError: If input_text is empty or exceeds the maximum length limit.
    """
    # Verify that input_text is a string
    if not isinstance(input_text, str):
        raise TypeError("Input text must be a string.")

    # Remove leading and trailing whitespace characters
    trimmed_text = input_text.strip()

    # Calculate character count after trimming
    character_count = len(trimmed_text)

    # Check if text is too short
    if character_count < MIN_INPUT_LENGTH:
        raise ValueError("Input text cannot be empty.")

    # Check if text exceeds maximum character limit
    if character_count > MAX_INPUT_LENGTH:
        raise ValueError(
            f"Input text length ({character_count} characters) exceeds "
            f"the maximum allowed limit of {MAX_INPUT_LENGTH} characters."
        )

    # Normalize Unicode characters to NFKC format.
    # NFKC (Normalization Form Compatibility Composition) converts compatibility
    # characters into standard forms (e.g., standardizing Devanagari numerals or symbols).
    unicode_normalized_text = unicodedata.normalize("NFKC", trimmed_text)

    # Collapse multiple consecutive spaces into a single space
    normalized_words = unicode_normalized_text.split()
    cleaned_normalized_text = " ".join(normalized_words)

    return cleaned_normalized_text
