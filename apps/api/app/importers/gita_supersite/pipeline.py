"""Orchestrate download → parse → normalize → validate for Gita Supersite."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.corpus.taxonomies import GITA_VERSE_COUNTS
from app.importers.gita_supersite.downloader import GitaSupersiteDownloader
from app.importers.gita_supersite.license import assert_copyrighted_allowed
from app.importers.gita_supersite.normalizer import GitaSupersiteNormalizer
from app.importers.gita_supersite.parser import GitaSupersiteParser, RawVerseExtract
from app.importers.gita_supersite.validator import ExtractionReport, GitaSupersiteExtractValidator


@dataclass(slots=True)
class ImportResult:
    """Outcome of a supersite import run."""

    output_path: Path
    report_path: Path
    report: ExtractionReport
    verse_count: int


class GitaSupersiteImportPipeline:
    """
    One-time offline importer.

    Idempotent via HTML cache. Does not touch chat, retrieval, or frontend.
    """

    def __init__(
        self,
        *,
        cache_dir: Path,
        downloader: GitaSupersiteDownloader | None = None,
        parser: GitaSupersiteParser | None = None,
        normalizer: GitaSupersiteNormalizer | None = None,
        extract_validator: GitaSupersiteExtractValidator | None = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.downloader = downloader or GitaSupersiteDownloader(cache_dir)
        self.parser = parser or GitaSupersiteParser()
        self.normalizer = normalizer or GitaSupersiteNormalizer()
        self.extract_validator = extract_validator or GitaSupersiteExtractValidator()

    async def run(
        self,
        output_path: Path,
        *,
        include_copyrighted_text: bool = False,
        acknowledge_license: str | None = None,
        sanskrit_only: bool = True,
        chapters: list[int] | None = None,
        targets: list[tuple[int, int]] | None = None,
        force_download: bool = False,
        local_html_dir: Path | None = None,
    ) -> ImportResult:
        """
        Import verses into a Layer-1 corpus JSON + extraction report.

        ``local_html_dir`` (optional) reads ``chapter_XX/verse_YY.html`` without
        network — used for fixtures / air-gapped rebuilds.
        ``targets`` selects exact (chapter, verse) pairs for smoke tests.
        """
        assert_copyrighted_allowed(
            include_copyrighted=include_copyrighted_text and not sanskrit_only,
            acknowledge=acknowledge_license,
        )

        if targets is not None:
            verse_targets = list(targets)
            chapter_list = sorted({c for c, _ in verse_targets})
        else:
            chapter_list = chapters or list(GITA_VERSE_COUNTS.keys())
            verse_targets = [
                (chapter, verse)
                for chapter in chapter_list
                for verse in range(1, GITA_VERSE_COUNTS[chapter] + 1)
            ]

        extracts: list[RawVerseExtract] = []

        for chapter, verse in verse_targets:
            html, source_url = await self._load_html(
                chapter,
                verse,
                force_download=force_download,
                local_html_dir=local_html_dir,
            )
            extracts.append(
                self.parser.parse(
                    html,
                    chapter=chapter,
                    verse=verse,
                    source_url=source_url,
                )
            )

        nodes = [
            self.normalizer.normalize(
                extract,
                include_copyrighted_text=include_copyrighted_text,
                sanskrit_only=sanskrit_only,
            )
            for extract in extracts
        ]
        document = self.normalizer.build_corpus_document(
            nodes,
            include_copyrighted_text=include_copyrighted_text,
            sanskrit_only=sanskrit_only,
        )

        if targets is not None:
            # Smoke / fixture runs: validate schema only, skip full-chapter slot check
            from app.corpus.validator import CorpusValidator

            schema_report = CorpusValidator().validate_payload(document)
            report = ExtractionReport(
                total_verses=len(nodes),
                expected_verses=len(nodes),
                validation=schema_report,
            )
            for node in nodes:
                if not (node.get("sanskrit") or "").strip():
                    report.missing_sanskrit.append(node["id"])
                for warning in (node.get("source_metadata") or {}).get("parser_warnings") or []:
                    report.parser_warnings.append(f"{node['id']}: {warning}")
        else:
            report = self.extract_validator.validate(document, chapters=chapter_list)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report_path = output_path.with_suffix(".extraction_report.txt")
        report_path.write_text(
            self.extract_validator.format_report(report) + "\n",
            encoding="utf-8",
        )
        return ImportResult(
            output_path=output_path,
            report_path=report_path,
            report=report,
            verse_count=len(nodes),
        )

    async def _load_html(
        self,
        chapter: int,
        verse: int,
        *,
        force_download: bool,
        local_html_dir: Path | None,
    ) -> tuple[str, str | None]:
        if local_html_dir is not None:
            path = (
                local_html_dir
                / f"chapter_{chapter:02d}"
                / f"verse_{verse:02d}.html"
            )
            if not path.exists():
                # Also allow flat fixture: bg_2_47.html
                flat = local_html_dir / f"bg_{chapter}_{verse}.html"
                if flat.exists():
                    return flat.read_text(encoding="utf-8"), str(flat)
                raise FileNotFoundError(f"Missing local HTML for {chapter}.{verse}: {path}")
            return path.read_text(encoding="utf-8"), str(path)

        path = await self.downloader.fetch_verse(
            chapter,
            verse,
            force=force_download,
        )
        return path.read_text(encoding="utf-8"), self.downloader.verse_url(chapter, verse)
