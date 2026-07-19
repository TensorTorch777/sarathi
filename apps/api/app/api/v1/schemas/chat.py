"""Chat / answer API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.api.v1.schemas.retrieval import RetrievedVerseResponse


class ChatRequest(BaseModel):
    """Ask Sarathi AI a grounded question."""

    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    top_k: int = Field(default=5, ge=1, le=5)


class AnswerCitationResponse(BaseModel):
    """Verified citation attached to the answer."""

    citation: str
    chapter: int
    verse_number: int
    verse_id: UUID
    translation: str


class ChatResponse(BaseModel):
    """Grounded answer with pipeline metadata."""

    answer: str
    emotions: list[str]
    topics: list[str]
    rewritten_query: str
    citations: list[AnswerCitationResponse]
    verses: list[RetrievedVerseResponse]
    stages: dict[str, object]
