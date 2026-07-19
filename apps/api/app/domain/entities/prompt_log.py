"""PromptLog domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums import PromptStatus


@dataclass(slots=True)
class PromptLog:
    """Append-only audit record for an LLM prompt."""

    id: UUID
    model: str
    prompt: str
    status: PromptStatus
    created_at: datetime
    user_id: UUID | None = None
    conversation_id: UUID | None = None
    message_id: UUID | None = None
    completion: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
