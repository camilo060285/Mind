"""System specification and component definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from enum import Enum


class SystemRole(Enum):
    """Role types for agents in a system."""

    ORCHESTRATOR = "orchestrator"
    EXECUTOR = "executor"
    COORDINATOR = "coordinator"
    DATA_MANAGER = "data_manager"
    MONITOR = "monitor"


@dataclass
class SystemComponent:
    """A component in the system (agent, data store, tool integration)."""

    name: str
    component_type: str  # "agent", "data_store", "tool", "service"
    role: SystemRole
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemSpec:
    """Specification for an autonomous system."""

    name: str
    goal: str
    description: str
    version: str = "1.0"
    components: List[SystemComponent] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    data_models: Dict[str, Dict[str, str]] = field(default_factory=dict)
    workflows: List[Dict[str, Any]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    def add_component(self, component: SystemComponent) -> None:
        """Add a component to the system."""
        self.components.append(component)

    def add_workflow(self, workflow: Dict[str, Any]) -> None:
        """Add a workflow definition."""
        self.workflows.append(workflow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert spec to dictionary."""
        return {
            "name": self.name,
            "goal": self.goal,
            "description": self.description,
            "version": self.version,
            "components": [
                {
                    "name": c.name,
                    "type": c.component_type,
                    "role": c.role.value,
                    "description": c.description,
                    "inputs": c.inputs,
                    "outputs": c.outputs,
                    "dependencies": c.dependencies,
                }
                for c in self.components
            ],
            "features": self.features,
            "tools": self.tools,
            "data_models": self.data_models,
            "workflows": self.workflows,
        }
