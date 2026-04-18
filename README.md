# delta-exchange-mcp

Unofficial MCP (Model Context Protocol) server for **Delta Exchange India** — lets AI assistants (Claude Desktop, Cursor, Zed, Claude Code) query Delta Exchange public market data through standardized tools.

> **v1 scope**: 9 public market-data tools. No credentials required, no mutating actions. Account-read + trading arrive together in v2.

## Quick start

```json
{
  "mcpServers": {
    "delta-exchange": {
      "command": "uvx",
      "args": ["delta-exchange-mcp"],
      "env": { "DELTA_MCP_ENV": "india_prod" }
    }
  }
}
```

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `DELTA_MCP_ENV` | `india_prod` | Target environment. Valid: `india_prod`, `india_testnet`. |

`DELTA_API_KEY` / `DELTA_API_SECRET` are **not** used by v1. They'll be introduced in v2 alongside trading tools.

## Tools (v1)

- `list_products` / `get_product`
- `get_ticker` / `list_tickers` / `get_options_chain`
- `get_orderbook`
- `get_recent_trades` / `get_candles`
- `get_reference_data` (assets + indices)

## Development

```bash
uv sync
uv run pytest
uv run delta-exchange-mcp   # starts stdio server (defaults to india_prod)
DELTA_MCP_ENV=india_testnet uv run delta-exchange-mcp   # testnet
```

### Testing with MCP Inspector

Run the official [MCP Inspector](https://github.com/modelcontextprotocol/inspector) against this server — useful for exercising each tool without wiring it into a chat client.

**CLI mode (headless, works over SSH — recommended for remote hosts):**

```bash
bash scripts/inspect.sh --cli --method tools/list
bash scripts/inspect.sh --cli --method tools/call \
  --tool-name get_ticker --tool-arg symbol=BTCUSD
```

**Web UI mode:**

```bash
bash scripts/inspect.sh
# → UI on http://localhost:6274, proxy on :6277
```

The helper binds to `0.0.0.0` by default; open `http://<host>:6274` from your laptop, or SSH-forward with `ssh -L 6274:localhost:6274 -L 6277:localhost:6277 <host>`.

## Roadmap

- **v1** (current): 9 public market-data tools, stdio transport, no auth.
- **v2**: HMAC auth, account-read (balances/positions/orders/fills), trading (place/edit/cancel/close/leverage) gated by `DELTA_MCP_MODE=trade`, audit log, guardrails.

## Safety

- **No trading in v1.** No mutating tools exist — the server is a pure read-only wrapper over public endpoints.
- Unofficial — not affiliated with Delta Exchange. Use at your own risk.
