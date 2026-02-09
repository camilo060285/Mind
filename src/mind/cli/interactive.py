"""Interactive CLI shell for Mind."""

import sys
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from pathlib import Path
from mind.cli.commands import CommandRegistry, CommandExecutor
from mind.cli.formatters import MindFormatter
from mind.cli.history import CommandHistory
from mind.memory import MemoryManager


class InteractiveMindShell:
    """Interactive shell for Mind CLI."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """Initialize the shell.

        Args:
            memory_manager: Optional MemoryManager instance for memory commands
        """
        self.registry = CommandRegistry()
        self.executor = CommandExecutor(self.registry)
        self.cmd_history = CommandHistory()
        self.memory_manager = memory_manager or MemoryManager()

        # Setup prompt toolkit history
        history_file = Path.home() / ".mind_shell_history"
        self.prompt_history = FileHistory(str(history_file))

        self._setup_commands()

    def _setup_commands(self) -> None:
        """Setup built-in and memory commands."""
        # Built-in commands
        self.register_command(
            "help", self._cmd_help, "Show help for commands", aliases=["h", "?"]
        )
        self.register_command(
            "history", self._cmd_history_show, "Show command history", aliases=["hist"]
        )
        self.register_command(
            "clear", self._cmd_clear, "Clear the screen", aliases=["cls"]
        )
        self.register_command("exit", self._cmd_exit, "Exit the shell", aliases=["q"])
        self.register_command(
            "stats", self._cmd_stats, "Show history statistics", aliases=["stat"]
        )

        # Memory commands
        if self.memory_manager:
            from mind.cli.memory_commands import MemoryCommandHandler

            mem_handler = MemoryCommandHandler(self.memory_manager)
            self.register_command(
                "remember", mem_handler.handle_remember, "Remember a fact or goal"
            )
            self.register_command(
                "recall", mem_handler.handle_recall, "Recall a specific memory"
            )
            self.register_command(
                "search", mem_handler.handle_search, "Search memories"
            )
            self.register_command(
                "list", mem_handler.handle_list_category, "List memories by category"
            )
            self.register_command(
                "forget", mem_handler.handle_forget, "Forget a memory"
            )
            self.register_command("tag", mem_handler.handle_tag, "Tag a memory")
            self.register_command(
                "memory_stats", mem_handler.handle_stats, "Show memory statistics"
            )
            self.register_command(
                "recent", mem_handler.handle_recent, "Show recent memories"
            )
            self.register_command(
                "export", mem_handler.handle_export, "Export memories to file"
            )
            self.register_command(
                "import", mem_handler.handle_import, "Import memories from file"
            )

    def register_command(
        self,
        name: str,
        handler,
        description: str,
        aliases: list[str] | None = None,
    ) -> None:
        """Register a custom command.

        Args:
            name: Command name
            handler: Command handler function
            description: Short description
            aliases: List of aliases
        """
        self.registry.register(name, description, handler, description, aliases or [])

    def _cmd_help(self, args: str = "") -> str:
        """Handle help command."""
        command = args.strip() if args else None
        help_text = self.registry.get_help(command)
        return help_text or ""

    def _cmd_history_show(self, args: str = "") -> None:
        """Handle history command."""
        limit = 10
        if args.strip():
            try:
                limit = int(args.strip())
            except ValueError:
                MindFormatter.print_error("Limit must be a number")
                return

        history = self.cmd_history.get_history(limit=limit)
        if not history:
            MindFormatter.print_info("No commands in history")
            return

        data = [
            {
                "Time": h.timestamp.split("T")[1][:8],
                "Command": h.command,
                "Status": h.status,
            }
            for h in history
        ]
        MindFormatter.print_list_table(data, title=f"Last {limit} Commands")

    def _cmd_clear(self, args: str = "") -> None:
        """Handle clear command."""
        import os

        os.system("clear" if sys.platform != "win32" else "cls")

    def _cmd_exit(self, args: str = "") -> None:
        """Handle exit command."""
        MindFormatter.print_info("Exiting Mind shell...")
        sys.exit(0)

    def _cmd_stats(self, args: str = "") -> str:
        """Handle stats command."""
        stats = self.cmd_history.statistics()
        output = "Command History Statistics:\n"
        for key, value in stats.items():
            output += f"  {key}: {value}\n"
        return output.rstrip()

    def _get_bottom_toolbar(self) -> HTML:
        """Get bottom toolbar HTML."""
        stats = self.cmd_history.statistics()
        total = stats.get("total_commands", 0)
        success = stats.get("successful", 0)
        return HTML(
            f"<b>Commands:</b> {total} | <b>Success:</b> {success} | "
            f'<style bg="blue">Type "help" for commands | "exit" to quit</style>'
        )

    def run(self) -> None:
        """Run the interactive shell."""
        MindFormatter.print_header("Welcome to Mind Interactive Shell")
        MindFormatter.print_info("Type 'help' for available commands or 'exit' to quit")

        session = PromptSession(history=self.prompt_history)

        while True:
            try:
                user_input = session.prompt(
                    "mind> ",
                    bottom_toolbar=self._get_bottom_toolbar,
                )

                if not user_input.strip():
                    continue

                # Parse command
                parts = user_input.strip().split()
                command_name = parts[0]
                args = " ".join(parts[1:]) if len(parts) > 1 else ""

                try:
                    # Execute command
                    result = self.executor.execute(command_name, args)

                    # Record success
                    self.cmd_history.record(
                        command_name, [args], "success", output=str(result)
                    )

                    # Display result
                    if result is not None:
                        if isinstance(result, str):
                            print(result)
                        else:
                            print(result)

                except KeyError as e:
                    MindFormatter.print_error(str(e))
                    self.cmd_history.record(command_name, [args], "error", error=str(e))
                except Exception as e:
                    MindFormatter.print_error(f"Error: {str(e)}")
                    self.cmd_history.record(command_name, [args], "error", error=str(e))

            except KeyboardInterrupt:
                MindFormatter.print_info("Use 'exit' command to quit")
            except EOFError:
                self._cmd_exit()


def start_interactive_shell() -> None:
    """Start the interactive Mind shell."""
    shell = InteractiveMindShell()
    shell.run()
