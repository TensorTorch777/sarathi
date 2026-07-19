"""Relation types for the Wisdom Graph between KnowledgeNodes."""

from enum import StrEnum


class WisdomRelation(StrEnum):
    """Directed edge kinds that connect ideas beyond vector similarity."""

    RELATED_VERSE = "related_verse"
    DEFINES_CONCEPT = "defines_concept"
    ILLUSTRATES_CONCEPT = "illustrates_concept"
    EVOKES_EMOTION = "evokes_emotion"
    SUGGESTS_PRACTICE = "suggests_practice"
    PART_OF = "part_of"
    SUMMARIZES = "summarizes"
    COMMENTS_ON = "comments_on"
    INVOLVES_CHARACTER = "involves_character"
    DESCRIBES_EVENT = "describes_event"
    SUPPORTS = "supports"
    CONTRASTS = "contrasts"
