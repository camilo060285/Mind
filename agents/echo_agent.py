from agents.base_agent import BaseAgent


class EchoAgent(BaseAgent):
    """A simple agent that returns whatever it receives."""

    def act(self, context: dict):
        return {
            "agent": self.name,
            "received": context,
        }
