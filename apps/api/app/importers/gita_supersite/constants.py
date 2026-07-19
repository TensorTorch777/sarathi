"""Constants for the IIT Kanpur / Gita Supersite importer."""

from __future__ import annotations

from app.corpus.taxonomies import GITA_VERSE_COUNTS

# Legacy Drupal viewer (stable HTML verse pages). New SPA is JS-only.
DEFAULT_BASE_URL = "https://old.gitasupersite.in"

# Query flags enabling English translations + major commentaries.
# See acknowledgement page: copyrights remain with original publishers.
DEFAULT_FIELD_FLAGS: dict[str, str] = {
    "choose": "1",
    "language": "dv",
    # English translations
    "etpurohit": "1",
    "etsiva": "1",
    "etgb": "1",
    "etadi": "1",
    "etssa": "1",
    # English translation of Shankara commentary
    "setgb": "1",
    # Sanskrit commentaries
    "scsh": "1",
    "scang": "1",
    # Hindi translations (captured as non-English translation editions)
    "httyn": "1",
    "htrskd": "1",
    "htshg": "1",
}

SOURCE_NAME = "gita_supersite"
SOURCE_LABEL = "Gita Supersite (IIT Kanpur / gitasupersite)"

EXPECTED_VERSE_TOTAL = sum(GITA_VERSE_COUNTS.values())  # 700

# Map header phrases → stable edition slugs
TRANSLATION_HEADER_MAP: dict[str, tuple[str, str, str]] = {
    # slug, translator, language
    "english translation by swami sivananda": ("sivananda", "Swami Sivananda", "en"),
    "english translation by swami gambirananda": (
        "gambirananda",
        "Swami Gambirananda",
        "en",
    ),
    "english translation by swami adidevananda": (
        "adidevananda",
        "Swami Adidevananda",
        "en",
    ),
    "english translation by by dr. s. sankaranarayan": (
        "sankaranarayan",
        "Dr. S. Sankaranarayan",
        "en",
    ),
    "english translation by dr. s. sankaranarayan": (
        "sankaranarayan",
        "Dr. S. Sankaranarayan",
        "en",
    ),
    "english translation by shri purohit swami": (
        "purohit",
        "Shri Purohit Swami",
        "en",
    ),
    "english translation by purohit swami": ("purohit", "Shri Purohit Swami", "en"),
    "hindi translation by swami tejomayananda": (
        "tejomayananda_hi",
        "Swami Tejomayananda",
        "hi",
    ),
    "hindi translation by swami ramsukhdas": (
        "ramsukhdas_hi",
        "Swami Ramsukhdas",
        "hi",
    ),
}

COMMENTARY_HEADER_MAP: dict[str, tuple[str, str, str]] = {
    "sanskrit commentary by sri shankaracharya": (
        "shankaracharya_sa",
        "Sri Shankaracharya",
        "sa",
    ),
    "sanskrit commentary by sri abhinavgupta": (
        "abhinavagupta_sa",
        "Sri Abhinavagupta",
        "sa",
    ),
    "english translation of sri shankaracharya's sanskrit commentary by swami gambirananda": (
        "shankaracharya_en_gambirananda",
        "Swami Gambirananda (tr. of Shankara)",
        "en",
    ),
    "hindi translation of sri shankaracharya's sanskrit commentary by sri harikrishnadas goenka": (
        "shankaracharya_hi_goenka",
        "Sri Harikrishnadas Goenka (tr. of Shankara)",
        "hi",
    ),
}

DEFAULT_TRANSLATION_PRIORITY = (
    "sivananda",
    "gambirananda",
    "purohit",
    "adidevananda",
    "sankaranarayan",
)
