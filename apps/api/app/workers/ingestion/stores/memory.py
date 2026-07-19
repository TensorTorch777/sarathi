"""In-memory repositories for architecture scaffolding / dry runs."""

from __future__ import annotations

from uuid import UUID

from app.domain.entities.corpus_manifest import CorpusManifest
from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.entities.wisdom_edge import WisdomEdge
from app.domain.enums.node_type import NodeType
from app.domain.enums.wisdom_relation import WisdomRelation


class InMemoryKnowledgeNodeRepository:
    """Ephemeral node store (not production Postgres)."""

    def __init__(self) -> None:
        self._nodes: dict[UUID, KnowledgeNode] = {}

    async def get_by_id(self, node_id: UUID) -> KnowledgeNode | None:
        return self._nodes.get(node_id)

    async def upsert(self, node: KnowledgeNode) -> KnowledgeNode:
        self._nodes[node.id] = node
        return node

    async def upsert_many(self, nodes: list[KnowledgeNode]) -> list[KnowledgeNode]:
        for node in nodes:
            self._nodes[node.id] = node
        return nodes

    async def list_by_scripture(
        self,
        scripture: str,
        *,
        edition: str | None = None,
        node_type: NodeType | None = None,
    ) -> list[KnowledgeNode]:
        out: list[KnowledgeNode] = []
        for node in self._nodes.values():
            if node.scripture != scripture:
                continue
            if edition and node.provenance.edition != edition:
                continue
            if node_type and node.node_type != node_type:
                continue
            out.append(node)
        return out


class InMemoryCorpusManifestRepository:
    """Ephemeral manifest store."""

    def __init__(self) -> None:
        self._items: dict[UUID, CorpusManifest] = {}

    async def create(self, manifest: CorpusManifest) -> CorpusManifest:
        self._items[manifest.id] = manifest
        return manifest

    async def get_by_id(self, manifest_id: UUID) -> CorpusManifest | None:
        return self._items.get(manifest_id)

    async def get_latest(self, scripture: str, edition: str) -> CorpusManifest | None:
        matches = [
            m
            for m in self._items.values()
            if m.scripture == scripture and m.edition == edition
        ]
        if not matches:
            return None
        return max(matches, key=lambda m: m.imported_at)


class InMemoryWisdomGraphRepository:
    """Ephemeral wisdom-graph edge store."""

    def __init__(self) -> None:
        self._edges: dict[UUID, WisdomEdge] = {}

    async def upsert_edge(self, edge: WisdomEdge) -> WisdomEdge:
        self._edges[edge.id] = edge
        return edge

    async def upsert_edges(self, edges: list[WisdomEdge]) -> list[WisdomEdge]:
        for edge in edges:
            self._edges[edge.id] = edge
        return edges

    async def neighbors(
        self,
        node_id: UUID,
        *,
        relations: list[WisdomRelation] | None = None,
        direction: str = "outgoing",
    ) -> list[WisdomEdge]:
        results: list[WisdomEdge] = []
        for edge in self._edges.values():
            if direction == "outgoing" and edge.source_node_id != node_id:
                continue
            if direction == "incoming" and edge.target_node_id != node_id:
                continue
            if direction == "both" and node_id not in {
                edge.source_node_id,
                edge.target_node_id,
            }:
                continue
            if relations and edge.relation not in relations:
                continue
            results.append(edge)
        return results


class NullKnowledgeVectorStore:
    """No-op Qdrant adapter for scaffolding without a live cluster write."""

    async def ensure_collection(self) -> None:
        return None

    async def upsert_node(self, node, vector: list[float]) -> str:
        from app.workers.ingestion.versioning import qdrant_point_id

        version = node.embedding_version or "unknown"
        return qdrant_point_id(str(node.id), version)
