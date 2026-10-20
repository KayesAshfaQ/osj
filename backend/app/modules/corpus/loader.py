"""Data loading and normalization for legal datasets."""

from __future__ import annotations

import json
import logging
from typing import cast

from app.modules.corpus.cross_references import extract_section_number_from_content
from app.modules.corpus.domain import LegalDocument
from app.modules.corpus.identity import source_identity

logger = logging.getLogger(__name__)

MAX_FOOTNOTE_CHARS = 500


def load_constitution_documents(path: str) -> list[LegalDocument]:
    """Load the Bangladesh Constitution dataset."""
    with open(path, encoding="utf-8") as fh:
        raw_data: object = json.load(fh)

    data: list[dict[str, object]] = (
        [cast(dict[str, object], d) for d in cast(list[object], raw_data) if isinstance(d, dict)]
        if isinstance(raw_data, list)
        else []
    )

    documents: list[LegalDocument] = []
    for item in data:
        content_en = str(item.get("content") or "").strip()
        content_bn = str(item.get("article_bn") or "").strip()
        combined = f"{content_en}\n\n{content_bn}".strip()

        if not combined:
            logger.warning("Skipping constitution article with empty content: %s", item)
            continue

        doc = LegalDocument(
            content=combined,
            source_type="constitution",
            act_title=str(item.get("law_name_en") or "The Constitution of Bangladesh"),
            act_no="",
            act_year="1972",
            section_number=str(item.get("section_no_en") or ""),
            section_title=str(item.get("article_name_en") or ""),
            language="english",
            is_repealed=False,
            governing_regime="",
            legal_system="Constitutional Law",
            source_url="",
            footnotes="",
            source_id="bd-constitution",
        )
        documents.append(doc)

    logger.info("Loaded %d constitution articles from %s", len(documents), path)
    return documents


def _build_footnote_text(footnotes: list[object], max_chars: int = MAX_FOOTNOTE_CHARS) -> str:
    texts: list[str] = []
    current_len = 0

    for fn in footnotes:
        if not isinstance(fn, dict):
            continue
        fn_dict = cast(dict[str, object], fn)
        text = str(fn_dict.get("footnote_text") or "").strip()
        if not text:
            continue

        if current_len + len(text) + 3 > max_chars:
            remaining = max_chars - current_len - 3
            if remaining > 20:
                texts.append(text[:remaining] + "...")
            break

        texts.append(text)
        current_len += len(text) + 3

    return " | ".join(texts)


def _extract_governing_regime(govt_ctx: dict[str, object]) -> str:
    if not govt_ctx:
        return ""
    parts: list[str] = []
    if govt_ctx.get("govt_system"):
        parts.append(str(govt_ctx["govt_system"]))
    if govt_ctx.get("head_govt_name"):
        parts.append(f"under {govt_ctx['head_govt_name']}")
    if govt_ctx.get("period_years"):
        parts.append(f"({govt_ctx['period_years']})")
    return " ".join(parts)


def _extract_legal_system(legal_ctx: dict[str, object]) -> str:
    if not legal_ctx:
        return ""

    period_info = legal_ctx.get("period_info")
    if isinstance(period_info, dict):
        period_name = cast(dict[str, object], period_info).get("period_name")
        if period_name:
            return str(period_name)

    framework = legal_ctx.get("legal_framework")
    if isinstance(framework, str):
        return framework
    elif isinstance(framework, dict):
        framework_dict = cast(dict[str, object], framework)
        basis = framework_dict.get("legal_basis")
        if basis:
            return str(basis)
        laws = framework_dict.get("primary_laws")
        if isinstance(laws, list):
            return ", ".join(str(x) for x in cast(list[object], laws)[:3])
        return ""

    return ""


def load_legal_acts_documents(path: str) -> list[LegalDocument]:
    """Load the Contextualized Bangladesh Legal Acts dataset."""
    with open(path, encoding="utf-8") as fh:
        raw_data: object = json.load(fh)

    data = cast(dict[str, object], raw_data) if isinstance(raw_data, dict) else {}
    raw_acts = data.get("acts")
    acts: list[dict[str, object]] = (
        [cast(dict[str, object], a) for a in cast(list[object], raw_acts) if isinstance(a, dict)]
        if isinstance(raw_acts, list)
        else []
    )
    documents: list[LegalDocument] = []

    seen_sources: dict[str, tuple[str, str, str]] = {}
    for act in acts:
        identity = source_identity(act)
        signature = (str(act.get("act_title") or ""), str(act.get("act_year") or ""), str(act.get("act_no") or ""))
        if identity in seen_sources and seen_sources[identity] != signature:
            raise ValueError(f"Source identity collision: {identity}")
        seen_sources[identity] = signature
        act_title = str(act.get("act_title") or "").strip()
        act_no = str(act.get("act_no") or "").strip()
        act_year = str(act.get("act_year") or "").strip()
        language = str(act.get("language") or "english").strip().lower()
        source_url = str(act.get("source_url") or "").strip()

        raw_csv_meta = act.get("csv_metadata")
        csv_meta = cast(dict[str, object], raw_csv_meta) if isinstance(raw_csv_meta, dict) else {}
        is_repealed: bool = bool(csv_meta.get("is_repealed", False))

        raw_gov = act.get("government_context")
        governing_regime = _extract_governing_regime(
            cast(dict[str, object], raw_gov) if isinstance(raw_gov, dict) else {}
        )
        raw_legal = act.get("legal_system_context")
        legal_system = _extract_legal_system(cast(dict[str, object], raw_legal) if isinstance(raw_legal, dict) else {})
        raw_footnotes = act.get("footnotes")
        footnote_text = _build_footnote_text(
            cast(list[object], raw_footnotes) if isinstance(raw_footnotes, list) else []
        )

        raw_sections = act.get("sections")
        sections: list[dict[str, object]] = (
            [cast(dict[str, object], s) for s in cast(list[object], raw_sections) if isinstance(s, dict)]
            if isinstance(raw_sections, list)
            else []
        )
        if not sections:
            continue

        for idx, section in enumerate(sections):
            section_content = str(section.get("section_content") or "").strip()
            if not section_content:
                continue

            extracted_sec_num = extract_section_number_from_content(section_content)
            sec_num = extracted_sec_num if extracted_sec_num else str(idx + 1)

            doc = LegalDocument(
                content=section_content,
                source_type="legal_act",
                act_title=act_title,
                act_no=act_no,
                act_year=act_year,
                section_number=sec_num,
                section_title="",
                language=language,
                is_repealed=is_repealed,
                governing_regime=governing_regime,
                legal_system=legal_system,
                source_url=source_url,
                footnotes=footnote_text,
                source_id=identity,
            )
            documents.append(doc)

    logger.info("Loaded %d section documents from %s", len(documents), path)
    return documents


def load_all_documents(
    constitution_path: str,
    legal_acts_path: str,
) -> list[LegalDocument]:
    """Load and combine documents from both Constitution and Legal Acts datasets."""
    constitution_docs = load_constitution_documents(constitution_path)
    legal_acts_docs = load_legal_acts_documents(legal_acts_path)

    all_docs = constitution_docs + legal_acts_docs
    logger.info(
        "Total documents loaded: %d (%d constitution + %d legal act sections)",
        len(all_docs),
        len(constitution_docs),
        len(legal_acts_docs),
    )
    return all_docs
