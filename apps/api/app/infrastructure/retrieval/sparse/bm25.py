"""Okapi BM25 sparse retriever over the in-memory Gita corpus."""

import re
from uuid import UUID

from rank_bm25 import BM25Okapi

from app.application.dto.retrieval import RetrievalFilters
from app.domain.entities import Verse
from app.infrastructure.retrieval.filters import verse_matches_filters

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokenizer for BM25."""
    return _TOKEN_RE.findall(text.lower())


class BM25SparseRetriever:
    """In-process BM25 index with metadata / emotion / topic filtering."""

    def __init__(self) -> None:
        self._verses: list[Verse] = []
        self._bm25: BM25Okapi | None = None
        self._tokenized: list[list[str]] = []

    async def rebuild(self, verses: list[Verse]) -> None:
        """Rebuild the BM25 index from canonical verses."""
        self._verses = list(verses)
        self._tokenized = [tokenize(v.searchable_text) for v in self._verses]
        self._bm25 = BM25Okapi(self._tokenized) if self._tokenized else None

    async def search(
        self,
        query: str,
        *,
        filters: RetrievalFilters,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """Score filtered verses with BM25 and return top_k."""
        if self._bm25 is None or not self._verses:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)
        ranked: list[tuple[UUID, float]] = []
        for verse, score in zip(self._verses, scores, strict=True):
            if score <= 0:
                continue
            if not verse_matches_filters(verse, filters):
                continue
            ranked.append((verse.id, float(score)))

        ranked.sort(key=lambda item: item[1], reverse=True)
        return ranked[:top_k]
