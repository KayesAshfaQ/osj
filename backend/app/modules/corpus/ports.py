from __future__ import annotations

from typing import Protocol


class CorpusRepositoryPort(Protocol):
    """Abstraction for saving legal acts into staging and parent-document stores."""

    async def save_act(
        self,
        source_id: str,
        source_type: str,
        act_title: str,
        act_year: str,
        raw_json_str: str,
        sections_count: int,
        parent_chunks: list[dict[str, object]],
        cross_references: list[dict[str, object]],
    ) -> dict[str, object]: ...

    async def rollback(self) -> None: ...
