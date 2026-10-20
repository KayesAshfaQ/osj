from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from langchain_core.documents import Document

from app.modules.chat.schemas import ChatAnswer, SourceReference
from app.modules.corpus.domain import LegalDocument


class FakeRedis:
    """In-memory Redis fake for testing anonymous session management."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    async def set(self, name: str, value: str, *, ex: int | None = None, nx: bool = False) -> bool:
        if nx and name in self.values:
            return False
        self.values[name] = value
        if ex:
            self.ttls[name] = ex
        return True

    async def get(self, name: str) -> str | None:
        return self.values.get(name)

    async def expire(self, name: str, time: int) -> bool:
        if name not in self.values:
            return False
        self.ttls[name] = time
        return True

    async def delete(self, name: str) -> int:
        self.values.pop(name, None)
        return 1

    async def eval(self, script: str, numkeys: int, *keys_and_args: str) -> object:
        if len(keys_and_args) >= 2 and self.values.get(keys_and_args[0]) == keys_and_args[1]:
            await self.delete(keys_and_args[0])
            return 1
        return 0

    async def incr(self, name: str) -> int:
        value = int(self.values.get(name, "0")) + 1
        self.values[name] = str(value)
        return value

    async def ping(self) -> bool:
        return True


class FakeChatService:
    """Fake ChatService implementing answer & admit protocols for HTTP tests."""

    def __init__(
        self,
        answer_text: str = "Section 54 permits arrest.",
        outcome: Literal["answered", "refused"] = "answered",
    ) -> None:
        self.calls: list[str] = []
        self.answer_text = answer_text
        self.outcome: Literal["answered", "refused"] = outcome

    async def answer(
        self,
        query: str,
        *,
        token: str | None = None,
        address: str = "",
        admitted: bool = False,
        lease: str | None = None,
    ) -> ChatAnswer:
        self.calls.append(query)
        sources: list[SourceReference] = (
            [SourceReference(source_id="crpc", act_title="CrPC", section_number="54")]
            if self.outcome == "answered"
            else []
        )
        return ChatAnswer(
            request_id="req-1",
            outcome=self.outcome,
            answer=self.answer_text,
            sources=sources,
        )

    async def admit(self, *, token: str | None = None, address: str = "") -> None:
        return None


@dataclass
class FakeWaitlistRepository:
    """In-memory waitlist repository test double."""

    emails: set[str]

    async def register(self, email: str) -> None:
        from app.modules.waitlist.domain import DuplicateEmail

        if email in self.emails:
            raise DuplicateEmail
        self.emails.add(email)


def make_evidence_doc(
    content: str = "Police may arrest. See Section 99 of Another Act.",
    source_id: str = "crpc",
    act_title: str = "Code of Criminal Procedure",
    section_number: str = "54",
    **extra_metadata: Any,
) -> Document:
    metadata: dict[str, Any] = {
        "source_id": source_id,
        "act_title": act_title,
        "section_number": section_number,
        **extra_metadata,
    }
    return Document(page_content=content, metadata=metadata)


def make_legal_doc(
    content: str = "Some legal content here.",
    source_type: str = "legal_act",
    act_title: str = "The Penal Code, 1860",
    act_no: str = "XLV",
    act_year: str = "1860",
    section_number: str = "1",
    section_title: str = "",
    language: str = "english",
    is_repealed: bool = False,
    governing_regime: str = "British Colonial",
    legal_system: str = "British Colonial Legal System",
    source_url: str = "http://bdlaws.minlaw.gov.bd/act-11.html",
    footnotes: str = "",
    source_id: str = "act-1",
) -> LegalDocument:
    return LegalDocument(
        content=content,
        source_type=source_type,
        act_title=act_title,
        act_no=act_no,
        act_year=act_year,
        section_number=section_number,
        section_title=section_title,
        language=language,
        is_repealed=is_repealed,
        governing_regime=governing_regime,
        legal_system=legal_system,
        source_url=source_url,
        footnotes=footnotes,
        source_id=source_id,
    )
