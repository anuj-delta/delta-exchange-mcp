import pytest

from delta_exchange_mcp import config as config_mod


def test_defaults_to_india_prod(monkeypatch):
    monkeypatch.delenv("DELTA_MCP_ENV", raising=False)
    monkeypatch.delenv("DELTA_API_KEY", raising=False)
    monkeypatch.delenv("DELTA_API_SECRET", raising=False)
    cfg = config_mod.load()
    assert cfg.env == "india_prod"
    assert cfg.base_url == config_mod.INDIA_PROD_REST
    assert cfg.has_credentials is False


def test_testnet_override(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_ENV", "india_testnet")
    cfg = config_mod.load()
    assert cfg.env == "india_testnet"
    assert cfg.base_url == config_mod.INDIA_TESTNET_REST


def test_invalid_env_rejected(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_ENV", "mainnet")  # old alias no longer accepted
    with pytest.raises(ValueError, match="DELTA_MCP_ENV"):
        config_mod.load()


def test_transport_defaults_stdio(monkeypatch):
    monkeypatch.delenv("DELTA_MCP_TRANSPORT", raising=False)
    cfg = config_mod.load()
    assert cfg.transport == "stdio"


def test_transport_http_with_port_override(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_TRANSPORT", "http")
    monkeypatch.setenv("DELTA_MCP_HTTP_PORT", "9090")
    monkeypatch.setenv("DELTA_MCP_HTTP_HOST", "127.0.0.1")
    cfg = config_mod.load()
    assert cfg.transport == "http"
    assert cfg.http_port == 9090
    assert cfg.http_host == "127.0.0.1"


def test_invalid_transport_rejected(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_TRANSPORT", "grpc")
    with pytest.raises(ValueError, match="DELTA_MCP_TRANSPORT"):
        config_mod.load()
