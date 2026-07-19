"""Helpers to turn grounded answers into calm spoken narration."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_BULLET = re.compile(r"^[\-\*]\s+", re.MULTILINE)
_CODE = re.compile(r"`{1,3}.*?`{1,3}", re.DOTALL)
_SANSKRIT_BLOCK = re.compile(
    r"(?:###\s*Relevant verse.*?\n)(?:BG[^\n]*\n)?([\u0900-\u097F].*\n?)+",
    re.IGNORECASE,
)
_WHITESPACE = re.compile(r"\s+")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")


def answer_to_spoken(answer: str) -> str:
    """Convert a markdown answer into plain speech-friendly prose."""
    text = answer.strip()
    text = _CODE.sub(" ", text)
    text = _SANSKRIT_BLOCK.sub(" ", text)
    text = _HEADING.sub("", text)
    text = _BULLET.sub("", text)
    # Drop heavy Devanagari lines — keep English teachings for calm narration.
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"[\u0900-\u097F]", stripped) and not re.search(r"[A-Za-z]", stripped):
            continue
        lines.append(stripped)
    text = " ".join(lines)
    text = _WHITESPACE.sub(" ", text).strip()
    return text


def iter_speakable_sentences(buffer: str) -> tuple[list[str], str]:
    """Split completed sentences from a streaming buffer.

    Returns (ready_sentences, remainder).
    """
    buffer = buffer.strip()
    if not buffer:
        return [], ""

    parts = _SENTENCE_END.split(buffer)
    if len(parts) == 1:
        # Emit early if the buffer is already a long clause with terminal punctuation.
        if buffer[-1:] in ".!?" and len(buffer) >= 40:
            return [buffer], ""
        return [], buffer

    *ready, remainder = parts
    ready = [p.strip() for p in ready if p.strip()]
    return ready, remainder.strip()
