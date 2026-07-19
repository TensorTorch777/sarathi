"""Canonical user intents for retrieval-oriented metadata."""

from enum import StrEnum


class UserIntent(StrEnum):
    """Why a seeker may approach Sarathi — improves human retrieval later."""

    SEEKING_GUIDANCE = "seeking_guidance"
    SEEKING_ENCOURAGEMENT = "seeking_encouragement"
    SEEKING_MEANING = "seeking_meaning"
    SEEKING_COURAGE = "seeking_courage"
    SEEKING_DISCIPLINE = "seeking_discipline"
    SEEKING_FORGIVENESS = "seeking_forgiveness"
    SEEKING_DETACHMENT = "seeking_detachment"
    SEEKING_PEACE = "seeking_peace"
