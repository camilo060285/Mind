"""CLI module for Mind interactive shell and command system."""

from mind.cli.commands import Command, CommandRegistry, CommandExecutor
from mind.cli.evolution_commands import EvolutionCommandHandler
from mind.cli.formatters import MindFormatter
from mind.cli.history import CommandHistory, CommandRecord
from mind.cli.interactive import InteractiveMindShell, start_interactive_shell
from mind.cli.memory_commands import MemoryCommandHandler

__all__ = [
    "Command",
    "CommandRegistry",
    "CommandExecutor",
    "MindFormatter",
    "CommandHistory",
    "CommandRecord",
    "InteractiveMindShell",
    "start_interactive_shell",
    "MemoryCommandHandler",
    "EvolutionCommandHandler",
]
