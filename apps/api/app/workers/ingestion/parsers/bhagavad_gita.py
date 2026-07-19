"""Bhagavad Gita parser adapter (architecture stub — no full corpus yet)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.domain.enums.node_type import NodeType
from app.workers.ingestion.errors import IngestStageError
from app.workers.ingestion.models import RawKnowledgeRecord


class BhagavadGitaParser:
    """
    Parse Gita JSON seed / export format into VERSE knowledge records.

    Expected object shape (per verse)::

        {
          "chapter": 2,
          "verse_number": 47,
          "sanskrit": "...",
          "transliteration": "...",
          "translation": "...",
          "commentary": null,
          "topics": [],
          "emotions": []
        }
    """

    scripture = "bhagavad_gita"

    async def parse(self, source: str | bytes) -> list[RawKnowledgeRecord]:
        """Load JSON list or ``{\"verses\": [...]}`` from path or bytes."""
        payload = self._load_payload(source)
        rows = payload.get("verses", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise IngestStageError("parse", "Gita source must be a list or {verses: []}")

        records: list[RawKnowledgeRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            chapter = row.get("chapter")
            verse_number = row.get("verse_number") or row.get("verse")
            records.append(
                RawKnowledgeRecord(
                    node_type=NodeType.VERSE,
                    scripture=self.scripture,
                    locator={"chapter": chapter, "verse": verse_number},
                    chapter=int(chapter) if chapter is not None else None,
                    verse_number=int(verse_number) if verse_number is not None else None,
                    language=row.get("language") or "en",
                    sanskrit=row.get("sanskrit"),
                    transliteration=row.get("transliteration"),
                    translation=row.get("translation"),
                    commentary=row.get("commentary"),
                    topics=list(row.get("topics") or []),
                    emotions=list(row.get("emotions") or []),
                    virtues=list(row.get("virtues") or []),
                    keywords=list(row.get("keywords") or []),
                    life_domains=list(row.get("life_domains") or []),
                    user_intents=list(row.get("user_intents") or []),
                    related_citations=list(row.get("related_verses") or row.get("related_citations") or []),
                    source_path=str(source) if isinstance(source, str) else None,
                    extra={k: v for k, v in row.items() if k.startswith("meta_")},
                )
            )
        return records

    @staticmethod
    def _load_payload(source: str | bytes) -> Any:
        if isinstance(source, bytes):
            return json.loads(source.decode("utf-8"))
        path = Path(source)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return json.loads(source)
