from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

from aligner.config import AlignerConfig
from aligner.paragraph_aligner import AlignedPair, ParagraphAligner
from aligner.reading_stream import StreamEvent

logger = logging.getLogger(__name__)


@dataclass
class Block:
    en_text: str
    es_text: str
    en_event: Optional[StreamEvent]
    kind: str
    confidence: float
    pair: AlignedPair
    sub_index: int = 0
    sub_count: int = 1
    sub_text_offset: int = 0
    sub_text_length: int = 0
    es_extras: List[StreamEvent] = field(default_factory=list)
    needs_adjudication: bool = False

    @property
    def is_sub_block(self) -> bool:
        return self.sub_count > 1

    @property
    def is_first_sub(self) -> bool:
        return self.sub_index == 0


class BlockBuilder:
    """Turns aligned paragraph pairs into reader-visible Blocks.

    One paragraph = one block when ≤ max_sentences_per_block; long paragraphs
    are split at sentence boundaries into sub-blocks with proportional
    semantic distribution of the matching Spanish text.
    """

    def __init__(self, config: AlignerConfig, aligner: ParagraphAligner):
        self.config = config
        self.aligner = aligner
        self._segmenter_en = None
        self._segmenter_es = None

    # ----------------------------------------------------------- sentence split

    def _split_sentences(self, text: str, language: str) -> List[str]:
        if not text.strip():
            return []
        try:
            import pysbd
        except ImportError:
            return [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if language == "en":
            if self._segmenter_en is None:
                self._segmenter_en = pysbd.Segmenter(language="en", clean=False)
            seg = self._segmenter_en
        else:
            if self._segmenter_es is None:
                self._segmenter_es = pysbd.Segmenter(language="es", clean=False)
            seg = self._segmenter_es
        return [s.strip() for s in seg.segment(text) if s and s.strip()]

    # ---------------------------------------------------------------- entrypoint

    def build(self, pairs: Sequence[AlignedPair], config: Optional[AlignerConfig] = None) -> List[Block]:
        cfg = config if config is not None else self.config
        blocks: List[Block] = []
        for pair in pairs:
            if pair.is_es_only:
                continue  # handled later by OrphanHandler
            if pair.is_en_only:
                en_event = pair.en_events[0]
                blocks.append(
                    Block(
                        en_text=en_event.text,
                        es_text="",
                        en_event=en_event,
                        kind=en_event.kind,
                        confidence=pair.confidence,
                        pair=pair,
                        needs_adjudication=False,
                    )
                )
                continue

            en_text, es_text, primary_event, kind = self._combine_pair_texts(pair)
            needs_adj = (
                pair.confidence < cfg.adjudicator_confidence_threshold
                and not pair.is_anchor
            )

            if not self._should_split(primary_event, en_text, cfg):
                blocks.append(
                    Block(
                        en_text=en_text,
                        es_text=es_text,
                        en_event=primary_event,
                        kind=kind,
                        confidence=pair.confidence,
                        pair=pair,
                        sub_text_offset=0,
                        sub_text_length=len(en_text),
                        needs_adjudication=needs_adj,
                    )
                )
                continue

            sub_blocks = self._split_into_sub_blocks(
                pair, primary_event, en_text, es_text, kind, needs_adj, cfg
            )
            blocks.extend(sub_blocks)
        return blocks

    # --------------------------------------------------------------- pair texts

    def _combine_pair_texts(self, pair: AlignedPair) -> Tuple[str, str, StreamEvent, str]:
        en_texts = [e.text for e in pair.en_events]
        es_texts = [e.text for e in pair.es_events]
        en_text = "\n\n".join(en_texts) if len(en_texts) > 1 else en_texts[0]
        es_text = " ".join(t for t in es_texts if t)
        primary_event = pair.en_events[0]
        kind = primary_event.kind
        return en_text, es_text, primary_event, kind

    # ---------------------------------------------------------------- splitting

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())

    def _should_split(
        self, event: StreamEvent, en_text: str, config: Optional[AlignerConfig] = None
    ) -> bool:
        cfg = config if config is not None else self.config
        if event.kind != "paragraph":
            return False
        if cfg.word_budget_split:
            # Word-budget mode: split once the paragraph exceeds the target chunk
            # size and has at least two sentences (a single long sentence is
            # never broken mid-sentence, so it stays whole).
            if self._word_count(en_text) <= cfg.target_chunk_words:
                return False
            sentences = self._split_sentences(en_text, "en")
            return len(sentences) >= 2
        # Legacy sentence-window mode.
        if len(en_text) <= cfg.long_paragraph_threshold:
            return False
        sentences = self._split_sentences(en_text, "en")
        return len(sentences) > cfg.max_sentences_per_block

    def _chunk_windows(
        self, sentences: Sequence[str], config: Optional[AlignerConfig] = None
    ) -> List[List[str]]:
        """Group sentences into chunks. Word-budget mode targets
        ~target_chunk_words words per chunk; legacy mode uses fixed windows of
        max_sentences_per_block. Sentences are never broken mid-sentence."""
        cfg = config if config is not None else self.config
        if cfg.word_budget_split:
            return self._group_sentences_by_word_budget(sentences, cfg)
        max_per = max(1, cfg.max_sentences_per_block)
        return [list(sentences[i : i + max_per]) for i in range(0, len(sentences), max_per)]

    def _group_sentences_by_word_budget(
        self, sentences: Sequence[str], config: Optional[AlignerConfig] = None
    ) -> List[List[str]]:
        """Port of bilingual-epub-splitter's group_by_word_budget.

        Sentences accumulate into a chunk until adding the next one would push
        the chunk past an overshoot limit (and the chunk already carries enough
        words). A single sentence longer than the target stands alone.
        """
        cfg = config if config is not None else self.config
        target = max(1, cfg.target_chunk_words)
        overshoot_limit = int(target * 1.4)
        min_carry = int(target * 0.5)
        chunks: List[List[str]] = []
        current: List[str] = []
        current_words = 0
        for sent in sentences:
            w = self._word_count(sent)
            if not current:
                current = [sent]
                current_words = w
                continue
            if current_words >= min_carry and current_words + w > overshoot_limit:
                chunks.append(current)
                current = [sent]
                current_words = w
            else:
                current.append(sent)
                current_words += w
        if current:
            chunks.append(current)
        return chunks

    def _split_into_sub_blocks(
        self,
        pair: AlignedPair,
        event: StreamEvent,
        en_text: str,
        es_text: str,
        kind: str,
        needs_adj: bool,
        config: Optional[AlignerConfig] = None,
    ) -> List[Block]:
        cfg = config if config is not None else self.config
        en_sentences = self._split_sentences(en_text, "en")
        windows = self._chunk_windows(en_sentences, cfg)
        # Build sub-block strings with char offsets back into en_text
        sub_block_texts: List[str] = []
        sub_block_offsets: List[Tuple[int, int]] = []  # (start, end) within en_text
        cursor = 0
        for window in windows:
            joined = " ".join(window)
            sub_block_texts.append(joined)
            start = en_text.find(window[0], cursor)
            if start < 0:
                start = cursor
            end = en_text.find(window[-1], start)
            if end < 0:
                end = start + len(joined)
            else:
                end += len(window[-1])
            sub_block_offsets.append((start, end))
            cursor = end

        es_sentences = self._split_sentences(es_text, "es") if es_text else []
        es_partitions = self._distribute_es(sub_block_texts, es_sentences)

        blocks: List[Block] = []
        n_sub = len(sub_block_texts)
        for idx, (sub_text, (off, end), es_part) in enumerate(
            zip(sub_block_texts, sub_block_offsets, es_partitions)
        ):
            blocks.append(
                Block(
                    en_text=sub_text,
                    es_text=es_part,
                    en_event=event,
                    kind=kind,
                    confidence=pair.confidence,
                    pair=pair,
                    sub_index=idx,
                    sub_count=n_sub,
                    sub_text_offset=off,
                    sub_text_length=end - off,
                    needs_adjudication=needs_adj,
                )
            )
        return blocks

    # ----------------------------------------------------------- es distribution

    def _distribute_es(
        self,
        sub_block_texts: Sequence[str],
        es_sentences: Sequence[str],
    ) -> List[str]:
        n = len(sub_block_texts)
        m = len(es_sentences)
        if n == 1:
            return [" ".join(es_sentences)]
        if m == 0:
            return [""] * n
        if m <= n:
            # Distribute one ES sentence per EN sub-block, pad with "" at end
            out = list(es_sentences) + [""] * (n - m)
            return out

        en_embs = self.aligner.encode(list(sub_block_texts))
        es_embs = self.aligner.encode(list(es_sentences))

        results: List[str] = []
        es_cursor = 0
        for i, en_emb in enumerate(en_embs):
            if i == n - 1:
                results.append(" ".join(es_sentences[es_cursor:]))
                break
            remaining_subs = n - i - 1
            available = m - es_cursor - remaining_subs
            available = max(1, available)
            best_score = -float("inf")
            best_take = 1
            cumulative = np.zeros_like(es_embs[0])
            for take in range(1, available + 1):
                cumulative = cumulative + es_embs[es_cursor + take - 1]
                mean = cumulative / take
                denom = (np.linalg.norm(en_emb) * np.linalg.norm(mean)) or 1.0
                sim = float(en_emb @ mean) / denom
                en_len = len(sub_block_texts[i]) or 1
                es_len = sum(len(es_sentences[es_cursor + k]) for k in range(take)) or 1
                ratio_penalty = abs(math.log(en_len / es_len)) * 0.1
                score = sim - ratio_penalty
                if score > best_score:
                    best_score = score
                    best_take = take
            results.append(" ".join(es_sentences[es_cursor : es_cursor + best_take]))
            es_cursor += best_take
        return results
