from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from delta_exchange_mcp import config as config_mod
from delta_exchange_mcp.client import DeltaClient
from delta_exchange_mcp.tools import market


def build_server(cfg: config_mod.Config | None = None) -> FastMCP:
    cfg = cfg or config_mod.load()

    if cfg.transport == "http":
        mcp = FastMCP(
            "delta-exchange",
            host=cfg.http_host,
            port=cfg.http_port,
            stateless_http=True,
            json_response=True,
        )
    else:
        mcp = FastMCP("delta-exchange")

    client = DeltaClient(cfg)
    market.register(mcp, client)
    # Account-read + trading tools arrive in v2 with API-key auth.
    return mcp


def main() -> None:
    cfg = config_mod.load()
    mcp = build_server(cfg)

    if cfg.transport == "http":
        print(
            f"[delta-exchange-mcp] http transport on {cfg.http_host}:{cfg.http_port} "
            f"env={cfg.env} base_url={cfg.base_url}",
            file=sys.stderr,
        )
        mcp.run(transport="streamable-http")
    else:
        print(
            f"[delta-exchange-mcp] stdio transport env={cfg.env} base_url={cfg.base_url}",
            file=sys.stderr,
        )
        mcp.run()
