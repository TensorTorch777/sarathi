"""Emotion ORM model — taxonomy of emotional states."""

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.journal import Journal
    from app.infrastructure.db.models.message import Message


class Emotion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Reusable emotion label for chat and journaling contexts."""

    __tablename__ = "emotions"
    __table_args__ = (Index("ix_emotions_slug", "slug", unique=True),)

    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    messages: Mapped[list["Message"]] = relationship(
        secondary="message_emotions",
        back_populates="emotions",
    )
    journals: Mapped[list["Journal"]] = relationship(
        secondary="journal_emotions",
        back_populates="emotions",
    )
