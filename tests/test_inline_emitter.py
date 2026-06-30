import os
import sys
import unittest

from bs4 import BeautifulSoup

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aligner.block_builder import Block
from aligner.config import AlignerConfig
from aligner.inline_emitter import InlineBilingualEmitter, merge_pairs, wrap_pairs
from aligner.paragraph_aligner import AlignedPair
from aligner.reading_stream import StreamEvent


def _pair():
    return AlignedPair(
        en_indices=(0,), es_indices=(0,), confidence=0.9, transition="1:1",
    )


def _block(node, en_text, es_text, kind="paragraph", sub_index=0, sub_count=1):
    ev = StreamEvent(kind=kind, text=en_text, source={"node": node})
    return Block(
        en_text=en_text, es_text=es_text, en_event=ev, kind=kind,
        confidence=0.9, pair=_pair(), sub_index=sub_index, sub_count=sub_count,
    )


def _soup(body_html):
    return BeautifulSoup(
        f"<html><head></head><body>{body_html}</body></html>", "html.parser"
    )


class TestInlineEmitter(unittest.TestCase):
    def setUp(self):
        self.cfg = AlignerConfig()  # output_mode=inline, keep_together_mode=wrap
        self.emitter = InlineBilingualEmitter(self.cfg)

    def test_single_block_wraps_pair_in_keeptogether_div(self):
        soup = _soup('<p class="body" id="p1">It was a bright cold day.</p>')
        p = soup.find("p")
        result = self.emitter.emit([_block(p, "It was a bright cold day.", "Era un dia luminoso y frio.")], soup)

        ps = soup.find_all("p")
        self.assertEqual(len(ps), 2)
        en, es = ps[0], ps[1]
        # Spanish comes right after English...
        self.assertEqual(es["lang"], "es")
        self.assertIn("Era un dia", es.get_text())
        # Spanish carries the English paragraph class plus the marker class
        self.assertIn("es-tandem", es.get("class", []))
        # ...and the whole pair is enclosed in one break-inside:avoid container.
        wrapper = en.parent
        self.assertEqual(wrapper.name, "div")
        self.assertIn("keeptogether", wrapper.get("class", []))
        self.assertIn("break-inside:avoid", wrapper.get("style", ""))
        self.assertIs(es.parent, wrapper)  # EN and ES share the one wrapper
        # No fragile sibling break hints in wrap mode; margins keep the pair tight.
        self.assertNotIn("page-break", en.get("style", ""))
        self.assertIn("margin-bottom:0", en.get("style", ""))
        self.assertEqual(result.block_count, 1)

    def test_split_block_wraps_each_pair(self):
        soup = _soup('<p class="body">A. B. C. D.</p>')
        p = soup.find("p")
        blocks = [
            _block(p, "A. B.", "Ay. Bey.", sub_index=0, sub_count=2),
            _block(p, "C. D.", "Cey. Dey.", sub_index=1, sub_count=2),
        ]
        result = self.emitter.emit(blocks, soup)

        ps = soup.find_all("p")
        # 2 EN chunks + 2 ES chunks = 4 paragraphs
        self.assertEqual(len(ps), 4)
        langs = [p.get("lang") for p in ps]
        self.assertEqual(langs, [None, "es", None, "es"])
        # Two independent keeptogether wrappers, each holding exactly one EN+ES
        # pair (so a break may fall *between* pairs but never *within* one).
        wrappers = soup.find_all("div", class_="keeptogether")
        self.assertEqual(len(wrappers), 2)
        for w in wrappers:
            inner = w.find_all("p")
            self.assertEqual(len(inner), 2)
            self.assertIsNone(inner[0].get("lang"))
            self.assertEqual(inner[1].get("lang"), "es")
            self.assertIn("break-inside:avoid", w.get("style", ""))
        self.assertEqual(result.sub_split_count, 1)
        self.assertEqual(result.block_count, 2)

    def test_flat_mode_uses_sibling_break_css_no_wrapper(self):
        cfg = AlignerConfig(keep_together_mode="flat")
        emitter = InlineBilingualEmitter(cfg)
        soup = _soup('<p class="body">It was a bright cold day.</p>')
        p = soup.find("p")
        emitter.emit([_block(p, "It was a bright cold day.", "Era un dia.")], soup)
        ps = soup.find_all("p")
        en, es = ps[0], ps[1]
        self.assertIn("page-break-after:avoid", en.get("style", ""))
        self.assertIn("page-break-before:avoid", es.get("style", ""))
        # flat makes no structural change
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)

    def test_english_only_block_untouched(self):
        soup = _soup('<p>English with no translation.</p>')
        p = soup.find("p")
        result = self.emitter.emit([_block(p, "English with no translation.", "")], soup)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)  # no Spanish added
        self.assertIsNone(ps[0].get("style"))
        self.assertEqual(result.block_count, 0)

    def test_header_spanish_uses_same_tag(self):
        soup = _soup('<h2 class="chap">Chapter One</h2>')
        h = soup.find("h2")
        self.emitter.emit([_block(h, "Chapter One", "Capitulo Uno", kind="header")], soup)
        headers = soup.find_all("h2")
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers[1]["lang"], "es")
        self.assertIn("Capitulo Uno", headers[1].get_text())

    def test_keep_together_none_disables_css_and_wrapping(self):
        cfg = AlignerConfig(keep_together_mode="none")
        emitter = InlineBilingualEmitter(cfg)
        soup = _soup('<p>One sentence.</p>')
        p = soup.find("p")
        emitter.emit([_block(p, "One sentence.", "Una oracion.")], soup)
        for para in soup.find_all("p"):
            self.assertNotIn("page-break", para.get("style", "") or "")
        # none means no structural change either
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)

    def test_whitespace_only_spanish_emits_nothing(self):
        soup = _soup('<p>Hello world.</p>')
        p = soup.find("p")
        result = self.emitter.emit([_block(p, "Hello world.", "   \n  ")], soup)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)  # no empty Spanish <p>
        self.assertIsNone(ps[0].get("style"))  # no stranded keep-CSS
        self.assertEqual(result.block_count, 0)

    def test_dropcap_class_not_repeated_on_split_or_spanish(self):
        soup = _soup('<p class="dropcap first-para">A. B. C. D.</p>')
        p = soup.find("p")
        blocks = [
            _block(p, "A. B.", "Ay. Bey.", sub_index=0, sub_count=2),
            _block(p, "C. D.", "Cey. Dey.", sub_index=1, sub_count=2),
        ]
        self.emitter.emit(blocks, soup)
        ps = soup.find_all("p")
        # First EN chunk reuses the original node -> keeps drop-cap class.
        self.assertIn("dropcap", ps[0].get("class", []))
        # Every other paragraph (ES of first, EN chunk 2, ES of chunk 2) must NOT.
        for para in ps[1:]:
            self.assertNotIn("dropcap", para.get("class", []))
            self.assertNotIn("first-para", para.get("class", []))

    def test_orphan_extra_matches_translation_style(self):
        # An ES orphan attached as an "extra" must look like a normal grey
        # translation, not a smaller broken fragment: same tag, the EN node's
        # structural class, es-tandem, plus an invisible es-nota marker.
        soup = _soup('<p class="indent">She spoke.</p>')
        p = soup.find("p")
        block = _block(p, "She spoke.", "Ella habló.")
        block.es_extras = [StreamEvent(kind="paragraph", text="—Hola.", source={"node": object()})]
        self.emitter.emit([block], soup)

        notes = [t for t in soup.find_all("p") if "es-nota" in (t.get("class") or [])]
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(note["lang"], "es")
        self.assertIn("es-tandem", note.get("class"))
        self.assertIn("indent", note.get("class"))  # structural class copied
        self.assertIn("—Hola.", note.get_text())

    def test_css_makes_translations_grey_without_shrinking_notes(self):
        soup = _soup("<p>Hi.</p>")
        self.emitter.install_stylesheet(soup)
        css = soup.find("style").string
        # Main translations are grey...
        self.assertIn(".es-tandem { color: #555; }", css)
        # ...and notes are not singled out with a smaller font any more.
        self.assertNotIn("es-nota", css)

    def test_stylesheet_installed_once(self):
        soup = _soup('<p>Hi.</p>')
        self.emitter.install_stylesheet(soup)
        self.emitter.install_stylesheet(soup)
        styles = soup.find_all("style")
        self.assertEqual(len(styles), 1)
        self.assertIn("es-tandem", styles[0].string)

    def test_stylesheet_has_guarded_column_break_fallback(self):
        # The wrap-mode container fallback for multicolumn-paginating readers must
        # be @supports-guarded in the sheet (NOT inline alongside page-break-inside,
        # which makes some WebKit readers drop both — standardebooks/tools#101).
        soup = _soup("<p>Hi.</p>")
        self.emitter.install_stylesheet(soup)
        css = soup.find("style").string
        self.assertIn("@supports", css)
        self.assertIn(".keeptogether", css)
        self.assertIn("-webkit-column-break-inside: avoid", css)


