import os
import sys
import unittest

import numpy as np

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aligner.block_builder import BlockBuilder
from aligner.config import AlignerConfig
from aligner.paragraph_aligner import AlignedPair
from aligner.reading_stream import StreamEvent


class _FakeAligner:
    """Deterministic stand-in so tests don't load LaBSE."""

    def encode(self, texts):
        return np.array([[float(len(t) % 7 + 1), 1.0, 2.0] for t in texts])


def _words(text):
    return len(text.split())


def _pair(en_text, es_text):
    en_ev = StreamEvent(kind="paragraph", text=en_text, source={"node": object()})
    es_ev = StreamEvent(kind="paragraph", text=es_text, source={"node": object()})
    return AlignedPair(
        en_indices=(0,), es_indices=(0,), confidence=0.9, transition="1:1",
        is_anchor=True, en_events=(en_ev,), es_events=(es_ev,),
    )


class TestWordBudgetSplit(unittest.TestCase):
    def setUp(self):
        # This class exercises the word-budget splitting path, so enable it
        # explicitly (splitting is off by default — see test_defaults).
        self.cfg = AlignerConfig(word_budget_split=True)
        self.bb = BlockBuilder(self.cfg, _FakeAligner())

    def test_defaults(self):
        defaults = AlignerConfig()
        # Splitting is off by default: each paragraph stays a whole EN+ES pair.
        self.assertFalse(defaults.word_budget_split)
        self.assertEqual(defaults.target_chunk_words, 25)
        self.assertEqual(defaults.output_mode, "inline")
        self.assertEqual(defaults.keep_together_mode, "wrap")

    def test_group_by_word_budget_targets_size_without_losing_sentences(self):
        sents = [f"This is sentence number {i} with some filler words here." for i in range(6)]
        groups = self.bb._group_sentences_by_word_budget(sents)
        self.assertEqual(sum(len(g) for g in groups), 6)
        self.assertTrue(all(g for g in groups))
        # ~10-word sentences, target 25, overshoot 35 -> 3 per chunk
        for g in groups:
            self.assertLessEqual(sum(_words(s) for s in g), int(25 * 1.4) + 12)

    def test_single_long_sentence_is_never_split(self):
        text = ("word " * 120).strip()  # 120 words, one sentence
        ev = StreamEvent(kind="paragraph", text=text, source={"node": object()})
        self.assertFalse(self.bb._should_split(ev, text))

    def test_short_paragraph_not_split(self):
        text = "Just a short one. Two sentences only."
        ev = StreamEvent(kind="paragraph", text=text, source={"node": object()})
        self.assertFalse(self.bb._should_split(ev, text))

    def test_long_multi_sentence_splits_and_distributes_es(self):
        en = " ".join(f"English sentence {i} carries roughly ten words of content here." for i in range(8))
        es = " ".join(f"Oracion espanola numero {i} con texto de relleno aqui." for i in range(8))
        blocks = self.bb.build([_pair(en, es)])
        self.assertGreater(len(blocks), 1)
        # consistent sub_count, contiguous indices
        self.assertTrue(all(b.sub_count == len(blocks) for b in blocks))
        self.assertEqual([b.sub_index for b in blocks], list(range(len(blocks))))
        # offsets locate each sub-block start within the EN text
        for b in blocks:
            window = en[b.sub_text_offset:b.sub_text_offset + b.sub_text_length]
            self.assertIn(b.en_text.split()[0], window)
        # every EN word is preserved across sub-blocks
        self.assertEqual(
            sum(_words(b.en_text) for b in blocks), _words(en)
        )

    def test_split_disabled_keeps_paragraph_whole(self):
        cfg = AlignerConfig(word_budget_split=False)
        bb = BlockBuilder(cfg, _FakeAligner())
        en = " ".join(f"Sentence number {i} has enough words to matter here today." for i in range(10))
        es = " ".join(f"Oracion {i} con relleno." for i in range(10))
        blocks = bb.build([_pair(en, es)])
        # Splitting disabled -> the whole paragraph stays a single block/pair,
        # never broken in the middle.
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].en_text, en)


if __name__ == "__main__":
    unittest.main()
