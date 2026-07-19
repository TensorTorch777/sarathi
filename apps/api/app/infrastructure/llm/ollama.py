"""Local Ollama client for Gemma chat and embeddings (no API keys)."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import Settings
from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Thin async client for a local Ollama server."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._chat_model = settings.ollama_chat_model
        self._embed_model = settings.ollama_embed_model
        self._timeout = settings.ollama_timeout_seconds
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP client when owned by this instance."""
        if self._owns_client:
            await self._client.aclose()

    async def healthcheck(self) -> bool:
        """Return True when Ollama is reachable."""
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def complete(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        model: str | None = None,
    ) -> str:
        """Run a local chat completion (Gemma by default)."""
        payload: dict[str, Any] = {
            "model": model or self._chat_model,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            response = await self._client.post("/api/chat", json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise AppError(
                f"Local Ollama chat failed ({self._chat_model}). "
                "Is Ollama running and was the model pulled?",
                code="ollama_chat_error",
                status_code=502,
                details={"error": str(exc), "model": model or self._chat_model},
            ) from exc

        data = response.json()
        content = (data.get("message") or {}).get("content")
        if not content:
            raise AppError(
                "Empty response from local Ollama chat model",
                code="ollama_empty_response",
                status_code=502,
            )
        return str(content).strip()

    async def complete_stream(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.3,
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream chat completion token deltas from local Ollama."""
        payload: dict[str, Any] = {
            "model": model or self._chat_model,
            "stream": True,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            async with self._client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    import json

                    data = json.loads(line)
                    if data.get("done"):
                        break
                    content = (data.get("message") or {}).get("content")
                    if content:
                        yield str(content)
        except httpx.HTTPError as exc:
            raise AppError(
                f"Local Ollama stream failed ({self._chat_model}).",
                code="ollama_stream_error",
                status_code=502,
                details={"error": str(exc), "model": model or self._chat_model},
            ) from exc

    async def embed(self, text: str, *, model: str | None = None) -> list[float]:
        """Embed a single text with the local embedding model."""
        vectors = await self.embed_many([text], model=model)
        return vectors[0]

    async def embed_many(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """Embed many texts sequentially via Ollama embeddings API."""
        if not texts:
            return []
        model_name = model or self._embed_model
        vectors: list[list[float]] = []
        try:
            for text in texts:
                response = await self._client.post(
                    "/api/embeddings",
                    json={"model": model_name, "prompt": text},
                )
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding")
                if not embedding:
                    raise AppError(
                        "Empty embedding from local Ollama model",
                        code="ollama_empty_embedding",
                        status_code=502,
                    )
                vectors.append([float(x) for x in embedding])
        except httpx.HTTPError as exc:
            raise AppError(
                f"Local Ollama embeddings failed ({model_name}). "
                "Pull the embed model, e.g. `ollama pull nomic-embed-text`.",
                code="ollama_embed_error",
                status_code=502,
                details={"error": str(exc), "model": model_name},
            ) from exc
        return vectors
