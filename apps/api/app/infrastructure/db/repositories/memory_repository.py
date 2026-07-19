"""SQLAlchemy MemoryRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.memory_item import MemoryItem
from app.domain.enums.memory_kind import MemoryKind
from app.infrastructure.db.mappers.memory_mapper import apply_domain, to_domain
from app.infrastructure.db.models.memory_item import MemoryItem as MemoryItemModel
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


class SqlAlchemyMemoryRepository(SQLAlchemyRepository[MemoryItemModel, UUID]):
    """Persist memory items through SQLAlchemy."""

    model = MemoryItemModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, memory_id: UUID) -> MemoryItem | None:
        model = await self._session.get(MemoryItemModel, memory_id)
        return to_domain(model) if model is not None else None

    async def get_by_source(
        self,
        user_id: UUID,
        kind: MemoryKind,
        source_id: UUID,
    ) -> MemoryItem | None:
        result = await self._session.execute(
            select(MemoryItemModel).where(
                MemoryItemModel.user_id == user_id,
                MemoryItemModel.kind == kind.value,
                MemoryItemModel.source_id == source_id,
            ),
        )
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        kind: MemoryKind | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryItem]:
        stmt = select(MemoryItemModel).where(MemoryItemModel.user_id == user_id)
        if kind is not None:
            stmt = stmt.where(MemoryItemModel.kind == kind.value)
        stmt = (
            stmt.order_by(MemoryItemModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [to_domain(m) for m in result.scalars().all()]

    async def add(self, item: MemoryItem) -> MemoryItem:
        model = MemoryItemModel(
            id=item.id,
            user_id=item.user_id,
            kind=item.kind.value,
            title=item.title,
            content=item.content,
            source_id=item.source_id,
            metadata_=dict(item.metadata),
            qdrant_point_id=item.qdrant_point_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_domain(model)

    async def update(self, item: MemoryItem) -> MemoryItem:
        model = await self._session.get(MemoryItemModel, item.id)
        if model is None:
            raise ValueError(f"MemoryItem {item.id} not found")
        apply_domain(model, item)
        await self._session.flush()
        await self._session.refresh(model)
        return to_domain(model)

    async def delete(self, memory_id: UUID) -> bool:
        model = await self._session.get(MemoryItemModel, memory_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def update_qdrant_point_id(self, memory_id: UUID, point_id: str) -> None:
        model = await self._session.get(MemoryItemModel, memory_id)
        if model is None:
            return
        model.qdrant_point_id = point_id
        await self._session.flush()