class TestWrapPairsHelper(unittest.TestCase):
    """Direct coverage of the module-level wrap_pairs() (also reused by the
    flat->wrap EPUB post-processor)."""

    def test_english_only_paragraphs_not_wrapped(self):
        soup = _soup('<p>Solo English.</p><p>More English.</p>')
        self.assertEqual(wrap_pairs(soup), 0)
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)

    def test_groups_en_with_all_following_es_siblings(self):
        soup = _soup(
            '<p>EN.</p>'
            '<p lang="es" class="es-tandem">ES principal.</p>'
            '<p lang="es" class="es-tandem es-nota">ES nota.</p>'
            '<p>EN2 only.</p>'
        )
        self.assertEqual(wrap_pairs(soup), 1)
        wrappers = soup.find_all("div", class_="keeptogether")
        self.assertEqual(len(wrappers), 1)
        inner = wrappers[0].find_all("p")
        self.assertEqual(len(inner), 3)  # EN + ES + nota kept together
        # The trailing English-only paragraph stays outside the wrapper.
        self.assertNotIn("EN2", wrappers[0].get_text())

    def test_wraps_pairs_nested_inside_container_div(self):
        # Mirrors the real EPUB: pairs live inside a chapter <div>, not body.
        soup = _soup(
            '<div class="chap">'
            '<p class="chapter-number">42</p>'
            '<p>EN.</p><p lang="es" class="es-tandem">ES.</p>'
            '</div>'
        )
        self.assertEqual(wrap_pairs(soup), 1)
        # chapter-number (no es sibling) is untouched; the EN/ES pair is wrapped.
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 1)
        self.assertNotIn("42", soup.find("div", class_="keeptogether").get_text())

    def test_idempotent(self):
        soup = _soup('<p>EN.</p><p lang="es" class="es-tandem">ES.</p>')
        self.assertEqual(wrap_pairs(soup), 1)
        self.assertEqual(wrap_pairs(soup), 0)  # already wrapped, no double-nesting
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 1)

    def test_heading_pair_is_wrapped(self):
        # A <div> is valid content of <body>/<section>/<div>, so heading pairs
        # are wrapped just like paragraphs.
        soup = _soup('<h2>Title</h2><h2 lang="es" class="es-tandem">Titulo</h2>')
        self.assertEqual(wrap_pairs(soup), 1)
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 1)

    def test_list_items_fall_back_to_flat_not_wrapped(self):
        # A <div> is NOT valid content of <ul>/<ol>, so a list-item pair must not
        # be wrapped (that would emit invalid <ul><div><li>…); it gets the
        # per-element break-avoid hints instead.
        soup = _soup(
            '<ul><li>EN item</li>'
            '<li lang="es" class="es-tandem">Elemento ES</li></ul>'
        )
        kept = wrap_pairs(soup)
        self.assertEqual(kept, 1)
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)
        self.assertIsNone(soup.find("ul").find("div"))  # no div inside the list
        lis = soup.find_all("li")
        self.assertIn("break-after:avoid", lis[0].get("style", ""))
        self.assertIn("break-before:avoid", lis[1].get("style", ""))

    def test_list_item_fallback_is_idempotent(self):
        soup = _soup('<ul><li>EN</li><li lang="es" class="es-tandem">ES</li></ul>')
        self.assertEqual(wrap_pairs(soup), 1)  # first pass adds the hints
        self.assertEqual(wrap_pairs(soup), 0)  # second pass: nothing new
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)

    def test_strip_flat_removes_break_hints_keeps_margins(self):
        soup = _soup(
            '<p style="page-break-after:avoid;break-after:avoid;margin-bottom:0">EN.</p>'
            '<p lang="es" class="es-tandem" '
            'style="page-break-before:avoid;break-before:avoid;margin-top:0">ES.</p>'
        )
        wrap_pairs(soup, strip_flat=True)
        en, es = soup.find_all("p")
        self.assertNotIn("break", en.get("style", ""))
        self.assertIn("margin-bottom:0", en.get("style", ""))
        self.assertNotIn("break", es.get("style", ""))
        self.assertIn("margin-top:0", es.get("style", ""))


