"""Application-owned bounded execution for synchronous retrieval work."""

from __future__ import annotations

import asyncio
import contextvars
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from types import TracebackType
from typing import ParamSpec, TypeVar, cast

logger = logging.getLogger(__name__)
P = ParamSpec("P")
T = TypeVar("T")


class RetrievalExecutor:
    """Admit at most four sync jobs, retaining slots after caller cancellation.

    Async waiters acquire a slot before submission, so the thread pool cannot
    accumulate a backlog. Cancelling a request never terminates its sync work.
    The owner must drain this executor before closing retrieval resources.
    """

    def __init__(self, max_workers: int = 4) -> None:
        if not 1 <= max_workers <= 4:
            raise ValueError("Retrieval executor requires between one and four workers")
        self._loop = asyncio.get_running_loop()
        self._slots = asyncio.Semaphore(max_workers)
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="retrieval")
        self._jobs: set[asyncio.Future[object]] = set()
        self._closed = False
        self._close_task: asyncio.Task[None] | None = None

    async def run(self, operation: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        if self._closed:
            raise RuntimeError("Retrieval executor is closed")
        await self._slots.acquire()
        if self._closed:
            self._slots.release()
            raise RuntimeError("Retrieval executor is closed")
        try:
            context = contextvars.copy_context()
            job = self._loop.run_in_executor(self._pool, context.run, partial(operation, *args, **kwargs))
        except BaseException:
            self._slots.release()
            raise
        self._jobs.add(cast(asyncio.Future[object], job))
        detached = False

        def completed(future: asyncio.Future[T]) -> None:
            self._jobs.discard(cast(asyncio.Future[object], future))
            self._slots.release()
            error = future.exception()
            if detached and error is not None:
                logger.warning("Cancelled retrieval job finished with %s", type(error).__name__)

        job.add_done_callback(completed)
        try:
            return await asyncio.shield(job)
        except asyncio.CancelledError:
            detached = True
            raise

    async def _drain(self) -> None:
        if self._jobs:
            await asyncio.gather(*self._jobs, return_exceptions=True)
        # Every submitted future has completed; this only joins idle threads.
        self._pool.shutdown(wait=True)

    async def aclose(self) -> None:
        """Reject new jobs and drain actual work, even if shutdown is cancelled.

        There is no safe force-stop for Python threads. Shutdown waits for sync
        calls to finish, then re-raises any cancellation received while draining.
        """
        self._closed = True
        if self._close_task is None:
            self._close_task = asyncio.create_task(self._drain())
        cancelled = False
        while not self._close_task.done():
            try:
                await asyncio.shield(self._close_task)
            except asyncio.CancelledError:
                cancelled = True
        self._close_task.result()
        if cancelled:
            raise asyncio.CancelledError

    async def __aenter__(self) -> RetrievalExecutor:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        await self.aclose()
