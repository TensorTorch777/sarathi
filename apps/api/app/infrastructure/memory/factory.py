"""Compose memory indexing and recall services."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.memory import IndexMemoryUseCase, RecallMemoryUseCase
from app.core.config import Settings
from app.infrastructure.db.repositories.memory_repository import SqlAlchemyMemoryRepository
from app.infrastructure.llm.embeddings import HashEmbedder, OllamaEmbedder
from app.infrastructure.llm.ollama import OllamaClient
from app.infrastructure.vector.memory_store import QdrantMemoryStore


def build_memory_embedder(settings: Settings) -> OllamaEmbedder | HashEmbedder:
    """Local Ollama embeddings, with hash fallback for tests."""
    if settings.use_local_llm:
        return OllamaEmbedder(settings, client=OllamaClient(settings))
    return HashEmbedder(dimensions=settings.embedding_dimensions)


def build_memory_store(settings: Settings, *, vector_size: int | None = None) -> QdrantMemoryStore:
    """Qdrant collection for user memories."""
    return QdrantMemoryStore(settings, vector_size=vector_size)


def build_index_memory_use_case(
    *,
    session: AsyncSession,
    settings: Settings,
) -> IndexMemoryUseCase:
    """Wire IndexMemoryUseCase for the current request."""
    embedder = build_memory_embedder(settings)
    return IndexMemoryUseCase(
        memories=SqlAlchemyMemoryRepository(session),
        store=build_memory_store(settings, vector_size=embedder.dimensions),
        embedder=embedder,
    )


def build_recall_memory_use_case(
    *,
    session: AsyncSession,
    settings: Settings,
) -> RecallMemoryUseCase:
    """Wire RecallMemoryUseCase for the current request."""
    embedder = build_memory_embedder(settings)
    return RecallMemoryUseCase(
        memories=SqlAlchemyMemoryRepository(session),
        store=build_memory_store(settings, vector_size=embedder.dimensions),
        embedder=embedder,
    )
