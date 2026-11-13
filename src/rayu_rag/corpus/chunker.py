"""Markdown chunking for the frozen corpus (ported from ``docs.ts``).

Owner: Nike.
"""

from __future__ import annotations

import re

from ..contracts import Chunk

__all__ = ["chunk_document", "slugify"]

_HEADING_RE = re.compile(r"^( {0,3})(#{1,6})(?:[ \t]+(.*?)[ \t]*|[ \t]*)$")
_FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})")
_WORD_RE = re.compile(r"\S+")


def slugify(text: str) -> str:
    """Return a GitHub-style heading id for *text*.

    Rules (mirror the shipped docs renderer):

    * lowercase the text;
    * strip characters that are not word characters, spaces, ``_`` or ``-``;
    * collapse runs of whitespace to a single ``-``.

    GitHub keeps underscores and existing hyphens, removes punctuation, and
    turns whitespace into hyphens.
    """
    text = re.sub(r"[^\w\s-]", "", text.casefold(), flags=re.UNICODE)
    return re.sub(r"\s+", "-", text.strip())


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

    The parser deliberately works on lines so that a fence can never make a
    heading appear in the document structure.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be positive")

    lines = markdown.splitlines()
    headings: list[tuple[int, int, str, str]] = []
    in_fence = False
    fence_char = ""
    seen: dict[str, int] = {}
    used_ids: set[str] = set()
    for index, line in enumerate(lines):
        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(2)[0]
            if not in_fence:
                in_fence, fence_char = True, marker
            elif marker == fence_char:
                in_fence = False
            continue
        if not in_fence:
            match = _HEADING_RE.match(line)
            if match:
                level = len(match.group(2))
                heading = (match.group(3) or "").strip()
                base = slugify(heading)
                occurrence = seen.get(base, 0)
                heading_id = base if occurrence == 0 else f"{base}-{occurrence}"
                while heading_id in used_ids:
                    occurrence += 1
                    heading_id = f"{base}-{occurrence}"
                seen[base] = occurrence + 1
                used_ids.add(heading_id)
                headings.append((index, level, heading, heading_id))

    h1 = next((heading for heading in headings if heading[1] == 1), None)
    preamble_end = next(
        (heading[0] for heading in headings if heading[1] > 1),
        len(lines),
    )
    sections: list[tuple[int, int, str, tuple[str, ...], str | None]] = []
    if h1 is not None:
        sections.append((0, preamble_end, h1[2], (h1[2],), None))
    elif preamble_end:
        sections.append((0, preamble_end, title, (), None))

    stack: list[tuple[int, str]] = [(1, h1[2])] if h1 is not None else []
    for position, (start, level, heading, heading_id) in enumerate(headings):
        if level == 1:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, heading))
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        sections.append((start, end, heading, tuple(item[1] for item in stack), heading_id))

    chunks: list[Chunk] = []
    order = 0
    for start, end, heading, heading_path, heading_id in sections:
        section_lines = lines[start:end]
        for part_index, text in enumerate(_split_lines(section_lines, max_chars)):
            chunk_id = slug if heading_id is None else f"{slug}#{heading_id}"
            if part_index:
                chunk_id += f"~{part_index + 1}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    slug=slug,
                    title=title,
                    heading=heading,
                    heading_path=heading_path,
                    url=f"/docs/{slug}" if heading_id is None else f"/docs/{slug}#{heading_id}",
                    text=text,
                    char_len=len(text),
                    token_count=len(_WORD_RE.findall(text)),
                    part_index=part_index,
                    order=order,
                )
            )
            order += 1
    return chunks


def _split_lines(lines: list[str], max_chars: int) -> list[str]:
    """Pack complete lines, keeping fenced blocks together when possible."""
    result: list[str] = []
    current: list[str] = []
    in_fence = False
    fence_char = ""

    def flush() -> None:
        if current:
            text = "\n".join(current).strip()
            if text:
                result.append(text)
            current.clear()

    for line in lines:
        fence = _FENCE_RE.match(line)
        if fence and current and len("\n".join(current + [line]).strip()) > max_chars:
            flush()
        if fence:
            marker = fence.group(2)[0]
            if not in_fence:
                in_fence, fence_char = True, marker
            elif marker == fence_char:
                in_fence = False
        candidate = "\n".join(current + [line]).strip()
        if current and len(candidate) > max_chars and not in_fence:
            flush()
        current.append(line)
        if not in_fence and len("\n".join(current).strip()) > max_chars:
            flush()
    flush()
    return result
