import os
import sys
import unittest

from bs4 import BeautifulSoup

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aligner.block_builder import Block
from aligner.config import AlignerConfig
from aligner.inline_emitter import InlineBilingualEmitter
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
        self.cfg = AlignerConfig()  # output_mode=inline, keep_together_mode=flat
        self.emitter = InlineBilingualEmitter(self.cfg)

    def test_single_block_inserts_spanish_after_english(self):
        soup = _soup('<p class="body" id="p1">It was a bright cold day.</p>')
        p = soup.find("p")
        result = self.emitter.emit([_block(p, "It was a bright cold day.", "Era un dia luminoso y frio.")], soup)

        ps = soup.find_all("p")
        self.assertEqual(len(ps), 2)
        en, es = ps[0], ps[1]
        # Spanish comes right after English
        self.assertEqual(es["lang"], "es")
        self.assertIn("Era un dia", es.get_text())
        # keep-together CSS
        self.assertIn("page-break-after:avoid", en.get("style", ""))
        self.assertIn("page-break-before:avoid", es.get("style", ""))
        # Spanish carries the English paragraph class plus the marker class
        self.assertIn("es-tandem", es.get("class", []))
        self.assertEqual(result.block_count, 1)

    def test_split_block_emits_multiple_kept_together_pairs(self):
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
        # every EN has break-after:avoid, every ES has break-before:avoid
        for i, p in enumerate(ps):
            if i % 2 == 0:
                self.assertIn("page-break-after:avoid", p.get("style", ""))
            else:
                self.assertIn("page-break-before:avoid", p.get("style", ""))
        self.assertEqual(result.sub_split_count, 1)
        self.assertEqual(result.block_count, 2)

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

    def test_keep_together_none_disables_css(self):
        cfg = AlignerConfig(keep_together_mode="none")
        emitter = InlineBilingualEmitter(cfg)
        soup = _soup('<p>One sentence.</p>')
        p = soup.find("p")
        emitter.emit([_block(p, "One sentence.", "Una oracion.")], soup)
        for para in soup.find_all("p"):
            self.assertNotIn("page-break", para.get("style", "") or "")

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

    def test_stylesheet_installed_once(self):
        soup = _soup('<p>Hi.</p>')
        self.emitter.install_stylesheet(soup)
        self.emitter.install_stylesheet(soup)
        styles = soup.find_all("style")
        self.assertEqual(len(styles), 1)
        self.assertIn("es-tandem", styles[0].string)


if __name__ == "__main__":
    unittest.main()
