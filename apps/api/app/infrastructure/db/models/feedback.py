"""Feedback ORM model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.message import Message
    from app.infrastructure.db.models.user import User


class Feedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User feedback on an assistant message."""

    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("user_id", "message_id", name="uq_feedback_user_message"),
        Index("ix_feedback_message_id", "message_id"),
        Index("ix_feedback_user_id_created_at", "user_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="feedback")
    message: Mapped["Message"] = relationship(back_populates="feedback")
