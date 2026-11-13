"""Port of the shipped keyword scorer (``scoreSection`` in ``docs.ts``).

Owner: Tanchhay.
"""

from __future__ import annotations

import math
import re

from ..contracts import LoadedIndex, ScoredChunk
from ..indexing.tokenizer import _STOPWORDS
from ._util import finalize

__all__ = ["KeywordRanker", "query_identifiers", "query_terms"]

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

_WORD_RE = re.compile(r"[a-z0-9]+")
_IDENT = re.compile(IDENTIFIER_RE)
_MIN_TERM_LEN = 3
_MIN_PHRASE_LEN = 4
#: Boost per query term found in a document slug.
_SLUG_BOOST = 5


def query_terms(query: str) -> list[str]:
    """Distinct lowercase query words, minus stopwords and 1-2 char words."""

    seen: dict[str, None] = {}
    for word in _WORD_RE.findall(query.lower()):
        if len(word) >= _MIN_TERM_LEN and word not in _STOPWORDS:
            seen.setdefault(word)
    return list(seen)


def query_identifiers(query: str) -> list[str]:
    """Distinct identifier-shaped tokens (``429``, ``rayu_sk_live``, ``a-b.c``)."""

    return list(dict.fromkeys(_IDENT.findall(query.lower())))


def _hits(terms: list[str], text: str) -> int:
    return sum(1 for term in terms if term in text)


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

    ``docs.ts`` is not in this repo, so query tokenization and the per-document
    boost (5 per query term in the slug, added once to the document's best
    chunk, capped at 30) follow the formula above rather than the TypeScript.
    """

    name = "keyword"

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]:
        """Score *index.chunks* for *query* and return the top *k* chunks.

        Each ``ScoredChunk.components`` records the ``heading``, ``title``,
        ``body``, ``phrase``, ``identifier`` and ``boost`` contributions.
        """

        terms = query_terms(query)
        identifiers = query_identifiers(query)
        phrase = " ".join(_WORD_RE.findall(query.lower()))
        if not terms and not identifiers:
            return []

        rows: list[list] = []
        best_per_slug: dict[str, int] = {}
        for chunk in index.chunks:
            text = chunk.text.lower()
            heading_part = HEADING_WEIGHT * _hits(terms, chunk.heading.lower())
            title_part = TITLE_WEIGHT * _hits(terms, chunk.title.lower())
            body_part = min(sum(text.count(term) for term in terms), BODY_CAP)
            phrase_part = (
                PHRASE_BONUS
                if len(phrase) >= _MIN_PHRASE_LEN and phrase in " ".join(_WORD_RE.findall(text))
                else 0
            )
            ident_part = min(
                IDENTIFIER_BONUS * sum(1 for ident in identifiers if ident in text),
                IDENTIFIER_CAP,
            )
            raw = heading_part + title_part + body_part + phrase_part + ident_part
            scale = SCALE / math.sqrt(max(chunk.char_len or len(chunk.text), CHAR_FLOOR))
            score = raw * scale
            if score < MIN_SCORE:
                continue
            components = {
                "heading": heading_part * scale,
                "title": title_part * scale,
                "body": body_part * scale,
                "phrase": phrase_part * scale,
                "identifier": ident_part * scale,
                "boost": 0.0,
            }
            rows.append([chunk, score, components])
            current = best_per_slug.get(chunk.slug)
            if current is None or score > rows[current][1]:
                best_per_slug[chunk.slug] = len(rows) - 1

        for slug, position in best_per_slug.items():
            boost = min(_SLUG_BOOST * _hits(terms, slug.lower()), DOC_BOOST_CAP)
            if boost:
                rows[position][1] += boost
                rows[position][2]["boost"] = float(boost)

        return finalize(((c, s, comp) for c, s, comp in rows), k)
