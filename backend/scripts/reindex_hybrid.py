"""Build a separate deterministic Qdrant index; never cut over the active path.

Usage: uv run python scripts/reindex_hybrid.py --output qdrant_db_candidate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path

from langchain_core.documents import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.qdrant_store import QdrantStoreManager
from app.core.config import settings
from app.modules.corpus.chunker import chunk_documents
from app.modules.corpus.identity import child_identity
from app.modules.corpus.loader import load_all_documents, load_legal_acts_documents

logger = logging.getLogger(__name__)
COLLECTION = "statutory_law"


def deduplicate_children(documents: list[Document]) -> list[Document]:
    unique: dict[str, Document] = {}
    for document in documents:
        point_id = str(document.metadata["child_id"])
        previous = unique.get(point_id)
        if previous is None:
            unique[point_id] = document
        elif (
            previous.page_content != document.page_content
            or previous.metadata["parent_id"] != document.metadata["parent_id"]
        ):
            raise ValueError(f"Child identity collision: {point_id}")
    return list(unique.values())


def prepare_documents_from_data_dir(data_dir: Path, *, demo: bool = False) -> list[Document]:
    legal_docs = (
        load_legal_acts_documents(str(data_dir / "examples/demo-acts.json"))
        if demo
        else load_all_documents(
            constitution_path=str(data_dir / "bd-constitution.json"),
            legal_acts_path=str(
                data_dir / "bangladesh_legal_acts_dataset" / "Contextualized_Bangladesh_Legal_Acts.json"
            ),
        )
    )
    chunks = chunk_documents(legal_docs)
    prepared: list[Document] = []
    for chunk in chunks:
        metadata = dict(chunk.metadata)
        title = str(metadata["act_title"])
        number = str(metadata["section_number"])
        year = str(metadata["act_year"])
        header = f"[Act: {title} | Section: {number} | Year: {year}]\n\n"
        content = header + chunk.page_content.strip()
        metadata["jurisdiction"] = "Synthetic demonstration" if demo else "Bangladesh"
        metadata["status"] = "Synthetic" if demo else ("Repealed" if metadata["is_repealed"] else "Active")
        metadata["child_id"] = child_identity(str(metadata["parent_id"]), content, int(metadata["chunk_position"]))
        prepared.append(Document(page_content=content, metadata=metadata))
    return deduplicate_children(prepared)


def build_manifest(documents: list[Document]) -> dict[str, object]:
    entries = sorted(
        (str(doc.metadata["child_id"]), hashlib.sha256(doc.page_content.encode()).hexdigest()) for doc in documents
    )
    if len({item[0] for item in entries}) != len(entries):
        raise ValueError("Duplicate child identity in corpus")
    serialized = json.dumps(entries, separators=(",", ":"))
    return {
        "collection": COLLECTION,
        "point_count": len(entries),
        "corpus_version": hashlib.sha256(serialized.encode()).hexdigest(),
    }


def validate_replacement_path(output: Path, active: Path) -> Path:
    output = output.expanduser().resolve()
    if output == active.expanduser().resolve():
        raise ValueError("Replacement path must differ from active Qdrant path")
    if output.exists() and any(output.iterdir()) and not (output / "justify_manifest.json").is_file():
        raise ValueError("Replacement path contains unrecognized data; choose a new path")
    return output


def _write_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True))
    temporary.replace(path)


def reindex_qdrant(output: Path, data_dir: Path, *, batch_size: int = 100, demo: bool = False) -> dict[str, object]:
    if not 1 <= batch_size <= 100:
        raise ValueError("batch_size must be between 1 and 100")
    output = validate_replacement_path(output, Path(settings.qdrant_path))
    documents = prepare_documents_from_data_dir(data_dir, demo=demo)
    manifest = build_manifest(documents)
    documents.sort(key=lambda doc: str(doc.metadata["child_id"]))
    for document in documents:
        document.metadata["corpus_version"] = manifest["corpus_version"]
    manifest_path = output / "justify_manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise ValueError("Corpus changed; build into a fresh replacement directory")
    output.mkdir(parents=True, exist_ok=True)
    _write_json(manifest_path, manifest)
    checkpoint_path = output / "justify_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {"completed_batches": 0}
    completed = int(checkpoint["completed_batches"])
    manager = QdrantStoreManager(collection_name=COLLECTION, path=str(output))
    try:
        for index, start in enumerate(range(0, len(documents), batch_size)):
            if index < completed:
                continue
            manager.add_documents(documents[start : start + batch_size])
            _write_json(checkpoint_path, {"completed_batches": index + 1})
            logger.info("Indexed %d/%d points", min(start + batch_size, len(documents)), len(documents))
        actual = manager.client.count(collection_name=COLLECTION, exact=True).count
        if actual != len(documents):
            raise ValueError(f"Replacement index has {actual} points; expected {len(documents)}")
    finally:
        manager.client.close()
    return manifest


def reindex_qdrant_remote(
    url: str,
    data_dir: Path,
    *,
    api_key: str | None = None,
    batch_size: int = 100,
    demo: bool = False,
) -> dict[str, object]:
    """Index documents directly into a remote Qdrant server (e.g. Qdrant Cloud or GCP service)."""
    if not 1 <= batch_size <= 100:
        raise ValueError("batch_size must be between 1 and 100")
    documents = prepare_documents_from_data_dir(data_dir, demo=demo)
    manifest = build_manifest(documents)
    documents.sort(key=lambda doc: str(doc.metadata["child_id"]))
    for document in documents:
        document.metadata["corpus_version"] = manifest["corpus_version"]

    effective_api_key = api_key or settings.qdrant_api_key or None
    manager = QdrantStoreManager(collection_name=COLLECTION, url=url, api_key=effective_api_key)
    try:
        for start in range(0, len(documents), batch_size):
            manager.add_documents(documents[start : start + batch_size])
            logger.info(
                "Indexed %d/%d points into remote Qdrant", min(start + batch_size, len(documents)), len(documents)
            )
        actual = manager.client.count(collection_name=COLLECTION, exact=True).count
        if actual != len(documents):
            raise ValueError(f"Remote index has {actual} points; expected {len(documents)}")
    finally:
        manager.client.close()
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a replacement local or remote Qdrant hybrid index")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path, help="Local directory for replacement index")
    group.add_argument("--url", type=str, help="Remote Qdrant server URL")
    parser.add_argument("--api-key", type=str, default=None, help="Remote Qdrant API key")
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--data-dir", type=Path, help="Directory containing reader-supplied corpus files")
    inputs.add_argument("--demo", action="store_true", help="Use the bundled fictional demonstration corpus")
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    data_dir = Path(__file__).resolve().parents[1] / "data" if args.demo else args.data_dir
    if args.output:
        report = reindex_qdrant(args.output, data_dir, batch_size=args.batch_size, demo=args.demo)
    else:
        report = reindex_qdrant_remote(
            args.url, data_dir, api_key=args.api_key, batch_size=args.batch_size, demo=args.demo
        )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
