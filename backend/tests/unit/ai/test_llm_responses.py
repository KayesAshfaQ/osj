"""Provider response boundaries preserve text, errors, and cancellation."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from google.genai.errors import ClientError, ServerError
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from app.ai.llm_responses import invoke_llm, response_text
from app.core.exceptions import LLMProviderError

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("answer", "answer"),
        (["first", {"type": "text", "text": "second", "extras": {"signature": "private"}}], "firstsecond"),
        ([{"type": "thinking", "thinking": "private"}, {"type": "text", "text": "visible"}], "visible"),
        ([{"type": "text", "text": "private", "thought": True}], ""),
        ([{"type": "image", "url": "private"}, {"type": "text", "text": 123}], ""),
        ([], ""),
        (None, ""),
    ],
)
def test_response_text_only_extracts_visible_text(content: object, expected: str) -> None:
    assert response_text(SimpleNamespace(content=content)) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [400, 401, 403, 404, 429, 500, 503])
@pytest.mark.parametrize("wrapped", [False, True])
async def test_google_errors_normalize_without_sensitive_message(code: int, wrapped: bool) -> None:
    upstream = (ClientError if code < 500 else ServerError)(code, {"error": {"message": "private upstream payload"}})
    error: Exception = upstream
    if wrapped:
        error = ChatGoogleGenerativeAIError("private wrapper")
        error.__cause__ = upstream
    provider = AsyncMock()
    provider.ainvoke.side_effect = error
    with pytest.raises(LLMProviderError) as captured:
        await invoke_llm(provider, [HumanMessage(content="sanitized")])
    assert captured.value.status_code == code
    assert "private" not in str(captured.value)
    provider.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancellation_is_not_normalized() -> None:
    provider = AsyncMock()
    provider.ainvoke.side_effect = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        await invoke_llm(provider, [])


@pytest.mark.asyncio
async def test_sync_provider_still_works() -> None:
    class Provider:
        def invoke(self, messages: object) -> AIMessage:
            return AIMessage(content="answer")

    assert response_text(await invoke_llm(Provider(), [])) == "answer"
