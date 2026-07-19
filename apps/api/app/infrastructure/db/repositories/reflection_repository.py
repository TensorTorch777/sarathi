"""SQLAlchemy ReflectionRepository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.reflection import Reflection
from app.infrastructure.db.models.reflection import Reflection as ReflectionModel
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


def _to_domain(model: ReflectionModel) -> Reflection:
    return Reflection(
        id=model.id,
        journal_id=model.journal_id,
        user_id=model.user_id,
        verse_id=model.verse_id,
        content=model.content,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyReflectionRepository(SQLAlchemyRepository[ReflectionModel, UUID]):
    """Persist reflections through SQLAlchemy."""

    model = ReflectionModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, reflection_id: UUID) -> Reflection | None:
        model = await self._session.get(ReflectionModel, reflection_id)
        return _to_domain(model) if model is not None else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Reflection]:
        result = await self._session.execute(
            select(ReflectionModel)
            .where(ReflectionModel.user_id == user_id)
            .order_by(ReflectionModel.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def list_by_journal(self, journal_id: UUID) -> list[Reflection]:
        result = await self._session.execute(
            select(ReflectionModel)
            .where(ReflectionModel.journal_id == journal_id)
            .order_by(ReflectionModel.created_at.desc()),
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def add(self, reflection: Reflection) -> Reflection:
        model = ReflectionModel(
            id=reflection.id or uuid4(),
            journal_id=reflection.journal_id,
            user_id=reflection.user_id,
            verse_id=reflection.verse_id,
            content=reflection.content,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def delete(self, reflection_id: UUID) -> bool:
        model = await self._session.get(ReflectionModel, reflection_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
