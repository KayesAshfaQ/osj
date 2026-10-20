"""Explicit async database engine and session lifetimes."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def create_engine(url: str) -> AsyncEngine:
    """Build an engine without connecting or writing to the database."""
    return create_async_engine(url, echo=False, future=True)


def create_session_factory(
    engine: AsyncEngine, *, session_class: type[AsyncSession] = AsyncSession
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=session_class,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@asynccontextmanager
async def cli_session(factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """CLI callers own and pass their factory explicitly."""
    async with factory() as session:
        yield session


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    async with factory() as session:
        yield session
