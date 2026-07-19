"""Shared filter matching for sparse retrieval and corpus loading."""

from app.application.dto.retrieval import RetrievalFilters
from app.domain.entities import Verse


def verse_matches_filters(verse: Verse, filters: RetrievalFilters) -> bool:
    """Return True when a verse satisfies all provided filters."""
    if filters.chapters and verse.chapter not in filters.chapters:
        return False
    if filters.chapter_min is not None and verse.chapter < filters.chapter_min:
        return False
    if filters.chapter_max is not None and verse.chapter > filters.chapter_max:
        return False
    if filters.translation_source and verse.translation_source != filters.translation_source:
        return False
    if filters.emotions:
        verse_emotions = {e.lower() for e in verse.emotions}
        if not verse_emotions.intersection({e.lower() for e in filters.emotions}):
            return False
    if filters.topics:
        verse_topics = {t.lower() for t in verse.topics}
        if not verse_topics.intersection({t.lower() for t in filters.topics}):
            return False
    return True


def build_qdrant_filter(filters: RetrievalFilters) -> dict | None:
    """Build a Qdrant filter payload dict from retrieval filters."""
    must: list[dict] = []

    if filters.chapters:
        must.append({"key": "chapter", "match": {"any": list(filters.chapters)}})
    if filters.chapter_min is not None or filters.chapter_max is not None:
        rng: dict[str, int] = {}
        if filters.chapter_min is not None:
            rng["gte"] = filters.chapter_min
        if filters.chapter_max is not None:
            rng["lte"] = filters.chapter_max
        must.append({"key": "chapter", "range": rng})
    if filters.translation_source:
        must.append(
            {"key": "translation_source", "match": {"value": filters.translation_source}},
        )
    if filters.emotions:
        must.append({"key": "emotions", "match": {"any": [e.lower() for e in filters.emotions]}})
    if filters.topics:
        must.append({"key": "topics", "match": {"any": [t.lower() for t in filters.topics]}})

    if not must:
        return None
    return {"must": must}
