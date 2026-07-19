"""
Sarathi Canonical Corpus — JSON schema (Pydantic).

Two layers
----------
Layer 1 — ``authentic``
  Faithful scripture extract (Sanskrit, optional transliteration,
  source translations/commentaries). Never invents summaries or tags.

Layer 2 — ``enriched``
  Sarathi Intelligence overlay: summary, topics, emotions, practices,
  reflection questions, related nodes. Human-curated; never LLM-invented
  at import time.

Multi-edition translations are first-class so users can later choose
Mukundananda / Easwaran / Sivananda / Gambirananda, etc.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.corpus.taxonomies import ALLOWED_NODE_TYPES
from app.domain.enums.node_type import NodeType

_NODE_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_CITATION_RE = re.compile(r"^BG\s+\d+\.\d+$")

CorpusLayer = Literal["authentic", "enriched"]


class Locator(BaseModel):
    """Scripture-agnostic structural address."""

    model_config = ConfigDict(extra="forbid")

    chapter: int = Field(..., ge=1)
    verse: int = Field(..., ge=1)


class TranslationEdition(BaseModel):
    """One approved translation of a verse/node."""

    model_config = ConfigDict(extra="forbid")

    edition: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1)
    translator: str | None = None
    language: str = "en"
    license: str | None = None
    is_default: bool = False
    source: str | None = None


class CommentaryEdition(BaseModel):
    """One source commentary attached to a verse (Layer 1)."""

    model_config = ConfigDict(extra="forbid")

    edition: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1)
    author: str | None = None
    language: str = "en"
    license: str | None = None
    source: str | None = None


class CorpusManifestFile(BaseModel):
    """Manifest block inside a corpus JSON file (authoring-time)."""

    model_config = ConfigDict(extra="forbid")

    scripture: str
    edition: str
    language: str = "en"
    version: str
    corpus_layer: CorpusLayer = "enriched"
    description: str | None = None
    publisher: str | None = None
    license: str | None = None
    source: str | None = None


class CanonicalKnowledgeNode(BaseModel):
    """
    One KnowledgeNode in the canonical corpus JSON.

    Layer 1 (authentic): scripture text + provenance only.
    Layer 2 (enriched): adds Sarathi Intelligence fields.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=3, max_length=64)
    scripture: str
    node_type: Literal[
        "VERSE",
        "SUMMARY",
        "COMMENTARY",
        "CONCEPT",
        "CHARACTER",
        "EVENT",
    ]
    locator: Locator
    citation: str
    corpus_layer: CorpusLayer = "enriched"
    sanskrit: str = Field(..., min_length=1)
    transliteration: str | None = None
    translations: list[TranslationEdition] = Field(default_factory=list)
    commentaries: list[CommentaryEdition] = Field(default_factory=list)
    # Authoring shorthand — stripped after normalization
    translation: str | None = Field(default=None, exclude=True)
    commentary: str | None = None
    summary: str | None = None
    topics: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    life_domains: list[str] = Field(default_factory=list)
    user_intents: list[str] = Field(default_factory=list)
    virtues: list[str] = Field(default_factory=list)
    practice: list[str] = Field(default_factory=list)
    reflection_question: str | None = None
    related_nodes: list[str] = Field(default_factory=list)
    source_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def _id_slug(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not _NODE_ID_RE.match(cleaned):
            raise ValueError(
                "id must be lowercase slug (letters, digits, underscore), e.g. bg_2_47"
            )
        return cleaned

    @field_validator("citation")
    @classmethod
    def _citation_shape(cls, value: str) -> str:
        text = " ".join(value.split())
        if not _CITATION_RE.match(text):
            raise ValueError('citation must look like "BG 2.47"')
        return text

    @field_validator("node_type")
    @classmethod
    def _node_type_allowed(cls, value: str) -> str:
        if value not in ALLOWED_NODE_TYPES:
            raise ValueError(f"unsupported node_type: {value}")
        return value

    @field_validator(
        "topics",
        "emotions",
        "life_domains",
        "user_intents",
        "virtues",
        "related_nodes",
        "practice",
    )
    @classmethod
    def _strip_list(cls, values: list[str]) -> list[str]:
        return [v.strip() for v in values if v and v.strip()]

    @model_validator(mode="before")
    @classmethod
    def _coerce_translation_shorthand(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        translations = list(payload.get("translations") or [])
        shorthand = payload.get("translation")
        if shorthand and not translations:
            translations = [
                {
                    "edition": "sarathi_curated",
                    "text": shorthand,
                    "translator": "Sarathi editorial",
                    "license": "internal-curated",
                    "is_default": True,
                }
            ]
            payload["translations"] = translations
        if translations and "translation" in payload:
            payload.pop("translation", None)
        return payload

    @model_validator(mode="after")
    def _layer_and_identity_rules(self) -> CanonicalKnowledgeNode:
        expected = f"BG {self.locator.chapter}.{self.locator.verse}"
        if self.citation != expected:
            raise ValueError(f"citation {self.citation!r} must equal {expected!r}")

        expected_id = f"bg_{self.locator.chapter}_{self.locator.verse}"
        if self.node_type == "VERSE" and self.id != expected_id:
            raise ValueError(f"VERSE id {self.id!r} must equal {expected_id!r}")

        defaults = [t for t in self.translations if t.is_default]
        if len(defaults) > 1:
            raise ValueError("at most one translation may have is_default=true")
        if self.translations and not defaults:
            self.translations[0].is_default = True

        if self.corpus_layer == "enriched":
            if not self.translations:
                raise ValueError("enriched nodes require at least one translation")
            if not (self.summary and self.summary.strip()):
                raise ValueError("enriched nodes require summary")
            if not (self.reflection_question and self.reflection_question.strip()):
                raise ValueError("enriched nodes require reflection_question")
            has_commentary = bool(self.commentary and self.commentary.strip()) or bool(
                self.commentaries
            )
            if not has_commentary:
                raise ValueError("enriched nodes require commentary or commentaries")

        return self

    @property
    def default_translation(self) -> str:
        """Primary translation text for display / later ingest."""
        if not self.translations:
            return ""
        for item in self.translations:
            if item.is_default:
                return item.text
        return self.translations[0].text

    def to_domain_node_type(self) -> NodeType:
        """Map corpus literal to domain enum."""
        return NodeType(self.node_type.lower())


class CanonicalCorpusFile(BaseModel):
    """Root document for ``data/corpus/<scripture>/<file>.json``."""

    model_config = ConfigDict(extra="forbid")

    manifest: CorpusManifestFile
    nodes: list[CanonicalKnowledgeNode] = Field(..., min_length=1)
