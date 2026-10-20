"""Retrieval routing and deadline regressions, without live services."""

from __future__ import annotations

import asyncio

import pytest
from langchain_core.documents import Document

from app.ai.retrieval_executor import RetrievalExecutor
from app.modules.chat.workflows.graph import retrieve_hybrid_node
from tests.fakes import make_evidence_doc

pytestmark = pytest.mark.unit


class Retriever:
    def invoke(self, query: str) -> list[Document]:
        return [make_evidence_doc()]


@pytest.mark.asyncio
async def test_mixed_collections_keep_available_statutory_evidence(retrieval_executor: RetrievalExecutor) -> None:
    result = await retrieve_hybrid_node(
        {"query": "Which statutes and cases govern arrest?", "collections": ["statutory_law", "case_law"]},
        Retriever(),
        retrieval_executor=retrieval_executor,
    )
    assert result["retrieved_chunks"]


@pytest.mark.asyncio
async def test_parent_hydration_obeys_request_deadline(retrieval_executor: RetrievalExecutor) -> None:
    class Parents:
        async def get_parents(self, keys: object) -> dict[object, object]:
            await asyncio.sleep(0.04)
            return {}

    with pytest.raises(TimeoutError):
        await retrieve_hybrid_node(
            {"query": "Section 54?", "deadline": asyncio.get_running_loop().time() + 0.01},
            Retriever(),
            Parents(),
            retrieval_executor=retrieval_executor,
        )


@pytest.mark.asyncio
async def test_cancelled_requests_keep_sync_worker_capacity_reserved(retrieval_executor: RetrievalExecutor) -> None:
    import threading

    release = threading.Event()
    four_started = asyncio.Event()
    loop = asyncio.get_running_loop()
    started = 0
    lock = threading.Lock()

    class BlockingRetriever:
        def invoke(self, query: str) -> list[Document]:
            nonlocal started
            with lock:
                started += 1
                if started == 4:
                    loop.call_soon_threadsafe(four_started.set)
            if not release.wait(2):
                raise TimeoutError("test did not release sync worker")
            return []

    retriever = BlockingRetriever()
    tasks = [
        asyncio.create_task(
            retrieve_hybrid_node({"query": "Section 54?"}, retriever, retrieval_executor=retrieval_executor)
        )
        for _ in range(4)
    ]
    fifth = None
    try:
        await asyncio.wait_for(four_started.wait(), 1)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        fifth = asyncio.create_task(
            retrieve_hybrid_node({"query": "Section 54?"}, retriever, retrieval_executor=retrieval_executor)
        )
        await asyncio.sleep(0.02)
        assert started == 4
    finally:
        release.set()
        await asyncio.gather(*tasks, *([fifth] if fifth else []), return_exceptions=True)


@pytest.mark.parametrize("collections", [["case_law"], ["special_laws"], ["case_law", "special_laws"]])
@pytest.mark.asyncio
async def test_unsupported_only_collections_do_not_search(collections: list[str]) -> None:
    result = await retrieve_hybrid_node({"query": "Which cases?", "collections": collections})
    assert result == {"retrieved_chunks": []}


@pytest.mark.asyncio
async def test_node_budget_caps_later_request_deadline(
    retrieval_executor: RetrievalExecutor, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.modules.chat.workflows import graph

    cancelled = asyncio.Event()

    class Parents:
        async def get_parents(self, keys: object) -> dict[object, object]:
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
            raise AssertionError("unreachable")

    monkeypatch.setattr(graph, "RETRIEVAL_TIMEOUT_SECONDS", 0.01)
    with pytest.raises(TimeoutError):
        await retrieve_hybrid_node(
            {"query": "Section 54?", "deadline": asyncio.get_running_loop().time() + 5},
            Retriever(),
            Parents(),
            retrieval_executor=retrieval_executor,
        )
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_fusion_is_also_bounded(retrieval_executor: RetrievalExecutor, monkeypatch: pytest.MonkeyPatch) -> None:
    import threading

    from app.modules.chat.workflows import graph

    release = threading.Event()
    started = asyncio.Event()
    loop = asyncio.get_running_loop()

    def fusion(*args: object, **kwargs: object) -> list[Document]:
        loop.call_soon_threadsafe(started.set)
        if not release.wait(2):
            raise TimeoutError("test did not release fusion")
        return []

    monkeypatch.setattr(graph, "reciprocal_rank_fusion", fusion)
    task = asyncio.create_task(
        retrieve_hybrid_node(
            {"query": "Section 54?", "deadline": loop.time() + 0.05},
            Retriever(),
            retrieval_executor=retrieval_executor,
        )
    )
    try:
        await asyncio.wait_for(started.wait(), 1)
        with pytest.raises(TimeoutError):
            await task
    finally:
        release.set()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_expired_deadline_does_not_submit_sync_retrieval(retrieval_executor: RetrievalExecutor) -> None:
    called = False

    class ForbiddenRetriever:
        def invoke(self, query: str) -> list[Document]:
            nonlocal called
            called = True
            return []

    with pytest.raises(TimeoutError):
        await retrieve_hybrid_node(
            {"query": "Section 54?", "deadline": asyncio.get_running_loop().time() - 1},
            ForbiddenRetriever(),
            retrieval_executor=retrieval_executor,
        )
    assert not called
