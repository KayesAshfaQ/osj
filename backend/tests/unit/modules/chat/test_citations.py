"""Unit tests for chat citation extraction and evidence-grounding verification."""

from __future__ import annotations

import pytest
from langchain_core.documents import Document

from app.modules.chat.citations import extract_answer_citations, verify_answer_citations
from tests.fakes import make_evidence_doc

pytestmark = pytest.mark.unit


def test_extract_answer_citations_finds_english_and_bengali_sections() -> None:
    text = "According to Section 54 of the Code of Criminal Procedure, 1898 and Article 32 of the Constitution..."
    citations = extract_answer_citations(text)
    assert len(citations) >= 2
    sec_nums = {c["section_number"] for c in citations}
    assert "54" in sec_nums
    assert "32" in sec_nums

    bengali_text = "Under Section 54 and ধারা ৩০২, police can take action."
    bengali_cites = extract_answer_citations(bengali_text)
    bengali_nums = {c["section_number"] for c in bengali_cites}
    assert "54" in bengali_nums
    assert "302" in bengali_nums


def test_verify_answer_citations_grounded_evidence_returns_valid() -> None:
    text = "Under Section 54 of CrPC, police can arrest without a warrant."
    docs = [
        Document(
            page_content="54.(1) Any police-officer may, without an order from a Magistrate and without a warrant, arrest...",
            metadata={"act_title": "The Code of Criminal Procedure, 1898", "section_number": "54"},
        )
    ]
    res = verify_answer_citations(text, docs)
    assert res["is_valid"] is True
    assert res["ungrounded_citations"] == []


def test_verify_answer_citations_hallucinated_section_returns_invalid() -> None:
    text = "According to Section 999 of the Penal Code, 1860, this is illegal."
    docs = [
        Document(
            page_content="302. Punishment for murder...",
            metadata={"act_title": "1The Penal Code, 1860", "section_number": "302"},
        )
    ]
    res = verify_answer_citations(text, docs)
    assert res["is_valid"] is False
    assert len(res["ungrounded_citations"]) >= 1
    assert res["ungrounded_citations"][0]["section_number"] == "999"


@pytest.mark.parametrize(
    "answer",
    [
        "Under Section 54 of the Penal Code, police may arrest.",
        "Under Section 99 of Another Act, police may arrest.",
        "Police can always arrest anyone.",
    ],
)
def test_unsupported_claims_are_invalid(answer: str) -> None:
    evidence = make_evidence_doc()
    assert not verify_answer_citations(answer, [evidence])["is_valid"]


def test_repeated_number_in_different_acts_is_not_deduplicated() -> None:
    evidence = make_evidence_doc()
    answer = "Section 54 of CrPC, permits arrest. Section 54 of the Penal Code, also permits arrest."
    assert not verify_answer_citations(answer, [evidence])["is_valid"]


def test_false_claim_with_real_citation_is_rejected() -> None:
    evidence = make_evidence_doc()
    answer = "Under Section 54 of the Code of Criminal Procedure, citizens must pay tax on cryptocurrency dividends."
    result = verify_answer_citations(answer, [evidence])
    assert not result["is_valid"]


@pytest.mark.parametrize(
    "citation",
    [
        "Sections 54 and 999998",
        "sections 54, 999998",
        "§54 and §999998",
        "§§54,999998",
        "ধারা ৫৪ ও ৯৯৯৯৯৮",
        "Articles 54 and 999998",
        "Sections 54-56",
    ],
)
def test_every_list_and_range_member_requires_retrieved_evidence(citation: str) -> None:
    result = verify_answer_citations(f"Section 54 permits arrest. {citation} permits arrest.", [make_evidence_doc()])
    assert result["is_valid"] is False
    assert result["ungrounded_citations"]


@pytest.mark.parametrize(
    "citation", ["Sections 54-999999999999999999999", "Sections 56-54", "Sections 54-", "Sections 54-56A"]
)
def test_ambiguous_or_unbounded_ranges_fail_closed(citation: str) -> None:
    assert not verify_answer_citations(f"Section 54 permits arrest. {citation} permits arrest.", [make_evidence_doc()])[
        "is_valid"
    ]


