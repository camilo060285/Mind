from agents.base_agent import BaseAgent


class BoundarySetterAgent(BaseAgent):
    """Defines what the system should and should not do."""

    def __init__(self):
        super().__init__(
            name="boundary_setter_agent",
            description="Sets constraints, scope, and non-goals.",
        )

    def run(self, architecture: dict, constraints: list) -> dict:
        architecture["boundaries"] = constraints
        self.log(f"Applied boundaries: {constraints}")
        return architecture
