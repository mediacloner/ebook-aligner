# Tandem

Read in English. Tap any paragraph when you get stuck — its Spanish
translation pops up as a Kindle/iBooks footnote. Fluent reading on demand
instead of constant inline parallel text.

## Why

Side-by-side bilingual books let your brain skim the easier language. Lookup
Mode keeps you in the target language by default and surfaces the translation
only when you ask for it. Fewer crutches, faster acquisition.

## How it works

The aligner is a three-layer pipeline (`aligner/` module):

1. **Reading Stream** — parse both EPUBs into ordered typed events
   (paragraph / header / figure / caption / list-item / scene-break) with
   DOM-node references for later injection.
2. **Paragraph Aligner** — LaBSE embeddings + Bertalign-style two-step
   alignment: top-k mutual nearest neighbours pick high-confidence anchors,
   then DP over span pairs (1:1, 1:2, 2:1, 2:2, plus gap transitions) fills the
   rest with a globally optimal monotonic alignment.
3. **OpenAI Adjudicator** — for the small fraction of pairs where embedding
   alignment is uncertain, send EN + ES + context to `gpt-5.5` with a strict
   JSON schema; the model confirms or proposes a replacement Spanish text.
   Disk-cached on `sha256(en + es + model)` so re-runs are free.

Long paragraphs are split into 3–4-sentence sub-blocks at sentence boundaries.
ES-only orphan content (translator notes, lost captions) is appended to the
nearest block's footnote, prefixed with **Nota**.

Every block ends with a faint middle-dot marker (`·`) that serves two
purposes: it gives Kindle/KFX a real noteref token to fire the popup on
(whole-paragraph anchors alone are unreliable on Amazon's reader), and
it cues the reader that translation is available. The whole paragraph
remains tappable; the marker is just a small grey "ping". A one-line
onboarding notice in the first chapter explains the interaction.

## Requirements

- Python 3.10+
- LaBSE via `sentence-transformers` (downloads on first run, ~470MB)
- OpenAI API key (optional but recommended for the adjudicator pass)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repo root:

```
OPENAI_API_KEY=sk-...
OPENAI_ALIGNER_MODEL=gpt-5.5
ALIGNER_USE_LLM=true
```

The `.env` file is gitignored. To run without the adjudicator, set
`ALIGNER_USE_LLM=false`.

## Usage

### Web

```bash
python3 app.py
```

Open http://127.0.0.1:8080. Drop both EPUBs, hit **Generate**, download the
resulting `…(Lookup Mode).epub`.

### CLI

EPUBs must be unzipped to OEBPS folders first (EPUBs are just ZIPs).

```bash
unzip english_book.epub -d en_folder
unzip spanish_book.epub -d es_folder
python3 align_book.py --en en_folder/OEBPS --es es_folder/OEBPS --output out.epub
```

## Cost expectations

LaBSE runs locally. The OpenAI adjudicator is called only on low-confidence
paragraph pairs — typically 1–5% of paragraphs. Expected spend per book is
**$0.20–$0.60** on `gpt-5.5`; subsequent re-runs hit the disk cache and cost
nothing.

## Reader compatibility

- **Apple Books / iBooks**: tap anywhere on the paragraph → native popup ✓
- **Kindle (KFX/AZW3)**: the trailing `·` marker is the popup trigger;
  newer Paperwhites and Send-to-Kindle conversions of EPUB3 footnotes show
  the popup. Older Kindles fall back to navigating to an endnote.
- **Kobo**: popup works on most models; a few older devices fall back to
  endnote navigation.
- **Calibre / Sigil**: footnote opens inline at the chapter's footnote section.
- **Other EPUB3 readers**: graceful endnote fallback at chapter end.

## Project structure

```
aligner/
  reading_stream.py    typed paragraph events from parsed chunks
  paragraph_aligner.py LaBSE + Bertalign two-step DP
  block_builder.py     sentence-level sub-blocks for long paragraphs
  orphan_handler.py    attach ES-only content to nearest block
  footnote_emitter.py  EPUB3 noteref + aside markup
  adjudicator.py       OpenAI structured-output verifier with cache
  pipeline.py          orchestrator
  bridge.py            adapter into align_book.py's chapter loop
align_book.py          EPUB I/O, OPF/NCX, TOC alignment, multi-chapter loop
app.py                 Flask web UI
```
