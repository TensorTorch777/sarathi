"""Render journey steps and detect accept / continue / exit cues."""

from __future__ import annotations

import re

from app.conversation.intelligence_loader import IntelligenceIndex
from app.conversation.journey_loader import Journey, JourneyStep

_ACCEPT = re.compile(
    r"^\s*(yes|yeah|yep|sure|ok|okay|please|let'?s (go|do it|begin|start)|"
    r"i('d| would) like (that|to)|start( the)? journey|begin)\s*[.!?]?\s*$",
    re.I,
)
_CONTINUE = re.compile(
    r"\b(continue|next( step)?|keep going|go on|another|proceed)\b",
    re.I,
)
_EXIT = re.compile(
    r"\b(stop|exit|enough|quit|end( the)? journey|not now|no thanks|"
    r"skip( the)? journey|leave (this|the) journey)\b",
    re.I,
)
_DECLINE = re.compile(
    r"^\s*(no|nope|not now|no thanks|maybe later)\s*[.!?]?\s*$",
    re.I,
)


def accepts_journey(message: str) -> bool:
    return bool(_ACCEPT.match(message.strip()))


def declines_journey(message: str) -> bool:
    return bool(_DECLINE.match(message.strip()))


def wants_continue(message: str) -> bool:
    return bool(_CONTINUE.search(message))


def wants_exit_journey(message: str) -> bool:
    return bool(_EXIT.search(message))


def render_journey_step(
    journey: Journey,
    step: JourneyStep,
    *,
    step_index: int,
    index: IntelligenceIndex,
) -> str:
    """Build natural prose for one journey step from approved enrichment + curated practice."""
    enr = index.enrichments.get(step.verse)
    summary = ""
    citation = step.verse
    if enr:
        summary = (enr.response_levels.get("level_1") or enr.summary or "").strip()
        citation = enr.citation

    total = len(journey.steps)
    n = step_index + 1
    parts: list[str] = [
        f"**{journey.title}** — step {n} of {total}",
        "",
        summary or f"A teaching from {citation}.",
        f"The Gita points to this in {citation}.",
    ]
    practice = step.practice or ((enr.practice[0] if enr and enr.practice else "") or "")
    reflection = step.reflection or (enr.reflection_question if enr else "") or ""
    if practice:
        parts.extend(["", f"One small step: {practice}"])
    if reflection:
        parts.extend(["", f"A question to sit with: {reflection}"])

    if n < total:
        parts.extend(
            [
                "",
                'When you are ready, say "continue" for the next teaching — '
                'or "stop" to leave the journey anytime.',
            ]
        )
    else:
        parts.extend(
            [
                "",
                f"That completes the {journey.title} journey. "
                "You can ask another question whenever you like.",
            ]
        )
    return "\n".join(parts)
