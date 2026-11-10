"""Shared tokenizer for indexing and querying.

Owner: Somnang.
"""

from __future__ import annotations

__all__ = ["normalize", "stem", "tokenize"]


def normalize(text: str) -> str:
    """Normalize *text* before tokenization.

    Steps: NFKC normalize, lowercase, and collapse whitespace. Identifier
    punctuation (``_``, ``.``, ``-``) is preserved for :func:`tokenize`.

    TODO(Somnang): implement NFKC + lowercase normalization.
    """

    raise NotImplementedError("TODO(Somnang): implement normalize")


def tokenize(text: str, *, for_query: bool = False) -> list[str]:
    """Split *text* into index/query terms.

    Rules to implement:

    * split on any character that is not a letter or digit;
    * drop stopwords but keep negations ``not``, ``no`` and ``without``;
    * apply light stemming, except for identifiers;
    * identifiers (for example ``rayu_sk_live_...``,
      ``deepseek-v4.1-flash-cloud``, ``429``) are exceptions to stemming and
      are indexed both whole *and* split into their alphanumeric parts.

    *for_query* may apply lighter normalization for short user queries.

    TODO(Somnang): implement the shared tokenizer with identifier handling.
    """

    raise NotImplementedError("TODO(Somnang): implement tokenize")


def stem(token: str) -> str:
    """Return a light stem of *token* (identity for identifier exceptions).

    TODO(Somnang): implement light stemming with an identifier exception list.
    """

    raise NotImplementedError("TODO(Somnang): implement stem")
