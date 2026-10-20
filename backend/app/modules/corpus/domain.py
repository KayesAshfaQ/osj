"""Domain models and value objects for legal corpus documents."""

from dataclasses import dataclass


@dataclass
class LegalDocument:
    """Normalized domain representation of a single legal provision."""

    content: str
    source_type: str
    act_title: str
    act_no: str
    act_year: str
    section_number: str
    section_title: str
    language: str
    is_repealed: bool
    governing_regime: str
    legal_system: str
    source_url: str
    footnotes: str
    source_id: str = ""


@dataclass(frozen=True)
class CrossReferenceItem:
    """A cross-reference link discovered within statutory text."""

    target_act_title: str
    target_section_number: str
    relation: str = "cites"


@dataclass(frozen=True)
class ParentEvidence:
    source_id: str
    act_title: str
    section_number: str
    content: str
    source_url: str | None = None
