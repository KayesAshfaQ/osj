"""Unit tests for FastAPI lifespan resource management and isolation."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import create_app

pytestmark = pytest.mark.unit


@dataclass
class FakeResources:
    name: str
    closed: bool = False

    def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_apps_have_independent_lifetimes() -> None:
    created: list[FakeResources] = []

    @asynccontextmanager
    async def factory(_app: FastAPI) -> AsyncGenerator[FakeResources, None]:
        item = FakeResources(str(len(created)))
        created.append(item)
        try:
            yield item
        finally:
            item.closed = True

    first, second = create_app(resource_factory=factory), create_app(resource_factory=factory)
    async with first.router.lifespan_context(first):
        async with second.router.lifespan_context(second):
            assert first.state.resources is not second.state.resources
            assert not created[0].closed and not created[1].closed
        assert created[1].closed and not created[0].closed
    assert created[0].closed


@pytest.mark.asyncio
async def test_partial_startup_releases_owned_resource() -> None:
    item = FakeResources("partial")

    @asynccontextmanager
    async def factory(_app: FastAPI) -> AsyncGenerator[FakeResources, None]:
        try:
            raise RuntimeError("later startup failed")
            yield item
        finally:
            item.closed = True

    app = create_app(resource_factory=factory)
    with pytest.raises(RuntimeError, match="later startup failed"):
        async with app.router.lifespan_context(app):
            pass
    assert item.closed


@pytest.mark.asyncio
async def test_default_apps_open_and_close_separate_qdrant_readers(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main

    clients: list[FakeResources] = []

    def open_reader(_settings: object) -> FakeResources:
        client = FakeResources(str(len(clients)))
        clients.append(client)
        return client

    class Manager:
        def __init__(self, *, client: FakeResources) -> None:
            self.client = client

        def as_retriever(self, *, k: int) -> FakeResources:
            return self.client

    monkeypatch.setattr(main, "open_reader", open_reader, raising=False)
    monkeypatch.setattr(main, "QdrantStoreManager", Manager, raising=False)
    monkeypatch.setattr(main, "create_rag_graph", lambda retriever, **kwargs: retriever, raising=False)
    first, second = create_app(), create_app()
    async with first.router.lifespan_context(first):
        async with second.router.lifespan_context(second):
            assert first.state.chat_service.workflow is clients[0]
            assert second.state.chat_service.workflow is clients[1]
            assert not clients[0].closed and not clients[1].closed
        assert clients[1].closed and not clients[0].closed
    assert clients[0].closed


@pytest.mark.asyncio
async def test_health_is_liveness_and_ready_checks_required_resources() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        health = await client.get("/health")
        readiness = await client.get("/ready")
    assert health.status_code == 200
    assert readiness.status_code == 503


@pytest.mark.asyncio
async def test_shutdown_drains_cancelled_retrieval_before_closing_qdrant(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio
    import threading

    from app import main
    from app.ai.retrieval_executor import RetrievalExecutor

    client = FakeResources("blocked")
    release = threading.Event()
    started = asyncio.Event()
    loop = asyncio.get_running_loop()

    class Manager:
        def __init__(self, *, client: FakeResources) -> None:
            self.client = client

        def as_retriever(self, *, k: int) -> FakeResources:
            return self.client

    def block() -> None:
        loop.call_soon_threadsafe(started.set)
        if not release.wait(2):
            raise TimeoutError("test did not release retrieval")
        assert not client.closed

    def graph_factory(
        retriever: object, *, retrieval_executor: RetrievalExecutor, **kwargs: object
    ) -> RetrievalExecutor:
        return retrieval_executor

    monkeypatch.setattr(main, "open_reader", lambda _settings: client)
    monkeypatch.setattr(main, "QdrantStoreManager", Manager)
    monkeypatch.setattr(main, "create_rag_graph", graph_factory)
    app = create_app()
    context = app.router.lifespan_context(app)
    await context.__aenter__()
    executor = app.state.chat_service.workflow
    job = asyncio.create_task(executor.run(block))
    shutdown = None
    try:
        await asyncio.wait_for(started.wait(), 1)
        job.cancel()
        with pytest.raises(asyncio.CancelledError):
            await job
        shutdown = asyncio.create_task(context.__aexit__(None, None, None))
        await asyncio.sleep(0.01)
        assert not shutdown.done()
        assert not client.closed
        shutdown.cancel()
        await asyncio.sleep(0.01)
        assert not shutdown.done()
        assert not client.closed
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await shutdown
        assert client.closed
    finally:
        release.set()
        await asyncio.gather(job, *([shutdown] if shutdown else []), return_exceptions=True)
        if shutdown is None:
            await context.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_graph_startup_failure_closes_executor_and_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main
    from app.ai.retrieval_executor import RetrievalExecutor

    client = FakeResources("partial")
    executors: list[RetrievalExecutor] = []

    class Manager:
        def __init__(self, *, client: FakeResources) -> None:
            self.client = client

        def as_retriever(self, *, k: int) -> FakeResources:
            return self.client

    def failing_graph(retriever: object, *, retrieval_executor: RetrievalExecutor, **kwargs: object) -> None:
        executors.append(retrieval_executor)
        raise RuntimeError("graph setup failed")

    monkeypatch.setattr(main, "open_reader", lambda _settings: client)
    monkeypatch.setattr(main, "QdrantStoreManager", Manager)
    monkeypatch.setattr(main, "create_rag_graph", failing_graph)
    app = create_app()
    with pytest.raises(RuntimeError, match="graph setup failed"):
        async with app.router.lifespan_context(app):
            pass
    assert client.closed
    assert len(executors) == 1
    with pytest.raises(RuntimeError, match="closed"):
        await executors[0].run(lambda: None)
