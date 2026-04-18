import hashlib
import hmac

import httpx
import pytest
import respx

from delta_exchange_mcp.client import DeltaClient, sign
from delta_exchange_mcp.config import TESTNET_REST, Config


def _client_with_creds() -> DeltaClient:
    cfg = Config(
        env="testnet", mode="read", api_key="k1", api_secret="s1", base_url=TESTNET_REST
    )
    return DeltaClient(cfg)


def test_sign_matches_hmac_sha256_spec():
    expected = hmac.new(b"s1", b"GET1600000000/wallet/balances", hashlib.sha256).hexdigest()
    assert sign("s1", "GET", "1600000000", "/wallet/balances", "", "") == expected


@pytest.mark.asyncio
@respx.mock
async def test_authenticated_request_sends_signed_headers():
    route = respx.get(f"{TESTNET_REST}/wallet/balances").mock(
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

    cfg = Config(env="testnet", mode="read", api_key=None, api_secret=None, base_url=TESTNET_REST)
    client = DeltaClient(cfg)
    with pytest.raises(DeltaApiError, match="credentials_missing"):
        await client.get("/wallet/balances", auth=True)
