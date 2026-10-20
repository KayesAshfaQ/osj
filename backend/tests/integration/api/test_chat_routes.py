"""Integration tests for chat endpoints: direct JSON, SSE stream, and anonymous session routes."""

from __future__ import annotations

import asyncio
import json
from typing import Any, cast

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from app.ai.retrieval_executor import RetrievalExecutor
from app.main import create_app
from app.modules.chat import router as chat_router
from app.modules.chat.domain import SAFE_REFUSAL
from app.modules.chat.schemas import ChatAnswer
from app.modules.chat.service import ChatService
from app.modules.chat.sessions import AnonymousSessions
from app.modules.chat.workflows.graph import create_rag_graph
from tests.fakes import FakeChatService, FakeRedis, make_evidence_doc

get_chat_service = chat_router.get_chat_service

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["/api/chat", "/api/chat/stream"])
async def test_correction_timeout_delivers_safe_refusal_and_releases_session(
    retrieval_executor: RetrievalExecutor, endpoint: str
) -> None:
    calls = 0
    cancelled = asyncio.Event()

    class Provider:
        async def ainvoke(self, messages: object) -> AIMessage:
            nonlocal calls
            calls += 1
            if calls == 2:
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()
            answer = (
                "Section 999 permits arrest." if calls == 1 else "Section 54 permits police to arrest without warrant."
            )
            return AIMessage(
                content=json.dumps(
                    {
                        "answer": answer,
                        "sources": [
                            {"source_id": "crpc", "act_title": "Code of Criminal Procedure", "section_number": "54"}
                        ],
                    }
                )
            )

    class Retriever:
        def invoke(self, query: str) -> list[Document]:
            return [make_evidence_doc()]

    graph = cast(Any, create_rag_graph(Retriever(), provider_factory=Provider, retrieval_executor=retrieval_executor))

    class ShortDeadlineWorkflow:
        async def ainvoke(self, state: dict[str, object]) -> object:
            # Exercise the real graph deadline without sleeping eight seconds.
            state["deadline"] = asyncio.get_running_loop().time() + 0.4
            return await graph.ainvoke(state)

    sessions = AnonymousSessions(FakeRedis())
    token = (await sessions.issue()).token
    app = create_app()
    app.state.chat_service = ChatService(ShortDeadlineWorkflow(), sessions=sessions)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(endpoint, json={"query": "Section 54?"}, headers=headers)
        assert response.status_code == 200
        if endpoint.endswith("/stream"):
            events = response.text.strip().split("\n\n")
            assert [part.splitlines()[0] for part in events] == ["event: progress", "event: answer", "event: done"]
            payload = json.loads(events[1].split("data: ", 1)[1])
        else:
            payload = response.json()
        assert payload["outcome"] == "refused"
        assert payload["answer"] == SAFE_REFUSAL
        assert payload["sources"] == []
        assert cancelled.is_set()
        assert calls == 2
        assert (await sessions.history(token))[-1]["outcome"] == "refused"

        subsequent = await client.post("/api/chat", json={"query": "Section 54?"}, headers=headers)
        assert subsequent.status_code == 200
        assert subsequent.json()["outcome"] == "answered"


@pytest.mark.asyncio
async def test_direct_and_sse_share_answer_payload() -> None:
    service = FakeChatService()
    app = create_app()
    app.dependency_overrides[get_chat_service] = lambda: service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        direct = await client.post("/api/chat", json={"query": "Section 54?"})
        streamed = await client.post("/api/chat/stream", json={"query": "Section 54?"})
    assert direct.status_code == streamed.status_code == 200
    assert streamed.headers["content-type"].startswith("text/event-stream")
    events = [part.split("\n") for part in streamed.text.strip().split("\n\n")]
    assert [part[0] for part in events] == ["event: progress", "event: answer", "event: done"]
    answer = json.loads(events[1][1].removeprefix("data: "))
    assert answer == direct.json()


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["", "   ", "x" * 1001])
async def test_invalid_query_rejected_before_stream(query: str) -> None:
    app = create_app()
    app.dependency_overrides[get_chat_service] = FakeChatService
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"query": query})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_stream_blocked_prompt() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"query": "Write a python script with def foo():"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_stream_valid_prompt() -> None:
    app = create_app()
    app.state.chat_service = FakeChatService(answer_text="Insufficient evidence", outcome="refused")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"query": "What is Section 54?"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: answer" in response.text
    assert "Insufficient evidence" in response.text