class TestMergeMode(unittest.TestCase):
    """`keep_together_mode="merge"` folds each EN/ES pair into ONE block element
    (EN text + <br/> + <span class="es-tandem"> ES), so readers with no CSS break
    support (Boox NeoReader, Moon+ Reader) cannot split the pair across a page."""

    def setUp(self):
        self.cfg = AlignerConfig(keep_together_mode="merge")
        self.emitter = InlineBilingualEmitter(self.cfg)

    def test_single_pair_becomes_one_block_with_inline_span(self):
        soup = _soup('<p class="body" id="p1">It was a bright cold day.</p>')
        p = soup.find("p")
        result = self.emitter.emit(
            [_block(p, "It was a bright cold day.", "Era un dia luminoso.")], soup
        )
        ps = soup.find_all("p")
        # ONE block only: no separate ES <p>, no wrapper <div>.
        self.assertEqual(len(ps), 1)
        block = ps[0]
        self.assertEqual(block.get("id"), "p1")  # original node reused
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)
        # ES is an inline grey span after a <br/>, inside the one block.
        self.assertIsNotNone(block.find("br"))
        span = block.find("span")
        self.assertIsNotNone(span)
        self.assertEqual(span.get("lang"), "es")
        self.assertIn("es-tandem", span.get("class", []))
        self.assertIn("Era un dia", span.get_text())
        self.assertIn("bright cold day", block.get_text())
        # The single block IS the keep-together unit: break-inside:avoid (so
        # Calibre/Kindle push the whole pair to the next page) + keeptogether
        # class (so the @supports column-break fallback reaches it).
        self.assertIn("break-inside:avoid", block.get("style", ""))
        self.assertIn("keeptogether", block.get("class", []))
        self.assertIn("body", block.get("class", []))  # original class preserved
        self.assertEqual(result.block_count, 1)

    def test_split_block_merges_each_chunk_into_its_own_block(self):
        soup = _soup('<p class="body">A. B. C. D.</p>')
        p = soup.find("p")
        blocks = [
            _block(p, "A. B.", "Ay. Bey.", sub_index=0, sub_count=2),
            _block(p, "C. D.", "Cey. Dey.", sub_index=1, sub_count=2),
        ]
        result = self.emitter.emit(blocks, soup)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 2)  # two merged blocks, no ES siblings
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)
        for blk in ps:
            self.assertIsNone(blk.get("lang"))  # the block itself stays English
            self.assertEqual(len(blk.find_all("span", class_="es-tandem")), 1)
            # each merged chunk is its own keep-together unit
            self.assertIn("break-inside:avoid", blk.get("style", ""))
            self.assertIn("keeptogether", blk.get("class", []))
        self.assertEqual(result.sub_split_count, 1)
        self.assertEqual(result.block_count, 2)

    def test_header_pair_merges_into_one_heading(self):
        soup = _soup('<h2 class="chap">Chapter One</h2>')
        h = soup.find("h2")
        self.emitter.emit([_block(h, "Chapter One", "Capitulo Uno", kind="header")], soup)
        h2s = soup.find_all("h2")
        self.assertEqual(len(h2s), 1)
        span = h2s[0].find("span", class_="es-tandem")
        self.assertIsNotNone(span)
        self.assertIn("Capitulo Uno", span.get_text())
        self.assertIn("keeptogether", h2s[0].get("class", []))
        self.assertIn("break-inside:avoid", h2s[0].get("style", ""))

    def test_english_only_block_untouched(self):
        soup = _soup('<p>English with no translation.</p>')
        p = soup.find("p")
        result = self.emitter.emit([_block(p, "English with no translation.", "")], soup)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)
        self.assertIsNone(ps[0].find("span"))  # no translation folded in
        self.assertIsNone(ps[0].get("style"))
        self.assertEqual(result.block_count, 0)

    def test_orphan_extra_merged_as_extra_span(self):
        soup = _soup('<p class="indent">She spoke.</p>')
        p = soup.find("p")
        block = _block(p, "She spoke.", "Ella habló.")
        block.es_extras = [
            StreamEvent(kind="paragraph", text="—Hola.", source={"node": object()})
        ]
        self.emitter.emit([block], soup)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)
        spans = ps[0].find_all("span", class_="es-tandem")
        self.assertEqual(len(spans), 2)  # main translation + orphan note, both inline
        notes = [s for s in spans if "es-nota" in (s.get("class") or [])]
        self.assertEqual(len(notes), 1)
        self.assertIn("—Hola.", notes[0].get_text())


