"""Local and fallback embedding adapters."""

from app.core.config import Settings
from app.infrastructure.llm.ollama import OllamaClient


class OllamaEmbedder:
    """Dense embeddings via a local Ollama embedding model (no API keys)."""

    def __init__(self, settings: Settings, client: OllamaClient | None = None) -> None:
        self._settings = settings
        self._client = client or OllamaClient(settings)

    @property
    def dimensions(self) -> int:
        """Configured embedding vector size."""
        return self._settings.embedding_dimensions

    async def embed(self, text: str) -> list[float]:
        """Embed a single text (query or document)."""
        return await self._client.embed(text)

    async def embed_query(self, text: str) -> list[float]:
        """Embed a search query."""
        return await self.embed(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents for indexing."""
        return await self._client.embed_many(texts)


class HashEmbedder:
    """Deterministic local embedder for unit tests (not for production quality)."""

    def __init__(self, dimensions: int = 64) -> None:
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        return self._embed(text)

    async def embed_query(self, text: str) -> list[float]:
        return await self.embed(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        tokens = text.lower().split()
        if not tokens:
            return vector
        for token in tokens:
            idx = hash(token) % self._dimensions
            vector[idx] += 1.0
        norm = sum(v * v for v in vector) ** 0.5 or 1.0
        return [v / norm for v in vector]
