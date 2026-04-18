"""Private account-read tools (M2). Registered only when creds are present."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from delta_exchange_mcp.client import DeltaClient


def _csv(values: list[str] | None) -> str | None:
    if not values:
        return None
    return ",".join(values)


def _csv_ints(values: list[int] | None) -> str | None:
    if not values:
        return None
    return ",".join(str(v) for v in values)


def register(mcp: FastMCP, client: DeltaClient) -> None:
    @mcp.tool()
    async def get_balances() -> dict[str, Any]:
        """Wallet balances across all assets. Fields: asset_symbol, balance, available_balance, position_margin."""
        return await client.get("/wallet/balances", auth=True)

    @mcp.tool()
    async def get_positions(
        product_id: int | None = Field(default=None, description="Single product id."),
        underlying_asset_symbol: str | None = Field(
            default=None, description="Underlying asset symbol (e.g. BTC) — returns all positions under it."
        ),
    ) -> dict[str, Any]:
        """Open positions. Pass product_id OR underlying_asset_symbol. Omit both to get all margined positions."""
        if product_id is None and not underlying_asset_symbol:
            return await client.get("/positions/margined", auth=True)
        return await client.get(
            "/positions",
            params={"product_id": product_id, "underlying_asset_symbol": underlying_asset_symbol},
            auth=True,
        )

    @mcp.tool()
    async def get_open_orders(
        product_ids: list[int] | None = Field(default=None, description="Max 10 product ids."),
        states: list[str] | None = Field(default=None, description="Subset of: open, pending."),
        contract_types: list[str] | None = Field(default=None),
        page_size: int = Field(default=50, ge=1, le=200),
        after: str | None = Field(default=None, description="Cursor from previous response's meta.after."),
    ) -> dict[str, Any]:
        """Current open/pending orders. Paginated via meta.after / meta.before."""
        return await client.get(
            "/orders",
            params={
                "product_ids": _csv_ints(product_ids),
                "states": _csv(states),
                "contract_types": _csv(contract_types),
                "page_size": page_size,
                "after": after,
            },
            auth=True,
        )

    @mcp.tool()
    async def get_order_history(
        product_ids: list[int] | None = None,
        contract_types: list[str] | None = None,
        order_types: list[str] | None = Field(
            default=None, description="market, limit, stop_market, stop_limit, all_stop."
        ),
        start_time_us: int | None = Field(default=None, description="Microseconds epoch (note: micro, not milli)."),
        end_time_us: int | None = None,
        page_size: int = Field(default=50, ge=1, le=200),
        after: str | None = None,
    ) -> dict[str, Any]:
        """Closed / cancelled orders, filterable + paginated. Timestamps are microseconds."""
        return await client.get(
            "/orders/history",
            params={
                "product_ids": _csv_ints(product_ids),
                "contract_types": _csv(contract_types),
                "order_types": _csv(order_types),
                "start_time": start_time_us,
                "end_time": end_time_us,
                "page_size": page_size,
                "after": after,
            },
            auth=True,
        )

    @mcp.tool()
    async def get_order(
        order_id: int | None = Field(default=None, description="Delta-assigned order id."),
        client_order_id: str | None = Field(default=None, description="Your client_order_id if you set one."),
    ) -> dict[str, Any]:
        """Fetch a single order by id or client_order_id. Exactly one must be provided."""
        if (order_id is None) == (not client_order_id):
            raise ValueError("pass exactly one of order_id or client_order_id")
        if order_id is not None:
            return await client.get(f"/orders/{order_id}", auth=True)
        return await client.get(f"/orders/client_order_id/{client_order_id}", auth=True)

    @mcp.tool()
    async def get_fills(
        product_ids: list[int] | None = None,
        contract_types: list[str] | None = None,
        start_time_us: int | None = Field(default=None, description="Microseconds epoch."),
        end_time_us: int | None = None,
        page_size: int = Field(default=50, ge=1, le=200),
        after: str | None = None,
    ) -> dict[str, Any]:
        """Your trade fills (executed trades). Paginated. Timestamps are microseconds."""
        return await client.get(
            "/fills",
            params={
                "product_ids": _csv_ints(product_ids),
                "contract_types": _csv(contract_types),
                "start_time": start_time_us,
                "end_time": end_time_us,
                "page_size": page_size,
                "after": after,
            },
            auth=True,
        )

    @mcp.tool()
    async def get_profile() -> dict[str, Any]:
        """User profile merged with trading preferences (margin mode, notifications, etc.)."""
        profile = await client.get("/profile", auth=True)
        try:
            prefs = await client.get("/users/trading_preferences", auth=True)
        except Exception as e:  # noqa: BLE001 — prefs is best-effort, don't fail profile lookup
            prefs = {"error": str(e)}
        return {"profile": profile, "trading_preferences": prefs}
