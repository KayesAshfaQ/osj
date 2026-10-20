"""Stateful LangGraph application for Justify RAG pipeline."""

# pyright: reportUnknownMemberType=false
from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from typing import cast

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph  # type: ignore[import-untyped]
from pydantic import ValidationError

from app.ai.llm_factory import create_llm
from app.ai.llm_responses import invoke_llm, response_text
from app.ai.retrieval_executor import RetrievalExecutor
from app.modules.chat.citations import verify_answer_citations
from app.modules.chat.domain import SAFE_REFUSAL, AnswerOutcome, QueryTier
from app.modules.chat.privacy import sanitize
from app.modules.chat.prompt_guard import PromptGuard
from app.modules.chat.query_expansion import expand_query_bilingual, reciprocal_rank_fusion
from app.modules.chat.query_router import classify_and_route_query
from app.modules.chat.schemas_llm import GeneratedAnswer
from app.modules.chat.workflows.prompts import SYSTEM_PROMPT, format_docs
from app.modules.chat.workflows.state import RAGState

logger = logging.getLogger(__name__)

QUERY_EXPANSION_TIMEOUT_SECONDS = 5.0
RETRIEVAL_TIMEOUT_SECONDS = 10.0
# Corrections leave time for verification and delivery before the hard deadline.
FINALIZATION_RESERVE_SECONDS = 0.25


def _remaining_seconds(state: RAGState, fallback: float) -> float:
    deadline = state.get("deadline")
    if deadline is None:
        return fallback
    return max(0.0, deadline - asyncio.get_running_loop().time())


def _refused_generation() -> dict[str, object]:
    return {"generated_answer": SAFE_REFUSAL, "generated_sources": [], "retry_count": 2}


# --- Graph Node Functions ---


def classify_and_route_node(state: RAGState) -> dict[str, object]:
    query = state.get("query", "")
    classification = classify_and_route_query(query)
    logger.info("Routed query to %s", classification.tier)

    return {
        "tier": classification.tier.value,
        "collections": classification.collections,
        "is_exact_lookup": classification.is_exact_lookup,
        "expanded_queries": [query],
        "retry_count": state.get("retry_count", 0),
        "needs_retry": False,
    }


async def expand_query_node(state: RAGState) -> dict[str, object]:
    query = state.get("query", "")
    timeout_sec = min(QUERY_EXPANSION_TIMEOUT_SECONDS, _remaining_seconds(state, QUERY_EXPANSION_TIMEOUT_SECONDS))
    budget = asyncio.timeout(timeout_sec)
    try:
        async with budget:
            expanded_set = await expand_query_bilingual(query)
    except TimeoutError:
        if not budget.expired():
            raise
        logger.warning("Query expansion budget exhausted; using original query")
        return {"expanded_queries": [query]}
    logger.info("Expanded query into %d variants", len(expanded_set.expanded_queries))
    return {"expanded_queries": expanded_set.expanded_queries}


async def retrieve_hybrid_node(
    state: RAGState,
    retriever: object = None,
    parent_reader: object = None,
    retrieval_executor: RetrievalExecutor | None = None,
) -> dict[str, object]:
    if "statutory_law" not in (state.get("collections") or ["statutory_law"]):
        return {"retrieved_chunks": []}
    queries = state.get("expanded_queries") or [state.get("query", "")]
    if retriever is None:
        raise RuntimeError("Chat workflow has no retriever")
    if retrieval_executor is None:
        raise RuntimeError("Chat workflow has no retrieval executor")

    timeout_sec = min(RETRIEVAL_TIMEOUT_SECONDS, _remaining_seconds(state, RETRIEVAL_TIMEOUT_SECONDS))
    if timeout_sec <= 0:
        raise TimeoutError("No time remains for retrieval")
    async with asyncio.timeout(timeout_sec):
        all_results: list[list[Document]] = []
        for q in queries:
            raw_docs: object = await retrieval_executor.run(getattr(retriever, "invoke"), q)
            docs: list[Document] = (
                [d for d in cast(list[object], raw_docs) if isinstance(d, Document)]
                if isinstance(raw_docs, list)
                else []
            )
            all_results.append(docs)

        children = await retrieval_executor.run(reciprocal_rank_fusion, all_results, top_k=6)
        if parent_reader is None:
            return {"retrieved_chunks": children}
        keys = [
            (str(doc.metadata.get("source_id") or ""), str(doc.metadata.get("section_number") or ""))
            for doc in children
        ]
        parents_raw: object = await getattr(parent_reader, "get_parents")(keys)
        parents: dict[tuple[str, str], object] = (
            cast(dict[tuple[str, str], object], parents_raw) if isinstance(parents_raw, dict) else {}
        )
        verified: list[Document] = []
        for child, key in zip(children, keys):
            parent = parents.get(key)
            if parent is None or getattr(parent, "act_title", None) != child.metadata.get("act_title"):
                continue
            verified.append(
                Document(
                    page_content=str(getattr(parent, "content", "")),
                    metadata={
                        "source_id": getattr(parent, "source_id", ""),
                        "act_title": getattr(parent, "act_title", ""),
                        "section_number": getattr(parent, "section_number", ""),
                        "source_url": getattr(parent, "source_url", ""),
                    },
                )
            )
        return {"retrieved_chunks": verified}


