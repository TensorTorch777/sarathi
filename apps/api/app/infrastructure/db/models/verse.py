"""Verse ORM model — canonical Bhagavad Gita corpus rows."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.message import Message
    from app.infrastructure.db.models.reflection import Reflection


class Verse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A grounded Bhagavad Gita verse with stable chapter/verse identity."""

    __tablename__ = "verses"
    __table_args__ = (
        UniqueConstraint("chapter", "verse_number", name="uq_verses_chapter_verse_number"),
        Index("ix_verses_chapter", "chapter"),
        Index("ix_verses_topics", "topics", postgresql_using="gin"),
        Index("ix_verses_emotions", "emotions", postgresql_using="gin"),
    )

    chapter: Mapped[int] = mapped_column(Integer, nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sanskrit: Mapped[str] = mapped_column(Text, nullable=False)
    transliteration: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation: Mapped[str] = mapped_column(Text, nullable=False)
    translation_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    topics: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )
    emotions: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )

    messages: Mapped[list["Message"]] = relationship(
        secondary="message_verses",
        back_populates="verses",
    )
    reflections: Mapped[list["Reflection"]] = relationship(back_populates="verse")
