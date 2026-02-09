"""File-based memory store implementation."""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from mind.memory.memory_store import BaseMemoryStore, MemoryEntry


class FileMemoryStore(BaseMemoryStore):
    """File-based memory storage using JSON."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize file-based memory store.

        Args:
            storage_dir: Directory to store memory files. Defaults to ~/.mind_memory
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mind_memory"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.entries_file = self.storage_dir / "entries.json"

        self._entries: Dict[str, MemoryEntry] = {}
        self._load_entries()

    def _load_entries(self) -> None:
        """Load entries from disk."""
        if self.entries_file.exists():
            try:
                with open(self.entries_file, "r") as f:
                    data = json.load(f)
                    self._entries = {
                        k: MemoryEntry(
                            id=v["id"],
                            content=v["content"],
                            category=v["category"],
                            timestamp=v.get("timestamp"),
                            tags=v.get("tags", []),
                            metadata=v.get("metadata", {}),
                            relevance_score=v.get("relevance_score", 1.0),
                        )
                        for k, v in data.items()
                    }
            except (json.JSONDecodeError, ValueError):
                self._entries = {}

    def _save_entries(self) -> None:
        """Save entries to disk."""
        data = {}
        for entry_id, entry in self._entries.items():
            data[entry_id] = {
                "id": entry.id,
                "content": entry.content,
                "category": entry.category,
                "timestamp": entry.timestamp,
                "tags": entry.tags,
                "metadata": entry.metadata,
                "relevance_score": entry.relevance_score,
            }

        with open(self.entries_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry.

        Args:
            entry: Memory entry to store

        Returns:
            Entry ID
        """
        if not entry.id:
            entry.id = str(uuid.uuid4())

        self._entries[entry.id] = entry
        self._save_entries()
        return entry.id

    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID.

        Args:
            entry_id: ID of entry to retrieve

        Returns:
            Memory entry or None if not found
        """
        return self._entries.get(entry_id)

    def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memory.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching entries sorted by relevance
        """
        results = []
        query_lower = query.lower()

        for entry in self._entries.values():
            # Apply category filter
            if category and entry.category != category:
                continue

            # Check if query matches content or tags
            content_str = str(entry.content).lower()
            if query_lower in content_str or any(
                query_lower in tag.lower() for tag in entry.tags
            ):
                results.append(entry)

        # Sort by relevance score (higher first)
        results.sort(key=lambda e: e.relevance_score, reverse=True)
        return results[:limit]

    def get_by_category(self, category: str) -> List[MemoryEntry]:
        """Get all entries in a category.

        Args:
            category: Category name

        Returns:
            List of entries sorted by timestamp (newest first)
        """
        entries = [e for e in self._entries.values() if e.category == category]
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry.

        Args:
            entry_id: ID of entry to delete

        Returns:
            True if deleted, False if not found
        """
        if entry_id in self._entries:
            del self._entries[entry_id]
            self._save_entries()
            return True
        return False

    def clear_category(self, category: str) -> int:
        """Clear all entries in a category.

        Args:
            category: Category name

        Returns:
            Number of entries deleted
        """
        to_delete = [
            entry_id
            for entry_id, entry in self._entries.items()
            if entry.category == category
        ]
        for entry_id in to_delete:
            del self._entries[entry_id]

        if to_delete:
            self._save_entries()

        return len(to_delete)

    def statistics(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dict with statistics
        """
        categories = {}
        for entry in self._entries.values():
            if entry.category not in categories:
                categories[entry.category] = 0
            categories[entry.category] += 1

        return {
            "total_entries": len(self._entries),
            "by_category": categories,
            "storage_location": str(self.storage_dir),
        }

    def export(self, filepath: str) -> None:
        """Export all memory to file.

        Args:
            filepath: Path to export to
        """
        export_file = Path(filepath)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for entry_id, entry in self._entries.items():
            data[entry_id] = {
                "id": entry.id,
                "content": entry.content,
                "category": entry.category,
                "timestamp": entry.timestamp,
                "tags": entry.tags,
                "metadata": entry.metadata,
                "relevance_score": entry.relevance_score,
            }

        with open(export_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def import_data(self, filepath: str) -> None:
        """Import memory from file.

        Args:
            filepath: Path to import from
        """
        import_file = Path(filepath)
        if not import_file.exists():
            raise FileNotFoundError(f"Import file not found: {filepath}")

        with open(import_file, "r") as f:
            data = json.load(f)
            for entry_id, entry_data in data.items():
                entry = MemoryEntry(
                    id=entry_data["id"],
                    content=entry_data["content"],
                    category=entry_data["category"],
                    timestamp=entry_data.get("timestamp"),
                    tags=entry_data.get("tags", []),
                    metadata=entry_data.get("metadata", {}),
                    relevance_score=entry_data.get("relevance_score", 1.0),
                )
                self._entries[entry_id] = entry

        self._save_entries()
