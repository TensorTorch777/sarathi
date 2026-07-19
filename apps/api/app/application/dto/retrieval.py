"""Retrieval pipeline DTOs."""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True, frozen=True)
class RetrievalFilters:
    """Structured filters applied to sparse and dense retrieval."""

    chapters: tuple[int, ...] = ()
    chapter_min: int | None = None
    chapter_max: int | None = None
    emotions: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()
    translation_source: str | None = None


@dataclass(slots=True, frozen=True)
class RetrieveVersesQuery:
    """Input to the hybrid RAG retrieval use case."""

    query: str
    filters: RetrievalFilters = field(default_factory=RetrievalFilters)
    top_k: int = 5
    candidate_pool_size: int = 30
    expand_query: bool = True


@dataclass(slots=True)
class RankedVerse:
    """A verse candidate with stage scores."""

    verse_id: UUID
    chapter: int
    verse_number: int
    citation: str
    sanskrit: str
    translation: str
    transliteration: str | None
    commentary: str | None
    topics: list[str]
    emotions: list[str]
    bm25_score: float = 0.0
    dense_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0
    compressed_context: str = ""
    verified: bool = False


@dataclass(slots=True, frozen=True)
class RetrievalResult:
    """Final retrieval output: top verified verses + pipeline metadata."""

    query: str
    expanded_queries: tuple[str, ...]
    filters: RetrievalFilters
    verses: tuple[RankedVerse, ...]
    stages: dict[str, object] = field(default_factory=dict)
