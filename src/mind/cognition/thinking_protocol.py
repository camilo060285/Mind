class ThinkingProtocol:
    """Transforms blueprint steps into actionable agent instructions."""

    def think(self, step: dict) -> dict:
        # In the future: reasoning, validation, context propagation
        return {
            "agent": step.get("agent"),
            "action": step.get("action"),
            "context": step.get("context", {}),
        }
