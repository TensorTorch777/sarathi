"""Unit tests for the hybrid RAG retrieval pipeline (in-memory adapters)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.dto.retrieval import RetrievalFilters, RetrieveVersesQuery
from app.application.use_cases.retrieval import RetrieveVersesUseCase
from app.domain.entities import Verse
from app.infrastructure.llm.embeddings import HashEmbedder
from app.infrastructure.retrieval.citation import CorpusCitationVerifier
from app.infrastructure.retrieval.compression import ExtractiveContextCompressor
from app.infrastructure.retrieval.hybrid.rrf import ReciprocalRankFusion
from app.infrastructure.retrieval.query_expansion import GitaQueryExpander
from app.infrastructure.retrieval.rerank.cross_encoder import LexicalCrossEncoderReranker
from app.infrastructure.retrieval.sparse.bm25 import BM25SparseRetriever
from app.infrastructure.vector.qdrant_store import InMemoryDenseRetriever
from app.core.config import Settings


class InMemoryCorpus:
    """Simple corpus port for tests."""

    def __init__(self, verses: list[Verse]) -> None:
        self._verses = {v.id: v for v in verses}

    async def list_all(self) -> list[Verse]:
        return list(self._verses.values())

    async def get_by_ids(self, verse_ids: list) -> dict:
        return {vid: self._verses[vid] for vid in verse_ids if vid in self._verses}

    async def get_by_citation(self, chapter: int, verse_number: int) -> Verse | None:
        for verse in self._verses.values():
            if verse.chapter == chapter and verse.verse_number == verse_number:
                return verse
        return None


def _verse(
    chapter: int,
    number: int,
    translation: str,
    *,
    topics: list[str],
    emotions: list[str],
) -> Verse:
    now = datetime.now(UTC)
    return Verse(
        id=uuid4(),
        chapter=chapter,
        verse_number=number,
        sanskrit=f"sanskrit-{chapter}-{number}",
        transliteration=None,
        translation=translation,
        translation_source="sample",
        commentary=f"Commentary about {translation[:40]}",
        qdrant_point_id=None,
        topics=topics,
        emotions=emotions,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
async def pipeline() -> RetrieveVersesUseCase:
    verses = [
        _verse(
            2,
            47,
            "You have a right to duty but not to the fruits of action; practice detachment.",
            topics=["karma", "duty", "detachment"],
            emotions=["anxiety", "fear"],
        ),
        _verse(
            2,
            63,
            "From anger comes delusion; from delusion loss of memory and intelligence.",
            topics=["mind", "anger"],
            emotions=["anger", "confusion"],
        ),
        _verse(
            18,
            66,
            "Surrender unto Me and do not fear; I shall deliver you.",
            topics=["devotion", "surrender"],
            emotions=["fear", "grief"],
        ),
        _verse(
            6,
            5,
            "Elevate yourself by the mind; the mind can be friend or enemy.",
            topics=["mind", "discipline"],
            emotions=["grief", "anxiety"],
        ),
        _verse(
            12,
            13,
            "Be a kind friend to all beings, free from ego, equal in joy and distress.",
            topics=["compassion", "devotion"],
            emotions=["anger", "peace"],
        ),
        _verse(
            2,
            14,
            "Tolerate happiness and distress like seasons; they are temporary.",
            topics=["equanimity"],
            emotions=["grief", "anxiety"],
        ),
    ]
    corpus = InMemoryCorpus(verses)
    sparse = BM25SparseRetriever()
    await sparse.rebuild(verses)
    dense = InMemoryDenseRetriever()
    embedder = HashEmbedder(dimensions=64)
    for verse in verses:
        vector = await embedder.embed_documents([verse.searchable_text])
        await dense.upsert_verse(verse, vector[0])

    settings = Settings()
    return RetrieveVersesUseCase(
        corpus=corpus,
        query_expander=GitaQueryExpander(settings),
        sparse=sparse,
        dense=dense,
        embedder=embedder,
        fusion=ReciprocalRankFusion(k=60),
        reranker=LexicalCrossEncoderReranker(),
        compressor=ExtractiveContextCompressor(),
        verifier=CorpusCitationVerifier(corpus),
        bm25_top_k=10,
        dense_top_k=10,
        min_rerank_score=-1.0,
    )


@pytest.mark.asyncio
async def test_retrieve_top_verified_verses(pipeline: RetrieveVersesUseCase) -> None:
    result = await pipeline.execute(
        RetrieveVersesQuery(query="I feel anxious about results of my work and duty"),
    )
    assert 1 <= len(result.verses) <= 5
    assert all(v.verified for v in result.verses)
    assert all(v.citation.startswith("BG ") for v in result.verses)
    assert all(v.compressed_context for v in result.verses)
    citations = {v.citation for v in result.verses}
    assert "BG 2.47" in citations or any("duty" in v.translation.lower() for v in result.verses)


@pytest.mark.asyncio
async def test_emotion_and_topic_filters(pipeline: RetrieveVersesUseCase) -> None:
    result = await pipeline.execute(
        RetrieveVersesQuery(
            query="anger and delusion",
            filters=RetrievalFilters(emotions=("anger",), topics=("mind",)),
            expand_query=False,
        ),
    )
    assert result.verses
    for verse in result.verses:
        assert "anger" in [e.lower() for e in verse.emotions]
        assert "mind" in [t.lower() for t in verse.topics]


@pytest.mark.asyncio
async def test_query_expansion_adds_variants() -> None:
    expander = GitaQueryExpander(Settings())
    expanded = await expander.expand("Help me with anxiety about duty")
    assert expanded[0].lower().startswith("help me with anxiety")
    assert len(expanded) > 1
