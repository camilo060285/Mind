"""CLI handlers for distributed features."""

import json
import uuid

from mind.distributed import (
    AgentNetwork,
    LoadBalancer,
    LoadBalancingStrategy,
    RPCServer,
    FaultRecovery,
    StateSync,
)


class DistributedCommandHandler:
    """Command handler exposing distributed operations to the CLI.

    Each handler returns a short string or serialized data to be printed by the
    interactive shell. Usage examples are provided in the command descriptions
    registered by the interactive shell.
    """

    def __init__(
        self,
        network: AgentNetwork,
        rpc: RPCServer,
        load_balancer: LoadBalancer,
        recovery: FaultRecovery,
        state_sync: StateSync,
    ) -> None:
        self.network = network
        self.rpc = rpc
        self.load_balancer = load_balancer
        self.recovery = recovery
        self.state_sync = state_sync

    # Network commands
    def handle_net_register(self, args: str) -> str:
        """Register an agent: net_register <name> <host> <port> [cap1,cap2]

        Example: net_register worker1 127.0.0.1 5005 processing,analysis

        Returns:
            agent_id string on success or usage message on failure
        """
        parts = args.split()
        if len(parts) < 3:
            return "Usage: net_register <name> <host> <port> [cap1,cap2]"

        name, host, port_str = parts[0], parts[1], parts[2]
        try:
            port = int(port_str)
        except ValueError:
            return "Port must be an integer"

        caps = []
        if len(parts) > 3:
            caps = [c.strip() for c in " ".join(parts[3:]).split(",") if c.strip()]

        agent_id = self.network.register_agent(name, host, port, capabilities=caps)
        return agent_id

    def handle_net_list(self, args: str) -> str:
        """List agents or filter by capability: net_list [capability]

        Example: net_list processing
        """
        cap = args.strip() or None
        if cap:
            agents = self.network.get_agents_by_capability(cap)
        else:
            agents = list(self.network.agents.values())

        out = []
        for a in agents:
            out.append(f"{a.agent_id} - {a.name} @ {a.host}:{a.port} ({a.status})")
        return "\n".join(out) if out else "No agents found"

    # RPC commands
    def handle_rpc_call(self, args: str) -> str:
        """Call an RPC method: rpc_call <method> [<params-json>]

        Example: rpc_call add '{"a":2,"b":3}'
        """
        parts = args.split(None, 1)
        if not parts:
            return "Usage: rpc_call <method> [params_json]"

        method = parts[0]
        params = {}
        if len(parts) > 1:
            try:
                params = json.loads(parts[1])
            except json.JSONDecodeError:
                return "Params must be valid JSON"

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": str(uuid.uuid4()),
        }
        response = self.rpc.handle_request(json.dumps(request))
        return response

    # Load balancer commands
    def handle_lb_assign(self, args: str) -> str:
        """Assign a task: lb_assign <task_id> <agent1,agent2,...> [strategy]

        Example: lb_assign task42 agent1,agent2 round_robin
        """
        parts = args.split()
        if len(parts) < 2:
            return "Usage: lb_assign <task_id> <agent1,agent2,...> [strategy]"

        task_id = parts[0]
        agent_ids = [a.strip() for a in parts[1].split(",") if a.strip()]
        agents = [{"agent_id": aid, "name": aid} for aid in agent_ids]
        strategy = (
            parts[2] if len(parts) > 2 else LoadBalancingStrategy.LEAST_LOADED.value
        )

        try:
            strat_enum = LoadBalancingStrategy(strategy)
        except Exception:
            strat_enum = LoadBalancingStrategy.LEAST_LOADED

        selected = self.load_balancer.assign_task(task_id, agents, strategy=strat_enum)
        return str(selected) if selected else "No agent selected"

    def handle_lb_stats(self, args: str) -> str:
        """Return load balancer statistics.

        Example: lb_stats
        """
        return str(self.load_balancer.get_load_statistics())

    # State sync commands
    def handle_state_set(self, args: str) -> str:
        """Set state: state_set <key> <value-json-or-string>

        Example: state_set config '{"mode": "fast"}'
        """
        parts = args.split(None, 1)
        if not parts:
            return "Usage: state_set <key> <value>"
        key = parts[0]
        value = parts[1] if len(parts) > 1 else ""
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = value

        change_id = self.state_sync.set_state(key, parsed)
        return change_id

    def handle_state_get(self, args: str) -> str:
        """Get state: state_get <key>

        Example: state_get config
        """
        key = args.strip()
        if not key:
            return "Usage: state_get <key>"
        val = self.state_sync.get_state(key)
        return str(val)
