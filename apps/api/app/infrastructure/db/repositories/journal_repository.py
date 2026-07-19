"""SQLAlchemy JournalRepository."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.journal import Journal
from app.infrastructure.db.models.journal import Journal as JournalModel
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


def _to_domain(model: JournalModel) -> Journal:
    return Journal(
        id=model.id,
        user_id=model.user_id,
        title=model.title,
        content=model.content,
        mood_note=model.mood_note,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyJournalRepository(SQLAlchemyRepository[JournalModel, UUID]):
    """Persist journals through SQLAlchemy."""

    model = JournalModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, journal_id: UUID) -> Journal | None:
        model = await self._session.get(JournalModel, journal_id)
        return _to_domain(model) if model is not None else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Journal]:
        result = await self._session.execute(
            select(JournalModel)
            .where(JournalModel.user_id == user_id)
            .order_by(JournalModel.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def add(self, journal: Journal) -> Journal:
        model = JournalModel(
            id=journal.id or uuid4(),
            user_id=journal.user_id,
            title=journal.title,
            content=journal.content,
            mood_note=journal.mood_note,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def update(self, journal: Journal) -> Journal:
        model = await self._session.get(JournalModel, journal.id)
        if model is None:
            raise ValueError(f"Journal {journal.id} not found")
        model.title = journal.title
        model.content = journal.content
        model.mood_note = journal.mood_note
        model.updated_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def delete(self, journal_id: UUID) -> bool:
        model = await self._session.get(JournalModel, journal_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
