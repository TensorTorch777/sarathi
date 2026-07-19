"""Context compression for grounded generation."""

import re

from app.application.dto.retrieval import RankedVerse

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class ExtractiveContextCompressor:
    """Keep citation identity plus query-relevant translation/commentary spans."""

    def compress(self, query: str, verse: RankedVerse) -> str:
        """Build a compact context string that always includes the citation."""
        query_terms = {t for t in re.findall(r"[a-z0-9']+", query.lower()) if len(t) > 2}
        lines = [
            f"Citation: {verse.citation}",
            f"Sanskrit: {verse.sanskrit}",
            f"Translation: {verse.translation}",
        ]

        if verse.commentary:
            selected = self._select_sentences(verse.commentary, query_terms, limit=2)
            if selected:
                lines.append(f"Commentary: {selected}")

        if verse.topics:
            lines.append(f"Topics: {', '.join(verse.topics)}")
        if verse.emotions:
            lines.append(f"Emotions: {', '.join(verse.emotions)}")

        return "\n".join(lines)

    @staticmethod
    def _select_sentences(text: str, query_terms: set[str], *, limit: int) -> str:
        sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
        if not sentences:
            return text[:400]

        scored: list[tuple[int, str]] = []
        for sentence in sentences:
            tokens = set(re.findall(r"[a-z0-9']+", sentence.lower()))
            overlap = len(tokens & query_terms)
            scored.append((overlap, sentence))

        scored.sort(key=lambda item: item[0], reverse=True)
        chosen = [sentence for score, sentence in scored[:limit] if score > 0]
        if not chosen:
            chosen = sentences[:1]
        return " ".join(chosen)
