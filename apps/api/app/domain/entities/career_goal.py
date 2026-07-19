"""Career goal domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class CareerGoal:
    """A lasting career intention the assistant should remember."""

    id: UUID
    user_id: UUID
    title: str
    description: str
    status: str  # active | paused | achieved
    memory_item_id: UUID | None
    created_at: datetime
    updated_at: datetime
