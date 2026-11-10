"""Citation extraction and source pills.

Owner: Reach.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..contracts import Chunk, Citation, SourceRef

__all__ = ["extract_citations", "source_pills"]


def extract_citations(answer: str, sources: Sequence[SourceRef]) -> list[Citation]:
    """Map numeric citation markers in *answer* back to retrieved sources.

    Markers are 1-based and correspond to the order of *sources*; unknown
    markers are ignored. Returns citations in marker order, de-duplicated.

    TODO(Reach): implement citation extraction.
    """

    raise NotImplementedError("TODO(Reach): implement extract_citations")


def source_pills(chunks: Sequence[Chunk], limit: int = 4) -> list[SourceRef]:
    """Return at most *limit* unique source references, in retrieval order.

    Uniqueness is by URL (not chunk id), so overflow parts of the same section
    collapse to a single pill.

    TODO(Reach): implement source-pill assembly.
    """

    raise NotImplementedError("TODO(Reach): implement source_pills")
