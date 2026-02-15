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
            blueprint = yaml.safe_load(f)

        self._validate_blueprint(blueprint, path=str(file_path))
        return blueprint

    def _validate_blueprint(self, blueprint: dict, path: str) -> None:
        """Validate minimal blueprint structure.

        Raises ValueError with actionable context when invalid.
        """
        if not isinstance(blueprint, dict):
            raise ValueError(f"Blueprint must be a mapping: {path}")

        goal = blueprint.get("goal")
        if not isinstance(goal, dict):
            raise ValueError(f"Blueprint missing 'goal' mapping: {path}")

        raw_text = goal.get("raw_text")
        if not isinstance(raw_text, str) or not raw_text.strip():
            raise ValueError(f"Blueprint goal.raw_text must be a non-empty string: {path}")

        pipeline = blueprint.get("pipeline")
        if not isinstance(pipeline, list) or not pipeline:
            raise ValueError(f"Blueprint pipeline must be a non-empty list: {path}")

        for index, step in enumerate(pipeline):
            if not isinstance(step, dict):
                raise ValueError(
                    f"Blueprint pipeline step {index} must be a mapping: {path}"
                )
            agent = step.get("agent")
            if not isinstance(agent, str) or not agent.strip():
                raise ValueError(
                    f"Blueprint pipeline step {index} missing 'agent': {path}"
                )

        constraints = blueprint.get("constraints")
        if constraints is not None and not isinstance(constraints, list):
            raise ValueError(
                f"Blueprint constraints must be a list when provided: {path}"
            )
