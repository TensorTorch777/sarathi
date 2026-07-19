"""Null / no-op classifier stubs (no LLM prompts in this phase)."""

from __future__ import annotations

from uuid import UUID, uuid4
from datetime import UTC, datetime

from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.entities.wisdom_edge import WisdomEdge
from app.domain.enums.wisdom_relation import WisdomRelation


def _seed_or_empty(seeded: list[str]) -> list[str]:
    return list(seeded)


class NullTopicClassifier:
    """Pass through pre-seeded topics only."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.topics)


class NullEmotionClassifier:
    """Pass through pre-seeded emotions only."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.emotions)


class NullKeywordExtractor:
    """Pass through pre-seeded keywords only."""

    async def extract(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.keywords)


class NullVirtueClassifier:
    """Pass through pre-seeded virtues only."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.virtues)


class NullLifeDomainClassifier:
    """Pass through pre-seeded life domains only."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.life_domains)


class NullIntentClassifier:
    """Pass through pre-seeded user intents only (no LLM)."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        return _seed_or_empty(node.retrieval_metadata.user_intents)


class NullRelatedVerseResolver:
    """Resolve related citations via corpus_index when present."""

    async def resolve(
        self,
        node: KnowledgeNode,
        *,
        corpus_index: dict[str, UUID],
    ) -> list[UUID]:
        return list(node.related_node_ids)


class NullWisdomGraphBuilder:
    """
    Architecture stub for Wisdom Graph edge proposal.

    Later implementations will emit concept / emotion / practice / related-verse
    edges. This stub returns RELATED_VERSE edges for already-resolved ids.
    """

    async def build_edges(
        self,
        node: KnowledgeNode,
        *,
        corpus_index: dict[str, UUID],
    ) -> list[WisdomEdge]:
        now = datetime.now(UTC)
        edges: list[WisdomEdge] = []
        for target_id in node.related_node_ids:
            edges.append(
                WisdomEdge(
                    id=uuid4(),
                    source_node_id=node.id,
                    target_node_id=target_id,
                    relation=WisdomRelation.RELATED_VERSE,
                    weight=1.0,
                    created_at=now,
                    updated_at=now,
                    confidence=None,
                    metadata={"builder": "null"},
                )
            )
        return edges
