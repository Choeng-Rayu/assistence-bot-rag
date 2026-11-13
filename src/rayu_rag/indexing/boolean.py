"""Boolean query parsing and evaluation (the filter/debugging layer).

Owner: Somnang.

Grammar (precedence, lowest to highest):
    expr   := or_expr
    or_expr  := and_expr  ( 'OR'  and_expr )*
    and_expr := not_expr  ( 'AND' not_expr )*
    not_expr := 'NOT' not_expr
              | atom
    atom   := '(' expr ')'
              | TERM

AND binds tighter than OR; NOT binds tightest of all.
Terms are normalized/stemmed by the shared tokenizer before lookup.
"""

from __future__ import annotations

from typing import TypeAlias

from ..contracts import LoadedIndex
from .postings import complement, intersect, union
from .tokenizer import tokenize

#: A parsed Boolean expression tree.
#: Leaves are term strings; inner nodes are
#: ``("AND", left, right)``, ``("OR", left, right)``, or ``("NOT", node)``.
BoolNode: TypeAlias = str | tuple[object, ...]

__all__ = ["BoolNode", "boolean_query", "execute_boolean", "parse_boolean"]

# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

def _tokenize_expr(expr: str) -> list[str]:
    """Split a Boolean expression into operator/punctuation/term tokens.

    Returns a flat list where each item is one of:
    - ``"AND"`` / ``"OR"`` / ``"NOT"``  (Boolean operators, uppercase)
    - ``"("`` / ``")"``                  (grouping)
    - a plain term string                (everything else)
    """
    import re
    # Tokenise by splitting on whitespace and parentheses; keep parens as tokens
    raw = re.findall(r"[()]|[^\s()]+", expr)
    tokens: list[str] = []
    for tok in raw:
        upper = tok.upper()
        if upper in ("AND", "OR", "NOT", "(", ")"):
            tokens.append(upper if upper != tok else tok)
        else:
            tokens.append(tok)
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------

class _Parser:
    """Recursive-descent parser that builds a BoolNode tree."""

    def __init__(self, tokens: list[str]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- helpers ----------------------------------------------------------

    def _peek(self) -> str | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _consume(self) -> str:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, value: str) -> None:
        tok = self._consume()
        if tok != value:
            raise ValueError(f"Boolean parse error: expected {value!r}, got {tok!r}")

    # -- grammar rules ----------------------------------------------------

    def parse(self) -> BoolNode:
        node = self._or_expr()
        if self._peek() is not None:
            raise ValueError(
                f"Boolean parse error: unexpected token {self._peek()!r}"
            )
        return node

    def _or_expr(self) -> BoolNode:
        """or_expr := and_expr ( 'OR' and_expr )*"""
        left = self._and_expr()
        while self._peek() == "OR":
            self._consume()  # eat "OR"
            right = self._and_expr()
            left = ("OR", left, right)
        return left

    def _and_expr(self) -> BoolNode:
        """and_expr := not_expr ( 'AND' not_expr )*"""
        left = self._not_expr()
        while self._peek() == "AND":
            self._consume()  # eat "AND"
            right = self._not_expr()
            left = ("AND", left, right)
        return left

    def _not_expr(self) -> BoolNode:
        """not_expr := 'NOT' not_expr | atom"""
        if self._peek() == "NOT":
            self._consume()  # eat "NOT"
            operand = self._not_expr()
            return ("NOT", operand)
        return self._atom()

    def _atom(self) -> BoolNode:
        """atom := '(' expr ')' | TERM"""
        tok = self._peek()
        if tok is None:
            raise ValueError("Boolean parse error: unexpected end of expression")
        if tok == "(":
            self._consume()  # eat "("
            node = self._or_expr()
            self._expect(")")
            return node
        if tok in ("AND", "OR", "NOT", ")"):
            raise ValueError(
                f"Boolean parse error: unexpected operator {tok!r} where a term was expected"
            )
        self._consume()
        return tok  # leaf: a raw term string


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def parse_boolean(expr: str) -> BoolNode:
    """Parse a Boolean expression such as ``429 AND NOT hosted``.

    Grammar: term, NOT expr, expr AND expr, expr OR expr with
    parentheses. AND binds tighter than OR.

    Returns a BoolNode tree:
    - Leaf nodes are raw term strings (not yet tokenized/stemmed).
    - Inner nodes are ``("AND", left, right)``, ``("OR", left, right)``,
      or ``("NOT", node)``.

    Examples::

        parse_boolean("install AND NOT windows")
        # ("AND", "install", ("NOT", "windows"))

        parse_boolean("429 OR rate limit")
        # ("OR", ("OR", "429", "rate"), "limit")
    """
    tokens = _tokenize_expr(expr.strip())
    if not tokens:
        raise ValueError("Boolean parse error: empty expression")
    parser = _Parser(tokens)
    return parser.parse()


def execute_boolean(node: BoolNode, index: LoadedIndex) -> list[str]:
    """Evaluate a parsed Boolean tree against *index*, returning sorted chunk ids.

    - Leaf (term string): normalize + stem via the shared tokenizer, then look
      up in ``index.artifact.postings``.  Unknown terms produce an empty list.
    - ``("AND", left, right)`` → :func:`~rayu_rag.indexing.postings.intersect`
    - ``("OR",  left, right)`` → :func:`~rayu_rag.indexing.postings.union`
    - ``("NOT", node)``        → :func:`~rayu_rag.indexing.postings.complement`
      against the full ``index.artifact.chunk_ids``.
    """
    if isinstance(node, str):
        # Leaf: tokenize the raw term to apply the same normalization used at
        # index time.  A single word typically produces one stemmed token.
        terms = tokenize(node)
        if not terms:
            return []
        # Use the first term produced (tokenize may split an identifier)
        # and union all produced terms so identifiers work correctly.
        all_ids: list[str] = []
        for term in terms:
            posting_list = index.artifact.postings.get(term, [])
            chunk_ids = [p.chunk_id for p in posting_list]
            all_ids = union(all_ids, chunk_ids)
        return all_ids

    # Inner node
    op = node[0]
    if op == "AND":
        _, left, right = node
        left_ids = execute_boolean(left, index)   # type: ignore[arg-type]
        right_ids = execute_boolean(right, index)  # type: ignore[arg-type]
        return intersect(left_ids, right_ids)

    if op == "OR":
        _, left, right = node
        left_ids = execute_boolean(left, index)   # type: ignore[arg-type]
        right_ids = execute_boolean(right, index)  # type: ignore[arg-type]
        return union(left_ids, right_ids)

    if op == "NOT":
        _, operand = node
        operand_ids = execute_boolean(operand, index)  # type: ignore[arg-type]
        universe = list(index.artifact.chunk_ids)
        return complement(operand_ids, universe)

    raise ValueError(f"execute_boolean: unknown operator {op!r}")


def boolean_query(expr: str, index: LoadedIndex) -> list[str]:
    """Parse and evaluate *expr*, returning sorted matching chunk ids.

    Convenience wrapper around :func:`parse_boolean` +
    :func:`execute_boolean`.

    Example::

        boolean_query("install AND NOT windows", index)
        # ["01-installation#one-command-any-machine", ...]
    """
    tree = parse_boolean(expr)
    return execute_boolean(tree, index)
