"""Local LLM / embedding adapters (Ollama)."""

from app.infrastructure.llm.embeddings import HashEmbedder, OllamaEmbedder
from app.infrastructure.llm.ollama import OllamaClient

__all__ = ["HashEmbedder", "OllamaClient", "OllamaEmbedder"]
