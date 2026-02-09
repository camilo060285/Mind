"""Command history manager for Mind CLI."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict


@dataclass
class CommandRecord:
    """A record of a CLI command execution."""

    timestamp: str
    command: str
    args: List[str]
    status: str  # "success" or "error"
    output: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class CommandHistory:
    """Manages command history persistence and querying."""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize history manager.

        Args:
            history_file: Path to history file. Defaults to ~/.mind_history
        """
        if history_file is None:
            history_file = Path.home() / ".mind_history"

        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[CommandRecord] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self._records = [CommandRecord(**record) for record in data]
            except (json.JSONDecodeError, ValueError):
                self._records = []

    def _save_history(self) -> None:
        """Save history to file."""
        with open(self.history_file, "w") as f:
            json.dump([r.to_dict() for r in self._records], f, indent=2)

    def record(
        self,
        command: str,
        args: List[str],
        status: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Record a command execution.

        Args:
            command: The command name
            args: Command arguments
            status: Execution status ("success" or "error")
            output: Command output
            error: Error message if failed
        """
        record = CommandRecord(
            timestamp=datetime.now().isoformat(),
            command=command,
            args=args,
            status=status,
            output=output,
            error=error,
        )
        self._records.append(record)
        self._save_history()

    def get_history(self, limit: Optional[int] = None) -> List[CommandRecord]:
        """Get command history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of command records
        """
        if limit is None:
            return self._records
        return self._records[-limit:]

    def search(self, query: str) -> List[CommandRecord]:
        """Search history by command name or args.

        Args:
            query: Search query

        Returns:
            Matching records
        """
        return [
            r
            for r in self._records
            if query.lower() in r.command.lower()
            or any(query.lower() in arg.lower() for arg in r.args)
        ]

    def clear(self) -> None:
        """Clear all history."""
        self._records = []
        self._save_history()

    def statistics(self) -> dict:
        """Get history statistics.

        Returns:
            Dict with stats
        """
        if not self._records:
            return {"total_commands": 0}

        success_count = sum(1 for r in self._records if r.status == "success")
        error_count = sum(1 for r in self._records if r.status == "error")

        return {
            "total_commands": len(self._records),
            "successful": success_count,
            "failed": error_count,
            "success_rate": f"{(success_count / len(self._records) * 100):.1f}%",
            "first_command": self._records[0].timestamp,
            "last_command": self._records[-1].timestamp,
        }
