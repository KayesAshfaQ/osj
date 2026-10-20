from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.persistence.models.legal_data
import app.persistence.models.user
import app.persistence.models.waitlist

_ = (
    app.persistence.models.waitlist,
    app.persistence.models.legal_data,
    app.persistence.models.user,
)
from app.main import app as fastapi_app
from app.persistence.base import Base
from app.persistence.session import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, poolclass=StaticPool)
db_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def override_get_db():
    async with db_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with db_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def async_client():
    fastapi_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        yield client
    fastapi_app.dependency_overrides.clear()
