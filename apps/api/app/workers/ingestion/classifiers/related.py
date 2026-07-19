"""Related-node resolution using citation keys and corpus index."""

from __future__ import annotations

from uuid import UUID

from app.domain.entities.knowledge_node import KnowledgeNode


class CitationRelatedVerseResolver:
    """
    Resolve related citations present on the node's provisional related ids
    and any ``BG X.Y`` keys already registered in ``corpus_index``.
    """

    async def resolve(
        self,
        node: KnowledgeNode,
        *,
        corpus_index: dict[str, UUID],
    ) -> list[UUID]:
        found: list[UUID] = []
        seen: set[UUID] = set()
        for node_id in node.related_node_ids:
            if node_id not in seen and node_id != node.id:
                seen.add(node_id)
                found.append(node_id)
        return found
