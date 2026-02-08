class BaseAgent:
    """Base class for all agents in Mind."""

    def __init__(self, name):
        self.name = name

    def act(self, context: dict):
        raise NotImplementedError("Agents must implement the act() method.")
