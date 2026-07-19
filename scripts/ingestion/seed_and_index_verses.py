#!/usr/bin/env python3
"""Seed sample Bhagavad Gita verses and index them into BM25 + Qdrant (local)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.domain.entities import Verse  # noqa: E402
from app.infrastructure.db.repositories.verse_repository import (  # noqa: E402
    SqlAlchemyVerseRepository,
)
from app.infrastructure.db.session import dispose_engine, get_session_factory, init_engine  # noqa: E402
from app.infrastructure.llm.embeddings import HashEmbedder, OllamaEmbedder  # noqa: E402
from app.infrastructure.llm.ollama import OllamaClient  # noqa: E402
from app.infrastructure.retrieval import reset_bm25_index  # noqa: E402
from app.infrastructure.vector.qdrant_store import QdrantDenseRetriever  # noqa: E402


async def run(seed_path: Path, *, skip_qdrant: bool) -> None:
    settings = get_settings()
    get_settings.cache_clear()
    settings = get_settings()
    init_engine(settings.database_url)
    reset_bm25_index()

    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    now = datetime.now(UTC)

    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = SqlAlchemyVerseRepository(session)
        created: list[Verse] = []
        for row in payload:
            existing = await repo.get_by_chapter_verse(row["chapter"], row["verse_number"])
            if existing is not None:
                created.append(existing)
                continue
            verse = Verse(
                id=uuid4(),
                chapter=row["chapter"],
                verse_number=row["verse_number"],
                sanskrit=row["sanskrit"],
                transliteration=row.get("transliteration"),
                translation=row["translation"],
                translation_source=row.get("translation_source", "sample"),
                commentary=row.get("commentary"),
                qdrant_point_id=None,
                topics=list(row.get("topics", [])),
                emotions=list(row.get("emotions", [])),
                created_at=now,
                updated_at=now,
            )
            created.append(await repo.add(verse))
        await session.commit()

    if skip_qdrant:
        print(f"Seeded {len(created)} verses (Qdrant indexing skipped).")
        await dispose_engine()
        return

    if settings.use_local_llm:
        ollama = OllamaClient(settings)
        if not await ollama.healthcheck():
            raise SystemExit(
                "Ollama is not reachable at "
                f"{settings.ollama_base_url}. Start it, then: "
                f"`ollama pull {settings.ollama_embed_model}`",
            )
        embedder: OllamaEmbedder | HashEmbedder = OllamaEmbedder(settings, client=ollama)
        print(
            f"Indexing with local embeddings: {settings.ollama_embed_model} "
            f"({settings.embedding_dimensions} dims)",
        )
    else:
        embedder = HashEmbedder(dimensions=settings.embedding_dimensions)
        print("WARNING: LLM_PROVIDER!=ollama — using HashEmbedder.")

    dense = QdrantDenseRetriever(settings, vector_size=embedder.dimensions)
    await dense.ensure_collection()

    texts = [v.searchable_text for v in created]
    vectors = await embedder.embed_documents(texts)

    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = SqlAlchemyVerseRepository(session)
        for verse, vector in zip(created, vectors, strict=True):
            point_id = await dense.upsert_verse(verse, vector)
            await repo.update_qdrant_point_id(verse.id, point_id)
        await session.commit()

    await dispose_engine()
    print(
        f"Seeded and indexed {len(created)} verses into Qdrant "
        f"collection '{settings.qdrant_collection}'.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed",
        type=Path,
        default=ROOT / "data" / "gita" / "sample_verses.json",
    )
    parser.add_argument("--skip-qdrant", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.seed, skip_qdrant=args.skip_qdrant))


if __name__ == "__main__":
    main()
