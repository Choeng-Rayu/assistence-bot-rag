"""Corpus manifest: provenance and integrity hashes.

Owner: Nike.
"""

from __future__ import annotations

from pathlib import Path

from ..contracts import Chunk, DocumentMeta
from ..io import read_json, read_jsonl, sha256_file

__all__ = ["build_manifest", "verify_manifest"]


def build_manifest(
    docs_dir: Path,
    docs: list[DocumentMeta],
    chunks: list[Chunk],
    *,
    source_commit: str,
) -> dict:
    """Build the canonical corpus manifest.

    The manifest records ``source_repo``, ``source_commit``, the number of
    documents/chunks, and per-file ``sha256`` hashes so the corpus can be
    verified and the index ``corpus_version`` can be derived reproducibly.

    Source provenance is fixed by the frozen corpus README.
    """
    files = [
        {"path": path.name, "sha256": sha256_file(path)}
        for path in sorted(Path(docs_dir).glob("*.md"), key=lambda item: item.name)
        if path.stem.lower() != "readme"
    ]
    return {
        "schema_version": 1,
        "source_repo": "Choeng-Rayu/rayu-web",
        "source_commit": source_commit,
        "document_count": len(docs),
        "chunk_count": len(chunks),
        "files": files,
    }


def verify_manifest(docs_dir: Path, manifest_path: Path) -> list[str]:
    """Return a list of human-readable problems; ``[]`` means the corpus is valid.

    Checks that every manifest file exists under *docs_dir*, that its SHA-256
    still matches, and that the document/chunk counts agree.

    Missing or malformed artifacts are reported rather than silently treated as
    valid, which keeps CLI verification actionable.
    """
    problems: list[str] = []
    try:
        manifest = read_json(manifest_path)
    except (OSError, ValueError) as exc:
        return [f"cannot read manifest: {exc}"]
    files = manifest.get("files")
    if not isinstance(files, list):
        return ["manifest files is not a list"]
    for entry in files:
        relative = entry.get("path") if isinstance(entry, dict) else None
        expected = entry.get("sha256") if isinstance(entry, dict) else None
        if not isinstance(relative, str) or not isinstance(expected, str):
            problems.append(f"invalid manifest file entry: {entry!r}")
            continue
        path = Path(docs_dir) / relative
        if not path.is_file():
            problems.append(f"missing source file: {relative}")
        elif sha256_file(path) != expected:
            problems.append(f"sha256 mismatch: {relative}")

    documents_path = Path(manifest_path).with_name("documents.jsonl")
    chunks_path = Path(manifest_path).with_name("chunks.jsonl")
    try:
        document_count = len(read_jsonl(documents_path))
        chunk_count = len(read_jsonl(chunks_path))
        if document_count != manifest.get("document_count"):
            problems.append("document count mismatch")
        if chunk_count != manifest.get("chunk_count"):
            problems.append("chunk count mismatch")
    except (OSError, ValueError) as exc:
        problems.append(f"cannot read corpus artifacts: {exc}")
    return problems
