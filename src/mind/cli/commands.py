"""Command handlers for Mind CLI."""

from typing import Callable, Dict, Any, List
from dataclasses import dataclass
from mind.cli.formatters import MindFormatter


@dataclass
class Command:
    """Definition of a CLI command."""

    name: str
    description: str
    help_text: str
    handler: Callable
    aliases: List[str] | None = None

    def __post_init__(self) -> None:
        """Initialize aliases."""
        if self.aliases is None:
            self.aliases = []


class CommandRegistry:
    """Registry of available commands."""

    def __init__(self):
        """Initialize command registry."""
        self._commands: Dict[str, Command] = {}
        self._alias_map: Dict[str, str] = {}

    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
        help_text: str = "",
        aliases: List[str] | None = None,
    ) -> None:
        """Register a command.

        Args:
            name: Command name
            description: Short description
            handler: Command handler function
            help_text: Detailed help text
            aliases: List of aliases
        """
        cmd = Command(
            name=name,
            description=description,
            help_text=help_text or description,
            handler=handler,
            aliases=aliases or [],
        )
        self._commands[name] = cmd

        # Register aliases
        if cmd.aliases:
            for alias in cmd.aliases:
                self._alias_map[alias] = name

    def get(self, name: str) -> Command:
        """Get command by name or alias.

        Args:
            name: Command name or alias

        Returns:
            Command object
        """
        # Check aliases first
        if name in self._alias_map:
            name = self._alias_map[name]

        if name not in self._commands:
            raise KeyError(f"Unknown command: {name}")

        return self._commands[name]

    def list_commands(self) -> List[Command]:
        """List all available commands.

        Returns:
            List of commands
        """
        return list(self._commands.values())

    def get_help(self, command_name: str | None = None) -> str:
        """Get help text for a command or all commands.

        Args:
            command_name: Specific command or None for all

        Returns:
            Help text
        """
        if command_name:
            try:
                cmd = self.get(command_name)
                return f"{cmd.name}: {cmd.help_text}"
            except KeyError:
                return f"Unknown command: {command_name}"

        # Return all commands help
        help_lines = ["Available commands:\n"]
        for cmd in self.list_commands():
            aliases_str = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_lines.append(f"  {cmd.name}{aliases_str}: {cmd.description}")

        return "\n".join(help_lines)


class CommandExecutor:
    """Executes registered commands."""

    def __init__(self, registry: CommandRegistry):
        """Initialize executor.

        Args:
            registry: Command registry
        """
        self.registry = registry

    def execute(self, command_name: str, args: str = "", **kwargs) -> Any:
        """Execute a command.

        Args:
            command_name: Name or alias of command
            args: Arguments string
            **kwargs: Keyword arguments

        Returns:
            Command result
        """
        try:
            cmd = self.registry.get(command_name)
            return cmd.handler(args, **kwargs)
        except Exception as e:
            MindFormatter.print_error(f"Command execution failed: {str(e)}")
            raise

    def get_help(self, command_name: str | None = None) -> None:
        """Display help.

        Args:
            command_name: Specific command or None for all
        """
        help_text = self.registry.get_help(command_name)
        MindFormatter.print_panel(help_text, title="Help", style="blue")
