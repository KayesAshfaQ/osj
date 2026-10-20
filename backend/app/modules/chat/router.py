"""Direct JSON and SSE delivery of the same verified chat outcome."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.modules.chat.prompt_guard import PromptGuard
from app.modules.chat.schemas import ChatAnswer, ChatRequest, SessionResponse
from app.modules.chat.service import ChatService

router = APIRouter()


def get_chat_service(request: Request) -> ChatService:
    service = getattr(request.app.state, "chat_service", None)
    return service if service is not None else ChatService()


def validate_prompt(request: ChatRequest) -> ChatRequest:
    if not PromptGuard.is_safe_prompt(request.query):
        raise HTTPException(status_code=422, detail="Query contains an instruction or code payload")
    return request


def bearer_token(authorization: Annotated[str | None, Header()] = None) -> str | None:
    if authorization is None:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return token


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(service: Annotated[ChatService, Depends(get_chat_service)]) -> SessionResponse:
    issued = await service.issue_session()
    return SessionResponse(token=issued.token, expires_at=issued.expires_at)


@router.delete("/sessions/current", status_code=204)
async def delete_session(
    service: Annotated[ChatService, Depends(get_chat_service)],
    token: Annotated[str | None, Depends(bearer_token)],
) -> Response:
    if token is None:
        raise HTTPException(status_code=401, detail="Session token required")
    await service.delete_session(token)
    return Response(status_code=204)


@router.post("", response_model=ChatAnswer)
async def chat_endpoint(
    request: Annotated[ChatRequest, Depends(validate_prompt)],
    service: Annotated[ChatService, Depends(get_chat_service)],
    peer: Request,
    token: Annotated[str | None, Depends(bearer_token)],
) -> ChatAnswer:
    return await service.answer(request.query, token=token, address=peer.client.host if peer.client else "")


@router.post("/stream")
async def chat_stream_endpoint(
    request: Annotated[ChatRequest, Depends(validate_prompt)],
    service: Annotated[ChatService, Depends(get_chat_service)],
    peer: Request,
    token: Annotated[str | None, Depends(bearer_token)],
) -> StreamingResponse:
    address = peer.client.host if peer.client else ""
    # Admission and session checks run before response headers are sent.
    lease = await service.admit(token=token, address=address)

    async def events() -> AsyncIterator[str]:
        nonlocal lease
        try:
            yield f"event: progress\ndata: {json.dumps({'stage': 'processing'})}\n\n"
            try:
                result = await service.answer(request.query, token=token, address=address, admitted=True, lease=lease)
                lease = None
                yield f"event: answer\ndata: {result.model_dump_json()}\n\n"
            except HTTPException as exc:
                yield f"event: error\ndata: {json.dumps({'detail': exc.detail})}\n\n"
            except Exception:
                yield 'event: error\ndata: {"detail":"Chat processing failed"}\n\n'
            yield "event: done\ndata: {}\n\n"
        finally:
            if lease is not None and token and service.sessions:
                try:
                    await service.sessions.end(token, lease)
                except Exception:
                    pass

    return StreamingResponse(events(), media_type="text/event-stream")
