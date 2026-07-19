"""Generate split retrieval metadata via swappable classifiers."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.application.ports.knowledge import (
    EmotionClassifier,
    IntentClassifier,
    KeywordExtractor,
    LifeDomainClassifier,
    RelatedVerseResolver,
    TopicClassifier,
    VirtueClassifier,
    WisdomGraphBuilder,
)
from app.domain.entities.knowledge_metadata import (
    EditorialMetadata,
    IngestionMetadata,
    RetrievalMetadata,
)
from app.domain.entities.knowledge_node import KnowledgeNode
from app.domain.entities.provenance import Provenance
from app.domain.entities.wisdom_edge import WisdomEdge
from app.domain.enums.embedding_status import EmbeddingStatus
from app.domain.enums.validation_status import ValidationStatus
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import NormalizedKnowledgeRecord
from app.workers.ingestion.versioning import normalize_edition_slug


class MetadataStage:
    """
    Fan-out to classifiers; produce provisional KnowledgeNodes + graph edges.

    Classifiers are injectable — Null stubs now, lexicon/LLM later.
    """

    def __init__(
        self,
        *,
        topics: TopicClassifier,
        emotions: EmotionClassifier,
        keywords: KeywordExtractor,
        virtues: VirtueClassifier,
        life_domains: LifeDomainClassifier,
        intents: IntentClassifier,
        related: RelatedVerseResolver,
        wisdom_graph: WisdomGraphBuilder,
    ) -> None:
        self._topics = topics
        self._emotions = emotions
        self._keywords = keywords
        self._virtues = virtues
        self._life_domains = life_domains
        self._intents = intents
        self._related = related
        self._wisdom_graph = wisdom_graph

    async def run(
        self,
        records: list[NormalizedKnowledgeRecord],
        context: IngestRunContext,
    ) -> tuple[list[KnowledgeNode], list[WisdomEdge]]:
        """Attach retrieval metadata and propose wisdom-graph edges."""
        now = datetime.now(UTC)
        nodes: list[KnowledgeNode] = []
        all_edges: list[WisdomEdge] = []

        # First pass: provisional nodes so corpus_index can resolve relations
        for record in records:
            node_id = uuid4()
            context.corpus_index[record.citation_key] = node_id
            # Also index short Gita-style keys for related_citations like "BG 2.48"
            if record.chapter is not None and record.verse_number is not None:
                context.corpus_index[f"BG {record.chapter}.{record.verse_number}"] = node_id
                context.corpus_index[f"bg {record.chapter}.{record.verse_number}"] = node_id

            node = self._to_provisional_node(record, context, node_id, now)
            nodes.append(node)

        enriched: list[KnowledgeNode] = []
        for node in nodes:
            retrieval = RetrievalMetadata(
                topics=await self._topics.classify(node),
                emotions=await self._emotions.classify(node),
                virtues=await self._virtues.classify(node),
                keywords=await self._keywords.extract(node),
                life_domains=await self._life_domains.classify(node),
                user_intents=await self._intents.classify(node),
            )
            related_ids = await self._related.resolve(
                node,
                corpus_index=context.corpus_index,
            )
            # Resolve citation strings that were not yet node ids
            related_ids = list(related_ids)
            for citation in _related_citations_for(node, records):
                found = context.corpus_index.get(citation) or context.corpus_index.get(
                    citation.upper()
                )
                if found and found not in related_ids and found != node.id:
                    related_ids.append(found)

            node.retrieval_metadata = retrieval
            node.related_node_ids = related_ids
            node.editorial_metadata.metadata_confidence = (
                0.0 if not any(
                    [
                        retrieval.topics,
                        retrieval.emotions,
                        retrieval.user_intents,
                    ]
                )
                else 0.5
            )
            edges = await self._wisdom_graph.build_edges(
                node,
                corpus_index=context.corpus_index,
            )
            all_edges.extend(edges)
            enriched.append(node)

        return enriched, all_edges

    def _to_provisional_node(
        self,
        record: NormalizedKnowledgeRecord,
        context: IngestRunContext,
        node_id,
        now: datetime,
    ) -> KnowledgeNode:
        edition = normalize_edition_slug(context.edition)
        return KnowledgeNode(
            id=node_id,
            node_type=record.node_type,
            scripture=record.scripture,
            title=record.title,
            locator=record.locator,
            language=record.language,
            sanskrit=record.sanskrit,
            transliteration=record.transliteration,
            translation=record.translation,
            commentary=record.commentary,
            body=record.body,
            provenance=Provenance(
                source=context.source,
                edition=edition,
                publisher=context.publisher,
                translator=context.translator,
                license=context.license,
                checksum=record.content_checksum,
            ),
            ingestion_metadata=IngestionMetadata(
                parser_version=context.parser_version,
                source_path=record.source_path,
                content_checksum=record.content_checksum,
                batch_id=context.batch_id,
                imported_at=now,
                embedding_model=None,
                embedding_version=context.embedding_version,
            ),
            retrieval_metadata=RetrievalMetadata(
                topics=list(record.topics),
                emotions=list(record.emotions),
                virtues=list(record.virtues),
                keywords=list(record.keywords),
                life_domains=list(record.life_domains),
                user_intents=list(record.user_intents),
            ),
            editorial_metadata=EditorialMetadata(
                approved=False,
                quality_score=None,
                retrieval_confidence=None,
                metadata_confidence=None,
            ),
            embedding_version=context.embedding_version,
            qdrant_point_id=None,
            validation_status=ValidationStatus.VALID,
            embedding_status=EmbeddingStatus.PENDING,
            created_at=now,
            updated_at=now,
            chapter=record.chapter,
            verse_number=record.verse_number,
            related_node_ids=[],
        )


def _related_citations_for(
    node: KnowledgeNode,
    records: list[NormalizedKnowledgeRecord],
) -> list[str]:
    for record in records:
        if (
            record.chapter == node.chapter
            and record.verse_number == node.verse_number
            and record.scripture == node.scripture
        ):
            return list(record.related_citations)
    return []
