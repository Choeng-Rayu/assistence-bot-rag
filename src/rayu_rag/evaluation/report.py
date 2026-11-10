"""Render evaluation reports as Markdown.

Owner: Tanchhay.
"""

from __future__ import annotations

__all__ = ["to_markdown"]


def to_markdown(report: dict) -> str:
    """Render an evaluation report dict as a Markdown document.

    Expected sections: run metadata (ranker, split, corpus version), an
    aggregate metrics table with bootstrap CIs, a per-query table, and a short
    notes section (pool-relative recall, κ if available).

    TODO(Tanchhay): implement report rendering.
    """

    raise NotImplementedError("TODO(Tanchhay): implement to_markdown")
