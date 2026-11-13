"""Percentile bootstrap confidence intervals.

Owner: Tanchhay.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

__all__ = ["bootstrap_ci"]


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float] | None = None,
    n: int = 1000,
    alpha: float = 0.05,
    seed: int = 13,
) -> tuple[float, float]:
    """Return a ``(low, high)`` percentile bootstrap CI for *statistic*.

    Resample *values* with replacement *n* times using a seeded RNG; the default
    statistic is the mean. The paired bootstrap for ``candidate - baseline``
    reuses this helper with pre-paired differences.
    """

    if not values:
        return (0.0, 0.0)
    stat = statistic or _mean
    rng = random.Random(seed)
    size = len(values)
    estimates = sorted(stat([values[rng.randrange(size)] for _ in range(size)]) for _ in range(n))
    low = estimates[int((alpha / 2) * n)]
    high = estimates[min(n - 1, int((1 - alpha / 2) * n))]
    return (low, high)
