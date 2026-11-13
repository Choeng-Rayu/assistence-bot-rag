"""Shared tokenizer for indexing and querying.

Owner: Somnang.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["normalize", "stem", "tokenize"]

# ---------------------------------------------------------------------------
# Stopwords
# ---------------------------------------------------------------------------
# Common English function words that add no retrieval value.
# "not", "no", "without" are KEPT because they carry meaning in support queries
# (e.g. "install WITHOUT sudo", "NOT working", "NO api key").
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "it", "its", "as", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "do",
        "does", "did", "will", "would", "could", "should", "may", "might",
        "can", "this", "that", "these", "those", "then", "than", "so", "yet",
        "both", "also", "into", "over", "after", "before", "about", "between",
        "i", "you", "we", "my", "your", "our", "their", "his", "her", "its",
        "me", "him", "us", "them", "who", "which", "what", "when", "where",
        "how", "all", "each", "any", "some", "more", "most", "other", "such",
        "up", "out", "just", "now", "here", "there", "only", "very", "too",
        "s", "t",  # common after apostrophe splits: "it's" -> "it", "s"
    }
)

# ---------------------------------------------------------------------------
# Identifier detection
# ---------------------------------------------------------------------------
# A token is treated as an identifier (no stemming, indexed whole + split) if
# it matches any of the following patterns:
#
#   - contains an underscore:        rayu_sk_live_xxx, snake_case
#   - contains a dot or hyphen AND
#     digits or multiple segments:   deepseek-v4.1-flash-cloud, v1.2.3
#   - is purely numeric:             429, 200, 404
#   - starts with a known prefix:    rayu, deepseek, openai, ...

_IDENTIFIER_RE = re.compile(
    r"""
    ^(
        \d+                              # pure number: 429, 200
      | [a-z0-9]*_[a-z0-9_]+            # underscore name: rayu_sk_live
      | [a-z0-9]+(?:[-\.][a-z0-9]+){2,} # 3+ segments with - or .: deepseek-v4.1-flash-cloud
      | v\d+(?:\.\d+)+                  # version: v4.1, v1.2.3
    )$
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Split identifier into its alphanumeric parts:  "rayu_sk_live" -> ["rayu","sk","live"]
_ID_SPLIT_RE = re.compile(r"[^a-z0-9]+", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Light stemming rules
# ---------------------------------------------------------------------------
# Applied in order; the first matching rule wins.  Rules only fire when the
# result would be at least 4 characters long (to avoid over-stemming short words).
_STEM_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"nesses$"),  "ness"),
    (re.compile(r"nesses$"),  "ness"),
    (re.compile(r"ational$"), "ate"),
    (re.compile(r"tional$"),  "tion"),
    (re.compile(r"enci$"),    "ence"),
    (re.compile(r"anci$"),    "ance"),
    (re.compile(r"izer$"),    "ize"),
    (re.compile(r"ising$"),   "ise"),
    (re.compile(r"izing$"),   "ize"),
    (re.compile(r"ising$"),   "ise"),
    (re.compile(r"alism$"),   "al"),
    (re.compile(r"iveness$"), "ive"),
    (re.compile(r"fulness$"), "ful"),
    (re.compile(r"ousness$"), "ous"),
    (re.compile(r"aliti$"),   "al"),
    (re.compile(r"iviti$"),   "ive"),
    (re.compile(r"biliti$"),  "ble"),
    (re.compile(r"icate$"),   "ic"),
    (re.compile(r"ative$"),   ""),
    (re.compile(r"alize$"),   "al"),
    (re.compile(r"iciti$"),   "ic"),
    (re.compile(r"ical$"),    "ic"),
    (re.compile(r"ful$"),     ""),
    (re.compile(r"ness$"),    ""),
    (re.compile(r"ement$"),   ""),
    (re.compile(r"ment$"),    ""),
    (re.compile(r"ance$"),    ""),
    (re.compile(r"ence$"),    ""),
    (re.compile(r"ings$"),    "ing"),
    (re.compile(r"ers$"),     "er"),
    (re.compile(r"ies$"),     "i"),
    (re.compile(r"ing$"),     ""),
    (re.compile(r"tion$"),    "t"),
    (re.compile(r"ions$"),    "ion"),
    (re.compile(r"ion$"),     ""),
    (re.compile(r"ed$"),      ""),
    (re.compile(r"ly$"),      ""),
    (re.compile(r"er$"),      ""),
    (re.compile(r"al$"),      ""),
    (re.compile(r"ic$"),      ""),
    (re.compile(r"es$"),      ""),
    (re.compile(r"s$"),       ""),
]

