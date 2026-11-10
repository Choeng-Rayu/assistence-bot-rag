"""Answer-level evaluation: citations, abstention and completeness.

Owner: Tanchhay.
"""

from __future__ import annotations

from ..config import Config

__all__ = ["evaluate_answers"]


def evaluate_answers(n: int = 30, config: Config | None = None) -> dict:
    """Score *n* end-to-end answers (10 answerable, 10 adversarial, 10
    unanswerable) and return a report dict.

    Targets: citation correctness ≥85%, abstention ≥90%, completeness ≥80%,
    plus a human spot-check of 10 answers.

    TODO(Tanchhay): implement answer-level evaluation.
    """

    raise NotImplementedError("TODO(Tanchhay): implement evaluate_answers")
