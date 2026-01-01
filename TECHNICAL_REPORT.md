# Bilingual EPUB Aligner: Technical Report

## 1. Project Overview

This project is an advanced, automated tool for creating **Bilingual EPUBs** by aligning an English source EPUB with its Spanish translation. Unlike simple text interactors, this tool works at the **EPUB structure level**, preserving the original English formatting, CSS, and layout while injecting Spanish translations as "shadow text" immediately following the English paragraphs.

The core goal is to produce a high-quality "Parallel Text" experience for language learners, robust enough to handle complex layouts, different chapter structures, and varying translation fidelities.

## 2. Technology Stack

### Core Libraries

- **Python 3.10+**: The integration language.
- **BeautifulSoup4 (`bs4`)**: The primary engine for HTML parsing, DOM manipulation, and structure analysis. Used with the `lxml` parser for speed and leniency.
- **Sentence-Transformers (`sentence_transformers`)**: Used for **Neural Alignment**. Specifically, the **LaBSE** (Language-agnostic BERT Sentence Embedding) model is used to generate semantic embeddings for paragraphs, allowing alignment based on _meaning_ rather than just keywords or position.
- **SciPy & NumPy**: Used for calculating Cosine Distance matrices and handling efficient array operations during alignment.
- **Standard Library**: `zipfile` (EPUB handling), `re` (Regex for headers/figures), `shutil` (File ops).

## 3. Architecture & Workflow

The pipeline consists of six distinct stages:

### Phase 1: Preparation & Expansion

1.  **Input**: Two `.epub` files (English and Spanish).
2.  **Expansion**: Both files are unzipped into standard directory structures (`OEBPS/` or `OPS/`).
3.  **Metadata Extraction**: The OPF (Open Packaging Format) file is parsed to understand the "Spine" (reading order) and "Manifest" (file list).

### Phase 2: Structural Alignment (TOC Mapping)

Before aligning text, the tool aligns **Chapters**. This is complex because translations often have different file structures (e.g., English has 1 file per chapter, Spanish has 1 file for the whole book, or vice versa).

- **TOC Parsing**: The NCX (Navigation Control file) is parsed to extract a hierarchy of chapters.
- **Recursive Alignment**: A custom "Anchor & Fill" algorithm aligns TOC items:
  - **Anchors**: Finds high-confidence matches (text similarity > 0.85) to pin the structure.
  - **Gap Filling**: Recursively fills gaps between anchors.
- **Proportional Mapping**: For **Sparse TOCs** (e.g., _Animal Farm_, where the Spanish TOC is missing 90% of chapters), the system:
  1.  Discovers hidden content files in the directory.
  2.  Calculates file sizes.
  3.  Assigns English chapters to Spanish files based on **Proportional Position** (e.g., if Chapter 3 is at the 30% mark of the English book, it maps to the file at the 30% mark of the Spanish content).

### Phase 3: Content Parsing & Normalization

Once a pair of files (or a set of chapters) is identified:

- **Parsers**: Language-specific parsers (`EnglishParser`, `SpanishParser`) extract text "Chunks".
- **Chunking Strategy**: content is split by Paragraphs (`<p>`), Headers (`<h1>`...`<h6>`), and Lists (`<li>`).
- **Granularity Control**: Long paragraphs (> 240 chars) are split into sentences to improve alignment accuracy.
- **Filtering**: Classes like `.credit`, `.copyright`, `.page-num` are recursively ignored to prevent noise.
- **Header Normalization**:
  - _Atomic Habits Case_: Merges split headers (e.g., `<h1>Chapter 1</h1>` followed by `<h1>The Standard</h1>`) into a single logical chunk to match the Spanish translation (which often combines them).
  - _Hidden Figures Case_: Disables merging for generic headers like "Bibliography" vs "Sources" to preserve distinct sections.

### Phase 4: Neural Alignment (The Core)

This is the most computationally intensive phase.

1.  **Embedding Generation**: Every English and Spanish chunk is passed through **LaBSE** to get a 768-dimensional vector.
2.  **Distance Matrix**: A matrix is built calculating the Semantic Distance (Cosine) between every EN and ES chunk.
    - **Positional Penalty**: A bias is added to diagonal elements to favor sequential reading order.
3.  **Hard Constraints**: Critical checkpoints are locked:
    - **Figures**: Regex detects "Figure 12" vs "Figura 12". These are forced to align, effectively breaking the problem into smaller sub-matrices.
    - **Headers**: Strongly matching headers act as "Reset Points".
4.  **Reconstruction**: An algorithm (linear interpolation or DTW-inspired) finds the optimal path through the matrix, creating pairs (1:1), splits (1:N), or merges (N:1).

