"""Persistence port for Wisdom Graph edges."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.wisdom_edge import WisdomEdge
from app.domain.enums.wisdom_relation import WisdomRelation


class WisdomGraphRepository(Protocol):
    """Store and query directed links between KnowledgeNodes."""

    async def upsert_edge(self, edge: WisdomEdge) -> WisdomEdge:
        """Insert or update an edge (source, target, relation)."""
        ...

    async def upsert_edges(self, edges: list[WisdomEdge]) -> list[WisdomEdge]:
        """Batch upsert."""
        ...

    async def neighbors(
        self,
        node_id: UUID,
        *,
        relations: list[WisdomRelation] | None = None,
        direction: str = "outgoing",
    ) -> list[WisdomEdge]:
        """Adjacent edges for graph navigation (later retrieval layer)."""
        ...
