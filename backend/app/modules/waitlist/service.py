"""Waitlist signup use case; independent of FastAPI and SQLAlchemy."""

from app.modules.waitlist.domain import WaitlistSignup
from app.modules.waitlist.ports import WaitlistRepositoryPort


class WaitlistService:
    def __init__(self, repository: WaitlistRepositoryPort) -> None:
        self.repository = repository

    async def register(self, email: str) -> str:
        command = WaitlistSignup(email=email.lower())
        await self.repository.register(command.email)
        return command.email
