# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project in one line

FastMCP server that wraps Delta Exchange India's public REST endpoints as MCP tools, deployable as a stdio subprocess, a local Docker container, or a hosted HTTP endpoint.

## Commands

```bash
uv sync                                        # install deps (runtime + dev)
uv run pytest                                  # run full suite (asyncio_mode=auto)
uv run pytest tests/test_market_tools.py::test_429_retries_then_succeeds  # single test
uv run ruff check src tests scripts            # lint
uv run ruff check --fix src tests scripts      # lint + autofix

uv run delta-exchange-mcp                      # stdio transport (default)
DELTA_MCP_TRANSPORT=http uv run delta-exchange-mcp   # http on :8000

uv run python scripts/smoke.py                 # live smoke against DELTA_MCP_ENV

bash scripts/inspect.sh --cli --method tools/list                                # Inspector CLI — list tools
bash scripts/inspect.sh --cli --method tools/call --tool-name get_ticker --tool-arg symbol=BTCUSD
bash scripts/inspect.sh                                                          # Inspector web UI on :6274

docker build -t delta-exchange-mcp . && docker run -p 8000:8000 delta-exchange-mcp
```

**Rebuilding the editable install after changing `pyproject.toml` or entry points**: `uv sync` again — `uv run` caches the build.

## Architecture

### Tool registration pattern

Each tool module exposes `register(mcp: FastMCP, client: DeltaClient) -> None` that attaches `@mcp.tool()`-decorated closures. `server.py::build_server()` instantiates `DeltaClient` once and passes it into every `register` call. **To add a tool group**: create `src/delta_exchange_mcp/tools/<group>.py` with a `register(mcp, client)`, then call it from `build_server`.

### DeltaClient — single point for HTTP concerns

`src/delta_exchange_mcp/client.py` centralizes five cross-cutting behaviors that every tool depends on. Read this file before touching any tool logic:

1. **None-param stripping** — `filtered_params` is computed once and fed to **both** the signing payload (`query_str`) and `httpx.request(params=...)`. Delta's API rejects `?expiry=` as "invalid date"; this is why the same filter applies in two places. Regression test: `test_none_params_are_stripped_before_send`.
2. **Retry policy** — 429 backs off using the `X-RATE-LIMIT-RESET` header (ms); 5xx uses exponential backoff. Only retries GET; POST/PUT/DELETE never auto-retry.
3. **Error-envelope unwrapping** — `{success: false, error: {code, context}}` is raised as `DeltaApiError` (see `errors.py`); success responses with a `result` key return `{"result": ..., "meta": ...}`, otherwise raw JSON.
4. **HMAC-SHA256 signing** — `sign()` concatenates `method + timestamp + path + query + body`. Enabled per-call via `client.get(..., auth=True)`. **Dormant in v1** because no registered tool sets `auth=True`.
5. **User-Agent header is required by Delta** — a missing one returns 403. Do not remove it.

### Transport branching

`server.main()` reads `cfg.transport`:
- `stdio` → `mcp.run()` — default, used by Claude Desktop/Code/Cursor/Zed.
- `http` → `mcp.run(transport="streamable-http")` — FastMCP is constructed with `stateless_http=True, json_response=True` for this mode (production-recommended per MCP SDK docs).

Docker image defaults to `http` (see `Dockerfile` ENV block).

### v1 scope lives in `server.py`, not in config

`tools/account.py` has 7 fully-implemented private-endpoint tools, and `client.py` has working HMAC auth. **Neither is registered in v1.** `server.py::build_server()` deliberately only calls `market.register(...)`. The `api_key`/`api_secret` fields on `Config` are loaded from env but unused. When v2 trading lands, re-enable registration and wire a `DELTA_MCP_MODE=trade` gate — the code is ready for it.

Do **not** delete `account.py` or the signer as "dead code" — they're preserved infrastructure for v2.

### Environment naming

`DELTA_MCP_ENV` values are `india_prod` / `india_testnet` (not `mainnet`/`testnet`) to match Delta's own URL naming (`api.india.delta.exchange`, `cdn-ind.testnet.deltaex.org`). `india_prod` is the default — users ask "what's BTCUSD mid", they mean prod, not testnet.

## Reference — Delta Exchange API

The upstream source of truth for endpoint shapes is the **Slate docs repo at `/home/delta/work/slate`**, specifically `swagger_v2.json` and `source/includes/_*.md`. When adding or fixing a tool:

```bash
jq '.paths["/products"].get.parameters' /home/delta/work/slate/swagger_v2.json
```

Auth spec lives at `/home/delta/work/slate/source/includes/_authentication.md` (signing payload format, ±5 sec timestamp window).

## Distribution modes

Three, all from the same image/package (see README for the user-facing config snippets):

| Mode | Transport | Who runs it |
|---|---|---|
| stdio (via `uvx`) | stdio | each user locally |
| Docker local | http | each user locally in a container |
| Hosted URL | http | one shared deployment |

**The hosted-URL mode only works for v1's public-data surface.** v2 (trading) requires per-user API keys, which a shared HTTP server cannot route safely — v2 users will need stdio or Docker-per-user. Any architectural decision that assumes a persistent hosted URL should be revisited before v2 ships.

## Tests

`respx` mocks httpx for unit tests (no live network). Live verification happens through `scripts/smoke.py` (Python-level) and `scripts/inspect.sh --cli` (MCP-protocol-level) — both hit real testnet/prod and are run manually, not in CI. When fixing a bug surfaced by live use, add a `respx` regression test (see `test_none_params_are_stripped_before_send` for the pattern).

## Distribution repo

Private: `github.com/anuj-delta/delta-exchange-mcp`. Teammate install path is `uvx --from git+https://github.com/anuj-delta/delta-exchange-mcp.git delta-exchange-mcp` — they need repo read access.
