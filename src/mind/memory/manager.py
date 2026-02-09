"""Memory management orchestration layer."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mind.memory.file_store import FileMemoryStore
from mind.memory.memory_store import BaseMemoryStore, MemoryEntry
from mind.memory.vector_store import VectorMemoryStore


class MemoryManager:
    """High-level memory management with multiple backends."""

    def __init__(
        self,
        file_store_dir: Optional[Path] = None,
        vector_store_dir: Optional[Path] = None,
        enable_vector_search: bool = True,
    ):
        """Initialize memory manager.

        Args:
            file_store_dir: Directory for file-based storage
            vector_store_dir: Directory for vector storage
            enable_vector_search: Whether to enable semantic search
        """
        self.file_store = FileMemoryStore(file_store_dir)
        self.vector_store = None

        if enable_vector_search:
            try:
                self.vector_store = VectorMemoryStore(vector_store_dir)
            except Exception:
                # If vector store fails (missing dependencies), continue with file store only
                pass

        self.primary_store: BaseMemoryStore = self.vector_store or self.file_store

    def remember(
        self,
        content: Any,
        category: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a memory entry.

        Args:
            content: Memory content
            category: Memory category (e.g., "goal", "experience", "decision")
            tags: Optional tags for organization
            metadata: Optional metadata dictionary

        Returns:
            Entry ID
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}

        entry = MemoryEntry(
            id="",  # Will be generated
            content=content,
            category=category,
            timestamp=datetime.now().isoformat(),
            tags=tags,
            metadata=metadata,
            relevance_score=1.0,
        )

        entry_id = self.file_store.store(entry)

        # Also store in vector store if available
        if self.vector_store:
            self.vector_store.store(entry)

        return entry_id

    def recall(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID.

        Args:
            entry_id: Entry ID to retrieve

        Returns:
            Memory entry or None
        """
        return self.primary_store.retrieve(entry_id)

    def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories using semantic search (if available) or keyword search.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching entries
        """
        if self.vector_store:
            return self.vector_store.search(query, category, limit)
        return self.file_store.search(query, category, limit)

    def recall_category(self, category: str) -> List[MemoryEntry]:
        """Get all memories in a category.

        Args:
            category: Category name

        Returns:
            List of entries
        """
        return self.primary_store.get_by_category(category)

    def forget(self, entry_id: str) -> bool:
        """Delete a memory entry.

        Args:
            entry_id: Entry ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = self.file_store.delete(entry_id)
        if self.vector_store:
            self.vector_store.delete(entry_id)
        return result

    def forget_category(self, category: str) -> int:
        """Delete all memories in a category.

        Args:
            category: Category name

        Returns:
            Number of entries deleted
        """
        count = self.file_store.clear_category(category)
        if self.vector_store:
            self.vector_store.clear_category(category)
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "file_store": self.file_store.statistics(),
            "has_vector_store": self.vector_store is not None,
        }

        if self.vector_store:
            stats["vector_store"] = self.vector_store.statistics()

        return stats

    def export_all(self, filepath: str) -> None:
        """Export all memories to file.

        Args:
            filepath: Path to export to
        """
        self.primary_store.export(filepath)

    def import_all(self, filepath: str) -> None:
        """Import memories from file.

        Args:
            filepath: Path to import from
        """
        self.file_store.import_data(filepath)
        if self.vector_store:
            self.vector_store.import_data(filepath)

    def get_recent_memories(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[MemoryEntry]:
        """Get recent memories.

        Args:
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of recent entries sorted by timestamp (newest first)
        """
        if category:
            return self.primary_store.get_by_category(category)[:limit]

        # Return from all categories
        all_entries = list(
            {entry.id: entry for entry in self.file_store._entries.values()}.values()
        )
        all_entries.sort(key=lambda e: e.timestamp, reverse=True)
        return all_entries[:limit]

    def update_relevance(self, entry_id: str, relevance_score: float) -> bool:
        """Update the relevance score of a memory.

        Args:
            entry_id: Entry ID
            relevance_score: New relevance score (0-1)

        Returns:
            True if updated, False if not found
        """
        entry = self.recall(entry_id)
        if entry is None:
            return False

        entry.relevance_score = max(0.0, min(1.0, relevance_score))
        self.file_store.store(entry)
        if self.vector_store:
            self.vector_store.store(entry)
        return True

    def tag_memory(self, entry_id: str, tag: str) -> bool:
        """Add a tag to a memory entry.

        Args:
            entry_id: Entry ID
            tag: Tag to add

        Returns:
            True if tagged, False if not found
        """
        entry = self.recall(entry_id)
        if entry is None:
            return False

        if tag not in entry.tags:
            entry.tags.append(tag)
            self.file_store.store(entry)
            if self.vector_store:
                self.vector_store.store(entry)

        return True

    def search_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        """Search memories by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of entries with any of the tags
        """
        results = []
        for entry in self.file_store._entries.values():
            if any(tag in entry.tags for tag in tags):
                results.append(entry)

        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results
