"""LLM client: mock mode and the OpenAI-compatible gateway.

Owner: Reach.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence

from ..config import Config

__all__ = ["stream_chat"]


async def stream_chat(
    messages: Sequence[dict[str, str]],
    config: Config,
) -> AsyncIterator[str]:
    """Stream answer text for *messages*.

    Modes (from ``config.llm_mode``):

    * ``mock`` — yield a deterministic canned answer built from the retrieved
      context, so tests, dev, and the demo never touch the network.
    * ``gateway`` — ``POST {gateway_url}/v1/chat/completions`` with
      ``Authorization: Bearer $RAYU_BOT_API_KEY``, ``model``, ``temperature``
      0.2, ``max_tokens`` 900 and ``stream: true``; yield text deltas parsed
      from the SSE response.

    Raises ``NotImplementedError`` today because the body is not written yet.

    TODO(Reach): implement mock and gateway streaming.
    """

    raise NotImplementedError("TODO(Reach): implement stream_chat")
    yield ""  # pragma: no cover - makes this an async generator
