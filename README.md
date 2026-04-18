# delta-exchange-mcp

Unofficial MCP (Model Context Protocol) server for **Delta Exchange India** — lets AI assistants (Claude Desktop, Cursor, Zed, …) query Delta Exchange market data and your account state through standardized tools.

> **v1 is read-only.** Market data (public) + account read (private). Trading tools are planned for v2. Testnet is the default environment — mainnet is opt-in.

## Status

**v0.1.0 — M0 bootstrap.** Project scaffold only; tool implementations land in M1/M2.

## Quick start (once published)

```json
{
  "mcpServers": {
    "delta-exchange": {
      "command": "uvx",
      "args": ["delta-exchange-mcp"],
      "env": {
        "DELTA_API_KEY": "...",
        "DELTA_API_SECRET": "...",
        "DELTA_MCP_ENV": "testnet"
      }
    }
  }
}
```

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `DELTA_MCP_ENV` | `testnet` | `testnet` or `mainnet`. Mainnet is explicit opt-in. |
| `DELTA_MCP_MODE` | `read` | `read` or `trade`. `trade` is v2-only; v1 rejects it. |
| `DELTA_API_KEY` | — | Delta API key. Required for account-read tools. |
| `DELTA_API_SECRET` | — | Delta API secret. Required for account-read tools. |

Account-read tools are registered only when both credentials are present. Without them, the server still starts with market-data tools only.

## Safety

- **Secrets are env-var only.** Never paste your key/secret into chat as tool arguments.
- **Testnet by default.** Mainnet requires setting `DELTA_MCP_ENV=mainnet` explicitly.
- **No trading in v1.** No mutating tools exist — no place/edit/cancel order, no leverage change, no withdrawal.
- Unofficial — not affiliated with Delta Exchange. Use at your own risk.

## Development

```bash
uv sync
uv run pytest
uv run delta-exchange-mcp   # starts stdio server
```

### Testing with MCP Inspector

Run the official [MCP Inspector](https://github.com/modelcontextprotocol/inspector) against this server — useful for exercising each tool without wiring it into a chat client.

**CLI mode (headless, works over SSH — recommended for remote hosts):**

```bash
# list registered tools
bash scripts/inspect.sh --cli --method tools/list

# call a tool
bash scripts/inspect.sh --cli --method tools/call \
  --tool-name get_ticker --tool-arg symbol=BTCUSD

# with credentials (enables account-read tools)
DELTA_API_KEY=... DELTA_API_SECRET=... \
  bash scripts/inspect.sh --cli --method tools/call --tool-name get_balances
```

**Web UI mode:**

```bash
bash scripts/inspect.sh
# → UI on http://localhost:6274, proxy on :6277
```

The helper binds to `0.0.0.0` by default; open `http://<tailscale-ip>:6274` from your laptop, or SSH-forward with `ssh -L 6274:localhost:6274 -L 6277:localhost:6277 <host>`.

## Roadmap

- **M1**: 8 market-data tools (products, ticker, orderbook, candles, options chain, …).
- **M2**: 7 account-read tools (balances, positions, orders, fills, profile).
- **M3**: polish + PyPI 1.0.0.
- **v2**: trading tools gated by `DELTA_MCP_MODE=trade`, audit log, guardrails.
