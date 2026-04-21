from __future__ import annotations

from decimal import Decimal

from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Order
from mctrader.domain.orderbook import Level, OrderBookSnapshot
from mctrader.ports.queue_model import QueuePositionModel, QueueState


class NaiveQueueModel(QueuePositionModel):
    """Naive queue position model. Tracks orders in queue by qty at price level."""

    def __init__(self) -> None:
        self._queue: dict[str, Decimal] = {}
        self._meta: dict[str, tuple[str, Decimal]] = {}

    def register(self, order: Order, snapshot: OrderBookSnapshot) -> None:
        intent = order.intent
        price = intent.price
        if price is None:
            self._queue[order.order_id] = Decimal(0)
            return

        side_str = intent.side.value
        levels = snapshot.bids if side_str == "buy" else snapshot.asks

        qty_ahead = self._get_qty_at_price(levels, price)
        self._queue[order.order_id] = qty_ahead
        self._meta[order.order_id] = (side_str, price)

    def on_trade(self, trade: TradeEvent) -> None:
        # decrement qty_ahead for orders whose side/price matches the trade
        for oid, (side, price) in list(self._meta.items()):
            if price == trade.price and side == trade.side:
                current = self._queue[oid]
                self._queue[oid] = max(Decimal(0), current - trade.qty)

    def on_diff(self, event: OrderBookDiffEvent) -> None:
        # Naive model ignores diff-driven depth changes; queue drains only via
        # trades.  Implemented as no-op to satisfy the port contract.
        pass

    def estimate(
        self,
        order: Order,
        snapshot: OrderBookSnapshot,
        recent_trades: list[TradeEvent],
    ) -> QueueState:
        qty_ahead = self._queue.get(order.order_id, Decimal(0))
        return QueueState(qty_ahead=qty_ahead, estimated_fill_ts=None)

    def remove(self, order_id: str) -> None:
        self._queue.pop(order_id, None)
        self._meta.pop(order_id, None)

    @staticmethod
    def _get_qty_at_price(levels: tuple[Level, ...], price: Decimal) -> Decimal:
        for level in levels:
            if level.price == price:
                return level.qty
        return Decimal(0)
