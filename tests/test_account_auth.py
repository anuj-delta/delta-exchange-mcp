"""Signer + auth plumbing tests. Kept for v2 when trading + account tools ship."""

import hashlib
import hmac

import httpx
import pytest
import respx

from delta_exchange_mcp.client import DeltaClient, sign
from delta_exchange_mcp.config import INDIA_TESTNET_REST, Config


def _client_with_creds() -> DeltaClient:
    cfg = Config(
        env="india_testnet", base_url=INDIA_TESTNET_REST, api_key="k1", api_secret="s1"
    )
    return DeltaClient(cfg)


def test_sign_matches_hmac_sha256_spec():
    expected = hmac.new(b"s1", b"GET1600000000/wallet/balances", hashlib.sha256).hexdigest()
    assert sign("s1", "GET", "1600000000", "/wallet/balances", "", "") == expected


@pytest.mark.asyncio
@respx.mock
async def test_authenticated_request_sends_signed_headers():
    route = respx.get(f"{INDIA_TESTNET_REST}/wallet/balances").mock(
        return_value=httpx.Response(200, json={"success": True, "result": []})
    )
    client = _client_with_creds()
    await client.get("/wallet/balances", auth=True)

    assert route.called
    req = route.calls[0].request
    assert req.headers.get("api-key") == "k1"
    assert req.headers.get("timestamp") is not None
    sig = req.headers.get("signature")
    assert sig and len(sig) == 64


@pytest.mark.asyncio
@respx.mock
async def test_auth_required_without_creds_raises():
    from delta_exchange_mcp.errors import DeltaApiError

    cfg = Config(env="india_testnet", base_url=INDIA_TESTNET_REST)
    client = DeltaClient(cfg)
    with pytest.raises(DeltaApiError, match="credentials_missing"):
        await client.get("/wallet/balances", auth=True)
