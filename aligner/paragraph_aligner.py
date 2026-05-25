from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

from aligner.config import AlignerConfig
from aligner.reading_stream import ReadingStream, StreamEvent

logger = logging.getLogger(__name__)

_GAP_COST = 0.75
_HEADER_BONUS = 0.20
_FIGURE_PENALTY = 0.15
_MAX_SPAN = 3


@dataclass(frozen=True)
class AlignedPair:
    en_indices: Tuple[int, ...]
    es_indices: Tuple[int, ...]
    confidence: float
    transition: str
    is_anchor: bool = False
    en_events: Tuple[StreamEvent, ...] = field(default_factory=tuple, repr=False)
    es_events: Tuple[StreamEvent, ...] = field(default_factory=tuple, repr=False)

    @property
    def is_en_only(self) -> bool:
        return bool(self.en_indices) and not self.es_indices

    @property
    def is_es_only(self) -> bool:
        return not self.en_indices and bool(self.es_indices)


class ParagraphAligner:
    """Bertalign-style two-step paragraph aligner.

    Step 1: top-k mutual nearest neighbours produce monotonic anchors.
    Step 2: DP over span pairs (1:1, 1:2, 2:1, 2:2, plus 1:0 / 0:1 gaps) between
    anchors, minimising (1 - cosine_sim) + length_ratio_penalty.
    """

    def __init__(self, config: AlignerConfig, model=None):
        self.config = config
        self._model = model

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s", self.config.embedding_model)
            self._model = SentenceTransformer(self.config.embedding_model)
        return self._model

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 768), dtype=np.float32)
        embs = self.model.encode(list(texts), show_progress_bar=False, convert_to_numpy=True)
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (embs / norms).astype(np.float32)

    def align(
        self,
        en_stream: ReadingStream,
        es_stream: ReadingStream,
    ) -> List[AlignedPair]:
        en_events = en_stream.alignable()
        es_events = es_stream.alignable()
        if not en_events and not es_events:
            return []
        if not en_events:
            return [
                AlignedPair((), (i,), 0.0, "0:1", False, (), (e,))
                for i, e in enumerate(es_events)
            ]
        if not es_events:
            return [
                AlignedPair((i,), (), 0.0, "1:0", False, (e,), ())
                for i, e in enumerate(en_events)
            ]

        en_texts = [e.text for e in en_events]
        es_texts = [e.text for e in es_events]
        en_embs = self.encode(en_texts)
        es_embs = self.encode(es_texts)

        sim = en_embs @ es_embs.T  # cosine similarity (rows L2-normalised)
        anchors = self._find_anchors(sim, en_events, es_events)
        return self._align_with_anchors(
            en_events, es_events, en_embs, es_embs, sim, anchors
        )

    # ------------------------------------------------------------------ anchors

    def _find_anchors(
        self,
        sim: np.ndarray,
        en_events: Sequence[StreamEvent],
        es_events: Sequence[StreamEvent],
    ) -> List[Tuple[int, int, float]]:
        n, m = sim.shape
        if n == 0 or m == 0:
            return []
        k = min(self.config.anchor_top_k, m, n)
        en_topk = np.argsort(-sim, axis=1)[:, :k]
        es_topk = np.argsort(-sim.T, axis=1)[:, :k]
        es_topk_sets = [set(row.tolist()) for row in es_topk]

        candidates: List[Tuple[int, int, float]] = []
        threshold = self.config.anchor_min_similarity
        for i in range(n):
            for j in en_topk[i]:
                s = float(sim[i, j])
                if s < threshold:
                    continue
                if i in es_topk_sets[j]:
                    bonus = 0.0
                    if en_events[i].is_header and es_events[j].is_header:
                        bonus += _HEADER_BONUS
                    if en_events[i].is_figure != es_events[j].is_figure:
                        bonus -= _FIGURE_PENALTY
                    candidates.append((i, int(j), s + bonus))

        candidates.sort(key=lambda x: -x[2])
        selected: List[Tuple[int, int, float]] = []
        used_en, used_es = set(), set()
        for i, j, score in candidates:
            if i in used_en or j in used_es:
                continue
            if not all(
                (ei < i and ej < j) or (ei > i and ej > j)
                for ei, ej, _ in selected
            ):
                continue
            selected.append((i, j, score))
            used_en.add(i)
            used_es.add(j)
        selected.sort(key=lambda x: x[0])
        logger.debug("Found %d mutual-NN anchors out of %d candidates", len(selected), len(candidates))
        return selected

    # ----------------------------------------------------------------- DP body

    def _align_with_anchors(
        self,
        en_events: Sequence[StreamEvent],
        es_events: Sequence[StreamEvent],
        en_embs: np.ndarray,
        es_embs: np.ndarray,
        sim: np.ndarray,
        anchors: List[Tuple[int, int, float]],
    ) -> List[AlignedPair]:
        pairs: List[AlignedPair] = []
        en_cursor, es_cursor = 0, 0
        for ai, aj, score in anchors:
            if ai > en_cursor or aj > es_cursor:
                pairs.extend(
                    self._dp_segment(
                        en_events, es_events,
                        en_embs, es_embs, sim,
                        en_cursor, ai, es_cursor, aj,
                    )
                )
            confidence = float(min(1.0, max(0.0, score)))
            pairs.append(
                AlignedPair(
                    en_indices=(ai,),
                    es_indices=(aj,),
                    confidence=confidence,
                    transition="1:1",
                    is_anchor=True,
                    en_events=(en_events[ai],),
                    es_events=(es_events[aj],),
                )
            )
            en_cursor, es_cursor = ai + 1, aj + 1

        if en_cursor < len(en_events) or es_cursor < len(es_events):
            pairs.extend(
                self._dp_segment(
                    en_events, es_events,
                    en_embs, es_embs, sim,
                    en_cursor, len(en_events),
                    es_cursor, len(es_events),
                )
            )
        return pairs

    def _dp_segment(
        self,
        en_events: Sequence[StreamEvent],
        es_events: Sequence[StreamEvent],
        en_embs: np.ndarray,
        es_embs: np.ndarray,
        sim: np.ndarray,
        en_lo: int, en_hi: int,
        es_lo: int, es_hi: int,
    ) -> List[AlignedPair]:
        n = en_hi - en_lo
        m = es_hi - es_lo
        if n == 0 and m == 0:
            return []
        if n == 0:
            return [
                AlignedPair((), (es_lo + j,), 0.0, "0:1", False, (), (es_events[es_lo + j],))
                for j in range(m)
            ]
        if m == 0:
            return [
                AlignedPair((en_lo + i,), (), 0.0, "1:0", False, (en_events[en_lo + i],), ())
                for i in range(n)
            ]

        INF = float("inf")
        cost = [[INF] * (m + 1) for _ in range(n + 1)]
        back: List[List[Optional[Tuple[int, int]]]] = [
            [None] * (m + 1) for _ in range(n + 1)
        ]
        cost[0][0] = 0.0

        transitions: List[Tuple[int, int]] = []
        for di in range(0, _MAX_SPAN + 1):
            for dj in range(0, _MAX_SPAN + 1):
                if di == 0 and dj == 0:
                    continue
                if di + dj > _MAX_SPAN + 1:
                    continue
                transitions.append((di, dj))

        for i in range(n + 1):
            for j in range(m + 1):
                if cost[i][j] == INF:
                    continue
                for di, dj in transitions:
                    ni, nj = i + di, j + dj
                    if ni > n or nj > m:
                        continue
                    step_cost = self._step_cost(
                        en_events, es_events, en_embs, es_embs, sim,
                        en_lo + i, en_lo + ni,
                        es_lo + j, es_lo + nj,
                    )
                    nc = cost[i][j] + step_cost
                    if nc < cost[ni][nj]:
                        cost[ni][nj] = nc
                        back[ni][nj] = (i, j)

        # Backtrack
        path: List[Tuple[int, int, int, int]] = []
        ci, cj = n, m
        while (ci, cj) != (0, 0):
            prev = back[ci][cj]
            if prev is None:
                # Fall back: emit remainder as gaps
                while ci > 0:
                    ci -= 1
                    path.append((ci, ci + 1, cj, cj))
                while cj > 0:
                    cj -= 1
                    path.append((ci, ci, cj, cj + 1))
                break
            pi, pj = prev
            path.append((pi, ci, pj, cj))
            ci, cj = pi, pj
        path.reverse()

        out: List[AlignedPair] = []
        for pi, qi, pj, qj in path:
            di, dj = qi - pi, qj - pj
            en_idx = tuple(en_lo + x for x in range(pi, qi))
            es_idx = tuple(es_lo + y for y in range(pj, qj))
            if not en_idx and not es_idx:
                continue
            transition = f"{di}:{dj}"
            confidence = self._pair_confidence(
                en_embs, es_embs, en_lo + pi, en_lo + qi, es_lo + pj, es_lo + qj
            )
            out.append(
                AlignedPair(
                    en_indices=en_idx,
                    es_indices=es_idx,
                    confidence=confidence,
                    transition=transition,
                    is_anchor=False,
                    en_events=tuple(en_events[k] for k in en_idx),
                    es_events=tuple(es_events[k] for k in es_idx),
                )
            )
        return out

    # ------------------------------------------------------------ cost helpers

    def _step_cost(
        self,
        en_events: Sequence[StreamEvent],
        es_events: Sequence[StreamEvent],
        en_embs: np.ndarray,
        es_embs: np.ndarray,
        sim: np.ndarray,
        i0: int, i1: int,
        j0: int, j1: int,
    ) -> float:
        di, dj = i1 - i0, j1 - j0
        if di == 0 and dj > 0:
            return _GAP_COST * dj
        if dj == 0 and di > 0:
            return _GAP_COST * di
        if di == 1 and dj == 1:
            base = 1.0 - float(sim[i0, j0])
        else:
            en_vec = en_embs[i0:i1].mean(axis=0)
            es_vec = es_embs[j0:j1].mean(axis=0)
            denom = (np.linalg.norm(en_vec) * np.linalg.norm(es_vec)) or 1.0
            base = 1.0 - float(en_vec @ es_vec) / denom
        en_chars = sum(len(en_events[k].text) for k in range(i0, i1)) or 1
        es_chars = sum(len(es_events[k].text) for k in range(j0, j1)) or 1
        ratio_penalty = abs(math.log(en_chars / es_chars)) * self.config.length_ratio_alpha
        span_penalty = 0.05 * max(0, (di - 1) + (dj - 1))
        return base + ratio_penalty + span_penalty

    def _pair_confidence(
        self,
        en_embs: np.ndarray,
        es_embs: np.ndarray,
        i0: int, i1: int, j0: int, j1: int,
    ) -> float:
        if i1 == i0 or j1 == j0:
            return 0.0
        en_vec = en_embs[i0:i1].mean(axis=0)
        es_vec = es_embs[j0:j1].mean(axis=0)
        denom = (np.linalg.norm(en_vec) * np.linalg.norm(es_vec)) or 1.0
        sim = float(en_vec @ es_vec) / denom
        span = (i1 - i0) + (j1 - j0)
        return float(max(0.0, min(1.0, sim - 0.04 * max(0, span - 2))))
