from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from delta_exchange_mcp import config as config_mod
from delta_exchange_mcp.client import DeltaClient
from delta_exchange_mcp.tools import market


def build_server() -> FastMCP:
    cfg = config_mod.load()
    mcp = FastMCP("delta-exchange")
    client = DeltaClient(cfg)

    market.register(mcp, client)
    # Account-read and trading tools arrive in v2 along with API-key auth.
    # See delta_exchange_mcp/tools/account.py — registration is intentionally
    # omitted here to keep v1 a pure public-market-data server.

    print(
        f"[delta-exchange-mcp] env={cfg.env} base_url={cfg.base_url}",
        file=sys.stderr,
    )
    return mcp


def main() -> None:
    build_server().run()  # stdio transport (default)
