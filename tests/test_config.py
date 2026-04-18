import pytest

from delta_exchange_mcp import config as config_mod


def test_defaults_to_testnet_read(monkeypatch):
    monkeypatch.delenv("DELTA_MCP_ENV", raising=False)
    monkeypatch.delenv("DELTA_MCP_MODE", raising=False)
    monkeypatch.delenv("DELTA_API_KEY", raising=False)
    monkeypatch.delenv("DELTA_API_SECRET", raising=False)
    cfg = config_mod.load()
    assert cfg.env == "testnet"
    assert cfg.mode == "read"
    assert cfg.base_url == config_mod.TESTNET_REST
    assert cfg.has_credentials is False


def test_mainnet_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_ENV", "mainnet")
    cfg = config_mod.load()
    assert cfg.base_url == config_mod.MAINNET_REST


def test_trade_mode_rejected_in_v1(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_MODE", "trade")
    with pytest.raises(ValueError, match="v1"):
        config_mod.load()


def test_invalid_env_rejected(monkeypatch):
    monkeypatch.setenv("DELTA_MCP_ENV", "prod")
    with pytest.raises(ValueError):
        config_mod.load()
