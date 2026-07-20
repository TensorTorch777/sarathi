"""Evaluation metric helpers and score aggregates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class EditorialScore:
    fidelity: float
    clarity: float
    practicality: float
    progressive_disclosure: float
    sarathi_voice: float
    misconception_handling: float

    @property
    def mean(self) -> float:
        vals = [
            self.fidelity,
            self.clarity,
            self.practicality,
            self.progressive_disclosure,
            self.sarathi_voice,
            self.misconception_handling,
        ]
        return sum(vals) / len(vals)

    def to_dict(self) -> dict[str, float]:
        d = asdict(self)
        d["mean"] = round(self.mean, 4)
        return d


@dataclass(slots=True)
class ConversationScore:
    response_length_ok: float
    followup_discipline: float
    journey_offer_appropriate: float
    depth_respected: float
    notes: list[str] = field(default_factory=list)

    @property
    def mean(self) -> float:
        vals = [
            self.response_length_ok,
            self.followup_discipline,
            self.journey_offer_appropriate,
            self.depth_respected,
        ]
        return sum(vals) / len(vals)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["mean"] = round(self.mean, 4)
        return d


@dataclass(slots=True)
class SafetyScore:
    passed: bool
    score: float
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "violations": list(self.violations),
        }


@dataclass(slots=True)
class RetrievalDiagnostics:
    approved_family_used: bool
    anchor: bool
    core: bool
    fallback: bool
    confidence: float
    normalized_confidence: float
    family_id: str | None
    verse_ids: list[str]
    alternatives_considered: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def mean_or_zero(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# Editorial confidence from retriever is often 40–100+; normalize for reports.
def normalize_retrieval_confidence(raw: float, *, low: float = 20.0, high: float = 100.0) -> float:
    if high <= low:
        return 0.0
    return clamp01((raw - low) / (high - low))
