class MindIdentity:
    """Defines Mind's identity, metadata, capabilities, and self-description."""

    def __init__(self):
        self.name = "Mind"
        self.version = "0.1.0"
        self.author = "Cristian"
        self.description = (
            "A modular, privacy-first agentic meta-system designed to orchestrate "
            "distributed subsystems and execute autonomous workflows."
        )
        self.capabilities = [
            "Load and validate blueprints",
            "Execute agent workflows",
            "Perform cognitive reasoning",
            "Coordinate distributed hardware",
        ]

    def describe(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "capabilities": self.capabilities,
        }
