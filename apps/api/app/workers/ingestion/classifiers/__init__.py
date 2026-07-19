"""Swappable metadata classifiers for knowledge ingestion."""

from app.workers.ingestion.classifiers.nulls import (
    NullEmotionClassifier,
    NullIntentClassifier,
    NullKeywordExtractor,
    NullLifeDomainClassifier,
    NullRelatedVerseResolver,
    NullTopicClassifier,
    NullVirtueClassifier,
    NullWisdomGraphBuilder,
)

__all__ = [
    "NullTopicClassifier",
    "NullEmotionClassifier",
    "NullKeywordExtractor",
    "NullVirtueClassifier",
    "NullLifeDomainClassifier",
    "NullIntentClassifier",
    "NullRelatedVerseResolver",
    "NullWisdomGraphBuilder",
]
