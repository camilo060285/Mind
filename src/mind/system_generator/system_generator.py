"""Core System Generator - generates complete autonomous systems."""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from .system_spec import SystemSpec, SystemComponent, SystemRole
from .generators import (
    AgentGenerator,
    DataModelGenerator,
    BlueprintGenerator,
    OrchestrationGenerator,
    TestGenerator,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GeneratedSystem:
    """Represents a generated system ready for deployment."""

    def __init__(
        self,
        spec: SystemSpec,
        system_dir: Path,
        system_id: str,
    ):
        """Initialize generated system.

        Args:
            spec: System specification
            system_dir: Root directory of generated system
            system_id: Unique system identifier
        """
        self.spec = spec
        self.system_dir = Path(system_dir)
        self.system_id = system_id
        self.created_at = datetime.now().isoformat()

    def save_manifest(self) -> None:
        """Save system manifest."""
        manifest = {
            "system_id": self.system_id,
            "name": self.spec.name,
            "goal": self.spec.goal,
            "created_at": self.created_at,
            "spec": self.spec.to_dict(),
        }
        manifest_file = self.system_dir / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"System manifest saved: {manifest_file}")

    def get_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "system_id": self.system_id,
            "name": self.spec.name,
            "goal": self.spec.goal,
            "root": str(self.system_dir),
            "created_at": self.created_at,
            "components": len(self.spec.components),
            "workflows": len(self.spec.workflows),
        }


