"""Load balancing for distributed task distribution.

Implements multiple load balancing strategies for distributing tasks
across agents in the network.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class TaskAssignment:
    """Record of a task assignment to an agent."""

    task_id: str
    agent_id: str
    strategy: str
    assignment_time: str
    estimated_completion: Optional[str] = None
    actual_completion: Optional[str] = None
    execution_time: float = 0.0
    success: bool = True
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentLoad:
    """Current load information for an agent."""

    agent_id: str
    name: str
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    performance_score: float = 1.0  # 0-1 scale
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class LoadBalancer:
    """Manages task distribution across agents."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize load balancer.

        Args:
            data_dir: Directory for load data persistence
        """
        self.assignments: Dict[str, TaskAssignment] = {}
        self.agent_loads: Dict[str, AgentLoad] = {}
        self.round_robin_index = 0

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".mind_loadbalancer")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.assignments_file = self.data_dir / "assignments.jsonl"
        self._load_assignments()
        logger.info("LoadBalancer initialized")

    def assign_task(
        self,
        task_id: str,
        agents: List[Dict[str, Any]],
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED,
        weights: Optional[Dict[str, float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Assign a task to an agent.

        Args:
            task_id: Task ID
            agents: List of available agents
            strategy: Load balancing strategy
            weights: Weights for weighted strategy

        Returns:
            Selected agent or None
        """
        if not agents:
            return None

        selected_agent = None

        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected_agent = self._assign_round_robin(agents)
        elif strategy == LoadBalancingStrategy.RANDOM:
            import random

            selected_agent = random.choice(agents)
        elif strategy == LoadBalancingStrategy.LEAST_LOADED:
            selected_agent = self._assign_least_loaded(agents)
        elif strategy == LoadBalancingStrategy.WEIGHTED:
            selected_agent = self._assign_weighted(agents, weights or {})
        elif strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            selected_agent = self._assign_performance_based(agents)

        if selected_agent:
            assignment = TaskAssignment(
                task_id=task_id,
                agent_id=selected_agent["agent_id"],
                strategy=strategy.value,
                assignment_time=datetime.now().isoformat(),
            )
            self.assignments[task_id] = assignment
            self._save_assignment(assignment)

            # Update agent load
            agent_id = selected_agent["agent_id"]
            if agent_id not in self.agent_loads:
                self.agent_loads[agent_id] = AgentLoad(
                    agent_id=agent_id,
                    name=selected_agent.get("name", agent_id),
                )
            self.agent_loads[agent_id].active_tasks += 1

            logger.info(f"Task assigned: {task_id} -> {agent_id} ({strategy.value})")

        return selected_agent

    def complete_task(
        self,
        task_id: str,
        execution_time: float,
        success: bool = True,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Mark a task as complete.

        Args:
            task_id: Task ID
            execution_time: Execution time in seconds
            success: Whether task succeeded
            result: Task result
            error: Error message if failed

        Returns:
            True if completed successfully
        """
        if task_id not in self.assignments:
            return False

        assignment = self.assignments[task_id]
        assignment.actual_completion = datetime.now().isoformat()
        assignment.execution_time = execution_time
        assignment.success = success
        assignment.result = result
        assignment.error = error

        # Update agent load
        agent_id = assignment.agent_id
        if agent_id in self.agent_loads:
            load = self.agent_loads[agent_id]
            load.active_tasks = max(0, load.active_tasks - 1)

            if success:
                load.completed_tasks += 1
            else:
                load.failed_tasks += 1

            load.total_execution_time += execution_time
            if load.completed_tasks + load.failed_tasks > 0:
                load.average_execution_time = load.total_execution_time / (
                    load.completed_tasks + load.failed_tasks
                )

            # Update performance score
            total_tasks = load.completed_tasks + load.failed_tasks
            if total_tasks > 0:
                success_rate = load.completed_tasks / total_tasks
                load.performance_score = success_rate

        self._save_assignment(assignment)
        return True

    def get_assignment(self, task_id: str) -> Optional[TaskAssignment]:
        """Get assignment information.

        Args:
            task_id: Task ID

        Returns:
            Task assignment or None
        """
        return self.assignments.get(task_id)

    def get_agent_load(self, agent_id: str) -> Optional[AgentLoad]:
        """Get load information for agent.

        Args:
            agent_id: Agent ID

        Returns:
            Agent load or None
        """
        return self.agent_loads.get(agent_id)

    def get_all_agent_loads(self) -> Dict[str, AgentLoad]:
        """Get load information for all agents.

        Returns:
            Dictionary of agent loads
        """
        return self.agent_loads.copy()

    def get_load_statistics(self) -> Dict[str, Any]:
        """Get load balancing statistics.

        Returns:
            Statistics dictionary
        """
        if not self.agent_loads:
            return {
                "total_agents": 0,
                "total_tasks": 0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "average_load": 0.0,
                "agents": {},
            }

        loads = list(self.agent_loads.values())

        total_tasks = len(self.assignments)
        active_tasks = sum(a.active_tasks for a in loads)
        completed_tasks = sum(a.completed_tasks for a in loads)
        failed_tasks = sum(a.failed_tasks for a in loads)
        average_load = active_tasks / len(loads) if loads else 0.0

        agents_info = {
            agent_id: {
                "name": load.name,
                "active_tasks": load.active_tasks,
                "completed_tasks": load.completed_tasks,
                "failed_tasks": load.failed_tasks,
                "average_execution_time": load.average_execution_time,
                "performance_score": load.performance_score,
            }
            for agent_id, load in self.agent_loads.items()
        }

        return {
            "total_agents": len(loads),
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "average_load": average_load,
            "agents": agents_info,
        }

    def reset(self) -> None:
        """Reset load balancer state."""
        self.assignments.clear()
        self.agent_loads.clear()
        self.round_robin_index = 0
        logger.info("LoadBalancer reset")

    # Private methods

    def _assign_round_robin(
        self, agents: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Assign using round robin strategy."""
        if not agents:
            return None

        selected = agents[self.round_robin_index % len(agents)]
        self.round_robin_index += 1
        return selected

    def _assign_least_loaded(
        self, agents: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Assign to least loaded agent."""
        if not agents:
            return None

        min_load = float("inf")
        selected = None

        for agent in agents:
            agent_id = agent["agent_id"]
            load = self.agent_loads.get(agent_id, AgentLoad(agent_id=agent_id, name=""))
            current_load = load.active_tasks

            if current_load < min_load:
                min_load = current_load
                selected = agent

        return selected

    def _assign_weighted(
        self, agents: List[Dict[str, Any]], weights: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """Assign using weighted strategy."""
        if not agents:
            return None

        import random

        weighted_agents = []
        for agent in agents:
            agent_id = agent["agent_id"]
            weight = weights.get(agent_id, 1.0)
            weighted_agents.extend([agent] * int(weight * 10))

        return random.choice(weighted_agents) if weighted_agents else agents[0]

    def _assign_performance_based(
        self, agents: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Assign based on agent performance scores."""
        if not agents:
            return None

        best_agent = None
        best_score = 0.0

        for agent in agents:
            agent_id = agent["agent_id"]
            load = self.agent_loads.get(agent_id, AgentLoad(agent_id=agent_id, name=""))

            # Combine performance score with current load
            score = load.performance_score * (1.0 - load.active_tasks / 10.0)

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent

    def _save_assignment(self, assignment: TaskAssignment) -> None:
        """Save assignment to file."""
        try:
            with open(self.assignments_file, "a") as f:
                f.write(json.dumps(asdict(assignment)) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving assignment: {e}")

    def _load_assignments(self) -> None:
        """Load assignments from file."""
        if not self.assignments_file.exists():
            return

        try:
            with open(self.assignments_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        assignment = TaskAssignment(**data)
                        self.assignments[assignment.task_id] = assignment
                    except (json.JSONDecodeError, TypeError):
                        continue
        except (OSError, IOError) as e:
            logger.error(f"Error loading assignments: {e}")
