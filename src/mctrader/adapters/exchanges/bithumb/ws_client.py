from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
import uuid
from collections.abc import AsyncGenerator

import certifi
import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

logger = logging.getLogger(__name__)

_DEFAULT_RECONNECT_INTERVAL_SEC = 5


class BithumbWsClient:
    """
    Bithumb WebSocket client with automatic reconnection.
    Handles subscription to orderbook and trade streams.
    """

    WS_URL = "wss://ws-api.bithumb.com/websocket/v1"

    def __init__(
        self,
        symbols: list[str],
        ws_url: str | None = None,
        reconnect_interval_sec: int = _DEFAULT_RECONNECT_INTERVAL_SEC,
    ) -> None:
        self._symbols = symbols
        self._url = ws_url or self.WS_URL
        self._reconnect_interval_sec = reconnect_interval_sec
        self._ws: ClientConnection | None = None
        self._closed = False

    async def connect(self) -> None:
        self._ws = await websockets.connect(self._url, ssl=_SSL_CTX)
        await self._subscribe()

    async def messages(self) -> AsyncGenerator[dict[str, object], None]:
        while not self._closed:
            if self._ws is None:
                await self._reconnect()

            try:
                async for raw in self._ws:  # type: ignore[union-attr]
                    msg = json.loads(raw)
                    yield msg
            except ConnectionClosed as exc:
                if self._closed:
                    return
                logger.warning(
                    "WebSocket closed (%s), reconnecting in %ds",
                    exc,
                    self._reconnect_interval_sec,
                )
                await self._handle_disconnection()
            except Exception as exc:
                if self._closed:
                    return
                logger.error(
                    "WebSocket error: %s, reconnecting in %ds",
                    exc,
                    self._reconnect_interval_sec,
                )
                await self._handle_disconnection()

    async def _handle_disconnection(self) -> None:
        self._ws = None
        await asyncio.sleep(self._reconnect_interval_sec)

    async def close(self) -> None:
        self._closed = True
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def _subscribe(self) -> None:
        codes = [f"{s.split('_')[1]}-{s.split('_')[0]}" for s in self._symbols]
        payload = json.dumps([
            {"ticket": str(uuid.uuid4())},
            {"type": "orderbook", "codes": codes},
            {"type": "trade", "codes": codes},
        ])
        await self._ws.send(payload)  # type: ignore[union-attr]

    async def probe_handshake(self, timeout_sec: float = 5.0) -> float:
        """Perform TLS handshake only — no subscription, immediate close.

        Returns elapsed time in milliseconds.
        Raises asyncio.TimeoutError, OSError, ssl.SSLError on failure.
        """
        start = time.monotonic()
        ws = await asyncio.wait_for(
            websockets.connect(self._url, ssl=_SSL_CTX),
            timeout=timeout_sec,
        )
        elapsed = (time.monotonic() - start) * 1000.0
        await ws.close()
        return elapsed

    async def _reconnect(self) -> None:
        logger.info("Reconnecting to %s", self._url)
        try:
            self._ws = await websockets.connect(self._url, ssl=_SSL_CTX)
            await self._subscribe()
        except Exception as exc:
            logger.error("Reconnect failed: %s, retrying in %ds", exc, self._reconnect_interval_sec)
            self._ws = None
            await asyncio.sleep(self._reconnect_interval_sec)
