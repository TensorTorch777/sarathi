"""Association tables for many-to-many relationships."""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base


class MessageVerse(Base):
    """Citation link between an assistant message and a grounded verse."""

    __tablename__ = "message_verses"

    message_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    )
    verse_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("verses.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class MessageEmotion(Base):
    """Emotion labels associated with a message."""

    __tablename__ = "message_emotions"

    message_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    )
    emotion_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("emotions.id", ondelete="RESTRICT"),
        primary_key=True,
    )


class JournalEmotion(Base):
    """Emotion labels associated with a journal entry."""

    __tablename__ = "journal_emotions"

    journal_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("journals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    emotion_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("emotions.id", ondelete="RESTRICT"),
        primary_key=True,
    )
