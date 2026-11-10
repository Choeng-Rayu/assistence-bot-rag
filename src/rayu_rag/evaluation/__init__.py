"""Evaluation harness: metrics, bootstrap CIs, agreement, pooling, reports.

Owner: Tanchhay. Every metric/algorithm is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Tanchhay)`` message until P3/P4
land. ``RANKERS`` is implemented data.
"""

from __future__ import annotations

from . import answer_eval
from .agreement import cohens_kappa
from .bootstrap import bootstrap_ci
from .harness import evaluate
from .metrics import (
    average_precision,
    dcg_at_k,
    f1_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from .pool import build_pool
from .report import to_markdown

__all__ = [
    "answer_eval",
    "average_precision",
    "bootstrap_ci",
    "build_pool",
    "cohens_kappa",
    "dcg_at_k",
    "evaluate",
    "f1_at_k",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "to_markdown",
]
