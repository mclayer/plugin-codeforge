from __future__ import annotations

import asyncio
import logging
import signal
from typing import TYPE_CHECKING

from mctrader.adapters.exchanges.bithumb.gateway import BithumbGateway
from mctrader.adapters.exchanges.bithumb.ws_client import BithumbWsClient
from mctrader.adapters.storage.parquet_sink import ParquetSink
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.ports.market_data import MarketDataSink

if TYPE_CHECKING:
    from mctrader.infra.config import CollectorConfig

logger = logging.getLogger(__name__)

_LOG_INTERVAL = 10_000


class CollectorService:
    """
    Bithumb WebSocket에서 시장 데이터를 수집해 Parquet에 저장.
    asyncio 기반.

    실행 흐름:
    1. BithumbWsClient 연결
    2. messages() 루프에서 raw msg 수신
    3. gateway.normalize_event(raw) -> MarketEvent
    4. sink.write_*(event) 저장
    5. flush_interval_sec 마다 sink.flush()
    6. SIGINT/SIGTERM 시 graceful shutdown (sink.close())
    """

    def __init__(
        self,
        ws_client: BithumbWsClient,
        gateway: BithumbGateway,
        sink: MarketDataSink,
        flush_interval_sec: int = 60,
    ) -> None:
        self._ws_client = ws_client
        self._gateway = gateway
        self._sink = sink
        self._flush_interval_sec = flush_interval_sec
        self._running = False
        self._flush_task: asyncio.Task | None = None

    async def run(self) -> None:
        self._running = True
        await self._ws_client.connect()
        logger.info("CollectorService started")

        self._flush_task = asyncio.create_task(self._periodic_flush())

        received = 0
        stored = 0

        try:
            async for raw in self._ws_client.messages():
                if not self._running:
                    break

                event = self._gateway.normalize_event(raw)
                if event is None:
                    continue

                received += 1

                if isinstance(event, OrderBookDiffEvent):
                    self._sink.write_orderbook_diff(event)
                    stored += 1
                elif isinstance(event, TradeEvent):
                    self._sink.write_trade(event)
                    stored += 1

                if received % _LOG_INTERVAL == 0:
                    logger.info(
                        "CollectorService stats: received=%d stored=%d",
                        received,
                        stored,
                    )
        finally:
            await self._shutdown()

    async def stop(self) -> None:
        logger.info("CollectorService stop requested")
        self._running = False
        await self._ws_client.close()

    async def _periodic_flush(self) -> None:
        while self._running:
            await asyncio.sleep(self._flush_interval_sec)
            if not self._running:
                break
            # run flush in background so it doesn't block the message loop
            asyncio.create_task(asyncio.to_thread(self._sink.flush))

    async def _shutdown(self) -> None:
        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        await asyncio.to_thread(self._sink.close)
        logger.info("CollectorService shutdown complete")

    @classmethod
    def from_config(cls, config: CollectorConfig) -> CollectorService:
        gateway = BithumbGateway()

        if config.collector.symbols == "all":
            symbol_objs = gateway.symbols()
        elif isinstance(config.collector.symbols, list):
            symbol_objs = [s for s in gateway.symbols() if s.name in config.collector.symbols]
        else:
            # single string that is not "all" — treat as one symbol name
            symbol_objs = [s for s in gateway.symbols() if s.name == config.collector.symbols]

        ws_symbols = [s.name for s in symbol_objs]
        ws_client = BithumbWsClient(
            symbols=ws_symbols,
            ws_url=config.bithumb.ws_url or None,
            reconnect_interval_sec=config.collector.reconnect_interval_sec,
        )

        sink = ParquetSink(
            root_path=config.data.root_path,
            flush_interval_sec=config.collector.flush_interval_sec,
            flush_max_mb=config.collector.flush_max_mb,
        )

        return cls(
            ws_client=ws_client,
            gateway=gateway,
            sink=sink,
            flush_interval_sec=config.collector.flush_interval_sec,
        )


async def run_collector(config: CollectorConfig) -> None:
    service = CollectorService.from_config(config)
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(service.stop()))

    await service.run()
