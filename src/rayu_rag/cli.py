"""Command-line interface for the RayuCode RAG assistant.

All subcommand handlers import their implementation lazily, inside the handler.
That keeps ``python -m rayu_rag --help`` working even when a member-owned
module is still a stub or has missing optional dependencies.
"""

from __future__ import annotations

import argparse
import inspect
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from . import __version__
from .config import Config
from .io import read_json, read_jsonl, sha256_file, write_json

DEFAULT_SOURCE_COMMIT = "486bab47797719a893e6aae9b9363460cd7f9cce"

Handler = Callable[[argparse.Namespace, Config], int]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _as_path(value: str | Path | None, fallback: Path) -> Path:
    return Path(value) if value is not None else fallback


def _require_file(path: Path, hint: str) -> bool:
    if path.exists():
        return True
    print(f"error: missing {path}; {hint}", file=sys.stderr)
    return False


def _jsonable(value: Any) -> Any:
    """Best-effort conversion of a report object to plain JSON data."""

    if is_dataclass(value) and not isinstance(value, type):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _supported_kwargs(fn: Callable[..., Any], candidates: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    """Select keyword arguments that *fn* actually accepts.

    ``candidates`` is an ordered list of ``(name, value)`` pairs. The first name
    in each conceptual group wins, so callers should pass aliases in priority
    order and accept that only one is forwarded. If the callable takes
    ``**kwargs`` every candidate is forwarded.
    """

    try:
        parameters = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return dict(candidates)

    accepts_var_kwargs = any(
        param.kind is inspect.Parameter.VAR_KEYWORD for param in parameters.values()
    )
    if accepts_var_kwargs:
        return dict(candidates)

    selected: dict[str, Any] = {}
    for name, value in candidates:
        if name in parameters and name not in selected:
            selected[name] = value
    return selected


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


def _cmd_prepare(args: argparse.Namespace, config: Config) -> int:
    from .corpus.manifest import build_manifest
    from .corpus.prepare import prepare_corpus

    docs_dir = _as_path(args.docs_dir, config.docs_dir)
    out_dir = _as_path(args.out_dir, config.corpus_dir)

    if not docs_dir.is_dir():
        print(f"error: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    docs, chunks = prepare_corpus(docs_dir, out_dir)

    source_commit = os.environ.get("RAYU_DOCS_SOURCE_COMMIT", DEFAULT_SOURCE_COMMIT)
    manifest = build_manifest(docs_dir, docs, chunks, source_commit=source_commit)
    write_json(out_dir / "manifest.json", _jsonable(manifest))

    print(f"{len(docs)} docs, {len(chunks)} chunks")
    return 0


def _cmd_build_index(args: argparse.Namespace, config: Config) -> int:
    from .indexing.builder import build_index
    from .indexing.store import write_index
    from .io import chunk_from_dict

    chunks_path = _as_path(args.chunks, config.corpus_dir / "chunks.jsonl")
    manifest_path = _as_path(args.manifest, config.corpus_dir / "manifest.json")
    out_dir = _as_path(args.out_dir, config.index_dir)

    if not _require_file(chunks_path, "run 'rayu-rag prepare' first"):
        return 1
    if not _require_file(manifest_path, "run 'rayu-rag prepare' first"):
        return 1

    chunks = tuple(chunk_from_dict(row) for row in read_jsonl(chunks_path))
    manifest = read_json(manifest_path)

    artifact = build_index(chunks, manifest)
    write_index(artifact, out_dir)

    index_path = out_dir / "index.json"
    digest = sha256_file(index_path) if index_path.exists() else "unavailable"
    print(f"{artifact.chunk_count} chunks, {len(artifact.postings)} terms")
    print(f"sha256(index.json) = {digest}")
    return 0


def _cmd_boolean(args: argparse.Namespace, config: Config) -> int:
    index_dir = _as_path(args.index_dir, config.index_dir)
    if not _require_file(index_dir / "index.json", "run 'rayu-rag build-index' first"):
        return 1

    from .indexing import boolean_query, load_index

    index = load_index(index_dir)
    for chunk_id in boolean_query(args.expr, index):
        print(chunk_id)
    return 0


def _cmd_retrieve(args: argparse.Namespace, config: Config) -> int:
    index_dir = _as_path(args.index_dir, config.index_dir)
    if not _require_file(index_dir / "index.json", "run 'rayu-rag build-index' first"):
        return 1

    from .ranking import build_ranker, retrieve

    index = load_index_checked(index_dir)
    ranker = build_ranker(args.ranker or config.ranker)
    result = retrieve(
        args.query,
        index,
        ranker,
        k=args.k if args.k is not None else config.top_k,
        budget_chars=config.budget_chars,
        threshold=config.refusal_threshold,
    )

    print("rank\tscore\tchunk_id\turl")
    for hit in result.hits:
        print(f"{hit.rank}\t{hit.score:.4f}\t{hit.chunk.chunk_id}\t{hit.chunk.url}")
    if result.refused:
        print("refused: no result cleared the relevance threshold", file=sys.stderr)
    return 0


def load_index_checked(index_dir: Path) -> Any:
    """Load an index artifact via the indexing package."""

    from .indexing import load_index

    return load_index(index_dir)


def _cmd_eval(args: argparse.Namespace, config: Config) -> int:
    queries_path = _as_path(args.queries, Path("eval/queries.jsonl"))
    qrels_path = _as_path(args.qrels, Path("eval/qrels.jsonl"))
    out_dir = _as_path(args.out_dir, Path("reports"))

    if not _require_file(queries_path, "provide --queries or run the evaluation seed setup"):
        return 1
    if not _require_file(qrels_path, "provide --qrels or run the evaluation seed setup"):
        return 1

    from .evaluation import evaluate, to_markdown

    ranker_name = args.ranker or config.ranker
    candidates: list[tuple[str, Any]] = [
        ("queries_path", queries_path),
        ("queries", queries_path),
        ("qrels_path", qrels_path),
        ("qrels", qrels_path),
        ("ranker", ranker_name),
        ("ranker_name", ranker_name),
        ("split", args.split),
        ("bootstrap", args.bootstrap),
        ("n_bootstrap", args.bootstrap),
        ("resamples", args.bootstrap),
        ("config", config),
        ("out_dir", out_dir),
        ("output_dir", out_dir),
    ]
    report = evaluate(**_supported_kwargs(evaluate, candidates))

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "eval.json", _jsonable(report))

    markdown = to_markdown(report)
    (out_dir / "eval.md").write_text(str(markdown).rstrip() + "\n", encoding="utf-8")

    print(f"wrote {out_dir / 'eval.json'} and {out_dir / 'eval.md'}")
    return 0


def _cmd_pool(args: argparse.Namespace, config: Config) -> int:
    out_path = _as_path(args.out, Path("eval/pools.jsonl"))
    queries_path = Path("eval/queries.jsonl")
    if not _require_file(queries_path, "provide the evaluation queries first"):
        return 1

    from .evaluation import build_pool

    candidates: list[tuple[str, Any]] = [
        ("queries_path", queries_path),
        ("queries", queries_path),
        ("index_dir", config.index_dir),
        ("depth", args.depth),
        ("random", args.random),
        ("random_per_query", args.random),
        ("out_path", out_path),
        ("out", out_path),
    ]
    rows = build_pool(**_supported_kwargs(build_pool, candidates))

    if rows is not None and not out_path.exists():
        from .io import write_jsonl

        write_jsonl(out_path, (_jsonable(row) for row in rows))
    print(f"pool written to {out_path}")
    return 0


def _cmd_answer_eval(args: argparse.Namespace, config: Config) -> int:
    from .evaluation import answer_eval

    fn = None
    for name in ("evaluate_answers", "run_answer_eval", "run"):
        candidate = getattr(answer_eval, name, None)
        if callable(candidate):
            fn = candidate
            break
    if fn is None and callable(answer_eval):
        fn = answer_eval
    if fn is None:
        raise NotImplementedError("answer-level evaluation is not implemented yet")

    report = fn(**_supported_kwargs(fn, [("n", args.n), ("config", config)]))
    if report is not None:
        write_json(Path("reports/answer-eval.json"), _jsonable(report))
        print("wrote reports/answer-eval.json")
    return 0


def _cmd_verify(args: argparse.Namespace, config: Config) -> int:
    docs_dir = _as_path(args.docs_dir, config.docs_dir)
    corpus_dir = _as_path(args.corpus_dir, config.corpus_dir)
    index_dir = _as_path(args.index_dir, config.index_dir)
    manifest_path = corpus_dir / "manifest.json"

    problems: list[str] = []
    if not docs_dir.is_dir():
        problems.append(f"docs directory not found: {docs_dir}")
    if not manifest_path.exists():
        problems.append(f"manifest not found: {manifest_path} (run 'rayu-rag prepare')")
    if not (index_dir / "index.json").exists():
        problems.append(f"index not found: {index_dir / 'index.json'} (run 'rayu-rag build-index')")

    if not problems:
        from .corpus.manifest import verify_manifest

        problems.extend(verify_manifest(docs_dir, manifest_path))

    if problems:
        print("verify: problems found")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("OK")
    return 0


def _cmd_serve(args: argparse.Namespace, config: Config) -> int:
    import uvicorn

    from .api.app import create_app

    app = create_app(config)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rayu-rag",
        description="Docs-only RAG support assistant for RayuCode.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    prepare = sub.add_parser("prepare", help="chunk frozen docs into corpus artifacts")
    prepare.add_argument("--docs-dir", default=None, help="source Markdown directory")
    prepare.add_argument("--out-dir", default=None, help="corpus artifact directory")
    prepare.set_defaults(func=_cmd_prepare)

    build_index = sub.add_parser("build-index", help="build the inverted index artifact")
    build_index.add_argument("--chunks", default=None, help="chunks.jsonl to index")
    build_index.add_argument("--out-dir", default=None, help="index artifact directory")
    build_index.add_argument("--manifest", default=None, help="corpus manifest.json")
    build_index.set_defaults(func=_cmd_build_index)

    boolean = sub.add_parser("boolean", help="run a Boolean query against the index")
    boolean.add_argument("expr", help="Boolean expression, e.g. '429 AND NOT hosted'")
    boolean.add_argument("--index-dir", default=None, help="index artifact directory")
    boolean.set_defaults(func=_cmd_boolean)

    retrieve = sub.add_parser("retrieve", help="rank chunks for a query")
    retrieve.add_argument("query", help="user query text")
    retrieve.add_argument("--index-dir", default=None, help="index artifact directory")
    retrieve.add_argument("--ranker", default=None, help="ranker name (keyword, tfidf, bm25, fusion)")
    retrieve.add_argument("--k", type=int, default=None, help="number of hits to return")
    retrieve.set_defaults(func=_cmd_retrieve)

    evaluate = sub.add_parser("eval", help="run the retrieval evaluation harness")
    evaluate.add_argument("--ranker", default=None, help="ranker name")
    evaluate.add_argument("--split", choices=("dev", "test", "all"), default="dev")
    evaluate.add_argument("--queries", default=None, help="queries JSONL path")
    evaluate.add_argument("--qrels", default=None, help="qrels JSONL path")
    evaluate.add_argument("--bootstrap", type=int, default=1000, help="bootstrap resamples")
    evaluate.add_argument("--out-dir", default=None, help="report output directory")
    evaluate.set_defaults(func=_cmd_eval)

    pool = sub.add_parser("pool", help="build the pooled judgement candidates")
    pool.add_argument("--depth", type=int, default=10, help="hits per ranker")
    pool.add_argument("--random", type=int, default=5, help="seeded random chunks per query")
    pool.add_argument("--out", default=None, help="pools JSONL output path")
    pool.set_defaults(func=_cmd_pool)

    answer_eval = sub.add_parser("answer-eval", help="score end-to-end answers")
    answer_eval.add_argument("--n", type=int, default=30, help="number of answers to score")
    answer_eval.set_defaults(func=_cmd_answer_eval)

    verify = sub.add_parser("verify", help="verify corpus and index artifacts")
    verify.add_argument("--docs-dir", default=None, help="source Markdown directory")
    verify.add_argument("--corpus-dir", default=None, help="corpus artifact directory")
    verify.add_argument("--index-dir", default=None, help="index artifact directory")
    verify.set_defaults(func=_cmd_verify)

    serve = sub.add_parser("serve", help="run the chat API and frontend")
    serve.add_argument("--host", default="127.0.0.1", help="bind host")
    serve.add_argument("--port", type=int, default=8000, help="bind port")
    serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "command", None) is None:
        parser.print_help()
        return 0

    config = Config.from_env()
    try:
        return int(args.func(args, config))
    except NotImplementedError as exc:
        message = str(exc) or "not implemented"
        print(f"not implemented: {message}", file=sys.stderr)
        return 2
