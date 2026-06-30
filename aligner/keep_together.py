"""Keep an English paragraph and its Spanish translation together across page
breaks. Dependency-light (BeautifulSoup only) so the post-processing script can
reuse it without pulling in the alignment pipeline's ML stack.

Three strategies, all keyed off the ``es-tandem`` marker the inline emitter puts
on every Spanish translation:

- **merge** (``merge_pairs``): fold each English element and its Spanish
  translation(s) into a *single* block — the English text, a ``<br/>``, and a
  ``<span class="es-tandem" lang="es">`` per Spanish part. A single block has no
  *between-block* break point, so e-readers that ignore CSS fragmentation
  entirely (Onyx Boox NeoReader, Moon+ Reader, and most custom-paginating
  Android readers) cannot split the English from its translation across a page.
  This is the only technique that survives readers with no real CSS break
  support; the CSS hints below are honored by Calibre/ADE-class engines but are
  documented no-ops on the readers above (they fake pagination with CSS
  multi-columns and do not implement ``break-inside``).
- **wrap** (``wrap_pairs``): enclose each English element + its Spanish
  translation(s) in one ``<div class="keeptogether"
  style="page-break-inside:avoid;break-inside:avoid">``. ``break-inside:avoid``
  on a *container* is the most reliably honored break hint *among fragmentation-
  aware readers*, so the whole pair is pushed to the next page (leaving a gap)
  instead of being split across it. NOTE: the ``-webkit-column-break-inside``
  fallback for multicolumn-paginating readers must NOT be added to this inline
  style — declaring it in the same rule as ``page-break-inside`` makes some
  WebKit readers ignore *both* (standardebooks/tools#101). It belongs in a
  stylesheet behind an ``@supports`` guard (see ``inline_emitter._CSS``).
- **flat** (the per-element fallback applied by ``_apply_flat_breaks``):
  ``page-break-after:avoid`` on the English element and ``page-break-before:
  avoid`` on the Spanish one. No structural change, but break-avoid *between
  sibling blocks* is weakly honored. Used automatically by ``wrap_pairs`` where a
  ``<div>`` is not valid markup (e.g. a ``<li>`` pair inside ``<ul>``/``<ol>``);
  ``merge_pairs`` has no such restriction since it adds no wrapper element.
"""
from __future__ import annotations

from typing import List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag

# Marker class the inline emitter puts on every Spanish translation element.
ES_CLASS = "es-tandem"

# "wrap" keep-together container.
WRAP_CLASS = "keeptogether"
WRAP_STYLE = "page-break-inside:avoid;break-inside:avoid"

# Inline elements the "merge" strategy itself introduces (the <br/> and the
# <span> carrying the Spanish). They must never be treated as a pair boundary,
# or a second merge_pairs pass would re-merge an already-merged block — keeping
# the pass idempotent.
_MERGE_INLINE_FORMS = frozenset(("br", "span"))

# Style properties that carry the "flat" sibling break-avoid hints.
_FLAT_BREAK_PROPS = frozenset(
    ("page-break-before", "page-break-after", "break-before", "break-after")
)

# Parents in which a <div> is NOT valid content: phrasing/inline contexts and
# the list/table/definition element-content models. A pair living directly
# inside one of these gets the structurally-safe flat break-avoid fallback
# instead of a <div> wrapper — e.g. <li> inside <ul> would otherwise produce the
# invalid <ul><div><li>…</li></div></ul>.
_DIV_FORBIDDEN_PARENTS = frozenset(
    (
        "p", "span", "a", "em", "strong", "i", "b", "small", "sub", "sup",
        "ul", "ol", "dl", "tr", "table", "thead", "tbody", "tfoot", "colgroup",
    )
)


def _next_element_sibling(tag: Tag) -> Optional[Tag]:
    """The next sibling that is an element, skipping whitespace/text nodes."""
    sib = tag.next_sibling
    while sib is not None and not isinstance(sib, Tag):
        sib = sib.next_sibling
    return sib if isinstance(sib, Tag) else None


def _append_decls(el: Tag, decls: str) -> None:
    style = (el.get("style") or "").strip()
    if style and not style.endswith(";"):
        style += ";"
    el["style"] = style + decls


def _strip_flat_breaks(el: Tag) -> None:
    """Drop any ``(page-)break-before/after:avoid`` declarations from ``el``
    while keeping every other declaration (margins, indents, …). Used when
    upgrading a flat-strategy EPUB: the wrapping div now owns the break
    behavior, so the per-paragraph hints are redundant."""
    style = el.get("style")
    if not style:
        return
    kept = []
    for decl in style.split(";"):
        prop = decl.split(":", 1)[0].strip().lower()
        if prop in _FLAT_BREAK_PROPS:
            continue
        if decl.strip():
            kept.append(decl.strip())
    if kept:
        el["style"] = ";".join(kept)
    else:
        del el["style"]


