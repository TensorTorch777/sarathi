"""Persistence port for KnowledgeNode (Postgres — not wired to chat yet)."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.enums.node_type import NodeType


class KnowledgeNodeRepository(Protocol):
    """CRUD / upsert for knowledge-base nodes beside the legacy Verse table."""

    async def get_by_id(self, node_id: UUID) -> KnowledgeNode | None:
        """Load a single node."""
        ...

    async def upsert(self, node: KnowledgeNode) -> KnowledgeNode:
        """Insert or update by scripture+edition+locator identity."""
        ...

    async def upsert_many(self, nodes: list[KnowledgeNode]) -> list[KnowledgeNode]:
        """Batch upsert."""
        ...

    async def list_by_scripture(
        self,
        scripture: str,
        *,
        edition: str | None = None,
        node_type: NodeType | None = None,
    ) -> list[KnowledgeNode]:
        """List nodes for a scripture (optional edition / type filter)."""
        ...
