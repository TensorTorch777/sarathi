"""Chat answer routes — full grounded pipeline."""

from fastapi import APIRouter

from app.api.v1.deps import CurrentUserDep, GenerateAnswerUseCaseDep
from app.api.v1.schemas.chat import (
    AnswerCitationResponse,
    ChatRequest,
    ChatResponse,
)
from app.api.v1.schemas.retrieval import RetrievedVerseResponse
from app.application.dto.answer import GenerateAnswerQuery

router = APIRouter(prefix="/chat")


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Ask Sarathi AI",
    description=(
        "Runs User → Emotion → Topic → Query Rewrite → Hybrid Search → Rerank → "
        "Prompt Builder → GPT → Citation Verification → Answer."
    ),
)
async def ask(
    body: ChatRequest,
    user: CurrentUserDep,
    use_case: GenerateAnswerUseCaseDep,
) -> ChatResponse:
    """Generate a citation-grounded answer from the Bhagavad Gita."""
    result = await use_case.execute(
        GenerateAnswerQuery(
            message=body.message,
            conversation_id=body.conversation_id,
            top_k=body.top_k,
            user_id=user.id,
        ),
    )
    return ChatResponse(
        answer=result.answer,
        emotions=list(result.emotions),
        topics=list(result.topics),
        rewritten_query=result.rewritten_query,
        stages=result.stages,
        citations=[
            AnswerCitationResponse(
                citation=c.citation,
                chapter=c.chapter,
                verse_number=c.verse_number,
                verse_id=c.verse_id,
                translation=c.translation,
            )
            for c in result.citations
        ],
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
