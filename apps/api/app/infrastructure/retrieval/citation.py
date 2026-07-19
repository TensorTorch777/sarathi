"""Citation verification against the canonical Gita corpus."""

from app.application.dto.retrieval import RankedVerse
from app.application.ports import VerseCorpusPort
from app.core.logging import get_logger

logger = get_logger(__name__)


class CorpusCitationVerifier:
    """Ensure every returned verse exists in Postgres with a valid citation."""

    def __init__(self, corpus: VerseCorpusPort) -> None:
        self._corpus = corpus

    async def verify(
        self,
        candidates: list[RankedVerse],
        *,
        min_rerank_score: float,
        top_k: int,
    ) -> list[RankedVerse]:
        """Filter fabrications / low-score hits and return at most top_k."""
        if not candidates:
            return []

        ids = [c.verse_id for c in candidates]
        canonical = await self._corpus.get_by_ids(ids)
        verified: list[RankedVerse] = []

        for candidate in candidates:
            if candidate.rerank_score < min_rerank_score:
                logger.info(
                    "citation_rejected_low_score",
                    citation=candidate.citation,
                    score=candidate.rerank_score,
                )
                continue

            verse = canonical.get(candidate.verse_id)
            if verse is None:
                logger.warning("citation_rejected_unknown_id", verse_id=str(candidate.verse_id))
                continue

            if (
                verse.chapter != candidate.chapter
                or verse.verse_number != candidate.verse_number
            ):
                logger.warning(
                    "citation_rejected_identity_mismatch",
                    verse_id=str(candidate.verse_id),
                )
                continue

            # Re-bind fields from canonical row — never trust unverified payload text alone.
            candidate.chapter = verse.chapter
            candidate.verse_number = verse.verse_number
            candidate.citation = verse.citation
            candidate.sanskrit = verse.sanskrit
            candidate.translation = verse.translation
            candidate.transliteration = verse.transliteration
            candidate.commentary = verse.commentary
            candidate.topics = list(verse.topics)
            candidate.emotions = list(verse.emotions)
            candidate.verified = True
            verified.append(candidate)

            if len(verified) >= top_k:
                break

        return verified
