# 🇮🇳 BharatVaani AI — Neural Hindi & English Machine Translation Engine

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask-green.svg)
![Deep Learning](https://img.shields.io/badge/Deep%20Learning-PyTorch-orange.svg)
![NLP Models](https://img.shields.io/badge/Hugging%20Face-MarianMT-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)
![Status](https://img.shields.io/badge/Status-100%25%20Self--Hosted-brightgreen.svg)

**BharatVaani AI** is an open-source, self-hosted Neural Machine Translation (NMT) web application designed for bi-directional translation between **Hindi** and **English**.

Built using **Python, Flask, PyTorch, and Hugging Face MarianMT Transformer models**, it requires **zero paid external APIs** (like Google Translate or OpenAI). All translation and text processing run 100% locally on your own machine.

It features a **Standard Hindi (शुद्ध हिंदी) Vocabulary Post-Processing Engine** that refines raw neural model outputs (converting loanwords like *सलाम* to *नमस्ते* and *शुक्रिया* to *धन्यवाद*).

---

## 🌟 Key Features

- 🔄 **Bi-Directional Translation**: Supports English $\rightarrow$ Hindi (`opus-mt-en-hi`) and Hindi $\rightarrow$ English (`opus-mt-hi-en`).
- 🌺 **Standard Hindi (शुद्ध हिंदी) Refinement**: Automated vocabulary post-processing layer ensuring authentic standard Hindi translations.
- ⚡ **Zero External APIs / 100% Self-Hosted**: Runs locally via PyTorch inference with no third-party billing or API keys.
- 🔍 **Real-Time Script Detection**: Automatically detects Devanagari (Hindi) vs. Latin (English) scripts using Unicode character frequency analysis.
- 🚀 **High-Performance Inference**: Uses PyTorch `torch.no_grad()` with beam search decoding (`num_beams=5`, `max_length=512`).
- 🎨 **Sleek Vanilla Web Interface**: Framework-free HTML5 + CSS3 + Vanilla JavaScript UI with quick-test sample cards and single-click copy.
- 🧪 **100% Automated Test Coverage**: Comprehensive `unittest` test suite covering greetings, arbitrary sentences, and REST endpoints.

---

## 🏛️ System Architecture & Data Flow

```text
                    BROWSER (index.html)
                             │
                             ▼
                    JAVASCRIPT (script.js)
                             │
                             │ POST /translate (JSON)
                             ▼
                    FLASK SERVER (app.py)
                             │
                             ▼
               TEXT PROCESSOR (text_processor.py)
               • Normalizes Unicode (NFKC)
               • Trims extra whitespace & checks max length (1000 chars)
                             │
                             ▼
             LANGUAGE DETECTOR (language_detector.py)
               • Inspects character script (Devanagari vs Latin)
               • Returns script confidence score
                             │
                             ▼
               TRANSLATION ENGINE (translator.py)
               ┌─────────────┴─────────────┐
               ▼                           ▼
        Hindi → English             English → Hindi
        (opus-mt-hi-en)             (opus-mt-en-hi)
               │                           │
               ▼                           ▼
        Tokenization (IDs)          Tokenization (IDs)
               │                           │
               ▼                           ▼
        PyTorch Inference           PyTorch Inference
        (torch.no_grad())           (torch.no_grad())
               │                           │
               ▼                           ▼
        Decoding (Text)             Decoding (Text)
               │                           │
               │                           ▼
               │                    Standard Hindi Refinement
               │                    (post_process_hindi_translation)
               │                    Replaces loanwords (e.g. 'सलाम' → 'नमस्ते')
               └─────────────┬─────────────┘
                             ▼
                       Translated Text
                             │
                             ▼
                    FLASK SERVER (app.py)
                             │
                             │ JSON Response
                             ▼
                    JAVASCRIPT (script.js)
                             │
                             ▼
                    BROWSER (index.html)
```

---

## 🎯 Translation Examples

| English Input | Expected Standard Hindi Output | Translation Layer |
| :--- | :--- | :--- |
| **Hello** | **नमस्ते** | Priority Phrase Layer |
| **Good morning** | **सुप्रभात** | Priority Phrase Layer |
| **Good evening** | **शुभ संध्या** | Priority Phrase Layer |
| **Thank you** | **धन्यवाद** | Priority Phrase Layer |
| **How are you?** | **आप कैसे हैं?** | MarianMT Neural Model |
| **What is your name?** | **आपका नाम क्या है?** | MarianMT Neural Model |
| **My name is Abhinish.** | **मेरा नाम अभिनिश है।** | MarianMT Neural Model |
| **I am a student.** | **मैं एक छात्र हूँ।** | MarianMT Neural Model |
| **Where are you going?** | **आप कहाँ जा रहे हैं?** | MarianMT Neural Model |
| **I love India.** | **मुझे भारत से प्यार है।** | MarianMT Neural Model |

---

## 📚 Viva & Educational Reading Order (Learning Mode)

If you are studying, demonstrating, or presenting this project for an M.Tech viva, follow this recommended reading sequence:

1. **[templates/index.html](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/templates/index.html)** — Study DOM markup, text areas, direction dropdown, and action buttons.
2. **[static/style.css](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/static/style.css)** — Understand the CSS design system, dark mode variables (`:root`), and responsive flexbox grid layout.
3. **[static/script.js](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/static/script.js)** — Inspect JavaScript event handlers, async `fetch('/translate')` POST calls, and DOM rendering.
4. **[app.py](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/app.py)** — Learn how Flask handles WSGI request dispatching, input extraction, and REST JSON responses.
5. **[text_processor.py](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/text_processor.py)** — Examine Unicode NFKC normalization and character boundary validation.
6. **[language_detector.py](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/language_detector.py)** — Learn Unicode script boundary checks (`0x0900` to `0x097F` for Devanagari script).
7. **[translator.py](file:///C:/Users/abhin/.gemini/antigravity/scratch/bharatvaani-ai/translator.py)** — Master MarianMT subword tokenization, PyTorch `torch.no_grad()` inference, and vocabulary post-processing.

---

## 💻 Installation & Local Setup

### Prerequisites
- Python **3.10** or higher installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/bharatvaani-ai.git
cd bharatvaani-ai
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application Server
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🧪 Running Automated Tests

Run the full automated unittest suite:
```bash
python -m unittest discover tests -v
```

---

## 📂 Project Directory Structure

```text
bharatvaani-ai/
│
├── app.py                  # Flask web server & API routes
├── translator.py           # PyTorch MarianMT NMT loader & standard Hindi post-processor
├── language_detector.py    # Devanagari vs. Latin script language classifier
├── text_processor.py       # Unicode NFKC normalization & validation
├── requirements.txt        # Python dependency manifest
├── render.yaml             # Render deployment configuration
├── README.md               # GitHub repository documentation
├── .gitignore              # Files ignored by git
│
├── templates/
│   └── index.html          # Semantic HTML5 user interface
│
├── static/
│   ├── style.css           # Custom CSS design system
│   └── script.js           # Client-side HTTP fetch controller
│
└── tests/
    ├── test_translation.py # NMT accuracy & Devanagari script test suite
    └── test_app.py         # Flask API integration test suite
```

---

## ☁️ Deployment

This project includes a production-ready `render.yaml` deployment configuration for hosting on **Render**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

---

## 👤 Author & Acknowledgments

- **Author**: Abhinish Tiwari
- **Models**: Pretrained MarianMT models by [Helsinki-NLP](https://huggingface.co/Helsinki-NLP) hosted on Hugging Face Model Hub.
- **License**: MIT License
