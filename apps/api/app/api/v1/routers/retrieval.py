"""Retrieval API routes."""

from fastapi import APIRouter

from app.api.v1.deps import CurrentUserDep, RetrieveVersesUseCaseDep
from app.api.v1.schemas.retrieval import (
    RetrieveRequest,
    RetrieveResponse,
    RetrievedVerseResponse,
)
from app.application.dto.retrieval import RetrievalFilters, RetrieveVersesQuery

router = APIRouter(prefix="/retrieval")


@router.post(
    "/search",
    response_model=RetrieveResponse,
    summary="Hybrid RAG verse retrieval",
    description=(
        "Runs query expansion, BM25 + dense hybrid retrieval, cross-encoder "
        "reranking, context compression, and citation verification. Returns top 5."
    ),
)
async def search_verses(
    body: RetrieveRequest,
    _user: CurrentUserDep,
    use_case: RetrieveVersesUseCaseDep,
) -> RetrieveResponse:
    """Authenticate and retrieve grounded Bhagavad Gita verses."""
    result = await use_case.execute(
        RetrieveVersesQuery(
            query=body.query,
            filters=RetrievalFilters(
                chapters=tuple(body.filters.chapters),
                chapter_min=body.filters.chapter_min,
                chapter_max=body.filters.chapter_max,
                emotions=tuple(e.lower() for e in body.filters.emotions),
                topics=tuple(t.lower() for t in body.filters.topics),
                translation_source=body.filters.translation_source,
            ),
            top_k=body.top_k,
            expand_query=body.expand_query,
        ),
    )
    return RetrieveResponse(
        query=result.query,
        expanded_queries=list(result.expanded_queries),
        stages=result.stages,
        verses=[
            RetrievedVerseResponse(
                verse_id=v.verse_id,
                citation=v.citation,
                chapter=v.chapter,
                verse_number=v.verse_number,
                sanskrit=v.sanskrit,
                translation=v.translation,
                transliteration=v.transliteration,
                topics=v.topics,
                emotions=v.emotions,
                bm25_score=v.bm25_score,
                dense_score=v.dense_score,
                rrf_score=v.rrf_score,
                rerank_score=v.rerank_score,
                compressed_context=v.compressed_context,
                verified=v.verified,
            )
            for v in result.verses
        ],
    )
