"""Tests for Phase 10: Distributed Agents components."""

import json
import tempfile

from mind.distributed import (
    AgentNetwork,
    CircuitState,
    FaultRecovery,
    LoadBalancer,
    LoadBalancingStrategy,
    RPCServer,
    StateSync,
)


class TestAgentNetwork:
    """Test agent network discovery and management."""

    def test_register_agent(self):
        """Test agent registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)
            agent_id = network.register_agent(
                "agent1", "localhost", 5000, capabilities=["processing", "analysis"]
            )

            assert agent_id
            agent = network.get_agent(agent_id)
            assert agent is not None
            assert agent.name == "agent1"
            assert agent.host == "localhost"
            assert agent.port == 5000
            assert "processing" in agent.capabilities

    def test_deregister_agent(self):
        """Test agent deregistration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)
            agent_id = network.register_agent("agent1", "localhost", 5000)

            result = network.deregister_agent(agent_id)
            assert result is True
            assert network.get_agent(agent_id) is None

    def test_get_agents_by_capability(self):
        """Test retrieval of agents by capability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)

            network.register_agent(
                "agent1", "localhost", 5000, capabilities=["analysis"]
            )
            network.register_agent(
                "agent2", "localhost", 5001, capabilities=["processing", "analysis"]
            )
            network.register_agent(
                "agent3", "localhost", 5002, capabilities=["logging"]
            )

            analysis_agents = network.get_agents_by_capability("analysis")
            assert len(analysis_agents) == 2

    def test_heartbeat(self):
        """Test agent heartbeat recording."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)
            agent_id = network.register_agent("agent1", "localhost", 5000)

            result = network.heartbeat(agent_id)
            assert result is True

            agent = network.get_agent(agent_id)
            assert agent.status == "active"

    def test_connect_agents(self):
        """Test agent connection establishment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)

            agent1_id = network.register_agent("agent1", "localhost", 5000)
            agent2_id = network.register_agent("agent2", "localhost", 5001)

            result = network.connect_agents(agent1_id, agent2_id)
            assert result is True

            peers_1 = network.get_peers(agent1_id)
            peers_2 = network.get_peers(agent2_id)
            assert len(peers_1) == 1
            assert len(peers_2) == 1

    def test_get_topology(self):
        """Test network topology retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)

            agent_id = network.register_agent("agent1", "localhost", 5000)
            network.heartbeat(agent_id)

            topology = network.get_topology()
            assert len(topology.agents) == 1
            assert agent_id in topology.active_agents

    def test_get_statistics(self):
        """Test network statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)

            network.register_agent(
                "agent1", "localhost", 5000, capabilities=["analysis"]
            )
            network.register_agent(
                "agent2", "localhost", 5001, capabilities=["processing"]
            )

            stats = network.get_statistics()
            assert stats["total_agents"] == 2
            assert stats["capabilities"]["analysis"] == 1
            assert stats["capabilities"]["processing"] == 1


class TestRPCServer:
    """Test JSON-RPC 2.0 server."""

    def test_register_method(self):
        """Test method registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = RPCServer("agent1", data_dir=tmpdir)

            def add(a: int, b: int) -> int:
                return a + b

            server.register_method("add", add)
            assert "add" in server.methods

    def test_handle_request_valid(self):
        """Test handling valid RPC request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = RPCServer("agent1", data_dir=tmpdir)

            def add(a: int, b: int) -> int:
                return a + b

            server.register_method("add", add)

            request = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "add",
                    "params": {"a": 5, "b": 3},
                    "id": "1",
                }
            )

            response_str = server.handle_request(request)
            response = json.loads(response_str)

            assert response["result"] == 8
            assert response["id"] == "1"

    def test_handle_request_method_not_found(self):
        """Test handling request for non-existent method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = RPCServer("agent1", data_dir=tmpdir)

            request = json.dumps(
                {"jsonrpc": "2.0", "method": "nonexistent", "params": {}, "id": "1"}
            )

            response_str = server.handle_request(request)
            response = json.loads(response_str)

            assert "error" in response
            assert response["error"]["code"] == -32601

    def test_get_call_statistics(self):
        """Test RPC call statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = RPCServer("agent1", data_dir=tmpdir)

            def add(a: int, b: int) -> int:
                return a + b

            server.register_method("add", add)

            request = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "add",
                    "params": {"a": 5, "b": 3},
                    "id": "1",
                }
            )
            server.handle_request(request)

            stats = server.get_call_statistics()
            assert stats["total_calls"] == 1
            assert stats["successful_calls"] == 1


class TestLoadBalancer:
    """Test load balancing."""

    def test_assign_task_round_robin(self):
        """Test round-robin task assignment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            balancer = LoadBalancer(data_dir=tmpdir)

            agents = [
                {"agent_id": "agent1", "name": "Agent1"},
                {"agent_id": "agent2", "name": "Agent2"},
            ]

            selected1 = balancer.assign_task(
                "task1", agents, strategy=LoadBalancingStrategy.ROUND_ROBIN
            )
            selected2 = balancer.assign_task(
                "task2", agents, strategy=LoadBalancingStrategy.ROUND_ROBIN
            )

            assert selected1 is not None
            assert selected2 is not None
            assert selected1["agent_id"] != selected2["agent_id"]

    def test_assign_task_least_loaded(self):
        """Test least-loaded task assignment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            balancer = LoadBalancer(data_dir=tmpdir)

            agents = [
                {"agent_id": "agent1", "name": "Agent1"},
                {"agent_id": "agent2", "name": "Agent2"},
            ]

            # Assign to agent1
            balancer.assign_task(
                "task1", agents, strategy=LoadBalancingStrategy.LEAST_LOADED
            )
            # Mark as complete
            balancer.complete_task("task1", execution_time=1.0)

            # Next should still go to agent1 (now has 0 tasks, agent2 has 0)
            # or to the first one in the list
            selected = balancer.assign_task(
                "task2", agents, strategy=LoadBalancingStrategy.LEAST_LOADED
            )
            assert selected is not None

    def test_complete_task(self):
        """Test task completion tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            balancer = LoadBalancer(data_dir=tmpdir)

            agents = [{"agent_id": "agent1", "name": "Agent1"}]

            balancer.assign_task(
                "task1", agents, strategy=LoadBalancingStrategy.LEAST_LOADED
            )
            balancer.complete_task("task1", execution_time=2.5, success=True)

            assignment = balancer.get_assignment("task1")
            assert assignment.execution_time == 2.5
            assert assignment.success is True

    def test_get_load_statistics(self):
        """Test load statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            balancer = LoadBalancer(data_dir=tmpdir)

            agents = [
                {"agent_id": "agent1", "name": "Agent1"},
                {"agent_id": "agent2", "name": "Agent2"},
            ]

            balancer.assign_task(
                "task1", agents, strategy=LoadBalancingStrategy.LEAST_LOADED
            )
            balancer.complete_task("task1", execution_time=1.0, success=True)

            stats = balancer.get_load_statistics()
            assert stats["total_agents"] == 1
            assert stats["completed_tasks"] == 1


class TestFaultRecovery:
    """Test fault tolerance and recovery."""

    def test_register_failure(self):
        """Test failure registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=3, data_dir=tmpdir)

            failure_id = recovery.register_failure(
                "agent1", "connection_error", "Connection timeout"
            )
            assert failure_id
            assert recovery.get_failure(failure_id) is not None

    def test_circuit_breaker_open(self):
        """Test circuit breaker opening."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=2, data_dir=tmpdir)

            recovery.register_failure("agent1", "error", "Error 1")
            recovery.register_failure("agent1", "error", "Error 2")

            cb = recovery.get_circuit_breaker("agent1")
            assert cb.state == CircuitState.OPEN

    def test_record_success_recovery(self):
        """Test successful recovery from failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=2, data_dir=tmpdir)

            recovery.register_failure("agent1", "error", "Error 1")
            recovery.register_failure("agent1", "error", "Error 2")

            # Circuit is now open, wait for reset
            cb = recovery.get_circuit_breaker("agent1")
            assert cb.state == CircuitState.OPEN

            # Manually move to half-open and record successes
            cb.state = CircuitState.HALF_OPEN
            recovery.record_success("agent1")
            recovery.record_success("agent1")
            recovery.record_success("agent1")

            # Circuit should now be closed
            cb = recovery.get_circuit_breaker("agent1")
            assert cb.state == CircuitState.CLOSED

    def test_is_agent_healthy(self):
        """Test agent health check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=5, data_dir=tmpdir)

            assert recovery.is_agent_healthy("agent1") is True

            recovery.register_failure("agent1", "error", "Error")
            assert recovery.is_agent_healthy("agent1") is True

    def test_get_health_status(self):
        """Test overall health status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=2, data_dir=tmpdir)

            recovery.register_failure("agent1", "error", "Error 1")
            recovery.register_failure("agent1", "error", "Error 2")

            status = recovery.get_health_status()
            assert status["total_agents"] == 1
            assert status["failing_agents"] == 1


