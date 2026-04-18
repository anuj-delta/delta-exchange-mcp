# delta-exchange-mcp

Unofficial MCP (Model Context Protocol) server for **Delta Exchange India** — lets AI assistants (Claude Desktop, Cursor, Zed, Claude Code) query Delta Exchange public market data through standardized tools.

> **v1 scope**: 9 public market-data tools. No credentials required, no mutating actions. Account-read + trading arrive together in v2.

## Usage modes

The same codebase supports three deployment patterns. Pick whichever matches how your users connect.

### 1. Stdio (local) — simplest for individual use

Each user runs the server as a subprocess of their MCP client. No network, no hosting.

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

Requires `uv` on the user's machine.

### 2. Docker (local or shared host)

```bash
docker build -t delta-exchange-mcp .
docker run -p 8000:8000 -e DELTA_MCP_ENV=india_prod delta-exchange-mcp
```

The container runs HTTP transport on `:8000` by default. Point your MCP client at it:

```json
{
  "mcpServers": {
    "delta-exchange": { "type": "http", "url": "http://localhost:8000/mcp" }
  }
}
```

### 3. Hosted URL — one shared instance for a team

Deploy the Docker image to any host (ECS, Cloud Run, k8s, Fly, fly-VPS). Teammates connect with zero setup:

```json
{
  "mcpServers": {
    "delta-exchange": { "type": "http", "url": "https://mcp.yourdomain.com/mcp" }
  }
}
```

**Caveats for a public/hosted deployment:**
- Delta's rate limit (10k units / 5 min) is **per source IP** — one shared server → one shared bucket. Watch for 429s.
- The server has no auth of its own; anyone reaching the URL can call tools. Use your ingress (Cloudflare Access, VPN, API gateway, Tailscale ACL) to gate it.
- Only public market data is exposed in v1, so a leaked URL is low-severity. That changes in v2 when account + trading land.

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `DELTA_MCP_ENV` | `india_prod` | `india_prod` or `india_testnet`. |
| `DELTA_MCP_TRANSPORT` | `stdio` | `stdio` or `http`. Docker image flips this to `http`. |
| `DELTA_MCP_HTTP_HOST` | `0.0.0.0` | Bind address when `TRANSPORT=http`. |
| `DELTA_MCP_HTTP_PORT` | `8000` | Listen port when `TRANSPORT=http`. |

`DELTA_API_KEY` / `DELTA_API_SECRET` are **not** used by v1. They're wired in v2 alongside trading tools.

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
uv run delta-exchange-mcp                          # stdio (default)
DELTA_MCP_TRANSPORT=http uv run delta-exchange-mcp # http on :8000
```

### Testing with MCP Inspector

Run the official [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
# stdio — spawns the server as a subprocess
bash scripts/inspect.sh --cli --method tools/list
bash scripts/inspect.sh --cli --method tools/call \
  --tool-name get_ticker --tool-arg symbol=BTCUSD

# against a running HTTP server
npx @modelcontextprotocol/inspector --cli \
  http://127.0.0.1:8000/mcp --transport http \
  --method tools/call --tool-name get_ticker --tool-arg symbol=BTCUSD
```

**Inspector web UI:**

```bash
bash scripts/inspect.sh
# → UI on http://localhost:6274, proxy on :6277
```

## Roadmap

- **v1** (current): 9 public market-data tools. stdio + http transports. Docker image.
- **v2**: HMAC auth, account-read (balances/positions/orders/fills), trading (place/edit/cancel/close/leverage) gated by `DELTA_MCP_MODE=trade`, audit log, guardrails. Per-user keys → the hosted-URL pattern stops working for trading; use stdio or Docker-per-user.

## Safety

- **No trading in v1.** No mutating tools exist — the server is a pure read-only wrapper over public endpoints.
- Unofficial — not affiliated with Delta Exchange. Use at your own risk.
