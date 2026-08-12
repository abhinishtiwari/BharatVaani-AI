"""
translator.py

This file contains the translation logic for BharatVaani AI.

It loads pretrained MarianMT Transformer models from HuggingFace to perform:
1. English to Hindi translation (Helsinki-NLP/opus-mt-en-hi)
2. Hindi to English translation (Helsinki-NLP/opus-mt-hi-en)

No external translation APIs are used. All translation happens locally
using PyTorch and HuggingFace Transformers.
"""

import sys
import torch
import sentencepiece
from transformers import MarianTokenizer, MarianMTModel

# Ensure UTF-8 encoding for standard output and error on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Pretrained model identifiers from HuggingFace model hub
EN_TO_HI_MODEL_NAME = "Helsinki-NLP/opus-mt-en-hi"
HI_TO_EN_MODEL_NAME = "Helsinki-NLP/opus-mt-hi-en"

# Backward compatibility aliases for existing imports
ENGLISH_TO_HINDI_MODEL_NAME = EN_TO_HI_MODEL_NAME
HINDI_TO_ENGLISH_MODEL_NAME = HI_TO_EN_MODEL_NAME

# Explicit direction identifiers
EN_TO_HI = "en-hi"
HI_TO_EN = "hi-en"

# Backward compatibility aliases for direction codes
ENGLISH_TO_HINDI_DIRECTION = EN_TO_HI
HINDI_TO_ENGLISH_DIRECTION = HI_TO_EN

# Common fixed expressions dictionary for standard greetings and phrases
COMMON_ENGLISH_TO_HINDI = {
    "hello": "नमस्ते",
    "hi": "नमस्ते",
    "hey": "नमस्ते",
    "good morning": "सुप्रभात",
    "good evening": "शुभ संध्या",
    "good night": "शुभ रात्रि",
    "thank you": "धन्यवाद",
    "thanks": "धन्यवाद",
}

COMMON_HINDI_TO_ENGLISH = {
    "नमस्ते": "Hello",
    "नमस्कार": "Hello",
    "सुप्रभात": "Good morning",
    "शुभ संध्या": "Good evening",
    "शुभ रात्रि": "Good night",
    "धन्यवाद": "Thank you",
    "शुक्रिया": "Thank you",
}


