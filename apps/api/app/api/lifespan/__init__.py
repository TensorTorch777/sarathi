"""Application lifespan hooks."""

from app.api.lifespan.events import lifespan

__all__ = ["lifespan"]
