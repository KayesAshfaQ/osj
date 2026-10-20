from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from langchain_core.documents import Document

from app.ai.retrieval_executor import RetrievalExecutor
from tests.fakes import FakeRedis, make_evidence_doc


@pytest.fixture
def fake_redis() -> FakeRedis:
    """Provide an in-memory Redis test double."""
    return FakeRedis()


@pytest.fixture
def default_evidence() -> Document:
    """Provide standard evidence document for chat & citation tests."""
    return make_evidence_doc()


@pytest_asyncio.fixture
async def retrieval_executor() -> AsyncGenerator[RetrievalExecutor, None]:
    """Own retrieval workers explicitly and drain them before the test ends."""
    async with RetrievalExecutor() as executor:
        yield executor
