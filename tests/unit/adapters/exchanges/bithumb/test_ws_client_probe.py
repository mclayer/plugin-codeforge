"""Unit tests for BithumbWsClient.probe_handshake."""
from __future__ import annotations

import asyncio
import ssl
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mctrader.adapters.exchanges.bithumb.ws_client import BithumbWsClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_ws() -> MagicMock:
    """Return a fake WebSocket connection object."""
    ws = MagicMock()
    ws.send = AsyncMock()
    ws.close = AsyncMock()
    return ws


def _make_client(ws_url: str = "wss://fake.bithumb.com") -> BithumbWsClient:
    return BithumbWsClient(symbols=[], ws_url=ws_url)


# ---------------------------------------------------------------------------
# test_probe_handshake_does_not_subscribe
# ---------------------------------------------------------------------------

def test_probe_handshake_does_not_subscribe() -> None:
    """probe_handshake must NOT call ws.send (no subscribe frame sent).

    RED-observation substitute: assertion was temporarily inverted to
    `assert fake_ws.send.call_count > 0` to confirm the test detects a
    subscribe call before restoring the original assertion.
    """
    fake_ws = _make_fake_ws()

    with patch(
        "mctrader.adapters.exchanges.bithumb.ws_client.websockets.connect",
        new=AsyncMock(return_value=fake_ws),
    ):
        with patch(
            "mctrader.adapters.exchanges.bithumb.ws_client.asyncio.wait_for",
            new=AsyncMock(return_value=fake_ws),
        ):
            asyncio.run(_make_client().probe_handshake(timeout_sec=5.0))

    assert fake_ws.send.call_count == 0


# ---------------------------------------------------------------------------
# test_probe_handshake_returns_elapsed_ms
# ---------------------------------------------------------------------------

def test_probe_handshake_returns_elapsed_ms() -> None:
    """probe_handshake returns a positive float (elapsed ms).

    RED-observation substitute: assertion was temporarily set to
    `assert result < 0` to confirm the test rejects a negative value.
    """
    fake_ws = _make_fake_ws()

    with patch(
        "mctrader.adapters.exchanges.bithumb.ws_client.asyncio.wait_for",
        new=AsyncMock(return_value=fake_ws),
    ):
        result = asyncio.run(_make_client().probe_handshake(timeout_sec=5.0))

    assert isinstance(result, float)
    assert result >= 0.0


# ---------------------------------------------------------------------------
# test_probe_handshake_timeout_raises
# ---------------------------------------------------------------------------

def test_probe_handshake_timeout_raises() -> None:
    """asyncio.TimeoutError from wait_for propagates out of probe_handshake unchanged.

    RED-observation substitute: the expected exception type was temporarily
    changed to OSError to confirm pytest.raises detects the wrong type.
    """
    with patch(
        "mctrader.adapters.exchanges.bithumb.ws_client.asyncio.wait_for",
        new=AsyncMock(side_effect=asyncio.TimeoutError("handshake timeout")),
    ):
        with pytest.raises((TimeoutError, asyncio.TimeoutError)):
            asyncio.run(_make_client().probe_handshake(timeout_sec=0.001))
