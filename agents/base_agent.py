from utils.logger import get_logger

class BaseAgent:
    """
    Base class for all Mind meta-agents.
    Provides a consistent interface and shared utilities.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.history = []
        self.logger = get_logger(self.name)

    def log(self, entry: str):
        """Append an entry to the agent's history and log it."""
        self.history.append(entry)
        self.logger.info(entry)

    def run(self, *args, **kwargs):
        """Main execution method. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run().")
