"""v1 is public-only: only market tools register, regardless of creds."""

import asyncio

from delta_exchange_mcp.server import build_server


MARKET_TOOLS = {
    "list_products",
    "get_product",
    "get_ticker",
    "list_tickers",
    "get_orderbook",
    "get_recent_trades",
    "get_candles",
    "get_options_chain",
    "get_reference_data",
}

ACCOUNT_TOOLS = {
    "get_balances",
    "get_positions",
    "get_open_orders",
    "get_order_history",
    "get_order",
    "get_fills",
    "get_profile",
}


def _tool_names(mcp) -> set[str]:
    return {t.name for t in asyncio.run(mcp.list_tools())}


def test_v1_registers_only_market_tools_without_creds(monkeypatch):
    monkeypatch.delenv("DELTA_API_KEY", raising=False)
    monkeypatch.delenv("DELTA_API_SECRET", raising=False)
    names = _tool_names(build_server())
    assert MARKET_TOOLS.issubset(names)
    assert ACCOUNT_TOOLS.isdisjoint(names)


def test_v1_still_public_only_even_with_creds(monkeypatch):
    """Account tools are v2 material — creds in env must not accidentally enable them."""
    monkeypatch.setenv("DELTA_API_KEY", "k")
    monkeypatch.setenv("DELTA_API_SECRET", "s")
    names = _tool_names(build_server())
    assert MARKET_TOOLS.issubset(names)
    assert ACCOUNT_TOOLS.isdisjoint(names)
