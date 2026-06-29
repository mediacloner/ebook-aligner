from __future__ import annotations

import logging
import os
import threading
import traceback
from typing import Optional

from bs4 import BeautifulSoup

from aligner.config import AlignerConfig
from aligner.pipeline import AlignmentPipeline

logger = logging.getLogger(__name__)

_pipeline: Optional[AlignmentPipeline] = None
_pipeline_lock = threading.Lock()


def get_pipeline() -> AlignmentPipeline:
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                _pipeline = AlignmentPipeline(AlignerConfig.from_env())
    return _pipeline


def reset_pipeline() -> None:
    """Test hook: drop the cached pipeline so the next call rebuilds it."""
    global _pipeline
    with _pipeline_lock:
        _pipeline = None


def _apply_split_overrides(cfg: AlignerConfig, config: dict) -> None:
    """Apply per-job sentence-splitting overrides sent from the web config.

    The pipeline is a process-wide singleton built from .env; these keys, when
    present in the job config, let the UI tune splitting per run. cfg is shared
    with the block builder (same object), so setting attributes here is enough.
    """
    if config.get("word_budget_split") is not None:
        cfg.word_budget_split = bool(config["word_budget_split"])
    target = config.get("target_chunk_words")
    if isinstance(target, int) and target > 0:
        cfg.target_chunk_words = target
    min_words = config.get("split_min_words")
    if isinstance(min_words, int) and min_words > 0:
        cfg.split_min_words = min_words


def _slice_shared_es(es_chunks, chunk_range):
    if not chunk_range:
        return es_chunks
    a, b = chunk_range
    if isinstance(a, int) and isinstance(b, int):
        return es_chunks[a:b]
    position, proportions = a, b
    total = len(es_chunks)
    cumulative = sum(proportions[:position])
    start_idx = int(cumulative * total)
    cumulative += proportions[position]
    end_idx = int(cumulative * total) if position < len(proportions) - 1 else total
    return es_chunks[start_idx:end_idx]


def run_chapter_pair(args):
    """Drop-in replacement for align_book.process_chapter_pair.

    Returns the same 6-tuple shape: (idx, target_path, label, _, flagged, stats).
    """
    # Import here to avoid a circular import at module load (align_book imports
    # this module; this module imports a few helpers back from align_book).
    from align_book import extract_nodes, parse_file, SpanishParser, is_navigation_page

    staging_info = None
    if len(args) == 9:
        idx, en_path, es_path, es_opf_dir, config, label, chunk_range, model, staging_info = args
    elif len(args) == 8:
        idx, en_path, es_path, es_opf_dir, config, label, chunk_range, model = args
    elif len(args) == 7:
        idx, en_path, es_path, es_opf_dir, config, label, chunk_range = args
    else:
        idx, en_path, es_path, es_opf_dir, config, label = args
        chunk_range = None

    target_path = en_path
    if staging_info:
        staging_root, _staging_fixed_root, en_base = staging_info
        if staging_root and en_path.startswith(staging_root):
            target_path = en_path
        elif en_base and en_path.startswith(en_base):
            rel_path = os.path.relpath(en_path, en_base)
            target_path = os.path.join(staging_root, rel_path)

    empty_stats = {"count": 0, "en_chars": 0, "es_chars": 0}

    if config.get("bypass_alignment"):
        return (idx, None, "Bypassed", None, [], empty_stats)

    try:
        if not os.path.exists(target_path):
            return (idx, None, f"Target file not found: {target_path}", None, [], empty_stats)

        with open(target_path, "r", encoding="utf-8") as fh:
            soup = BeautifulSoup(fh.read(), "lxml")

        en_chunks = extract_nodes(soup)

        if is_navigation_page(soup):
            return (idx, target_path, label, [], [], empty_stats)

        if not es_path or not os.path.exists(es_path):
            with open(target_path, "w", encoding="utf-8") as fh:
                fh.write(str(soup))
            return (idx, target_path, label, [], [], empty_stats)

        if "es" not in config:
            config["es"] = {
                "header_tags": ["h1", "h2", "h3"],
                "ignore_classes": [],
            }
        es_chunks = parse_file(es_path, SpanishParser, config)
        es_chunks = _slice_shared_es(es_chunks, chunk_range)
        es_chunks = [
            c for c in es_chunks
            if (c.get("text") or "").strip() or c.get("type") != "std"
        ]

        pipeline = get_pipeline()
        _apply_split_overrides(pipeline.config, config)
        chapter_id = f"ch{idx:03d}"
        install_onboarding = idx == 0
        result = pipeline.process_chapter(
            en_chunks,
            es_chunks,
            soup,
            chapter_id=chapter_id,
            install_onboarding=install_onboarding,
            local_mode=bool(config.get("local_mode")),
        )

        with open(target_path, "w", encoding="utf-8") as fh:
            fh.write(str(soup))

        stats = {
            "count": result.emit.block_count,
            "en_chars": sum(len(b.en_text) for b in result.blocks),
            "es_chars": sum(len(b.es_text) for b in result.blocks),
        }
        return (idx, target_path, label, [], [], stats)
    except Exception as exc:
        traceback.print_exc()
        logger.error("Chapter %s failed: %s", label, exc)
        return (idx, None, str(exc), [], [], empty_stats)
