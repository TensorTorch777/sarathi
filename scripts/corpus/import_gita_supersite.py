#!/usr/bin/env python3
"""CLI: import Bhagavad Gita from Gita Supersite into Layer-1 corpus JSON."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.importers.gita_supersite.license import ACK_PHRASE, LICENSE_NOTICE  # noqa: E402
from app.importers.gita_supersite.pipeline import GitaSupersiteImportPipeline  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import Gita Supersite → Sarathi Layer-1 corpus (offline)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT
        / "data"
        / "corpus"
        / "bhagavad_gita"
        / "sources"
        / "gita_supersite"
        / "bhagavad_gita.layer1.json",
        help="Output Layer-1 JSON path (default under sources/, gitignored)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=ROOT
        / "data"
        / "corpus"
        / "bhagavad_gita"
        / "sources"
        / "gita_supersite"
        / "raw",
        help="HTML cache directory",
    )
    parser.add_argument(
        "--local-html-dir",
        type=Path,
        default=None,
        help="Read cached/fixture HTML only (no network)",
    )
    parser.add_argument(
        "--chapters",
        type=str,
        default=None,
        help="Comma-separated chapters (default: all 1–18)",
    )
    parser.add_argument(
        "--sanskrit-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Extract Sanskrit structure only (default: true; safest redistributable mode)",
    )
    parser.add_argument(
        "--include-copyrighted-text",
        action="store_true",
        help="Also extract translations/commentaries (requires --acknowledge-license)",
    )
    parser.add_argument(
        "--acknowledge-license",
        type=str,
        default=None,
        help=f"Must equal {ACK_PHRASE} when including copyrighted text",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Re-download even when cache exists",
    )
    parser.add_argument(
        "--print-license",
        action="store_true",
        help="Print licensing notice and exit",
    )
    args = parser.parse_args(argv)

    if args.print_license:
        print(LICENSE_NOTICE)
        return 0

    chapters = None
    if args.chapters:
        chapters = [int(part.strip()) for part in args.chapters.split(",") if part.strip()]

    # If copyrighted requested, turn off sanskrit-only unless user kept both
    sanskrit_only = args.sanskrit_only
    if args.include_copyrighted_text:
        sanskrit_only = False

    pipeline = GitaSupersiteImportPipeline(cache_dir=args.cache_dir)
    try:
        result = asyncio.run(
            pipeline.run(
                args.out,
                include_copyrighted_text=args.include_copyrighted_text,
                acknowledge_license=args.acknowledge_license,
                sanskrit_only=sanskrit_only,
                chapters=chapters,
                force_download=args.force_download,
                local_html_dir=args.local_html_dir,
            )
        )
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(result.report_path.read_text(encoding="utf-8"))
    print(f"wrote {result.output_path}")
    print(f"verses {result.verse_count}")
    return 0 if result.report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
