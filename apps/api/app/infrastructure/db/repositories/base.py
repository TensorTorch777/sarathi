"""Base SQLAlchemy repository implementation."""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")
IdT = TypeVar("IdT")


class SQLAlchemyRepository(Generic[ModelT, IdT]):
    """Generic async repository backed by SQLAlchemy.

    Subclass with a concrete model once domain tables exist.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: IdT) -> ModelT | None:
        """Fetch a model row by primary key."""
        return await self._session.get(self.model, entity_id)

    async def add(self, entity: ModelT) -> ModelT:
        """Add a model instance to the session."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def delete(self, entity_id: IdT) -> bool:
        """Delete a model row by primary key."""
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Return a simple paginated list of rows."""
        result = await self._session.execute(
            select(self.model).limit(limit).offset(offset),
        )
        return list(result.scalars().all())
