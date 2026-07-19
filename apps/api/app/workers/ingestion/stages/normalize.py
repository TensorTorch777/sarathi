"""Normalize accepted raw records into deterministic pipeline records."""

from __future__ import annotations

import unicodedata

from app.domain.enums.validation_status import ValidationStatus
from app.workers.ingestion.context import IngestRunContext
from app.workers.ingestion.models import NormalizedKnowledgeRecord, RawKnowledgeRecord
from app.workers.ingestion.versioning import content_checksum, normalize_edition_slug


class NormalizeStage:
    """Unicode NFC, slug cleanup, locator + citation_key, content checksum."""

    async def run(
        self,
        records: list[RawKnowledgeRecord],
        context: IngestRunContext,
    ) -> list[NormalizedKnowledgeRecord]:
        """Normalize every accepted raw record."""
        edition = normalize_edition_slug(context.edition)
        normalized: list[NormalizedKnowledgeRecord] = []
        for record in records:
            scripture = (record.scripture or context.scripture).strip().lower()
            language = (record.language or context.language).strip().lower()
            chapter = record.chapter
            verse_number = record.verse_number
            locator = dict(record.locator)
            if chapter is not None:
                locator.setdefault("chapter", chapter)
            if verse_number is not None:
                locator.setdefault("verse", verse_number)

            citation_key = self._citation_key(scripture, edition, locator, record)
            checksum = content_checksum(
                scripture,
                edition,
                record.sanskrit,
                record.transliteration,
                record.translation,
                record.commentary,
                record.body,
                record.title,
            )
            normalized.append(
                NormalizedKnowledgeRecord(
                    node_type=record.node_type,
                    scripture=scripture,
                    title=self._clean_optional(record.title),
                    locator=locator,
                    citation_key=citation_key,
                    chapter=chapter,
                    verse_number=verse_number,
                    language=language,
                    sanskrit=self._clean_optional(record.sanskrit),
                    transliteration=self._clean_optional(record.transliteration),
                    translation=self._clean_optional(record.translation),
                    commentary=self._clean_optional(record.commentary),
                    body=self._clean_optional(record.body),
                    content_checksum=checksum,
                    topics=self._slug_list(record.topics),
                    emotions=self._slug_list(record.emotions),
                    virtues=self._slug_list(record.virtues),
                    keywords=self._slug_list(record.keywords),
                    life_domains=self._slug_list(record.life_domains),
                    user_intents=self._slug_list(record.user_intents),
                    related_citations=[c.strip() for c in record.related_citations if c.strip()],
                    source_path=record.source_path,
                    validation_status=ValidationStatus.VALID,
                )
            )
        return normalized

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None
        text = unicodedata.normalize("NFC", value.strip())
        return text or None

    @staticmethod
    def _slug_list(values: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for value in values:
            slug = value.strip().lower().replace(" ", "_")
            if not slug or slug in seen:
                continue
            seen.add(slug)
            out.append(slug)
        return out

    @staticmethod
    def _citation_key(
        scripture: str,
        edition: str,
        locator: dict,
        record: RawKnowledgeRecord,
    ) -> str:
        if record.chapter is not None and record.verse_number is not None:
            return f"{scripture}:{edition}:c{record.chapter}.v{record.verse_number}"
        loc = ".".join(f"{k}={locator[k]}" for k in sorted(locator))
        title = (record.title or "node").strip().lower().replace(" ", "_")
        return f"{scripture}:{edition}:{record.node_type}:{loc or title}"
