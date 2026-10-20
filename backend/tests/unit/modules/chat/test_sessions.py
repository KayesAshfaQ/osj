"""Unit tests for anonymous chat session management, bearer tokens, TTL, and rate limits."""

from __future__ import annotations

import json

import pytest

from app.modules.chat.sessions import AnonymousSessions, QuotaExceeded, SessionBusy, SessionMissing
from tests.fakes import FakeRedis

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_random_tokens_are_hashed_and_history_bounded(fake_redis: FakeRedis) -> None:
    sessions = AnonymousSessions(fake_redis)
    first = await sessions.issue()
    second = await sessions.issue()
    assert first.token != second.token
    assert len(first.token) >= 43
    assert first.token not in str(fake_redis.values)
    lease = await sessions.begin(first.token)
    for number in range(12):
        await sessions.append(first.token, f"email: user{number}@example.com", "answered", "Section 54")
    await sessions.end(first.token, lease)
    history = await sessions.history(first.token)
    assert len(history) == 10
    assert "user" not in json.dumps(history)
    assert await sessions.history(second.token) == []
    assert all(
        ttl == 86400
        for key, ttl in fake_redis.ttls.items()
        if key.startswith("chat:session:") and not key.endswith(":lease")
    )
    assert fake_redis.ttls[f"{sessions._key(first.token)}:lease"] == 35


@pytest.mark.asyncio
async def test_expired_and_overlapping_sessions(fake_redis: FakeRedis) -> None:
    sessions = AnonymousSessions(fake_redis)
    issued = await sessions.issue()
    lease = await sessions.begin(issued.token)
    with pytest.raises(SessionBusy):
        await sessions.begin(issued.token)
    await sessions.end(issued.token, lease)
    fake_redis.values.clear()
    with pytest.raises(SessionMissing):
        await sessions.history(issued.token)


@pytest.mark.asyncio
async def test_session_and_peer_limits_are_enforced(fake_redis: FakeRedis) -> None:
    sessions = AnonymousSessions(fake_redis)
    issued = await sessions.issue()
    for _ in range(10):
        await sessions.check_limits(issued.token, "192.0.2.1")
    with pytest.raises(QuotaExceeded):
        await sessions.check_limits(issued.token, "192.0.2.1")
    assert "192.0.2.1" not in str(fake_redis.values)


@pytest.mark.asyncio
async def test_corrupt_history_is_rejected_before_generation(fake_redis: FakeRedis) -> None:
    sessions = AnonymousSessions(fake_redis)
    issued = await sessions.issue()
    fake_redis.values[sessions._key(issued.token)] = '[{"query": 42, "answer": "x", "outcome": "answered"}]'
    with pytest.raises(ValueError):
        await sessions.history(issued.token)


@pytest.mark.asyncio
async def test_peer_limit_is_shared_across_workers(fake_redis: FakeRedis) -> None:
    first = AnonymousSessions(fake_redis)
    second = AnonymousSessions(fake_redis)
    for _ in range(15):
        await first.check_limits(None, "192.0.2.1")
        await second.check_limits(None, "192.0.2.1")
    with pytest.raises(QuotaExceeded):
        await first.check_limits(None, "192.0.2.1")
