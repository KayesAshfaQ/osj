"""Inbound service depends only on feature-owned repository and email ports."""

from typing import Protocol


class WaitlistRepositoryPort(Protocol):
    async def register(self, email: str) -> None: ...


class EmailPort(Protocol):
    def send_welcome(self, email: str) -> None: ...
