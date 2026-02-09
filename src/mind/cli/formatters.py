"""Rich output formatting utilities for Mind CLI."""

from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
import json


console = Console()


class MindFormatter:
    """Handles rich formatting of Mind CLI output."""

    @staticmethod
    def print_header(text: str, style: str = "bold cyan") -> None:
        """Print a formatted header."""
        console.print(f"\n[{style}]{'=' * 80}[/{style}]")
        console.print(f"[{style}]{text.center(80)}[/{style}]")
        console.print(f"[{style}]{'=' * 80}[/{style}]\n")

    @staticmethod
    def print_success(text: str) -> None:
        """Print success message."""
        console.print(f"[green]✓ {text}[/green]")

    @staticmethod
    def print_error(text: str) -> None:
        """Print error message."""
        console.print(f"[red]✗ {text}[/red]")

    @staticmethod
    def print_warning(text: str) -> None:
        """Print warning message."""
        console.print(f"[yellow]⚠ {text}[/yellow]")

    @staticmethod
    def print_info(text: str) -> None:
        """Print info message."""
        console.print(f"[blue]ℹ {text}[/blue]")

    @staticmethod
    def print_dict_table(data: dict[str, Any], title: str = "Data") -> None:
        """Print dictionary as formatted table."""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.items():
            value_str = (
                json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            )
            table.add_row(str(key), value_str)

        console.print(table)

    @staticmethod
    def print_list_table(
        items: list[dict[str, Any]],
        title: str = "Items",
        columns: list[str] | None = None,
    ) -> None:
        """Print list of dicts as formatted table."""
        if not items:
            console.print("[yellow]No items to display[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")

        if columns is None:
            columns = list(items[0].keys())

        for col in columns:
            table.add_column(col, style="cyan")

        for item in items:
            row_values = [str(item.get(col, "")) for col in columns]
            table.add_row(*row_values)

        console.print(table)

    @staticmethod
    def print_code(code: str, language: str = "python", title: str = "Code") -> None:
        """Print syntax-highlighted code."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=title, expand=False))

    @staticmethod
    def print_json(data: Any, title: str = "JSON") -> None:
        """Print formatted JSON."""
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=title, expand=False))

    @staticmethod
    def print_panel(text: str, title: str = "Panel", style: str = "blue") -> None:
        """Print text in a rich panel."""
        console.print(Panel(text, title=title, style=style))

    @staticmethod
    def spinner(description: str = "Processing"):
        """Return a context manager for spinner animation."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ).track(range(1), description=description)
