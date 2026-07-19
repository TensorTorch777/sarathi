"""Message ORM model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.conversation import Conversation
    from app.infrastructure.db.models.emotion import Emotion
    from app.infrastructure.db.models.feedback import Feedback
    from app.infrastructure.db.models.prompt_log import PromptLog
    from app.infrastructure.db.models.verse import Verse


class Message(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single message within a conversation."""

    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
        Index("ix_messages_role", "role"),
    )

    conversation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    verses: Mapped[list["Verse"]] = relationship(
        secondary="message_verses",
        back_populates="messages",
    )
    emotions: Mapped[list["Emotion"]] = relationship(
        secondary="message_emotions",
        back_populates="messages",
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )
    prompt_logs: Mapped[list["PromptLog"]] = relationship(back_populates="message")
