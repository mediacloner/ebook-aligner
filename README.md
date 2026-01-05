# Bilingual Ebook Aligner

This tool automatically aligns an English EPUB and its Spanish translation to create a single **Bilingual EPUB** file. It aligns content paragraph-by-paragraph, allowing for parallel reading.

## Features

- **Web Interface**: Easy-to-use drag-and-drop web page.
- **CLI Tool**: Scriptable command-line interface for batch processing.
- **Smart Alignment**: Heuristic matching for headers and proportional splitting for long paragraphs.
- **Customizable**: Configuration-based parsing rules to support different book formats.

## Installation

1. **Prerequisites**: Python 3.8+ installed.
2. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install flask
   ```

## Usage

### 1. Web Interface (Recommended)

The easiest way to use the tool is via the web browser.

1. **Start the Server**:
   ```bash
   python3 app.py
   ```
2. **Open Browser**: Navigate to `http://127.0.0.1:8080`.
3. **Generate**:
   - Drag and drop your **English** EPUB.
   - Drag and drop your **Spanish** EPUB.
   - Click **Generate Bilingual Book**.
   - The aligned EPUB will start downloading automatically.

### 2. Command Line Interface (CLI)

For valid output, you must extract the `OEBPS` (or OPS) folders from your EPUBs first (EPUBs are just Zip files).

1. **Unzip EPUBs**:
   ```bash
   unzip english_book.epub -d en_folder
   unzip spanish_book.epub -d es_folder
   ```
2. **Run Script**:
   ```bash
   python3 align_book.py --en en_folder/OEBPS --es es_folder/OEBPS --output output_book.epub
   ```

## Configuration for New Books

The alignment logic relies on identifying headers and structure, which varies by publisher. To support a **different book**, open `align_book.py` and modify the `BOOK_CONFIG` dictionary at the top:

```python
BOOK_CONFIG = {
    'en': {
        'header_classes': ['CN', 'CT', 'My-New-Header-Class'],
        # ...
    },
    'es': {
        'header_indicators': ['Capitulo', 'Parte'],
        # ...
    }
}
```

- **English Rules**: define which CSS classes on `<h1>` tags indicate a chapter start.
- **Spanish Rules**: define classes or triggers for identifying headers (and merging split titles).

## Troubleshooting

- **Desynchronization**: If text is misaligned (e.g., Chapter 1 English text appearing next to Chapter 2 Spanish), check if the `BOOK_CONFIG` matches the class names in your specific EPUB files. You may need to inspect the source XHTML.
- **Missing Fonts**: This tool creates a "clean" EPUB relying on the e-reader's default fonts for maximum compatibility.

## LLM Verification & Auto-Fix [NEW]

The tool now includes an advanced module to verify alignment quality and automatically fix errors using a local LLM.

### Prerequisites for Verification

1.  **Install Ollama**: [https://ollama.com/download](https://ollama.com/download)
2.  **Pull the Model**:
    ```bash
    ollama pull qwen2.5:7b  # Recommended for EN/ES
    ```
3.  **Install Python Package**:
    ```bash
    pip install ollama sentence-transformers
    ```

### Verification Modes

In the **Web Interface**, you will see a dropdown under "Advanced Options":

1.  **No Verification** (Default): Fast alignment, no LLM check.
2.  **Validation Only**:
    - Analyzes the aligned book.
    - Generates a `_verification_report.md` next to your output file.
    - Flags suspicious pairs (missing text, severe misalignment).
3.  **Validation + Auto-Fix**:
    - **Smart Repair**: If a translation is missing, it first searches the original Spanish chapter using **Vector Embeddings** to find the lost sentence.
    - **Translation Fallback**: If the sentence is truly missing, the LLM generates a fresh translation to maintain continuity.
    - **Dual Output**: Generates two files:
      - `Book (bilingual).epub` (Original alignment)
      - `Book (bilingual) (Fixed).epub` (With repairs injected)

### Viewing the Report

After generation, open the `(Report).md` file. It will show:

- ⚠️ **Flagged** issues.
- ✅ **Fixed** issues (showing the "Before" and "After").
- **Method Used**: `🔍 Vector Search` (Found original text) or `✨ LLM Repair` (Generated translation).
