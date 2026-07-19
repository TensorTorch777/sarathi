"""Directed edge in the Wisdom Graph between KnowledgeNodes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums.wisdom_relation import WisdomRelation


@dataclass(slots=True)
class WisdomEdge:
    """
    Link between two knowledge nodes (ideas, not just similar text).

    Example: BG 2.47 --defines_concept--> Nishkama Karma
             BG 2.47 --related_verse--> BG 2.48
    """

    id: UUID
    source_node_id: UUID
    target_node_id: UUID
    relation: WisdomRelation
    weight: float
    created_at: datetime
    updated_at: datetime
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
