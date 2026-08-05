"""CLI entry point: ``tokopedia-mcp`` or ``python -m tokopedia_mcp``."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Tokopedia MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for network transports")
    parser.add_argument("--port", type=int, default=8000, help="Bind port for network transports")
    args = parser.parse_args()

    from .server import create_server

    # MCPServer.run() is the canonical (synchronous) entry point; it wraps the
    # async runners with anyio and defaults to stdio.
    create_server().run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
