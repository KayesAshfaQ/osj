"""Integration tests for waitlist HTTP endpoints, duplicate checking, and email dispatch."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import create_app
from app.modules.waitlist.router import get_waitlist_service
from app.modules.waitlist.service import WaitlistService
from app.persistence.models.waitlist import WaitlistEntry
from tests.fakes import FakeWaitlistRepository
from tests.integration.conftest import db_session_factory

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@patch("app.modules.waitlist.email.send_welcome_email")
async def test_join_waitlist_success(mock_send_email: object, async_client: AsyncClient) -> None:
    response = await async_client.post("/api/waitlist", json={"email": "test@example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Successfully joined the waitlist"
    assert data["email"] == "test@example.com"

    async with db_session_factory() as session:
        result = await session.execute(select(WaitlistEntry).where(WaitlistEntry.email == "test@example.com"))
        entry = result.scalar_one_or_none()
        assert entry is not None
        assert entry.email == "test@example.com"

    mock_send_email.assert_called_once_with(to_email="test@example.com")  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_join_waitlist_duplicate_email(async_client: AsyncClient) -> None:
    response1 = await async_client.post("/api/waitlist", json={"email": "duplicate@example.com"})
    assert response1.status_code == 201

    response2 = await async_client.post("/api/waitlist", json={"email": "duplicate@example.com"})
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_join_waitlist_invalid_email(async_client: AsyncClient) -> None:
    response = await async_client.post("/api/waitlist", json={"email": "not-an-email"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_join_waitlist_missing_body(async_client: AsyncClient) -> None:
    response = await async_client.post("/api/waitlist", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_join_waitlist_email_case_insensitive(async_client: AsyncClient) -> None:
    response1 = await async_client.post("/api/waitlist", json={"email": "UPPER@EXAMPLE.COM"})
    assert response1.status_code == 201

    response2 = await async_client.post("/api/waitlist", json={"email": "upper@example.com"})
    assert response2.status_code == 409


@pytest.mark.asyncio
@patch("app.modules.waitlist.email.resend.Emails.send")
async def test_email_service_failure_does_not_crash(mock_resend: object, async_client: AsyncClient) -> None:
    mock_resend.side_effect = Exception("Failed to connect to Resend API")  # type: ignore[attr-defined]

    response = await async_client.post("/api/waitlist", json={"email": "fail@example.com"})
    assert response.status_code == 201

    async with db_session_factory() as session:
        result = await session.execute(select(WaitlistEntry).where(WaitlistEntry.email == "fail@example.com"))
        assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_waitlist_http_contract_with_injected_service() -> None:
    repository = FakeWaitlistRepository(set())
    application = create_app()
    application.dependency_overrides[get_waitlist_service] = lambda: WaitlistService(repository=repository)
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as client:
        response = await client.post("/api/waitlist", json={"email": "UPPER@EXAMPLE.COM"})
        assert response.status_code == 201
        assert response.json() == {"message": "Successfully joined the waitlist", "email": "upper@example.com"}
        duplicate = await client.post("/api/waitlist", json={"email": "upper@example.com"})
        assert duplicate.status_code == 409
        assert duplicate.json()["detail"] == "Email already registered"
        invalid = await client.post("/api/waitlist", json={"email": "broken"})
        assert invalid.status_code == 422
    assert repository.emails == {"upper@example.com"}
