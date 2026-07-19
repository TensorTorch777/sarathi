"""Tests for the offline Gita Supersite importer (fixtures only — no network)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.importers.gita_supersite.license import ACK_PHRASE, assert_copyrighted_allowed
from app.importers.gita_supersite.normalizer import GitaSupersiteNormalizer
from app.importers.gita_supersite.parser import GitaSupersiteParser
from app.importers.gita_supersite.pipeline import GitaSupersiteImportPipeline

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "gita_supersite"
    / "bg_2_47.html"
)


def test_parser_extracts_sanskrit_and_english_from_fixture() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    extract = GitaSupersiteParser().parse(html, chapter=2, verse=47)
    assert "कर्मण्येवाधिकारस्ते" in extract.sanskrit
    assert extract.translations
    assert any(t.edition == "sivananda" for t in extract.translations)
    assert extract.commentaries


def test_normalizer_sanskrit_only_omits_copyrighted_text() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    extract = GitaSupersiteParser().parse(html, chapter=2, verse=47)
    node = GitaSupersiteNormalizer().normalize(
        extract,
        include_copyrighted_text=False,
        sanskrit_only=True,
    )
    assert node["corpus_layer"] == "authentic"
    assert node["sanskrit"]
    assert node["translations"] == []
    assert node["commentaries"] == []
    assert node["summary"] is None
    assert node["topics"] == []


def test_license_gate_blocks_copyrighted_without_ack() -> None:
    with pytest.raises(PermissionError):
        assert_copyrighted_allowed(include_copyrighted=True, acknowledge=None)
    assert_copyrighted_allowed(
        include_copyrighted=True,
        acknowledge=ACK_PHRASE,
    )


@pytest.mark.asyncio
async def test_pipeline_fixture_import(tmp_path: Path) -> None:
    pipeline = GitaSupersiteImportPipeline(cache_dir=tmp_path / "cache")
    out = tmp_path / "layer1.json"
    result = await pipeline.run(
        out,
        sanskrit_only=True,
        targets=[(2, 47)],
        local_html_dir=FIXTURE.parent,
    )
    assert result.verse_count == 1
    assert result.output_path.exists()
    assert result.report.ok
    text = out.read_text(encoding="utf-8")
    assert "bg_2_47" in text
    assert "कर्मण्येवाधिकारस्ते" in text
