"""
Controlled vocabularies for the Sarathi Canonical Corpus.

Metadata must use these slugs (or be empty). No free-form LLM invention at ingest.
"""

from __future__ import annotations

# Bhagavad Gita chapter → verse count (standard 700-verse numbering).
GITA_VERSE_COUNTS: dict[int, int] = {
    1: 47,
    2: 72,
    3: 43,
    4: 42,
    5: 29,
    6: 47,
    7: 30,
    8: 28,
    9: 34,
    10: 42,
    11: 55,
    12: 20,
    13: 34,  # classic 700-verse numbering (some editions print 35)
    14: 27,
    15: 20,
    16: 24,
    17: 28,
    18: 78,
}

ALLOWED_NODE_TYPES = frozenset(
    {
        "VERSE",
        "SUMMARY",
        "COMMENTARY",
        "CONCEPT",
        "CHARACTER",
        "EVENT",
    }
)

ALLOWED_TOPICS = frozenset(
    {
        "karma",
        "duty",
        "dharma",
        "detachment",
        "devotion",
        "mind",
        "wisdom",
        "equanimity",
        "compassion",
        "liberation",
        "discipline",
        "surrender",
        "self",
        "desire",
        "anger",
        "yoga",
        "action",
        "right_action",
        "knowledge",
        "renunciation",
    }
)

ALLOWED_EMOTIONS = frozenset(
    {
        "anxiety",
        "fear",
        "fear_of_failure",
        "performance_pressure",
        "grief",
        "anger",
        "confusion",
        "hopelessness",
        "peace",
        "guilt",
        "shame",
        "loneliness",
        "overwhelm",
        "restlessness",
    }
)

ALLOWED_LIFE_DOMAINS = frozenset(
    {
        "career",
        "placements",
        "business",
        "family",
        "relationships",
        "studies",
        "health",
        "grief_loss",
        "spiritual_practice",
        "leadership",
        "money",
        "identity",
    }
)

ALLOWED_USER_INTENTS = frozenset(
    {
        "seeking_guidance",
        "seeking_encouragement",
        "seeking_meaning",
        "seeking_courage",
        "seeking_discipline",
        "seeking_forgiveness",
        "seeking_detachment",
        "seeking_peace",
    }
)

ALLOWED_VIRTUES = frozenset(
    {
        "discipline",
        "perseverance",
        "courage",
        "compassion",
        "humility",
        "patience",
        "honesty",
        "self_control",
        "equanimity",
        "devotion",
        "wisdom",
        "non_attachment",
    }
)

ALLOWED_SCRIPURES = frozenset({"bhagavad_gita"})
