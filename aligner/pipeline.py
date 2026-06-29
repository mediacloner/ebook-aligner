from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from bs4 import BeautifulSoup

from aligner.adjudicator import Adjudicator
from aligner.block_builder import Block, BlockBuilder
from aligner.config import AlignerConfig
from aligner.footnote_emitter import EmitResult, FootnoteEmitter
from aligner.orphan_handler import attach_orphans
from aligner.paragraph_aligner import AlignedPair, ParagraphAligner
from aligner.reading_stream import ReadingStream

logger = logging.getLogger(__name__)


@dataclass
class ChapterResult:
    chapter_id: str
    blocks: List[Block]
    pairs: List[AlignedPair]
    emit: EmitResult
    stats: dict = field(default_factory=dict)


class AlignmentPipeline:
    """End-to-end alignment pipeline: stream → align → block → adjudicate → emit."""

    def __init__(self, config: Optional[AlignerConfig] = None, *, aligner: Optional[ParagraphAligner] = None):
        self.config = config or AlignerConfig.from_env()
        self.aligner = aligner or ParagraphAligner(self.config)
        self.block_builder = BlockBuilder(self.config, self.aligner)
        self.footnote_emitter = FootnoteEmitter(self.config)
        self.adjudicator = Adjudicator(self.config) if self.config.has_llm() else None

    def process_chapter(
        self,
        en_chunks: Sequence[dict],
        es_chunks: Sequence[dict],
        soup: BeautifulSoup,
        chapter_id: str,
        install_onboarding: bool = False,
        local_mode: bool = False,
    ) -> ChapterResult:
        en_stream = ReadingStream.from_chunks(en_chunks)
        es_stream = ReadingStream.from_chunks(es_chunks)
        pairs = self.aligner.align(en_stream, es_stream)
        blocks = self.block_builder.build(pairs)
        blocks = attach_orphans(blocks, pairs)

        if self.adjudicator and not local_mode:
            try:
                self.adjudicator.adjudicate_blocks(blocks)
            except Exception as exc:
                logger.warning("Adjudicator pass failed for %s: %s", chapter_id, exc)

        self.footnote_emitter.reset_counter()
        emit = self.footnote_emitter.emit(blocks, soup, chapter_prefix=f"{chapter_id}-")
        self.footnote_emitter.install_asides(soup, emit.asides)
        self.footnote_emitter.install_stylesheet(soup)
        self.footnote_emitter.ensure_epub_namespace(soup)
        if install_onboarding:
            self.footnote_emitter.install_onboarding(soup)

        stats = self._summarise(pairs, blocks, emit)
        logger.info(
            "Chapter %s: %d blocks, %d sub-splits, %d orphans, avg confidence %.2f, anchors %d",
            chapter_id,
            emit.block_count,
            emit.sub_split_count,
            emit.orphan_count,
            stats["avg_confidence"],
            stats["anchor_count"],
        )
        return ChapterResult(chapter_id=chapter_id, blocks=blocks, pairs=pairs, emit=emit, stats=stats)

    @staticmethod
    def _summarise(pairs: Sequence[AlignedPair], blocks: Sequence[Block], emit: EmitResult) -> dict:
        anchor_count = sum(1 for p in pairs if p.is_anchor)
        en_only = sum(1 for p in pairs if p.is_en_only)
        es_only = sum(1 for p in pairs if p.is_es_only)
        if blocks:
            avg_conf = sum(b.confidence for b in blocks) / len(blocks)
        else:
            avg_conf = 0.0
        low_conf = sum(1 for b in blocks if b.confidence < 0.55)
        return {
            "pairs": len(pairs),
            "blocks": emit.block_count,
            "sub_splits": emit.sub_split_count,
            "orphan_es_pairs": es_only,
            "en_only_pairs": en_only,
            "anchor_count": anchor_count,
            "avg_confidence": avg_conf,
            "low_confidence_blocks": low_conf,
        }
