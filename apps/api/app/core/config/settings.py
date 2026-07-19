"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[5]
_ENV_FILES = (
    str(_REPO_ROOT / ".env"),
    str(_API_ROOT / ".env"),
)


class Settings(BaseSettings):
    """Central configuration for the Sarathi AI API."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="Sarathi AI", alias="APP_NAME")
    app_env: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        alias="APP_ENV",
    )
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    database_url: str = Field(
        default="postgresql+asyncpg://sarathi:sarathi@localhost:5432/sarathi",
        alias="DATABASE_URL",
    )

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="gita_verses_local", alias="QDRANT_COLLECTION")
    memory_qdrant_collection: str = Field(
        default="user_memory_local",
        alias="MEMORY_QDRANT_COLLECTION",
    )
    memory_recall_top_k: int = Field(default=6, alias="MEMORY_RECALL_TOP_K")
    memory_enabled: bool = Field(default=True, alias="MEMORY_ENABLED")

    # Local LLM (Ollama / Gemma) — no cloud API keys required
    llm_provider: Literal["ollama", "template"] = Field(
        default="ollama",
        alias="LLM_PROVIDER",
    )
    ollama_base_url: str = Field(default="http://127.0.0.1:11435", alias="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(default="gemma4:12b", alias="OLLAMA_CHAT_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    ollama_timeout_seconds: float = Field(default=180.0, alias="OLLAMA_TIMEOUT_SECONDS")
    embedding_dimensions: int = Field(default=768, alias="EMBEDDING_DIMENSIONS")

    # Voice mode — local Whisper STT + Piper TTS (no cloud keys)
    voice_enabled: bool = Field(default=True, alias="VOICE_ENABLED")
    voice_warmup_on_startup: bool = Field(default=True, alias="VOICE_WARMUP_ON_STARTUP")
    whisper_model: str = Field(default="base.en", alias="WHISPER_MODEL")
    # Prefer cuda when libcublas is present; WhisperSTT auto-falls back to CPU.
    whisper_device: str = Field(default="cpu", alias="WHISPER_DEVICE")
    whisper_compute_type: str = Field(default="int8", alias="WHISPER_COMPUTE_TYPE")
    whisper_language: str = Field(default="en", alias="WHISPER_LANGUAGE")
    piper_model_path: str = Field(
        default="~/.local/share/sarathi/piper/en_US-lessac-medium.onnx",
        alias="PIPER_MODEL_PATH",
    )
    piper_use_cuda: bool = Field(default=False, alias="PIPER_USE_CUDA")
    tts_sample_rate: int = Field(default=22050, alias="TTS_SAMPLE_RATE")
    tts_length_scale: float = Field(default=1.12, alias="TTS_LENGTH_SCALE")
    tts_noise_scale: float = Field(default=0.45, alias="TTS_NOISE_SCALE")
    tts_noise_w_scale: float = Field(default=0.65, alias="TTS_NOISE_W_SCALE")
    voice_stt_target_ms: int = Field(default=700, alias="VOICE_STT_TARGET_MS")

    # Retrieval / RAG
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    retrieval_candidate_pool: int = Field(default=30, alias="RETRIEVAL_CANDIDATE_POOL")
    retrieval_bm25_top_k: int = Field(default=20, alias="RETRIEVAL_BM25_TOP_K")
    retrieval_dense_top_k: int = Field(default=20, alias="RETRIEVAL_DENSE_TOP_K")
    retrieval_rrf_k: int = Field(default=60, alias="RETRIEVAL_RRF_K")
    retrieval_min_rerank_score: float = Field(
        default=-10.0,
        alias="RETRIEVAL_MIN_RERANK_SCORE",
    )
    retrieval_query_expansion: bool = Field(
        default=True,
        alias="RETRIEVAL_QUERY_EXPANSION",
    )
    reranker_backend: Literal["cross_encoder", "lexical"] = Field(
        default="lexical",
        alias="RERANKER_BACKEND",
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        alias="RERANKER_MODEL",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=False, alias="LOG_JSON")

    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    @field_validator("qdrant_api_key", mode="before")
    @classmethod
    def empty_str_to_none(cls, value: object) -> object:
        """Treat blank env vars as unset."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Return True when running in production."""
        return self.app_env == "production"

    @property
    def use_local_llm(self) -> bool:
        """Return True when Ollama-backed generation/embeddings are enabled."""
        return self.llm_provider == "ollama"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for dependency injection."""
    return Settings()
