"""Persist KnowledgeNodes, WisdomEdges, and CorpusManifest (scaffolding)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.corpus_manifest import CorpusManifest
from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.entities.wisdom_edge import WisdomEdge
from app.domain.repositories.corpus_manifest_repository import CorpusManifestRepository
from app.domain.repositories.knowledge_node_repository import KnowledgeNodeRepository
from app.domain.repositories.wisdom_graph_repository import WisdomGraphRepository
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.versioning import content_checksum


class PersistPostgresStage:
    """
    Write structured KB entities beside the legacy ``verses`` table.

    Repositories are injected; use ``InMemory*`` stubs until Alembic models land.
    """

    def __init__(
        self,
        *,
        nodes: KnowledgeNodeRepository,
        manifests: CorpusManifestRepository,
        graph: WisdomGraphRepository,
    ) -> None:
        self._nodes = nodes
        self._manifests = manifests
        self._graph = graph

    async def run(
        self,
        nodes: list[KnowledgeNode],
        edges: list[WisdomEdge],
        context: IngestRunContext,
    ) -> CorpusManifest:
        """Upsert nodes + edges and create a CorpusManifest."""
        if not context.dry_run:
            await self._nodes.upsert_many(nodes)
            if edges:
                await self._graph.upsert_edges(edges)

        counts: dict[str, int] = {}
        for node in nodes:
            key = str(node.node_type)
            counts[key] = counts.get(key, 0) + 1

        checksum = content_checksum(
            *(n.provenance.checksum or "" for n in nodes),
            context.scripture,
            context.edition,
            context.embedding_version,
        )
        now = datetime.now(UTC)
        manifest = CorpusManifest(
            id=uuid4(),
            scripture=context.scripture,
            edition=context.edition,
            version=context.edition_version,
            language=context.language,
            parser_version=context.parser_version,
            embedding_version=context.embedding_version,
            total_nodes=len(nodes),
            checksum=checksum,
            imported_at=now,
            created_at=now,
            updated_at=now,
            publisher=context.publisher,
            translator=context.translator,
            license=context.license,
            source=context.source,
            node_type_counts=counts,
        )
        if not context.dry_run:
            await self._manifests.create(manifest)
        return manifest