# Minimum length of the stem result (protects short words from over-stemming).
_MIN_STEM_LEN = 3


def normalize(text: str) -> str:
    """Normalize *text* before tokenization.

    Steps:
    1. NFKC unicode normalization (e.g. ligatures, fullwidth chars).
    2. Lowercase.
    3. Collapse runs of whitespace to a single space.

    Identifier punctuation (``_``, ``.``, ``-``) is preserved so that
    :func:`tokenize` can detect and split them correctly.
    """
    # Step 1: NFKC normalization (ﬁ → fi, ² → 2, fullwidth → ASCII, etc.)
    text = unicodedata.normalize("NFKC", text)
    # Step 2: lowercase
    text = text.lower()
    # Step 3: collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_identifier(token: str) -> bool:
    """Return True if *token* should be treated as an identifier (no stemming)."""
    return bool(_IDENTIFIER_RE.match(token))


def stem(token: str) -> str:
    """Return a light stem of *token*.

    Applies a Porter-style suffix stripping in a single pass.  Identifiers
    (pure numbers, underscore names, versioned strings) are returned unchanged.

    The result is never shorter than :data:`_MIN_STEM_LEN` characters.
    """
    if _is_identifier(token):
        return token

    original = token
    for pattern, replacement in _STEM_RULES:
        new = pattern.sub(replacement, token)
        if new != token and len(new) >= _MIN_STEM_LEN:
            return new

    return original


def tokenize(text: str, *, for_query: bool = False) -> list[str]:
    """Split *text* into index/query terms.

    Processing pipeline:
    1. :func:`normalize` — NFKC + lowercase + whitespace collapse.
    2. Split on any character that is not a letter or digit; the raw
       split tokens still include ``_``, ``.``, ``-`` fragments so we
       re-join identifier-shaped sequences first.
    3. Drop stopwords (but keep ``not``, ``no``, ``without``).
    4. Identifiers are indexed **whole** AND as their split parts:
       ``rayu_sk_live_xxx``  →  ``["rayu_sk_live_xxx", "rayu", "sk", "live", "xxx"]``
    5. Non-identifier tokens are light-stemmed.

    *for_query* does not change the algorithm today but is reserved for
    future query-time relaxations (e.g. skip stemming for very short queries).
    """
    text = normalize(text)

    # -----------------------------------------------------------------------
    # Phase 1: Extract raw candidate tokens (keep identifier punctuation).
    # We walk through the normalized text and collect maximal runs of
    # alphanumeric + {_, ., -} characters, then decide per-token whether it
    # is an identifier or a plain word.
    # -----------------------------------------------------------------------
    raw_tokens: list[str] = re.findall(r"[a-z0-9][a-z0-9_.@-]*[a-z0-9]|[a-z0-9]", text)

    terms: list[str] = []
    seen: set[str] = set()

    def _add(term: str) -> None:
        """Add *term* to terms if non-empty, non-stopword, and not duplicate."""
        if term and term not in _STOPWORDS and term not in seen:
            seen.add(term)
            terms.append(term)

    for raw in raw_tokens:
        if not raw:
            continue

        if _is_identifier(raw):
            # Index whole identifier (no stemming)
            _add(raw)
            # Also index each alphanumeric part individually
            parts = [p for p in _ID_SPLIT_RE.split(raw) if p]
            for part in parts:
                # Stem the individual parts unless they look like a sub-identifier
                if _is_identifier(part):
                    _add(part)
                else:
                    stemmed = stem(part)
                    _add(stemmed)
        else:
            # Plain word — apply stopword filter then stem
            if raw in _STOPWORDS:
                continue
            stemmed = stem(raw)
            _add(stemmed)

    return terms