def _apply_flat_breaks(group: List[Tag]) -> bool:
    """Structurally-safe keep-together fallback for a pair that cannot be
    enclosed in a ``<div>`` (e.g. a ``<li>`` inside ``<ul>``/``<ol>``): put
    ``break-after:avoid`` on the English element and ``break-before:avoid`` on
    each Spanish element — the same hints the flat strategy uses. Applied
    idempotently; returns True iff it added anything."""
    changed = False
    for i, el in enumerate(group):
        if i == 0:
            if "break-after:avoid" in (el.get("style") or ""):
                continue
            _append_decls(el, "page-break-after:avoid;break-after:avoid")
        else:
            if "break-before:avoid" in (el.get("style") or ""):
                continue
            _append_decls(el, "page-break-before:avoid;break-before:avoid")
        changed = True
    return changed


def wrap_pairs(soup: BeautifulSoup, *, strip_flat: bool = False) -> int:
    """Keep every English element together with its immediately-following
    Spanish translation(s). Returns the number of pairs kept together.

    A "pair" is any element whose next element sibling carries the ``es-tandem``
    class, plus every consecutive ``es-tandem`` sibling after it (the Spanish
    translation and any orphan-note extras). English-only elements — those with
    no ``es-tandem`` sibling — are left untouched so a page break can still fall
    between blocks.

    Where a ``<div>`` is valid content of the pair's parent, the pair is
    enclosed in ``<div class="keeptogether" style="…break-inside:avoid">``.
    Where it is not (a ``<li>`` inside ``<ul>``/``<ol>``, a table cell, an inline
    context, …), the pair instead gets per-element ``break-avoid`` hints so the
    markup stays valid. Elements already inside a ``keeptogether`` div are
    skipped, so the pass is idempotent.

    ``strip_flat=True`` removes pre-existing break-before/after:avoid hints from
    the *wrapped* paragraphs (for converting a flat-strategy EPUB to wrap);
    fallback pairs keep their hints since that is exactly how they stay together.
    """
    root = soup.find("body") or soup
    # Snapshot the starters first: the loop mutates the tree (moving elements
    # into wrappers), but each starter stays at its original position so the
    # collected references remain valid.
    starters = [
        el
        for el in root.find_all(True)
        if ES_CLASS not in (el.get("class") or [])
        and (
            (nxt := _next_element_sibling(el)) is not None
            and ES_CLASS in (nxt.get("class") or [])
        )
    ]

    kept = 0
    for en in starters:
        parent = en.parent
        if (
            parent is not None
            and parent.name == "div"
            and WRAP_CLASS in (parent.get("class") or [])
        ):
            # Already wrapped (idempotent). Re-assert the current WRAP_STYLE so a
            # re-run heals wrappers written with an older style string instead of
            # leaving them stale — the wrapper carries no style but the keep-
            # together declarations, so a flat overwrite is safe.
            parent["style"] = WRAP_STYLE
            continue
        group = [en]
        sib = _next_element_sibling(en)
        while sib is not None and ES_CLASS in (sib.get("class") or []):
            group.append(sib)
            sib = _next_element_sibling(sib)

        if parent is None or parent.name in _DIV_FORBIDDEN_PARENTS:
            # A <div> would be invalid content here; keep the pair together with
            # per-element break-avoid hints instead of restructuring.
            if _apply_flat_breaks(group):
                kept += 1
            continue

        wrapper = soup.new_tag("div")
        wrapper["class"] = [WRAP_CLASS]
        wrapper["style"] = WRAP_STYLE
        en.insert_before(wrapper)
        for member in group:
            if strip_flat:
                _strip_flat_breaks(member)
            wrapper.append(member.extract())
        kept += 1
    return kept


def _strip_keep_hints(el: Tag) -> None:
    """Remove the keep-together CSS hints (break-avoid declarations and the
    ``margin-top/bottom:0`` pair-tightening) from ``el``'s inline style, keeping
    every other declaration. Used by ``merge_pairs`` when folding a pair that was
    previously laid out for the wrap/flat strategies: once the pair is a single
    block those hints are meaningless, and ``margin-bottom:0`` would wrongly
    glue this block to the next pair."""
    style = el.get("style")
    if not style:
        return
    kept = []
    for decl in style.split(";"):
        decl = decl.strip()
        if not decl:
            continue
        prop, _, val = decl.partition(":")
        prop = prop.strip().lower()
        if prop in _FLAT_BREAK_PROPS:
            continue
        if prop in ("margin-top", "margin-bottom") and val.strip().lower() in (
            "0", "0px", "0em", "0rem", "0%"
        ):
            continue
        kept.append(decl)
    if kept:
        el["style"] = ";".join(kept)
    else:
        del el["style"]


