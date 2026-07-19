"""PromptLog ORM model — audit trail for LLM calls."""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.conversation import Conversation
    from app.infrastructure.db.models.message import Message
    from app.infrastructure.db.models.user import User


class PromptLog(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    """Append-only log of prompts sent to the language model."""

    __tablename__ = "prompt_logs"
    __table_args__ = (
        Index("ix_prompt_logs_user_id_created_at", "user_id", "created_at"),
        Index("ix_prompt_logs_conversation_id_created_at", "conversation_id", "created_at"),
        Index("ix_prompt_logs_message_id", "message_id"),
        Index("ix_prompt_logs_status", "status"),
    )

    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    conversation_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )
    message_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    completion: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="success",
        server_default="success",
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    user: Mapped["User | None"] = relationship(back_populates="prompt_logs")
    conversation: Mapped["Conversation | None"] = relationship(back_populates="prompt_logs")
    message: Mapped["Message | None"] = relationship(back_populates="prompt_logs")
