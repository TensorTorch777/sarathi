"""Base repository protocol for the repository pattern."""

from typing import Protocol, TypeVar

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT")


class Repository(Protocol[EntityT, IdT]):
    """Generic async repository contract.

    Concrete implementations live under ``infrastructure.db.repositories``.
    """

    async def get_by_id(self, entity_id: IdT) -> EntityT | None:
        """Fetch a single entity by identifier."""
        ...

    async def add(self, entity: EntityT) -> EntityT:
        """Persist a new entity."""
        ...

    async def delete(self, entity_id: IdT) -> bool:
        """Delete an entity by identifier. Returns True if deleted."""
        ...
