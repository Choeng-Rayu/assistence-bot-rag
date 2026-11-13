"""Retrieval metrics.

Owner: Tanchhay.

Binary relevance is ``grade >= 2`` for P/R/F1/MRR/MAP. Graded NDCG uses gains
``2**grade - 1``. Recall is reported as pool-relative (relevant ids come from the
pooled judgements).
"""

from __future__ import annotations

import math
from collections.abc import Collection, Mapping, Sequence

__all__ = [
    "average_precision",
    "dcg_at_k",
    "f1_at_k",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
]


def precision_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    """Fraction of the top *k* retrieved ids that are relevant."""

    if k <= 0:
        return 0.0
    return sum(1 for item in retrieved[:k] if item in relevant) / k


def recall_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    """Fraction of relevant ids found in the top *k* (pool-relative)."""

    if not relevant:
        return 0.0
    return len({item for item in retrieved[:k] if item in relevant}) / len(relevant)


def f1_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    """Harmonic mean of precision@k and recall@k."""

    precision = precision_at_k(retrieved, relevant, k)
    recall = recall_at_k(retrieved, relevant, k)
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def reciprocal_rank(
    retrieved: Sequence[str],
    relevant: Collection[str],
    k: int = 10,
) -> float:
    """``1 / rank`` of the first relevant id within the top *k*, else ``0``."""

    for position, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            return 1.0 / position
    return 0.0


def average_precision(
    retrieved: Sequence[str],
    relevant: Collection[str],
    k: int | None = None,
) -> float:
    """Mean of precision values at every relevant hit, divided by ``|relevant|``."""

    if not relevant:
        return 0.0
    hits = 0
    total = 0.0
    for position, item in enumerate(retrieved if k is None else retrieved[:k], start=1):
        if item in relevant:
            hits += 1
            total += hits / position
    return total / len(relevant)


def dcg_at_k(grades_in_rank_order: Sequence[int], k: int) -> float:
    """Discounted cumulative gain with gain ``2**grade - 1`` and ``log2`` discount."""

    return sum(
        (2**grade - 1) / math.log2(position + 1)
        for position, grade in enumerate(grades_in_rank_order[:k], start=1)
    )


def ndcg_at_k(
    retrieved: Sequence[str],
    grades: Mapping[str, int],
    k: int,
) -> float:
    """DCG@k of *retrieved* divided by the ideal DCG@k over *grades*."""

    ideal = dcg_at_k(sorted(grades.values(), reverse=True), k)
    if ideal == 0.0:
        return 0.0
    actual = dcg_at_k([grades.get(item, 0) for item in retrieved[:k]], k)
    return actual / ideal
