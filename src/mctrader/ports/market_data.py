from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator

from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Symbol


class MarketDataSource(ABC):
    """백테스트용 — 저장된 데이터를 시간순으로 방출"""

    @abstractmethod
    def stream(
        self,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
    ) -> Iterator[MarketEvent]: ...


class MarketDataSink(ABC):
    """수집기용 — 이벤트를 저장"""

    @abstractmethod
    def write_orderbook_diff(self, event: OrderBookDiffEvent) -> None: ...

    @abstractmethod
    def write_trade(self, event: TradeEvent) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...


class MarketDataFeed(ABC):
    """실시간용 (future) — 비동기 스트림"""

    @abstractmethod
    async def subscribe(self, symbols: list[Symbol]) -> AsyncIterator[MarketEvent]: ...
