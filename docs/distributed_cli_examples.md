# Distributed CLI Examples

This page contains example usages for the distributed CLI commands available in the interactive shell.

## Register an agent
- Register a new agent in the network:

```
net_register my-agent 127.0.0.1 5001 cpu,gpu
```

## List agents
- List all agents or filter by capability:

```
net_list
net_list gpu
```

## Call RPC method
- Call an RPC method on a remote agent (JSON params):

```
rpc_call add_numbers {"a": 1, "b": 2}
```

- When using framed transport (recommended): send/receive with a 4-byte big-endian length prefix.

## Load balancer
- Assign a task to agents:

```
lb_assign task-123 agent1,agent2 round_robin
```

- Show stats:

```
lb_stats
```

## Distributed state
- Set state:

```
state_set my_key some_value
```

- Get state:

```
state_get my_key
```

Notes:
- For production, prefer the framed protocol (length-prefixed) or enable TLS for the RPC server.
- To enable TLS, start the RPC server with a certificate and key and set `use_tls=True`.

