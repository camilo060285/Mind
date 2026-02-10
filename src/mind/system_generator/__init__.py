"""System Generator - Meta-layer for creating autonomous systems.

This module enables Mind to design, generate, and deploy complete
system architectures without human intervention.
"""

from .system_generator import SystemGenerator
from .system_spec import SystemSpec, SystemRole, SystemComponent

__all__ = [
    "SystemGenerator",
    "SystemSpec",
    "SystemRole",
    "SystemComponent",
]
