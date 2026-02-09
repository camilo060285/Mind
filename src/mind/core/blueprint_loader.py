import yaml
from pathlib import Path


class BlueprintLoader:
    """Loads and validates blueprint files."""

    def load(self, path: str) -> dict:
        file_path = Path(path)

        # If path doesn't exist and it's a relative path, try looking in the blueprints directory
        if not file_path.exists():
            blueprints_dir = Path(__file__).parent.parent / "blueprints"
            alternative_path = blueprints_dir / Path(path).name
            if alternative_path.exists():
                file_path = alternative_path
            else:
                raise FileNotFoundError(f"Blueprint not found: {path}")

        with open(file_path, "r") as f:
            return yaml.safe_load(f)
