"""Refusal policy for ungrounded answers.

Owner: Reach.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..contracts import RetrievalResult

__all__ = ["calibrate_threshold", "should_refuse"]


def should_refuse(result: RetrievalResult, threshold: float | None) -> bool:
    """Return whether the assistant must refuse to answer.

    Refuse when the result has no hits, or when *threshold* is set and the top
    score is below it. ``threshold=None`` disables the score check.

    TODO(Reach): implement the refusal predicate.
    """

    raise NotImplementedError("TODO(Reach): implement should_refuse")


def calibrate_threshold(dev_results: Sequence[RetrievalResult]) -> float:
    """Choose a refusal threshold from dev-split retrieval results.

    Pick the score cut-off that maximises answerable-vs-unanswerable separation
    on the dev split only; the hold-out split is never consulted.

    TODO(Reach): implement threshold calibration on dev results.
    """

    raise NotImplementedError("TODO(Reach): implement calibrate_threshold")
