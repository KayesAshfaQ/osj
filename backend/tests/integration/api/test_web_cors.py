"""Browser preflight behavior using an explicit reader-owned allowlist."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import create_app

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "origin,allowed",
    [
        ("https://app.example.com", True),
        ("https://www.example.com", True),
        ("https://osj-example-app.web.app", True),
        ("https://osj-example-app.firebaseapp.com", True),
        ("https://untrusted.example", False),
    ],
)
async def test_reader_configured_browser_preflights(
    monkeypatch: pytest.MonkeyPatch, origin: str, allowed: bool
) -> None:
    monkeypatch.setattr(
        settings,
        "cors_origins",
        [
            "https://app.example.com",
            "https://www.example.com",
            "https://osj-example-app.web.app",
            "https://osj-example-app.firebaseapp.com",
        ],
    )
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test") as client:
        for path, method in [
            ("/api/chat/sessions", "POST"),
            ("/api/chat", "POST"),
            ("/api/chat/sessions/current", "DELETE"),
        ]:
            response = await client.options(
                path,
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": method,
                    "Access-Control-Request-Headers": "authorization,content-type",
                },
            )
            assert response.status_code == (200 if allowed else 400)
            assert response.headers.get("access-control-allow-origin") == (origin if allowed else None)
            assert "access-control-allow-credentials" not in response.headers
