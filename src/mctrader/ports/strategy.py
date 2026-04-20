from __future__ import annotations

from abc import ABC, abstractmethod

from mctrader.domain.events import MarketEvent
from mctrader.domain.order import Fill, OrderIntent
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.signal import Signal
from mctrader.domain.symbol import Symbol


class SignalGenerator(ABC):
    @abstractmethod
    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
    ) -> list[Signal]: ...


class TradingStrategy(ABC):
    @abstractmethod
    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
        portfolio: Portfolio,
    ) -> list[OrderIntent]: ...

    @abstractmethod
    def on_execution(
        self,
        fill: Fill,
        portfolio: Portfolio,
    ) -> list[OrderIntent]: ...


class CoinSelector(ABC):
    """TO-DO: 코인 필터링 전략"""

    @abstractmethod
    def select(self, universe: list[Symbol], ts: int) -> list[Symbol]: ...


class RiskManager(ABC):
    """TO-DO: 리스크 관리"""

    @abstractmethod
    def check(self, intent: OrderIntent, portfolio: Portfolio) -> bool: ...
