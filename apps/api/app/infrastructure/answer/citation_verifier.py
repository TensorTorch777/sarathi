"""Answer-level citation verification."""

import re

from app.application.dto.answer import AnswerCitation
from app.application.dto.retrieval import RankedVerse
from app.core.logging import get_logger

logger = get_logger(__name__)

# Matches BG 2.47, Bg 2.47, BG2.47, chapter 2 verse 47 (normalized separately).
_CITATION_RE = re.compile(
    r"\bBG\s*(\d{1,2})\s*[.:]\s*(\d{1,3})\b",
    flags=re.IGNORECASE,
)


class AnswerCitationVerifier:
    """Keep only citations that appear in the retrieved, verified evidence set."""

    def verify(
        self,
        answer: str,
        verses: list[RankedVerse],
    ) -> tuple[str, list[AnswerCitation], list[str]]:
        """Strip unverifiable citations and return structured kept citations."""
        allowed: dict[str, RankedVerse] = {}
        for verse in verses:
            if not verse.verified:
                continue
            key = f"{verse.chapter}.{verse.verse_number}"
            allowed[key] = verse
            allowed[verse.citation.upper().replace(" ", "")] = verse

        kept: list[AnswerCitation] = []
        removed: list[str] = []
        seen: set[str] = set()

        def _replace(match: re.Match[str]) -> str:
            chapter = int(match.group(1))
            verse_number = int(match.group(2))
            key = f"{chapter}.{verse_number}"
            label = f"BG {chapter}.{verse_number}"
            verse = allowed.get(key)
            if verse is None:
                removed.append(label)
                logger.warning("answer_citation_removed", citation=label)
                return ""
            if key not in seen:
                seen.add(key)
                kept.append(
                    AnswerCitation(
                        citation=label,
                        chapter=chapter,
                        verse_number=verse_number,
                        verse_id=verse.verse_id,
                        translation=verse.translation,
                    ),
                )
            return label

        cleaned = _CITATION_RE.sub(_replace, answer)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

        # If the model cited nothing valid but we have evidence, append canonical citations.
        if not kept and verses:
            appendix = "\n\nReferences: " + ", ".join(v.citation for v in verses if v.verified)
            cleaned = (cleaned + appendix).strip()
            for verse in verses:
                if not verse.verified:
                    continue
                kept.append(
                    AnswerCitation(
                        citation=verse.citation,
                        chapter=verse.chapter,
                        verse_number=verse.verse_number,
                        verse_id=verse.verse_id,
                        translation=verse.translation,
                    ),
                )

        return cleaned, kept, removed
