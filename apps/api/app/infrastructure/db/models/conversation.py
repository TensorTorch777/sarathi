"""Conversation ORM model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.message import Message
    from app.infrastructure.db.models.prompt_log import PromptLog
    from app.infrastructure.db.models.user import User


class Conversation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A chat session between a user and Sarathi AI."""

    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_user_id_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    prompt_logs: Mapped[list["PromptLog"]] = relationship(back_populates="conversation")
