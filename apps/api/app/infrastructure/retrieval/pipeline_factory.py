"""Compose retrieval pipeline dependencies (local Ollama by default)."""

from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.retrieval import RetrieveVersesUseCase
from app.core.config import Settings
from app.infrastructure.db.repositories.verse_repository import SqlAlchemyVerseRepository
from app.infrastructure.llm.embeddings import HashEmbedder, OllamaEmbedder
from app.infrastructure.llm.ollama import OllamaClient
from app.infrastructure.retrieval.citation import CorpusCitationVerifier
from app.infrastructure.retrieval.compression import ExtractiveContextCompressor
from app.infrastructure.retrieval.hybrid.rrf import ReciprocalRankFusion
from app.infrastructure.retrieval.query_expansion import GitaQueryExpander
from app.infrastructure.retrieval.rerank.cross_encoder import (
    CrossEncoderReranker,
    LexicalCrossEncoderReranker,
)
from app.infrastructure.retrieval.sparse.bm25 import BM25SparseRetriever
from app.infrastructure.vector.qdrant_store import InMemoryDenseRetriever, QdrantDenseRetriever

_bm25_index = BM25SparseRetriever()
_bm25_ready = False


async def ensure_bm25_index(session: AsyncSession) -> BM25SparseRetriever:
    """Load all verses into the shared BM25 index once."""
    global _bm25_ready
    if not _bm25_ready:
        corpus = SqlAlchemyVerseRepository(session)
        verses = await corpus.list_all()
        await _bm25_index.rebuild(verses)
        _bm25_ready = True
    return _bm25_index


def reset_bm25_index() -> None:
    """Test helper to force BM25 rebuild."""
    global _bm25_ready
    _bm25_ready = False


async def build_retrieve_verses_use_case(
    *,
    session: AsyncSession,
    settings: Settings,
    use_inmemory_dense: bool = False,
    ollama: OllamaClient | None = None,
) -> RetrieveVersesUseCase:
    """Wire a local retrieval pipeline (Ollama embeddings + Qdrant)."""
    corpus = SqlAlchemyVerseRepository(session)
    sparse = await ensure_bm25_index(session)

    llm = ollama
    if settings.use_local_llm and llm is None:
        llm = OllamaClient(settings)

    if settings.use_local_llm and not use_inmemory_dense:
        embedder: OllamaEmbedder | HashEmbedder = OllamaEmbedder(settings, client=llm)
    else:
        embedder = HashEmbedder(dimensions=min(settings.embedding_dimensions, 64))

    if use_inmemory_dense:
        dense: QdrantDenseRetriever | InMemoryDenseRetriever = InMemoryDenseRetriever()
    else:
        qdrant = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        dense = QdrantDenseRetriever(
            settings,
            client=qdrant,
            vector_size=embedder.dimensions,
        )
        await dense.ensure_collection()

    if settings.reranker_backend == "cross_encoder":
        reranker: CrossEncoderReranker | LexicalCrossEncoderReranker = CrossEncoderReranker(
            settings.reranker_model,
        )
    else:
        reranker = LexicalCrossEncoderReranker()

    expander = GitaQueryExpander(settings, llm=llm if settings.use_local_llm else None)

    return RetrieveVersesUseCase(
        corpus=corpus,
        query_expander=expander,
        sparse=sparse,
        dense=dense,
        embedder=embedder,
        fusion=ReciprocalRankFusion(k=settings.retrieval_rrf_k),
        reranker=reranker,
        compressor=ExtractiveContextCompressor(),
        verifier=CorpusCitationVerifier(corpus),
        bm25_top_k=settings.retrieval_bm25_top_k,
        dense_top_k=settings.retrieval_dense_top_k,
        min_rerank_score=settings.retrieval_min_rerank_score,
    )
