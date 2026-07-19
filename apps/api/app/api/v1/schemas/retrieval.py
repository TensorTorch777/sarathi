"""Retrieval API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalFiltersRequest(BaseModel):
    """Optional metadata / emotion / topic filters."""

    chapters: list[int] = Field(default_factory=list)
    chapter_min: int | None = Field(default=None, ge=1, le=18)
    chapter_max: int | None = Field(default=None, ge=1, le=18)
    emotions: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    translation_source: str | None = None


class RetrieveRequest(BaseModel):
    """Hybrid RAG retrieval request."""

    query: str = Field(min_length=1, max_length=2000)
    filters: RetrievalFiltersRequest = Field(default_factory=RetrievalFiltersRequest)
    top_k: int = Field(default=5, ge=1, le=5)
    expand_query: bool = True


class RetrievedVerseResponse(BaseModel):
    """A single verified retrieved verse."""

    verse_id: UUID
    citation: str
    chapter: int
    verse_number: int
    sanskrit: str
    translation: str
    transliteration: str | None = None
    topics: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    bm25_score: float
    dense_score: float
    rrf_score: float
    rerank_score: float
    compressed_context: str
    verified: bool


class RetrieveResponse(BaseModel):
    """Top verified verses from the hybrid pipeline."""

    query: str
    expanded_queries: list[str]
    verses: list[RetrievedVerseResponse]
    stages: dict[str, object]
