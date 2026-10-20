"""Sync worker capacity and resource shutdown remain correct on cancellation."""

from __future__ import annotations

import asyncio
import contextvars
import threading

import pytest

from app.ai.retrieval_executor import RetrievalExecutor

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_close_drains_cancelled_job_and_preserves_shutdown_cancellation() -> None:
    release = threading.Event()
    started = asyncio.Event()
    loop = asyncio.get_running_loop()
    executor = RetrievalExecutor(max_workers=1)

    def block() -> None:
        loop.call_soon_threadsafe(started.set)
        if not release.wait(2):
            raise TimeoutError("test did not release worker")

    job = asyncio.create_task(executor.run(block))
    close = None
    try:
        await asyncio.wait_for(started.wait(), 1)
        job.cancel()
        with pytest.raises(asyncio.CancelledError):
            await job
        close = asyncio.create_task(executor.aclose())
        await asyncio.sleep(0)
        with pytest.raises(RuntimeError, match="closed"):
            await executor.run(lambda: None)
        close.cancel()
        await asyncio.sleep(0.01)
        assert not close.done()
        close.cancel()
        await asyncio.sleep(0)
        assert not close.done()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await close
        await executor.aclose()
    finally:
        release.set()
        await asyncio.gather(job, *([close] if close else []), return_exceptions=True)
        await executor.aclose()


@pytest.mark.asyncio
async def test_cancelling_waiter_does_not_submit_it_or_lose_slot() -> None:
    release = threading.Event()
    started = asyncio.Event()
    loop = asyncio.get_running_loop()
    calls: list[str] = []

    def block() -> None:
        loop.call_soon_threadsafe(started.set)
        if not release.wait(2):
            raise TimeoutError("test did not release worker")

    async with RetrievalExecutor(max_workers=1) as executor:
        first = asyncio.create_task(executor.run(block))
        try:
            await asyncio.wait_for(started.wait(), 1)
            waiting = asyncio.create_task(executor.run(calls.append, "cancelled"))
            await asyncio.sleep(0)
            waiting.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiting
            release.set()
            await first
            await executor.run(calls.append, "next")
            assert calls == ["next"]
        finally:
            release.set()
            await first


@pytest.mark.asyncio
async def test_worker_failure_propagates_and_context_is_preserved() -> None:
    marker: contextvars.ContextVar[str] = contextvars.ContextVar("retrieval_test", default="missing")
    marker.set("request context")

    def fail() -> None:
        raise ValueError("query failed")

    async with RetrievalExecutor(max_workers=1) as executor:
        with pytest.raises(ValueError, match="query failed"):
            await executor.run(fail)
        assert await executor.run(marker.get) == "request context"
