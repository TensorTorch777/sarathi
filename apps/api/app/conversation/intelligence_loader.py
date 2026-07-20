"""Read-only loader for Sarathi Intelligence + verse families (frozen corpus)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any


def default_intelligence_root() -> Path:
    """Resolve repo `data/corpus/bhagavad_gita/sarathi_intelligence`."""
    # app/conversation → app → api → apps → repo
    return (
        Path(__file__).resolve().parents[4]
        / "data"
        / "corpus"
        / "bhagavad_gita"
        / "sarathi_intelligence"
    )


@dataclass(frozen=True, slots=True)
class FamilyRecord:
    id: str
    name: str
    verse_ids: tuple[str, ...]
    status: str
    tier: str
    overview: str | None = None
    why_this_matters_today: str | None = None
    family_misconceptions: tuple[str, ...] = ()
    theme: str | None = None
    anchor_family: bool = False


@dataclass(frozen=True, slots=True)
class EnrichmentRecord:
    node_id: str
    citation: str
    status: str
    summary: str
    modern_interpretation: str
    topics: tuple[str, ...]
    emotions: tuple[str, ...]
    life_domains: tuple[str, ...]
    user_intents: tuple[str, ...]
    virtues: tuple[str, ...]
    practice: tuple[str, ...]
    reflection_question: str | None
    related_verses: tuple[str, ...]
    misconceptions: tuple[str, ...]
    common_queries: tuple[str, ...]
    verse_family: str | None
    response_levels: dict[str, Any] = field(default_factory=dict)
    confidence_overall: float = 0.0


@dataclass(frozen=True, slots=True)
class IntelligenceIndex:
    enrichments: dict[str, EnrichmentRecord]
    families: dict[str, FamilyRecord]
    anchor_family_ids: frozenset[str]
    core_family_ids: frozenset[str]


_STATUS_RANK = {
    "approved": 4,
    "reviewed": 3,
    "generated": 2,
    "locked": 5,
}


def status_rank(status: str) -> int:
    return _STATUS_RANK.get(status, 0)


def tier_rank(tier: str, *, anchor: bool) -> int:
    if anchor or tier == "anchor":
        return 40
    if tier == "core":
        return 30
    if tier == "supporting":
        return 10
    return 0


def load_intelligence(root: Path | None = None) -> IntelligenceIndex:
    """Load ALL.generated.json + verse_families.json (read-only)."""
    base = root or default_intelligence_root()
    all_path = base / "ALL.generated.json"
    fam_path = base / "verse_families.json"
    raw_all = json.loads(all_path.read_text(encoding="utf-8"))
    raw_fam = json.loads(fam_path.read_text(encoding="utf-8"))

    enrichments: dict[str, EnrichmentRecord] = {}
    for item in raw_all.get("enrichments", []):
        conf = item.get("confidence") or {}
        enrichments[item["node_id"]] = EnrichmentRecord(
            node_id=item["node_id"],
            citation=item.get("citation") or item["node_id"],
            status=item.get("status") or "generated",
            summary=item.get("summary") or "",
            modern_interpretation=item.get("modern_interpretation") or "",
            topics=tuple(item.get("topics") or []),
            emotions=tuple(item.get("emotions") or []),
            life_domains=tuple(item.get("life_domains") or []),
            user_intents=tuple(item.get("user_intents") or []),
            virtues=tuple(item.get("virtues") or []),
            practice=tuple(item.get("practice") or []),
            reflection_question=item.get("reflection_question"),
            related_verses=tuple(item.get("related_verses") or []),
            misconceptions=tuple(item.get("misconceptions") or []),
            common_queries=tuple(item.get("common_queries") or []),
            verse_family=item.get("verse_family"),
            response_levels=dict(item.get("response_levels") or {}),
            confidence_overall=float(conf.get("overall") or 0.0),
        )

    families: dict[str, FamilyRecord] = {}
    for fam in raw_fam.get("families", []):
        families[fam["id"]] = FamilyRecord(
            id=fam["id"],
            name=fam.get("name") or fam["id"],
            verse_ids=tuple(fam.get("verse_ids") or []),
            status=fam.get("status") or "planned",
            tier=fam.get("tier") or ("anchor" if fam.get("anchor_family") else "supporting"),
            overview=fam.get("overview"),
            why_this_matters_today=fam.get("why_this_matters_today"),
            family_misconceptions=tuple(fam.get("family_misconceptions") or []),
            theme=fam.get("theme"),
            anchor_family=bool(fam.get("anchor_family")),
        )

    anchors = frozenset(raw_fam.get("anchor_families") or [
        fid for fid, f in families.items() if f.anchor_family or f.tier == "anchor"
    ])
    cores = frozenset(
        fid for fid, f in families.items() if f.tier == "core" and fid not in anchors
    )
    return IntelligenceIndex(
        enrichments=enrichments,
        families=families,
        anchor_family_ids=anchors,
        core_family_ids=cores,
    )


@lru_cache(maxsize=1)
def get_intelligence_index() -> IntelligenceIndex:
    """Cached process-wide index (corpus is frozen for product alpha)."""
    return load_intelligence()
