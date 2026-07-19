"""Answer-generation pipeline DTOs."""

from dataclasses import dataclass, field
from uuid import UUID

from app.application.dto.retrieval import RankedVerse


@dataclass(slots=True, frozen=True)
class GenerateAnswerQuery:
    """User question entering the full Sarathi answer pipeline."""

    message: str
    conversation_id: UUID | None = None
    top_k: int = 5
    # Voice fast-path: skip LLM-based emotion/topic/rewrite to cut latency.
    voice_fast: bool = False
    user_id: UUID | None = None


@dataclass(slots=True, frozen=True)
class PromptBundle:
    """Messages prepared for the language model."""

    system_prompt: str
    user_prompt: str


@dataclass(slots=True)
class AnswerCitation:
    """A citation kept after answer-level verification."""

    citation: str
    chapter: int
    verse_number: int
    verse_id: UUID
    translation: str


@dataclass(slots=True, frozen=True)
class GenerateAnswerResult:
    """Final grounded answer plus pipeline trace."""

    answer: str
    emotions: tuple[str, ...]
    topics: tuple[str, ...]
    rewritten_query: str
    verses: tuple[RankedVerse, ...]
    citations: tuple[AnswerCitation, ...]
    stages: dict[str, object] = field(default_factory=dict)
