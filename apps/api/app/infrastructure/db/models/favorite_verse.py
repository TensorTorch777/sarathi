"""Favorite verse ORM model."""

from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FavoriteVerse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-marked favorite Gita verse with optional personal note."""

    __tablename__ = "favorite_verses"
    __table_args__ = (
        UniqueConstraint("user_id", "verse_id", name="uq_favorite_verses_user_verse"),
        Index("ix_favorite_verses_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    verse_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("verses.id", ondelete="CASCADE"),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    memory_item_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("memory_items.id", ondelete="SET NULL"),
        nullable=True,
    )
