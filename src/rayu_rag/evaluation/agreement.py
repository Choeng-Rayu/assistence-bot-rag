"""Inter-annotator agreement.

Owner: Tanchhay.
"""

from __future__ import annotations

from collections.abc import Sequence

__all__ = ["cohens_kappa"]


def cohens_kappa(a: Sequence[int], b: Sequence[int]) -> float:
    """Return Cohen's kappa for two annotators' paired graded labels.

    ``kappa = (p_o - p_e) / (1 - p_e)``; ``1.0`` is perfect agreement and
    ``0.0`` is chance. If kappa falls below 0.5 the protocol says to fall back
    to binary relevance and report that.

    TODO(Tanchhay): implement Cohen's kappa.
    """

    raise NotImplementedError("TODO(Tanchhay): implement cohens_kappa")