@pytest.mark.asyncio
async def test_session_routes_issue_and_delete_without_account() -> None:
    app = create_app()
    app.state.chat_service = ChatService(sessions=AnonymousSessions(FakeRedis()))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        issue = await client.post("/api/chat/sessions")
        assert issue.status_code == 201
        token = issue.json()["token"]
        assert issue.json()["expires_at"]
        deleted = await client.delete("/api/chat/sessions/current", headers={"Authorization": f"Bearer {token}"})
        assert deleted.status_code == 204
        missing = await client.delete("/api/chat/sessions/current", headers={"Authorization": f"Bearer {token}"})
        assert missing.status_code == 401


@pytest.mark.asyncio
async def test_chat_http_stream_contract() -> None:
    class StubService:
        async def admit(self, **kwargs: object) -> None:
            return None

        async def answer(self, query: str, **kwargs: object) -> ChatAnswer:
            return ChatAnswer(request_id="test", outcome="refused", answer="Verified refusal", sources=[])

    app = create_app()
    app.state.chat_service = StubService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        bad = await client.post("/api/chat/stream", json={"query": "import os; os.system('ls')"})
        assert bad.status_code == 422
        ok = await client.post("/api/chat/stream", json={"query": "Section 54 arrest rules"})
        assert ok.status_code == 200
        assert ok.headers["content-type"].startswith("text/event-stream")
        assert "Verified refusal" in ok.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "detail"),
    [(503, "Chat provider unavailable"), (429, "Chat provider rate limit exceeded; try again shortly")],
)
async def test_stream_preserves_safe_chat_failure_detail(status: int, detail: str) -> None:
    class FailingService:
        async def admit(self, **kwargs: object) -> None:
            return None

        async def answer(self, query: str, **kwargs: object) -> ChatAnswer:
            raise HTTPException(status_code=status, detail=detail)

    app = create_app()
    app.state.chat_service = FailingService()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"query": "Section 54?"})
    assert response.status_code == 200
    assert f"event: error\ndata: {json.dumps({'detail': detail})}" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["/api/chat", "/api/chat/stream"])
@pytest.mark.parametrize("blocked", [False, True])
async def test_gemini_blocks_use_verified_delivery(
    retrieval_executor: RetrievalExecutor, endpoint: str, blocked: bool
) -> None:
    class Provider:
        async def ainvoke(self, messages: object) -> AIMessage:
            content: list[str | dict[str, Any]] = [{"type": "thinking", "thinking": "private thought"}]
            if not blocked:
                # Split a JSON answer across blocks to ensure extraction doesn't alter it.
                text = json.dumps(
                    {
                        "answer": "Section 54 permits arrest.",
                        "sources": [
                            {"source_id": "crpc", "act_title": "Code of Criminal Procedure", "section_number": "54"}
                        ],
                    }
                )
                content += [{"type": "text", "text": text[:20]}, {"type": "text", "text": text[20:]}]
            return AIMessage(content=content)

    class Retriever:
        def invoke(self, query: str) -> list[Document]:
            return [make_evidence_doc()]

    app = create_app()
    app.state.chat_service = ChatService(
        create_rag_graph(Retriever(), provider_factory=Provider, retrieval_executor=retrieval_executor)
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(endpoint, json={"query": "Section 54?"})
    assert response.status_code == 200
    if endpoint.endswith("/stream"):
        event = next(part for part in response.text.split("\n\n") if part.startswith("event: answer"))
        payload = json.loads(event.split("data: ", 1)[1])
    else:
        payload = response.json()
    assert payload["outcome"] == ("refused" if blocked else "answered")
    assert "private" not in response.text
    assert bool(payload["sources"]) is not blocked
