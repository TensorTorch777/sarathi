"""User ORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.conversation import Conversation
    from app.infrastructure.db.models.feedback import Feedback
    from app.infrastructure.db.models.journal import Journal
    from app.infrastructure.db.models.prompt_log import PromptLog
    from app.infrastructure.db.models.reflection import Reflection


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Authenticated application user."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        UniqueConstraint(
            "auth_provider",
            "oauth_subject",
            name="uq_users_auth_provider_oauth_subject",
        ),
        Index("ix_users_role", "role"),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="user",
        server_default="user",
    )
    auth_provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="local",
        server_default="local",
    )
    oauth_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(16), nullable=True)

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    journals: Mapped[list["Journal"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reflections: Mapped[list["Reflection"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    prompt_logs: Mapped[list["PromptLog"]] = relationship(
        back_populates="user",
    )