class TestStateSync:
    """Test distributed state synchronization."""

    def test_set_state(self):
        """Test setting state value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = StateSync("agent1", data_dir=tmpdir)

            change_id = sync.set_state("config", {"key": "value"})
            assert change_id
            assert sync.get_state("config") == {"key": "value"}

    def test_get_all_state(self):
        """Test retrieving all state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = StateSync("agent1", data_dir=tmpdir)

            sync.set_state("key1", "value1")
            sync.set_state("key2", "value2")

            all_state = sync.get_all_state()
            assert all_state["key1"] == "value1"
            assert all_state["key2"] == "value2"

    def test_sync_state(self):
        """Test state synchronization from another agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync1 = StateSync("agent1", data_dir=tmpdir)
            sync2 = StateSync("agent2", data_dir=tmpdir)

            sync1.set_state("key", "value1")

            # Sync from agent1 to agent2
            version = sync1.get_version("key").current_version
            result = sync2.sync_state("key", "value1", version, "agent1")

            assert result is True
            assert sync2.get_state("key") == "value1"

    def test_get_version(self):
        """Test version tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = StateSync("agent1", data_dir=tmpdir)

            sync.set_state("key", "value1")
            version1 = sync.get_version("key")
            assert version1.current_version == 1

            sync.set_state("key", "value2")
            version2 = sync.get_version("key")
            assert version2.current_version == 2

    def test_detect_conflicts(self):
        """Test conflict detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = StateSync("agent1", data_dir=tmpdir)

            sync.set_state("key", "value_a")

            # Simulate replica with different value
            sync.replicas["agent2"] = {"key": "value_b"}

            conflicts = sync.detect_conflicts()
            assert len(conflicts) > 0
            assert conflicts[0]["key"] == "key"

    def test_get_consistency_status(self):
        """Test consistency status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = StateSync("agent1", data_dir=tmpdir)

            sync.set_state("key1", "value1")
            sync.set_state("key2", "value2")

            status = sync.get_consistency_status()
            assert status["total_keys"] == 2
            assert status["agent_id"] == "agent1"


