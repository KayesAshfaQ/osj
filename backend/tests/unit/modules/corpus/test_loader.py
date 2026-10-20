"""Unit tests for corpus document loaders (Constitution, Acts, and combined datasets)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

from app.modules.corpus.loader import (
    LegalDocument,
    _build_footnote_text,
    _extract_legal_system,
    load_all_documents,
    load_constitution_documents,
    load_legal_acts_documents,
)

pytestmark = pytest.mark.unit

CONSTITUTION_DATA = [
    {
        "law_name_en": "The Constitution of the People's Republic of Bangladesh",
        "law_name_bn": "গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধান",
        "part_no_en": "Part I",
        "part_name_en": "THE REPUBLIC",
        "article_name_en": "The Republic",
        "article_name_bn": "প্রজাতন্ত্র",
        "section_no_en": "1",
        "section_no_bn": "১",
        "article_bn": "১৷ বাংলাদেশ একটি একক, স্বাধীন ও সার্বভৌম প্রজাতন্ত্র।",
        "content": "1. Bangladesh is a unitary, independent, sovereign Republic.",
    },
    {
        "law_name_en": "The Constitution of the People's Republic of Bangladesh",
        "law_name_bn": "গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধান",
        "part_no_en": "Part I",
        "part_name_en": "THE REPUBLIC",
        "article_name_en": "The state religion",
        "article_name_bn": "রাষ্ট্রধর্ম",
        "section_no_en": "2A",
        "section_no_bn": "২ক",
        "article_bn": "২ক। প্রজাতন্ত্রের রাষ্ট্রধর্ম ইসলাম।",
        "content": "2A. The state religion of the Republic is Islam.",
    },
]

LEGAL_ACTS_DATA = {
    "dataset_info": {
        "name": "Bangladesh Legal Acts Dataset",
        "total_acts": 2,
    },
    "acts": [
        {
            "act_title": "The Penal Code, 1860",
            "act_no": "XLV",
            "act_year": "1860",
            "publication_date": "1860-10-06",
            "language": "english",
            "token_count": 15420,
            "source_url": "http://bdlaws.minlaw.gov.bd/act-11.html",
            "source_file": "act-print-11.json",
            "fetch_timestamp": "2025-07-19 02:45:32",
            "csv_metadata": {
                "act_title_from_csv": "The Penal Code, 1860",
                "act_no_from_csv": "XLV",
                "act_year_from_csv": "1860",
                "is_repealed": False,
            },
            "sections": [
                {"section_content": "This Act shall be called the Penal Code."},
                {"section_content": "Every person shall be liable to punishment under this Code."},
            ],
            "footnotes": [
                {"footnote_text": "The word 'Bangladesh' was substituted for 'Pakistan' by Act VIII of 1973."},
            ],
            "government_context": {
                "govt_system": "Company Rule",
                "head_govt_name": "Lord Canning",
                "head_govt_designation": "Governor-General",
                "how_got_power": "Company appointment",
                "period_years": "1856-1862",
                "years_in_power": 6,
            },
            "legal_system_context": {
                "legal_framework": {
                    "primary_laws": ["Regulating Act 1773", "Bengal Regulations"],
                    "legal_basis": "Hybrid of British common law and Islamic/Hindu personal law",
                },
                "government_system": "Colonial Administration",
                "period_info": {
                    "period_name": "East India Company Rule",
                    "year_range": "1773-1858",
                },
                "key_characteristics": ["British Crown rule"],
            },
            "processing_info": {},
            "copyright_info": "",
        },
        {
            "act_title": "The Powers-of-Attorney Act, 1882",
            "act_no": "VII",
            "act_year": "1882",
            "publication_date": "1882-01-01",
            "language": "english",
            "token_count": 500,
            "source_url": "http://bdlaws.minlaw.gov.bd/act-50.html",
            "source_file": "act-print-50.json",
            "fetch_timestamp": "2025-07-19 02:45:32",
            "csv_metadata": {
                "act_title_from_csv": "The Powers-of-Attorney Act, 1882 [Repealed]",
                "act_no_from_csv": "VII",
                "act_year_from_csv": "1882",
                "is_repealed": True,
            },
            "sections": [
                {"section_content": "This Act may be cited as the Powers-of-Attorney Act, 1882."},
            ],
            "footnotes": [],
            "government_context": {},
            "legal_system_context": {},
            "processing_info": {},
            "copyright_info": "",
        },
    ],
}


def _write_json(tmp_path: Path, filename: str, content: Any) -> Path:
    p = tmp_path / filename
    p.write_text(json.dumps(content), encoding="utf-8")
    return p


def test_load_constitution_returns_list_of_legal_documents(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "constitution.json", CONSTITUTION_DATA)
    docs = load_constitution_documents(str(path))
    assert isinstance(docs, list)
    assert all(isinstance(d, LegalDocument) for d in docs)
    assert len(docs) == 2


def test_load_constitution_metadata_fields(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "constitution.json", CONSTITUTION_DATA)
    docs = load_constitution_documents(str(path))
    doc = docs[0]
    assert doc.source_type == "constitution"
    assert doc.act_title == "The Constitution of the People's Republic of Bangladesh"
    assert doc.section_number == "1"
    assert doc.section_title == "The Republic"
    assert doc.language == "english"
    assert doc.is_repealed is False
    assert "Bangladesh is a unitary" in doc.content
    assert "বাংলাদেশ একটি" in doc.content


def test_load_constitution_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_constitution_documents("/non/existent/path.json")


def test_load_constitution_invalid_json(tmp_path: Path) -> None:
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_constitution_documents(str(bad_path))


def test_load_legal_acts_returns_list_of_legal_documents(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    assert isinstance(docs, list)
    assert all(isinstance(d, LegalDocument) for d in docs)
    assert len(docs) == 3


def test_load_legal_acts_metadata_fields(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    doc = docs[0]
    assert doc.source_type == "legal_act"
    assert doc.act_title == "The Penal Code, 1860"
    assert doc.act_no == "XLV"
    assert doc.act_year == "1860"
    assert doc.language == "english"
    assert doc.is_repealed is False
    assert doc.source_url == "http://bdlaws.minlaw.gov.bd/act-11.html"


def test_load_legal_acts_repealed_flag_from_csv_metadata(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    repealed_doc = docs[-1]
    assert repealed_doc.act_title == "The Powers-of-Attorney Act, 1882"
    assert repealed_doc.is_repealed is True


def test_load_legal_acts_footnotes_appended_to_content(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    penal_docs = [d for d in docs if d.act_title == "The Penal Code, 1860"]
    assert any("Bangladesh" in d.footnotes for d in penal_docs)


def test_load_legal_acts_government_context_captured(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    doc = docs[0]
    assert "Company Rule" in doc.governing_regime or "Lord Canning" in doc.governing_regime


def test_load_legal_acts_legal_system_context_captured(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_legal_acts_documents(str(path))
    doc = docs[0]
    assert isinstance(doc.legal_system, str)
    assert "East India Company Rule" in doc.legal_system or "British" in doc.legal_system


def test_extract_legal_system_handles_dict() -> None:
    legal_ctx: dict[str, object] = {
        "legal_framework": {
            "primary_laws": ["Regulating Act 1773"],
            "legal_basis": "Hybrid of British law",
        }
    }
    res = _extract_legal_system(legal_ctx)
    assert isinstance(res, str)
    assert res == "Hybrid of British law"


def test_build_footnote_text_caps_at_max_chars() -> None:
    long_fns: list[object] = [{"footnote_text": "Footnote word " * 50} for _ in range(20)]
    res = _build_footnote_text(long_fns, max_chars=100)
    assert isinstance(res, str)
    assert len(res) <= 110


def test_load_legal_acts_handles_empty_sections(tmp_path: Path) -> None:
    data: dict[str, object] = dict(LEGAL_ACTS_DATA)
    acts = cast(list[dict[str, object]], LEGAL_ACTS_DATA["acts"])
    data["acts"] = [{**acts[0], "sections": [], "footnotes": []}]
    path = _write_json(tmp_path, "acts.json", data)
    docs = load_legal_acts_documents(str(path))
    assert docs == []


def test_load_legal_acts_handles_missing_optional_fields(tmp_path: Path) -> None:
    minimal_act = {
        "act_title": "Minimal Act",
        "act_no": "I",
        "act_year": "2000",
        "publication_date": "",
        "language": "english",
        "token_count": 10,
        "source_url": "",
        "source_file": "",
        "fetch_timestamp": "",
        "csv_metadata": {"is_repealed": False},
        "sections": [{"section_content": "Some content here."}],
        "footnotes": [],
    }
    data = {"dataset_info": {}, "acts": [minimal_act]}
    path = _write_json(tmp_path, "acts.json", data)
    docs = load_legal_acts_documents(str(path))
    assert len(docs) == 1
    assert docs[0].governing_regime == ""
    assert docs[0].legal_system == ""


def test_load_legal_acts_skips_empty_section_content(tmp_path: Path) -> None:
    acts = cast(list[dict[str, object]], LEGAL_ACTS_DATA["acts"])
    data = {
        "dataset_info": {},
        "acts": [
            {
                **acts[0],
                "sections": [
                    {"section_content": ""},
                    {"section_content": "   "},
                    {"section_content": "Real content here."},
                ],
                "footnotes": [],
            }
        ],
    }
    path = _write_json(tmp_path, "acts.json", data)
    docs = load_legal_acts_documents(str(path))
    assert len(docs) == 1
    assert "Real content" in docs[0].content


def test_load_legal_acts_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_legal_acts_documents("/non/existent/acts.json")


def test_load_all_documents_combines_both_sources(tmp_path: Path) -> None:
    const_path = _write_json(tmp_path, "constitution.json", CONSTITUTION_DATA)
    acts_path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    docs = load_all_documents(
        constitution_path=str(const_path),
        legal_acts_path=str(acts_path),
    )
    source_types = {d.source_type for d in docs}
    assert "constitution" in source_types
    assert "legal_act" in source_types
    assert len(docs) == 5


def test_load_all_documents_constitution_not_found_raises(tmp_path: Path) -> None:
    acts_path = _write_json(tmp_path, "acts.json", LEGAL_ACTS_DATA)
    with pytest.raises(FileNotFoundError):
        load_all_documents(
            constitution_path="/bad/path.json",
            legal_acts_path=str(acts_path),
        )


def test_loader_preserves_explicit_source_and_rejects_collision(tmp_path: Path) -> None:
    path = tmp_path / "acts.json"
    acts = [
        {
            "source_id": "same",
            "act_title": "Act A",
            "act_year": 2000,
            "sections": [{"section_content": "54. First text"}],
        },
        {
            "source_id": "same",
            "act_title": "Act B",
            "act_year": 2001,
            "sections": [{"section_content": "54. Other text"}],
        },
    ]
    path.write_text(json.dumps({"acts": acts}))
    with pytest.raises(ValueError, match="collision"):
        load_legal_acts_documents(str(path))
    acts[1]["source_id"] = "different"
    path.write_text(json.dumps({"acts": acts}))
    documents = load_legal_acts_documents(str(path))
    assert [doc.source_id for doc in documents] == ["same", "different"]
