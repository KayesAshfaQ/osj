"""Verified chat answers and anonymous session admission."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import cast
from uuid import uuid4

import httpx
from fastapi import HTTPException
from langsmith import tracing_context  # pyright: ignore[reportUnknownVariableType]
from redis.exceptions import RedisError

from app.ai.llm_factory import LLMConfigurationError
from app.core.exceptions import LLMProviderError
from app.modules.chat.privacy import sanitize
from app.modules.chat.schemas import ChatAnswer
from app.modules.chat.sessions import (
    AnonymousSessions,
    CorruptSession,
    IssuedSession,
    QuotaExceeded,
    SessionBusy,
    SessionMissing,
)
from app.modules.chat.workflows.graph import RAGState, verify_citations_node

logger = logging.getLogger(__name__)


CHAT_DEADLINE_SECONDS = 30.0


@dataclass
class ChatMetrics:
    """Sanitized operational metrics and counters."""

    answered_total: int = 0
    refusal_total: int = 0
    provider_failure_total: int = 0
    admission_rejection_total: int = 0


class ChatService:
    """Service facade for verified chat operations."""

    def __init__(
        self,
        workflow: object = None,
        sessions: AnonymousSessions | None = None,
        ready_probe: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        self.workflow = workflow
        self.sessions = sessions
        self.ready_probe = ready_probe
        self._active = asyncio.Semaphore(4)
        self.metrics = ChatMetrics()

    async def issue_session(self) -> IssuedSession:
        if self.sessions is None:
            raise HTTPException(status_code=503, detail="Conversation storage unavailable")
        try:
            return await self.sessions.issue()
        except (RedisError, CorruptSession) as exc:
            raise HTTPException(status_code=503, detail="Conversation storage unavailable") from exc

    async def delete_session(self, token: str) -> None:
        if self.sessions is None:
            raise HTTPException(status_code=503, detail="Conversation storage unavailable")
        try:
            await self.sessions.delete(token)
        except SessionMissing as exc:
            raise HTTPException(status_code=401, detail="Invalid session token") from exc
        except (RedisError, CorruptSession) as exc:
            raise HTTPException(status_code=503, detail="Conversation storage unavailable") from exc

    async def admit(self, *, token: str | None = None, address: str = "") -> str | None:
        await self.probe()
        if self.sessions is None:
            if token is not None:
                raise HTTPException(status_code=503, detail="Conversation storage unavailable")
            return None
        try:
            if token is not None:
                await self.sessions.history(token)
            await self.sessions.check_limits(token, address)
            return await self.sessions.begin(token) if token is not None else None
        except SessionMissing as exc:
            self.metrics.admission_rejection_total += 1
            raise HTTPException(status_code=401, detail="Invalid session token") from exc
        except QuotaExceeded as exc:
            self.metrics.admission_rejection_total += 1
            raise HTTPException(status_code=429, detail="Chat request quota exceeded") from exc
        except SessionBusy as exc:
            self.metrics.admission_rejection_total += 1
            raise HTTPException(status_code=409, detail="Session already has an active request") from exc
        except (RedisError, CorruptSession) as exc:
            raise HTTPException(status_code=503, detail="Conversation storage unavailable") from exc

    async def probe(self) -> None:
        if self.ready_probe is not None:
            await self.ready_probe()
        if self.sessions is not None:
            try:
                await asyncio.wait_for(self.sessions.redis.ping(), timeout=1)
            except (RedisError, TimeoutError) as exc:
                raise HTTPException(status_code=503, detail="Conversation storage unavailable") from exc

    async def answer(
        self,
        query: str,
        *,
        token: str | None = None,
        address: str = "",
        admitted: bool = False,
        lease: str | None = None,
    ) -> ChatAnswer:
        if not admitted:
            lease = await self.admit(token=token, address=address)
        acquired_active = False
        try:
            try:
                await asyncio.wait_for(self._active.acquire(), timeout=0.01)
                acquired_active = True
            except TimeoutError as exc:
                self.metrics.admission_rejection_total += 1
                raise HTTPException(status_code=429, detail="Chat capacity exhausted") from exc

            deadline = asyncio.get_running_loop().time() + CHAT_DEADLINE_SECONDS
            async with asyncio.timeout_at(deadline):
                if self.workflow is None:
                    self.metrics.provider_failure_total += 1
                    raise HTTPException(status_code=503, detail="Chat workflow unavailable")
                history = await self.sessions.history(token) if token and self.sessions else []
                with tracing_context(enabled=False):
                    raw_result: object = await self.workflow.ainvoke(  # type: ignore[attr-defined]
                        {
                            "query": sanitize(query),
                            "history": history,
                            "retry_count": 0,
                            "deadline": deadline,
                        }
                    )
                checked = verify_citations_node(cast(RAGState, raw_result))
                req_id = uuid4().hex
                raw_answer = str(checked.get("generated_answer") or "")
                outcome_val = checked.get("outcome")
                raw_outcome = str(getattr(outcome_val, "value", outcome_val or "refused"))
                raw_sources = checked.get("sources")
                answer = ChatAnswer(
                    request_id=req_id,
                    outcome=raw_outcome,  # type: ignore[arg-type]
                    answer=sanitize(raw_answer),
                    sources=raw_sources if isinstance(raw_sources, list) else [],  # type: ignore[arg-type]
                )
                if answer.outcome == "answered":
                    self.metrics.answered_total += 1
                else:
                    self.metrics.refusal_total += 1

                logger.info(
                    "Chat request completed: id=%s outcome=%s sources=%d",
                    req_id,
                    answer.outcome,
                    len(answer.sources),
                )

                if token and self.sessions:
                    await self.sessions.append(token, query, answer.outcome, answer.answer)
                return answer
        except TimeoutError as exc:
            self.metrics.refusal_total += 1
            logger.warning("Chat request timed out")
            raise HTTPException(status_code=504, detail="Chat processing deadline exceeded") from exc
        except (RedisError, CorruptSession) as exc:
            logger.warning("Session storage error during chat processing: %s", type(exc).__name__)
            raise HTTPException(status_code=503, detail="Conversation storage unavailable") from exc
        except (LLMConfigurationError, httpx.HTTPError, Exception) as exc:
            if getattr(exc, "status_code", None) == 429 or (
                isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429
            ):
                self.metrics.provider_failure_total += 1
                logger.warning("Chat provider rate limited")
                raise HTTPException(
                    status_code=429, detail="Chat provider rate limit exceeded; try again shortly"
                ) from exc
            if (
                isinstance(exc, (LLMConfigurationError, LLMProviderError, httpx.HTTPError))
                or "API" in type(exc).__name__
                or "openai" in type(exc).__module__.lower()
                or "groq" in type(exc).__module__.lower()
            ):
                self.metrics.provider_failure_total += 1
                logger.warning("Chat provider error: %s", type(exc).__name__)
                raise HTTPException(status_code=503, detail="Chat provider unavailable") from exc
            raise
        finally:
            if acquired_active:
                self._active.release()
            if token and lease and self.sessions:
                try:
                    await self.sessions.end(token, lease)
                except RedisError:
                    logger.warning("Session lease release failed")