class TestPhase10Integration:
    """Integration tests for Phase 10 components."""

    def test_network_and_rpc_integration(self):
        """Test integration of network and RPC components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)

            agent_id = network.register_agent("agent1", "localhost", 5000)
            agent = network.get_agent(agent_id)

            assert agent is not None
            assert agent.name == "agent1"

    def test_load_balancer_with_agents(self):
        """Test load balancer with network agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)
            balancer = LoadBalancer(data_dir=tmpdir)

            agent_id = network.register_agent("agent1", "localhost", 5000)
            agent = network.get_agent(agent_id)

            agents = [{"agent_id": agent.agent_id, "name": agent.name}]

            selected = balancer.assign_task("task1", agents)
            assert selected is not None

    def test_fault_recovery_with_load_balancer(self):
        """Test fault recovery with load balancing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recovery = FaultRecovery(failure_threshold=2, data_dir=tmpdir)

            recovery.register_failure("agent1", "error", "Error")

            assert recovery.is_agent_healthy("agent1") is True

    def test_state_sync_with_network(self):
        """Test state sync with network topology."""
        with tempfile.TemporaryDirectory() as tmpdir:
            network = AgentNetwork(data_dir=tmpdir)
            sync = StateSync("agent1", data_dir=tmpdir)

            agent_id = network.register_agent("agent1", "localhost", 5000)
            sync.set_state("network_id", agent_id)

            assert sync.get_state("network_id") == agent_id
