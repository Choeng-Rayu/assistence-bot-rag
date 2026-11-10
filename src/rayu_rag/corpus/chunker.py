"""Markdown chunking for the frozen corpus (ported from ``docs.ts``).

Owner: Nike.
"""

from __future__ import annotations

from ..contracts import Chunk

__all__ = ["chunk_document", "slugify"]


def slugify(text: str) -> str:
    """Return a GitHub-style heading id for *text*.

    Rules (mirror the shipped docs renderer):

    * lowercase the text;
    * strip characters that are not word characters, spaces, ``_`` or ``-``;
    * collapse runs of whitespace to a single ``-``.

    TODO(Nike): implement the GitHub slugifier used by the docs renderer.
    """

    raise NotImplementedError("TODO(Nike): implement GitHub-style heading slugify")


def chunk_document(
    markdown: str,
    *,
    slug: str,
    title: str,
    max_chars: int = 1800,
) -> list[Chunk]:
    """Split one document into retrievable :class:`Chunk` records.

    Rules to implement (port from ``lib/supportBot/docs.ts``):

    * Split at ATX headings (``#``..``######``) that appear outside fenced code
      blocks; the H1 plus its intro becomes a preamble chunk.
    * Every chunk is at most *max_chars* characters. Oversized sections split at
      line boundaries and never inside a fenced code block.
    * Heading ids use :func:`slugify`, de-duplicated per document as ``x``,
      ``x-1``, ``x-2`` (GitHub behaviour).
    * ``url`` is ``/docs/<slug>#<heading-id>``; the preamble is ``/docs/<slug>``.
    * Chunk ids: preamble ``<slug>``; first part ``<slug>#<heading-id>``;
      overflow parts ``<slug>#<heading-id>~2``, ``~3``. The citation ``url``
      never changes across overflow parts.

    TODO(Nike): implement the exact chunking semantics above.
    """

    raise NotImplementedError("TODO(Nike): implement heading-aware document chunking")
