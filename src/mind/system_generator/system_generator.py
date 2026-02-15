"""Core System Generator - generates complete autonomous systems.

Generates fully independent Git repositories for each new system,
keeping system code separate from Mind while maintaining references
in Mind's registry.
"""

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
from .repository_manager import RepositoryInitializer
from .system_registry import SystemRegistry
from .output_formatter import SystemGenerationOutput
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GeneratedSystem:
    """Represents a generated system ready for deployment.

    Includes repository information and registry entry, maintaining
    separation between system code and Mind metadata.
    """

    def __init__(
        self,
        spec: SystemSpec,
        system_dir: Path,
        system_id: str,
        repo_info: Dict[str, Any],
        registry_entry: Dict[str, Any],
    ):
        """Initialize generated system.

        Args:
            spec: System specification
            system_dir: Root directory of generated system
            system_id: Unique system identifier
            repo_info: Repository creation information
            registry_entry: Entry in Mind's system registry
        """
        self.spec = spec
        self.system_dir = Path(system_dir)
        self.system_id = system_id
        self.created_at = datetime.now().isoformat()
        self.repo_info = repo_info
        self.registry_entry = registry_entry

    def get_repo_path(self) -> str:
        """Get repository path."""
        return self.repo_info.get("repo_path", str(self.system_dir))

    def get_repo_url(self) -> str:
        """Get repository URL."""
        return self.repo_info.get("repo_url", str(self.system_dir))

    def get_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "system_id": self.system_id,
            "name": self.spec.name,
            "goal": self.spec.goal,
            "repository": self.get_repo_path(),
            "created_at": self.created_at,
            "components": len(self.spec.components),
            "workflows": len(self.spec.workflows),
            "independent_repo": True,
            "registry_tracked": True,
        }

    def get_output_summary(self) -> str:
        """Get human-friendly output summary."""
        return SystemGenerationOutput.format_console_output(
            self.repo_info,
            self.spec.to_dict(),
            "",
        )

    def get_json_output(self) -> Dict[str, Any]:
        """Get JSON-formatted output."""
        return SystemGenerationOutput.format_json_output(
            self.repo_info,
            self.spec.to_dict(),
            self.registry_entry,
        )


