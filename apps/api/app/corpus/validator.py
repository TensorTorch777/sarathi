"""Validate a Sarathi Canonical Corpus file for structural integrity."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.corpus.schema import CanonicalCorpusFile, CanonicalKnowledgeNode
from app.corpus.taxonomies import (
    ALLOWED_EMOTIONS,
    ALLOWED_LIFE_DOMAINS,
    ALLOWED_SCRIPURES,
    ALLOWED_TOPICS,
    ALLOWED_USER_INTENTS,
    ALLOWED_VIRTUES,
    GITA_VERSE_COUNTS,
)


@dataclass(slots=True)
class CorpusIssue:
    """One validation finding."""

    level: str  # error | warning
    code: str
    message: str
    node_id: str | None = None


@dataclass(slots=True)
class CorpusValidationReport:
    """Aggregate result of validating one corpus file."""

    path: str
    ok: bool
    node_count: int = 0
    errors: list[CorpusIssue] = field(default_factory=list)
    warnings: list[CorpusIssue] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.errors) + len(self.warnings)


class CorpusValidator:
    """
    Detect corpus defects before any database or vector work.

    Checks: schema, duplicates, Gita chapter/verse bounds, required text,
    taxonomy membership, broken related_nodes references.
    """

    def validate_path(self, path: Path) -> CorpusValidationReport:
        """Load JSON from disk and validate."""
        report = CorpusValidationReport(path=str(path), ok=False)
        if not path.exists():
            report.errors.append(
                CorpusIssue("error", "file_missing", f"Corpus file not found: {path}")
            )
            return report
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.errors.append(
                CorpusIssue("error", "invalid_json", f"Invalid JSON: {exc}")
            )
            return report
        return self.validate_payload(payload, path=str(path))

    def validate_payload(
        self,
        payload: Any,
        *,
        path: str = "<memory>",
    ) -> CorpusValidationReport:
        """Validate an already-loaded corpus document."""
        report = CorpusValidationReport(path=path, ok=False)

        try:
            corpus = CanonicalCorpusFile.model_validate(payload)
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(part) for part in err.get("loc", ()))
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "schema",
                        f"{loc}: {err.get('msg')}",
                    )
                )
            return report

        report.node_count = len(corpus.nodes)
        self._check_manifest(corpus, report)
        self._check_nodes(corpus.nodes, report)
        report.ok = len(report.errors) == 0
        return report

    def _check_manifest(
        self,
        corpus: CanonicalCorpusFile,
        report: CorpusValidationReport,
    ) -> None:
        scripture = corpus.manifest.scripture.strip().lower()
        if scripture not in ALLOWED_SCRIPURES:
            report.errors.append(
                CorpusIssue(
                    "error",
                    "scripture",
                    f"Unsupported scripture {scripture!r}",
                )
            )
        for node in corpus.nodes:
            if node.scripture != scripture:
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "scripture_mismatch",
                        f"node scripture {node.scripture!r} != manifest {scripture!r}",
                        node_id=node.id,
                    )
                )

    def _check_nodes(
        self,
        nodes: list[CanonicalKnowledgeNode],
        report: CorpusValidationReport,
    ) -> None:
        seen_ids: set[str] = set()
        seen_citations: set[str] = set()
        id_set = {n.id for n in nodes}

        for node in nodes:
            if node.id in seen_ids:
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "duplicate_id",
                        f"Duplicate id {node.id!r}",
                        node_id=node.id,
                    )
                )
            seen_ids.add(node.id)

            if node.citation in seen_citations:
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "duplicate_citation",
                        f"Duplicate citation {node.citation!r}",
                        node_id=node.id,
                    )
                )
            seen_citations.add(node.citation)

            self._check_gita_bounds(node, report)
            self._check_required_text(node, report)
            self._check_metadata_taxonomies(node, report)
            self._check_related(node, id_set, report)

            if node.corpus_layer == "enriched" and not node.practice:
                report.warnings.append(
                    CorpusIssue(
                        "warning",
                        "empty_practice",
                        "practice list is empty",
                        node_id=node.id,
                    )
                )

    def _check_gita_bounds(
        self,
        node: CanonicalKnowledgeNode,
        report: CorpusValidationReport,
    ) -> None:
        if node.scripture != "bhagavad_gita":
            return
        chapter = node.locator.chapter
        verse = node.locator.verse
        if chapter not in GITA_VERSE_COUNTS:
            report.errors.append(
                CorpusIssue(
                    "error",
                    "invalid_chapter",
                    f"Chapter {chapter} is outside 1–18",
                    node_id=node.id,
                )
            )
            return
        max_verse = GITA_VERSE_COUNTS[chapter]
        if verse < 1 or verse > max_verse:
            report.errors.append(
                CorpusIssue(
                    "error",
                    "invalid_verse",
                    f"Verse {verse} invalid for chapter {chapter} (max {max_verse})",
                    node_id=node.id,
                )
            )

    def _check_required_text(
        self,
        node: CanonicalKnowledgeNode,
        report: CorpusValidationReport,
    ) -> None:
        if not node.sanskrit.strip():
            report.errors.append(
                CorpusIssue("error", "missing_sanskrit", "Missing Sanskrit", node.id)
            )
        if node.corpus_layer == "authentic":
            if not node.transliteration:
                report.warnings.append(
                    CorpusIssue(
                        "warning",
                        "missing_transliteration",
                        "Transliteration not present in source extract",
                        node.id,
                    )
                )
            return
        if not node.default_translation.strip():
            report.errors.append(
                CorpusIssue(
                    "error",
                    "missing_translation",
                    "Missing translation text",
                    node.id,
                )
            )
        if not (node.summary and node.summary.strip()):
            report.errors.append(
                CorpusIssue("error", "missing_summary", "Missing summary", node.id)
            )

    def _check_metadata_taxonomies(
        self,
        node: CanonicalKnowledgeNode,
        report: CorpusValidationReport,
    ) -> None:
        checks = (
            ("topics", node.topics, ALLOWED_TOPICS),
            ("emotions", node.emotions, ALLOWED_EMOTIONS),
            ("life_domains", node.life_domains, ALLOWED_LIFE_DOMAINS),
            ("user_intents", node.user_intents, ALLOWED_USER_INTENTS),
            ("virtues", node.virtues, ALLOWED_VIRTUES),
        )
        for field_name, values, allowed in checks:
            for value in values:
                slug = value.strip().lower().replace(" ", "_")
                if slug not in allowed:
                    report.errors.append(
                        CorpusIssue(
                            "error",
                            "invalid_metadata",
                            f"{field_name} contains unknown slug {value!r}",
                            node_id=node.id,
                        )
                    )
            # Detect duplicates within a field
            if len(values) != len(set(v.lower() for v in values)):
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "duplicate_metadata",
                        f"{field_name} contains duplicates",
                        node_id=node.id,
                    )
                )

        if node.corpus_layer != "enriched":
            return
        for field_name, values, _ in checks:
            if not values and node.node_type == "VERSE":
                report.warnings.append(
                    CorpusIssue(
                        "warning",
                        "empty_metadata",
                        f"{field_name} is empty (curation incomplete)",
                        node_id=node.id,
                    )
                )

    def _check_related(
        self,
        node: CanonicalKnowledgeNode,
        id_set: set[str],
        report: CorpusValidationReport,
    ) -> None:
        for related in node.related_nodes:
            if related == node.id:
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "self_related",
                        "related_nodes must not include self",
                        node_id=node.id,
                    )
                )
            elif related not in id_set:
                # Allow forward references to nodes not yet in this file (full corpus)
                # only as warnings when they look like valid ids — still error for sample
                # completeness: broken refs are errors so build fails closed.
                report.errors.append(
                    CorpusIssue(
                        "error",
                        "broken_related_node",
                        f"related_nodes references missing id {related!r}",
                        node_id=node.id,
                    )
                )