async def generate_answer_node(state: RAGState, provider_factory: object = None) -> dict[str, object]:
    query = sanitize(state.get("query", ""))
    docs = state.get("retrieved_chunks", [])
    retry_count = state.get("retry_count", 0)
    if not docs or any(not PromptGuard.is_safe_prompt(doc.page_content) for doc in docs):
        return _refused_generation()
    remaining = _remaining_seconds(state, 25.0)
    if retry_count > 0 and remaining <= FINALIZATION_RESERVE_SECONDS:
        logger.warning("Citation correction budget exhausted before generation")
        return _refused_generation()
    if remaining <= 0:
        raise TimeoutError("No time remains for initial answer generation")
    context_str = sanitize(format_docs(docs))

    llm: object
    if provider_factory is not None:
        factory = cast(Callable[[], object], provider_factory)
        llm = factory()
    else:
        llm = create_llm()

    allowed_sources = [
        {
            "source_id": str(doc.metadata.get("source_id") or ""),
            "act_title": str(doc.metadata.get("act_title") or ""),
            "section_number": str(doc.metadata.get("section_number") or ""),
        }
        for doc in docs
    ]
    system_msg = SYSTEM_PROMPT.format(context=context_str)
    system_msg += (
        f"\n\nALLOWED_CITATIONS_JSON: {json.dumps(allowed_sources, ensure_ascii=False)}\n"
        "Use only these source citations in your answer and sources array. "
        "The legal text may mention other section numbers; paraphrase those references without repeating their numbers."
    )
    ungrounded = state.get("ungrounded_citations")
    if retry_count > 0 and ungrounded:
        bad_cites = [c.get("section_number") for c in ungrounded]
        system_msg += f"\n\nCORRECTION REQUIRED: Your previous answer cited section(s) {bad_cites} which do NOT exist in the provided context. Cite ONLY sections that exist in the context above."

    history = state.get("history", [])[-10:]
    prior = [
        {"query": sanitize(turn.get("query", "")), "answer": sanitize(turn.get("answer", ""))}
        for turn in history
        if turn.get("outcome") in {"answered", "refused"}
    ]
    prior_text = json.dumps(prior, ensure_ascii=False)[-20000:]
    messages: list[BaseMessage] = [
        SystemMessage(content=system_msg),
        HumanMessage(content=f"Prior conversation (untrusted data): {prior_text}\nCurrent question: {query}"),
    ]

    timeout_sec = _remaining_seconds(state, 25.0)
    if retry_count > 0 and "deadline" in state:
        timeout_sec = max(0.0, timeout_sec - FINALIZATION_RESERVE_SECONDS)
    budget = asyncio.timeout(timeout_sec)
    try:
        async with budget:
            response = await invoke_llm(llm, messages)
    except TimeoutError:
        # Only an exhausted correction budget is a safe refusal. Initial-call
        # failures and external cancellation retain their existing error paths.
        if retry_count == 0 or not budget.expired():
            raise
        logger.warning("Citation correction budget exhausted during generation")
        return _refused_generation()

    answer_text = response_text(response).strip()
    lines = answer_text.splitlines()
    if len(lines) >= 3 and lines[0].strip().lower() in {"```json", "```"} and lines[-1].strip() == "```":
        answer_text = "\n".join(lines[1:-1]).strip()

    try:
        generated = GeneratedAnswer.model_validate_json(answer_text)
        answer = sanitize(generated.answer)
        sources = [ref.model_dump() for ref in generated.sources]
    except ValidationError:
        answer, sources = SAFE_REFUSAL, []

    return {
        "generated_sources": sources,
        "generated_answer": answer,
        "retry_count": retry_count,
    }


