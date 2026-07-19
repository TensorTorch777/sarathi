"""Map MemoryItem ORM ↔ domain."""

from app.domain.entities.memory_item import MemoryItem
from app.domain.enums.memory_kind import MemoryKind
from app.infrastructure.db.models.memory_item import MemoryItem as MemoryItemModel


def to_domain(model: MemoryItemModel) -> MemoryItem:
    """Convert ORM row to domain entity."""
    return MemoryItem(
        id=model.id,
        user_id=model.user_id,
        kind=MemoryKind(model.kind),
        title=model.title,
        content=model.content,
        source_id=model.source_id,
        metadata=dict(model.metadata_ or {}),
        qdrant_point_id=model.qdrant_point_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def apply_domain(model: MemoryItemModel, item: MemoryItem) -> None:
    """Copy domain fields onto an ORM row."""
    model.user_id = item.user_id
    model.kind = item.kind.value
    model.title = item.title
    model.content = item.content
    model.source_id = item.source_id
    model.metadata_ = dict(item.metadata)
    model.qdrant_point_id = item.qdrant_point_id
