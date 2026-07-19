#!/usr/bin/env python3
"""CLI: validate then emit a normalized corpus build artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.corpus.builder import CorpusBuilder  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Sarathi canonical corpus artifact")
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT
        / "data"
        / "corpus"
        / "bhagavad_gita"
        / "samples"
        / "bg_2_47_50.curated.json",
        help="Source corpus JSON",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "corpus" / "bhagavad_gita" / "build",
        help="Output directory for build artifacts",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any warnings are present",
    )
    args = parser.parse_args(argv)

    builder = CorpusBuilder()
    result = builder.build(args.source, args.out, strict_warnings=args.strict)
    report = result.report
    status = "OK" if report.ok and result.output_path else "FAIL"
    print(f"[{status}] source={result.source_path}")
    for issue in report.errors:
        print(f"  ERROR {issue.code}: {issue.message}" + (f" ({issue.node_id})" if issue.node_id else ""))
    for issue in report.warnings:
        print(f"  WARN  {issue.code}: {issue.message}" + (f" ({issue.node_id})" if issue.node_id else ""))

    if not report.ok or not result.output_path:
        return 1

    print(f"  wrote {result.output_path}")
    print(f"  sha256 {result.checksum}")
    print(f"  nodes  {report.node_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
