"""FastAPI composition root and lifetime owner for backend resources."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import cast

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlalchemy import text as sql_text
from sqlalchemy.exc import SQLAlchemyError

from app.ai.qdrant_store import QdrantStoreManager, open_reader
from app.ai.retrieval_executor import RetrievalExecutor
from app.core.config import settings
from app.core.schemas import HealthResponse, WelcomeResponse
from app.modules.chat.router import router as chat_router
from app.modules.chat.service import ChatService
from app.modules.chat.sessions import AnonymousSessions
from app.modules.chat.workflows.graph import create_rag_graph
from app.modules.corpus.repository import SessionParentReader
from app.modules.waitlist.router import router as waitlist_router
from app.persistence.session import create_engine, create_session_factory

logger = logging.getLogger(__name__)

ResourceFactory = Callable[[FastAPI], AbstractAsyncContextManager[object]]


@asynccontextmanager
async def default_resources(app: FastAPI) -> AsyncGenerator[object, None]:
    logger.info("Initializing Qdrant hybrid retriever...")
    redis_client: Redis | None = None
    qdrant_client = None
    engine = None
    retrieval_executor = None
    try:
        qdrant_client = open_reader(settings)
        retriever = QdrantStoreManager(client=qdrant_client).as_retriever(k=5)
        if settings.database_url:
            engine = create_engine(settings.database_url)
            app.state.session_factory = create_session_factory(engine)
            parent_reader = SessionParentReader(app.state.session_factory)
        else:
            parent_reader = None

        async def ready_probe() -> None:
            if engine is None:
                raise HTTPException(status_code=503, detail="Database unavailable")
            try:
                async with asyncio.timeout(1):
                    async with engine.connect() as connection:
                        await connection.execute(sql_text("SELECT 1"))
            except (SQLAlchemyError, TimeoutError) as exc:
                raise HTTPException(status_code=503, detail="Database unavailable") from exc

        redis_client = Redis.from_url(settings.redis_url, socket_timeout=1.0, socket_connect_timeout=1.0)  # pyright: ignore[reportUnknownMemberType]
        retrieval_executor = RetrievalExecutor()
        app.state.chat_service = ChatService(
            workflow=create_rag_graph(retriever, parent_reader=parent_reader, retrieval_executor=retrieval_executor),
            sessions=AnonymousSessions(cast(object, redis_client)),  # type: ignore[arg-type]
            ready_probe=ready_probe,
        )
        logger.info("Qdrant hybrid retriever initialized.")
        yield retriever
    finally:
        # Cancellation ends an awaiter, never the synchronous Qdrant operation.
        # Drain workers before closing any resources they could still be using.
        try:
            if retrieval_executor is not None:
                await retrieval_executor.aclose()
        finally:
            try:
                if redis_client is not None:
                    await redis_client.aclose()
            finally:
                try:
                    if engine is not None:
                        await engine.dispose()
                finally:
                    if qdrant_client is not None:
                        qdrant_client.close()
        logger.info("Shutting down...")


def create_app(resource_factory: ResourceFactory | None = None) -> FastAPI:
    owner = resource_factory or default_resources

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        async with owner(application) as resources:
            application.state.resources = resources
            try:
                yield
            finally:
                del application.state.resources

    application = FastAPI(
        title="Justify API",
        description="Backend API for the Justify Legal Copilot",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.chat_service = ChatService()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    application.include_router(waitlist_router, prefix="/api/waitlist", tags=["waitlist"])

    @application.get("/", response_model=WelcomeResponse)
    def read_root() -> WelcomeResponse:
        return WelcomeResponse(message="Welcome to Justify API")

    @application.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        return HealthResponse(status="healthy")

    @application.get("/ready")
    async def readiness_check() -> dict[str, str]:
        if not hasattr(application.state, "resources"):
            raise HTTPException(status_code=503, detail="Application resources unavailable")
        await application.state.chat_service.probe()
        return {"status": "ready"}

    return application


app = create_app()
