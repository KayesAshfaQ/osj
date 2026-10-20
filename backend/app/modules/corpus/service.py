from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import cast

from app.modules.corpus.cross_references import (
    extract_cross_references,
    extract_section_number_from_content,
    generate_deterministic_chunk_id,
)
from app.modules.corpus.identity import provision_identity, source_identity
from app.modules.corpus.ports import CorpusRepositoryPort

logger = logging.getLogger(__name__)


class CorpusIngestionService:
    """Orchestrates parsing and persisting raw legal Acts into staging and parent stores."""

    def __init__(self, repository: CorpusRepositoryPort) -> None:
        self.repository = repository

    async def rollback(self) -> None:
        await self.repository.rollback()

    async def ingest_act(
        self,
        source_id: str,
        source_type: str,
        act_json: Mapping[str, object],
    ) -> dict[str, object]:
        """Ingest a raw legal Act JSON into staging and parent chunk stores."""
        if act_json.get("source_id") or act_json.get("id") or act_json.get("source_url"):
            if source_identity(act_json) != source_id:
                raise ValueError("Dataset source identity differs from supplied identity")
        act_title = str(act_json.get("act_title") or act_json.get("law_name_en") or "Unknown Act")
        act_year = str(act_json.get("act_year") or "")
        raw_sections = act_json.get("sections")
        sections: list[dict[str, object]] = []
        if isinstance(raw_sections, list):
            for sec_item in cast(list[object], raw_sections):
                if isinstance(sec_item, dict):
                    sections.append({str(k): v for k, v in cast(dict[object, object], sec_item).items()})

        raw_json_str = json.dumps(dict(act_json), ensure_ascii=False)

        parsed_chunks: list[dict[str, object]] = []
        parsed_refs: list[dict[str, object]] = []

        for idx, sec_obj in enumerate(sections):
            raw_sec_content = str(sec_obj.get("section_content") or "").strip()
            if not raw_sec_content:
                continue

            sec_num = extract_section_number_from_content(raw_sec_content) or str(idx + 1)
            chunk_id = generate_deterministic_chunk_id(source_id, sec_num, raw_sec_content)

            # Prepend contextual header
            header_parts = [f"Act: {act_title}"]
            if act_year:
                header_parts.append(f"Year: {act_year}")
            if sec_num:
                header_parts.append(f"Section: {sec_num}")

            contextual_content = f"[{' | '.join(header_parts)}]\n\n{raw_sec_content}"

            parsed_chunks.append(
                {
                    "id": chunk_id,
                    "source_id": source_id,
                    "act_title": act_title,
                    "chapter_name": sec_obj.get("chapter_name"),
                    "section_number": sec_num,
                    "content": contextual_content,
                    "chunk_metadata": {
                        "parent_id": provision_identity(source_id, sec_num),
                        "source_url": str(act_json.get("source_url") or ""),
                        "act_year": act_year,
                        "source_type": source_type,
                        "raw_section_content": raw_sec_content,
                    },
                }
            )

            # Extract cross-references
            refs = extract_cross_references(raw_sec_content, current_act=act_title)
            for ref in refs:
                parsed_refs.append(
                    {
                        "source_section_id": chunk_id,
                        "target_section_id": None,
                        "target_act_title": ref["target_act_title"],
                        "target_section_number": ref["target_section_number"],
                        "relation": ref["relation"],
                    }
                )

        result = await self.repository.save_act(
            source_id=source_id,
            source_type=source_type,
            act_title=act_title,
            act_year=act_year,
            raw_json_str=raw_json_str,
            sections_count=len(sections),
            parent_chunks=parsed_chunks,
            cross_references=parsed_refs,
        )

        logger.info(
            "Ingested %s (%s): %d parent chunks, %d cross-refs",
            source_id,
            act_title,
            result["parent_chunks_created"],
            result["cross_refs_created"],
        )
        return result
