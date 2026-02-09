"""Memory CLI commands for the interactive shell."""

from mind.memory import MemoryManager


class MemoryCommandHandler:
    """Handler for memory-related CLI commands."""

    def __init__(self, memory_manager: MemoryManager):
        """Initialize memory command handler.

        Args:
            memory_manager: Memory manager instance
        """
        self.memory = memory_manager

    def handle_remember(self, args: str) -> str:
        """Remember a fact or goal.

        Usage: remember <category> <content>
        Example: remember goal "Deploy system to production"

        Args:
            args: Command arguments

        Returns:
            Result message
        """
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return "Error: Usage: remember <category> <content>"

        category, content = parts[0], parts[1].strip().strip("\"'")
        entry_id = self.memory.remember(content, category)
        return f'Remembered: {entry_id[:8]}... "{content}"'

    def handle_recall(self, args: str) -> str:
        """Recall a specific memory.

        Usage: recall <entry_id>

        Args:
            args: Entry ID

        Returns:
            Memory entry details
        """
        entry_id = args.strip()
        if not entry_id:
            return "Error: Please provide an entry ID"

        entry = self.memory.recall(entry_id)
        if not entry:
            return f"Not found: {entry_id}"

        output = f"Entry: {entry.id}\n"
        output += f"Content: {entry.content}\n"
        output += f"Category: {entry.category}\n"
        output += f"Tags: {', '.join(entry.tags) if entry.tags else 'None'}\n"
        output += f"Relevance: {entry.relevance_score}\n"
        output += f"Timestamp: {entry.timestamp}"

        return output

    def handle_search(self, args: str) -> str:
        """Search memories.

        Usage: search <query> [limit]

        Args:
            args: Search query and optional limit

        Returns:
            Search results
        """
        parts = args.split()
        if not parts:
            return "Error: Please provide a search query"

        query = (
            " ".join(parts[:-1])
            if len(parts) > 1 and parts[-1].isdigit()
            else " ".join(parts)
        )
        limit = int(parts[-1]) if parts[-1].isdigit() else 10

        results = self.memory.search(query, limit=limit)
        if not results:
            return f'No memories found matching "{query}"'

        output = f"Found {len(results)} matching memories:\n"
        for i, entry in enumerate(results, 1):
            output += f"{i}. [{entry.category}] {entry.content[:60]}"
            if len(entry.content) > 60:
                output += "..."
            output += f"\n   ID: {entry.id[:8]}...\n"

        return output.rstrip()

    def handle_list_category(self, args: str) -> str:
        """List memories in a category.

        Usage: list <category>

        Args:
            args: Category name

        Returns:
            Category entries
        """
        category = args.strip()
        if not category:
            return "Error: Please provide a category"

        entries = self.memory.recall_category(category)
        if not entries:
            return f"No memories in category: {category}"

        output = f"{category.upper()} ({len(entries)} entries):\n"
        for i, entry in enumerate(entries, 1):
            output += f"{i}. {entry.content[:60]}"
            if len(entry.content) > 60:
                output += "..."
            output += f"\n   Tags: {', '.join(entry.tags) if entry.tags else 'None'}\n"

        return output.rstrip()

    def handle_forget(self, args: str) -> str:
        """Forget a specific memory.

        Usage: forget <entry_id>

        Args:
            args: Entry ID to delete

        Returns:
            Confirmation message
        """
        entry_id = args.strip()
        if not entry_id:
            return "Error: Please provide an entry ID"

        if self.memory.forget(entry_id):
            return f"Forgotten: {entry_id[:8]}..."
        return f"Not found: {entry_id}"

    def handle_tag(self, args: str) -> str:
        """Add a tag to a memory.

        Usage: tag <entry_id> <tag>

        Args:
            args: Entry ID and tag

        Returns:
            Confirmation message
        """
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return "Error: Usage: tag <entry_id> <tag>"

        entry_id, tag = parts[0], parts[1]
        if self.memory.tag_memory(entry_id, tag):
            return f"Tagged: {entry_id[:8]}... with '{tag}'"
        return f"Not found: {entry_id}"

    def handle_stats(self, args: str) -> str:
        """Show memory statistics.

        Args:
            args: Unused

        Returns:
            Statistics summary
        """
        stats = self.memory.get_stats()

        output = "Memory Statistics:\n"
        output += f"Total entries: {stats['file_store']['total_entries']}\n"

        if stats["file_store"]["by_category"]:
            output += "By category:\n"
            for category, count in stats["file_store"]["by_category"].items():
                output += f"  - {category}: {count}\n"

        output += f"Vector store enabled: {stats['has_vector_store']}\n"
        output += f"Storage: {stats['file_store']['storage_location']}"

        return output

    def handle_recent(self, args: str) -> str:
        """Show recent memories.

        Usage: recent [limit]

        Args:
            args: Optional limit (default 5)

        Returns:
            Recent memories
        """
        limit = 5
        if args.strip():
            try:
                limit = int(args.strip())
            except ValueError:
                return "Error: Limit must be a number"

        recent = self.memory.get_recent_memories(limit=limit)
        if not recent:
            return "No memories found"

        output = f"Recent memories ({len(recent)}):\n"
        for i, entry in enumerate(recent, 1):
            output += f"{i}. [{entry.category}] {entry.content[:60]}"
            if len(entry.content) > 60:
                output += "..."
            output += f"\n   ID: {entry.id[:8]}...\n"

        return output.rstrip()

    def handle_export(self, args: str) -> str:
        """Export memories to file.

        Usage: export <filepath>

        Args:
            args: File path to export to

        Returns:
            Confirmation message
        """
        filepath = args.strip()
        if not filepath:
            return "Error: Please provide a file path"

        try:
            self.memory.export_all(filepath)
            return f"Exported memories to {filepath}"
        except Exception as e:
            return f"Error exporting: {e}"

    def handle_import(self, args: str) -> str:
        """Import memories from file.

        Usage: import <filepath>

        Args:
            args: File path to import from

        Returns:
            Confirmation message
        """
        filepath = args.strip()
        if not filepath:
            return "Error: Please provide a file path"

        try:
            self.memory.import_all(filepath)
            return f"Imported memories from {filepath}"
        except FileNotFoundError:
            return f"Error: File not found: {filepath}"
        except Exception as e:
            return f"Error importing: {e}"
