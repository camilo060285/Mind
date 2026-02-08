from agents.base_agent import BaseAgent

class AgentArchitectAgent(BaseAgent):
    """Designs the internal agents of the subsystem."""

    def __init__(self):
        super().__init__(
            name="agent_architect_agent",
            description="Creates agent roles and responsibilities."
        )

    def run(self, architecture: dict) -> dict:
        architecture["agents"] = []
        self.log("Created initial agent list.")
        return architecture
