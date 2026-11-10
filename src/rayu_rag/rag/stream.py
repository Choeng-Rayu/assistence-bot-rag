"""Parse OpenAI-style SSE into chat events.

Owner: Reach.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from ..contracts import ChatEvent

__all__ = ["parse_openai_sse"]


async def parse_openai_sse(chunks: AsyncIterator[bytes]) -> AsyncIterator[ChatEvent]:
    """Parse an OpenAI-compatible SSE byte stream into :data:`ChatEvent`s.

    Behaviour to implement (port of ``lib/supportBot/stream.ts``):

    * buffer across arbitrary network chunk splits, splitting on newlines;
    * ignore SSE comments and ``event:`` / ``id:`` / ``retry:`` fields;
    * ignore malformed JSON lines instead of aborting the stream;
    * stop at ``data: [DONE]``;
    * yield ``{"type": "delta", "text": ...}`` from ``choices[0].delta.content``,
      and accept a non-streaming ``choices[0].message.content`` fallback;
    * flush a final line that does not end with a newline.

    The route appends the surrounding ``sources``/``done``/``error`` events.

    TODO(Reach): implement the SSE parser.
    """

    raise NotImplementedError("TODO(Reach): implement parse_openai_sse")
    yield {"type": "done"}  # pragma: no cover - makes this an async generator
