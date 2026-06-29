from __future__ import annotations

import logging
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag

from aligner.block_builder import Block
from aligner.config import AlignerConfig
from aligner.footnote_emitter import EmitResult

logger = logging.getLogger(__name__)


_CSS = """\
p[lang="es"].es-tandem, .es-tandem { }
.es-tandem.es-nota { font-size: 0.85em; color: #555; }
.es-onboarding {
    font-size: 0.9em; color: #555; border-left: 3px solid #888;
    padding-left: 0.8em; margin: 1em 0;
}
"""

ONBOARDING_CLASS = "es-onboarding"
ES_CLASS = "es-tandem"

# Cosmetic first-of-paragraph classes (drop caps / chapter openers) that must
# not be repeated on mid-paragraph English chunks or on Spanish paragraphs.
_DROPCAP_RE = re.compile(r"drop|lettrine|first[-_]?(letter|para)|initial|opener", re.I)


class InlineBilingualEmitter:
    """Mutates the EN DOM to interleave each English chunk with its visible
    Spanish translation, strongly discouraging a page break between an
    English→Spanish pair.

    Per paragraph:
    - Single block: insert a Spanish paragraph right after the English one.
    - Split (sub-blocks): replace the English paragraph with a sequence of
      English-chunk / Spanish-chunk pairs, each kept together.

    Keep-together uses the "flat" strategy (CSS directly on the paragraphs):
    ``page-break-after:avoid`` on the English side and ``page-break-before:avoid``
    on its Spanish side. Breaks between pairs are still allowed. Note this is a
    hint, not a guarantee: Apple Books and most Kobo readers honor it, but
    Kindle/KFX may still break a pair (``avoid`` is the strongest CSS offers).
    """

    def __init__(self, config: AlignerConfig):
        self.config = config

    def reset_counter(self) -> None:  # parity with FootnoteEmitter
        pass

    def emit(
        self,
        blocks: Sequence[Block],
        soup: BeautifulSoup,
        chapter_prefix: str = "",
    ) -> EmitResult:
        sub_split = 0
        orphan = 0
        pair_count = 0

        by_node: Dict[int, List[Block]] = {}
        node_order: List[int] = []
        for block in blocks:
            node = self._dom_node(block)
            if node is None:
                if block.es_text or block.es_extras:
                    orphan += 1
                continue
            key = id(node)
            if key not in by_node:
                by_node[key] = []
                node_order.append(key)
            by_node[key].append(block)

        for key in node_order:
            node_blocks = sorted(by_node[key], key=lambda b: b.sub_index)
            node = self._dom_node(node_blocks[0])
            if node is None:
                continue
            if len(node_blocks) == 1:
                block = node_blocks[0]
                _, emitted = self._emit_es(node, block, node, soup)
                if emitted:
                    self._apply_keep(node, "en")
                    pair_count += 1
                # else: English-only block, leave it untouched.
            else:
                sub_split += 1
                pair_count += self._replace_with_inline_pairs(node, node_blocks, soup)

        return EmitResult(
            asides=[],
            block_count=pair_count,
            sub_split_count=sub_split,
            orphan_count=orphan,
        )

    # ----------------------------------------------------------------- helpers

    def _dom_node(self, block: Block) -> Optional[Tag]:
        ev = block.en_event
        if ev is None:
            return None
        source = ev.source
        if not isinstance(source, dict):
            return None
        return source.get("node")

    def _replace_with_inline_pairs(
        self, node: Tag, sub_blocks: Sequence[Block], soup: BeautifulSoup
    ) -> int:
        """Reuse the original node for the first English chunk (keeps its class,
        id and any drop-cap styling), then append the remaining EN/ES pairs as
        new sibling paragraphs after it. Returns the number of pairs that
        actually emitted Spanish (English chunks are always kept). The
        keep-together rule is applied to an English chunk only when its Spanish
        was emitted, so it never binds to an unrelated following paragraph."""
        pairs = 0
        first = sub_blocks[0]
        node.clear()
        node.append(NavigableString(first.en_text))
        ref, emitted = self._emit_es(node, first, node, soup)
        if emitted:
            self._apply_keep(node, "en")
            pairs += 1
        for sub in sub_blocks[1:]:
            en_p = soup.new_tag(node.name)
            # Strip cosmetic drop-cap/first-letter classes so they don't repeat
            # mid-paragraph; structural classes (indent, etc.) are preserved.
            self._copy_class(node, en_p)
            en_p.append(NavigableString(sub.en_text))
            ref.insert_after(en_p)
            ref, emitted = self._emit_es(en_p, sub, node, soup)
            if emitted:
                self._apply_keep(en_p, "en")
                pairs += 1
        return pairs

    def _emit_es(
        self, ref: Tag, block: Block, base_node: Tag, soup: BeautifulSoup
    ) -> Tuple[Tag, bool]:
        """Insert the Spanish paragraph (plus any orphan extras) after ``ref``,
        applying keep-before CSS. Returns (new_ref, emitted) where emitted is
        True iff at least one paragraph was actually inserted."""
        emitted = False
        es_p = self._make_es_para(soup, block, base_node)
        if es_p is not None:
            self._apply_keep(es_p, "es")
            ref.insert_after(es_p)
            ref = es_p
            emitted = True
        for extra_p in self._make_extra_paras(soup, block, base_node):
            self._apply_keep(extra_p, "es")
            ref.insert_after(extra_p)
            ref = extra_p
            emitted = True
        return ref, emitted

    def _make_es_para(
        self, soup: BeautifulSoup, block: Block, base_node: Tag
    ) -> Optional[Tag]:
        text = (block.es_text or "").strip()
        if not text:
            return None
        name = base_node.name if base_node is not None and base_node.name else "p"
        p = soup.new_tag(name)
        self._copy_class(base_node, p, extra=ES_CLASS)
        p["lang"] = "es"
        p.append(NavigableString(text))
        return p

    def _make_extra_paras(
        self, soup: BeautifulSoup, block: Block, base_node: Tag
    ) -> List[Tag]:
        out: List[Tag] = []
        for extra in block.es_extras or []:
            text = (getattr(extra, "text", "") or "").strip()
            if not text:
                continue
            p = soup.new_tag("p")
            p["lang"] = "es"
            p["class"] = [ES_CLASS, "es-nota"]
            p.append(NavigableString(text))
            out.append(p)
        return out

    @staticmethod
    def _copy_class(src: Optional[Tag], dest: Tag, extra: Optional[str] = None) -> None:
        """Copy the source paragraph's classes onto a synthesized paragraph,
        dropping cosmetic drop-cap/first-letter classes that must not repeat."""
        classes: List[str] = []
        if src is not None:
            cls = src.get("class")
            if cls:
                raw = list(cls) if isinstance(cls, list) else [cls]
                classes = [c for c in raw if c and not _DROPCAP_RE.search(c)]
        if extra and extra not in classes:
            classes.append(extra)
        if classes:
            dest["class"] = classes

    def _apply_keep(self, p: Optional[Tag], role: str) -> None:
        if p is None:
            return
        mode = (self.config.keep_together_mode or "flat").lower()
        if mode == "none":
            return
        if role == "en":
            rule = "page-break-after:avoid;break-after:avoid;margin-bottom:0"
        else:
            rule = "page-break-before:avoid;break-before:avoid;margin-top:0"
        style = (p.get("style") or "").strip()
        if style and not style.endswith(";"):
            style += ";"
        p["style"] = style + rule

    # ------------------------------------------------------------- chapter ops

    def install_asides(self, soup: BeautifulSoup, asides: Iterable[Tag]) -> None:
        # No asides in inline mode; method kept for emitter parity.
        return

    def install_stylesheet(self, soup: BeautifulSoup) -> None:
        head = soup.find("head")
        if head is None:
            return
        for existing in head.find_all("style"):
            if existing.string and "es-tandem" in existing.string:
                return
        style = soup.new_tag("style")
        style.string = _CSS
        head.append(style)

    def install_onboarding(self, soup: BeautifulSoup) -> None:
        body = soup.find("body")
        if body is None:
            return
        if body.find(attrs={"class": ONBOARDING_CLASS}):
            return
        notice = soup.new_tag("p")
        notice["class"] = ONBOARDING_CLASS
        notice.string = (
            "Cada pasaje en inglés va seguido de su traducción al español. — "
            "Each English passage is followed by its Spanish translation."
        )
        first_child = next((c for c in body.contents if isinstance(c, Tag)), None)
        if first_child is None:
            body.insert(0, notice)
        else:
            first_child.insert_before(notice)

    @staticmethod
    def ensure_epub_namespace(soup: BeautifulSoup) -> None:
        # Inline mode emits no epub:type attributes; nothing to ensure.
        return
