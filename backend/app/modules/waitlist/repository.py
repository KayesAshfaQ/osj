"""SQLAlchemy adapter for waitlist signup."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.waitlist.domain import DuplicateEmail
from app.persistence.models.waitlist import WaitlistEntry


class SqlAlchemyWaitlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, email: str) -> None:
        self.session.add(WaitlistEntry(email=email))
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            constraint = str(getattr(getattr(exc.orig, "diag", None), "constraint_name", "") or "")
            message = str(exc.orig).lower()
            if (
                constraint in {"ix_waitlist_email", "waitlist_email_key"}
                or "unique constraint failed: waitlist.email" in message
            ):
                raise DuplicateEmail from exc
            raise
