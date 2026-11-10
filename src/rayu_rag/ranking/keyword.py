"""Port of the shipped keyword scorer (``scoreSection`` in ``docs.ts``).

Owner: Tanchhay.
"""

from __future__ import annotations

from ..contracts import LoadedIndex, ScoredChunk

__all__ = ["KeywordRanker"]

#: Exact scoring constants from ``lib/supportBot/docs.ts``.
HEADING_WEIGHT = 3
TITLE_WEIGHT = 2
BODY_CAP = 12
PHRASE_BONUS = 10
IDENTIFIER_BONUS = 8
IDENTIFIER_CAP = 16
SCALE = 30
CHAR_FLOOR = 1000
DOC_BOOST_CAP = 30
MIN_SCORE = 2
IDENTIFIER_RE = r"[a-z0-9]+(?:[._-][a-z0-9]+)+|\d{3}"


class KeywordRanker:
    """Baseline ranker: exact port of the hand-tuned keyword scorer.

    Reference formula (must match ``docs.ts`` exactly)::

        raw = 3 * heading_hits
            + 2 * title_hits
            + min(body_occurrences, 12)
            + (10 if the query phrase appears verbatim else 0)
            + min(8 * identifier_hits, 16)
        score = raw * 30 / sqrt(max(chars, 1000))

    A per-document boost is added once and capped at 30. Chunks scoring below
    ``MIN_SCORE = 2`` are dropped. Identifiers are matched with
    ``[a-z0-9]+(?:[._-][a-z0-9]+)+|\\d{3}``.

    Ties break by higher score, then by document order. This is the baseline the
    BM25/fusion rankers must beat on the labelled query set.
    """

    name = "keyword"

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Score *index.chunks* for *query* and return the top *k* chunks.

        Each ``ScoredChunk.components`` records the ``heading``, ``title``,
        ``body``, ``phrase``, ``identifier`` and ``boost`` contributions.

        TODO(Tanchhay): implement the exact keyword scoring port.
        """

        raise NotImplementedError("TODO(Tanchhay): implement KeywordRanker.rank")
