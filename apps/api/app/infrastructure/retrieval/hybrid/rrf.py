"""Reciprocal Rank Fusion for hybrid retrieval."""

from uuid import UUID


class ReciprocalRankFusion:
    """Fuse multiple ranked lists with Reciprocal Rank Fusion (RRF)."""

    def __init__(self, k: int = 60) -> None:
        self._k = k

    def fuse(
        self,
        sparse: list[tuple[UUID, float]],
        dense: list[tuple[UUID, float]],
        *,
        top_k: int,
    ) -> list[tuple[UUID, float]]:
        """Combine BM25 and dense rankings into a single RRF ranking."""
        scores: dict[UUID, float] = {}

        for rank, (verse_id, _) in enumerate(sparse, start=1):
            scores[verse_id] = scores.get(verse_id, 0.0) + 1.0 / (self._k + rank)

        for rank, (verse_id, _) in enumerate(dense, start=1):
            scores[verse_id] = scores.get(verse_id, 0.0) + 1.0 / (self._k + rank)

        fused = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return fused[:top_k]
