"""Integration tests for root, health, and route contract definitions."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

import app.main as app_module
from app.main import app

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_read_root() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Welcome to Justify API"


@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_app_preserves_root_health_and_route_contract() -> None:
    candidate = app_module.create_app()
    assert app.title == candidate.title == "Justify API"
    paths = {
        (getattr(route, "path", None), tuple(sorted(getattr(route, "methods", ()) or ()))) for route in candidate.routes
    }
    assert ("/api/chat/stream", ("POST",)) in paths
    assert ("/api/waitlist", ("POST",)) in paths
    async with AsyncClient(transport=ASGITransport(app=candidate), base_url="http://test") as client:
        root = await client.get("/")
        health = await client.get("/health")
        assert root.status_code == health.status_code == 200
        assert root.json() == {"message": "Welcome to Justify API"}
        assert health.json() == {"status": "healthy"}
