"""Ports for knowledge-base metadata generation and vector indexing."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.entities.wisdom_edge import WisdomEdge


class TopicClassifier(Protocol):
    """Assign topic slugs to a knowledge node."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        """Return normalized topic slugs."""
        ...


class EmotionClassifier(Protocol):
    """Assign emotion slugs relevant to a knowledge node."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        """Return normalized emotion slugs."""
        ...


class KeywordExtractor(Protocol):
    """Extract searchable keywords from a knowledge node."""

    async def extract(self, node: KnowledgeNode) -> list[str]:
        """Return keyword tokens / phrases."""
        ...


class VirtueClassifier(Protocol):
    """Assign virtue / guna-aligned slugs."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        """Return virtue slugs."""
        ...


class LifeDomainClassifier(Protocol):
    """Assign life-domain slugs (career, family, grief, …)."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        """Return life-domain slugs."""
        ...


class IntentClassifier(Protocol):
    """Assign user-intent slugs (seeking encouragement, guidance, …)."""

    async def classify(self, node: KnowledgeNode) -> list[str]:
        """Return user_intent slugs from the canonical taxonomy."""
        ...


class RelatedVerseResolver(Protocol):
    """Resolve related verse / node references for a knowledge node."""

    async def resolve(
        self,
        node: KnowledgeNode,
        *,
        corpus_index: dict[str, UUID],
    ) -> list[UUID]:
        """Return related KnowledgeNode ids (often other VERSE nodes)."""
        ...


class WisdomGraphBuilder(Protocol):
    """Propose Wisdom Graph edges from a node and optional corpus index."""

    async def build_edges(
        self,
        node: KnowledgeNode,
        *,
        corpus_index: dict[str, UUID],
    ) -> list[WisdomEdge]:
        """Return candidate edges (not yet persisted)."""
        ...


class KnowledgeVectorStore(Protocol):
    """
    Qdrant indexing for KnowledgeNodes.

    One collection with payload filters (scripture, node_type, edition,
    embedding_version). Never overwrite a different embedding_version.
    """

    async def ensure_collection(self) -> None:
        """Create collection if missing (cosine, configured dimensions)."""
        ...

    async def upsert_node(
        self,
        node: KnowledgeNode,
        vector: list[float],
    ) -> str:
        """Upsert point id = ``{node_id}:{embedding_version}``; return point id."""
        ...
