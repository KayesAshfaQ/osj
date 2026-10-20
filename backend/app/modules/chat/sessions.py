"""Redis-backed anonymous chat sessions with bounded sanitized history."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol, cast

from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError

from app.modules.chat.privacy import sanitize

TTL_SECONDS = 86400
LEASE_TTL_SECONDS = 35
MAX_TURNS = 10
MAX_CHARS = 20000


class SessionMissing(Exception):
    pass


class CorruptSession(ValueError):
    pass


class SessionBusy(Exception):
    pass


class QuotaExceeded(Exception):
    pass


class HistoryTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: StrictStr
    answer: StrictStr
    outcome: Literal["answered", "refused"]


@dataclass(frozen=True)
class IssuedSession:
    token: str
    expires_at: datetime


class RedisPrimitives(Protocol):
    async def set(self, name: str, value: str, *, ex: int | None = None, nx: bool = False) -> object: ...
    async def get(self, name: str) -> str | bytes | None: ...
    async def expire(self, name: str, time: int) -> object: ...
    async def delete(self, name: str) -> object: ...
    async def eval(self, script: str, numkeys: int, *keys_and_args: str) -> object: ...
    async def incr(self, name: str) -> int: ...
    async def ping(self) -> object: ...


_RELEASE_LEASE = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
end
return 0
"""


class AnonymousSessions:
    def __init__(self, redis: RedisPrimitives) -> None:
        self.redis = redis

    @staticmethod
    def _identifier(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _key(self, token: str) -> str:
        return f"chat:session:{self._identifier(token)}"

    async def issue(self) -> IssuedSession:
        token = secrets.token_urlsafe(32)
        issued = IssuedSession(token, datetime.now(UTC) + timedelta(seconds=TTL_SECONDS))
        await self.redis.set(self._key(token), "[]", ex=TTL_SECONDS)
        return issued

    async def history(self, token: str) -> list[dict[str, str]]:
        key = self._key(token)
        raw = await self.redis.get(key)
        if raw is None:
            raise SessionMissing
        await self.redis.expire(key, TTL_SECONDS)
        try:
            parsed: object = json.loads(raw)
            if not isinstance(parsed, list):
                raise CorruptSession("Invalid session data")
            items = cast(list[object], parsed)
            if len(items) > MAX_TURNS:
                raise CorruptSession("Invalid session data")
            turns = [HistoryTurn.model_validate(turn) for turn in items]
        except (TypeError, ValidationError, json.JSONDecodeError) as exc:
            raise CorruptSession("Invalid session data") from exc
        if sum(len(json.dumps(turn.model_dump(), ensure_ascii=False)) for turn in turns) > MAX_CHARS:
            raise CorruptSession("Invalid session data")
        return [
            {"query": sanitize(turn.query), "answer": sanitize(turn.answer), "outcome": turn.outcome} for turn in turns
        ]

    async def begin(self, token: str) -> str:
        await self.history(token)
        lease = secrets.token_urlsafe(16)
        if not await self.redis.set(f"{self._key(token)}:lease", lease, ex=LEASE_TTL_SECONDS, nx=True):
            raise SessionBusy
        return lease

    async def check_limits(self, token: str | None, address: str) -> None:
        salt_key = "chat:peer:salt"
        await self.redis.set(salt_key, secrets.token_hex(32), nx=True)
        salt = await self.redis.get(salt_key)
        if salt is None:
            raise CorruptSession("Peer quota salt unavailable")
        salt_bytes = salt.encode() if isinstance(salt, str) else salt
        peer = hmac.new(salt_bytes, address.encode(), hashlib.sha256).hexdigest()
        for key, maximum in ((f"chat:limit:peer:{peer}", 30),):
            value = await self.redis.incr(key)
            if value == 1:
                await self.redis.expire(key, 60)
            if value > maximum:
                raise QuotaExceeded
        if token is not None:
            key = f"chat:limit:session:{self._identifier(token)}"
            value = await self.redis.incr(key)
            if value == 1:
                await self.redis.expire(key, 60)
            if value > 10:
                raise QuotaExceeded

    async def end(self, token: str, lease: str) -> None:
        await self.redis.eval(_RELEASE_LEASE, 1, f"{self._key(token)}:lease", lease)

    async def append(self, token: str, query: str, outcome: str, answer: str) -> None:
        history = await self.history(token)
        history.append({"query": sanitize(query), "outcome": outcome, "answer": sanitize(answer)})
        while (
            len(history) > MAX_TURNS or sum(len(json.dumps(item, ensure_ascii=False)) for item in history) > MAX_CHARS
        ):
            history.pop(0)
        await self.redis.set(self._key(token), json.dumps(history, ensure_ascii=False), ex=TTL_SECONDS)

    async def delete(self, token: str) -> None:
        await self.history(token)
        await self.redis.delete(self._key(token))
