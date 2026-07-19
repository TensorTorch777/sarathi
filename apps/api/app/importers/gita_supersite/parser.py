"""Parse Gita Supersite (Drupal) verse HTML into raw extract records."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import unescape

from app.importers.gita_supersite.constants import (
    COMMENTARY_HEADER_MAP,
    TRANSLATION_HEADER_MAP,
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_VERSE_MARK_RE = re.compile(r"।।\s*(\d+)\.(\d+)\s*।।")
_MUL_BLOCK_RE = re.compile(
    r"मूल\s*श्लोक[ः:]?</b></font></p>\s*"
    r"<p[^>]*><font[^>]*>(.*?)</font>",
    re.IGNORECASE | re.DOTALL,
)
_SECTION_RE = re.compile(
    r"<p[^>]*>\s*<font[^>]*>\s*<b>\s*([^<]+?)\s*</b>\s*</font>\s*</p>\s*"
    r"<p[^>]*>\s*<font[^>]*>\s*(.*?)\s*</font>\s*</p>",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(slots=True)
class RawTranslation:
    """One translation block from the source HTML."""

    header: str
    edition: str
    translator: str
    language: str
    text: str


@dataclass(slots=True)
class RawCommentary:
    """One commentary block from the source HTML."""

    header: str
    edition: str
    author: str
    language: str
    text: str


@dataclass(slots=True)
class RawVerseExtract:
    """Faithful extract for one verse (no Sarathi metadata)."""

    chapter: int
    verse: int
    sanskrit: str
    transliteration: str | None = None
    translations: list[RawTranslation] = field(default_factory=list)
    commentaries: list[RawCommentary] = field(default_factory=list)
    source_url: str | None = None
    warnings: list[str] = field(default_factory=list)


class GitaSupersiteParser:
    """Extract Sanskrit, translations, and commentaries from verse HTML."""

    def parse(
        self,
        html: str,
        *,
        chapter: int,
        verse: int,
        source_url: str | None = None,
    ) -> RawVerseExtract:
        """Parse one verse page. Does not invent missing fields."""
        warnings: list[str] = []
        sanskrit = self._extract_sanskrit(html, chapter, verse, warnings)
        translations, commentaries = self._extract_sections(html, warnings)

        mark = _VERSE_MARK_RE.search(html)
        if mark:
            marked_c, marked_v = int(mark.group(1)), int(mark.group(2))
            if marked_c != chapter or marked_v != verse:
                warnings.append(
                    f"verse marker ।।{marked_c}.{marked_v}।। != requested {chapter}.{verse}"
                )

        if not translations:
            warnings.append("no translations extracted")
        if not commentaries:
            warnings.append("no commentaries extracted")

        return RawVerseExtract(
            chapter=chapter,
            verse=verse,
            sanskrit=sanskrit,
            transliteration=None,  # Supersite page does not expose IAST reliably
            translations=translations,
            commentaries=commentaries,
            source_url=source_url,
            warnings=warnings,
        )

    def _extract_sanskrit(
        self,
        html: str,
        chapter: int,
        verse: int,
        warnings: list[str],
    ) -> str:
        match = _MUL_BLOCK_RE.search(html)
        if match:
            text = self._html_to_text(match.group(1))
        else:
            # Some pages omit the "मूल श्लोक" label but still print Devanagari + ।।c.v।।
            text = self._extract_sanskrit_near_marker(html, chapter, verse)
            if not text:
                warnings.append("sanskrit block not found")
                return ""
            warnings.append("sanskrit recovered via verse marker (no मूल श्लोक header)")
        # Drop trailing citation mark like ।।2.47।।
        text = _VERSE_MARK_RE.sub("", text).strip()
        text = re.sub(r"[।.]{2,}\s*$", "।", text).strip()
        if not text:
            warnings.append("sanskrit block empty after cleanup")
        return text

    def _extract_sanskrit_near_marker(
        self,
        html: str,
        chapter: int,
        verse: int,
    ) -> str:
        """Fallback: capture Devanagari immediately before ।।chapter.verse।।."""
        pattern = re.compile(
            rf"(<p[^>]*>\s*<font[^>]*>)(.*?)(।।\s*{chapter}\.{verse}\s*।।)",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(html)
        if not match:
            return ""
        return self._html_to_text(match.group(2))

    def _extract_sections(
        self,
        html: str,
        warnings: list[str],
    ) -> tuple[list[RawTranslation], list[RawCommentary]]:
        translations: list[RawTranslation] = []
        commentaries: list[RawCommentary] = []
        seen_editions: set[str] = set()

        for match in _SECTION_RE.finditer(html):
            header = _WS_RE.sub(" ", unescape(match.group(1))).strip()
            body = self._html_to_text(match.group(2))
            if not body:
                continue
            key = header.lower().strip()
            # Skip UI chrome
            if key in {"translations and commentaries"}:
                continue

            if key in TRANSLATION_HEADER_MAP:
                edition, translator, language = TRANSLATION_HEADER_MAP[key]
                if edition in seen_editions:
                    continue
                seen_editions.add(edition)
                translations.append(
                    RawTranslation(
                        header=header,
                        edition=edition,
                        translator=translator,
                        language=language,
                        text=body,
                    )
                )
                continue

            if key in COMMENTARY_HEADER_MAP:
                edition, author, language = COMMENTARY_HEADER_MAP[key]
                if edition in seen_editions:
                    continue
                seen_editions.add(edition)
                commentaries.append(
                    RawCommentary(
                        header=header,
                        edition=edition,
                        author=author,
                        language=language,
                        text=body,
                    )
                )
                continue

            # Unknown section — keep as warning, do not invent classification
            if "translation" in key or "commentary" in key:
                warnings.append(f"unmapped section header: {header}")

        return translations, commentaries

    @staticmethod
    def _html_to_text(fragment: str) -> str:
        text = fragment
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
        text = _TAG_RE.sub("", text)
        text = unescape(text)
        text = text.replace("\xa0", " ")
        lines = [_WS_RE.sub(" ", line).strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines).strip()
