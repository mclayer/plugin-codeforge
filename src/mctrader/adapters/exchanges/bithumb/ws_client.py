from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

_DEFAULT_RECONNECT_INTERVAL_SEC = 5


class BithumbWsClient:
    """
    Bithumb WebSocket client with automatic reconnection.
    Handles subscription to orderbook and trade streams.
    """

    WS_URL = "wss://global-api.bithumb.pro/message/realtime"

    def __init__(
        self,
        symbols: list[str],
        ws_url: str | None = None,
        reconnect_interval_sec: int = _DEFAULT_RECONNECT_INTERVAL_SEC,
    ) -> None:
        self._symbols = symbols
        self._url = ws_url or self.WS_URL
        self._reconnect_interval_sec = reconnect_interval_sec
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._closed = False

    async def connect(self) -> None:
        self._ws = await websockets.connect(self._url)
        await self._subscribe()

    async def messages(self) -> AsyncGenerator[dict, None]:
        while not self._closed:
            if self._ws is None:
                await self._reconnect()

            try:
                async for raw in self._ws:  # type: ignore[union-attr]
                    msg = json.loads(raw)
                    if msg.get("type") == "ping" or "ping" in msg:
                        continue
                    yield msg
            except ConnectionClosed as exc:
                if self._closed:
                    return
                logger.warning("WebSocket closed (%s), reconnecting in %ds", exc, self._reconnect_interval_sec)
                await self._handle_disconnection()
            except Exception as exc:
                if self._closed:
                    return
                logger.error("WebSocket error: %s, reconnecting in %ds", exc, self._reconnect_interval_sec)
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
        args: list[str] = []
        for sym in self._symbols:
            args.append(f"ORDERBOOK:{sym}")
            args.append(f"TRADE:{sym}")
        payload = json.dumps({"cmd": "subscribe", "args": args})
        await self._ws.send(payload)  # type: ignore[union-attr]

    async def _reconnect(self) -> None:
        logger.info("Reconnecting to %s", self._url)
        try:
            self._ws = await websockets.connect(self._url)
            await self._subscribe()
        except Exception as exc:
            logger.error("Reconnect failed: %s, retrying in %ds", exc, self._reconnect_interval_sec)
            self._ws = None
            await asyncio.sleep(self._reconnect_interval_sec)
