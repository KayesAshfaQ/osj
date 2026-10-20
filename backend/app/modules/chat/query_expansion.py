from __future__ import annotations

import logging
import re

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.llm_factory import create_llm
from app.ai.llm_responses import invoke_llm, response_text
from app.modules.chat.privacy import sanitize
from app.modules.chat.schemas_llm import ExpandedQuerySet

logger = logging.getLogger(__name__)

EXPANSION_SYSTEM_PROMPT = (
    "You are an expert Bangladeshi legal assistant. "
    "Take the user's input query (which may be informal Bengali, English, or Banglish) "
    "and generate exactly two distinct, formal search queries: one English and one Bengali.\n\n"
    "Rules:\n"
    "1. Keep output as a plain bulleted list or one query per line.\n"
    "2. Include formal legal keywords (e.g. 'unlawful termination', 'বেতন না দেওয়া', 'Arrest without warrant').\n"
    "3. Do not add commentary or conversational preambles."
)


async def expand_query_bilingual(query: str) -> ExpandedQuerySet:
    """Generate parallel Bengali and English formal legal query variations."""
    query = sanitize(query)
    if not query or len(query.strip()) < 5:
        return ExpandedQuerySet(original_query=query, expanded_queries=[query])

    try:
        llm = create_llm()
        messages = [
            SystemMessage(content=EXPANSION_SYSTEM_PROMPT),
            HumanMessage(content=f"User query: {query}"),
        ]
        response = await invoke_llm(llm, messages)
        content_str = response_text(response)

        lines = [
            re.sub(r"^(?:[-*•]\s+|[0-9০-৯]+[.)]\s+)", "", line.strip())
            for line in content_str.split("\n")
            if line.strip()
        ]
        # The original counts toward the three-query retrieval budget.
        queries = list(dict.fromkeys([query, *(q for q in lines if len(q) > 3)]))[:3]

        return ExpandedQuerySet(original_query=query, expanded_queries=queries)

    except Exception:
        logger.warning("Query expansion failed; using sanitized original")
        return ExpandedQuerySet(original_query=query, expanded_queries=[query])


def reciprocal_rank_fusion(
    results_list: list[list[Document]],
    top_k: int = 5,
    rrf_k: int = 60,
) -> list[Document]:
    """Merge and deduplicate multiple ranked document lists using Reciprocal Rank Fusion."""
    if not results_list:
        return []

    doc_scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for doc_list in results_list:
        for rank, doc in enumerate(doc_list, 1):
            key = doc.metadata.get("parent_id") or doc.metadata.get("id") or hash(doc.page_content[:100])
            key_str = str(key)

            if key_str not in doc_map:
                doc_map[key_str] = doc

            doc_scores[key_str] = doc_scores.get(key_str, 0.0) + (1.0 / (rrf_k + rank))

    sorted_keys = sorted(doc_scores.keys(), key=lambda k: doc_scores[k], reverse=True)[:top_k]

    final_docs: list[Document] = []
    for key in sorted_keys:
        doc = doc_map[key]
        doc.metadata["rrf_score"] = doc_scores[key]
        final_docs.append(doc)

    return final_docs
