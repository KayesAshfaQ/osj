"""Bulk ingestion script for legal corpus into PostgreSQL staging and parent tables.

Usage:
    uv run python scripts/ingest_corpus_postgres.py [--acts-dir PATH] [--limit N]
"""

import argparse
import asyncio
import glob
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.modules.corpus.identity import source_identity
from app.modules.corpus.repository import SqlAlchemyCorpusRepository
from app.modules.corpus.service import CorpusIngestionService
from app.persistence.session import cli_session, create_engine, create_session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_constitution(service: CorpusIngestionService, data_dir: Path) -> None:
    const_path = data_dir / "bd-constitution.json"
    if not const_path.exists():
        logger.warning("Constitution file not found at %s", const_path)
        return

    logger.info("Ingesting Constitution from %s...", const_path)
    with open(const_path, encoding="utf-8") as f:
        articles_data = cast(list[object], json.load(f))
    articles: list[dict[str, object]] = [
        cast(dict[str, object], item) for item in articles_data if isinstance(item, dict)
    ]
    sections: list[dict[str, object]] = []
    for art in articles:
        sec_num = str(art.get("section_no_en") or art.get("section_no_bn") or "")
        art_name = str(art.get("article_name_en") or art.get("article_name_bn") or "")
        content = str(art.get("article_bn") or art.get("article_en") or "")
        sections.append(
            {
                "section_content": f"Article {sec_num}: {art_name}\n\n{content}".strip(),
                "chapter_name": art.get("part_name_en"),
            }
        )

    const_json: dict[str, object] = {
        "act_title": "The Constitution of the People’s Republic of Bangladesh",
        "act_year": "1972",
        "sections": sections,
    }

    res = await service.ingest_act(
        source_id="bd-constitution",
        source_type="constitution",
        act_json=const_json,
    )
    logger.info("Constitution ingested: %s", res)


async def ingest_all_acts(
    service: CorpusIngestionService,
    acts_dir: Path,
    limit: int | None = None,
) -> int:
    """Ingest acts from directory. Returns the number of failed acts."""
    if not acts_dir.exists():
        logger.warning("Acts directory not found at %s", acts_dir)
        return 0

    act_files = sorted(glob.glob(str(acts_dir / "*.json")))
    if limit:
        act_files = act_files[:limit]

    logger.info("Found %d act JSON files to ingest from %s...", len(act_files), acts_dir)

    start_time = time.perf_counter()
    total_parents: int = 0
    total_refs: int = 0
    failures: int = 0

    for i, act_file in enumerate(act_files, 1):
        try:
            with open(act_file, encoding="utf-8") as f:
                act_data: dict[str, object] = json.load(f)
            source_id = source_identity(act_data)
            res = await service.ingest_act(
                source_id=source_id,
                source_type="statute",
                act_json=act_data,
            )
            parents_created = res.get("parent_chunks_created")
            if isinstance(parents_created, int):
                total_parents += parents_created
            refs_created = res.get("cross_refs_created")
            if isinstance(refs_created, int):
                total_refs += refs_created

            if i % 100 == 0 or i == len(act_files):
                logger.info(
                    "[%d/%d] Ingested %s — Total parents: %d, Total refs: %d",
                    i,
                    len(act_files),
                    source_id,
                    total_parents,
                    total_refs,
                )
        except Exception as e:
            failures += 1
            logger.error("Failed to ingest %s: %s", act_file, e)
            await service.rollback()

    elapsed = time.perf_counter() - start_time
    logger.info(
        "Bulk ingestion complete in %.2fs. Total parents: %d, Total refs: %d, Failures: %d",
        elapsed,
        total_parents,
        total_refs,
        failures,
    )
    return failures


def resolve_acts_dir(data_dir: Path, custom_path: str | None = None) -> Path:
    if custom_path:
        return Path(custom_path)
    env_path = os.getenv("ACTS_DIR")
    if env_path:
        return Path(env_path)
    default_dataset = data_dir / "bangladesh_legal_acts_dataset" / "acts"
    if default_dataset.exists() and any(default_dataset.glob("*.json")):
        return default_dataset
    return default_dataset


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest legal corpus into PostgreSQL")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--acts-dir", default=None, help="Path to reader-supplied acts directory")
    inputs.add_argument("--demo", action="store_true", help="Ingest the bundled fictional demonstration document")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of acts")
    args = parser.parse_args()

    data_dir = Path(__file__).parent.parent / "data"
    acts_dir = resolve_acts_dir(data_dir, args.acts_dir)

    engine = create_engine(settings.database_url)
    try:
        session_factory = create_session_factory(engine)
        async with cli_session(session_factory) as session:
            service = CorpusIngestionService(SqlAlchemyCorpusRepository(session))
            if args.demo:
                demo = json.loads((data_dir / "examples/demo-acts.json").read_text(encoding="utf-8"))
                for act in demo["acts"]:
                    await service.ingest_act(source_id=source_identity(act), source_type="statute", act_json=act)
                failed_count = 0
            else:
                if not acts_dir.exists():
                    parser.error("Supply --demo, --acts-dir or ACTS_DIR pointing to an existing corpus")
                await ingest_constitution(service, data_dir)
                failed_count = await ingest_all_acts(service, acts_dir, limit=args.limit)
    finally:
        await engine.dispose()

    if failed_count > 0:
        logger.error("Ingestion encountered %d failures.", failed_count)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
