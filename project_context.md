# Bilingual EPUB Alignment Project Context

## Overview

This project aligns the English and Spanish editions of "Artificial Intelligence" by Melanie Mitchell to create a combined bilingual EPUB. The core logic handles structural parsing, paragraph-level alignment, and EPUB generation.

## Key Components

### 1. `align_book.py`

The main script that:

- Parses source EPUBs (extracted directories).
- Maps chapters using TOC (NCX) analysis.
- Aligns content chunks.
- Generates bilingual XHTML and packages the final EPUB.

### 2. Alignment Logic

- **TOC Mapping**: Chapters are mapped by heuristically matching simplified labels (e.g., "Chapter 1" matches "Capítulo 1", "IV" matches "4").
- **Header Anchoring**: The script identifies headers in both languages to synchronize sections (preventing text from drifting across chapter subsections).
- **Chunk Alignment**:
  - Paragraphs are aligned sequentially.
  - Long English paragraphs are split (trigger > 240 chars), and Spanish paragraphs are split proportionally.
  - **Floating Elements**: Captions (`figcaption` in EN, specific classes in ES) are allowed to "float" (emit independently) if they don't match the other language's current chunk type.

## Parser Specifics (Critical)

### English Structure (`EnglishParser`)

- **Headers**:
  - `<h1>` tags are headers.
  - **Crucial**: Recognized classes include `CN`, `CT`, and `CN-Only`.
  - `h1.book-title` is treated as standard text/code block.
- **Captions**:
  - Uses `<figcaption>`.
  - Nested `<p>` tags inside `figcaption` are ignored to prevent splitting the caption into multiple chunks.

### Spanish Structure (`SpanishParser`)

- **Headers**:
  - Titles are often split into multiple paragraphs (e.g., Number "1" on one line, Title "Roots..." on the next).
  - **Merge Logic**: The parser automatically merges chunks with class `Capitulos_Capitulo_1_Linea` into the preceding `Capitulos_Capitulo_Numero` or `Capitulos_Capitulo_1_Linea` chunk. This ensures strict 1-to-1 header correspondence with English.
- **Classes**:
  - Headers: `Capitulos_Capitulo_Numero`, `Capitulos_Capitulo_1_Linea`, `Subcapitulos*`.
  - Captions: `Basico_pie_foto_centrado`.

## Configuration

- **Inputs**:
  - `temp_bilingual/en_full` (Extracted English EPUB)
  - `temp_bilingual/es_full` (Extracted Spanish EPUB)
- **Output**: `bilingual_book.epub`
- **Fonts**: Uses the system default serif font (no custom font embedding) to match the original English style.

### 3. Metadata & Styling

- **Metadata Preservation**: The script now extracts metadata (`dc:title`, `dc:creator`, `dc:identifier`, `dc:language`) from the English source OPF and preserves it in the output `content.opf`.
- **Title Modification**: Appends " (bilingual)" to the book title to distinguish the edition.
- **CSS Spacing**:
  - `p { margin: 0; }`: Removes vertical margins from all paragraphs to visually group the English text with its immediate Spanish translation below.
  - `.es-trans { margin-bottom: 1em; }`: Adds a specific bottom margin to Spanish paragraphs to separate unrelated bilingual pairs.
- **Cover & Metadata**:
  - Full metadata extraction (including extended fields and `meta` tags) from source OPF.
  - Automatic detection and preservation of the cover image.

## Future Iterations / Todo

- **Images**: Content images are currently stripped. Only the cover is preserved. Future work could re-integrate chapter images.
- **Footnotes**: Footnote references are present but links/content may need further refinement for full interactivity.
