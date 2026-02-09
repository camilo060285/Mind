"""JSON-RPC 2.0 server for inter-agent communication.

Implements JSON-RPC 2.0 specification for remote procedure calls
between distributed agents.
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RPCRequest:
    """JSON-RPC 2.0 request."""

    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RPCResponse:
    """JSON-RPC 2.0 response."""

    jsonrpc: str = "2.0"
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        resp: Dict[str, Any] = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
        }
        if self.error:
            resp["error"] = self.error
        else:
            resp["result"] = self.result
        return resp


@dataclass
class RPCCall:
    """Record of an RPC call execution."""

    request_id: str
    method: str
    agent_id: str
    timestamp: str
    execution_time: float
    success: bool
    error: Optional[str] = None


class RPCServer:
    """JSON-RPC 2.0 server for agent communication."""

    def __init__(self, agent_id: str, data_dir: Optional[str] = None):
        """Initialize RPC server.

        Args:
            agent_id: ID of agent running this server
            data_dir: Directory for call history persistence
        """
        self.agent_id = agent_id
        self.methods: Dict[str, Callable] = {}
        self.call_history: Dict[str, RPCCall] = {}

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".mind_rpc")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.calls_file = self.data_dir / f"{agent_id}_calls.jsonl"
        self._load_calls()
        logger.info(f"RPCServer initialized for agent: {agent_id}")

        # Networking (typed as Optional to satisfy static type checks)
        from typing import Optional as _Opt

        self._server_socket: _Opt[Any] = None
        self._listening_thread: _Opt[Any] = None
        self._stop_event: _Opt[Any] = None

    def register_method(self, name: str, method: Callable) -> None:
        """Register an RPC method.

        Args:
            name: Method name
            method: Callable to execute
        """
        self.methods[name] = method
        logger.debug(f"RPC method registered: {name}")

    def handle_request(self, request_data: str) -> str:
        """Handle incoming RPC request.

        Args:
            request_data: JSON-RPC request string

        Returns:
            JSON-RPC response string
        """
        try:
            req_dict = json.loads(request_data)
        except json.JSONDecodeError as e:
            return self._error_response(None, -32700, f"Parse error: {e}")

        # Validate RPC structure
        if not isinstance(req_dict, dict):
            return self._error_response(None, -32600, "Invalid Request: not a dict")

        if req_dict.get("jsonrpc") != "2.0":
            return self._error_response(
                req_dict.get("id"), -32600, "Invalid Request: invalid jsonrpc"
            )

        method = req_dict.get("method")
        if not method:
            return self._error_response(
                req_dict.get("id"), -32600, "Invalid Request: no method"
            )

        # Check if method exists
        if method not in self.methods:
            return self._error_response(
                req_dict.get("id"), -32601, f"Method not found: {method}"
            )

        # Execute method and measure time
        params = req_dict.get("params", {})
        request_id = req_dict.get("id", str(uuid.uuid4()))
        start_time = time.time()

        try:
            result = self.methods[method](**params)
            execution_time = time.time() - start_time

            # Record successful call
            call = RPCCall(
                request_id=request_id,
                method=method,
                agent_id=self.agent_id,
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time,
                success=True,
            )
            self.call_history[request_id] = call
            self._save_call(call)

            response = RPCResponse(result=result, id=request_id)
            return json.dumps(response.to_dict())

        except TypeError as e:
            execution_time = time.time() - start_time
            error_msg = f"Invalid params: {e}"

            call = RPCCall(
                request_id=request_id,
                method=method,
                agent_id=self.agent_id,
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time,
                success=False,
                error=error_msg,
            )
            self.call_history[request_id] = call
            self._save_call(call)

            return self._error_response(request_id, -32602, error_msg)

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Server error: {str(e)}"

            call = RPCCall(
                request_id=request_id,
                method=method,
                agent_id=self.agent_id,
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time,
                success=False,
                error=error_msg,
            )
            self.call_history[request_id] = call
            self._save_call(call)

            return self._error_response(request_id, -32603, error_msg)

    def get_call(self, request_id: str) -> Optional[RPCCall]:
        """Get information about an RPC call.

        Args:
            request_id: Request ID

        Returns:
            Call record or None
        """
        return self.call_history.get(request_id)

    def get_recent_calls(self, limit: int = 10) -> list[RPCCall]:
        """Get recent RPC calls.

        Args:
            limit: Maximum number of calls to return

        Returns:
            List of recent calls
        """
        calls = list(self.call_history.values())
        return sorted(calls, key=lambda c: c.timestamp, reverse=True)[:limit]

    def get_call_statistics(self) -> Dict[str, Any]:
        """Get statistics about RPC calls.

        Returns:
            Statistics dictionary
        """
        if not self.call_history:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "methods": {},
            }

        calls = list(self.call_history.values())
        successful = [c for c in calls if c.success]
        failed = [c for c in calls if not c.success]

        # Group by method
        method_stats: Dict[str, Dict[str, Any]] = {}
        for call in calls:
            if call.method not in method_stats:
                method_stats[call.method] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                }

            method_stats[call.method]["count"] += 1
            if call.success:
                method_stats[call.method]["successful"] += 1
            else:
                method_stats[call.method]["failed"] += 1
            method_stats[call.method]["total_time"] += call.execution_time

        # Calculate averages
        for stats in method_stats.values():
            if stats["count"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["count"]

        total_time = sum(c.execution_time for c in calls)
        avg_time = total_time / len(calls) if calls else 0.0

        return {
            "agent_id": self.agent_id,
            "total_calls": len(calls),
            "successful_calls": len(successful),
            "failed_calls": len(failed),
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "methods": method_stats,
        }

    def start_listening(self, host: str = "0.0.0.0", port: int = 0) -> int:
        """Start a simple TCP listener that accepts JSON-RPC requests line-delimited.

        Args:
            host: Host to bind
            port: Port to bind (0 picks an ephemeral port)

        Returns:
            The port number the server is listening on
        """
        import socket
        import threading

        if self._server_socket is not None:
            raise RuntimeError("Server already listening")

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)

        self._stop_event = threading.Event()
        self._server_socket = srv

        def _accept_loop(sock, stop_event):
            while not stop_event.is_set():
                try:
                    sock.settimeout(0.5)
                    conn, addr = sock.accept()
                except Exception:
                    continue

                # Handle connection in a short-lived thread
                def _handle_conn(c):
                    with c:
                        data = b""
                        try:
                            # read until newline
                            while not data.endswith(b"\n"):
                                chunk = c.recv(4096)
                                if not chunk:
                                    break
                                data += chunk
                            if not data:
                                return
                            req_str = data.decode().strip()
                            resp = self.handle_request(req_str)
                            c.sendall((resp + "\n").encode())
                        except Exception:
                            try:
                                c.sendall(
                                    (
                                        json.dumps(
                                            {
                                                "jsonrpc": "2.0",
                                                "error": {
                                                    "code": -32603,
                                                    "message": "server error",
                                                },
                                                "id": "",
                                            }
                                        )
                                        + "\n"
                                    ).encode()
                                )
                            except Exception:
                                pass

                t = threading.Thread(target=_handle_conn, args=(conn,))
                t.daemon = True
                t.start()

        t = threading.Thread(target=_accept_loop, args=(srv, self._stop_event))
        t.daemon = True
        t.start()

        self._listening_thread = t
        bound_port = srv.getsockname()[1]
        logger.info(f"RPCServer listening on {host}:{bound_port}")
        return bound_port

    def stop_listening(self) -> None:
        """Stop the TCP listener if running."""
        if self._stop_event is not None:
            self._stop_event.set()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
        self._server_socket = None
        self._listening_thread = None
        self._stop_event = None

    def clear_history(self) -> None:
        """Clear call history."""
        self.call_history.clear()
        logger.info(f"RPC call history cleared for agent: {self.agent_id}")

    # Private methods

    def _error_response(
        self, request_id: Optional[str], code: int, message: str
    ) -> str:
        """Generate JSON-RPC error response.

        Args:
            request_id: Request ID
            code: Error code
            message: Error message

        Returns:
            JSON-RPC error response
        """
        response = RPCResponse(
            error={"code": code, "message": message},
            id=request_id or "",
        )
        return json.dumps(response.to_dict())

    def _save_call(self, call: RPCCall) -> None:
        """Save call to file."""
        try:
            with open(self.calls_file, "a") as f:
                f.write(json.dumps(asdict(call)) + "\n")
        except (OSError, IOError) as e:
            logger.error(f"Error saving RPC call: {e}")

    def _load_calls(self) -> None:
        """Load call history from file."""
        if not self.calls_file.exists():
            return

        try:
            with open(self.calls_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        call = RPCCall(**data)
                        self.call_history[call.request_id] = call
                    except (json.JSONDecodeError, TypeError):
                        continue
        except (OSError, IOError) as e:
            logger.error(f"Error loading RPC calls: {e}")