class SystemGenerator:
    """Meta-layer for creating autonomous systems."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize SystemGenerator.

        Args:
            base_dir: Base directory for generated systems (default: ~/.mind_systems)
        """
        if base_dir is None:
            base_dir = Path.home() / ".mind_systems"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-generators
        self.agent_gen = AgentGenerator()
        self.model_gen = DataModelGenerator()
        self.blueprint_gen = BlueprintGenerator()
        self.orch_gen = OrchestrationGenerator()
        self.test_gen = TestGenerator()

        logger.info(f"SystemGenerator initialized: {self.base_dir}")

    def create(
        self,
        name: str,
        goal: str,
        features: list[str],
        tools: list[str],
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
    ) -> GeneratedSystem:
        """Create a new system from specification.

        Args:
            name: System name
            goal: What the system does
            features: List of features/capabilities
            tools: List of external tools to integrate
            description: Detailed description
            config: Additional configuration

        Returns:
            GeneratedSystem instance ready for deployment
        """
        system_id = str(uuid.uuid4())[:8]
        system_name = name.lower().replace(" ", "_")
        system_dir = self.base_dir / f"{system_name}_{system_id}"
        system_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating system: {name} (id={system_id})")

        # Create spec
        spec = SystemSpec(
            name=name,
            goal=goal,
            description=description or goal,
            features=features,
            tools=tools,
            config=config or {},
        )

        # Design architecture
        self._design_architecture(spec)

        # Generate all code
        self._generate_code(system_dir, spec)

        # Create system instance
        system = GeneratedSystem(spec, system_dir, system_id)
        system.save_manifest()

        logger.info(f"System created: {system_dir}")
        return system

    def _design_architecture(self, spec: SystemSpec) -> None:
        """Design the system architecture based on spec."""
        logger.debug(f"Designing architecture for: {spec.name}")

        # Always include core components
        core_components = [
            SystemComponent(
                name="SystemOrchestrator",
                component_type="agent",
                role=SystemRole.ORCHESTRATOR,
                description="Main orchestrator for system execution",
                outputs=["task_queue", "execution_state"],
            ),
            SystemComponent(
                name="DataManager",
                component_type="data_store",
                role=SystemRole.DATA_MANAGER,
                description="Central data and asset management",
                inputs=["task_queue"],
                outputs=["data_state"],
            ),
            SystemComponent(
                name="Monitor",
                component_type="service",
                role=SystemRole.MONITOR,
                description="System health and metrics",
                inputs=["execution_state", "data_state"],
                outputs=["metrics", "alerts"],
            ),
        ]

        for component in core_components:
            spec.add_component(component)

        # Add feature-specific components
        for feature in spec.features:
            component = SystemComponent(
                name=f"{feature.capitalize()}Agent",
                component_type="agent",
                role=SystemRole.EXECUTOR,
                description=f"Executor for {feature}",
                inputs=["task_queue"],
                outputs=["results"],
                dependencies=["SystemOrchestrator"],
            )
            spec.add_component(component)

        logger.debug(f"Architecture designed with {len(spec.components)} components")

    def _generate_code(self, system_dir: Path, spec: SystemSpec) -> None:
        """Generate all system code."""
        logger.info(f"Generating code for: {spec.name}")

        # Create directory structure
        self._create_structure(system_dir)

        # Generate agents
        agents_dir = system_dir / "agents"
        for component in spec.components:
            if component.component_type == "agent":
                self.agent_gen.generate(component, agents_dir)

        # Generate data models
        models_dir = system_dir / "models"
        self.model_gen.generate(spec, models_dir)

        # Generate blueprint
        blueprints_dir = system_dir / "blueprints"
        self.blueprint_gen.generate(spec, blueprints_dir)

        # Generate orchestration logic
        core_dir = system_dir / "core"
        self.orch_gen.generate(spec, core_dir)

        # Generate tests
        tests_dir = system_dir / "tests"
        self.test_gen.generate(spec, tests_dir)

        # Generate CLI
        self._generate_cli(system_dir, spec)

        # Generate README
        self._generate_readme(system_dir, spec)

        logger.info(f"Code generation complete: {system_dir}")

    def _create_structure(self, system_dir: Path) -> None:
        """Create standard system directory structure."""
        dirs = [
            "agents",
            "models",
            "blueprints",
            "core",
            "tests",
            "data",
            "config",
            "scripts",
        ]
        for d in dirs:
            (system_dir / d).mkdir(parents=True, exist_ok=True)

    def _generate_cli(self, system_dir: Path, spec: SystemSpec) -> None:
        """Generate system CLI."""
        cli_file = system_dir / "cli.py"
        features_str = str(spec.features)
        cli_code = f'''"""CLI for {spec.name}."""

import sys

def run():
    """Run {spec.name}."""
    print("=== {spec.name} ===")
    print(f"Goal: {spec.goal}")
    print(f"Features: {{', '.join({features_str!r})}}")
    print()
    print("System is ready for operation.")

if __name__ == "__main__":
    run()
'''
        cli_file.write_text(cli_code)
        logger.debug(f"CLI generated: {cli_file}")

    def _generate_readme(self, system_dir: Path, spec: SystemSpec) -> None:
        """Generate README for the system."""
        readme_file = system_dir / "README.md"
        readme = f"""# {spec.name}

**Goal**: {spec.goal}

**Description**: {spec.description}

## Features

{chr(10).join(f'- {f}' for f in spec.features)}

## Tools

{chr(10).join(f'- {t}' for t in spec.tools)}

## Components

{chr(10).join(f'- {c.name} ({c.role.value})' for c in spec.components)}

## Getting Started

1. Review the blueprints in `blueprints/`
2. Configure settings in `config/`
3. Run: `python cli.py`

## Architecture

This system was auto-generated by Mind SystemGenerator.

### Structure
- `agents/` - Agent implementations
- `models/` - Data models
- `blueprints/` - Workflow definitions (YAML)
- `core/` - Orchestration logic
- `tests/` - Test suite
- `data/` - Runtime data and assets
- `config/` - System configuration

## Running the System

```bash
python cli.py
```

## Integration

To integrate external tools:

1. Add tool wrapper to `agents/`
2. Register in orchestrator (`core/orchestrator.py`)
3. Define workflow in blueprint (`blueprints/`)
4. Add tests in `tests/`

"""
        readme_file.write_text(readme)
        logger.debug(f"README generated: {readme_file}")
