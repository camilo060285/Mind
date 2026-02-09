"""Simple framed-protocol RPC client with optional TLS.

Sends a length-prefixed JSON-RPC request and prints the response.

Usage:
    python scripts/framed_rpc_client_example.py --host 127.0.0.1 --port 5001 --method echo --params '{"message": "hello"}' --tls

If `--tls` is provided the client will use an SSL context that does not verify
by default (for demo). For production, enable certificate verification.
"""

import argparse
import json
import socket
import ssl


def send_framed(host: str, port: int, payload: str, use_tls: bool = False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if use_tls:
        ctx = ssl.create_default_context()
        # For demo purposes skip verification (not recommended for production)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(s, server_hostname=host)

    s.connect((host, port))
    try:
        data = payload.encode()
        header = len(data).to_bytes(4, byteorder="big")
        s.sendall(header + data)

        # Read 4-byte length
        hdr = s.recv(4)
        if len(hdr) != 4:
            raise RuntimeError("Incomplete response header")
        resp_len = int.from_bytes(hdr, byteorder="big")
        resp = b""
        while len(resp) < resp_len:
            chunk = s.recv(resp_len - len(resp))
            if not chunk:
                break
            resp += chunk
        return resp.decode()
    finally:
        s.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--params", default="{}")
    parser.add_argument("--tls", action="store_true")
    args = parser.parse_args()

    params = json.loads(args.params)
    req = {"jsonrpc": "2.0", "method": args.method, "params": params, "id": "cli-1"}
    payload = json.dumps(req)

    resp = send_framed(args.host, args.port, payload, use_tls=args.tls)
    print("Response:", resp)


if __name__ == "__main__":
    main()
