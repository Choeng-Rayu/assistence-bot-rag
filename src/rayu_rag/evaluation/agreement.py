"""Inter-annotator agreement.

Owner: Tanchhay.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

__all__ = ["cohens_kappa"]


def cohens_kappa(a: Sequence[int], b: Sequence[int]) -> float:
    """Return Cohen's kappa for two annotators' paired graded labels.

    ``kappa = (p_o - p_e) / (1 - p_e)``; ``1.0`` is perfect agreement and
    ``0.0`` is chance. If kappa falls below 0.5 the protocol says to fall back
    to binary relevance and report that.
    """

    if len(a) != len(b):
        raise ValueError("annotator label sequences must have equal length")
    if not a:
        raise ValueError("cannot compute kappa for empty label sequences")
    total = len(a)
    observed = sum(1 for x, y in zip(a, b) if x == y) / total
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(count_a[label] * count_b[label] for label in count_a) / (total * total)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)
