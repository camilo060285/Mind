"""Domain-agnostic latent reasoning layer for Mind."""

from .contracts import (
    build_latent_payload,
    validate_latent_payload,
    validate_animation_extension,
)
from .prompts import ENCODER_PROMPT_TEMPLATE, DECODER_PROMPT_TEMPLATE

__all__ = [
    "build_latent_payload",
    "validate_latent_payload",
    "validate_animation_extension",
    "ENCODER_PROMPT_TEMPLATE",
    "DECODER_PROMPT_TEMPLATE",
]
