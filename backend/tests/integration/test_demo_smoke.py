"""Fresh synthetic CLI ingestion, parent hydration, graph and HTTP delivery."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.retrieval_executor import RetrievalExecutor
from app.main import create_app
from app.modules.chat.domain import SAFE_REFUSAL
from app.modules.chat.service import ChatService
from app.modules.chat.sessions import AnonymousSessions
from app.modules.chat.workflows.graph import create_rag_graph
from app.modules.corpus.repository import SessionParentReader
from app.persistence.base import Base
from app.persistence.models.legal_data import ParentChunk
from scripts.reindex_hybrid import prepare_documents_from_data_dir
from tests.fakes import FakeRedis

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_synthetic_cli_to_verified_http_answer_and_refusal(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'demo.sqlite'}"
    engine = create_async_engine(url)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "scripts/ingest_corpus_postgres.py",
            "--demo",
            cwd=ROOT,
            env={**os.environ, "DATABASE_URL": url},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15)
        assert process.returncode == 0, stderr.decode()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(ParentChunk)) == 3
        children = prepare_documents_from_data_dir(ROOT / "data", demo=True)
        first = next(doc for doc in children if doc.metadata["section_number"] == "1")
        source = {key: str(first.metadata[key]) for key in ("source_id", "act_title", "section_number")}

        class Retriever:
            def invoke(self, query):
                return [first]

        class Provider:
            async def ainvoke(self, messages):
                actual = "actual" in str(messages[-1].content).lower()
                return AIMessage(
                    content=json.dumps(
                        {
                            "answer": SAFE_REFUSAL
                            if actual
                            else (
                                "Section 1 of the Synthetic Demonstration Act (fictional) defines a sample widget as a blue square."
                            ),
                            "sources": [] if actual else [source],
                        }
                    )
                )

        @asynccontextmanager
        async def resources(app: FastAPI):
            async with RetrievalExecutor() as executor:
                app.state.chat_service = ChatService(
                    workflow=create_rag_graph(
                        Retriever(),
                        provider_factory=Provider,
                        parent_reader=SessionParentReader(factory),
                        retrieval_executor=executor,
                    ),
                    sessions=AnonymousSessions(FakeRedis()),
                )
                yield executor

        app = create_app(resource_factory=resources)
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                assert (await client.get("/ready")).status_code == 200
                answer = await client.post("/api/chat", json={"query": "Section 1?"})
                assert answer.status_code == 200
                assert answer.json()["outcome"] == "answered"
                assert answer.json()["sources"][0]["act_title"] == source["act_title"]
                refused = await client.post("/api/chat", json={"query": "Section 1 under actual law?"})
                assert refused.status_code == 200
                assert refused.json()["outcome"] == "refused"
                assert refused.json()["sources"] == []
    finally:
        await engine.dispose()
