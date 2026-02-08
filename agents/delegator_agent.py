from agents.base_agent import BaseAgent


class DelegatorAgent(BaseAgent):
    """Hands off subsystems to run autonomously."""

    def __init__(self):
        super().__init__(
            name="delegator_agent",
            description="Delegates systems and manages autonomy.",
        )

    def run(self, architecture: dict) -> str:
        self.log("Delegated system.")
        return "system_delegated"
