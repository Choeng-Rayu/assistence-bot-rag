"""Foundation tests: frozen contracts, canonical IO, config, and CLI skeleton."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from rayu_rag import io
from rayu_rag.config import Config
from rayu_rag.contracts import (
    SCHEMA_VERSION,
    ChatMessage,
    Chunk,
    Citation,
    DocumentMeta,
    IndexArtifact,
    LoadedIndex,
    Posting,
    Ranker,
    RetrievalResult,
    ScoredChunk,
    SourceRef,
)

ENV_VARS = (
    "RAYU_BOT_GATEWAY_URL",
    "RAYU_BOT_API_KEY",
    "RAYU_BOT_MODEL",
    "RAYU_RAG_LLM",
    "RAYU_RAG_RANKER",
    "RAYU_RAG_DEBUG",
    "RAYU_RAG_REFUSAL_THRESHOLD",
    "RAYU_DOCS_SITE_BASE",
)


@pytest.fixture()
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


# ---------------------------------------------------------------------------
# contracts
# ---------------------------------------------------------------------------


def test_schema_version() -> None:
    assert SCHEMA_VERSION == 1


def test_chunk_contract_shape(tiny_chunks: tuple[Chunk, ...]) -> None:
    chunk = tiny_chunks[1]
    assert isinstance(chunk, Chunk)
    assert chunk.chunk_id == "tiny-a#install"
    assert chunk.heading_path == ("Tiny A", "Install")
    assert chunk.source_type == "docs"
    assert isinstance(chunk.heading_path, tuple)


def test_chunk_is_frozen(tiny_chunks: tuple[Chunk, ...]) -> None:
    chunk = tiny_chunks[0]
    with pytest.raises(FrozenInstanceError):
        chunk.title = "mutated"  # type: ignore[misc]


def test_loaded_index_contract(tiny_loaded_index: LoadedIndex) -> None:
    assert isinstance(tiny_loaded_index, LoadedIndex)
    assert isinstance(tiny_loaded_index.artifact, IndexArtifact)
    assert tiny_loaded_index.artifact.schema_version == SCHEMA_VERSION
    assert tiny_loaded_index.artifact.chunk_count == len(tiny_loaded_index.chunks)
    assert set(tiny_loaded_index.by_id) == {chunk.chunk_id for chunk in tiny_loaded_index.chunks}
    assert isinstance(tiny_loaded_index.artifact.postings["install"][0], Posting)
    # postings are sorted by chunk_id
    for postings in tiny_loaded_index.artifact.postings.values():
        assert [posting.chunk_id for posting in postings] == sorted(
            posting.chunk_id for posting in postings
        )

    with pytest.raises(FrozenInstanceError):
        tiny_loaded_index.chunks = ()  # type: ignore[misc]


def test_scored_chunk_and_result_contract(tiny_chunks: tuple[Chunk, ...]) -> None:
    scored = ScoredChunk(
        chunk=tiny_chunks[0],
        score=2.5,
        rank=1,
        components={"keyword": 2.5},
    )
    result = RetrievalResult(
        query="install rayu",
        normalized_terms=("install", "rayu"),
        hits=(scored,),
        refused=False,
        used_fallback=False,
        diagnostics={"k": 1},
    )

    assert result.hits[0].chunk is tiny_chunks[0]
    assert result.hits[0].rank == 1
    assert result.diagnostics["k"] == 1
    assert result.used_fallback is False

    with pytest.raises(FrozenInstanceError):
        scored.score = 3.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.refused = True  # type: ignore[misc]


def test_ranker_protocol_shape() -> None:
    assert "name" in Ranker.__annotations__
    assert callable(Ranker.rank)


def test_message_and_reference_contracts() -> None:
    message = ChatMessage(role="user", content="hello")
    source = SourceRef(title="Install", url="/docs/tiny-a#install", chunk_id="tiny-a#install")
    citation = Citation(marker=1, chunk_id="tiny-a#install", url="/docs/tiny-a#install", title="Install")

    assert message.role == "user"
    assert source.chunk_id == citation.chunk_id

    with pytest.raises(FrozenInstanceError):
        message.content = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# io
# ---------------------------------------------------------------------------


def test_canonical_json_is_sorted_and_compact() -> None:
    text = io.canonical_json({"b": 1, "a": [1, 2], "c": "héllo"})
    assert text == '{"a":[1,2],"b":1,"c":"héllo"}'
    assert " " not in text


def test_chunk_dict_round_trip(tiny_chunks: tuple[Chunk, ...]) -> None:
    expected_keys = {
        "chunk_id",
        "slug",
        "title",
        "heading",
        "heading_path",
        "url",
        "text",
        "char_len",
        "token_count",
        "part_index",
        "order",
        "source_type",
    }
    for chunk in tiny_chunks:
        row = io.chunk_to_dict(chunk)
        assert set(row) == expected_keys
        assert isinstance(row["heading_path"], list)
        assert io.chunk_from_dict(row) == chunk
        assert isinstance(io.chunk_from_dict(row).heading_path, tuple)


def test_document_meta_round_trip() -> None:
    meta = DocumentMeta(
        slug="tiny-a",
        title="Tiny A",
        source_path="tests/fixtures/docs/tiny-a.md",
        source_url="/docs/tiny-a",
        sha256="0" * 64,
        char_count=163,
        word_count=26,
        heading_count=3,
        chunk_count=2,
    )
    row = io.document_to_dict(meta)
    assert row["slug"] == "tiny-a"
    assert row["source_type"] == "docs"
    assert io.document_from_dict(row) == meta


def test_write_and_read_json(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "data.json"
    io.write_json(path, {"b": 2, "a": 1})
    assert path.read_text(encoding="utf-8") == '{"a":1,"b":2}\n'
    assert io.read_json(path) == {"a": 1, "b": 2}


def test_write_and_read_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    rows = [{"b": 2, "a": 1}, {"a": 3}]
    io.write_jsonl(path, rows)
    assert path.read_text(encoding="utf-8") == '{"a":1,"b":2}\n{"a":3}\n'
    assert io.read_jsonl(path) == rows


def test_sha256_helpers(tmp_path: Path) -> None:
    assert (
        io.sha256_text("abc")
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    path = tmp_path / "abc.bin"
    path.write_bytes(b"abc")
    assert io.sha256_file(path) == io.sha256_text("abc")


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


def test_config_defaults(clean_env: None) -> None:
    config = Config.from_env()
    assert config.docs_dir == Path("data/docs")
    assert config.artifacts_dir == Path("artifacts")
    assert config.corpus_dir == Path("artifacts/corpus")
    assert config.index_dir == Path("artifacts/index")
    assert config.gateway_url == "https://gateway.rayucode.com"
    assert config.bot_api_key is None
    assert config.model == "deepseek-v4.1-flash-cloud"
    assert config.llm_mode == "mock"
    assert config.ranker == "keyword"
    assert config.top_k == 5
    assert config.budget_chars == 6000
    assert config.refusal_threshold is None
    assert config.max_turns == 12
    assert config.max_turn_chars == 2000
    assert config.max_total_chars == 8000
    assert config.retrieval_user_turns == 2
    assert config.retrieval_max_chars == 600
    assert config.max_sources == 4
    assert config.docs_site_base == "https://rayucode.com"
    assert config.debug is False
    assert (config.ip_window_limit, config.ip_window_minutes) == (6, 10)
    assert (config.ip_daily_limit, config.global_daily_limit) == (50, 500)


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAYU_BOT_API_KEY", "test-key")
    monkeypatch.setenv("RAYU_BOT_GATEWAY_URL", "https://gateway.example.test")
    monkeypatch.setenv("RAYU_BOT_MODEL", "test-model")
    monkeypatch.setenv("RAYU_RAG_LLM", "mock")
    monkeypatch.setenv("RAYU_RAG_RANKER", "bm25")
    monkeypatch.setenv("RAYU_RAG_DEBUG", "1")
    monkeypatch.setenv("RAYU_RAG_REFUSAL_THRESHOLD", "0.25")
    monkeypatch.setenv("RAYU_DOCS_SITE_BASE", "https://docs.example.test")

    config = Config.from_env()
    assert config.bot_api_key == "test-key"
    assert config.gateway_url == "https://gateway.example.test"
    assert config.model == "test-model"
    assert config.llm_mode == "mock"
    assert config.ranker == "bm25"
    assert config.debug is True
    assert config.refusal_threshold == 0.25
    assert config.docs_site_base == "https://docs.example.test"


def test_llm_mode_auto_selects_gateway_with_key(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAYU_BOT_API_KEY", "test-key")
    assert Config.from_env().llm_mode == "gateway"
    monkeypatch.delenv("RAYU_BOT_API_KEY")
    assert Config.from_env().llm_mode == "mock"


def test_config_is_frozen(clean_env: None) -> None:
    config = Config()
    with pytest.raises(FrozenInstanceError):
        config.top_k = 10  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CLI skeleton (lazy imports)
# ---------------------------------------------------------------------------


def test_cli_help_exits_zero() -> None:
    from rayu_rag.cli import main

    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0


def test_cli_version_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    from rayu_rag.cli import main

    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert "rayu-rag" in capsys.readouterr().out


def test_cli_missing_index_returns_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from rayu_rag.cli import main

    code = main(["retrieve", "install", "--index-dir", str(tmp_path / "missing")])
    assert code == 1
    assert "missing" in capsys.readouterr().err
