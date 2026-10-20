"""Unit tests for WaitlistService registration logic using in-memory fake repository."""

from __future__ import annotations

import pytest

from app.modules.waitlist.domain import DuplicateEmail
from app.modules.waitlist.service import WaitlistService
from tests.fakes import FakeWaitlistRepository

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_waitlist_service_normalizes_email_to_lowercase() -> None:
    repository = FakeWaitlistRepository(set())
    service = WaitlistService(repository=repository)
    email = await service.register("UPPER@EXAMPLE.COM")
    assert email == "upper@example.com"
    assert repository.emails == {"upper@example.com"}


@pytest.mark.asyncio
async def test_waitlist_service_raises_duplicate_email() -> None:
    repository = FakeWaitlistRepository(set())
    service = WaitlistService(repository=repository)
    await service.register("UPPER@EXAMPLE.COM")
    assert repository.emails == {"upper@example.com"}
    with pytest.raises(DuplicateEmail):
        await service.register("upper@example.com")
