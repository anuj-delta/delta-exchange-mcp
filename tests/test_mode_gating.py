"""Verify tool registration respects creds gating."""

import asyncio
import pytest

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


def test_no_creds_registers_only_market_tools(monkeypatch):
    monkeypatch.delenv("DELTA_API_KEY", raising=False)
    monkeypatch.delenv("DELTA_API_SECRET", raising=False)
    names = _tool_names(build_server())
    assert MARKET_TOOLS.issubset(names)
    assert ACCOUNT_TOOLS.isdisjoint(names)


def test_with_creds_registers_both_groups(monkeypatch):
    monkeypatch.setenv("DELTA_API_KEY", "k")
    monkeypatch.setenv("DELTA_API_SECRET", "s")
    names = _tool_names(build_server())
    assert MARKET_TOOLS.issubset(names)
    assert ACCOUNT_TOOLS.issubset(names)


def test_trade_mode_rejected_even_with_creds(monkeypatch):
    monkeypatch.setenv("DELTA_API_KEY", "k")
    monkeypatch.setenv("DELTA_API_SECRET", "s")
    monkeypatch.setenv("DELTA_MCP_MODE", "trade")
    with pytest.raises(ValueError, match="v1"):
        build_server()
