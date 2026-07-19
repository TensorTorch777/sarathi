"""Knowledge-base node kinds (scripture units and future wisdom entities)."""

from enum import StrEnum


class NodeType(StrEnum):
    """Type of a KnowledgeNode in the Sarathi knowledge base."""

    VERSE = "verse"
    SUMMARY = "summary"
    COMMENTARY = "commentary"
    CONCEPT = "concept"
    CHARACTER = "character"
    EVENT = "event"
