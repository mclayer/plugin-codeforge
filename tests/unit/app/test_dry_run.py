"""Unit tests for mctrader.app.dry_run.run_dry_run."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mctrader.app.dry_run import (
    DRY_RUN_STAGE_CONFIG_VALIDATE,
    DRY_RUN_STAGE_SYMBOL_RESOLVE,
    DRY_RUN_STAGE_WEBSOCKET_HANDSHAKE,
    DryRunFailed,
    run_dry_run,
)
from mctrader.domain.symbol import Market, Symbol


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_config(ws_url: str = "wss://ws-api.bithumb.com/v1", symbols: list[str] | None = None) -> MagicMock:
    """Build a minimal CollectorConfig-shaped MagicMock."""
    cfg = MagicMock()
    cfg.bithumb.ws_url = ws_url
    cfg.collector.symbols = symbols if symbols is not None else ["BTC_KRW", "ETH_KRW"]
    return cfg


def _make_symbols(*names: str) -> list[Symbol]:
    return [Symbol(base=n.split("_")[0], quote=n.split("_")[1], market=Market.BITHUMB) for n in names]


# ---------------------------------------------------------------------------
# test_run_dry_run_success_happy_path
# ---------------------------------------------------------------------------

def test_run_dry_run_success_happy_path(capsys: pytest.CaptureFixture[str]) -> None:
    """Happy path: probe_handshake returns 123.4 ms, 2 symbols resolved.

    RED-observation substitute: the assertion for the third stdout line was
    temporarily inverted (asserting the wrong URL) to confirm the test fails
    before being restored.
    """
    config = _make_config(ws_url="wss://fake.bithumb.com", symbols=["BTC_KRW", "ETH_KRW"])
    gateway_symbols = _make_symbols("BTC_KRW", "ETH_KRW")

    with (
        patch("mctrader.app.dry_run.BithumbGateway") as MockGateway,
        patch("mctrader.app.dry_run.BithumbWsClient") as MockWsClient,
        patch("mctrader.app.dry_run.filter_symbols", return_value=gateway_symbols),
    ):
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.symbols.return_value = gateway_symbols

        mock_ws_instance = MockWsClient.return_value
        mock_ws_instance.probe_handshake = AsyncMock(return_value=123.4)

        asyncio.run(run_dry_run(config, "/etc/mctrader"))

    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    assert lines[0] == "[dry-run] config loaded: /etc/mctrader"
    assert lines[1] == "[dry-run] exchange=bithumb symbols=[BTC_KRW,ETH_KRW] (2 symbols)"
    assert lines[2] == "[dry-run] websocket handshake: OK (wss://fake.bithumb.com, 123ms)"
    assert lines[3] == "[dry-run] OK"


# ---------------------------------------------------------------------------
# test_run_dry_run_symbol_resolve_empty
# ---------------------------------------------------------------------------

def test_run_dry_run_symbol_resolve_empty() -> None:
    """When filter_symbols returns an empty list, DryRunFailed(stage=symbol_resolve) is raised.

    RED-observation substitute: assertion was temporarily changed to expect
    stage=config_validate to confirm test was detecting the correct stage.
    """
    config = _make_config(symbols=["XXX_YYY"])

    with (
        patch("mctrader.app.dry_run.BithumbGateway") as MockGateway,
        patch("mctrader.app.dry_run.BithumbWsClient"),
        patch("mctrader.app.dry_run.filter_symbols", return_value=[]),
    ):
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.symbols.return_value = []

        with pytest.raises(DryRunFailed) as exc_info:
            asyncio.run(run_dry_run(config, "/etc/mctrader"))

    assert exc_info.value.stage == DRY_RUN_STAGE_SYMBOL_RESOLVE


# ---------------------------------------------------------------------------
# test_run_dry_run_handshake_timeout
# ---------------------------------------------------------------------------

def test_run_dry_run_handshake_timeout() -> None:
    """probe_handshake raising TimeoutError is wrapped as DryRunFailed(websocket_handshake).

    RED-observation substitute: stage assertion was temporarily flipped to
    symbol_resolve to confirm the correct exception stage is caught.
    """
    config = _make_config()
    gateway_symbols = _make_symbols("BTC_KRW", "ETH_KRW")

    with (
        patch("mctrader.app.dry_run.BithumbGateway") as MockGateway,
        patch("mctrader.app.dry_run.BithumbWsClient") as MockWsClient,
        patch("mctrader.app.dry_run.filter_symbols", return_value=gateway_symbols),
    ):
        mock_gateway_instance = MockGateway.return_value
        mock_gateway_instance.symbols.return_value = gateway_symbols

        mock_ws_instance = MockWsClient.return_value
        mock_ws_instance.probe_handshake = AsyncMock(side_effect=TimeoutError("timed out"))

        with pytest.raises(DryRunFailed) as exc_info:
            asyncio.run(run_dry_run(config, "/etc/mctrader"))

    assert exc_info.value.stage == DRY_RUN_STAGE_WEBSOCKET_HANDSHAKE


# ---------------------------------------------------------------------------
# test_run_dry_run_invalid_exchange_filter
# ---------------------------------------------------------------------------

def test_run_dry_run_invalid_exchange_filter() -> None:
    """exchange_filter='binance' is not supported -> DryRunFailed(config_validate).

    RED-observation substitute: assertion was temporarily set to
    stage=symbol_resolve to confirm config_validate is raised before symbol
    resolution runs.
    """
    config = _make_config()

    with (
        patch("mctrader.app.dry_run.BithumbGateway"),
        patch("mctrader.app.dry_run.BithumbWsClient"),
        patch("mctrader.app.dry_run.filter_symbols"),
    ):
        with pytest.raises(DryRunFailed) as exc_info:
            asyncio.run(run_dry_run(config, "/etc/mctrader", exchange_filter="binance"))

    assert exc_info.value.stage == DRY_RUN_STAGE_CONFIG_VALIDATE
    assert "binance" in exc_info.value.reason
