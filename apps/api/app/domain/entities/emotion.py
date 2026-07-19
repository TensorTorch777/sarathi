"""Emotion domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Emotion:
    """Reusable emotion label."""

    id: UUID
    slug: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
