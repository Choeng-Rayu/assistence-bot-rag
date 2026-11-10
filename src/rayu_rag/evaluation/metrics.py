"""Retrieval metrics.

Owner: Tanchhay.

Binary relevance is ``grade >= 2`` for P/R/F1/MRR/MAP. Graded NDCG uses gains
``2**grade - 1``. Recall is reported as pool-relative (relevant ids come from the
pooled judgements).
"""

from __future__ import annotations

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
    """Fraction of the top *k* retrieved ids that are relevant.

    TODO(Tanchhay): implement precision@k.
    """

    raise NotImplementedError("TODO(Tanchhay): implement precision_at_k")


def recall_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    """Fraction of relevant ids found in the top *k* (pool-relative).

    TODO(Tanchhay): implement recall@k.
    """

    raise NotImplementedError("TODO(Tanchhay): implement recall_at_k")


def f1_at_k(retrieved: Sequence[str], relevant: Collection[str], k: int) -> float:
    """Harmonic mean of precision@k and recall@k.

    TODO(Tanchhay): implement F1@k.
    """

    raise NotImplementedError("TODO(Tanchhay): implement f1_at_k")


def reciprocal_rank(
    retrieved: Sequence[str],
    relevant: Collection[str],
    k: int = 10,
) -> float:
    """``1 / rank`` of the first relevant id within the top *k*, else ``0``.

    TODO(Tanchhay): implement reciprocal rank.
    """

    raise NotImplementedError("TODO(Tanchhay): implement reciprocal_rank")


def average_precision(
    retrieved: Sequence[str],
    relevant: Collection[str],
    k: int | None = None,
) -> float:
    """Mean of precision values at every relevant hit, divided by ``|relevant|``.

    TODO(Tanchhay): implement average precision.
    """

    raise NotImplementedError("TODO(Tanchhay): implement average_precision")


def dcg_at_k(grades_in_rank_order: Sequence[int], k: int) -> float:
    """Discounted cumulative gain with gain ``2**grade - 1`` and ``log2`` discount.

    TODO(Tanchhay): implement DCG@k.
    """

    raise NotImplementedError("TODO(Tanchhay): implement dcg_at_k")


def ndcg_at_k(
    retrieved: Sequence[str],
    grades: Mapping[str, int],
    k: int,
) -> float:
    """DCG@k of *retrieved* divided by the ideal DCG@k over *grades*.

    TODO(Tanchhay): implement NDCG@k.
    """

    raise NotImplementedError("TODO(Tanchhay): implement ndcg_at_k")
