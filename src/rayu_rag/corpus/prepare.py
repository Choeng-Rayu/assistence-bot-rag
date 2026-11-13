"""Corpus preparation entry point.

Owner: Nike.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..contracts import Chunk, DocumentMeta
from ..io import sha256_file, write_jsonl, chunk_to_dict, document_to_dict
from .chunker import chunk_document
from .titles import doc_title

__all__ = ["prepare_corpus"]


def prepare_corpus(
    docs_dir: Path,
    out_dir: Path,
) -> tuple[list[DocumentMeta], list[Chunk]]:
    """Chunk every ``*.md`` file in *docs_dir* and write corpus artifacts.

    Writes ``documents.jsonl`` and ``chunks.jsonl`` under *out_dir* and returns
    the in-memory ``(documents, chunks)`` pair. Ordering must be deterministic:
    documents by slug, chunks by document order then ``part_index``.

    Only the 14 frozen documents are expected; ``README`` files are skipped.

    README and non-Markdown files are provenance material, not source documents.
    """
    documents: list[DocumentMeta] = []
    all_chunks: list[Chunk] = []
    for path in sorted(Path(docs_dir).glob("*.md"), key=lambda item: item.name):
        if path.stem.lower() == "readme":
            continue
        slug = path.stem
        markdown = path.read_text(encoding="utf-8")
        title_match = re.search(r"^ {0,3}# +(.+?)\s*#*\s*$", markdown, re.MULTILINE)
        fallback = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
        title = doc_title(slug, fallback)
        chunks = chunk_document(markdown, slug=slug, title=title)
        all_chunks.extend(chunks)
        documents.append(
            DocumentMeta(
                slug=slug,
                title=title,
                source_path=(Path(Path(docs_dir).name) / path.name).as_posix(),
                source_url=f"/docs/{slug}",
                sha256=sha256_file(path),
                char_count=len(markdown),
                word_count=len(markdown.split()),
                heading_count=_heading_count(markdown),
                chunk_count=len(chunks),
            )
        )
    documents.sort(key=lambda document: document.slug)
    all_chunks.sort(key=lambda chunk: (chunk.slug, chunk.order))
    write_jsonl(Path(out_dir) / "documents.jsonl", (document_to_dict(document) for document in documents))
    write_jsonl(Path(out_dir) / "chunks.jsonl", (chunk_to_dict(chunk) for chunk in all_chunks))
    return documents, all_chunks


def _heading_count(markdown: str) -> int:
    count = 0
    in_fence = False
    fence_char = ""
    for line in markdown.splitlines():
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)[0]
            if not in_fence:
                in_fence, fence_char = True, marker
            elif marker == fence_char:
                in_fence = False
            continue
        if not in_fence and re.match(r"^ {0,3}#{1,6}(?:\s|$)", line):
            count += 1
    return count
