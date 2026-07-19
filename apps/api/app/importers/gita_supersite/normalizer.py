"""Normalize raw Supersite extracts into Layer-1 CanonicalKnowledgeNode dicts."""

from __future__ import annotations

from typing import Any

from app.importers.gita_supersite.constants import (
    DEFAULT_TRANSLATION_PRIORITY,
    SOURCE_LABEL,
    SOURCE_NAME,
)
from app.importers.gita_supersite.parser import RawVerseExtract


class GitaSupersiteNormalizer:
    """
    Map faithful extracts → Sarathi Canonical Corpus schema (Layer 1).

    Does NOT generate summaries, topics, emotions, practices, or related nodes.
    """

    def normalize(
        self,
        extract: RawVerseExtract,
        *,
        include_copyrighted_text: bool,
        sanskrit_only: bool,
    ) -> dict[str, Any]:
        """Return a node dict suitable for CanonicalKnowledgeNode(authentic)."""
        translations: list[dict[str, Any]] = []
        commentaries: list[dict[str, Any]] = []

        if include_copyrighted_text and not sanskrit_only:
            ordered = sorted(
                extract.translations,
                key=lambda t: (
                    DEFAULT_TRANSLATION_PRIORITY.index(t.edition)
                    if t.edition in DEFAULT_TRANSLATION_PRIORITY
                    else 99,
                    t.edition,
                ),
            )
            for index, item in enumerate(ordered):
                translations.append(
                    {
                        "edition": item.edition,
                        "text": item.text,
                        "translator": item.translator,
                        "language": item.language,
                        "license": "source-publisher-copyright",
                        "is_default": index == 0 and item.language == "en",
                        "source": SOURCE_NAME,
                    }
                )
            # Ensure one default among English if present
            if translations and not any(t.get("is_default") for t in translations):
                for item in translations:
                    if item.get("language") == "en":
                        item["is_default"] = True
                        break
                else:
                    translations[0]["is_default"] = True

            for item in extract.commentaries:
                commentaries.append(
                    {
                        "edition": item.edition,
                        "text": item.text,
                        "author": item.author,
                        "language": item.language,
                        "license": "source-publisher-copyright",
                        "source": SOURCE_NAME,
                    }
                )

        return {
            "id": f"bg_{extract.chapter}_{extract.verse}",
            "scripture": "bhagavad_gita",
            "node_type": "VERSE",
            "corpus_layer": "authentic",
            "locator": {"chapter": extract.chapter, "verse": extract.verse},
            "citation": f"BG {extract.chapter}.{extract.verse}",
            "sanskrit": extract.sanskrit,
            "transliteration": extract.transliteration,
            "translations": translations,
            "commentaries": commentaries,
            "commentary": None,
            "summary": None,
            "topics": [],
            "emotions": [],
            "life_domains": [],
            "user_intents": [],
            "virtues": [],
            "practice": [],
            "reflection_question": None,
            "related_nodes": [],
            "source_metadata": {
                "source": SOURCE_NAME,
                "source_label": SOURCE_LABEL,
                "source_url": extract.source_url,
                "parser_warnings": list(extract.warnings),
                "include_copyrighted_text": include_copyrighted_text and not sanskrit_only,
            },
        }

    def build_corpus_document(
        self,
        nodes: list[dict[str, Any]],
        *,
        include_copyrighted_text: bool,
        sanskrit_only: bool,
        version: str = "0.1.0-authentic",
    ) -> dict[str, Any]:
        """Wrap nodes in a CanonicalCorpusFile envelope."""
        mode = "sanskrit_only" if sanskrit_only or not include_copyrighted_text else "full_extract"
        return {
            "manifest": {
                "scripture": "bhagavad_gita",
                "edition": f"gita_supersite_{mode}",
                "language": "sa" if mode == "sanskrit_only" else "multi",
                "version": version,
                "corpus_layer": "authentic",
                "description": (
                    "Layer 1 authentic extract from Gita Supersite. "
                    "No Sarathi Intelligence metadata. "
                    "Translations/commentaries included only when license-acknowledged."
                ),
                "publisher": SOURCE_LABEL,
                "license": (
                    "sanskrit-public-domain; translations require publisher permission"
                    if mode == "sanskrit_only"
                    else "mixed — see SOURCE_LICENSE.md; publisher copyrights apply"
                ),
                "source": SOURCE_NAME,
            },
            "nodes": nodes,
        }
