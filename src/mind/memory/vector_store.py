"""Vector-based memory store for semantic search."""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from mind.memory.memory_store import BaseMemoryStore, MemoryEntry


class VectorMemoryStore(BaseMemoryStore):
    """Vector-based memory store supporting semantic search."""

    def __init__(self, storage_dir: Optional[Path] = None, embedding_dim: int = 384):
        """Initialize vector memory store.

        Args:
            storage_dir: Directory to store memory files. Defaults to ~/.mind_memory_vectors
            embedding_dim: Dimension of embeddings (384 for MiniLM, 768 for BERT)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mind_memory_vectors"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.entries_file = self.storage_dir / "entries.json"
        self.vectors_file = self.storage_dir / "vectors.npy"
        self.embedding_dim = embedding_dim

        self._entries: Dict[str, MemoryEntry] = {}
        self._vectors: Dict[str, np.ndarray] = {}
        self._entry_ids: List[str] = []

        self._load_data()

        # Try to import sentence transformer for embeddings
        # Skip in test environment for speed
        import os

        if os.getenv("SKIP_EMBEDDER", "0") != "1":
            try:
                from sentence_transformers import SentenceTransformer

                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                self.embedder = None
        else:
            self.embedder = None

    def _embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.embedder is None:
            # Fallback: hash-based simple embedding
            return self._fallback_embedding(text)

        embedding = self.embedder.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Fallback embedding using hash values."""
        import hashlib

        # Generate deterministic vector from text hash
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # Repeat hash to reach embedding_dim
        embedding = np.frombuffer(
            (hash_bytes * ((self.embedding_dim // 32) + 1))[: self.embedding_dim],
            dtype=np.float32,
        )
        # Normalize
        embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
        return embedding

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> np.float32:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score between -1 and 1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return np.float32(0)

        return np.float32(dot_product / (norm1 * norm2))

    def _load_data(self) -> None:
        """Load entries and vectors from disk."""
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
                    self._entry_ids = list(self._entries.keys())
            except (json.JSONDecodeError, ValueError):
                self._entries = {}
                self._entry_ids = []

        if self.vectors_file.exists():
            try:
                loaded_vectors = np.load(self.vectors_file, allow_pickle=True).item()
                self._vectors = loaded_vectors
            except (ValueError, OSError):
                self._vectors = {}

    def _save_data(self) -> None:
        """Save entries and vectors to disk."""
        # Save entries
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

        # Save vectors (store as pickled object); cast to Any to satisfy type checkers
        if self._vectors:
            from typing import cast, Any

            np.save(self.vectors_file, cast(Any, self._vectors), allow_pickle=True)

    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry with embedding.

        Args:
            entry: Memory entry to store

        Returns:
            Entry ID
        """
        if not entry.id:
            entry.id = str(uuid.uuid4())

        self._entries[entry.id] = entry
        self._entry_ids.append(entry.id)

        # Generate embedding
        embedding = self._embed_text(str(entry.content))
        self._vectors[entry.id] = embedding

        self._save_data()
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
        """Search memory using semantic similarity.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum results

        Returns:
            List of matching entries sorted by semantic similarity
        """
        query_embedding = self._embed_text(query)
        similarities = []

        for entry_id, entry in self._entries.items():
            # Apply category filter
            if category and entry.category != category:
                continue

            # Get stored embedding
            if entry_id in self._vectors:
                stored_embedding = self._vectors[entry_id]
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                similarities.append((entry, similarity))

        # Sort by similarity (higher first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in similarities[:limit]]

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
            if entry_id in self._vectors:
                del self._vectors[entry_id]
            if entry_id in self._entry_ids:
                self._entry_ids.remove(entry_id)
            self._save_data()
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
            if entry_id in self._vectors:
                del self._vectors[entry_id]
            if entry_id in self._entry_ids:
                self._entry_ids.remove(entry_id)

        if to_delete:
            self._save_data()

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
            "embedding_dim": self.embedding_dim,
            "has_embedder": self.embedder is not None,
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
                self._entry_ids.append(entry_id)

                # Generate embedding
                embedding = self._embed_text(str(entry.content))
                self._vectors[entry_id] = embedding

        self._save_data()
