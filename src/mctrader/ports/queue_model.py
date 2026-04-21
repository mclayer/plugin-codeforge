from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Order
from mctrader.domain.orderbook import OrderBookSnapshot


@dataclass
class QueueState:
    qty_ahead: Decimal
    estimated_fill_ts: int | None  # None if not estimable


class QueuePositionModel(ABC):
    """Port contract for queue-position tracking.

    Implementations must manage the full order lifecycle — registration on
    submit, market-event driven updates (trades and diffs), queue estimation,
    and removal on cancel/fill.  Adapters (e.g. SimulatedExecutionVenue)
    consume this interface directly and must not inspect implementation types.
    """

    @abstractmethod
    def register(self, order: Order, snapshot: OrderBookSnapshot) -> None:
        """Register a newly submitted order, capturing its initial queue position."""

    @abstractmethod
    def on_trade(self, trade: TradeEvent) -> None:
        """Update queue positions in response to a trade event."""

    @abstractmethod
    def on_diff(self, event: OrderBookDiffEvent) -> None:
        """Update queue positions in response to an order-book diff event.

        Implementations that do not model book-depth changes (e.g. naive FIFO)
        may provide a no-op body (``pass``).
        """

    @abstractmethod
    def remove(self, order_id: str) -> None:
        """Remove an order from tracking (on cancel or terminal fill)."""

    @abstractmethod
    def estimate(
        self,
        order: Order,
        snapshot: OrderBookSnapshot,
        recent_trades: list[TradeEvent],
    ) -> QueueState:
        """Return the current queue state for ``order``."""
