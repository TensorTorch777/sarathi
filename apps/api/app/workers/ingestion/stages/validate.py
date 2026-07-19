"""Validate raw knowledge records against structural rules."""

from __future__ import annotations

from app.domain.enums.node_type import NodeType
from app.domain.enums.validation_status import ValidationStatus
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import RawKnowledgeRecord


class ValidateStage:
    """Ensure required fields exist for the node type before normalize."""

    async def run(
        self,
        records: list[RawKnowledgeRecord],
        context: IngestRunContext,
    ) -> tuple[list[RawKnowledgeRecord], list[str]]:
        """Return (accepted, error_messages)."""
        accepted: list[RawKnowledgeRecord] = []
        errors: list[str] = []
        for index, record in enumerate(records):
            problem = self._validate_one(record, context)
            if problem:
                errors.append(f"record[{index}]: {problem}")
                continue
            accepted.append(record)
        return accepted, errors

    def _validate_one(
        self,
        record: RawKnowledgeRecord,
        context: IngestRunContext,
    ) -> str | None:
        scripture = record.scripture or context.scripture
        if not scripture:
            return "missing scripture"

        if record.node_type == NodeType.VERSE:
            if record.chapter is None or record.verse_number is None:
                if "chapter" not in record.locator and "verse" not in record.locator:
                    return "VERSE requires chapter/verse or locator"
            if not record.translation and not record.sanskrit:
                return "VERSE requires translation or sanskrit"

        if record.node_type in {NodeType.CONCEPT, NodeType.CHARACTER, NodeType.EVENT}:
            if not record.title and not record.body and not record.translation:
                return f"{record.node_type} requires title, body, or translation"

        if record.node_type in {NodeType.SUMMARY, NodeType.COMMENTARY}:
            if not record.body and not record.commentary and not record.translation:
                return f"{record.node_type} requires body, commentary, or translation"

        _ = ValidationStatus.VALID  # documents lifecycle; assigned in normalize
        return None