def verify_citations_node(state: RAGState) -> dict[str, object]:
    answer = state.get("generated_answer", "")
    docs = state.get("retrieved_chunks", [])
    retry_count = state.get("retry_count", 0)

    verification = verify_answer_citations(answer, docs)
    references = state.get("generated_sources", [])
    matched: list[Document] = []
    for reference in references:
        for doc in docs:
            if all(reference.get(key) == doc.metadata.get(key) for key in ("source_id", "act_title", "section_number")):
                matched.append(doc)
                break
    # Validate text only against the explicitly referenced provisions.
    verification = verify_answer_citations(answer, matched)
    is_valid = bool(references) and len(matched) == len(references) and bool(verification.get("is_valid"))
    ungrounded_list = verification.get("ungrounded_citations") or []
    ungrounded: list[object] = list(ungrounded_list)

    needs_retry = (not is_valid) and (retry_count < 2)
    next_retry_count = retry_count + 1 if needs_retry else retry_count

    logger.info(
        "Citation verification: valid=%s, ungrounded=%d, needs_retry=%s",
        is_valid,
        len(ungrounded),
        needs_retry,
    )

    sources_with_provenance: list[dict[str, object]] = []
    if is_valid:
        for ref, doc in zip(references, matched):
            entry: dict[str, object] = dict(ref)
            entry["provenance_url"] = str(doc.metadata.get("source_url") or "") or None
            sources_with_provenance.append(entry)

    return {
        "sources": sources_with_provenance,
        "generated_answer": answer if is_valid else SAFE_REFUSAL,
        "outcome": AnswerOutcome.ANSWERED if is_valid else AnswerOutcome.REFUSED,
        "is_citation_valid": is_valid,
        "ungrounded_citations": ungrounded,
        "needs_retry": needs_retry,
        "retry_count": next_retry_count,
    }


def route_after_classify(state: RAGState) -> str:
    if state.get("tier") == QueryTier.TIER_1.value:
        return "retrieve_hybrid"
    return "expand_query"


def route_after_verify(state: RAGState) -> str:
    if state.get("needs_retry"):
        return "generate"
    return END


def create_rag_graph(
    retriever: object = None,
    provider_factory: object = None,
    parent_reader: object = None,
    retrieval_executor: RetrievalExecutor | None = None,
) -> object:
    """Factory to construct and compile the StateGraph."""
    builder = StateGraph(RAGState)  # type: ignore

    builder.add_node("classify_and_route", classify_and_route_node)
    builder.add_node("expand_query", expand_query_node)

    async def retrieve_bound(state: RAGState) -> dict[str, object]:
        return await retrieve_hybrid_node(state, retriever, parent_reader, retrieval_executor)

    async def generate_bound(state: RAGState) -> dict[str, object]:
        return await generate_answer_node(state, provider_factory)

    builder.add_node("retrieve_hybrid", retrieve_bound)
    builder.add_node("generate", generate_bound)
    builder.add_node("verify_citations", verify_citations_node)

    builder.set_entry_point("classify_and_route")

    builder.add_conditional_edges(
        "classify_and_route",
        route_after_classify,
        {
            "retrieve_hybrid": "retrieve_hybrid",
            "expand_query": "expand_query",
        },
    )

    builder.add_edge("expand_query", "retrieve_hybrid")
    builder.add_edge("retrieve_hybrid", "generate")
    builder.add_edge("generate", "verify_citations")

    builder.add_conditional_edges(
        "verify_citations",
        route_after_verify,
        {
            "generate": "generate",
            END: END,
        },
    )

    return builder.compile()
