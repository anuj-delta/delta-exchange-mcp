from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from delta_exchange_mcp import config as config_mod
from delta_exchange_mcp.client import DeltaClient
from delta_exchange_mcp.tools import account, market


def build_server() -> FastMCP:
    cfg = config_mod.load()
    mcp = FastMCP("delta-exchange")
    client = DeltaClient(cfg)

    market.register(mcp, client)
    if cfg.has_credentials:
        account.register(mcp, client)
    else:
        print(
            "[delta-exchange-mcp] no DELTA_API_KEY / DELTA_API_SECRET — "
            "account-read tools disabled, market-data tools only.",
            file=sys.stderr,
        )

    if cfg.mode == "trade":
        print(
            "[delta-exchange-mcp] WARNING: mode=trade requested but trading ships in v2.",
            file=sys.stderr,
        )

    print(
        f"[delta-exchange-mcp] env={cfg.env} mode={cfg.mode} "
        f"base_url={cfg.base_url}",
        file=sys.stderr,
    )
    return mcp


def main() -> None:
    mcp = build_server()
    mcp.run()  # stdio transport (default)
