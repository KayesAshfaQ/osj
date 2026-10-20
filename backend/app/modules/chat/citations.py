from __future__ import annotations

import re
from collections.abc import Sequence
from typing import TypedDict

from langchain_core.documents import Document

from app.modules.corpus.cross_references import normalize_bengali_numeral

STOPWORDS: frozenset[str] = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "to",
        "at",
        "in",
        "on",
        "by",
        "for",
        "from",
        "of",
        "with",
        "as",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "can",
        "will",
        "just",
        "should",
        "now",
        "section",
        "article",
        "act",
        "code",
        "law",
        "laws",
        "said",
        "shall",
        "may",
        "must",
        "provides",
        "provided",
        "state",
        "states",
        "according",
        "prescribes",
        "procedure",
        "criminal",
        "penal",
        "constitution",
        "bangladesh",
        "ধারা",
        "আইন",
        "অনুচ্ছেদ",
        "কোড",
        "বলেন",
        "অনুযায়ী",
        "অনুসারে",
    }
)


class ExtractedCitation(TypedDict):
    act_title: str
    section_number: str
    type: str


class CitationVerificationResult(TypedDict):
    is_valid: bool
    grounded_citations: list[ExtractedCitation]
    ungrounded_citations: list[ExtractedCitation]


_CITATION_MARKER = re.compile(r"\b(?:sections?|articles?|arts?\.?)(?!\w)|§{1,2}|(?:ধারা|অনুচ্ছেদ)", re.I)
_NUMBER = re.compile(r"[0-9০-৯]+[a-z]?", re.I)
_RANGE = re.compile(r"\s*(?:[-–—]|\b(?:to|through)\b|থেকে)\s*", re.I)
_LIST = re.compile(r"\s*(?:,\s*(?:(?:and|ও|এবং)\s+)?|(?:and|ও|এবং)\s+|&\s*)", re.I)
_ACT_TITLE = re.compile(
    r"(?:code of criminal procedure|crpc|penal code|constitution(?: of (?:the people's republic of )?bangladesh)?"
    r"|(?:[\w'’()-]+\s+){0,31}?(?:act|code|ordinance|rules|regulations|order))"
    r"(?:\s*,?\s*[0-9০-৯]{4})?(?:\s+\([^()\n]{1,80}\))?(?!\w)",
    re.I,
)
_ACT_PREFIX = re.compile(
    r"(?<!\w)(?P<title>(?:Code of Criminal Procedure|CrPC|Penal Code|Constitution(?: of Bangladesh)?"
    r"|ফৌজদারি কার্যবিধি|দণ্ডবিধি|সংবিধান"
    r"|[A-Z][\w’'-]*(?:\s+[A-Z][\w’'-]*){0,31}\s+(?:Act|Code|Ordinance|Rules))"
    r"(?:\s+of(?:\s+[\w'’-]+){1,16})?"
    r"(?:\s*,?\s*[0-9০-৯]{4})?(?:\s+\([^()\n]{1,80}\))?)(?:'s|এর|র)?\s*$",
    re.I,
)
# A short alias must not silently discard a longer named law (e.g. CrPC Act).
_ACT_CONTINUATION = re.compile(
    r"\s+(?:of\b|(?:[\w'’()-]+\s+){0,31}(?:act|code|ordinance|rules|regulations|order)\b)",
    re.I,
)
_MAX_RANGE_MEMBERS = 100


def _citation_numbers(text: str, start: int) -> tuple[list[str], int]:
    """Read a bounded list; malformed ranges remain unverifiable citations."""
    numbers: list[str] = []
    position = start
    if re.match(r"[-–—]\s*[0-9০-৯]", text[position:]):
        return [""], position
    while match := _NUMBER.match(text, position):
        number = normalize_bengali_numeral(match.group()).lower()
        position = match.end()
        # Do not silently validate the prefix of a malformed provision number.
        if position < len(text) and (text[position].isalnum() or text[position] in "(_/"):
            return [""], position
        range_match = _RANGE.match(text, position)
        if range_match:
            end_match = _NUMBER.match(text, range_match.end())
            if not end_match:
                return [""], range_match.end()
            end = normalize_bengali_numeral(end_match.group()).lower()
            position = end_match.end()
            if (
                not number.isdecimal()
                or not end.isdecimal()
                or len(number) > 9
                or len(end) > 9
                or not 0 <= int(end) - int(number) < _MAX_RANGE_MEMBERS
                or (position < len(text) and (text[position].isalnum() or text[position] in "(_/-–—"))
            ):
                return [""], position
            numbers.extend(str(value) for value in range(int(number), int(end) + 1))
        else:
            numbers.append(number)
        separator = _LIST.match(text, position)
        if not separator or not _NUMBER.match(text, separator.end()):
            break
        position = separator.end()
    return numbers, position


