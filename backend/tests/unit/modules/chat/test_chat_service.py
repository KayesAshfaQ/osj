"""Unit tests for ChatService: input sanitization, workflow execution, error mapping, and observability."""

from __future__ import annotations

import asyncio
import logging

import httpx
import pytest
from fastapi import HTTPException
from groq import RateLimitError

from app.ai.llm_factory import LLMConfigurationError
from app.modules.chat.service import ChatService
from app.modules.chat.sessions import AnonymousSessions
from tests.fakes import FakeRedis, make_evidence_doc

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_workflow_deadline_includes_session_history_time(fake_redis: FakeRedis) -> None:
    history_started: list[float] = []
    workflow_budgets: list[float] = []

    class SlowHistorySessions(AnonymousSessions):
        async def history(self, token: str) -> list[dict[str, str]]:
            history_started.append(asyncio.get_running_loop().time())
            await asyncio.sleep(0.05)
            return await super().history(token)

    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            deadline = state["deadline"]
            assert isinstance(deadline, float)
            workflow_budgets.append(deadline - history_started[0])
            return {"generated_answer": "", "generated_sources": [], "retry_count": 2}

    sessions = SlowHistorySessions(fake_redis)
    issued = await sessions.issue()
    service = ChatService(Workflow(), sessions=sessions)

    await service.answer("Section 54?", token=issued.token, admitted=True)

    assert 29.0 <= workflow_budgets[0] <= 30.01


@pytest.mark.asyncio
async def test_delivery_checks_injected_workflow_and_sanitizes_input() -> None:
    class Workflow:
        query = ""

        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            self.query = str(state["query"])
            return {"generated_answer": "UNVERIFIED", "is_citation_valid": False}

    workflow = Workflow()
    service = ChatService(workflow=workflow)
    answer = await service.answer("email: person@example.com phone: 01712345678")
    assert "UNVERIFIED" not in answer.answer
    assert "person@example.com" not in workflow.query
    assert "01712345678" not in workflow.query
    assert workflow.query


@pytest.mark.asyncio
async def test_delivery_does_not_trust_workflow_valid_flag() -> None:
    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            return {"generated_answer": "UNVERIFIED", "is_citation_valid": True, "outcome": "answered"}

    answer = await ChatService(Workflow()).answer("Section 54?")
    assert "UNVERIFIED" not in answer.answer


@pytest.mark.asyncio
async def test_provider_configuration_failure_maps_to_503() -> None:
    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            raise LLMConfigurationError("synthetic missing key")

    with pytest.raises(HTTPException) as captured:
        await ChatService(Workflow()).answer("Section 54?")
    assert captured.value.status_code == 503
    assert captured.value.detail == "Chat provider unavailable"


@pytest.mark.asyncio
async def test_transient_provider_error_maps_to_503() -> None:
    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            raise httpx.ConnectError("Connection refused by upstream provider")

    with pytest.raises(HTTPException) as captured:
        await ChatService(Workflow()).answer("Section 54?")
    assert captured.value.status_code == 503
    assert captured.value.detail == "Chat provider unavailable"


@pytest.mark.asyncio
async def test_provider_rate_limit_maps_to_actionable_429() -> None:
    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            response = httpx.Response(
                429, request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
            )
            raise RateLimitError("private upstream message", response=response, body=None)

    with pytest.raises(HTTPException) as captured:
        await ChatService(Workflow()).answer("Section 54?")
    assert captured.value.status_code == 429
    assert captured.value.detail == "Chat provider rate limit exceeded; try again shortly"


@pytest.mark.asyncio
async def test_lease_released_when_answer_is_cancelled(fake_redis: FakeRedis) -> None:
    sessions = AnonymousSessions(fake_redis)
    issued = await sessions.issue()

    class StallingWorkflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            await asyncio.sleep(5)
            return {"generated_answer": "done", "retrieved_chunks": []}

    service = ChatService(workflow=StallingWorkflow(), sessions=sessions)
    task = asyncio.create_task(service.answer("Section 54?", token=issued.token))
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    new_lease = await sessions.begin(issued.token)
    assert new_lease is not None


@pytest.mark.asyncio
async def test_observability_counters_and_sanitized_logs(
    fake_redis: FakeRedis, caplog: pytest.LogCaptureFixture
) -> None:
    sessions = AnonymousSessions(fake_redis)
    issued = await sessions.issue()

    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            return {
                "generated_answer": "Section 54 of the Code of Criminal Procedure, police may arrest.",
                "generated_sources": [
                    {"source_id": "crpc", "act_title": "Code of Criminal Procedure", "section_number": "54"}
                ],
                "retrieved_chunks": [make_evidence_doc()],
                "retry_count": 0,
            }

    service = ChatService(workflow=Workflow(), sessions=sessions)
    with caplog.at_level(logging.INFO):
        answer = await service.answer("secret user query about Section 54", token=issued.token)
    assert answer.outcome == "answered"
    assert service.metrics.answered_total >= 1
    for record in caplog.records:
        assert "secret user query" not in record.message
        assert issued.token not in record.message


@pytest.mark.asyncio
@pytest.mark.parametrize(("upstream_code", "http_code"), [(429, 429), (400, 503), (401, 503), (503, 503)])
async def test_normalized_provider_failure_maps_to_existing_contract(upstream_code: int, http_code: int) -> None:
    from app.core.exceptions import LLMProviderError

    class Workflow:
        async def ainvoke(self, state: dict[str, object]) -> dict[str, object]:
            raise LLMProviderError(status_code=upstream_code)

    service = ChatService(Workflow())
    with pytest.raises(HTTPException) as captured:
        await service.answer("Section 54?")
    assert captured.value.status_code == http_code
    assert service.metrics.provider_failure_total == 1
