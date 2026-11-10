"""Boolean query parsing and evaluation (the filter/debugging layer).

Owner: Somnang.
"""

from __future__ import annotations

from typing import TypeAlias

from ..contracts import LoadedIndex

#: A parsed Boolean expression tree. Leaves are term strings; inner nodes are
#: ``("AND", left, right)``, ``("OR", left, right)`` or ``("NOT", node)``.
BoolNode: TypeAlias = str | tuple[object, ...]

__all__ = ["BoolNode", "boolean_query", "execute_boolean", "parse_boolean"]


def parse_boolean(expr: str) -> BoolNode:
    """Parse a Boolean expression such as ``429 AND NOT hosted``.

    Grammar: ``term``, ``NOT expr``, ``expr AND expr``, ``expr OR expr`` with
    parentheses. ``AND`` binds tighter than ``OR``. Terms are tokenized with the
    shared tokenizer.

    TODO(Somnang): implement the recursive-descent Boolean parser.
    """

    raise NotImplementedError("TODO(Somnang): implement parse_boolean")


def execute_boolean(node: BoolNode, index: LoadedIndex) -> list[str]:
    """Evaluate a parsed Boolean tree against *index*, returning sorted ids.

    ``AND``/``OR``/``NOT`` use the sorted :mod:`rayu_rag.indexing.postings` set
    operations; ``NOT`` complements against ``index.artifact.chunk_ids``.

    TODO(Somnang): implement Boolean tree evaluation.
    """

    raise NotImplementedError("TODO(Somnang): implement execute_boolean")


def boolean_query(expr: str, index: LoadedIndex) -> list[str]:
    """Parse and evaluate *expr*, returning sorted matching chunk ids.

    TODO(Somnang): implement parse + execute convenience wrapper.
    """

    raise NotImplementedError("TODO(Somnang): implement boolean_query")
