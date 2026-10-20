"""Unit tests for waitlist welcome email adapter, transport timeout, and log privacy."""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.modules.waitlist import email as email_service
from app.modules.waitlist.email import ResendWelcomeEmail

pytestmark = pytest.mark.unit


def test_demo_email_identifies_fictional_learning_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "resend_api_key", "synthetic-key")
    payloads: list[dict[str, object]] = []
    monkeypatch.setattr(email_service.resend.Emails, "send", lambda payload: payloads.append(payload))
    email_service.send_welcome_email("reader@example.com")
    assert "OSJ" in str(payloads[0]["subject"])
    assert "fictional" in str(payloads[0]["html"])
    assert "verified legal summaries" not in str(payloads[0]["html"])


def test_waitlist_email_adapter_does_not_log_recipient(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(settings, "resend_api_key", "test-key")
    monkeypatch.setattr(email_service.resend.Emails, "send", lambda _: {"id": "test-id"})
    ResendWelcomeEmail().send_welcome("private@example.com")
    assert "private@example.com" not in caplog.text


def test_email_transport_has_five_second_timeout_and_sanitized_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(settings, "resend_api_key", "synthetic-secret")
    timeouts: list[int] = []

    class Client:
        def __init__(self, timeout: int) -> None:
            timeouts.append(timeout)

    def fail(_payload: object) -> None:
        raise RuntimeError("private@example.com synthetic-secret")

    monkeypatch.setattr(email_service.resend, "RequestsClient", Client)
    monkeypatch.setattr(email_service.resend.Emails, "send", fail)
    email_service.send_welcome_email("private@example.com")
    assert timeouts == [5]
    assert "private@example.com" not in caplog.text
    assert "synthetic-secret" not in caplog.text
