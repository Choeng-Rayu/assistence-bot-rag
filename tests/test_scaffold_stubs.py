"""Scaffold guarantees: imports, owner-tagged stubs, and the frozen corpus.

Fast and network-free. These tests describe the project *setup*, not any
algorithm: every member function must still raise ``NotImplementedError`` with a
``TODO(<Owner>)`` message until its owner fills it in.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src" / "rayu_rag"
DOCS_DIR = REPO_ROOT / "data" / "docs"

OWNER_RE = re.compile(r"TODO\((Rayu|Nike|Somnang|Tanchhay|Reach)\)")

EXPECTED_DOCS = {
    "01-installation.md",
    "02-quickstart.md",
    "03-providers.md",
    "04-models.md",
    "05-configuration.md",
    "06-cli-reference.md",
    "07-slash-commands.md",
    "10-troubleshooting.md",
    "15-api-keys.md",
    "17-vscode-extension.md",
    "18-subscription-plans.md",
    "19-credits-and-limits.md",
    "20-how-token-credit-charge.md",
    "21-policies.md",
}

SUBPACKAGES = (
    "rayu_rag.corpus",
    "rayu_rag.indexing",
    "rayu_rag.ranking",
    "rayu_rag.rag",
    "rayu_rag.api",
    "rayu_rag.evaluation",
)

#: Representative stubs that should still raise ``NotImplementedError``.
REPRESENTATIVE_STUBS = (
    (
        "ranking",
        lambda: __import__("rayu_rag.ranking", fromlist=["build_ranker"]).build_ranker("keyword"),
        "Tanchhay",
    ),
    (
        "rag",
        lambda: __import__("rayu_rag.rag", fromlist=["build_messages"]).build_messages((), ()),
        "Reach",
    ),
    ("api", lambda: __import__("rayu_rag.api", fromlist=["create_app"]).create_app(), "Reach"),
    (
        "evaluation",
        lambda: __import__("rayu_rag.evaluation", fromlist=["precision_at_k"]).precision_at_k(
            [], set(), 1
        ),
        "Tanchhay",
    ),
)


@pytest.mark.parametrize("module_name", ("rayu_rag",) + SUBPACKAGES)
def test_package_imports(module_name: str) -> None:
    module = __import__(module_name, fromlist=["__name__"])
    assert module.__name__ == module_name


@pytest.mark.parametrize(("package", "call", "owner"), REPRESENTATIVE_STUBS)
def test_representative_stub_raises_with_owner(package: str, call, owner: str) -> None:
    with pytest.raises(NotImplementedError) as excinfo:
        call()
    message = str(excinfo.value)
    match = OWNER_RE.search(message)
    assert match is not None, f"{package} stub message lacks TODO(owner): {message!r}"
    assert match.group(1) == owner


def _iter_subpackage_sources() -> list[Path]:
    files: list[Path] = []
    for package in SUBPACKAGES:
        directory = SRC_ROOT / package.rsplit(".", 1)[-1]
        files.extend(sorted(directory.rglob("*.py")))
    return files


def test_every_not_implemented_error_is_owner_tagged() -> None:
    """Every ``raise NotImplementedError(...)`` under the subpackages is tagged."""

    files = _iter_subpackage_sources()
    assert files, "no subpackage sources found"

    tagged = 0
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise):
                continue
            exc = node.exc
            if not isinstance(exc, ast.Call):
                continue
            func = exc.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if name != "NotImplementedError":
                continue
            assert exc.args, f"{path}:{node.lineno} has no message"
            arg = exc.args[0]
            assert isinstance(arg, ast.Constant) and isinstance(arg.value, str), (
                f"{path}:{node.lineno} must use a literal string message"
            )
            assert OWNER_RE.search(arg.value), (
                f"{path}:{node.lineno} message is not TODO(owner): {arg.value!r}"
            )
            tagged += 1

    assert tagged >= len(SUBPACKAGES) * 3, "expected many owner-tagged stubs"


def test_each_subpackage_has_owner_tagged_stubs() -> None:
    for package in SUBPACKAGES:
        directory = SRC_ROOT / package.rsplit(".", 1)[-1]
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(directory.rglob("*.py"))
        )
        assert "NotImplementedError" in text, f"{package} has no stubs"
        assert OWNER_RE.search(text), f"{package} has no owner-tagged TODO"


def test_frozen_corpus_has_14_docs() -> None:
    docs = sorted(
        path.name for path in DOCS_DIR.glob("*.md") if path.name != "README.md"
    )
    assert len(docs) == 14, docs
    assert set(docs) == EXPECTED_DOCS


def test_corpus_readme_exists() -> None:
    readmes = [path.name for path in DOCS_DIR.iterdir() if path.name.startswith("README")]
    assert readmes, "data/docs must carry a provenance README"
    text = (DOCS_DIR / readmes[0]).read_text(encoding="utf-8")
    assert "486bab47797719a893e6aae9b9363460cd7f9cce" in text
    assert "Choeng-Rayu/rayu-web" in text


def test_doc_titles_are_frozen() -> None:
    from rayu_rag.corpus.titles import DOC_TITLES, doc_title

    assert len(DOC_TITLES) == 14
    assert doc_title("21-policies", "fallback") == "Policies"
    assert doc_title("19-credits-and-limits", "fallback") == "Credits and limits"
    assert doc_title("does-not-exist", "fallback") == "fallback"


def test_shared_interfaces_are_exported() -> None:
    from rayu_rag.api import create_app
    from rayu_rag.corpus import prepare_corpus
    from rayu_rag.indexing import load_index
    from rayu_rag.rag import build_messages
    from rayu_rag.ranking import Ranker, retrieve

    assert callable(prepare_corpus)
    assert callable(load_index)
    assert callable(retrieve)
    assert callable(build_messages)
    assert callable(create_app)
    assert "rank" in Ranker.__dict__ or callable(Ranker.rank)
