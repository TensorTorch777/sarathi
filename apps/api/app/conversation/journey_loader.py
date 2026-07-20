"""Wisdom journey models and read-only loader (curated JSON only)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def default_journeys_root() -> Path:
    """Resolve repo `data/journeys`."""
    return Path(__file__).resolve().parents[4] / "data" / "journeys"


@dataclass(frozen=True, slots=True)
class JourneyStep:
    family: str
    verse: str
    response_level: str
    practice: str
    reflection: str


@dataclass(frozen=True, slots=True)
class Journey:
    id: str
    title: str
    description: str
    entry_queries: tuple[str, ...]
    families: tuple[str, ...]
    steps: tuple[JourneyStep, ...]


@dataclass(frozen=True, slots=True)
class JourneyCatalog:
    journeys: dict[str, Journey]


def load_journeys(root: Path | None = None) -> JourneyCatalog:
    """Load all curated journey JSON files (no AI generation)."""
    base = root or default_journeys_root()
    journeys: dict[str, Journey] = {}
    for path in sorted(base.glob("*.json")):
        if path.name == "INDEX.json":
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        steps = tuple(
            JourneyStep(
                family=s["family"],
                verse=s["verse"],
                response_level=s.get("response_level") or "L1",
                practice=s.get("practice") or "",
                reflection=s.get("reflection") or "",
            )
            for s in raw.get("steps") or []
        )
        if not steps:
            continue
        jid = raw["id"]
        journeys[jid] = Journey(
            id=jid,
            title=raw["title"],
            description=raw.get("description") or "",
            entry_queries=tuple(raw.get("entry_queries") or []),
            families=tuple(raw.get("families") or []),
            steps=steps,
        )
    return JourneyCatalog(journeys=journeys)


@lru_cache(maxsize=1)
def get_journey_catalog() -> JourneyCatalog:
    return load_journeys()


def validate_journey_against_approved(
    catalog: JourneyCatalog,
    approved_ids: set[str],
) -> list[str]:
    """Return list of validation errors (empty if valid)."""
    errors: list[str] = []
    for journey in catalog.journeys.values():
        for step in journey.steps:
            if step.verse not in approved_ids:
                errors.append(f"{journey.id}: step verse {step.verse} is not approved")
    return errors
