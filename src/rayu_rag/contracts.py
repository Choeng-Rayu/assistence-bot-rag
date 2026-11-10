"""Frozen data contracts shared by every :mod:`rayu_rag` component.

These types are the only agreement between the corpus, indexing, ranking,
evaluation, RAG, and API modules. They are intentionally stdlib-only and
``frozen``/``slots`` so that consumers can rely on them without importing
heavy dependencies (FastAPI, httpx, ...).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol, TypedDict

SCHEMA_VERSION = 1

SourceType = Literal["docs", "web"]
Role = Literal["user", "assistant"]


@dataclass(frozen=True, slots=True)
class DocumentMeta:
    """One source document in the frozen corpus."""

    slug: str
    title: str
    source_path: str
    source_url: str
    sha256: str
    char_count: int
    word_count: int
    heading_count: int
    chunk_count: int
    source_type: SourceType = "docs"


@dataclass(frozen=True, slots=True)
class Chunk:
    """A retrievable, citable unit of a document."""

    chunk_id: str
    slug: str
    title: str
    heading: str
    heading_path: tuple[str, ...]
    url: str
    text: str
    char_len: int
    token_count: int
    part_index: int
    order: int
    source_type: SourceType = "docs"


@dataclass(frozen=True, slots=True)
class Posting:
    """A single term occurrence entry in the inverted index."""

    chunk_id: str
    tf: int


#: term -> postings sorted by chunk_id
Postings = dict[str, list[Posting]]


@dataclass(frozen=True, slots=True)
class IndexArtifact:
    """Serializable inverted index artifact (artifacts/index/index.json)."""

    schema_version: int
    corpus_version: str
    tokenizer_version: str
    chunk_count: int
    avgdl: float
    chunk_ids: tuple[str, ...]
    postings: Postings
    doc_lengths: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class LoadedIndex:
    """An index artifact with its chunks materialized for retrieval."""

    artifact: IndexArtifact
    chunks: tuple[Chunk, ...]
    by_id: Mapping[str, Chunk]


@dataclass(frozen=True, slots=True)
class ScoredChunk:
    """A chunk ranked for a query, with per-component score breakdown."""

    chunk: Chunk
    score: float
    rank: int
    components: Mapping[str, float]


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """The full result of a retrieval call, including refusal diagnostics."""

    query: str
    normalized_terms: tuple[str, ...]
    hits: tuple[ScoredChunk, ...]
    refused: bool
    used_fallback: bool
    diagnostics: Mapping[str, Any]


class Ranker(Protocol):
    """Anything that can score chunks for a query."""

    name: str

    def rank(self, query: str, index: LoadedIndex, k: int = 10) -> list[ScoredChunk]: ...


@dataclass(frozen=True, slots=True)
class ChatMessage:
    """One conversation turn."""

    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class SourceRef:
    """A unique source pill shown to the user."""

    title: str
    url: str
    chunk_id: str


@dataclass(frozen=True, slots=True)
class Citation:
    """A numeric citation marker mapped back to a retrieved chunk."""

    marker: int
    chunk_id: str
    url: str
    title: str


class SourcesEvent(TypedDict):
    type: Literal["sources"]
    sources: list[dict]


class DeltaEvent(TypedDict):
    type: Literal["delta"]
    text: str


class DoneEvent(TypedDict):
    type: Literal["done"]


class ErrorEvent(TypedDict):
    type: Literal["error"]
    code: str
    message: str


ChatEvent = SourcesEvent | DeltaEvent | DoneEvent | ErrorEvent
