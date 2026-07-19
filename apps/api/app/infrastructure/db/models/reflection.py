"""Reflection ORM model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.journal import Journal
    from app.infrastructure.db.models.user import User
    from app.infrastructure.db.models.verse import Verse


class Reflection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Grounded reflection tied to a journal entry and optional verse."""

    __tablename__ = "reflections"
    __table_args__ = (
        Index("ix_reflections_journal_id_created_at", "journal_id", "created_at"),
        Index("ix_reflections_user_id_created_at", "user_id", "created_at"),
        Index("ix_reflections_verse_id", "verse_id"),
    )

    journal_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("journals.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    verse_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("verses.id", ondelete="SET NULL"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    journal: Mapped["Journal"] = relationship(back_populates="reflections")
    user: Mapped["User"] = relationship(back_populates="reflections")
    verse: Mapped["Verse | None"] = relationship(back_populates="reflections")
