"""Edition and embedding version helpers (never overwrite prior vectors)."""

from __future__ import annotations

import hashlib
import re


_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([+-][A-Za-z0-9.-]+)?$")


def normalize_edition_slug(edition: str) -> str:
    """Stable edition identifier (lowercase, underscore)."""
    cleaned = edition.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_\-]+", "", cleaned)


def build_embedding_version(model_name: str, model_revision: str = "1") -> str:
    """
    Immutable embedding version tag.

    Changing the model or revision yields a new version; old Qdrant points remain.
    """
    model = model_name.strip().lower().replace(" ", "-")
    revision = model_revision.strip()
    return f"{model}@{revision}"


def content_checksum(*parts: str | None) -> str:
    """SHA-256 over non-empty text parts (provenance / manifest)."""
    hasher = hashlib.sha256()
    for part in parts:
        if not part:
            continue
        hasher.update(part.encode("utf-8"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def qdrant_point_id(node_id: str, embedding_version: str) -> str:
    """Point identity ties node + embedding version (no silent overwrite)."""
    safe_version = embedding_version.replace("/", "_").replace(" ", "_")
    return f"{node_id}:{safe_version}"


def assert_version_label(version: str) -> str:
    """Accept semver-like or free-form edition version labels."""
    label = version.strip()
    if not label:
        raise ValueError("version label must be non-empty")
    return label
