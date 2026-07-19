"""Cross-encoder reranking with lexical fallback."""

from app.application.dto.retrieval import RankedVerse
from app.core.logging import get_logger
from app.infrastructure.retrieval.sparse.bm25 import tokenize

logger = get_logger(__name__)


class CrossEncoderReranker:
    """Rerank candidates with a sentence-transformers CrossEncoder model."""

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "sentence-transformers is required for cross_encoder backend. "
                "Install with: poetry install --with ml",
            ) from exc
        logger.info("loading_cross_encoder", model=self._model_name)
        self._model = CrossEncoder(self._model_name)

    async def rerank(
        self,
        query: str,
        candidates: list[RankedVerse],
        *,
        top_k: int,
    ) -> list[RankedVerse]:
        """Score (query, verse) pairs and return top_k."""
        if not candidates:
            return []
        self._load()
        assert self._model is not None
        pairs = [(query, f"{c.citation}. {c.translation}") for c in candidates]
        scores = self._model.predict(pairs)
        for candidate, score in zip(candidates, scores, strict=True):
            candidate.rerank_score = float(score)
        candidates.sort(key=lambda item: item.rerank_score, reverse=True)
        return candidates[:top_k]


class LexicalCrossEncoderReranker:
    """Lightweight pair scorer used when ML deps/models are unavailable.

    Mimics cross-encoder pair scoring with query–document token overlap plus
    RRF prior. Suitable for tests and local bootstrapping; production should
    set RERANKER_BACKEND=cross_encoder.
    """

    async def rerank(
        self,
        query: str,
        candidates: list[RankedVerse],
        *,
        top_k: int,
    ) -> list[RankedVerse]:
        """Score candidates with lexical overlap informed by fusion prior."""
        query_tokens = set(tokenize(query))
        for candidate in candidates:
            doc_tokens = set(tokenize(f"{candidate.translation} {candidate.commentary or ''}"))
            overlap = len(query_tokens & doc_tokens)
            coverage = overlap / max(len(query_tokens), 1)
            candidate.rerank_score = coverage + (0.25 * candidate.rrf_score)
        candidates.sort(key=lambda item: item.rerank_score, reverse=True)
        return candidates[:top_k]
