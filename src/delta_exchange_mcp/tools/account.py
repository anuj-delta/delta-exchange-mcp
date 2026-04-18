"""Private account-read tools (M2 — registered only when creds present)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from delta_exchange_mcp.client import DeltaClient


def register(mcp: FastMCP, client: DeltaClient) -> None:
    # TODO M2: get_balances, get_positions, get_open_orders, get_order_history,
    # get_order, get_fills, get_profile.
    pass
