class ThinkingProtocol:
    """Transforms blueprint steps into actionable agent instructions."""

    def think(self, step: dict) -> dict:
        # In the future: reasoning, validation, context propagation
        return {
            "agent": step.get("agent"),
            "action": step.get("action"),
            "context": step.get("context", {}),
        }

    def encode(self, raw_input: str, domain: str = "general") -> dict:
        """Create a latent payload from raw user input."""
        from ..latent.contracts import build_latent_payload

        return build_latent_payload(raw_input=raw_input, domain=domain)

    def validate(self, latent_payload: dict) -> tuple[bool, list[str]]:
        """Validate latent payload consistency before downstream execution."""
        from ..latent.contracts import validate_latent_payload

        return validate_latent_payload(latent_payload)

    def decoder_input(
        self, latent_payload: dict, output_format: str = "structured document"
    ) -> dict:
        """Build decoder stage input payload for cloud expansion."""
        return {
            "latent": latent_payload,
            "output_format": output_format,
        }
