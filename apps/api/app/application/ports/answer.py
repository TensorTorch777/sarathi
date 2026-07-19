"""Ports for the end-to-end answer pipeline."""

from collections.abc import AsyncIterator
from typing import Protocol

from app.application.dto.answer import AnswerCitation, PromptBundle
from app.application.dto.memory import RecalledMemory
from app.application.dto.retrieval import RankedVerse


class EmotionDetectorPort(Protocol):
    """Infer emotional states from the user message."""

    async def detect(self, message: str) -> list[str]:
        """Return normalized emotion slugs (may be empty)."""
        ...


class TopicDetectorPort(Protocol):
    """Infer Gita topics from the user message."""

    async def detect(self, message: str) -> list[str]:
        """Return normalized topic slugs (may be empty)."""
        ...


class QueryRewriterPort(Protocol):
    """Rewrite the user message into a retrieval-optimized query."""

    async def rewrite(
        self,
        message: str,
        *,
        emotions: list[str],
        topics: list[str],
    ) -> str:
        """Return a single rewritten search query."""
        ...


class PromptBuilderPort(Protocol):
    """Build grounded prompts for GPT."""

    def build(
        self,
        *,
        message: str,
        emotions: list[str],
        topics: list[str],
        verses: list[RankedVerse],
        memories: list[RecalledMemory] | None = None,
    ) -> PromptBundle:
        """Compose system + user prompts from verified evidence (+ optional memory)."""
        ...


class AnswerGeneratorPort(Protocol):
    """Generate an assistant reply from a prompt bundle."""

    async def generate(self, prompt: PromptBundle) -> str:
        """Return the model completion text."""
        ...

    async def generate_stream(self, prompt: PromptBundle) -> AsyncIterator[str]:
        """Yield completion text deltas for low-latency voice/chat streaming."""
        ...


class AnswerCitationVerifierPort(Protocol):
    """Verify that answer citations exist in the retrieved evidence set."""

    def verify(
        self,
        answer: str,
        verses: list[RankedVerse],
    ) -> tuple[str, list[AnswerCitation], list[str]]:
        """Return cleaned answer, kept citations, and removed citation labels."""
        ...
