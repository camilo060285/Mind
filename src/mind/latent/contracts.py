"""Latent reasoning contracts and lightweight validation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast


def build_latent_payload(
    raw_input: str,
    domain: str = "general",
    intent: dict[str, str] | None = None,
    entities: list[dict[str, Any]] | None = None,
    constraints: list[dict[str, str]] | None = None,
    structure: dict[str, Any] | None = None,
    style: dict[str, str] | None = None,
    confidence: float = 0.7,
    encoder: str = "phi-local",
) -> dict[str, Any]:
    """Build a schema-aligned latent payload with safe defaults."""
    return {
        "schema_version": "1.0",
        "domain": domain,
        "intent": intent
        or {
            "goal": "Clarify user objective",
            "outcome": "Structured latent representation",
            "audience": "Internal agents",
        },
        "entities": entities or [],
        "constraints": constraints or [],
        "structure": structure
        or {
            "form": "outline",
            "sections": ["context", "requirements", "deliverable"],
        },
        "style": style
        or {
            "tone": "clear",
            "voice": "neutral",
            "length_hint": "concise",
        },
        "confidence": confidence,
        "source": {
            "raw_input": raw_input,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "encoder": encoder,
        },
    }


def validate_latent_payload(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate core latent payload without external dependencies."""
    errors: list[str] = []

    required_top = [
        "schema_version",
        "domain",
        "intent",
        "entities",
        "constraints",
        "structure",
        "style",
        "confidence",
        "source",
    ]
    for key in required_top:
        if key not in payload:
            errors.append(f"missing field: {key}")

    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append("confidence must be a number between 0 and 1")

    intent_value = payload.get("intent", {})
    intent = (
        cast(dict[str, Any], intent_value) if isinstance(intent_value, dict) else {}
    )
    for key in ["goal", "outcome", "audience"]:
        if not str(intent.get(key, "")).strip():
            errors.append(f"intent.{key} is required")

    structure_value = payload.get("structure", {})
    structure = (
        cast(dict[str, Any], structure_value)
        if isinstance(structure_value, dict)
        else {}
    )
    if not structure.get("form"):
        errors.append("structure.form is required")
    if not isinstance(structure.get("sections", []), list):
        errors.append("structure.sections must be an array")

    style_value = payload.get("style", {})
    style = cast(dict[str, Any], style_value) if isinstance(style_value, dict) else {}
    for key in ["tone", "voice", "length_hint"]:
        if not str(style.get(key, "")).strip():
            errors.append(f"style.{key} is required")

    source_value = payload.get("source", {})
    source = (
        cast(dict[str, Any], source_value) if isinstance(source_value, dict) else {}
    )
    for key in ["raw_input", "timestamp", "encoder"]:
        if key not in source:
            errors.append(f"source.{key} is required")

    return len(errors) == 0, errors


def validate_animation_extension(
    animation_data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Validate animation domain extension payload."""
    errors: list[str] = []

    required = ["story_beats", "scenes", "character_state", "shot_plan"]
    for key in required:
        if key not in animation_data:
            errors.append(f"missing animation field: {key}")

    if not isinstance(animation_data.get("story_beats", []), list):
        errors.append("story_beats must be an array")
    if not isinstance(animation_data.get("scenes", []), list):
        errors.append("scenes must be an array")
    if not isinstance(animation_data.get("character_state", []), list):
        errors.append("character_state must be an array")
    if not isinstance(animation_data.get("shot_plan", []), list):
        errors.append("shot_plan must be an array")

    return len(errors) == 0, errors
