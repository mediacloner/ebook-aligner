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
        return cls(
            openai_api_key=env.get("OPENAI_API_KEY"),
            openai_model=env.get("OPENAI_ALIGNER_MODEL", "gpt-5.5"),
            openai_fallback_model=env.get("OPENAI_ALIGNER_FALLBACK_MODEL", "gpt-5.4"),
            adjudicator_enabled=env.get("ALIGNER_USE_LLM", "true").lower() == "true",
            cache_dir=cache_dir,
        )

    def ensure_cache_dir(self) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir

    def has_llm(self) -> bool:
        return self.adjudicator_enabled and bool(self.openai_api_key)
