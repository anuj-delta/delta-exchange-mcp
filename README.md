# delta-exchange-mcp

Unofficial MCP (Model Context Protocol) server for **Delta Exchange India** — lets AI assistants (Claude Desktop, Cursor, Zed, Claude Code) query Delta Exchange public market data through standardized tools.

> **v1 scope**: 9 public market-data tools. No credentials required, no mutating actions. Account-read + trading arrive together in v2.

## Installation

This server is distributed **local-only**. Because it's a financial-tool MCP, users should be able to read the code running against their account — no shared hosted endpoint is provided. Pick one of the two modes below.

Repo access: the distribution repo is private at `github.com/anuj-delta/delta-exchange-mcp`. Ensure your GitHub account has read access and an SSH key or `gh auth login` set up.

### 1. uvx (stdio) — recommended

Each user runs the server as a subprocess of their MCP client. No network, no container.

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
      "env": { "DELTA_MCP_ENV": "india_prod" }
    }
  }
}
```

To update, `uvx` re-fetches the repo on each launch; pin a specific commit with `git+https://...@<sha>` if you need reproducibility.

### 2. Docker (local)

**Prerequisite:** Docker, plus a local clone of the repo.

```bash
git clone https://github.com/anuj-delta/delta-exchange-mcp.git
cd delta-exchange-mcp
docker build -t delta-exchange-mcp .
docker run --rm -p 8000:8000 -e DELTA_MCP_ENV=india_prod delta-exchange-mcp
```

The container runs HTTP transport on `:8000`. Point your MCP client at the local URL:

```json
{
  "mcpServers": {
    "delta-exchange": { "type": "http", "url": "http://localhost:8000/mcp" }
  }
}
```

## Add to your MCP client

All three flows below assume you've installed `uv` (see Installation above) and have read access to the private repo — the client launches `uvx` as a subprocess on first run and re-fetches the repo.

### Cursor

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=delta-exchange-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2FudWotZGVsdGEvZGVsdGEtZXhjaGFuZ2UtbWNwLmdpdCIsImRlbHRhLWV4Y2hhbmdlLW1jcCJdLCJlbnYiOnsiREVMVEFfTUNQX0VOViI6ImluZGlhX3Byb2QifX0=)

Clicking the button opens Cursor with the server pre-filled — review and accept the install prompt.

### Claude Code

```bash
claude mcp add delta-exchange-mcp \
  --scope user \
  --env DELTA_MCP_ENV=india_prod \
  -- uvx --from git+https://github.com/anuj-delta/delta-exchange-mcp.git delta-exchange-mcp
```

`--scope user` makes the server available across all projects. Drop it for project-local scope. Verify with `claude mcp list`.

### Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.delta-exchange-mcp]
command = "uvx"
args = ["--from", "git+https://github.com/anuj-delta/delta-exchange-mcp.git", "delta-exchange-mcp"]
env = { DELTA_MCP_ENV = "india_prod" }
```

### Other clients (Claude Desktop, Zed, Windsurf, etc.)

Use the generic JSON config shown under [Installation → uvx](#1-uvx-stdio--recommended).

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

- **v1** (current): 9 public market-data tools. Distributed locally via `uvx` or Docker.
- **v2**: HMAC auth, account-read (balances/positions/orders/fills), trading (place/edit/cancel/close/leverage) gated by `DELTA_MCP_MODE=trade`, audit log, guardrails. Per-user API keys — the local-only distribution model carries over.

## Safety

- **No trading in v1.** No mutating tools exist — the server is a pure read-only wrapper over public endpoints.
- Unofficial — not affiliated with Delta Exchange. Use at your own risk.
