"""Memory item ORM model — canonical long-term memory rows."""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MemoryItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User memory fact mirrored into the Qdrant vector index."""

    __tablename__ = "memory_items"
    __table_args__ = (
        Index("ix_memory_items_user_kind_created", "user_id", "kind", "created_at"),
        Index("ix_memory_items_user_source", "user_id", "kind", "source_id"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default="{}",
    )
    qdrant_point_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