def contains_devanagari(text):
    """
    Check if the given text contains at least one Devanagari script character.
    Devanagari Unicode block range: U+0900 to U+097F.

    Args:
        text (str): Input text string.

    Returns:
        bool: True if Devanagari character is found, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    return any('\u0900' <= char <= '\u097F' for char in text)


def post_process_hindi_translation(text):
    """
    Refine generated Hindi text to replace loanwords or Urdu variants with standard Hindi.

    Args:
        text (str): Raw output string from MarianMT model.

    Returns:
        str: Cleaned standard Hindi text.
    """
    if not text:
        return text

    text = text.strip()

    replacements = {
        "सलाम": "नमस्ते",
        "सलाम!": "नमस्ते!",
        "हैलो": "नमस्ते",
        "हेलो": "नमस्ते",
        "थैंक यू": "धन्यवाद",
        "थैंक्यू": "धन्यवाद",
        "शुक्रिया": "धन्यवाद",
        "अलविदा": "फिर मिलेंगे",
        "खुदा हाफिज": "फिर मिलेंगे",
        "मदद": "सहायता",
        "सवाल": "प्रश्न",
        "जवाब": "उत्तर",
        "किताब": "पुस्तक",
        "दोस्त": "मित्र",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    return text


def get_common_expression_translation(input_text, translation_direction):
    """
    Check if input_text is a common fixed expression and return its standard translation.
    Matching is case-insensitive and preserves trailing punctuation.

    Args:
        input_text (str): Source text phrase.
        translation_direction (str): 'en-hi' or 'hi-en'.

    Returns:
        str or None: Predefined standard translation if matched, None otherwise.
    """
    if not input_text or not isinstance(input_text, str):
        return None

    cleaned_text = input_text.strip()

    # Extract trailing punctuation (e.g., '!', '?', '.', '।')
    punctuation = ""
    while cleaned_text and cleaned_text[-1] in ".,!?।":
        punctuation = cleaned_text[-1] + punctuation
        cleaned_text = cleaned_text[:-1].strip()

    lookup_key = cleaned_text.lower()

    if translation_direction == EN_TO_HI and lookup_key in COMMON_ENGLISH_TO_HINDI:
        target_word = COMMON_ENGLISH_TO_HINDI[lookup_key]
        target_punctuation = "!" if punctuation == "!" else ("?" if punctuation == "?" else "")
        return target_word + target_punctuation

    if translation_direction == HI_TO_EN and lookup_key in COMMON_HINDI_TO_ENGLISH:
        target_word = COMMON_HINDI_TO_ENGLISH[lookup_key]
        target_punctuation = "!" if punctuation in "!।" else ("?" if punctuation == "?" else "")
        return target_word + target_punctuation

    return None


class TranslationEngine:
    """
    Manages loading MarianMT translation models and performing sequence-to-sequence translation.
    """

    def __init__(self):
        """
        Initialize model and tokenizer references. Lazy-loaded on first use.
        """
        self.english_to_hindi_tokenizer = None
        self.english_to_hindi_model = None

        self.hindi_to_english_tokenizer = None
        self.hindi_to_english_model = None

    def load_english_to_hindi_model(self):
        """
        Load pretrained English-to-Hindi MarianMT model (Helsinki-NLP/opus-mt-en-hi).
        """
        if self.english_to_hindi_model is None:
            self.english_to_hindi_tokenizer = MarianTokenizer.from_pretrained(
                EN_TO_HI_MODEL_NAME
            )
            self.english_to_hindi_model = MarianMTModel.from_pretrained(
                EN_TO_HI_MODEL_NAME
            )

    def load_hindi_to_english_model(self):
        """
        Load pretrained Hindi-to-English MarianMT model (Helsinki-NLP/opus-mt-hi-en).
        """
        if self.hindi_to_english_model is None:
            self.hindi_to_english_tokenizer = MarianTokenizer.from_pretrained(
                HI_TO_EN_MODEL_NAME
            )
            self.hindi_to_english_model = MarianMTModel.from_pretrained(
                HI_TO_EN_MODEL_NAME
            )

    def translate_english_to_hindi(self, input_text):
        """
        Translate English text to Hindi using MarianMT neural sequence-to-sequence model.

        Args:
            input_text (str): Cleaned English sentence.

        Returns:
            str: Translated standard Hindi text containing Devanagari script.
        """
        # Layer 1: Check common fixed expression layer
        common_expression_match = get_common_expression_translation(input_text, EN_TO_HI)
        if common_expression_match:
            print(f"\n[DEBUG LOG]\nINPUT:\n{input_text}\nDIRECTION:\nen-hi\nDETECTED LAYER:\nCommon Fixed Expression\nFINAL OUTPUT:\n{common_expression_match}\n", flush=True)
            return common_expression_match

        # Layer 2: Load English-to-Hindi MarianMT model
        self.load_english_to_hindi_model()

        # Step 1: Tokenization
        tokenized_text = self.english_to_hindi_tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        # Step 2: PyTorch Neural Inference with beam search
        with torch.no_grad():
            generated_tokens = self.english_to_hindi_model.generate(
                **tokenized_text,
                max_length=512,
                num_beams=5,
                early_stopping=True
            )

        # Step 3: Decode token IDs to text
        raw_translated_text = self.english_to_hindi_tokenizer.decode(
            generated_tokens[0],
            skip_special_tokens=True
        ).strip()

        # Step 4: Post-processing refinement
        refined_translated_text = post_process_hindi_translation(raw_translated_text)

        print(f"\n[DEBUG LOG]\nINPUT:\n{input_text}\nDIRECTION:\nen-hi\nMODEL:\n{EN_TO_HI_MODEL_NAME}\nRAW MODEL OUTPUT:\n{raw_translated_text}\nFINAL OUTPUT:\n{refined_translated_text}\n", flush=True)

        # Validation Rule: Must contain Devanagari characters for English -> Hindi
        if not contains_devanagari(refined_translated_text):
            raise ValueError(
                f"Translation failed: Model did not produce Hindi Devanagari text for '{input_text}'."
            )

        return refined_translated_text

    def translate_hindi_to_english(self, input_text):
        """
        Translate Hindi text to English using MarianMT neural sequence-to-sequence model.

        Args:
            input_text (str): Cleaned Hindi sentence.

        Returns:
            str: Translated English text.
        """
        # Layer 1: Check common fixed expression layer
        common_expression_match = get_common_expression_translation(input_text, HI_TO_EN)
        if common_expression_match:
            print(f"\n[DEBUG LOG]\nINPUT:\n{input_text}\nDIRECTION:\nhi-en\nDETECTED LAYER:\nCommon Fixed Expression\nFINAL OUTPUT:\n{common_expression_match}\n", flush=True)
            return common_expression_match

        # Layer 2: Load Hindi-to-English MarianMT model
        self.load_hindi_to_english_model()

        # Step 1: Tokenization
        tokenized_text = self.hindi_to_english_tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        # Step 2: PyTorch Neural Inference
        with torch.no_grad():
            generated_tokens = self.hindi_to_english_model.generate(
                **tokenized_text,
                max_length=512,
                num_beams=5,
                early_stopping=True
            )

        # Step 3: Decode token IDs to text
        translated_text = self.hindi_to_english_tokenizer.decode(
            generated_tokens[0],
            skip_special_tokens=True
        ).strip()

        print(f"\n[DEBUG LOG]\nINPUT:\n{input_text}\nDIRECTION:\nhi-en\nMODEL:\n{HI_TO_EN_MODEL_NAME}\nFINAL OUTPUT:\n{translated_text}\n", flush=True)

        return translated_text

    def translate_text(self, input_text, translation_direction):
        """
        Main entry point for translation requests.

        Args:
            input_text (str): Text string to translate.
            translation_direction (str): 'en-hi' or 'hi-en'.

        Returns:
            str: Translated string.
        """
        if translation_direction == EN_TO_HI:
            return self.translate_english_to_hindi(input_text)

        if translation_direction == HI_TO_EN:
            return self.translate_hindi_to_english(input_text)

        raise ValueError(
            f"Unsupported translation direction '{translation_direction}'. "
            f"Expected '{EN_TO_HI}' or '{HI_TO_EN}'."
        )


# Global singleton translation engine instance
translation_engine = TranslationEngine()