class TestMergePairsHelper(unittest.TestCase):
    """Direct coverage of the module-level merge_pairs(), also reused by the
    post-hoc EPUB converter (`scripts/wrap_keep_together.py --mode merge`)."""

    def test_merges_plain_sibling_pair(self):
        soup = _soup('<p>EN.</p><p lang="es" class="es-tandem">ES.</p>')
        self.assertEqual(merge_pairs(soup), 1)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)
        self.assertIsNotNone(ps[0].find("br"))
        self.assertEqual(ps[0].find("span", class_="es-tandem").get_text(), "ES.")

    def test_english_only_not_merged(self):
        soup = _soup('<p>Solo.</p><p>More.</p>')
        self.assertEqual(merge_pairs(soup), 0)
        self.assertEqual(len(soup.find_all("p")), 2)

    def test_groups_main_translation_and_note(self):
        soup = _soup(
            '<p>EN.</p>'
            '<p lang="es" class="es-tandem">ES principal.</p>'
            '<p lang="es" class="es-tandem es-nota">ES nota.</p>'
            '<p>EN2 only.</p>'
        )
        self.assertEqual(merge_pairs(soup), 1)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 2)  # merged block + the EN2-only paragraph
        spans = ps[0].find_all("span", class_="es-tandem")
        self.assertEqual(len(spans), 2)
        self.assertIn("es-nota", spans[1].get("class"))
        self.assertNotIn("EN2", ps[0].get_text())

    def test_list_item_pair_merges_into_valid_markup(self):
        # The case wrap_pairs has to punt on (a <div> is invalid in <ul>): merge
        # folds it into one <li>, valid markup, no div. break-inside goes on the
        # <li> itself.
        soup = _soup(
            '<ul><li>EN item</li>'
            '<li lang="es" class="es-tandem">Elemento ES</li></ul>'
        )
        self.assertEqual(merge_pairs(soup), 1)
        lis = soup.find_all("li")
        self.assertEqual(len(lis), 1)
        self.assertIsNone(soup.find("ul").find("div"))
        self.assertEqual(lis[0].find("span", class_="es-tandem").get_text(), "Elemento ES")
        self.assertIn("break-inside:avoid", lis[0].get("style", ""))

    def test_unwraps_keeptogether_div_from_wrap_epub(self):
        # Post-hoc wrap -> merge: the leftover one-child wrapper <div> is removed
        # and the break hint migrates onto the merged block; the redundant pair-
        # tightening margin is stripped.
        soup = _soup(
            '<div class="keeptogether" '
            'style="page-break-inside:avoid;break-inside:avoid">'
            '<p style="margin-bottom:0">EN.</p>'
            '<p lang="es" class="es-tandem" style="margin-top:0">ES.</p>'
            '</div>'
        )
        self.assertEqual(merge_pairs(soup), 1)
        self.assertEqual(len(soup.find_all("div", class_="keeptogether")), 0)
        ps = soup.find_all("p")
        self.assertEqual(len(ps), 1)
        self.assertIn("keeptogether", ps[0].get("class", []))
        self.assertIn("break-inside:avoid", ps[0].get("style", ""))
        self.assertNotIn("margin-bottom:0", ps[0].get("style", ""))  # tightening stripped
        self.assertEqual(ps[0].find("span", class_="es-tandem").get_text(), "ES.")

    def test_strips_flat_break_hints_and_carries_break_inside(self):
        # Post-hoc flat -> merge: the per-element flat break hints are dropped and
        # replaced by a single break-inside:avoid on the merged block.
        soup = _soup(
            '<p style="page-break-after:avoid;break-after:avoid;margin-bottom:0">EN.</p>'
            '<p lang="es" class="es-tandem" '
            'style="page-break-before:avoid;break-before:avoid">ES.</p>'
        )
        merge_pairs(soup)
        en = soup.find("p")
        style = en.get("style", "")
        self.assertNotIn("break-after", style)   # stale flat hint removed
        self.assertNotIn("margin-bottom:0", style)
        self.assertIn("break-inside:avoid", style)  # keep-together hint added

    def test_idempotent(self):
        soup = _soup('<p>EN.</p><p lang="es" class="es-tandem">ES.</p>')
        self.assertEqual(merge_pairs(soup), 1)
        self.assertEqual(merge_pairs(soup), 0)  # ES is now an inline span, no pairs left
        self.assertEqual(len(soup.find_all("p")), 1)


