"""Integration tests for SqlAlchemyWaitlistRepository error handling and transaction rollback."""

from __future__ import annotations

from typing import cast

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.waitlist.repository import SqlAlchemyWaitlistRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_unrelated_integrity_failure_is_not_duplicate_email() -> None:
    class FakeSession:
        rolled_back = False

        def add(self, value: object) -> None:
            pass

        async def commit(self) -> None:
            raise IntegrityError("INSERT", {}, Exception("NOT NULL constraint failed: waitlist.created_at"))

        async def rollback(self) -> None:
            self.rolled_back = True

    fake = FakeSession()
    with pytest.raises(IntegrityError):
        await SqlAlchemyWaitlistRepository(cast(AsyncSession, fake)).register("a@example.com")
    assert fake.rolled_back
