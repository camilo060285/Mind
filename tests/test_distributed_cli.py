"""Unit tests for distributed CLI handlers."""

import json
import socket
import tempfile

from mind.distributed import (
    RPCServer,
    AgentNetwork,
    LoadBalancer,
    FaultRecovery,
    StateSync,
)
from mind.cli.distributed_commands import DistributedCommandHandler


def test_net_register_and_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        net = AgentNetwork(data_dir=tmpdir)
        rpc = RPCServer(agent_id="a1", data_dir=tmpdir)
        lb = LoadBalancer(data_dir=tmpdir)
        fr = FaultRecovery(data_dir=tmpdir)
        ss = StateSync(agent_id="a1", data_dir=tmpdir)

        handler = DistributedCommandHandler(net, rpc, lb, fr, ss)

        aid = handler.handle_net_register("worker1 127.0.0.1 5001 processing,analysis")
        assert isinstance(aid, str) and len(aid) > 0

        out = handler.handle_net_list("")
        assert "worker1" in out


def test_state_set_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        net = AgentNetwork(data_dir=tmpdir)
        rpc = RPCServer(agent_id="a1", data_dir=tmpdir)
        lb = LoadBalancer(data_dir=tmpdir)
        fr = FaultRecovery(data_dir=tmpdir)
        ss = StateSync(agent_id="a1", data_dir=tmpdir)

        handler = DistributedCommandHandler(net, rpc, lb, fr, ss)

        cid = handler.handle_state_set('config {"mode":"fast"}')
        assert isinstance(cid, str)

        val = handler.handle_state_get("config")
        assert "fast" in val


def test_rpc_server_socket_listen():
    with tempfile.TemporaryDirectory() as tmpdir:
        rpc = RPCServer(agent_id="cli_test", data_dir=tmpdir)

        # register a simple method
        def mul(a: int, b: int) -> int:
            return a * b

        rpc.register_method("mul", mul)

        # start listening on ephemeral port (use framed=False for newline-delimited)
        port = rpc.start_listening(host="127.0.0.1", port=0, framed=False)
        assert port > 0

        # Send a request over TCP and read response
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)  # 2-second timeout to prevent hanging
        s.connect(("127.0.0.1", port))
        req = {
            "jsonrpc": "2.0",
            "method": "mul",
            "params": {"a": 6, "b": 7},
            "id": "r1",
        }
        s.sendall((json.dumps(req) + "\n").encode())

        # read response line
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()

        resp = json.loads(data.decode())
        assert resp.get("result") == 42

        rpc.stop_listening()
