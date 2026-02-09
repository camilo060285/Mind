"""Phase 8: Memory System - Usage Examples and Integration Guide."""

# Phase 8: Memory Management System
# ==================================

"""
The Memory system provides persistent storage for Mind agents with three tiers:
1. FileMemoryStore - JSON-based file persistence
2. VectorMemoryStore - Semantic search with embeddings
3. MemoryManager - High-level orchestration

Key Components:
- MemoryEntry: Atomic unit of memory (content, category, tags, metadata)
- BaseMemoryStore: Abstract interface for all storage implementations
- FileMemoryStore: File-based JSON storage
- VectorMemoryStore: Vector embeddings for semantic search
- MemoryManager: Unified interface combining both stores
- MemoryCommandHandler: CLI integration for memory operations
"""

# Example 1: Basic Memory Storage and Retrieval
# =============================================

from mind.memory import MemoryManager

# Initialize manager (auto-creates ~/.mind_memory directory)
memory = MemoryManager()

# Remember important facts
goal_id = memory.remember(
    content="Deploy the Mind system to production servers",
    category="goal",
    tags=["priority-high", "deployment"],
    metadata={"assigned_to": "system_architect"}
)

experience_id = memory.remember(
    content="Successfully optimized agent performance by 40%",
    category="experience",
    tags=["optimization", "completed"]
)

# Recall specific memory
recalled = memory.recall(goal_id)
print(f"Goal: {recalled.content}")
print(f"Tags: {recalled.tags}")


# Example 2: Semantic Search
# ==========================

# Store various related memories
memory.remember("Build distributed agent network", category="goal")
memory.remember("Implement load balancing algorithm", category="task")
memory.remember("Test network resilience with failover", category="task")

# Search using semantic similarity (if VectorMemoryStore available)
# Even if search term doesn't exact match, finds semantically similar memories
deployment_results = memory.search("system deployment", limit=5)
for entry in deployment_results:
    print(f"[{entry.category}] {entry.content}")


# Example 3: Category-based Organization
# ======================================

# Organize memories by category
goals = memory.recall_category("goal")
experiences = memory.recall_category("experience")

print(f"Active goals: {len(goals)}")
print(f"Completed experiences: {len(experiences)}")


# Example 4: Memory Tagging and Analysis
# =====================================

# Add tags to existing memories for organization
memory.tag_memory(goal_id, "critical")

# Search by tags
critical_items = memory.search_by_tags(["critical"])
print(f"Critical items: {len(critical_items)}")


# Example 5: Memory Statistics
# ===========================

stats = memory.get_stats()
print(f"Total memories: {stats['file_store']['total_entries']}")
print(f"By category: {stats['file_store']['by_category']}")
print(f"Vector search available: {stats['has_vector_store']}")


# Example 6: Export and Backup
# ============================

# Export all memories to JSON
memory.export_all("/tmp/mind_backup.json")

# Import memories from backup
new_memory = MemoryManager()
new_memory.import_all("/tmp/mind_backup.json")


# Example 7: CLI Integration (Phase 7-8)
# ====================================

# The interactive shell now includes memory commands:
# 
# > mind> help
# Available commands:
#   remember: Remember a fact or goal
#   recall: Recall a specific memory
#   search: Search memories
#   list: List memories by category
#   forget: Forget a memory
#   tag: Tag a memory
#   memory_stats: Show memory statistics
#   recent: Show recent memories
#   export: Export memories to file
#   import: Import memories from file
#
# Usage examples in CLI:
#
# > mind> remember goal "Deploy system to production"
# Remembered: abc12345... "Deploy system to production"
#
# > mind> search "deployment"
# Found 3 matching memories:
# 1. [goal] Deploy the Mind system to production servers
#    ID: abc12345...
#
# > mind> list goal
# GOAL (2 entries):
# 1. Deploy system to production
#    Tags: priority-high, critical
#
# > mind> memory_stats
# Memory Statistics:
# Total entries: 5
# By category:
#   - goal: 2
#   - experience: 1
#   - task: 2
# Vector store enabled: True
# Storage: /home/user/.mind_memory


# Example 8: Advanced - Memory Lifecycle Management
# ===============================================

# Update relevance score as memories prove valuable
memory.update_relevance(goal_id, relevance_score=0.95)

# Get recent memories (sorted by timestamp)
recent = memory.get_recent_memories(limit=5)

# Forget outdated memories
# memory.forget(outdated_id)

# Clear entire category if no longer needed
# deleted_count = memory.forget_category("deprecated")


# Example 9: Integration with Mind Agents
# ======================================

from mind.core.mind_orchestrator import MindOrchestrator

# Initialize orchestrator with memory manager
orchestrator = MindOrchestrator()

# Agents automatically store experiences in memory
goal = "Deploy Mind system"
result = orchestrator.execute(goal)

# Memories are persisted and available for future runs
previous_experiences = orchestrator.memory.recall_category("experience")
print(f"Learning from {len(previous_experiences)} previous experiences")


# Example 10: Memory Statistics and Monitoring
# ===========================================

# Track memory growth over time
stats = memory.get_stats()
for category, count in stats['file_store']['by_category'].items():
    print(f"{category}: {count} entries")

# Monitor recent activity
recent_30 = memory.get_recent_memories(limit=30)
print(f"Activities in recent period: {len(recent_30)}")


# Storage Locations
# ================
# 
# File-based storage: ~/.mind_memory/
#   - entries.json: All memory entries
#   - (one file per memory system instance)
#
# Vector storage: ~/.mind_memory_vectors/
#   - entries.json: Metadata
#   - vectors.npy: NumPy array of embeddings
#
# Shell history: ~/.mind_shell_history
#

# Configuration
# =============
#
# Custom storage paths:
from pathlib import Path
custom_memory = MemoryManager(
    file_store_dir=Path("/custom/path/file_store"),
    vector_store_dir=Path("/custom/path/vector_store"),
    enable_vector_search=True
)
#
# Disable vector search (if sentence-transformers not available):
lightweight_memory = MemoryManager(enable_vector_search=False)
