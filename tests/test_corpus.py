from __future__ import annotations

import json
from pathlib import Path

from rayu_rag.corpus import build_manifest, chunk_document, prepare_corpus, slugify, verify_manifest


def test_slugify_and_chunk_ids_are_stable() -> None:
    markdown = """# Guide

Intro.

## API, setup!

one

## API, setup!

```md
## Not a heading
```

two
"""
    chunks = chunk_document(markdown, slug="guide", title="Guide", max_chars=1800)
    assert slugify("API, setup!") == "api-setup"
    assert [chunk.chunk_id for chunk in chunks] == [
        "guide",
        "guide#api-setup",
        "guide#api-setup-1",
    ]
    assert all("not-a-heading" not in chunk.chunk_id for chunk in chunks)
    assert chunks[1].heading_path == ("Guide", "API, setup!")


def test_chunk_splits_at_line_boundaries(tmp_path: Path) -> None:
    markdown = "# Guide\n\n## Details\n\n" + "\n".join(f"line {i}" for i in range(30))
    chunks = chunk_document(markdown, slug="guide", title="Guide", max_chars=40)
    assert len(chunks) > 1
    assert all(chunk.char_len <= 40 for chunk in chunks)
    assert all("\n" not in line for chunk in chunks for line in chunk.text.splitlines() if len(line) > 40)


def test_prepare_and_manifest_are_deterministic(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    out_dir = tmp_path / "out"
    docs_dir.mkdir()
    (docs_dir / "README.md").write_text("provenance", encoding="utf-8")
    (docs_dir / "b.md").write_text("# B\n\n## Section\n\ntext\n", encoding="utf-8")
    (docs_dir / "a.md").write_text("# A\n\nintro\n", encoding="utf-8")

    documents, chunks = prepare_corpus(docs_dir, out_dir)
    manifest = build_manifest(docs_dir, documents, chunks, source_commit="abc123")
    (out_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    first_documents = (out_dir / "documents.jsonl").read_bytes()
    first_chunks = (out_dir / "chunks.jsonl").read_bytes()
    prepare_corpus(docs_dir, out_dir)
    assert (out_dir / "documents.jsonl").read_bytes() == first_documents
    assert (out_dir / "chunks.jsonl").read_bytes() == first_chunks
    assert [document.slug for document in documents] == ["a", "b"]
    assert manifest["files"] == [
        {"path": "a.md", "sha256": documents[0].sha256},
        {"path": "b.md", "sha256": documents[1].sha256},
    ]
    assert verify_manifest(docs_dir, out_dir / "manifest.json") == []
