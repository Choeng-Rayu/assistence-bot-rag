"""The evaluation harness entry point.

Owner: Tanchhay.
"""

from __future__ import annotations

from pathlib import Path

from ..config import Config

__all__ = ["evaluate"]


def evaluate(
    *,
    queries_path: Path | None = None,
    qrels_path: Path | None = None,
    ranker: str = "keyword",
    split: str = "dev",
    bootstrap: int = 1000,
    config: Config | None = None,
    out_dir: Path | None = None,
    **kwargs: object,
) -> dict:
    """Score *ranker* on the requested *split* and return a report dict.

    Loads queries/qrels, runs retrieval per query, computes P@1, P@5, R@5,
    MRR@10, MAP, NDCG@5 and NDCG@10 with bootstrap CIs (1000 resamples, seed
    13), and returns per-query rows plus aggregates. *split* is ``dev``,
    ``test`` or ``all``.

    TODO(Tanchhay): implement the evaluation harness.
    """

    raise NotImplementedError("TODO(Tanchhay): implement evaluate")
