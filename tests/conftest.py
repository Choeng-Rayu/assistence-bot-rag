"""Shared pytest fixtures for the foundation test suite.

``tiny_loaded_index`` is constructed purely from the frozen contracts so that
ranking/evaluation/API tests can exercise retrieval without depending on the
indexing implementation.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from rayu_rag.contracts import (
    Chunk,
    IndexArtifact,
    LoadedIndex,
    Posting,
)
from rayu_rag.io import chunk_from_dict, read_jsonl

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the repository root."""

    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def fixture_docs_dir(repo_root: Path) -> Path:
    """Directory holding the miniature Markdown corpus."""

    return repo_root / "tests" / "fixtures" / "docs"


@pytest.fixture(scope="session")
def tiny_chunks() -> tuple[Chunk, ...]:
    """The four fixture chunks, parsed through ``chunk_from_dict``."""

    rows = read_jsonl(FIXTURES_DIR / "tiny_chunks.jsonl")
    return tuple(chunk_from_dict(row) for row in rows)


@pytest.fixture(scope="session")
def tiny_qrels() -> list[dict]:
    """Two fixture queries with three graded judgements."""

    return read_jsonl(FIXTURES_DIR / "tiny_qrels.jsonl")


@pytest.fixture(scope="session")
def tiny_loaded_index(tiny_chunks: tuple[Chunk, ...]) -> LoadedIndex:
    """A hand-built inverted index over the fixture chunks."""

    postings: dict[str, list[Posting]] = {}
    doc_lengths: dict[str, int] = {}

    for chunk in tiny_chunks:
        tokens = _tokens(chunk.text)
        doc_lengths[chunk.chunk_id] = len(tokens)
        for term, tf in Counter(tokens).items():
            postings.setdefault(term, []).append(Posting(chunk_id=chunk.chunk_id, tf=tf))

    for term in postings:
        postings[term].sort(key=lambda posting: posting.chunk_id)

    chunk_ids = tuple(chunk.chunk_id for chunk in tiny_chunks)
    avgdl = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 0.0

    artifact = IndexArtifact(
        schema_version=1,
        corpus_version="fixture-corpus",
        tokenizer_version="1",
        chunk_count=len(tiny_chunks),
        avgdl=avgdl,
        chunk_ids=chunk_ids,
        postings=postings,
        doc_lengths=doc_lengths,
    )
    by_id = {chunk.chunk_id: chunk for chunk in tiny_chunks}
    return LoadedIndex(artifact=artifact, chunks=tiny_chunks, by_id=by_id)