@pytest.mark.parametrize("citation", ["Sections 54, 55 and 56", "§§54–56", "ধারা ৫৪, ৫৫ এবং ৫৬"])
def test_grounded_lists_and_bounded_ranges_keep_exact_schema(citation: str) -> None:
    docs = [make_evidence_doc(section_number=str(number)) for number in (54, 55, 56)]
    result = verify_answer_citations(f"{citation} of CrPC permits arrest.", docs)
    assert result["is_valid"] is True
    assert [item["section_number"] for item in result["grounded_citations"]] == ["54", "55", "56"]
    assert all(set(item) == {"act_title", "section_number", "type"} for item in result["grounded_citations"])


@pytest.mark.parametrize("marker", ["Section", "Sections", "§", "§§", "ধারা"])
def test_same_number_in_wrong_act_is_checked_per_occurrence(marker: str) -> None:
    answer = f"Section 54 of CrPC permits arrest. {marker} 54 of the Penal Code permits arrest."
    result = verify_answer_citations(answer, [make_evidence_doc()])
    assert result["is_valid"] is False
    assert len(result["grounded_citations"]) == 1
    assert len(result["ungrounded_citations"]) == 1
    assert result["ungrounded_citations"][0]["act_title"] == "Penal Code"


def test_article_and_section_with_same_number_are_distinct() -> None:
    docs = [make_evidence_doc(section_number="32", act_title="Constitution of Bangladesh")]
    result = verify_answer_citations("Article 32 protects liberty. Section 32 permits arrest.", docs)
    assert result["is_valid"] is False
    assert [item["type"] for item in result["grounded_citations"]] == ["article"]
    assert [item["type"] for item in result["ungrounded_citations"]] == ["section"]


def test_citation_act_suffix_does_not_swallow_claim_prose() -> None:
    result = verify_answer_citations(
        "Section 54 of CrPC permits police to arrest without a warrant.", [make_evidence_doc()]
    )
    assert result["is_valid"] is True


def test_explicit_act_year_and_full_identity_are_required() -> None:
    docs = [make_evidence_doc(act_title="Example Act, 2020")]
    assert not verify_answer_citations("Section 54 of Example Act, 2021 permits arrest.", docs)["is_valid"]
    assert not verify_answer_citations("Section 54 of Act permits arrest.", docs)["is_valid"]


@pytest.mark.parametrize(
    "answer",
    [
        "Section 54 of CrPC permits arrest. Penal Code Section 54 permits arrest.",
        "Section 54 of CrPC permits arrest. দণ্ডবিধির ধারা ৫৪ permits arrest.",
        "Section 54 of CrPC permits arrest. ধারা ৫৪ of the Penal Code permits arrest.",
        "Section 54 of CrPC and 54 of the Penal Code permit arrest.",
        "Section 54 permits arrest. Sections 54/999998 permit arrest.",
        "Section 54 permits arrest. Sections -54 permit arrest.",
    ],
)
def test_alternate_explicit_act_and_malformed_notation_cannot_bypass_verification(answer: str) -> None:
    assert not verify_answer_citations(answer, [make_evidence_doc()])["is_valid"]


def test_unnamed_number_in_multiple_acts_is_ambiguous() -> None:
    docs = [make_evidence_doc(), make_evidence_doc(act_title="Another Act", source_id="another")]
    assert not verify_answer_citations("Section 54 permits arrest.", docs)["is_valid"]
    assert verify_answer_citations("Section 54 of CrPC permits arrest.", docs)["is_valid"]


@pytest.mark.parametrize("answer", ["CrPC Section 54 permits arrest.", "ফৌজদারি কার্যবিধির ধারা ৫৪ permits arrest."])
def test_explicit_act_prefix_remains_grounded(answer: str) -> None:
    assert verify_answer_citations(answer, [make_evidence_doc()])["is_valid"]