class SystemGenerator:
    """Meta-layer for creating autonomous systems.

    Creates independent Git repositories for each system, tracking
    references in Mind's registry without storing system code.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        mind_dir: Optional[Path] = None,
    ):
        """Initialize SystemGenerator.

        Args:
            base_dir: Base directory for generated systems (default: ~/.mind_systems)
            mind_dir: Mind home directory (default: ~/.mind)
        """
        if base_dir is None:
            base_dir = Path.home() / ".mind_systems"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize repository and registry managers
        self.repo_manager = RepositoryInitializer(base_dir)
        self.registry = SystemRegistry(mind_dir)

        # Initialize code generators
        self.agent_gen = AgentGenerator()
        self.model_gen = DataModelGenerator()
        self.blueprint_gen = BlueprintGenerator()
        self.orch_gen = OrchestrationGenerator()
        self.test_gen = TestGenerator()

        logger.info(f"SystemGenerator initialized: {self.base_dir}")
        logger.info(f"System registry: {self.registry.get_registry_path()}")

    def create(
        self,
        name: str,
        goal: str,
        features: list[str],
        tools: list[str],
        description: str = "",
        system_type: str = "agent-cluster",
        config: Optional[Dict[str, Any]] = None,
    ) -> GeneratedSystem:
        """Create a new independent system repository.

        The system code lives in its own Git repository at ~/.mind_systems/.
        Mind only stores a reference in its registry at ~/.mind/system_registry/.

        Args:
            name: System name (human-readable)
            goal: What the system does
            features: List of features/capabilities
            tools: List of external tools to integrate
            description: Detailed description
            system_type: Type of system (agent-cluster, subsystem, orchestrator, etc.)
            config: Additional configuration

        Returns:
            GeneratedSystem instance with repo and registry info
        """
        # Generate unique system ID
        system_id = str(uuid.uuid4())[:8]
        system_name = name.lower().replace(" ", "_")

        logger.info(
            f"Creating independent system: {name} (id={system_id}, type={system_type})"
        )

        # Create specification
        spec = SystemSpec(
            name=name,
            goal=goal,
            description=description or goal,
            features=features,
            tools=tools,
            config=config or {},
        )

        # Add system metadata to config for reference
        spec.config["system_id"] = system_id
        spec.config["system_type"] = system_type
        spec.config["mind_version"] = self._get_mind_version()

        # Design architecture
        self._design_architecture(spec)

        # Create independent Git repository
        logger.info(f"Initializing Git repository for system: {system_name}")
        repo_info = self.repo_manager.create_system_repository(
            system_name, system_id, spec, system_type
        )

        # Get repository path
        repo_path = Path(repo_info["repo_path"])

        # Generate all system code in the new repository
        logger.info(f"Generating system code in repository: {repo_path}")
        self._generate_code(repo_path, spec)

        # Register system in Mind's registry
        logger.info("Registering system in Mind registry")
        registry_entry = {
            "system_id": system_id,
            "system_name": system_name,
            "repo_path": str(repo_path),
            "created_at": datetime.now().isoformat(),
        }
        self.registry.register_system(system_id, system_name, repo_info, spec.to_dict())

        # Create GeneratedSystem instance
        system = GeneratedSystem(spec, repo_path, system_id, repo_info, registry_entry)

        logger.info(f"System created successfully: {system_name} -> {repo_path}")
        logger.info("Registry entry: ~/.mind/system_registry/systems.json")

        return system

    def _get_mind_version(self) -> str:
        """Get current Mind version.

        Returns:
            Version string
        """
        try:
            from ..core.identity import MindIdentity

            identity = MindIdentity()
            return identity.version
        except Exception:
            return "unknown"

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
        """Generate all system code in the repository.

        Args:
            system_dir: System repository root directory
            spec: System specification
        """
        logger.info(f"Generating code for: {spec.name}")

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

        # Generate requirements file
        self._generate_requirements(system_dir, spec)

        logger.info(f"Code generation complete: {system_dir}")

    def _generate_requirements(self, system_dir: Path, spec: SystemSpec) -> None:
        """Generate requirements.txt for the system.

        Args:
            system_dir: System directory
            spec: System specification
        """
        requirements = [
            "# System dependencies",
            "# Generated automatically",
            "",
            "# Core dependencies",
            "PyYAML>=6.0",
            "pydantic>=2.0",
            "",
        ]

        # Add tool-specific requirements
        tool_requirements = {
            "openai": "openai>=1.0",
            "anthropic": "anthropic>=0.7",
            "huggingface": "transformers>=4.30",
            "langchain": "langchain>=0.1",
        }

        for tool in spec.tools:
            tool_lower = tool.lower()
            if tool_lower in tool_requirements:
                requirements.append(tool_requirements[tool_lower])

        requirements_path = system_dir / "requirements.txt"
        requirements_path.write_text("\n".join(requirements) + "\n")
        logger.debug(f"Requirements file generated: {requirements_path}")

    def _generate_cli(self, system_dir: Path, spec: SystemSpec) -> None:
        """Generate system CLI entrypoint.

        Args:
            system_dir: System directory
            spec: System specification
        """
        cli_file = system_dir / "cli.py"
        features_str = (
            ", ".join(spec.features) if spec.features else "Core functionality"
        )

        cli_code = f'''"""CLI for {spec.name}.

Generated autonomously by Mind SystemGenerator.
This system is independent and managed separately.
"""

import sys
import json
from pathlib import Path


def print_system_info():
    """Print system information."""
    print(f"=== {spec.name} ===")
    print(f"Goal: {spec.goal}")
    print(f"Features: {features_str}")
    print()


def load_metadata():
    """Load system metadata."""
    metadata_file = Path(__file__).parent / "system.metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            return json.load(f)
    return None


def run():
    """Run {spec.name}."""
    print_system_info()

    metadata = load_metadata()
    if metadata:
        print("System Configuration:")
        print(f"  Type: {{metadata.get('system', {{}}).get('type', 'unknown')}}")
        print(f"  ID: {{metadata.get('system', {{}}).get('id', 'unknown')}}")
        print()

    print("System is ready for operation.")
    print()
    print("Next steps:")
    print("  1. Review agents/ directory for available agents")
    print("  2. Check blueprints/ for workflow definitions")
    print("  3. Configure settings in config/")
    print("  4. Run: python -m your_module (after implementation)")


if __name__ == "__main__":
    run()
'''
        cli_file.write_text(cli_code)
        logger.debug(f"CLI generated: {cli_file}")
