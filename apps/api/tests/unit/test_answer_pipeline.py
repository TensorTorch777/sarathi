"""Unit tests for the full answer pipeline stage order."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.dto.answer import GenerateAnswerQuery
from app.application.dto.retrieval import RankedVerse
from app.application.use_cases.answer import GenerateAnswerUseCase
from app.application.use_cases.retrieval import RetrieveVersesUseCase
from app.core.config import Settings
from app.domain.entities import Verse
from app.infrastructure.answer.citation_verifier import AnswerCitationVerifier
from app.infrastructure.answer.emotion_detector import LexiconEmotionDetector
from app.infrastructure.answer.generator import TemplateAnswerGenerator
from app.infrastructure.answer.prompt_builder import GroundedPromptBuilder
from app.infrastructure.answer.query_rewriter import GitaQueryRewriter
from app.infrastructure.answer.topic_detector import LexiconTopicDetector
from app.infrastructure.llm.embeddings import HashEmbedder
from app.infrastructure.retrieval.citation import CorpusCitationVerifier
from app.infrastructure.retrieval.compression import ExtractiveContextCompressor
from app.infrastructure.retrieval.hybrid.rrf import ReciprocalRankFusion
from app.infrastructure.retrieval.query_expansion import GitaQueryExpander
from app.infrastructure.retrieval.rerank.cross_encoder import LexicalCrossEncoderReranker
from app.infrastructure.retrieval.sparse.bm25 import BM25SparseRetriever
from app.infrastructure.vector.qdrant_store import InMemoryDenseRetriever


class InMemoryCorpus:
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
    emotions: list[str],
    topics: list[str],
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
        commentary="Helpful commentary.",
        qdrant_point_id=None,
        topics=topics,
        emotions=emotions,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
async def answer_use_case() -> GenerateAnswerUseCase:
    verses = [
        _verse(
            2,
            47,
            "You have a right to duty but not to the fruits of action.",
            emotions=["anxiety", "fear"],
            topics=["karma", "duty", "detachment"],
        ),
        _verse(
            18,
            66,
            "Surrender unto Me and do not fear.",
            emotions=["fear", "grief"],
            topics=["devotion", "surrender"],
        ),
        _verse(
            2,
            63,
            "From anger comes delusion and loss of intelligence.",
            emotions=["anger", "confusion"],
            topics=["mind", "anger"],
        ),
    ]
    corpus = InMemoryCorpus(verses)
    sparse = BM25SparseRetriever()
    await sparse.rebuild(verses)
    dense = InMemoryDenseRetriever()
    embedder = HashEmbedder(dimensions=64)
    for verse in verses:
        vectors = await embedder.embed_documents([verse.searchable_text])
        await dense.upsert_verse(verse, vectors[0])

    settings = Settings()
    retrieve = RetrieveVersesUseCase(
        corpus=corpus,
        query_expander=GitaQueryExpander(settings),
        sparse=sparse,
        dense=dense,
        embedder=embedder,
        fusion=ReciprocalRankFusion(k=60),
        reranker=LexicalCrossEncoderReranker(),
        compressor=ExtractiveContextCompressor(),
        verifier=CorpusCitationVerifier(corpus),
        min_rerank_score=-1.0,
    )
    return GenerateAnswerUseCase(
        emotion_detector=LexiconEmotionDetector(settings),
        topic_detector=LexiconTopicDetector(settings),
        query_rewriter=GitaQueryRewriter(settings),
        retrieve_verses=retrieve,
        prompt_builder=GroundedPromptBuilder(),
        generator=TemplateAnswerGenerator(),
        citation_verifier=AnswerCitationVerifier(),
    )


@pytest.mark.asyncio
async def test_emotion_and_topic_detection() -> None:
    settings = Settings()
    emotions = await LexiconEmotionDetector(settings).detect(
        "I feel anxious about my duty at work",
    )
    topics = await LexiconTopicDetector(settings).detect(
        "I feel anxious about my duty at work",
    )
    assert "anxiety" in emotions
    assert "duty" in topics or "karma" in topics


@pytest.mark.asyncio
async def test_full_answer_pipeline(answer_use_case: GenerateAnswerUseCase) -> None:
    result = await answer_use_case.execute(
        GenerateAnswerQuery(message="I feel anxious about the fruits of my work and duty"),
    )
    assert result.emotions
    assert result.rewritten_query
    assert result.answer
    assert result.citations
    assert all(c.citation.startswith("BG ") for c in result.citations)
    assert result.stages["emotion"]
    assert result.stages["topic"] is not None
    assert "query_rewrite" in result.stages
    assert "citation_verification" in result.stages


def test_answer_citation_verifier_strips_unknown() -> None:
    verse = RankedVerse(
        verse_id=uuid4(),
        chapter=2,
        verse_number=47,
        citation="BG 2.47",
        sanskrit="x",
        translation="Duty without attachment to fruits.",
        transliteration=None,
        commentary=None,
        topics=["karma"],
        emotions=["anxiety"],
        verified=True,
    )
    raw = "See BG 2.47 for duty. Ignore BG 99.99 which is fake."
    cleaned, kept, removed = AnswerCitationVerifier().verify(raw, [verse])
    assert "BG 2.47" in cleaned
    assert "BG 99.99" not in cleaned
    assert any(c.citation == "BG 2.47" for c in kept)
    assert "BG 99.99" in removed
