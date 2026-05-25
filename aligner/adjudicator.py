from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

from aligner.block_builder import Block
from aligner.config import AlignerConfig

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
You verify Spanish translations of English literary text. For each pair you
will be given English source text, the candidate Spanish translation, and one
sentence of context from the surrounding paragraphs. Decide whether the
Spanish text is a faithful translation of the English. If it is not, either
because it is the wrong passage, badly mistranslated, missing key content, or
includes content that doesn't belong, propose a corrected Spanish replacement.
Reply only with JSON matching the provided schema."""


_SCHEMA = {
    "name": "alignment_decision",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "is_good_match": {
                "type": "boolean",
                "description": "True iff the Spanish reasonably translates the English.",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "0-1, how sure you are about the decision.",
            },
            "issue": {
                "type": ["string", "null"],
                "description": "Short explanation when is_good_match is false; null otherwise.",
            },
            "suggested_es_replacement": {
                "type": ["string", "null"],
                "description": (
                    "Replacement Spanish text when is_good_match is false. "
                    "Must be a literary translation of the English. Null when match is good."
                ),
            },
        },
        "required": ["is_good_match", "confidence", "issue", "suggested_es_replacement"],
        "additionalProperties": False,
    },
}


@dataclass
class AdjudicationDecision:
    is_good_match: bool
    confidence: float
    issue: Optional[str]
    suggested_es_replacement: Optional[str]
    model: str
    cached: bool = False


class Adjudicator:
    """OpenAI-backed verifier for low-confidence block translations.

    Disk-cached on SHA256(en_text + es_text + model) so re-runs are free.
    Designed to fail safe: any error short-circuits to leaving the original
    block intact; the rest of the run continues without adjudication.
    """

    def __init__(self, config: AlignerConfig):
        self.config = config
        self._client = None
        self._model = config.openai_model
        self._disabled = False
        self._calls_made = 0
        self._cache_dir = config.ensure_cache_dir()

    @property
    def enabled(self) -> bool:
        return (
            not self._disabled
            and self.config.adjudicator_enabled
            and bool(self.config.openai_api_key)
        )

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                logger.warning("openai package not installed; disabling adjudicator")
                self._disabled = True
                return None
            try:
                self._client = OpenAI(api_key=self.config.openai_api_key)
            except Exception as exc:
                logger.warning("Failed to construct OpenAI client (%s); disabling adjudicator", exc)
                self._disabled = True
                return None
        return self._client

    def adjudicate_blocks(self, blocks: Sequence[Block]) -> int:
        if not self.enabled:
            return 0
        candidates = [b for b in blocks if b.needs_adjudication and b.es_text]
        if not candidates:
            return 0
        if len(candidates) > self.config.adjudicator_max_calls_per_chapter:
            candidates.sort(key=lambda b: b.confidence)
            candidates = candidates[: self.config.adjudicator_max_calls_per_chapter]
            logger.info(
                "Capping adjudicator calls at %d (chapter had more low-confidence blocks)",
                self.config.adjudicator_max_calls_per_chapter,
            )

        fixed = 0
        for i, block in enumerate(candidates):
            if self._disabled:
                break
            context = self._build_context(blocks, block)
            decision = self.adjudicate(block.en_text, block.es_text, context)
            if decision is None:
                continue
            if not decision.is_good_match and decision.suggested_es_replacement:
                block.es_text = decision.suggested_es_replacement
                block.confidence = max(block.confidence, decision.confidence)
                block.needs_adjudication = False
                fixed += 1
            else:
                block.confidence = max(block.confidence, decision.confidence)
                block.needs_adjudication = False
        logger.info("Adjudicator processed %d/%d candidates; %d replaced", self._calls_made, len(candidates), fixed)
        return fixed

    # ----------------------------------------------------------- single decision

    def adjudicate(self, en_text: str, es_text: str, context: str) -> Optional[AdjudicationDecision]:
        cache_key = self._cache_key(en_text, es_text)
        cached = self._read_cache(cache_key)
        if cached is not None:
            cached.cached = True
            return cached

        client = self._get_client()
        if client is None:
            return None

        user_prompt = (
            f"CONTEXT: {context}\n\n"
            f"ENGLISH: {en_text}\n\n"
            f"SPANISH CANDIDATE: {es_text}"
        )

        for attempt, model in enumerate([self._model, self.config.openai_fallback_model]):
            if not model or (attempt > 0 and model == self._model):
                continue
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_schema", "json_schema": _SCHEMA},
                )
                self._calls_made += 1
                content = response.choices[0].message.content or "{}"
                data = json.loads(content)
                decision = AdjudicationDecision(
                    is_good_match=bool(data.get("is_good_match")),
                    confidence=float(data.get("confidence") or 0.0),
                    issue=data.get("issue"),
                    suggested_es_replacement=data.get("suggested_es_replacement"),
                    model=model,
                )
                self._write_cache(cache_key, decision)
                if attempt > 0:
                    self._model = model  # promote fallback for the rest of the run
                return decision
            except Exception as exc:
                logger.warning("Adjudicator call failed (model=%s, attempt=%d): %s", model, attempt, exc)
                continue
        self._disabled = True
        logger.warning("Disabling adjudicator after repeated failures")
        return None

    # -------------------------------------------------------------------- utils

    def _build_context(self, all_blocks: Sequence[Block], target: Block) -> str:
        try:
            idx = all_blocks.index(target)
        except ValueError:
            return ""
        bits: List[str] = []
        if idx > 0:
            prev = all_blocks[idx - 1].en_text
            bits.append(f"prev EN: {prev[:160]}")
        if idx + 1 < len(all_blocks):
            nxt = all_blocks[idx + 1].en_text
            bits.append(f"next EN: {nxt[:160]}")
        return " | ".join(bits)

    def _cache_key(self, en: str, es: str) -> str:
        h = hashlib.sha256()
        h.update(self._model.encode("utf-8"))
        h.update(b"\x00")
        h.update(en.encode("utf-8"))
        h.update(b"\x00")
        h.update(es.encode("utf-8"))
        return h.hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self._cache_dir / f"{key}.json"

    def _read_cache(self, key: str) -> Optional[AdjudicationDecision]:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return AdjudicationDecision(
                is_good_match=bool(data.get("is_good_match")),
                confidence=float(data.get("confidence") or 0.0),
                issue=data.get("issue"),
                suggested_es_replacement=data.get("suggested_es_replacement"),
                model=str(data.get("model") or self._model),
            )
        except Exception as exc:
            logger.debug("Failed to read cache %s: %s", path, exc)
            return None

    def _write_cache(self, key: str, decision: AdjudicationDecision) -> None:
        path = self._cache_path(key)
        try:
            path.write_text(
                json.dumps(
                    {
                        "is_good_match": decision.is_good_match,
                        "confidence": decision.confidence,
                        "issue": decision.issue,
                        "suggested_es_replacement": decision.suggested_es_replacement,
                        "model": decision.model,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.debug("Failed to write cache %s: %s", path, exc)
