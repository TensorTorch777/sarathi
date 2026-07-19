"""Build a validated corpus artifact ready for later ingestion."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.corpus.schema import CanonicalCorpusFile
from app.corpus.validator import CorpusValidationReport, CorpusValidator


@dataclass(slots=True)
class CorpusBuildResult:
    """Outcome of ``build_corpus``."""

    source_path: str
    output_path: str | None
    report: CorpusValidationReport
    checksum: str | None
    built_at: datetime | None


class CorpusBuilder:
    """
    Validate every node, then emit a normalized build artifact.

    Does not write Postgres or Qdrant — corpus product only.
    """

    def __init__(self, validator: CorpusValidator | None = None) -> None:
        self._validator = validator or CorpusValidator()

    def build(
        self,
        source: Path,
        output_dir: Path,
        *,
        strict_warnings: bool = False,
    ) -> CorpusBuildResult:
        """Validate ``source`` and write normalized JSON + checksum sidecar."""
        report = self._validator.validate_path(source)
        if not report.ok:
            return CorpusBuildResult(
                source_path=str(source),
                output_path=None,
                report=report,
                checksum=None,
                built_at=None,
            )
        if strict_warnings and report.warnings:
            report.ok = False
            return CorpusBuildResult(
                source_path=str(source),
                output_path=None,
                report=report,
                checksum=None,
                built_at=None,
            )

        payload = json.loads(source.read_text(encoding="utf-8"))
        corpus = CanonicalCorpusFile.model_validate(payload)
        normalized = corpus.model_dump(mode="json")
        built_at = datetime.now(UTC)
        normalized["build"] = {
            "built_at": built_at.isoformat(),
            "source": source.name,
            "node_count": len(corpus.nodes),
            "validator": "CorpusValidator",
        }

        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{source.stem}.build.json"
        text = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
        out_path.write_text(text, encoding="utf-8")

        checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
        (output_dir / f"{source.stem}.build.sha256").write_text(
            f"{checksum}  {out_path.name}\n",
            encoding="utf-8",
        )

        return CorpusBuildResult(
            source_path=str(source),
            output_path=str(out_path),
            report=report,
            checksum=checksum,
            built_at=built_at,
        )
