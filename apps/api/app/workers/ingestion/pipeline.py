"""
Knowledge-base ingestion pipeline orchestrator.

Parse → Validate → Normalize → Metadata → Embed → Postgres → Qdrant

Does not touch chat, retrieval APIs, or the legacy Verse table.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.application.ports.retrieval import EmbedderPort
from app.domain.repositories.corpus_manifest_repository import CorpusManifestRepository
from app.domain.repositories.knowledge_node_repository import KnowledgeNodeRepository
from app.domain.repositories.wisdom_graph_repository import WisdomGraphRepository
from app.application.ports.knowledge import KnowledgeVectorStore
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import IngestPipelineResult
from app.workers.ingestion.registry import default_classifiers, default_parser_registry
from app.workers.ingestion.stages import (
    EmbedStage,
    MetadataStage,
    NormalizeStage,
    PersistPostgresStage,
    PersistQdrantStage,
    ValidateStage,
)


class IngestionPipeline:
    """
    Scripture-agnostic orchestrator for KnowledgeNode ingestion.

    Inject repositories / embedder / vector store for real runs; defaults use
    in-memory stubs suitable for architecture dry-runs.
    """

    def __init__(
        self,
        *,
        nodes: KnowledgeNodeRepository,
        manifests: CorpusManifestRepository,
        graph: WisdomGraphRepository,
        embedder: EmbedderPort | None = None,
        vector_store: KnowledgeVectorStore | None = None,
        parser_registry=None,
        classifiers: dict[str, object] | None = None,
    ) -> None:
        self._parsers = parser_registry or default_parser_registry()
        clf = classifiers or default_classifiers()
        self._validate = ValidateStage()
        self._normalize = NormalizeStage()
        self._metadata = MetadataStage(
            topics=clf["topics"],  # type: ignore[arg-type]
            emotions=clf["emotions"],  # type: ignore[arg-type]
            keywords=clf["keywords"],  # type: ignore[arg-type]
            virtues=clf["virtues"],  # type: ignore[arg-type]
            life_domains=clf["life_domains"],  # type: ignore[arg-type]
            intents=clf["intents"],  # type: ignore[arg-type]
            related=clf["related"],  # type: ignore[arg-type]
            wisdom_graph=clf["wisdom_graph"],  # type: ignore[arg-type]
        )
        self._embed = EmbedStage(embedder)
        self._postgres = PersistPostgresStage(
            nodes=nodes,
            manifests=manifests,
            graph=graph,
        )
        self._qdrant = PersistQdrantStage(vector_store)

    async def run(
        self,
        context: IngestRunContext,
        source: str | bytes,
    ) -> IngestPipelineResult:
        """Execute the full stage chain for one scripture edition."""
        errors: list[str] = []
        parser = self._parsers.get(context.scripture)
        raw = await parser.parse(source)
        accepted, validation_errors = await self._validate.run(raw, context)
        errors.extend(validation_errors)

        normalized = await self._normalize.run(accepted, context)
        nodes, edges = await self._metadata.run(normalized, context)
        indexed = await self._embed.run(nodes, normalized, context)
        manifest = await self._postgres.run(nodes, edges, context)
        await self._qdrant.run(nodes, indexed, context)

        return IngestPipelineResult(
            run_id=context.run_id,
            scripture=context.scripture,
            edition=context.edition,
            parsed=len(raw),
            validated=len(accepted),
            rejected=len(validation_errors),
            indexed=sum(1 for item in indexed if item.vector is not None),
            edges_proposed=len(edges),
            manifest_id=manifest.id,
            checksum=manifest.checksum,
            finished_at=datetime.now(UTC),
            errors=errors,
        )