def merge_pairs(soup: BeautifulSoup) -> int:
    """Fold every English element and its immediately-following Spanish
    translation(s) into a *single* block element. Returns the number of pairs
    merged.

    The English element keeps its tag, id and classes (so drop-caps / structural
    styling survive); each Spanish sibling is moved into it as a ``<br/>`` plus a
    ``<span class="es-tandem" lang="es">`` carrying the Spanish text. The now-
    empty Spanish block is removed. The merged block is then given the
    ``keeptogether`` class and ``break-inside:avoid`` so it behaves as one
    keep-together unit.

    Why this and not ``wrap_pairs``: the keep hint alone is not enough on its
    own. ``break-inside:avoid`` (here, and on a wrapper ``<div>`` in wrap mode)
    makes fragmentation-aware engines (Calibre, Kindle, Adobe DE) push the whole
    pair to the next page — but readers that fake pagination with CSS
    multi-columns (Onyx Boox NeoReader, Moon+ Reader, most custom-paginating
    Android readers) ignore it. For *those*, the structural win is that a single
    block has no *between-block* split point: wrap leaves a tempting block
    boundary between the English and Spanish paragraphs that the reader splits
    at, whereas merge only lets a pair split if it is itself taller than the
    remaining page (rare when pairs are short — keep ``word_budget_split`` on).

    Works on freshly-emitted EN/ES sibling pairs (live ``"merge"`` mode) and as a
    post-hoc converter for an EPUB already laid out with the wrap or flat
    strategy: a leftover single-child ``keeptogether`` ``<div>`` is unwrapped and
    the per-element break/margin hints are migrated onto the merged block.
    Naturally idempotent — after a pass the ``es-tandem`` *blocks* are gone (they
    are now inline spans), so a second pass finds no pairs.
    """
    root = soup.find("body") or soup
    starters = [
        el
        for el in root.find_all(True)
        if el.name not in _MERGE_INLINE_FORMS
        and ES_CLASS not in (el.get("class") or [])
        and (
            (nxt := _next_element_sibling(el)) is not None
            and nxt.name not in _MERGE_INLINE_FORMS
            and ES_CLASS in (nxt.get("class") or [])
        )
    ]

    merged = 0
    for en in starters:
        es_group = []
        sib = _next_element_sibling(en)
        while (
            sib is not None
            and sib.name not in _MERGE_INLINE_FORMS
            and ES_CLASS in (sib.get("class") or [])
        ):
            es_group.append(sib)
            sib = _next_element_sibling(sib)
        if not es_group:
            continue

        for es in es_group:
            en.append(soup.new_tag("br"))
            span = soup.new_tag("span")
            # Carry only the es-* markers (es-tandem, es-nota) onto the span; the
            # structural class belongs to the block, not the inline translation.
            es_classes = [
                c for c in (es.get("class") or []) if c.startswith("es")
            ]
            if ES_CLASS not in es_classes:
                es_classes.insert(0, ES_CLASS)
            span["class"] = es_classes
            span["lang"] = "es"
            span.append(NavigableString(es.get_text()))
            en.append(span)
            es.extract()

        # The single block IS the keep-together unit now. Strip any stale flat/
        # margin hints, then make the block itself a keeptogether element:
        #  - break-inside:avoid makes fragmentation-aware readers (Calibre,
        #    Kindle, Adobe DE) push the WHOLE pair to the next page rather than
        #    breaking inside it — without this the block splits by line just
        #    like any other paragraph.
        #  - the keeptogether class lets the @supports -webkit-column-break-inside
        #    fallback (in the stylesheet) reach this block on multicolumn-
        #    paginating readers (some Android readers / Boox engines).
        # Readers that honor neither still benefit from there being no *between-
        # block* split point: a pair only splits if it is taller than the page.
        _strip_keep_hints(en)
        classes = list(en.get("class") or [])
        if WRAP_CLASS not in classes:
            classes.append(WRAP_CLASS)
        en["class"] = classes
        if "break-inside:avoid" not in (en.get("style") or ""):
            _append_decls(en, WRAP_STYLE)
        # Unwrap a leftover one-child keeptogether <div> (post-hoc wrap->merge);
        # the break hint now lives on the block itself, so the wrapper is moot.
        div = en.parent
        if (
            div is not None
            and div.name == "div"
            and WRAP_CLASS in (div.get("class") or [])
            and all(c is en for c in div.find_all(True, recursive=False))
        ):
            div.insert_before(en.extract())
            div.extract()

        merged += 1
    return merged
