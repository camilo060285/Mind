"""Base memory store interface for Mind."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """A single memory entry."""

    id: str
    content: Any
    category: str  # "goal", "experience", "metric", "observation"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 1.0


class BaseMemoryStore(ABC):
    """Abstract base class for memory stores."""

    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry.

        Args:
            entry: Memory entry to store

        Returns:
            Entry ID
        """
        pass

    @abstractmethod
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID.

        Args:
            entry_id: ID of entry to retrieve

        Returns:
            Memory entry or None if not found
        """
        pass

    @abstractmethod
    def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memory.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching entries
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[MemoryEntry]:
        """Get all entries in a category.

        Args:
            category: Category name

        Returns:
            List of entries
        """
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry.

        Args:
            entry_id: ID of entry to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def clear_category(self, category: str) -> int:
        """Clear all entries in a category.

        Args:
            category: Category name

        Returns:
            Number of entries deleted
        """
        pass

    @abstractmethod
    def statistics(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dict with statistics
        """
        pass

    @abstractmethod
    def export(self, filepath: str) -> None:
        """Export all memory to file.

        Args:
            filepath: Path to export to
        """
        pass

    @abstractmethod
    def import_data(self, filepath: str) -> None:
        """Import memory from file.

        Args:
            filepath: Path to import from
        """
        pass
