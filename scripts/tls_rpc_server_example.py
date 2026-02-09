"""Example TLS-enabled RPC server using the framed protocol.

Usage:
    python scripts/tls_rpc_server_example.py --cert cert.pem --key key.pem --host 127.0.0.1 --port 5001

This example registers a simple `echo` method and starts the `RPCServer` with
length-prefixed framing and TLS enabled.
"""

import argparse
import signal
import sys
from mind.distributed.rpc_server import RPCServer


def echo(message: str = ""):
    return {"echo": message}


def main():
    parser = argparse.ArgumentParser(description="TLS RPCServer example")
    parser.add_argument("--cert", required=True, help="Path to PEM certificate file")
    parser.add_argument("--key", required=True, help="Path to PEM private key file")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    srv = RPCServer(agent_id="tls-example")
    srv.register_method("echo", echo)

    port = srv.start_listening(
        host=args.host,
        port=args.port,
        framed=True,
        use_tls=True,
        certfile=args.cert,
        keyfile=args.key,
    )
    print(f"TLS RPCServer listening on {args.host}:{port} (framed)")

    def _shutdown(signum, frame):
        print("Stopping server...")
        srv.stop_listening()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Block until interrupted
    signal.pause()


if __name__ == "__main__":
    main()
