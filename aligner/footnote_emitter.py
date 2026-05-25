from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from bs4 import BeautifulSoup, NavigableString, Tag

from aligner.block_builder import Block
from aligner.config import AlignerConfig

logger = logging.getLogger(__name__)


@dataclass
class EmitResult:
    asides: List[Tag]
    block_count: int
    sub_split_count: int
    orphan_count: int


_CSS = """\
a.es-block { color: inherit; text-decoration: none; }
sup.es-marker {
    color: #999; font-size: 0.7em; vertical-align: super;
    margin-left: 2px; font-weight: normal; text-decoration: none;
}
aside.es-note { display: none; }
aside.es-note p { margin: 0 0 0.4em 0; }
aside.es-note .es-extras { font-size: 0.85em; color: #555; margin-top: 0.5em; }
.es-onboarding {
    font-size: 0.9em; color: #555; border-left: 3px solid #888;
    padding-left: 0.8em; margin: 1em 0;
}
"""

MARKER_GLYPH = "·"
ONBOARDING_CLASS = "es-onboarding"


class FootnoteEmitter:
    """Mutates the EN DOM to add EPUB3 noteref tap-targets and emits asides.

    Per-paragraph behaviour:
    - Single block: wrap the paragraph's existing children in <a epub:type="noteref">.
    - Sub-blocks (long paragraph split): replace the paragraph's content with
      one <a> per sub-block. Loses inline markup inside the paragraph; this
      only affects paragraphs that were >280 chars and had >4 sentences.
    """

    def __init__(self, config: AlignerConfig):
        self.config = config
        self._counter = 0

    def reset_counter(self) -> None:
        self._counter = 0

    def next_id(self, chapter_prefix: str) -> str:
        self._counter += 1
        return f"{chapter_prefix}b{self._counter:04d}"

    def emit(
        self,
        blocks: Sequence[Block],
        soup: BeautifulSoup,
        chapter_prefix: str = "",
    ) -> EmitResult:
        asides: List[Tag] = []
        sub_split = 0
        orphan = 0

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
                note_id = self.next_id(chapter_prefix)
                asides.append(self._build_aside(soup, note_id, block))
                self._wrap_node_in_noteref(node, note_id, soup)
            else:
                sub_split += 1
                ids: List[str] = []
                for sub in node_blocks:
                    note_id = self.next_id(chapter_prefix)
                    ids.append(note_id)
                    asides.append(self._build_aside(soup, note_id, sub))
                self._replace_with_subblock_noterefs(node, node_blocks, ids, soup)

        return EmitResult(
            asides=asides,
            block_count=self._counter,
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

    def _build_aside(self, soup: BeautifulSoup, note_id: str, block: Block) -> Tag:
        aside = soup.new_tag("aside")
        aside["id"] = note_id
        aside["epub:type"] = "footnote"
        aside["hidden"] = ""
        aside["class"] = "es-note"
        if block.es_text:
            p = soup.new_tag("p", lang="es")
            p.string = block.es_text
            aside.append(p)
        elif not block.es_extras:
            placeholder = soup.new_tag("p", lang="es")
            placeholder.string = "—"
            aside.append(placeholder)
        if block.es_extras:
            extras = soup.new_tag("div")
            extras["class"] = "es-extras"
            label = soup.new_tag("p", lang="es")
            em = soup.new_tag("em")
            em.string = "Nota:"
            label.append(em)
            extras.append(label)
            for extra in block.es_extras:
                if not extra.text:
                    continue
                xp = soup.new_tag("p", lang="es")
                xp.string = extra.text
                extras.append(xp)
            aside.append(extras)
        return aside

    def _wrap_node_in_noteref(self, node: Tag, note_id: str, soup: BeautifulSoup) -> None:
        anchor = soup.new_tag("a")
        anchor["epub:type"] = "noteref"
        anchor["href"] = f"#{note_id}"
        anchor["class"] = "es-block"
        children = list(node.contents)
        for child in children:
            child.extract()
            anchor.append(child)
        anchor.append(self._make_marker(soup))
        node.append(anchor)

    def _make_marker(self, soup: BeautifulSoup) -> Tag:
        marker = soup.new_tag("sup")
        marker["class"] = "es-marker"
        marker.string = MARKER_GLYPH
        return marker

    def _replace_with_subblock_noterefs(
        self,
        node: Tag,
        sub_blocks: Sequence[Block],
        ids: Sequence[str],
        soup: BeautifulSoup,
    ) -> None:
        node.clear()
        for i, (block, note_id) in enumerate(zip(sub_blocks, ids)):
            anchor = soup.new_tag("a")
            anchor["epub:type"] = "noteref"
            anchor["href"] = f"#{note_id}"
            anchor["class"] = "es-block"
            anchor.append(NavigableString(block.en_text))
            anchor.append(self._make_marker(soup))
            node.append(anchor)
            if i < len(sub_blocks) - 1:
                node.append(NavigableString(" "))

    # ------------------------------------------------------------- chapter ops

    def install_asides(self, soup: BeautifulSoup, asides: Iterable[Tag]) -> None:
        body = soup.find("body")
        if body is None:
            return
        container = soup.find("section", attrs={"class": "es-footnotes"})
        if container is None:
            container = soup.new_tag("section")
            container["class"] = "es-footnotes"
            container["epub:type"] = "footnotes"
            body.append(container)
        for aside in asides:
            container.append(aside)

    def install_stylesheet(self, soup: BeautifulSoup) -> None:
        head = soup.find("head")
        if head is None:
            return
        for existing in head.find_all("style"):
            if existing.string and "a.es-block" in existing.string:
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
        notice.string = self.config.onboarding_notice
        first_child = next((c for c in body.contents if isinstance(c, Tag)), None)
        if first_child is None:
            body.insert(0, notice)
        else:
            first_child.insert_before(notice)

    # ------------------------------------------------------- epub namespace fix

    @staticmethod
    def ensure_epub_namespace(soup: BeautifulSoup) -> None:
        html = soup.find("html")
        if html is None:
            return
        if html.get("xmlns:epub") is None:
            html["xmlns:epub"] = "http://www.idpf.org/2007/ops"
