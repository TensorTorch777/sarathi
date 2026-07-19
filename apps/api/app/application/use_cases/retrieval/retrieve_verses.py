"""Hybrid RAG retrieval use case — orchestrates all pipeline stages."""

from app.application.dto.retrieval import (
    RankedVerse,
    RetrievalResult,
    RetrieveVersesQuery,
)
from app.application.ports import (
    CitationVerifierPort,
    ContextCompressorPort,
    DenseRetrieverPort,
    EmbedderPort,
    HybridFusionPort,
    QueryExpanderPort,
    RerankerPort,
    SparseRetrieverPort,
    VerseCorpusPort,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class RetrieveVersesUseCase:
    """Production retrieval pipeline ending in top-K verified Gita verses."""

    def __init__(
        self,
        *,
        corpus: VerseCorpusPort,
        query_expander: QueryExpanderPort,
        sparse: SparseRetrieverPort,
        dense: DenseRetrieverPort,
        embedder: EmbedderPort,
        fusion: HybridFusionPort,
        reranker: RerankerPort,
        compressor: ContextCompressorPort,
        verifier: CitationVerifierPort,
        bm25_top_k: int = 20,
        dense_top_k: int = 20,
        min_rerank_score: float = -10.0,
    ) -> None:
        self._corpus = corpus
        self._query_expander = query_expander
        self._sparse = sparse
        self._dense = dense
        self._embedder = embedder
        self._fusion = fusion
        self._reranker = reranker
        self._compressor = compressor
        self._verifier = verifier
        self._bm25_top_k = bm25_top_k
        self._dense_top_k = dense_top_k
        self._min_rerank_score = min_rerank_score

    async def execute(self, request: RetrieveVersesQuery) -> RetrievalResult:
        """Run expansion → hybrid retrieve → rerank → compress → verify."""
        query = request.query.strip()
        if not query:
            return RetrievalResult(
                query=query,
                expanded_queries=(),
                filters=request.filters,
                verses=(),
                stages={"error": "empty_query"},
            )

        # Stage 1 — Query expansion
        if request.expand_query:
            expanded = await self._query_expander.expand(query)
        else:
            expanded = [query]
        primary_query = expanded[0]

        # Stage 2 — filters are applied inside sparse/dense search
        filters = request.filters

        # Stage 3a — BM25 over each expansion (merge unique hits)
        sparse_merged: dict = {}
        for variant in expanded:
            hits = await self._sparse.search(
                variant,
                filters=filters,
                top_k=self._bm25_top_k,
            )
            for verse_id, score in hits:
                prev = sparse_merged.get(verse_id)
                if prev is None or score > prev:
                    sparse_merged[verse_id] = score
        sparse_ranked = sorted(sparse_merged.items(), key=lambda i: i[1], reverse=True)

        # Stage 3b — Dense retrieval (embed primary + best expansions)
        dense_merged: dict = {}
        embed_texts = expanded[:3]
        for text in embed_texts:
            vector = await self._embedder.embed_query(text)
            hits = await self._dense.search(
                vector,
                filters=filters,
                top_k=self._dense_top_k,
            )
            for verse_id, score in hits:
                prev = dense_merged.get(verse_id)
                if prev is None or score > prev:
                    dense_merged[verse_id] = score
        dense_ranked = sorted(dense_merged.items(), key=lambda i: i[1], reverse=True)

        # Stage 4 — Hybrid RRF fusion
        fused = self._fusion.fuse(
            sparse_ranked,
            dense_ranked,
            top_k=request.candidate_pool_size,
        )

        verse_map = await self._corpus.get_by_ids([verse_id for verse_id, _ in fused])
        bm25_lookup = dict(sparse_ranked)
        dense_lookup = dict(dense_ranked)

        candidates: list[RankedVerse] = []
        for verse_id, rrf_score in fused:
            verse = verse_map.get(verse_id)
            if verse is None:
                continue
            candidates.append(
                RankedVerse(
                    verse_id=verse.id,
                    chapter=verse.chapter,
                    verse_number=verse.verse_number,
                    citation=verse.citation,
                    sanskrit=verse.sanskrit,
                    translation=verse.translation,
                    transliteration=verse.transliteration,
                    commentary=verse.commentary,
                    topics=list(verse.topics),
                    emotions=list(verse.emotions),
                    bm25_score=float(bm25_lookup.get(verse_id, 0.0)),
                    dense_score=float(dense_lookup.get(verse_id, 0.0)),
                    rrf_score=float(rrf_score),
                ),
            )

        # Stage 5 — Cross-encoder rerank
        reranked = await self._reranker.rerank(
            primary_query,
            candidates,
            top_k=max(request.top_k * 2, request.top_k),
        )

        # Stage 6 — Context compression
        for item in reranked:
            item.compressed_context = self._compressor.compress(primary_query, item)

        # Stage 7 — Citation verification → top 5
        verified = await self._verifier.verify(
            reranked,
            min_rerank_score=self._min_rerank_score,
            top_k=request.top_k,
        )

        logger.info(
            "retrieval_completed",
            query=primary_query,
            expanded=len(expanded),
            sparse=len(sparse_ranked),
            dense=len(dense_ranked),
            fused=len(fused),
            verified=len(verified),
        )

        return RetrievalResult(
            query=primary_query,
            expanded_queries=tuple(expanded),
            filters=filters,
            verses=tuple(verified),
            stages={
                "query_expansion": len(expanded),
                "bm25_hits": len(sparse_ranked),
                "dense_hits": len(dense_ranked),
                "fused_candidates": len(fused),
                "reranked": len(reranked),
                "verified_top_k": len(verified),
            },
        )
