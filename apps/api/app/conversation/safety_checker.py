"""Editorial safety checks before a response is returned."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SafetyResult:
    ok: bool
    violations: tuple[str, ...]
    sanitized_text: str | None = None


_PROMISE = re.compile(
    r"\b(everything will (be )?(ok|fine|work out)|you will (surely |definitely )?(succeed|be fine)|"
    r"guaranteed|i promise|this will fix)\b",
    re.I,
)
_DIAGNOSIS = re.compile(
    r"\b(you have (depression|anxiety disorder|ptsd|bipolar)|you are (bipolar|schizophrenic)|"
    r"clinical diagnosis|i diagnose)\b",
    re.I,
)
_GUILT = re.compile(
    r"\b(you should be ashamed|you are (a )?failure|you are (weak|pathetic|worthless)|"
    r"what is wrong with you)\b",
    re.I,
)
_PUNISHMENT = re.compile(
    r"\b(krishna is (punishing|testing) you|god is punishing|"
    r"divine (punishment|retaliation)|you deserve (this )?suffering)\b",
    re.I,
)
_FABRICATED_VERSE = re.compile(
    r"\bBG\s*(\d{1,2})\.(\d{1,3})\b",
    re.I,
)
_UNSAFE_RELATIONSHIP = re.compile(
    r"\b(stay with (your )?(abuser|him|her) anyway|endure (the )?abuse|"
    r"suffering is your duty in (this )?relationship)\b",
    re.I,
)

# Valid chapter/verse ranges for classic 700-verse Gita
_VERSE_COUNTS = {
    1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28,
    9: 34, 10: 42, 11: 55, 12: 20, 13: 34, 14: 27, 15: 20,
    16: 24, 17: 28, 18: 78,
}


class SafetyChecker:
    """Reject responses that violate Sarathi Voice / editorial safety."""

    def check(
        self,
        text: str,
        *,
        allowed_citations: set[str] | None = None,
    ) -> SafetyResult:
        violations: list[str] = []
        if _PROMISE.search(text):
            violations.append("promises")
        if _DIAGNOSIS.search(text):
            violations.append("diagnosis")
        if _GUILT.search(text):
            violations.append("guilt")
        if _PUNISHMENT.search(text):
            violations.append("punishment_framing")
        if _UNSAFE_RELATIONSHIP.search(text):
            violations.append("abusive_relationship_advice")

        for match in _FABRICATED_VERSE.finditer(text):
            chapter = int(match.group(1))
            verse = int(match.group(2))
            citation = f"BG {chapter}.{verse}"
            max_v = _VERSE_COUNTS.get(chapter)
            if max_v is None or verse < 1 or verse > max_v:
                violations.append(f"unsupported_citation:{citation}")
            elif allowed_citations is not None and citation not in allowed_citations:
                # Soft: only flag if we have an allow-list and citation is outside retrieved set
                # Still allow known valid citations from corpus even if not in turn set
                pass

        if violations:
            return SafetyResult(ok=False, violations=tuple(violations), sanitized_text=None)

        return SafetyResult(ok=True, violations=(), sanitized_text=text)

    def fallback_message(self) -> str:
        return (
            "I want to stay careful and grounded with you. "
            "Could you share what feels most pressing in your own words, "
            "and I will respond from the Gita's teaching without overreaching?"
        )
