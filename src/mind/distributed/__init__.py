"""Distributed agent coordination and management.

This package enables multi-agent distributed coordination with:
- Agent network discovery and registration
- JSON-RPC 2.0 inter-agent communication
- Intelligent load balancing across agents
- Fault tolerance and recovery mechanisms
- Distributed state synchronization and consensus
"""

from .agent_network import AgentInfo, AgentNetwork, NetworkTopology
from .fault_recovery import CircuitState, FaultRecovery, Failure
from .load_balancer import (
    AgentLoad,
    LoadBalancer,
    LoadBalancingStrategy,
    TaskAssignment,
)
from .rpc_server import RPCCall, RPCRequest, RPCResponse, RPCServer
from .state_sync import StateChange, StateSync, StateVersion

__all__ = [
    "AgentNetwork",
    "AgentInfo",
    "NetworkTopology",
    "RPCServer",
    "RPCRequest",
    "RPCResponse",
    "RPCCall",
    "LoadBalancer",
    "LoadBalancingStrategy",
    "TaskAssignment",
    "AgentLoad",
    "FaultRecovery",
    "Failure",
    "CircuitState",
    "StateSync",
    "StateChange",
    "StateVersion",
]
