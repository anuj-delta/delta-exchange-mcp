# delta-exchange-mcp

Unofficial MCP (Model Context Protocol) server for **Delta Exchange India** — lets AI assistants (Claude Desktop, Cursor, Zed, Claude Code) query Delta Exchange market data and your own account read-only data through standardized tools.

> **Scope**: 9 public market-data tools + 12 authenticated read-only account tools (positions, orders, fills, wallet, stats, leverage, preferences, profile). All read-only — no order placement / mutation.

## Installation

This server is **local-only** (stdio transport). Each user runs it as a subprocess of their MCP client. Because it's a financial-tool MCP, users should be able to read the code running against their account — no shared hosted endpoint is provided.

Repo access: `github.com/anuj-delta/delta-exchange-mcp` (private). Ensure your GitHub account has read access and an SSH key or `gh auth login` set up.

**Prerequisite:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/) on your machine.

```bash
# sanity-check the install works before wiring up your MCP client
uvx --from git+https://github.com/anuj-delta/delta-exchange-mcp.git delta-exchange-mcp --help
```

Add to your MCP client config (Claude Desktop, Claude Code, Cursor, Zed, etc.):

```json
{
  "mcpServers": {
    "delta-exchange": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/anuj-delta/delta-exchange-mcp.git",
        "delta-exchange-mcp"
      ],
      "env": {
        "DELTA_MCP_ENV": "india_prod",
        "DELTA_API_KEY": "your-api-key",
        "DELTA_API_SECRET": "your-api-secret"
      }
    }
  }
}
```

`DELTA_API_KEY` / `DELTA_API_SECRET` are **optional**. Without them, only the public market tools register. Set both to unlock the 12 account tools.

To update, `uvx` re-fetches the repo on each launch; pin a specific commit with `git+https://...@<sha>` if you need reproducibility.

## Add to your MCP client

All flows below assume you've installed `uv` (see Installation above) and have read access to the private repo — the client launches `uvx` as a subprocess on first run and re-fetches the repo.

### Cursor

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=delta-exchange-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2FudWotZGVsdGEvZGVsdGEtZXhjaGFuZ2UtbWNwLmdpdCIsImRlbHRhLWV4Y2hhbmdlLW1jcCJdLCJlbnYiOnsiREVMVEFfTUNQX0VOViI6ImluZGlhX3Byb2QifX0=)

Clicking the button opens Cursor with the server pre-filled. Add `DELTA_API_KEY` / `DELTA_API_SECRET` under `env` to enable the account tools.

### Claude Code

```bash
claude mcp add delta-exchange-mcp \
  --scope user \
  --env DELTA_MCP_ENV=india_prod \
  --env DELTA_API_KEY=your-api-key \
  --env DELTA_API_SECRET=your-api-secret \
  -- uvx --from git+https://github.com/anuj-delta/delta-exchange-mcp.git delta-exchange-mcp
```

`--scope user` makes the server available across all projects. Drop the API-key envs to use market-only mode. Verify with `claude mcp list`.

### Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.delta-exchange-mcp]
command = "uvx"
args = ["--from", "git+https://github.com/anuj-delta/delta-exchange-mcp.git", "delta-exchange-mcp"]
env = { DELTA_MCP_ENV = "india_prod", DELTA_API_KEY = "your-api-key", DELTA_API_SECRET = "your-api-secret" }
```

### Other clients (Claude Desktop, Zed, Windsurf, etc.)

Use the generic JSON config shown under [Installation](#installation).

## Authenticated tools (read-only)

To unlock the account tools, create an API key on Delta Exchange and pass it via env:

1. Go to [delta.exchange/app/account/manageapikeys](https://www.delta.exchange/app/account/manageapikeys) (testnet: [demo.delta.exchange](https://demo.delta.exchange/app/account/manageapikeys)).
2. Create a key. **Both `api_key` and `api_secret` are returned at creation** — the secret is shown once and must be saved by you. It can't be re-derived from the key.
3. Pick permissions — **Read Data** is sufficient for these tools; Trading is not required (and not exercised here).
4. Optional but recommended: whitelist your IP. Delta's API blocks requests from non-whitelisted IPs and returns the offending IP in the error context.
5. Use **prod keys with `DELTA_MCP_ENV=india_prod`** and **demo/testnet keys with `DELTA_MCP_ENV=india_testnet`**. Mixing them returns `InvalidApiKey`.

The server signs every authed request with HMAC-SHA256 over `method + timestamp + /v2{path} + query + body`, exactly per Delta's auth spec, and surfaces documented error codes (`SignatureExpired`, `InvalidApiKey`, `UnauthorizedApiAccess`, `ip_not_whitelisted_for_api_key`, `Signature Mismatch`) with actionable hints.

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `DELTA_MCP_ENV` | `india_prod` | `india_prod` or `india_testnet`. |
| `DELTA_API_KEY` | _(unset)_ | API key. Optional — when set with `DELTA_API_SECRET`, account tools register. |
| `DELTA_API_SECRET` | _(unset)_ | API secret matching `DELTA_API_KEY`. |

## Tools

### Public market data (always registered)

- `list_products` / `get_product`
- `get_ticker` / `list_tickers` / `get_options_chain`
- `get_orderbook`
- `get_recent_trades` / `get_candles`
- `get_reference_data` (assets + indices)

### Account read-only (registered when both `DELTA_API_KEY` and `DELTA_API_SECRET` are set)

- `get_positions` / `get_margined_positions`
- `get_wallet_balances` / `get_wallet_transactions`
- `get_open_orders` / `get_order_history` / `get_order_by_id`
- `get_fills`
- `get_product_leverage`
- `get_trading_stats` / `get_trading_preferences` / `get_profile`

## Development

```bash
uv sync
uv run pytest
uv run delta-exchange-mcp                          # stdio
```

### Testing with MCP Inspector

```bash
# stdio — spawns the server as a subprocess
bash scripts/inspect.sh --cli --method tools/list
bash scripts/inspect.sh --cli --method tools/call \
  --tool-name get_ticker --tool-arg symbol=BTCUSD

# with auth
DELTA_API_KEY=... DELTA_API_SECRET=... \
  bash scripts/inspect.sh --cli --method tools/call --tool-name get_wallet_balances
```

**Inspector web UI:**

```bash
bash scripts/inspect.sh
# → UI on http://localhost:6274, proxy on :6277
```

## Roadmap

- **Current**: 9 public market-data tools + 12 authenticated read-only account tools.
- **Next**: trading mutations (place/edit/cancel/close, leverage change) gated by an explicit `DELTA_MCP_MODE=trade` flag, plus an audit log and basic guardrails.

## Safety

- **No mutations.** Every tool is GET; the server cannot place, edit, or cancel orders. Account tools are pure read.
- Per-user keys never leave your machine — local stdio only, no shared hosted endpoint.
- Unofficial — not affiliated with Delta Exchange. Use at your own risk.
