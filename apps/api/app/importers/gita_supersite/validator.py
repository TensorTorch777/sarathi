"""Validate a full Bhagavad Gita Layer-1 extract (expect 700 verses)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.corpus.schema import CanonicalCorpusFile
from app.corpus.taxonomies import GITA_VERSE_COUNTS
from app.corpus.validator import CorpusIssue, CorpusValidationReport, CorpusValidator
from app.importers.gita_supersite.constants import EXPECTED_VERSE_TOTAL


@dataclass(slots=True)
class ExtractionReport:
    """Human-readable extraction / coverage report."""

    total_verses: int
    expected_verses: int = EXPECTED_VERSE_TOTAL
    missing_sanskrit: list[str] = field(default_factory=list)
    missing_translations: list[str] = field(default_factory=list)
    missing_transliterations: list[str] = field(default_factory=list)
    missing_commentaries: list[str] = field(default_factory=list)
    parser_warnings: list[str] = field(default_factory=list)
    missing_locator_slots: list[str] = field(default_factory=list)
    validation: CorpusValidationReport | None = None

    @property
    def ok(self) -> bool:
        structural_ok = (
            self.total_verses == self.expected_verses
            and not self.missing_sanskrit
            and not self.missing_locator_slots
        )
        schema_ok = self.validation.ok if self.validation else False
        return structural_ok and schema_ok


class GitaSupersiteExtractValidator:
    """Ensure completeness of a 700-verse Layer-1 corpus."""

    def __init__(self, corpus_validator: CorpusValidator | None = None) -> None:
        self._corpus_validator = corpus_validator or CorpusValidator()

    def validate(
        self,
        document: dict[str, Any],
        *,
        chapters: list[int] | None = None,
    ) -> ExtractionReport:
        """Validate schema + expected verse coverage (700 when chapters is None)."""
        chapter_set = set(chapters) if chapters is not None else set(GITA_VERSE_COUNTS)
        expected = sum(GITA_VERSE_COUNTS[c] for c in sorted(chapter_set))
        report = ExtractionReport(
            total_verses=len(document.get("nodes") or []),
            expected_verses=expected,
        )
        validation = self._corpus_validator.validate_payload(document)
        report.validation = validation

        nodes = document.get("nodes") or []
        present: set[tuple[int, int]] = set()
        for node in nodes:
            locator = node.get("locator") or {}
            chapter = int(locator.get("chapter", 0))
            verse = int(locator.get("verse", 0))
            present.add((chapter, verse))
            node_id = node.get("id", f"bg_{chapter}_{verse}")

            if not (node.get("sanskrit") or "").strip():
                report.missing_sanskrit.append(node_id)
            if not node.get("transliteration"):
                report.missing_transliterations.append(node_id)
            if not node.get("translations"):
                report.missing_translations.append(node_id)
            if not node.get("commentaries") and not node.get("commentary"):
                report.missing_commentaries.append(node_id)

            for warning in (node.get("source_metadata") or {}).get("parser_warnings") or []:
                report.parser_warnings.append(f"{node_id}: {warning}")

        for chapter in sorted(chapter_set):
            count = GITA_VERSE_COUNTS[chapter]
            for verse in range(1, count + 1):
                if (chapter, verse) not in present:
                    report.missing_locator_slots.append(f"bg_{chapter}_{verse}")

        if report.total_verses != expected:
            validation.errors.append(
                CorpusIssue(
                    "error",
                    "verse_count",
                    f"Expected {expected} verses, found {report.total_verses}",
                )
            )
            validation.ok = False

        try:
            CanonicalCorpusFile.model_validate(document)
        except Exception as exc:  # noqa: BLE001 — surface in report
            validation.errors.append(
                CorpusIssue("error", "schema_recheck", str(exc))
            )
            validation.ok = False

        return report

    def format_report(self, report: ExtractionReport) -> str:
        """Render a concise CLI report."""
        lines = [
            f"total_verses: {report.total_verses} (expected {report.expected_verses})",
            f"missing_locator_slots: {len(report.missing_locator_slots)}",
            f"missing_sanskrit: {len(report.missing_sanskrit)}",
            f"missing_transliterations: {len(report.missing_transliterations)}",
            f"missing_translations: {len(report.missing_translations)}",
            f"missing_commentaries: {len(report.missing_commentaries)}",
            f"parser_warnings: {len(report.parser_warnings)}",
        ]
        if report.validation:
            lines.append(f"schema_errors: {len(report.validation.errors)}")
            lines.append(f"schema_warnings: {len(report.validation.warnings)}")
            for issue in report.validation.errors[:20]:
                lines.append(f"  ERROR {issue.code}: {issue.message}")
        for slot in report.missing_locator_slots[:10]:
            lines.append(f"  missing slot: {slot}")
        for warning in report.parser_warnings[:15]:
            lines.append(f"  warn: {warning}")
        lines.append(f"status: {'OK' if report.ok else 'FAIL'}")
        return "\n".join(lines)
