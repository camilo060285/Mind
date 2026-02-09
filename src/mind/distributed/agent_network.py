"""Agent network discovery and management.

This module implements agent registration, discovery, and peer management
for distributed agent coordination.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentInfo:
    """Information about a registered agent."""

    agent_id: str
    name: str
    host: str
    port: int
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"  # active, inactive, failed
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class NetworkTopology:
    """Network topology snapshot."""

    timestamp: str
    agents: Dict[str, AgentInfo] = field(default_factory=dict)
    connections: Dict[str, Set[str]] = field(
        default_factory=dict
    )  # agent_id -> set of peer_ids
    active_agents: List[str] = field(default_factory=list)
    failed_agents: List[str] = field(default_factory=list)


class AgentNetwork:
    """Manages agent network discovery and peer coordination."""

    def __init__(self, network_name: str = "default", data_dir: Optional[str] = None):
        """Initialize agent network.

        Args:
            network_name: Name of the network
            data_dir: Directory for network data persistence
        """
        self.network_name = network_name
        self.agents: Dict[str, AgentInfo] = {}
        self.connections: Dict[str, Set[str]] = {}
        self.heartbeat_timeout = 30  # seconds

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".mind_network")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.network_file = self.data_dir / f"{network_name}_agents.jsonl"
        self.topology_file = self.data_dir / f"{network_name}_topology.jsonl"

        self._load_agents()
        logger.info(
            f"AgentNetwork initialized: {network_name} ({len(self.agents)} agents)"
        )

    def register_agent(
        self,
        name: str,
        host: str,
        port: int,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """Register a new agent in the network.

        Args:
            name: Agent name
            host: Host address
            port: Port number
            capabilities: List of agent capabilities
            metadata: Additional metadata

        Returns:
            Agent ID
        """
        agent_id = str(uuid.uuid4())
        agent = AgentInfo(
            agent_id=agent_id,
            name=name,
            host=host,
            port=port,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )

        self.agents[agent_id] = agent
        self.connections[agent_id] = set()
        self._save_agent(agent)

        logger.info(f"Agent registered: {name} ({agent_id}) at {host}:{port}")
        return agent_id

    def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent from network.

        Args:
            agent_id: ID of agent to deregister

        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        del self.agents[agent_id]
        if agent_id in self.connections:
            del self.connections[agent_id]

        # Remove from other agents' connections
        for peers in self.connections.values():
            peers.discard(agent_id)

        logger.info(f"Agent deregistered: {agent.name} ({agent_id})")
        return True

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information.

        Args:
            agent_id: ID of agent

        Returns:
            Agent info or None
        """
        return self.agents.get(agent_id)

    def get_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """Get all agents with a specific capability.

        Args:
            capability: Capability name

        Returns:
            List of agents with capability
        """
        return [
            agent for agent in self.agents.values() if capability in agent.capabilities
        ]

    def get_active_agents(self) -> List[AgentInfo]:
        """Get all active agents.

        Returns:
            List of active agents
        """
        return [
            agent
            for agent in self.agents.values()
            if agent.status == "active" and self._is_heartbeat_healthy(agent)
        ]

    def heartbeat(self, agent_id: str) -> bool:
        """Record heartbeat from agent.

        Args:
            agent_id: ID of agent

        Returns:
            True if heartbeat recorded
        """
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        agent.last_heartbeat = datetime.now().isoformat()

        if agent.status != "active":
            agent.status = "active"
            logger.info(f"Agent recovered: {agent.name} ({agent_id})")

        return True

    def connect_agents(self, agent_id_1: str, agent_id_2: str) -> bool:
        """Establish connection between two agents.

        Args:
            agent_id_1: First agent ID
            agent_id_2: Second agent ID

        Returns:
            True if connection established
        """
        if agent_id_1 not in self.agents or agent_id_2 not in self.agents:
            return False

        if agent_id_1 not in self.connections:
            self.connections[agent_id_1] = set()
        if agent_id_2 not in self.connections:
            self.connections[agent_id_2] = set()

        self.connections[agent_id_1].add(agent_id_2)
        self.connections[agent_id_2].add(agent_id_1)

        logger.info(f"Agents connected: {agent_id_1} <-> {agent_id_2}")
        return True

    def get_peers(self, agent_id: str) -> List[AgentInfo]:
        """Get peer agents for given agent.

        Args:
            agent_id: ID of agent

        Returns:
            List of peer agents
        """
        if agent_id not in self.connections:
            return []

        peer_ids = self.connections[agent_id]
        return [self.agents[pid] for pid in peer_ids if pid in self.agents]

    def get_topology(self) -> NetworkTopology:
        """Get current network topology.

        Returns:
            Network topology snapshot
        """
        # Check heartbeats and update status
        for agent in self.agents.values():
            if not self._is_heartbeat_healthy(agent) and agent.status == "active":
                agent.status = "failed"

        active = [a.agent_id for a in self.agents.values() if a.status == "active"]
        failed = [a.agent_id for a in self.agents.values() if a.status == "failed"]

        topology = NetworkTopology(
            timestamp=datetime.now().isoformat(),
            agents=self.agents.copy(),
            connections=self.connections.copy(),
            active_agents=active,
            failed_agents=failed,
        )

        self._save_topology(topology)
        return topology

    def get_statistics(self) -> Dict:
        """Get network statistics.

        Returns:
            Statistics dictionary
        """
        topology = self.get_topology()
        total_agents = len(self.agents)
        active_count = len(topology.active_agents)
        failed_count = len(topology.failed_agents)

        capabilities: Dict[str, int] = {}
        for agent in self.agents.values():
            for cap in agent.capabilities:
                capabilities[cap] = capabilities.get(cap, 0) + 1

        return {
            "network_name": self.network_name,
            "total_agents": total_agents,
            "active_agents": active_count,
            "failed_agents": failed_count,
            "total_connections": sum(len(peers) for peers in self.connections.values()),
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat(),
        }

    def reset(self) -> None:
        """Reset network state."""
        self.agents.clear()
        self.connections.clear()
        logger.info(f"AgentNetwork reset: {self.network_name}")

    # Private methods

    def _is_heartbeat_healthy(self, agent: AgentInfo) -> bool:
        """Check if agent heartbeat is healthy.

        Args:
            agent: Agent to check

        Returns:
            True if heartbeat is recent
        """
        try:
            last_beat = datetime.fromisoformat(agent.last_heartbeat)
            elapsed = (datetime.now() - last_beat).total_seconds()
            return elapsed < self.heartbeat_timeout
        except (ValueError, TypeError):
            return False

    def _save_agent(self, agent: AgentInfo) -> None:
        """Save agent to file."""
        try:
            with open(self.network_file, "a") as f:
                f.write(json.dumps(asdict(agent)) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving agent: {e}")

    def _save_topology(self, topology: NetworkTopology) -> None:
        """Save topology to file."""
        try:
            data = {
                "timestamp": topology.timestamp,
                "agents": {
                    agent_id: asdict(agent)
                    for agent_id, agent in topology.agents.items()
                },
                "connections": {k: list(v) for k, v in topology.connections.items()},
                "active_agents": topology.active_agents,
                "failed_agents": topology.failed_agents,
            }
            with open(self.topology_file, "a") as f:
                f.write(json.dumps(data) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving topology: {e}")

    def _load_agents(self) -> None:
        """Load agents from file."""
        if not self.network_file.exists():
            return

        try:
            with open(self.network_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        agent = AgentInfo(**data)
                        self.agents[agent.agent_id] = agent
                        self.connections[agent.agent_id] = set()
                    except (json.JSONDecodeError, TypeError):
                        continue
        except (OSError, IOError) as e:
            logger.error(f"Error loading agents: {e}")
