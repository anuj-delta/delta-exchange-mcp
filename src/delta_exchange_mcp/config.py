from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Mode = Literal["read", "trade"]
Env = Literal["testnet", "mainnet"]

MAINNET_REST = "https://api.india.delta.exchange/v2"
TESTNET_REST = "https://cdn-ind.testnet.deltaex.org/v2"


@dataclass(frozen=True)
class Config:
    env: Env
    mode: Mode
    api_key: str | None
    api_secret: str | None
    base_url: str

    @property
    def has_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)


def load() -> Config:
    env = os.environ.get("DELTA_MCP_ENV", "testnet").lower()
    if env not in ("testnet", "mainnet"):
        raise ValueError(f"DELTA_MCP_ENV must be 'testnet' or 'mainnet', got {env!r}")

    mode = os.environ.get("DELTA_MCP_MODE", "read").lower()
    if mode not in ("read", "trade"):
        raise ValueError(f"DELTA_MCP_MODE must be 'read' or 'trade', got {mode!r}")
    if mode == "trade":
        raise ValueError(
            "DELTA_MCP_MODE=trade is not supported in v1. Trading tools ship in v2."
        )

    api_key = os.environ.get("DELTA_API_KEY") or None
    api_secret = os.environ.get("DELTA_API_SECRET") or None

    base_url = MAINNET_REST if env == "mainnet" else TESTNET_REST

    return Config(
        env=env,  # type: ignore[arg-type]
        mode=mode,  # type: ignore[arg-type]
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
    )
