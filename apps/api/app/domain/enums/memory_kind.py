"""Kinds of long-term user memory stored in the vector index."""

from enum import StrEnum


class MemoryKind(StrEnum):
    """Canonical memory categories for Sarathi long-term memory."""

    CAREER_GOAL = "career_goal"
    CONVERSATION = "conversation"
    CONVERSATION_SUMMARY = "conversation_summary"
    FAVORITE_VERSE = "favorite_verse"
    JOURNAL = "journal"
    REFLECTION = "reflection"
    NOTE = "note"
