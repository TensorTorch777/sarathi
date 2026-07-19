"""add long-term memory tables

Revision ID: a1b2c3d4e5f6
Revises: 8c6e0d6c9f3c
Create Date: 2026-07-19 14:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "8c6e0d6c9f3c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "memory_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("qdrant_point_id", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_items_user_id", "memory_items", ["user_id"])
    op.create_index(
        "ix_memory_items_user_kind_created",
        "memory_items",
        ["user_id", "kind", "created_at"],
    )
    op.create_index(
        "ix_memory_items_user_source",
        "memory_items",
        ["user_id", "kind", "source_id"],
    )

    op.create_table(
        "career_goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("memory_item_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["memory_item_id"], ["memory_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_career_goals_user_id", "career_goals", ["user_id"])
    op.create_index("ix_career_goals_user_status", "career_goals", ["user_id", "status"])

    op.create_table(
        "favorite_verses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("verse_id", sa.Uuid(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("memory_item_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["memory_item_id"], ["memory_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verse_id"], ["verses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "verse_id", name="uq_favorite_verses_user_verse"),
    )
    op.create_index("ix_favorite_verses_user_id", "favorite_verses", ["user_id"])
    op.create_index(
        "ix_favorite_verses_user_created",
        "favorite_verses",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_favorite_verses_user_created", table_name="favorite_verses")
    op.drop_index("ix_favorite_verses_user_id", table_name="favorite_verses")
    op.drop_table("favorite_verses")
    op.drop_index("ix_career_goals_user_status", table_name="career_goals")
    op.drop_index("ix_career_goals_user_id", table_name="career_goals")
    op.drop_table("career_goals")
    op.drop_index("ix_memory_items_user_source", table_name="memory_items")
    op.drop_index("ix_memory_items_user_kind_created", table_name="memory_items")
    op.drop_index("ix_memory_items_user_id", table_name="memory_items")
    op.drop_table("memory_items")
