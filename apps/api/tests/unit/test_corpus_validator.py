"""Tests for canonical corpus schema and validator."""

from __future__ import annotations

import json
from pathlib import Path

from app.corpus.builder import CorpusBuilder
from app.corpus.validator import CorpusValidator

ROOT = Path(__file__).resolve().parents[4]
CORPUS = (
    ROOT / "data" / "corpus" / "bhagavad_gita" / "samples" / "bg_2_47_50.curated.json"
)


def test_sample_corpus_validates() -> None:
    report = CorpusValidator().validate_path(CORPUS)
    assert report.ok, [e.message for e in report.errors]
    assert report.node_count == 4


def test_duplicate_id_detected(tmp_path: Path) -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["nodes"].append(payload["nodes"][0].copy())
    report = CorpusValidator().validate_payload(payload)
    assert not report.ok
    assert any(i.code == "duplicate_id" for i in report.errors)


def test_broken_related_detected(tmp_path: Path) -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["nodes"][0]["related_nodes"] = ["bg_99_99"]
    report = CorpusValidator().validate_payload(payload)
    assert not report.ok
    assert any(i.code == "broken_related_node" for i in report.errors)


def test_invalid_metadata_slug() -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["nodes"][0]["topics"] = ["not_a_real_topic"]
    report = CorpusValidator().validate_payload(payload)
    assert not report.ok
    assert any(i.code == "invalid_metadata" for i in report.errors)


def test_build_corpus_writes_artifact(tmp_path: Path) -> None:
    result = CorpusBuilder().build(CORPUS, tmp_path)
    assert result.report.ok
    assert result.output_path
    assert Path(result.output_path).exists()
    assert result.checksum
    assert (tmp_path / "bg_2_47_50.curated.build.sha256").exists()
