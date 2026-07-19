"""
Sarathi Canonical Corpus — schema, validation, and build tooling.

This package is the knowledge *product* layer. It does not migrate databases
or index Qdrant. Humans curate JSON; the validator guards quality.
"""

from app.corpus.builder import CorpusBuilder, CorpusBuildResult
from app.corpus.schema import (
    CanonicalCorpusFile,
    CanonicalKnowledgeNode,
    CommentaryEdition,
    CorpusManifestFile,
    Locator,
    TranslationEdition,
)
from app.corpus.validator import CorpusIssue, CorpusValidationReport, CorpusValidator

__all__ = [
    "CanonicalCorpusFile",
    "CanonicalKnowledgeNode",
    "CorpusManifestFile",
    "Locator",
    "TranslationEdition",
    "CommentaryEdition",
    "CorpusValidator",
    "CorpusValidationReport",
    "CorpusIssue",
    "CorpusBuilder",
    "CorpusBuildResult",
]
