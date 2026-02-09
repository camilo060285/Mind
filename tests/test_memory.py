"""Tests for memory management system."""

import tempfile
from pathlib import Path

import pytest

from mind.memory import FileMemoryStore, MemoryEntry, MemoryManager, VectorMemoryStore


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_create_entry(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(
            id="test-1",
            content="Test content",
            category="goal",
            tags=["important"],
            metadata={"source": "test"},
        )
        assert entry.id == "test-1"
        assert entry.content == "Test content"
        assert entry.category == "goal"
        assert entry.tags == ["important"]
        assert entry.metadata["source"] == "test"

    def test_entry_defaults(self):
        """Test default values in memory entry."""
        entry = MemoryEntry(id="test-2", content="Test", category="experience")
        assert entry.tags == []
        assert entry.metadata == {}
        assert entry.relevance_score == 1.0


class TestFileMemoryStore:
    """Tests for file-based memory store."""

    @pytest.fixture
    def temp_store(self):
        """Create temporary memory store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileMemoryStore(Path(tmpdir))
            yield store

    def test_store_and_retrieve(self, temp_store):
        """Test storing and retrieving entries."""
        entry = MemoryEntry(id="", content="Test content", category="goal")
        entry_id = temp_store.store(entry)

        retrieved = temp_store.retrieve(entry_id)
        assert retrieved is not None
        assert retrieved.content == "Test content"
        assert retrieved.category == "goal"

    def test_search_by_content(self, temp_store):
        """Test searching memories by content."""
        temp_store.store(MemoryEntry(id="", content="Deploy system", category="goal"))
        temp_store.store(
            MemoryEntry(id="", content="Test application", category="goal")
        )

        results = temp_store.search("deploy", limit=5)
        assert len(results) == 1
        assert "deploy" in results[0].content.lower()

    def test_search_by_tags(self, temp_store):
        """Test searching memories by tags."""
        temp_store.store(
            MemoryEntry(
                id="",
                content="Goal 1",
                category="goal",
                tags=["priority-high"],
            )
        )
        temp_store.store(
            MemoryEntry(
                id="",
                content="Goal 2",
                category="goal",
                tags=["priority-low"],
            )
        )

        results = temp_store.search("priority-high", limit=5)
        assert len(results) >= 1

    def test_get_by_category(self, temp_store):
        """Test retrieving entries by category."""
        temp_store.store(MemoryEntry(id="", content="Goal 1", category="goal"))
        temp_store.store(MemoryEntry(id="", content="Goal 2", category="goal"))
        temp_store.store(
            MemoryEntry(id="", content="Experience 1", category="experience")
        )

        goals = temp_store.get_by_category("goal")
        assert len(goals) == 2
        assert all(e.category == "goal" for e in goals)

    def test_delete_entry(self, temp_store):
        """Test deleting an entry."""
        entry_id = temp_store.store(MemoryEntry(id="", content="Test", category="goal"))
        assert temp_store.delete(entry_id) is True
        assert temp_store.retrieve(entry_id) is None
        assert temp_store.delete(entry_id) is False

    def test_clear_category(self, temp_store):
        """Test clearing a category."""
        temp_store.store(MemoryEntry(id="", content="Goal 1", category="goal"))
        temp_store.store(MemoryEntry(id="", content="Goal 2", category="goal"))
        temp_store.store(
            MemoryEntry(id="", content="Experience 1", category="experience")
        )

        count = temp_store.clear_category("goal")
        assert count == 2
        assert len(temp_store.get_by_category("goal")) == 0
        assert len(temp_store.get_by_category("experience")) == 1

    def test_statistics(self, temp_store):
        """Test getting statistics."""
        temp_store.store(MemoryEntry(id="", content="Goal 1", category="goal"))
        temp_store.store(
            MemoryEntry(id="", content="Experience 1", category="experience")
        )

        stats = temp_store.statistics()
        assert stats["total_entries"] == 2
        assert stats["by_category"]["goal"] == 1
        assert stats["by_category"]["experience"] == 1

    def test_export_and_import(self):
        """Test exporting and importing data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store1 = FileMemoryStore(Path(tmpdir) / "store1")

            entry_id = store1.store(
                MemoryEntry(
                    id="",
                    content="Test content",
                    category="goal",
                    tags=["test"],
                )
            )

            export_file = Path(tmpdir) / "export.json"
            store1.export(str(export_file))

            # Create new store and import
            store2 = FileMemoryStore(Path(tmpdir) / "store2")
            store2.import_data(str(export_file))

            # Verify import
            imported = store2.retrieve(entry_id)
            assert imported is not None
            assert imported.content == "Test content"
            assert "test" in imported.tags

    def test_persistence(self):
        """Test that data persists between store instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_dir = Path(tmpdir) / "persistent"

            # Store data
            store1 = FileMemoryStore(store_dir)
            entry_id = store1.store(
                MemoryEntry(id="", content="Persistent", category="goal")
            )

            # Load in new instance
            store2 = FileMemoryStore(store_dir)
            retrieved = store2.retrieve(entry_id)
            assert retrieved is not None
            assert retrieved.content == "Persistent"


class TestVectorMemoryStore:
    """Tests for vector-based memory store."""

    @pytest.fixture
    def temp_vector_store(self):
        """Create temporary vector memory store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorMemoryStore(Path(tmpdir))
            yield store

    def test_store_and_retrieve(self, temp_vector_store):
        """Test storing and retrieving with embeddings."""
        entry = MemoryEntry(
            id="", content="Test content for embedding", category="goal"
        )
        entry_id = temp_vector_store.store(entry)

        retrieved = temp_vector_store.retrieve(entry_id)
        assert retrieved is not None
        assert retrieved.content == "Test content for embedding"

    def test_semantic_search(self, temp_vector_store):
        """Test semantic search capability."""
        temp_vector_store.store(
            MemoryEntry(id="", content="Deploy system to production", category="goal")
        )
        temp_vector_store.store(
            MemoryEntry(id="", content="Write unit tests", category="task")
        )
        temp_vector_store.store(
            MemoryEntry(id="", content="Launch application server", category="goal")
        )

        # Search for deployment-related
        results = temp_vector_store.search("deployment", limit=5)
        assert len(results) > 0

    def test_get_by_category(self, temp_vector_store):
        """Test retrieving entries by category."""
        temp_vector_store.store(MemoryEntry(id="", content="Goal 1", category="goal"))
        temp_vector_store.store(MemoryEntry(id="", content="Goal 2", category="goal"))
        temp_vector_store.store(
            MemoryEntry(id="", content="Experience 1", category="experience")
        )

        goals = temp_vector_store.get_by_category("goal")
        assert len(goals) == 2

    def test_delete_entry_vectors(self, temp_vector_store):
        """Test deleting entries with vector cleanup."""
        entry_id = temp_vector_store.store(
            MemoryEntry(id="", content="Test", category="goal")
        )
        assert temp_vector_store.delete(entry_id) is True
        assert temp_vector_store.retrieve(entry_id) is None

    def test_statistics(self, temp_vector_store):
        """Test vector store statistics."""
        temp_vector_store.store(MemoryEntry(id="", content="Goal 1", category="goal"))

        stats = temp_vector_store.statistics()
        assert stats["total_entries"] == 1
        assert stats["embedding_dim"] > 0


class TestMemoryManager:
    """Tests for memory manager orchestration."""

    @pytest.fixture
    def manager(self):
        """Create memory manager with temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(
                file_store_dir=Path(tmpdir) / "file",
                vector_store_dir=Path(tmpdir) / "vector",
                enable_vector_search=False,  # Skip sentence transformers for tests
            )
            yield manager

    def test_remember_and_recall(self, manager):
        """Test remembering and recalling memories."""
        entry_id = manager.remember(
            content="Test goal",
            category="goal",
            tags=["important"],
        )

        recalled = manager.recall(entry_id)
        assert recalled is not None
        assert recalled.content == "Test goal"
        assert "important" in recalled.tags

    def test_search_memories(self, manager):
        """Test searching memories."""
        manager.remember("Deploy system", category="goal")
        manager.remember("Test application", category="task")

        results = manager.search("deploy")
        assert len(results) >= 1

    def test_recall_category(self, manager):
        """Test recalling by category."""
        manager.remember("Goal 1", category="goal")
        manager.remember("Goal 2", category="goal")
        manager.remember("Experience 1", category="experience")

        goals = manager.recall_category("goal")
        assert len(goals) == 2

    def test_forget_entry(self, manager):
        """Test forgetting an entry."""
        entry_id = manager.remember("Test", category="goal")
        assert manager.forget(entry_id) is True
        assert manager.recall(entry_id) is None

    def test_forget_category(self, manager):
        """Test forgetting a category."""
        manager.remember("Goal 1", category="goal")
        manager.remember("Goal 2", category="goal")

        count = manager.forget_category("goal")
        assert count == 2

    def test_get_stats(self, manager):
        """Test getting statistics."""
        manager.remember("Memory 1", category="goal")
        manager.remember("Memory 2", category="experience")

        stats = manager.get_stats()
        assert stats["file_store"]["total_entries"] == 2

    def test_update_relevance(self, manager):
        """Test updating relevance scores."""
        entry_id = manager.remember("Test", category="goal")
        assert manager.update_relevance(entry_id, 0.8) is True

        recalled = manager.recall(entry_id)
        assert recalled.relevance_score == 0.8

    def test_tag_memory(self, manager):
        """Test adding tags to memories."""
        entry_id = manager.remember("Test", category="goal", tags=["a"])
        assert manager.tag_memory(entry_id, "b") is True

        recalled = manager.recall(entry_id)
        assert "a" in recalled.tags
        assert "b" in recalled.tags

    def test_search_by_tags(self, manager):
        """Test searching by tags."""
        manager.remember("Memory 1", category="goal", tags=["important"])
        manager.remember("Memory 2", category="goal", tags=["urgent"])

        results = manager.search_by_tags(["important"])
        assert len(results) >= 1

    def test_export_and_import(self):
        """Test exporting and importing with manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager1 = MemoryManager(Path(tmpdir) / "m1")
            entry_id = manager1.remember("Test content", category="goal", tags=["test"])

            export_file = Path(tmpdir) / "export.json"
            manager1.export_all(str(export_file))

            manager2 = MemoryManager(Path(tmpdir) / "m2")
            manager2.import_all(str(export_file))

            imported = manager2.recall(entry_id)
            assert imported is not None
            assert imported.content == "Test content"

    def test_get_recent_memories(self, manager):
        """Test getting recent memories."""
        manager.remember("Memory 1", category="goal")
        manager.remember("Memory 2", category="goal")
        manager.remember("Memory 3", category="experience")

        recent = manager.get_recent_memories(limit=2)
        assert len(recent) == 2

        recent_goals = manager.get_recent_memories(category="goal", limit=2)
        assert len(recent_goals) == 2
        assert all(e.category == "goal" for e in recent_goals)
