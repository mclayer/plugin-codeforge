from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from mctrader.domain.events import TradeEvent
from mctrader.domain.order import Order
from mctrader.domain.orderbook import OrderBookSnapshot


@dataclass
class QueueState:
    qty_ahead: Decimal
    estimated_fill_ts: int | None  # None if not estimable


class QueuePositionModel(ABC):
    @abstractmethod
    def estimate(
        self,
        order: Order,
        snapshot: OrderBookSnapshot,
        recent_trades: list[TradeEvent],
    ) -> QueueState: ...
