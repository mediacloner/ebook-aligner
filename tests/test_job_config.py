import os
import sys
import unittest

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aligner.bridge import _resolve_job_config
from aligner.config import AlignerConfig


class TestResolveJobConfig(unittest.TestCase):
    def setUp(self):
        self.base = AlignerConfig(
            output_mode="inline", target_chunk_words=25,
            keep_together_mode="flat", word_budget_split=True,
        )

    def test_overrides_applied_without_mutating_base(self):
        job = _resolve_job_config(
            self.base,
            {"output_mode": "footnote", "target_chunk_words": 80,
             "keep_together_mode": "none", "word_budget_split": False},
        )
        self.assertEqual(job.output_mode, "footnote")
        self.assertEqual(job.target_chunk_words, 80)
        self.assertEqual(job.keep_together_mode, "none")
        self.assertFalse(job.word_budget_split)
        # base (the shared singleton's config) is untouched
        self.assertEqual(self.base.output_mode, "inline")
        self.assertEqual(self.base.target_chunk_words, 25)
        self.assertEqual(self.base.keep_together_mode, "flat")
        self.assertTrue(self.base.word_budget_split)
        self.assertIsNot(job, self.base)

    def test_absent_keys_fall_back_to_baseline_not_prior_job(self):
        # A prior job set footnote; this job omits outputMode entirely.
        job = _resolve_job_config(self.base, {})
        # Falls back to the baseline (inline), NOT to any previous mutation.
        self.assertEqual(job.output_mode, "inline")
        self.assertEqual(job.target_chunk_words, 25)

    def test_wrap_is_an_accepted_override(self):
        job = _resolve_job_config(self.base, {"keep_together_mode": "wrap"})
        self.assertEqual(job.keep_together_mode, "wrap")

    def test_merge_is_an_accepted_override(self):
        job = _resolve_job_config(self.base, {"keep_together_mode": "merge"})
        self.assertEqual(job.keep_together_mode, "merge")

    def test_invalid_values_ignored(self):
        job = _resolve_job_config(
            self.base, {"output_mode": "bogus", "target_chunk_words": -3,
                        "keep_together_mode": "wat"},
        )
        self.assertEqual(job.output_mode, "inline")
        self.assertEqual(job.target_chunk_words, 25)
        self.assertEqual(job.keep_together_mode, "flat")


class TestEnvValidation(unittest.TestCase):
    def test_bogus_output_mode_env_falls_back_to_default(self):
        prev = dict(os.environ)
        try:
            os.environ["ALIGNER_OUTPUT_MODE"] = "bogus"
            os.environ["ALIGNER_KEEP_TOGETHER"] = "nope"
            cfg = AlignerConfig.from_env()
            self.assertEqual(cfg.output_mode, "inline")
            self.assertEqual(cfg.keep_together_mode, "wrap")
        finally:
            os.environ.clear()
            os.environ.update(prev)

    def test_merge_env_is_accepted(self):
        prev = dict(os.environ)
        try:
            os.environ["ALIGNER_KEEP_TOGETHER"] = "merge"
            cfg = AlignerConfig.from_env()
            self.assertEqual(cfg.keep_together_mode, "merge")
        finally:
            os.environ.clear()
            os.environ.update(prev)


class TestDotenvParsing(unittest.TestCase):
    """`_load_dotenv` must strip inline comments, or a line like
    `ALIGNER_KEEP_TOGETHER=merge  # note` stores the comment as part of the value
    and silently falls back to the default mode."""

    def test_inline_comment_stripped_but_hash_in_value_preserved(self):
        import tempfile
        from pathlib import Path
        from aligner.config import _load_dotenv

        prev = dict(os.environ)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text(
                "ALIGNER_KEEP_TOGETHER=merge        # merge = one block; wrap/flat/none\n"
                'QUOTED_VAL="value with # hash"   # trailing comment\n'
                "COLOR_VAL=#555\n"
                "PLAIN=gpt-5.5\n",
                encoding="utf-8",
            )
            for k in ("ALIGNER_KEEP_TOGETHER", "QUOTED_VAL", "COLOR_VAL", "PLAIN"):
                os.environ.pop(k, None)
            try:
                _load_dotenv(p)
                # Inline comment after whitespace is dropped...
                self.assertEqual(os.environ["ALIGNER_KEEP_TOGETHER"], "merge")
                # ...quoted values keep an interior '#'...
                self.assertEqual(os.environ["QUOTED_VAL"], "value with # hash")
                # ...a value that is itself a '#...' token is preserved...
                self.assertEqual(os.environ["COLOR_VAL"], "#555")
                # ...and a plain value is unchanged.
                self.assertEqual(os.environ["PLAIN"], "gpt-5.5")
            finally:
                os.environ.clear()
                os.environ.update(prev)


if __name__ == "__main__":
    unittest.main()
