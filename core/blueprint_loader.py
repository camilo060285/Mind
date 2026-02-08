import yaml
from pathlib import Path

class BlueprintLoader:
    """Loads and validates blueprint files."""

    def load(self, path: str) -> dict:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Blueprint not found: {path}")

        with open(file_path, "r") as f:
            return yaml.safe_load(f)
