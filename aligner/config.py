import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env_int(env, key: str, default: int) -> int:
    raw = env.get(key)
    if raw is None or not str(raw).strip():
        return default
    try:
        value = int(str(raw).strip())
    except ValueError:
        return default
    return value if value > 0 else default


_REPO_ROOT = Path(__file__).resolve().parent.parent
_load_dotenv(_REPO_ROOT / ".env")


@dataclass
class AlignerConfig:
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5.5"
    openai_fallback_model: str = "gpt-5.4"
    embedding_model: str = "sentence-transformers/LaBSE"

    max_sentences_per_block: int = 4
    long_paragraph_threshold: int = 280

    # Word-budget splitting (ported from bilingual-epub-splitter). When enabled,
    # long paragraphs are split into chunks of whole sentences targeting
    # ~target_chunk_words words each, instead of fixed max_sentences_per_block
    # windows. A single sentence longer than the target stands alone; sentences
    # are never broken mid-sentence. Splitting only kicks in once a paragraph
    # exceeds split_min_words words and has at least two sentences.
    word_budget_split: bool = True
    target_chunk_words: int = 25
    split_min_words: int = 70

    anchor_top_k: int = 5
    anchor_min_similarity: float = 0.55
    dp_max_span: int = 4
    length_ratio_alpha: float = 0.2

    adjudicator_enabled: bool = True
    adjudicator_confidence_threshold: float = 0.60
    adjudicator_max_calls_per_chapter: int = 30

    cache_dir: Path = field(default_factory=lambda: _REPO_ROOT / ".aligner_cache")
    onboarding_notice: str = (
        "Toca cualquier párrafo para ver la traducción al español. — "
        "Tap any paragraph to reveal its Spanish translation."
    )

    @classmethod
    def from_env(cls) -> "AlignerConfig":
        env = os.environ
        cache_dir_env = env.get("ALIGNER_CACHE_DIR")
        cache_dir = Path(cache_dir_env) if cache_dir_env else _REPO_ROOT / ".aligner_cache"
        defaults = cls()
        return cls(
            openai_api_key=env.get("OPENAI_API_KEY"),
            openai_model=env.get("OPENAI_ALIGNER_MODEL", "gpt-5.5"),
            openai_fallback_model=env.get("OPENAI_ALIGNER_FALLBACK_MODEL", "gpt-5.4"),
            adjudicator_enabled=env.get("ALIGNER_USE_LLM", "true").lower() == "true",
            word_budget_split=env.get(
                "ALIGNER_WORD_BUDGET_SPLIT", str(defaults.word_budget_split)
            ).lower() == "true",
            target_chunk_words=_env_int(
                env, "ALIGNER_TARGET_CHUNK_WORDS", defaults.target_chunk_words
            ),
            split_min_words=_env_int(
                env, "ALIGNER_SPLIT_MIN_WORDS", defaults.split_min_words
            ),
            cache_dir=cache_dir,
        )

    def ensure_cache_dir(self) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir

    def has_llm(self) -> bool:
        return self.adjudicator_enabled and bool(self.openai_api_key)
