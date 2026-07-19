"""Journal ORM model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.emotion import Emotion
    from app.infrastructure.db.models.reflection import Reflection
    from app.infrastructure.db.models.user import User


class Journal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Private user journal entry for reflective practice."""

    __tablename__ = "journals"
    __table_args__ = (Index("ix_journals_user_id_created_at", "user_id", "created_at"),)

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="journals")
    reflections: Mapped[list["Reflection"]] = relationship(
        back_populates="journal",
        cascade="all, delete-orphan",
    )
    emotions: Mapped[list["Emotion"]] = relationship(
        secondary="journal_emotions",
        back_populates="journals",
    )
