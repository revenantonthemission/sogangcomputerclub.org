"""
Abstract Base Repository Interface.
"""
from typing import Generic, TypeVar, List, Optional
from abc import ABC, abstractmethod

T = TypeVar("T")
K = TypeVar("K")

class BaseRepository(ABC, Generic[T, K]):
    """
    Abstract base repository defining standard CRUD operations.
    T: The entity type (e.g., Memo)
    K: The primary key type (e.g., int)
    """

    @abstractmethod
    async def get(self, id: K) -> Optional[T]:
        """Get an entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def create(self, obj_in: dict) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, id: K, obj_in: dict) -> Optional[T]:
        """Update an entity."""
        pass

    @abstractmethod
    async def delete(self, id: K) -> bool:
        """Delete an entity."""
        pass
