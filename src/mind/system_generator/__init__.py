"""System Generator - Meta-layer for creating autonomous systems.

This module enables Mind to design, generate, and deploy complete
independent system architectures without human intervention.

Each generated system gets its own Git repository, separate from Mind.
Mind maintains references in its registry only.
"""

from .system_generator import SystemGenerator, GeneratedSystem
from .system_spec import SystemSpec, SystemRole, SystemComponent
from .repository_manager import RepositoryInitializer
from .system_registry import SystemRegistry
from .output_formatter import SystemGenerationOutput

__all__ = [
    "SystemGenerator",
    "GeneratedSystem",
    "SystemSpec",
    "SystemRole",
    "SystemComponent",
    "RepositoryInitializer",
    "SystemRegistry",
    "SystemGenerationOutput",
]
