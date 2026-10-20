"""Integration tests for SQLAlchemy 2.0 AsyncSession lifetime, engine disposal, and scoped sessions."""

from __future__ import annotations

import importlib

import pytest
from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.persistence.base import Base
from app.persistence.models.waitlist import WaitlistEntry
from app.persistence.session import cli_session, create_engine, create_session_factory, get_db

pytestmark = pytest.mark.integration


class TrackedSession(AsyncSession):
    closed_by_context = False

    async def close(self) -> None:
        self.closed_by_context = True
        await super().close()


def test_base_metadata_is_shared_by_models() -> None:
    assert WaitlistEntry.metadata is Base.metadata
    assert WaitlistEntry.__table__ is Base.metadata.tables[WaitlistEntry.__tablename__]


def test_importing_metadata_does_not_construct_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.persistence import session

    def unexpected_engine(*args: object, **kwargs: object) -> None:
        raise AssertionError("engine constructed during metadata import")

    with monkeypatch.context() as patch:
        patch.setattr("sqlalchemy.ext.asyncio.create_async_engine", unexpected_engine)
        importlib.reload(session)
    importlib.reload(session)


@pytest.mark.asyncio
async def test_request_session_is_closed_on_generator_exit() -> None:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    factory = create_session_factory(engine, session_class=TrackedSession)
    app = FastAPI()
    app.state.session_factory = factory
    request = Request({"type": "http", "app": app})
    try:
        generator = get_db(request)
        session = await anext(generator)
        assert isinstance(session, TrackedSession)
        assert not session.closed_by_context
        await generator.aclose()
        assert session.closed_by_context
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_cli_session_requires_explicit_factory_and_closes_after_use() -> None:
    with pytest.raises(TypeError):
        cli_session()  # type: ignore[call-arg]
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    try:
        assert isinstance(engine, AsyncEngine)
        factory = create_session_factory(engine, session_class=TrackedSession)
        assert isinstance(factory, async_sessionmaker)
        async with cli_session(factory) as session:
            assert isinstance(session, TrackedSession)
            assert not session.closed_by_context
        assert session.closed_by_context
    finally:
        await engine.dispose()
