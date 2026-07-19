#!/usr/bin/env python3
"""CLI: validate Sarathi canonical corpus JSON files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running via Poetry from apps/api (PYTHONPATH=app package root).
ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.corpus.validator import CorpusValidator  # noqa: E402


def _default_paths() -> list[Path]:
    corpus_root = ROOT / "data" / "corpus"
    if not corpus_root.exists():
        return []
    return sorted(corpus_root.rglob("*.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Sarathi canonical corpus")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Corpus JSON files (default: data/corpus/**/*.json, excluding build/)",
    )
    args = parser.parse_args(argv)

    paths = args.paths or [
        p for p in _default_paths() if "build" not in p.parts and not p.name.endswith(".build.json")
    ]
    if not paths:
        print("No corpus files found.", file=sys.stderr)
        return 2

    validator = CorpusValidator()
    exit_code = 0
    for path in paths:
        report = validator.validate_path(path)
        status = "OK" if report.ok else "FAIL"
        print(f"[{status}] {path} — {report.node_count} nodes")
        for issue in report.errors:
            print(f"  ERROR {issue.code}: {issue.message}" + (f" ({issue.node_id})" if issue.node_id else ""))
        for issue in report.warnings:
            print(
                f"  WARN  {issue.code}: {issue.message}"
                + (f" ({issue.node_id})" if issue.node_id else "")
            )
        if not report.ok:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
