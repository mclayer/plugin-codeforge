from __future__ import annotations

from decimal import Decimal

from mctrader.domain.events import TradeEvent
from mctrader.domain.order import Order, OrderSide
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.ports.queue_model import QueuePositionModel, QueueState


class NaiveQueueModel(QueuePositionModel):
    def __init__(self) -> None:
        # order_id -> qty_ahead
        self._queue: dict[str, Decimal] = {}
        # order_id -> (side, price) needed to match trade events
        self._meta: dict[str, tuple[str, Decimal]] = {}

    def register(self, order: Order, snapshot: OrderBookSnapshot) -> None:
        intent = order.intent
        price = intent.price
        if price is None:
            # market orders: no queue position needed
            self._queue[order.order_id] = Decimal(0)
            return

        side_str = intent.side.value  # "buy" | "sell"
        levels = snapshot.bids if side_str == "buy" else snapshot.asks

        qty_ahead = Decimal(0)
        for level in levels:
            if level.price == price:
                qty_ahead = level.qty
                break

        self._queue[order.order_id] = qty_ahead
        self._meta[order.order_id] = (side_str, price)

    def on_trade(self, trade: TradeEvent) -> None:
        # decrement qty_ahead for orders whose side/price matches the trade
        for oid, (side, price) in list(self._meta.items()):
            if price == trade.price and side == trade.side:
                current = self._queue[oid]
                self._queue[oid] = max(Decimal(0), current - trade.qty)

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
