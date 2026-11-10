"""Runtime configuration for the RayuCode RAG assistant.

All values have safe defaults so the scaffold runs offline. Secrets are read
from the environment only; they are never written to disk.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_TRUTHY = {"1", "true", "yes", "on"}


def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _env_optional(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return None
    return value.strip()


def _env_bool(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def _env_float_optional(name: str) -> float | None:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return None
    return float(value)


@dataclass(frozen=True, slots=True)
class Config:
    """Frozen configuration shared by every runtime component."""

    docs_dir: Path = Path("data/docs")
    artifacts_dir: Path = Path("artifacts")
    corpus_dir: Path = Path("artifacts/corpus")
    index_dir: Path = Path("artifacts/index")

    gateway_url: str = "https://gateway.rayucode.com"
    bot_api_key: str | None = None
    model: str = "deepseek-v4.1-flash-cloud"
    llm_mode: str = "mock"

    ranker: str = "keyword"
    top_k: int = 5
    budget_chars: int = 6000
    refusal_threshold: float | None = None

    max_turns: int = 12
    max_turn_chars: int = 2000
    max_total_chars: int = 8000
    retrieval_user_turns: int = 2
    retrieval_max_chars: int = 600
    max_sources: int = 4

    docs_site_base: str = "https://rayucode.com"
    debug: bool = False

    ip_window_limit: int = 6
    ip_window_minutes: int = 10
    ip_daily_limit: int = 50
    global_daily_limit: int = 500

    @classmethod
    def from_env(cls) -> "Config":
        """Build a configuration from environment variables.

        Recognised variables: ``RAYU_BOT_GATEWAY_URL``, ``RAYU_BOT_API_KEY``,
        ``RAYU_BOT_MODEL``, ``RAYU_RAG_LLM``, ``RAYU_RAG_RANKER``,
        ``RAYU_RAG_DEBUG``, ``RAYU_RAG_REFUSAL_THRESHOLD`` and
        ``RAYU_DOCS_SITE_BASE``.
        """

        bot_api_key = _env_optional("RAYU_BOT_API_KEY")
        explicit_mode = _env_optional("RAYU_RAG_LLM")
        if explicit_mode is not None:
            llm_mode = explicit_mode.lower()
        else:
            llm_mode = "gateway" if bot_api_key else "mock"

        return cls(
            gateway_url=_env_str("RAYU_BOT_GATEWAY_URL", "https://gateway.rayucode.com"),
            bot_api_key=bot_api_key,
            model=_env_str("RAYU_BOT_MODEL", "deepseek-v4.1-flash-cloud"),
            llm_mode=llm_mode,
            ranker=_env_str("RAYU_RAG_RANKER", "keyword"),
            refusal_threshold=_env_float_optional("RAYU_RAG_REFUSAL_THRESHOLD"),
            docs_site_base=_env_str("RAYU_DOCS_SITE_BASE", "https://rayucode.com"),
            debug=_env_bool("RAYU_RAG_DEBUG"),
        )
