from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Env = Literal["india_prod", "india_testnet"]
Transport = Literal["stdio", "http"]

INDIA_PROD_REST = "https://api.india.delta.exchange/v2"
INDIA_TESTNET_REST = "https://cdn-ind.testnet.deltaex.org/v2"

BASE_URLS: dict[str, str] = {
    "india_prod": INDIA_PROD_REST,
    "india_testnet": INDIA_TESTNET_REST,
}

DEFAULT_ENV = "india_prod"
DEFAULT_TRANSPORT = "stdio"
DEFAULT_HTTP_HOST = "0.0.0.0"
DEFAULT_HTTP_PORT = 8000


@dataclass(frozen=True)
class Config:
    env: Env
    base_url: str
    transport: Transport = DEFAULT_TRANSPORT
    http_host: str = DEFAULT_HTTP_HOST
    http_port: int = DEFAULT_HTTP_PORT
    # v2 (trading) — kept here so DeltaClient can grow auth without a refactor.
    api_key: str | None = None
    api_secret: str | None = None

    @property
    def has_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)


def load() -> Config:
    env = os.environ.get("DELTA_MCP_ENV", DEFAULT_ENV).lower()
    if env not in BASE_URLS:
        raise ValueError(
            f"DELTA_MCP_ENV must be one of {sorted(BASE_URLS)}, got {env!r}"
        )

    transport = os.environ.get("DELTA_MCP_TRANSPORT", DEFAULT_TRANSPORT).lower()
    if transport not in ("stdio", "http"):
        raise ValueError(
            f"DELTA_MCP_TRANSPORT must be 'stdio' or 'http', got {transport!r}"
        )

    return Config(
        env=env,  # type: ignore[arg-type]
        base_url=BASE_URLS[env],
        transport=transport,  # type: ignore[arg-type]
        http_host=os.environ.get("DELTA_MCP_HTTP_HOST", DEFAULT_HTTP_HOST),
        http_port=int(os.environ.get("DELTA_MCP_HTTP_PORT", DEFAULT_HTTP_PORT)),
        api_key=os.environ.get("DELTA_API_KEY") or None,
        api_secret=os.environ.get("DELTA_API_SECRET") or None,
    )
