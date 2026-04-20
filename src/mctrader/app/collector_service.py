from __future__ import annotations

import asyncio
import logging
import signal
from typing import TYPE_CHECKING

from mctrader.adapters.exchanges.bithumb.gateway import BithumbGateway
from mctrader.adapters.exchanges.bithumb.ws_client import BithumbWsClient
from mctrader.adapters.storage.parquet_sink import ParquetSink
from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Symbol
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
        """Main collection loop: connect, stream, store, and shutdown."""
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
                stored += await self._handle_event(event)

                if received % _LOG_INTERVAL == 0:
                    logger.info(
                        "CollectorService stats: received=%d stored=%d",
                        received,
                        stored,
                    )
        finally:
            await self._shutdown()

    async def _handle_event(self, event: MarketEvent) -> int:
        """Store event if applicable. Return 1 if stored, 0 otherwise."""
        if isinstance(event, OrderBookDiffEvent):
            self._sink.write_orderbook_diff(event)
            return 1
        if isinstance(event, TradeEvent):
            self._sink.write_trade(event)
            return 1
        return 0

    async def stop(self) -> None:
        """Signal service to stop gracefully."""
        logger.info("CollectorService stop requested")
        self._running = False
        await self._ws_client.close()

    async def _periodic_flush(self) -> None:
        """Run sink flush on interval in background."""
        while self._running:
            await asyncio.sleep(self._flush_interval_sec)
            if not self._running:
                break
            asyncio.create_task(asyncio.to_thread(self._sink.flush))

    async def _shutdown(self) -> None:
        """Cancel periodic flush task and close sink."""
        await self._cancel_flush_task()
        await asyncio.to_thread(self._sink.close)
        logger.info("CollectorService shutdown complete")

    async def _cancel_flush_task(self) -> None:
        """Cancel periodic flush task if present."""
        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

    @classmethod
    def from_config(cls, config: CollectorConfig) -> CollectorService:
        """Create service from configuration."""
        gateway = BithumbGateway()
        symbol_objs = _filter_symbols(gateway.symbols(), config.collector.symbols)
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


def _filter_symbols(all_symbols: list[Symbol], selector: str | list[str]) -> list[Symbol]:
    """Filter symbols by selector: 'all', list of names, or single name."""
    if selector == "all":
        return all_symbols

    selected_names: list[str] = selector if isinstance(selector, list) else [selector]
    return [s for s in all_symbols if s.name in selected_names]


async def run_collector(config: CollectorConfig) -> None:
    """Run collector service with signal handlers for graceful shutdown."""
    service = CollectorService.from_config(config)
    loop = asyncio.get_running_loop()

    def _stop_service() -> None:
        asyncio.create_task(service.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _stop_service)

    await service.run()
