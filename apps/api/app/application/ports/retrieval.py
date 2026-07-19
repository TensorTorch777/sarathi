"""Ports for the hybrid RAG retrieval pipeline."""

from typing import Protocol
from uuid import UUID

from app.application.dto.retrieval import RankedVerse, RetrievalFilters
from app.domain.entities import Verse


class EmbedderPort(Protocol):
    """Create dense embeddings for queries and documents."""

    async def embed_query(self, text: str) -> list[float]:
        """Embed a search query."""
        ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents for indexing."""
        ...

    @property
    def dimensions(self) -> int:
        """Embedding vector size."""
        ...


class QueryExpanderPort(Protocol):
    """Expand a user query into retrieval-friendly variants."""

    async def expand(self, query: str) -> list[str]:
        """Return the original query plus expansions (deduplicated)."""
        ...


class SparseRetrieverPort(Protocol):
    """BM25 / lexical retriever."""

    async def search(
        self,
        query: str,
        *,
        filters: RetrievalFilters,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """Return (verse_id, bm25_score) ranked descending."""
        ...

    async def rebuild(self, verses: list[Verse]) -> None:
        """Rebuild the in-memory BM25 index from corpus verses."""
        ...


class DenseRetrieverPort(Protocol):
    """Dense vector retriever (Qdrant)."""

    async def search(
        self,
        query_vector: list[float],
        *,
        filters: RetrievalFilters,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """Return (verse_id, similarity_score) ranked descending."""
        ...

    async def upsert_verse(
        self,
        verse: Verse,
        vector: list[float],
    ) -> str:
        """Upsert a verse point; return point id."""
        ...


class HybridFusionPort(Protocol):
    """Fuse sparse and dense rankings."""

    def fuse(
        self,
        sparse: list[tuple[UUID, float]],
        dense: list[tuple[UUID, float]],
        *,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """Return fused (verse_id, rrf_score) ranked descending."""
        ...


class RerankerPort(Protocol):
    """Cross-encoder (or compatible) reranker."""

    async def rerank(
        self,
        query: str,
        candidates: list[RankedVerse],
        *,
        top_k: int,
    ) -> list[RankedVerse]:
        """Rescore candidates and return top_k ordered by rerank_score."""
        ...


class ContextCompressorPort(Protocol):
    """Compress verse context for grounded generation."""

    def compress(self, query: str, verse: RankedVerse) -> str:
        """Return a compact, citation-preserving context string."""
        ...


class CitationVerifierPort(Protocol):
    """Verify retrieved verses against the canonical corpus."""

    async def verify(
        self,
        candidates: list[RankedVerse],
        *,
        min_rerank_score: float,
        top_k: int,
    ) -> list[RankedVerse]:
        """Keep only authentic, score-qualified verses (max top_k)."""
        ...


class VerseCorpusPort(Protocol):
    """Load verse rows for indexing and verification."""

    async def list_all(self) -> list[Verse]:
        """Return the full grounded corpus."""
        ...

    async def get_by_ids(self, verse_ids: list[UUID]) -> dict[UUID, Verse]:
        """Fetch verses by id."""
        ...

    async def get_by_citation(self, chapter: int, verse_number: int) -> Verse | None:
        """Fetch a verse by canonical chapter/verse identity."""
        ...
