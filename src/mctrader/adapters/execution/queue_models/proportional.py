from __future__ import annotations

from decimal import Decimal

from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Order
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.ports.queue_model import QueuePositionModel, QueueState


class ProportionalQueueModel(QueuePositionModel):
    def __init__(self) -> None:
        # order_id -> qty_ahead
        self._queue: dict[str, Decimal] = {}
        # order_id -> (side_str, price)
        self._meta: dict[str, tuple[str, Decimal]] = {}
        # (side_str, price) -> last known level qty
        self._level_qty: dict[tuple[str, Decimal], Decimal] = {}

    def register(self, order: Order, snapshot: OrderBookSnapshot) -> None:
        intent = order.intent
        price = intent.price
        if price is None:
            self._queue[order.order_id] = Decimal(0)
            return

        side_str = intent.side.value
        levels = snapshot.bids if side_str == "buy" else snapshot.asks

        qty_ahead = Decimal(0)
        for level in levels:
            if level.price == price:
                qty_ahead = level.qty
                self._level_qty[(side_str, price)] = level.qty
                break

        self._queue[order.order_id] = qty_ahead
        self._meta[order.order_id] = (side_str, price)

    def on_trade(self, trade: TradeEvent) -> None:
        # trade directly clears qty_ahead by traded amount at that price
        for oid, (side, price) in list(self._meta.items()):
            if price == trade.price and side == trade.side:
                current = self._queue[oid]
                self._queue[oid] = max(Decimal(0), current - trade.qty)

    def on_diff(self, event: OrderBookDiffEvent) -> None:
        # when a level's total qty decreases (cancels or fills), our position
        # moves forward proportionally to the fraction that was removed
        for price, new_qty in event.bids_delta:
            self._apply_level_change("buy", price, new_qty)
        for price, new_qty in event.asks_delta:
            self._apply_level_change("sell", price, new_qty)

    def _apply_level_change(self, side: str, price: Decimal, new_qty: Decimal) -> None:
        key = (side, price)
        old_qty = self._level_qty.get(key)
        if old_qty is None:
            if new_qty > Decimal(0):
                self._level_qty[key] = new_qty
            return

        if new_qty >= old_qty:
            # level grew or unchanged — no forward movement
            self._level_qty[key] = new_qty
            return

        if new_qty == Decimal(0):
            self._level_qty.pop(key, None)
        else:
            self._level_qty[key] = new_qty

        # decrement qty_ahead proportionally for orders at this level
        removed = old_qty - new_qty
        for oid, (s, p) in self._meta.items():
            if s == side and p == price:
                current = self._queue[oid]
                if old_qty > Decimal(0):
                    # proportion of the level that was removed
                    fraction = removed / old_qty
                    reduction = current * fraction
                else:
                    reduction = current
                self._queue[oid] = max(Decimal(0), current - reduction)

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
