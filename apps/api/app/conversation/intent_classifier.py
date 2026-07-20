"""Deterministic conversation intent classifier (no AI agents)."""

from __future__ import annotations

import re
from dataclasses import dataclass


SUPPORTED_INTENTS = (
    "guidance",
    "reflection",
    "learning",
    "crisis",
    "comparison",
    "search",
)


@dataclass(frozen=True, slots=True)
class IntentResult:
    intent: str
    confidence: float
    matched_cues: tuple[str, ...]


_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "crisis",
        (
            r"\bsuicid",
            r"\bkill myself\b",
            r"\bend my life\b",
            r"\bself[- ]?harm\b",
            r"\bwant to die\b",
            r"\bcan't go on\b",
            r"\bcannot go on\b",
        ),
    ),
    (
        "comparison",
        (
            r"\bcompar(e|ing)\b",
            r"\bbetter than\b",
            r"\bothers (are|have)\b",
            r"\bjealous\b",
            r"\benvy\b",
            r"\beveryone else\b",
        ),
    ),
    (
        "learning",
        (
            r"\bteach me\b",
            r"\bphilosoph",
            r"\bwhat does .+ mean\b",
            r"\bexplain the (concept|teaching|verse)\b",
            r"\bsanskrit\b",
            r"\bdeeper meaning\b",
            r"\bwhy does the gita\b",
        ),
    ),
    (
        "reflection",
        (
            r"\bhow (do|should) i feel\b",
            r"\breflect\b",
            r"\bwhat am i (feeling|missing)\b",
            r"\bsit with\b",
            r"\bjournal\b",
        ),
    ),
    (
        "search",
        (
            r"\bwhich verse\b",
            r"\bfind (a )?verse\b",
            r"\bwhere does (krishna|the gita)\b",
            r"\bcite\b",
            r"\bbg\s*\d+",
        ),
    ),
    (
        "guidance",
        (
            r"\bhow (do|can|should) i\b",
            r"\bwhat should i\b",
            r"\bhelp me\b",
            r"\bi('m| am) (scared|afraid|terrified|anxious|stuck|lost)\b",
            r"\bfail(ure|ing)?\b",
            r"\badvice\b",
            r"\bguide\b",
        ),
    ),
]


class IntentClassifier:
    """Simple deterministic classifier over supported intents."""

    def classify(self, message: str) -> IntentResult:
        text = message.strip().lower()
        if not text:
            return IntentResult(intent="guidance", confidence=0.4, matched_cues=())

        scores: dict[str, list[str]] = {i: [] for i in SUPPORTED_INTENTS}
        for intent, patterns in _PATTERNS:
            for pat in patterns:
                if re.search(pat, text, flags=re.I):
                    scores[intent].append(pat)

        best_intent = "guidance"
        best_hits: list[str] = []
        for intent in SUPPORTED_INTENTS:
            hits = scores[intent]
            if len(hits) > len(best_hits):
                best_intent = intent
                best_hits = hits
            elif len(hits) == len(best_hits) and len(hits) > 0:
                # Prefer crisis over others when tied
                if intent == "crisis":
                    best_intent = intent
                    best_hits = hits

        if not best_hits:
            return IntentResult(intent="guidance", confidence=0.55, matched_cues=())

        confidence = min(0.95, 0.55 + 0.12 * len(best_hits))
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            matched_cues=tuple(best_hits[:5]),
        )


# Depth request detectors (for L2 / L3 transitions)
_L2_CUES = re.compile(
    r"\b(why|tell me more|explain|go (a )?bit deeper|expand|what does that mean|"
    r"can you (explain|say more)|more detail)\b",
    re.I,
)
_L3_CUES = re.compile(
    r"\b(philosoph|sanskrit|deeper (teaching|connection|meaning)|teach me (the )?(philosophy|concept)|"
    r"family (overview|context)|related families|full depth|go deep)\b",
    re.I,
)
_NEW_TOPIC_CUES = re.compile(
    r"\b(different (topic|question)|something else|new question|instead|"
    r"what about|another (question|problem))\b",
    re.I,
)


def wants_l2(message: str) -> bool:
    return bool(_L2_CUES.search(message))


def wants_l3(message: str) -> bool:
    return bool(_L3_CUES.search(message))


def wants_new_topic(message: str) -> bool:
    return bool(_NEW_TOPIC_CUES.search(message))