def test_explicit_provision_type_overrides_title_inference() -> None:
    docs = [make_evidence_doc(provision_type="article")]
    result = verify_answer_citations("Article 54 permits arrest. Section 54 permits arrest.", docs)
    assert not result["is_valid"]
    assert len(result["grounded_citations"]) == 1
    assert result["grounded_citations"][0]["type"] == "article"


@pytest.mark.parametrize("prefix", ["penal code", "PENAL CODE", "Example Act, 2021"])
def test_explicit_act_prefix_preserves_case_independence_and_year(prefix: str) -> None:
    docs = [make_evidence_doc(act_title="Example Act, 2020")]
    if "penal" in prefix.lower():
        docs = [make_evidence_doc()]
    assert not verify_answer_citations(f"{prefix} Section 54 permits arrest.", docs)["is_valid"]


def test_range_endpoint_cannot_be_partial_malformed_reference() -> None:
    docs = [make_evidence_doc(section_number=str(number)) for number in (54, 55, 56)]
    assert not verify_answer_citations("Sections 54-56/999998 permit arrest.", docs)["is_valid"]


def test_fictional_act_qualifier_is_part_of_grounded_title() -> None:
    docs = [
        make_evidence_doc(
            act_title="Synthetic Demonstration Act (fictional)",
            section_number="1",
            content="Section 1 defines a sample widget as a blue square.",
        )
    ]
    answer = "Section 1 of the Synthetic Demonstration Act (fictional) defines a sample widget as a blue square."
    result = verify_answer_citations(answer, docs)
    assert result["is_valid"] is True
    assert result["grounded_citations"][0]["act_title"] == "Synthetic Demonstration Act (fictional)"


def test_lowercase_generic_act_prefix_cannot_reuse_another_acts_number() -> None:
    answer = "Section 54 of CrPC permits arrest. example act Section 54 permits arrest."
    result = verify_answer_citations(answer, [make_evidence_doc()])
    assert result["is_valid"] is False
    assert result["ungrounded_citations"][0]["act_title"] == "example act"


@pytest.mark.parametrize("introducer", ["Under the", "According to the", "See the"])
def test_prefix_act_matching_does_not_absorb_introductory_prose(introducer: str) -> None:
    docs = [make_evidence_doc(act_title="Example Act")]
    assert verify_answer_citations(f"{introducer} Example Act Section 54 permits arrest.", docs)["is_valid"]


def test_repeated_prefix_words_do_not_block_citation_extraction() -> None:
    import subprocess
    import sys
    from pathlib import Path

    # Run outside pytest's event loop: a synchronous regex cannot be interrupted
    # by an asyncio deadline. The subprocess timeout bounds regression failures.
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from app.modules.chat.citations import extract_answer_citations; "
            "citations = extract_answer_citations(sys.stdin.read()); "
            "assert citations == [{'act_title': '', 'section_number': '54', 'type': 'section'}]",
        ],
        input="of " * 100 + "Section 54 permits arrest.",
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[4],
        timeout=5,
        check=True,
    )


@pytest.mark.parametrize(
    "title",
    ["Code of Criminal Procedure Amendment Act", "CrPC Act", "Code of Criminal Procedure example act"],
)
def test_act_alias_cannot_hide_a_longer_explicit_act_identity(title: str) -> None:
    assert not verify_answer_citations(f"Section 54 of the {title} permits arrest.", [make_evidence_doc()])["is_valid"]


def test_constitution_alias_cannot_hide_another_country() -> None:
    docs = [make_evidence_doc(section_number="32", act_title="Constitution of Bangladesh", content="Protects liberty.")]
    assert not verify_answer_citations("Article 32 of the Constitution of India protects liberty.", docs)["is_valid"]


@pytest.mark.parametrize("title", ["Constitution of India", "Penal Code of India"])
def test_prefix_country_qualifier_cannot_become_an_unnamed_citation(title: str) -> None:
    docs = [make_evidence_doc(section_number="32", act_title="Constitution of Bangladesh", content="Protects liberty.")]
    assert not verify_answer_citations(f"{title} Article 32 protects liberty.", docs)["is_valid"]