class TestSplitContinuationMarker(unittest.TestCase):
    """A long paragraph split into N pairs marks every English chunk EXCEPT the
    last with a trailing ⁂ (U+2042), so the reader sees the paragraph continues.
    English side only; never on a single unsplit pair or the final chunk."""

    MARK = "⁂"

    def _split_blocks(self, p):
        return [
            _block(p, "S1.", "E1.", sub_index=0, sub_count=3),
            _block(p, "S2.", "E2.", sub_index=1, sub_count=3),
            _block(p, "S3.", "E3.", sub_index=2, sub_count=3),
        ]

    def _emit_split(self, mode, **cfg_kw):
        cfg = AlignerConfig(keep_together_mode=mode, **cfg_kw)
        emitter = InlineBilingualEmitter(cfg)
        soup = _soup('<p class="body">S1. S2. S3.</p>')
        emitter.emit(self._split_blocks(soup.find("p")), soup)
        return soup

    def test_marker_on_non_final_english_chunks_only(self):
        # wrap keeps EN and ES as separate <p>, so EN chunks are easy to isolate.
        soup = self._emit_split("wrap")
        en = [p for p in soup.find_all("p") if p.get("lang") != "es"]
        self.assertEqual(len(en), 3)
        self.assertTrue(en[0].get_text().rstrip().endswith(self.MARK))
        self.assertTrue(en[1].get_text().rstrip().endswith(self.MARK))
        self.assertNotIn(self.MARK, en[2].get_text())  # final chunk: no marker

    def test_spanish_never_marked(self):
        soup = self._emit_split("wrap")
        es = [p for p in soup.find_all("p") if p.get("lang") == "es"]
        self.assertEqual(len(es), 3)
        for p in es:
            self.assertNotIn(self.MARK, p.get_text())

    def test_single_unsplit_pair_has_no_marker(self):
        cfg = AlignerConfig(keep_together_mode="wrap")
        emitter = InlineBilingualEmitter(cfg)
        soup = _soup('<p class="body">Just one.</p>')
        emitter.emit([_block(soup.find("p"), "Just one.", "Solo una.")], soup)
        for p in soup.find_all("p"):
            self.assertNotIn(self.MARK, p.get_text())

    def test_merge_mode_keeps_marker_on_english_side(self):
        soup = self._emit_split("merge")
        blocks = soup.find_all("p")
        self.assertEqual(len(blocks), 3)  # three merged single blocks
        self.assertIn(self.MARK, blocks[0].get_text())
        self.assertIn(self.MARK, blocks[1].get_text())
        self.assertNotIn(self.MARK, blocks[2].get_text())  # final chunk
        for blk in blocks:
            span = blk.find("span", class_="es-tandem")
            self.assertIsNotNone(span)
            self.assertNotIn(self.MARK, span.get_text())  # marker is English-side

    def test_flag_off_disables_marker(self):
        soup = self._emit_split("wrap", split_continuation_marker=False)
        for p in soup.find_all("p"):
            self.assertNotIn(self.MARK, p.get_text())


if __name__ == "__main__":
    unittest.main()