def extract_answer_citations(text: str) -> list[ExtractedCitation]:
    """Extract each occurrence, preserving provision type and explicitly named Act."""
    citations: list[ExtractedCitation] = []
    for marker in _CITATION_MARKER.finditer(text):
        start = marker.end()
        while start < len(text) and text[start].isspace():
            start += 1
        prefix = _ACT_PREFIX.search(text[: marker.start()])
        prefix_title = (
            re.sub(r"^(?:(?:under|according\s+to|see|the)\s+)+", "", prefix.group("title"), flags=re.I)
            if prefix
            else ""
        )
        ctype = "article" if marker.group().lower().startswith("art") or marker.group() == "অনুচ্ছেদ" else "section"
        while True:
            numbers, end = _citation_numbers(text, start)
            if not numbers:
                break
            act_title = prefix_title
            suffix = re.match(r"\s+of\s+(?:the\s+)?", text[end:], re.I)
            if suffix:
                title_start = end + suffix.end()
                title = _ACT_TITLE.match(text, title_start)
                if title and _ACT_CONTINUATION.match(text, title.end()):
                    title = None
                # An unrecognized explicit title cannot become an unnamed citation.
                act_title = title.group().strip() if title else text[title_start:].split(".", 1)[0].strip() or "?"
                end = title.end() if title else len(text)
                if prefix_title and _act_identity(prefix_title) != _act_identity(act_title):
                    numbers = [""]
            citations.extend({"act_title": act_title, "section_number": number, "type": ctype} for number in numbers)
            # An Act-qualified list item can introduce a differently qualified item.
            separator = _LIST.match(text, end)
            if not separator or not _NUMBER.match(text, separator.end()):
                break
            start = separator.end()
    return citations


def _act_identity(title: str) -> tuple[str, str]:
    normalized = normalize_bengali_numeral(title).lower().strip()
    normalized = re.sub(r"^\d*(?:the\s+)?", "", normalized)
    year = re.search(r"\b(\d{4})\b", normalized)
    name = re.sub(r"[\s,]*(?:\d{4})\s*$", "", normalized).strip()
    aliases = {
        "crpc": "code of criminal procedure",
        "ফৌজদারি কার্যবিধি": "code of criminal procedure",
        "দণ্ডবিধি": "penal code",
        "সংবিধান": "constitution",
        "constitution of bangladesh": "constitution",
        "constitution of the people's republic of bangladesh": "constitution",
    }
    return aliases.get(name, name), year.group(1) if year else ""


def _provision_type(metadata: dict[str, object]) -> str:
    explicit = metadata.get("provision_type") or metadata.get("citation_type")
    if explicit:
        return str(explicit).lower()
    return "article" if _act_identity(str(metadata.get("act_title", "")))[0] == "constitution" else "section"


def has_evidence_support(answer_text: str, docs: Sequence[Document]) -> bool:
    """Verify that substantive claims in answer_text have lexical overlap with context docs."""
    answer_words = {
        w for w in re.findall(r"[\w\u0980-\u09FF]+", answer_text.lower()) if len(w) > 2 and w not in STOPWORDS
    }
    if not answer_words:
        return True

    doc_words = {
        w
        for doc in docs
        for w in re.findall(r"[\w\u0980-\u09FF]+", doc.page_content.lower())
        if len(w) > 2 and w not in STOPWORDS
    }
    overlap = answer_words & doc_words
    if len(answer_words) >= 4:
        return len(overlap) >= 1 and (len(overlap) / len(answer_words) >= 0.15 or len(overlap) >= 2)
    return len(overlap) >= 1


def verify_answer_citations(answer_text: str, context_docs: Sequence[Document]) -> CitationVerificationResult:
    """Verify every citation in answer_text against the provided context_docs."""
    citations = extract_answer_citations(answer_text)
    if not citations:
        return {
            "is_valid": False,
            "grounded_citations": [],
            "ungrounded_citations": [],
        }

    grounded: list[ExtractedCitation] = []
    ungrounded: list[ExtractedCitation] = []

    for cite in citations:
        matching_docs: list[Document] = []
        requested_name, requested_year = _act_identity(cite["act_title"])
        for doc in context_docs:
            meta = doc.metadata or {}
            number = normalize_bengali_numeral(str(meta.get("section_number") or "").strip()).lower()
            title = str(meta.get("act_title") or "").strip()
            if not number or not title or number != cite["section_number"] or _provision_type(meta) != cite["type"]:
                continue
            name, year = _act_identity(title)
            if requested_name and (name != requested_name or (requested_year and year != requested_year)):
                continue
            matching_docs.append(doc)
        identities = {_act_identity(str(doc.metadata["act_title"])) for doc in matching_docs}
        if matching_docs and len(identities) == 1 and has_evidence_support(answer_text, matching_docs):
            grounded.append(cite)
        else:
            ungrounded.append(cite)

    is_valid = len(ungrounded) == 0

    return {
        "is_valid": is_valid,
        "grounded_citations": grounded,
        "ungrounded_citations": ungrounded,
    }
