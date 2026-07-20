"""Score conversation turns against editorial + product quality principles."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from app.conversation.intelligence_loader import IntelligenceIndex, get_intelligence_index
from app.conversation.safety_checker import SafetyChecker
from app.evaluation.metrics import (
    ConversationScore,
    EditorialScore,
    RetrievalDiagnostics,
    SafetyScore,
    clamp01,
    normalize_retrieval_confidence,
)

_PROMISE = re.compile(r"\b(everything will|you will succeed|i promise|guaranteed)\b", re.I)
_GUILT = re.compile(r"\b(you should be ashamed|you are (a )?failure|worthless)\b", re.I)
_PUNISH = re.compile(r"\b(krishna is (punishing|testing)|god is punishing)\b", re.I)
_SECTION_DUMP = re.compile(
    r"(^|\n)\s*(Verse|Summary|Interpretation|Practice|Reflection)\s*:\s*",
    re.I,
)


@dataclass(slots=True)
class EvaluationResult:
    response_id: str
    intent: str
    family: str | None
    response_level: str
    journey_used: bool
    retrieval_confidence: float
    editorial_score: dict[str, float]
    conversation_score: dict[str, Any]
    safety_score: dict[str, Any]
    overall_score: float
    retrieval_diagnostics: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ResponseEvaluator:
    """
    Observability-only evaluator.

    Consumes ConversationTurnResult fields / debug — does not alter answers.
    """

    def __init__(
        self,
        *,
        index: IntelligenceIndex | None = None,
        safety: SafetyChecker | None = None,
    ) -> None:
        self._index = index or get_intelligence_index()
        self._safety = safety or SafetyChecker()

    def evaluate(
        self,
        *,
        answer: str,
        intent: str,
        family_id: str | None,
        response_level: str,
        confidence: float,
        verse_ids: list[str],
        debug: dict[str, object] | None = None,
        alternatives: list[str] | None = None,
    ) -> EvaluationResult:
        debug = debug or {}
        journey_status = str(debug.get("journey_status") or "none")
        journey_used = journey_status in {"offered", "active", "completed"}
        followup_asked = bool(debug.get("followup_asked"))
        safety_ok = bool(debug.get("safety_checks", {}).get("ok", True)) if isinstance(
            debug.get("safety_checks"), dict
        ) else True
        violations = list(
            (debug.get("safety_checks") or {}).get("violations") or []  # type: ignore[union-attr]
        )

        # Re-check text for safety scoring independence
        safety_check = self._safety.check(answer)
        if not safety_check.ok:
            safety_ok = False
            violations = list(dict.fromkeys([*violations, *safety_check.violations]))

        editorial = self._score_editorial(
            answer=answer,
            response_level=response_level,
            verse_ids=verse_ids,
            family_id=family_id,
            debug=debug,
        )
        conversation = self._score_conversation(
            answer=answer,
            response_level=response_level,
            followup_asked=followup_asked,
            journey_status=journey_status,
            confidence=confidence,
            intent=intent,
        )
        safety = SafetyScore(
            passed=safety_ok and not violations,
            score=1.0 if (safety_ok and not violations) else 0.0,
            violations=violations,
        )
        retrieval = self._retrieval_diagnostics(
            family_id=family_id,
            confidence=confidence,
            verse_ids=verse_ids,
            alternatives=alternatives or list(verse_ids[1:5]),
        )

        overall = clamp01(
            0.40 * editorial.mean
            + 0.25 * conversation.mean
            + 0.20 * safety.score
            + 0.15 * retrieval.normalized_confidence
        )

        notes: list[str] = []
        if retrieval.anchor:
            notes.append("anchor_family_selected")
        if journey_used:
            notes.append(f"journey_{journey_status}")
        if followup_asked:
            notes.append("followup_asked")

        return EvaluationResult(
            response_id=str(uuid4()),
            intent=intent,
            family=family_id,
            response_level=response_level,
            journey_used=journey_used,
            retrieval_confidence=round(retrieval.normalized_confidence, 4),
            editorial_score=editorial.to_dict(),
            conversation_score=conversation.to_dict(),
            safety_score=safety.to_dict(),
            overall_score=round(overall, 4),
            retrieval_diagnostics=retrieval.to_dict(),
            notes=notes,
        )

    def _score_editorial(
        self,
        *,
        answer: str,
        response_level: str,
        verse_ids: list[str],
        family_id: str | None,
        debug: dict[str, object],
    ) -> EditorialScore:
        primary = self._index.enrichments.get(verse_ids[0]) if verse_ids else None
        family = self._index.families.get(family_id) if family_id else None

        # Fidelity: cites a real verse / uses approved enrichment
        fidelity = 0.4
        if primary and primary.status in {"approved", "locked"}:
            fidelity = 0.95
        elif primary and primary.status == "reviewed":
            fidelity = 0.7
        elif primary:
            fidelity = 0.45
        if primary and primary.citation in answer:
            fidelity = min(1.0, fidelity + 0.05)

        # Clarity: not a labeled dump; readable length
        clarity = 0.9
        if _SECTION_DUMP.search(answer):
            clarity = 0.45
        words = len(answer.split())
        if words < 8:
            clarity = min(clarity, 0.5)
        if words > 350:
            clarity = min(clarity, 0.55)

        # Practicality: practice present at L1 / journey
        practicality = 0.65
        practice = debug.get("practice_chosen")
        if practice or re.search(r"\b(one small step|practice|try)\b", answer, re.I):
            practicality = 0.95
        if response_level == "L3" and not practice:
            practicality = 0.75

        # Progressive disclosure: L1 short; L3 only when requested (caller responsibility)
        progressive = 0.9
        if response_level == "L1":
            paras = [p for p in answer.split("\n\n") if p.strip()]
            # Allow journey offer as extra short paragraph
            if len(paras) > 4:
                progressive = 0.55
            if words > 220:
                progressive = min(progressive, 0.6)
        elif response_level == "L3":
            progressive = 0.95  # depth only when reached via engine

        # Sarathi Voice: no promises / guilt / punishment
        voice = 1.0
        if _PROMISE.search(answer) or _GUILT.search(answer) or _PUNISH.search(answer):
            voice = 0.0

        # Misconception handling: L2/L3 or family misconceptions when deepening
        misconception = 0.7
        shown = debug.get("misconceptions_shown") or []
        if response_level == "L1":
            misconception = 0.85  # not required at L1
        elif shown:
            misconception = 0.98
        elif response_level in {"L2", "L3"} and family and family.family_misconceptions:
            # Expected but missing
            if any(m.lower() in answer.lower() for m in family.family_misconceptions):
                misconception = 0.95
            else:
                misconception = 0.6

        return EditorialScore(
            fidelity=clamp01(fidelity),
            clarity=clamp01(clarity),
            practicality=clamp01(practicality),
            progressive_disclosure=clamp01(progressive),
            sarathi_voice=clamp01(voice),
            misconception_handling=clamp01(misconception),
        )

    def _score_conversation(
        self,
        *,
        answer: str,
        response_level: str,
        followup_asked: bool,
        journey_status: str,
        confidence: float,
        intent: str,
    ) -> ConversationScore:
        notes: list[str] = []
        words = len(answer.split())

        # Length: L1 should stay concise (journey offer allowed)
        if response_level == "L1":
            length_ok = 1.0 if words <= 220 else clamp01(1.3 - words / 400)
        elif response_level == "L2":
            length_ok = 1.0 if words <= 320 else 0.7
        else:
            length_ok = 1.0 if words <= 450 else 0.75

        # Follow-up discipline: OK if asked only when needed; penalize if high conf + followup
        norm = normalize_retrieval_confidence(confidence)
        if followup_asked and norm >= 0.75:
            followup = 0.55
            notes.append("followup_despite_high_confidence")
        elif followup_asked and norm < 0.45:
            followup = 0.95
            notes.append("followup_for_low_confidence")
        else:
            followup = 0.95

        # Journey offer: appropriate when guidance + solid confidence
        if journey_status == "offered":
            journey = 0.95 if intent in {"guidance", "learning", "comparison"} and norm >= 0.5 else 0.6
        elif journey_status in {"active", "completed"}:
            journey = 0.95
        else:
            journey = 0.85  # not offering is fine

        # Depth respected: L1 default is correct starting depth
        depth = 1.0 if response_level in {"L1", "L2", "L3"} else 0.5

        return ConversationScore(
            response_length_ok=clamp01(length_ok),
            followup_discipline=clamp01(followup),
            journey_offer_appropriate=clamp01(journey),
            depth_respected=clamp01(depth),
            notes=notes,
        )

    def _retrieval_diagnostics(
        self,
        *,
        family_id: str | None,
        confidence: float,
        verse_ids: list[str],
        alternatives: list[str],
    ) -> RetrievalDiagnostics:
        family = self._index.families.get(family_id) if family_id else None
        primary = self._index.enrichments.get(verse_ids[0]) if verse_ids else None
        approved_family = bool(family and family.status == "approved")
        anchor = bool(family and (family.anchor_family or family.tier == "anchor"))
        core = bool(family and family.tier == "core")
        fallback = bool(
            primary is None
            or primary.status == "generated"
            or (family is None and primary is not None)
        )
        return RetrievalDiagnostics(
            approved_family_used=approved_family,
            anchor=anchor,
            core=core,
            fallback=fallback,
            confidence=confidence,
            normalized_confidence=normalize_retrieval_confidence(confidence),
            family_id=family_id,
            verse_ids=list(verse_ids),
            alternatives_considered=list(alternatives),
        )
