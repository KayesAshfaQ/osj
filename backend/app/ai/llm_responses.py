"""Text and error boundaries shared by provider-backed inference callers."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import cast

from google.genai.errors import APIError
from langchain_core.messages import BaseMessage
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from app.core.exceptions import LLMProviderError


def response_text(response: object) -> str:
    """Extract visible text without serializing reasoning or provider metadata."""
    content: object = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in cast(list[object], content):
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            item = cast(dict[str, object], block)
            text = item.get("text")
            if item.get("type") == "text" and not item.get("thought") and isinstance(text, str):
                parts.append(text)
    return "".join(parts)


async def invoke_llm(llm: object, messages: Sequence[BaseMessage]) -> object:
    """Invoke inside the caller's deadline, normalizing only Google SDK errors."""
    try:
        if hasattr(llm, "ainvoke"):
            return await cast(Callable[[list[BaseMessage]], Awaitable[object]], getattr(llm, "ainvoke"))(list(messages))
        return await asyncio.to_thread(
            cast(Callable[[list[BaseMessage]], object], getattr(llm, "invoke")), list(messages)
        )
    except (APIError, ChatGoogleGenerativeAIError) as exc:
        # LangChain wraps client errors and preserves the SDK error as the cause.
        upstream = exc if isinstance(exc, APIError) else exc.__cause__
        status_code = upstream.code if isinstance(upstream, APIError) else None
        raise LLMProviderError(status_code=status_code) from exc