### Phase 5: Injection & Output

1.  **Cloning**: The English DOM structure is cloned to serve as the skeleton.
2.  **Injection**: Spanish text is injected _after_ the corresponding English element.
    - **Styling**: Injected text is wrapped in `<span class="es-trans" style="color: grey;">` to visually distinguish it.
    - **Floating**: If a caption or image cannot be aligned, it is preserved in its original location ("Floating").
3.  **Shared File Handling**: If multiple English chapters map to a _single_ Spanish file (e.g., _Animal Farm_ Chapter 1 & 2 -> `52.xhtml`), the system:
    - Identifies the shared file.
    - semantically matches the _start_ of each English chapter within the Spanish file.
    - Splits the Spanish file into virtual segments for isolated alignment.

### Phase 6: Packaging

1.  The mapped/injected HTML files populate the output structure.
2.  The `content.opf` and `toc.ncx` are generated (or updated) to reflect the new structure.
3.  Directories are zipped back into a valid `.epub`.

## 4. Key "Tricks" & Algorithms

### 1. The "Gap Filler" (Proportional Assignment)

- **Problem**: Spanish EPUBs often have terrible Metadata/TOCs (e.g., missing chapters).
- **Solution**: Since we know the reading order is linear, `align_tocs` uses file size ratios. If "Chapter 5" is missing in the Spanish TOC, but we have 3 "Extra" files, we assign Chapter 5 to the file that corresponds to its relative byte-position. This solved the major alignment failure in _Animal Farm_.

### 2. Constraint-Based Dynamic Time Warping

- **Problem**: In technical books (_Artificial Intelligence_), long sequences of short paragraphs (bullets) can cause the aligner to drift.
- **Solution**: We extract "Anchors" (Figures, References). If "Figure 3.1" appears in chunk 50 (EN) and chunk 55 (ES), we _force_ the alignment path to pass through (50, 55). This resets any accumulated drift.

### 3. Recursive Class Ignoring

- **Problem**: Some books intersperse content with unaligned metadata (credits, pagelinks).
- **Solution**: The parser doesn't just check the tag; it checks the _ancestry_. If a node is inside a `div.credit`, it and all its children are ignored. This solved issues in _Hidden Figures_.

### 4. Shared File Splitting

- **Problem**: High-density Spanish EPUBs often combine 10 chapters into 1 massive HTML file.
- **Solution**: Instead of failing, the system aligns Chapter 1 (EN) to the _entire_ Spanish file, but _detects where Chapter 2 (EN) begins_. It virtually "slices" the Spanish file, ensuring Chapter 1 only matches text up to the start of Chapter 2.

  - Splits the Spanish file into virtual segments for isolated alignment.

### 5. Semantic Chapter Alignment ("The Little LLM")

- **Problem**: Table of Contents (TOC) metadata is often sparse, misleading, or completely mismatched (e.g., "Chapter One" in English TOC vs "Inicio" in Spanish TOC, or missing entries entirely).
- **Solution**: We implemented a **Semantic TOC Aligner** using the LaBSE neural model.
  - **Strategy**: Instead of relying on labels, the system reads the first 1000 characters of _content_ from every candidate file.
  - **Process**: These content samples are encoded into vector space. The system calculates a similarity matrix between English Chapter Starts and Spanish File Starts.
  - **Result**: Matches are made based on _Textual Meaning_. If "Chapter 1" text starts with "Mr. Jones...", it will find the Spanish file starting with "El señor Jones...", even if the file is named `09Cap1.xhtml` and is not in the TOC.

## 5. Supported/Tested Books (Case Studies)

| Book                        | Key Challenge                           | Solution Ref                     |
| :-------------------------- | :-------------------------------------- | :------------------------------- |
| **Artificial Intelligence** | Complex Figures, Captions, Bullet Lists | Hard Constraints, Constraint-DTW |
| **Sapiens**                 | Heavy Images, Non-standard Headers      | Extended Header Heuristics       |
| **Animal Farm**             | Sparse TOC, Hidden Files, Shared Files  | Proportional TOC Gap Filling     |
| **Atomic Habits**           | Split Headers (Number vs Title)         | Header Merging Pre-pass          |
| **Hidden Figures**          | Merged Bibliographies, Recursive Noise  | Recursive Ignore Classes         |
| **Normal People**           | Time-based Chapter Titles               | Date Extraction/Normalization    |

## 6. Future Improvements

- **Image Integration**: Currently, content images are largely stripped or left as placeholders. Merging image assets from both EPUBs.
- **Footnote Hybridization**: Merging interactive footnote links from both languages.
- **LLM Verification**: Using a small LLM (Gemini Flash) to verify "low confidence" pairs during the alignment phase itself.
