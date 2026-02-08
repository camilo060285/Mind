class MindIdentity:
    """Defines Mind's identity, metadata, and self-description."""

    def __init__(self):
        self.name = "Mind"
        self.version = "0.1.0"

    def describe(self):
        return {
            "name": self.name,
            "version": self.version,
            "purpose": "A modular, privacy-first agentic meta-system."
        }
