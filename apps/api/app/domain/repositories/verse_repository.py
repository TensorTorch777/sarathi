"""Verse repository interface."""

from typing import Protocol
from uuid import UUID

from app.domain.entities import Verse


class VerseRepository(Protocol):
    """Persistence port for Bhagavad Gita verses."""

    async def get_by_id(self, verse_id: UUID) -> Verse | None:
        """Fetch a verse by identifier."""
        ...

    async def get_by_chapter_verse(self, chapter: int, verse_number: int) -> Verse | None:
        """Fetch a verse by canonical chapter and verse number."""
        ...

    async def list_by_chapter(self, chapter: int) -> list[Verse]:
        """List all verses in a chapter, ordered by verse number."""
        ...

    async def add(self, verse: Verse) -> Verse:
        """Persist a new verse."""
        ...

    async def add_many(self, verses: list[Verse]) -> list[Verse]:
        """Persist multiple verses (ingestion)."""
        ...
