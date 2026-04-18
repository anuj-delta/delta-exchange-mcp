"""Public market-data tools (M1 — to be fleshed out)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from delta_exchange_mcp.client import DeltaClient


def register(mcp: FastMCP, client: DeltaClient) -> None:
    # TODO M1: list_products, get_product, get_ticker, get_orderbook,
    # get_recent_trades, get_candles, get_options_chain, get_reference_data.
    pass
