"""Waitlist route: HTTP boundary over feature-owned service and ports."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.waitlist.domain import DuplicateEmail
from app.modules.waitlist.email import ResendWelcomeEmail
from app.modules.waitlist.repository import SqlAlchemyWaitlistRepository
from app.modules.waitlist.schemas import WaitlistRequest, WaitlistResponse
from app.modules.waitlist.service import WaitlistService
from app.persistence.session import get_db

router = APIRouter()


def get_waitlist_service(db: AsyncSession = Depends(get_db)) -> WaitlistService:
    return WaitlistService(repository=SqlAlchemyWaitlistRepository(db))


@router.post("", response_model=WaitlistResponse, status_code=201)
async def join_waitlist(
    request: WaitlistRequest,
    background_tasks: BackgroundTasks,
    service: WaitlistService = Depends(get_waitlist_service),
) -> WaitlistResponse:
    try:
        email = await service.register(str(request.email))
    except DuplicateEmail as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc
    background_tasks.add_task(ResendWelcomeEmail().send_welcome, email)
    return WaitlistResponse(message="Successfully joined the waitlist", email=email)
