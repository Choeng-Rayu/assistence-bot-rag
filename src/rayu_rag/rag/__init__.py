"""Retrieval-augmented generation: prompt, LLM client, stream, citations, refusal.

Owner: Reach. Every algorithm in this package is a scaffold stub that raises
:class:`NotImplementedError` with a ``TODO(Reach)`` message until P5 lands.
The ``SYSTEM_PROMPT`` and ``CANONICAL_FACTS`` strings are verbatim data.
"""

from __future__ import annotations

from .citations import extract_citations, source_pills
from .llm import stream_chat
from .prompt import build_messages, build_retrieval_query, docs_block
from .refusal import calibrate_threshold, should_refuse
from .stream import parse_openai_sse

__all__ = [
    "build_messages",
    "build_retrieval_query",
    "calibrate_threshold",
    "docs_block",
    "extract_citations",
    "parse_openai_sse",
    "should_refuse",
    "source_pills",
    "stream_chat",
]
