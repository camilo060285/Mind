# RPC Example Scripts

This directory contains example scripts demonstrating the distributed RPC capabilities with both framed protocol and TLS support.

## framed_rpc_client_example.py

A client that sends JSON-RPC requests using the **framed protocol** (length-prefixed messages).

**Usage:**
```bash
# Send a request to an echo method
python scripts/framed_rpc_client_example.py \
  --host 127.0.0.1 \
  --port 5001 \
  --method echo \
  --params '{"message": "hello world"}'

# With TLS enabled
python scripts/framed_rpc_client_example.py \
  --host 127.0.0.1 \
  --port 5001 \
  --method echo \
  --params '{"message": "hello"}' \
  --tls
```

**Protocol Details:**
- Each message is prefixed with a 4-byte big-endian length header
- Format: `[4-byte length] [JSON payload]`
- Server responds with same framing
- Recommended for production use (reliable framing, handles partial reads)

## tls_rpc_server_example.py

A server that uses both **framed protocol** and **TLS encryption**.

**Usage:**
```bash
# First generate a self-signed certificate (for demo)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

# Start the server
python scripts/tls_rpc_server_example.py \
  --cert cert.pem \
  --key key.pem \
  --host 127.0.0.1 \
  --port 5001
```

**Features:**
- Listens on configurable host/port
- TLS encryption for all connections
- Registers an `echo` method as example
- Uses length-prefixed framing for reliable message boundaries
- Graceful shutdown on SIGINT/SIGTERM

## Quick Demo

Start the server in one terminal:
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
python scripts/tls_rpc_server_example.py --cert cert.pem --key key.pem
```

Call it from another terminal:
```bash
python scripts/framed_rpc_client_example.py \
  --host 127.0.0.1 \
  --port <PORT_FROM_SERVER> \
  --method echo \
  --params '{"message": "RPC over TLS works!"}' \
  --tls
```

## Extending the Examples

- Add new methods to the server by calling `srv.register_method(name, callable)`
- The framed client can be used as a template for non-TLS framed connections (omit `--tls`)
- Both support custom parameters via JSON in `--params`
