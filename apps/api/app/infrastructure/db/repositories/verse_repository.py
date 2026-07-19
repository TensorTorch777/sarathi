"""SQLAlchemy verse repository / corpus adapter."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Verse
from app.infrastructure.db.models import Verse as VerseModel


def to_domain(model: VerseModel) -> Verse:
    """Map ORM verse to domain entity."""
    return Verse(
        id=model.id,
        chapter=model.chapter,
        verse_number=model.verse_number,
        sanskrit=model.sanskrit,
        transliteration=model.transliteration,
        translation=model.translation,
        translation_source=model.translation_source,
        commentary=model.commentary,
        qdrant_point_id=model.qdrant_point_id,
        topics=[str(t) for t in (model.topics or [])],
        emotions=[str(e) for e in (model.emotions or [])],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyVerseRepository:
    """Persist and load grounded Bhagavad Gita verses."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, verse_id: UUID) -> Verse | None:
        model = await self._session.get(VerseModel, verse_id)
        return to_domain(model) if model is not None else None

    async def get_by_chapter_verse(self, chapter: int, verse_number: int) -> Verse | None:
        result = await self._session.execute(
            select(VerseModel).where(
                VerseModel.chapter == chapter,
                VerseModel.verse_number == verse_number,
            ),
        )
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def list_by_chapter(self, chapter: int) -> list[Verse]:
        result = await self._session.execute(
            select(VerseModel)
            .where(VerseModel.chapter == chapter)
            .order_by(VerseModel.verse_number),
        )
        return [to_domain(m) for m in result.scalars().all()]

    async def list_all(self) -> list[Verse]:
        result = await self._session.execute(
            select(VerseModel).order_by(VerseModel.chapter, VerseModel.verse_number),
        )
        return [to_domain(m) for m in result.scalars().all()]

    async def get_by_ids(self, verse_ids: list[UUID]) -> dict[UUID, Verse]:
        if not verse_ids:
            return {}
        result = await self._session.execute(
            select(VerseModel).where(VerseModel.id.in_(verse_ids)),
        )
        return {m.id: to_domain(m) for m in result.scalars().all()}

    async def get_by_citation(self, chapter: int, verse_number: int) -> Verse | None:
        return await self.get_by_chapter_verse(chapter, verse_number)

    async def add(self, verse: Verse) -> Verse:
        model = VerseModel(
            id=verse.id,
            chapter=verse.chapter,
            verse_number=verse.verse_number,
            sanskrit=verse.sanskrit,
            transliteration=verse.transliteration,
            translation=verse.translation,
            translation_source=verse.translation_source,
            commentary=verse.commentary,
            qdrant_point_id=verse.qdrant_point_id,
            topics=verse.topics,
            emotions=verse.emotions,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_domain(model)

    async def add_many(self, verses: list[Verse]) -> list[Verse]:
        return [await self.add(verse) for verse in verses]

    async def update_qdrant_point_id(self, verse_id: UUID, point_id: str) -> None:
        model = await self._session.get(VerseModel, verse_id)
        if model is None:
            return
        model.qdrant_point_id = point_id
        await self._session.flush()
