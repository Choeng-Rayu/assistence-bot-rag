"""Inverted index: tokenizer, postings, Boolean queries, build and store.

Owner: Somnang. Every algorithm in this package is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Somnang)`` message until P2 lands.
"""

from __future__ import annotations

from .boolean import BoolNode, boolean_query, execute_boolean, parse_boolean
from .builder import build_index
from .postings import build_postings, complement, intersect, union
from .store import load_index, write_index
from .tokenizer import normalize, stem, tokenize

__all__ = [
    "BoolNode",
    "boolean_query",
    "build_index",
    "build_postings",
    "complement",
    "execute_boolean",
    "intersect",
    "load_index",
    "normalize",
    "parse_boolean",
    "stem",
    "tokenize",
    "union",
    "write_index",
]
