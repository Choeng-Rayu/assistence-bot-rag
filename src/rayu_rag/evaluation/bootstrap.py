"""Percentile bootstrap confidence intervals.

Owner: Tanchhay.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

__all__ = ["bootstrap_ci"]


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

    TODO(Tanchhay): implement the percentile bootstrap.
    """

    raise NotImplementedError("TODO(Tanchhay): implement bootstrap_ci")
