from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, List, Optional

_SCENE_BREAK_RE = re.compile(r"^[\s*·•⁂❦※–—]+$")


@dataclass(frozen=True)
class StreamEvent:
    kind: str
    text: str
    source: Any = field(repr=False, compare=False)
    level: int = 0
    image_id: Optional[str] = None
    tag: str = "p"
    classes: tuple = ()

    @property
    def is_paragraph(self) -> bool:
        return self.kind == "paragraph"

    @property
    def is_header(self) -> bool:
        return self.kind == "header"

    @property
    def is_figure(self) -> bool:
        return self.kind == "figure"

    @property
    def is_caption(self) -> bool:
        return self.kind == "caption"

    @property
    def is_scene_break(self) -> bool:
        return self.kind == "scene_break"


def _kind_for_chunk(chunk: dict) -> str:
    ctype = chunk.get("type", "std")
    tag = chunk.get("tag", "p")
    text = (chunk.get("text") or "").strip()
    if ctype == "image":
        return "figure"
    if ctype == "header" or tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
        return "header"
    if ctype == "caption":
        return "caption"
    if tag == "li":
        return "list_item"
    if text and _SCENE_BREAK_RE.match(text):
        return "scene_break"
    return "paragraph"


def _header_level(chunk: dict) -> int:
    tag = chunk.get("tag", "")
    if len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
        return int(tag[1])
    return 1 if chunk.get("type") == "header" else 0


def _image_id(chunk: dict) -> Optional[str]:
    if chunk.get("type") != "image":
        return None
    src = chunk.get("src") or ""
    return os.path.basename(src) or None


class ReadingStream:
    """Ordered, typed view over a chapter's parsed chunks.

    Wraps the raw chunk dicts produced by EnglishParser/SpanishParser without
    mutating them, so the original DOM node references stay intact for later
    HTML injection by the footnote emitter.
    """

    def __init__(self, events: Iterable[StreamEvent]):
        self.events: List[StreamEvent] = list(events)

    @classmethod
    def from_chunks(cls, chunks: Iterable[dict]) -> "ReadingStream":
        events: List[StreamEvent] = []
        for chunk in chunks:
            text = (chunk.get("text") or "").strip()
            kind = _kind_for_chunk(chunk)
            if kind == "paragraph" and not text:
                continue
            events.append(
                StreamEvent(
                    kind=kind,
                    text=text,
                    source=chunk,
                    level=_header_level(chunk),
                    image_id=_image_id(chunk),
                    tag=chunk.get("tag", "p"),
                    classes=tuple(chunk.get("classes") or ()),
                )
            )
        return cls(events)

    def __iter__(self) -> Iterator[StreamEvent]:
        return iter(self.events)

    def __len__(self) -> int:
        return len(self.events)

    def __getitem__(self, idx):
        return self.events[idx]

    def paragraphs(self) -> List[StreamEvent]:
        return [e for e in self.events if e.is_paragraph]

    def headers(self) -> List[StreamEvent]:
        return [e for e in self.events if e.is_header]

    def figures(self) -> List[StreamEvent]:
        return [e for e in self.events if e.is_figure]

    def captions(self) -> List[StreamEvent]:
        return [e for e in self.events if e.is_caption]

    def alignable(self) -> List[StreamEvent]:
        """Events that participate in the EN-ES alignment (paragraphs + captions)."""
        return [e for e in self.events if e.kind in ("paragraph", "caption", "list_item")]
