"""Prompt log status enumeration."""

from enum import StrEnum


class PromptStatus(StrEnum):
    """Outcome status for a logged LLM prompt."""

    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
