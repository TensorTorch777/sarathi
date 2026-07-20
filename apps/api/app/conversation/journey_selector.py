"""Select an optional wisdom journey after a confident L1 answer."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.conversation.journey_loader import Journey, JourneyCatalog

_TOKEN_RE = re.compile(r"[a-z0-9']+", re.I)

# Must meet or exceed this combined retrieval score to offer a journey.
_MIN_CONFIDENCE = 40.0


@dataclass(frozen=True, slots=True)
class JourneyOffer:
    journey: Journey | None
    reason: str
    offer_text: str | None = None


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 2}


class JourneySelector:
    """
    Rules:
      - Never recommend if confidence is low.
      - Never recommend journeys whose steps aren't approved (caller validates).
      - Prefer journeys matching retrieved family + entry-query overlap.
    """

    def __init__(self, catalog: JourneyCatalog) -> None:
        self._catalog = catalog

    def select(
        self,
        *,
        message: str,
        intent: str,
        family_id: str | None,
        confidence: float,
        already_offered: bool,
        journey_active: bool,
    ) -> JourneyOffer:
        if journey_active:
            return JourneyOffer(journey=None, reason="journey_already_active")
        if already_offered:
            return JourneyOffer(journey=None, reason="already_offered")
        if confidence < _MIN_CONFIDENCE:
            return JourneyOffer(journey=None, reason="low_confidence")
        if intent == "crisis":
            return JourneyOffer(journey=None, reason="crisis_no_journey")
        if not self._catalog.journeys:
            return JourneyOffer(journey=None, reason="no_journeys")

        q_tokens = _tokens(message)
        q_lower = message.lower()
        scored: list[tuple[float, Journey]] = []

        for journey in self._catalog.journeys.values():
            score = 0.0
            if family_id and family_id in journey.families:
                score += 20.0
            for eq in journey.entry_queries:
                eq_l = eq.lower()
                if eq_l in q_lower or q_lower in eq_l:
                    score += 25.0
                else:
                    score += len(q_tokens & _tokens(eq)) * 3.0
            # Light intent affinity
            if intent == "guidance" and journey.id in {
                "fear_of_failure",
                "discipline",
                "purpose",
                "anger",
                "forgiveness",
            }:
                score += 2.0
            if intent == "comparison" and journey.id == "comparison":
                score += 15.0
            if score > 0:
                scored.append((score, journey))

        if not scored:
            return JourneyOffer(journey=None, reason="no_match")

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scored[0]
        if best_score < 12.0:
            return JourneyOffer(journey=None, reason="weak_match")

        offer_text = (
            f"If you'd like, we can explore a short journey on {best.title.lower()}. "
            f"It connects a few teachings that build on one another. "
            f'Say "yes" to begin, or we can stay with this single teaching.'
        )
        return JourneyOffer(
            journey=best,
            reason=f"matched:{best.id}:{best_score:.1f}",
            offer_text=offer_text,
        )
