"""Canonical, deterministic JSON/JSONL and hashing helpers.

Everything here is stdlib-only. Output is byte-stable: sorted keys, compact
separators, UTF-8, ``ensure_ascii=False`` and a single trailing newline. No
timestamps or host-specific values are ever written.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .contracts import Chunk, DocumentMeta


def canonical_json(obj: Any) -> str:
    """Serialize *obj* to canonical JSON (sorted keys, compact separators)."""

    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path: Path, obj: Any) -> None:
    """Write *obj* as canonical JSON with a trailing newline (UTF-8)."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(obj) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a JSON document from *path* (UTF-8)."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    """Write *rows* as canonical JSONL, one compact object per line."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(dict(row)))
            handle.write("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file, skipping blank lines."""

    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def sha256_text(text: str) -> str:
    """Return the hex SHA-256 of *text* encoded as UTF-8."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of the raw bytes of *path*."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def chunk_to_dict(chunk: Chunk) -> dict[str, Any]:
    """Convert a :class:`Chunk` to its snake_case JSONL representation."""

    return {
        "chunk_id": chunk.chunk_id,
        "slug": chunk.slug,
        "title": chunk.title,
        "heading": chunk.heading,
        "heading_path": list(chunk.heading_path),
        "url": chunk.url,
        "text": chunk.text,
        "char_len": chunk.char_len,
        "token_count": chunk.token_count,
        "part_index": chunk.part_index,
        "order": chunk.order,
        "source_type": chunk.source_type,
    }


def chunk_from_dict(row: Mapping[str, Any]) -> Chunk:
    """Build a :class:`Chunk` from a JSONL row (``heading_path`` -> tuple)."""

    heading_path = row.get("heading_path") or ()
    return Chunk(
        chunk_id=row["chunk_id"],
        slug=row["slug"],
        title=row["title"],
        heading=row["heading"],
        heading_path=tuple(heading_path),
        url=row["url"],
        text=row["text"],
        char_len=int(row["char_len"]),
        token_count=int(row["token_count"]),
        part_index=int(row["part_index"]),
        order=int(row["order"]),
        source_type=row.get("source_type", "docs"),
    )


def document_to_dict(meta: DocumentMeta) -> dict[str, Any]:
    """Convert a :class:`DocumentMeta` to its snake_case JSONL representation."""

    return {
        "slug": meta.slug,
        "title": meta.title,
        "source_path": meta.source_path,
        "source_url": meta.source_url,
        "sha256": meta.sha256,
        "char_count": meta.char_count,
        "word_count": meta.word_count,
        "heading_count": meta.heading_count,
        "chunk_count": meta.chunk_count,
        "source_type": meta.source_type,
    }


def document_from_dict(row: Mapping[str, Any]) -> DocumentMeta:
    """Build a :class:`DocumentMeta` from a JSONL row."""

    return DocumentMeta(
        slug=row["slug"],
        title=row["title"],
        source_path=row["source_path"],
        source_url=row["source_url"],
        sha256=row["sha256"],
        char_count=int(row["char_count"]),
        word_count=int(row["word_count"]),
        heading_count=int(row["heading_count"]),
        chunk_count=int(row["chunk_count"]),
        source_type=row.get("source_type", "docs"),
    )
