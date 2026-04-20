from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Protocol, runtime_checkable

from mctrader.domain.events import (
    ClockTickEvent,
    MarketEvent,
    OrderBookDiffEvent,
    TradeEvent,
)
from mctrader.domain.order import (
    ExecutionEvent,
    Fill,
    Order,
    OrderIntent,
    OrderSide,
    OrderStatus,
    OrderType,
)
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.domain.symbol import FeeSchedule
from mctrader.ports.clock import Clock
from mctrader.ports.execution import CancelAck, ExecutionVenue, OrderAck
from mctrader.ports.queue_model import QueuePositionModel


@runtime_checkable
class _ExtendedQueueModel(Protocol):
    def register(self, order: Order, snapshot: OrderBookSnapshot) -> None: ...
    def on_trade(self, trade: TradeEvent) -> None: ...
    def remove(self, order_id: str) -> None: ...


class SimulatedExecutionVenue(ExecutionVenue):
    def __init__(
        self,
        fee_schedule: FeeSchedule,
        clock: Clock,
        queue_model: QueuePositionModel,
    ) -> None:
        self._fee = fee_schedule
        self._clock = clock
        self._queue_model = queue_model
        self._orders: dict[str, Order] = {}  # order_id -> Order
        # latest snapshot provided by the caller
        self._snapshot: OrderBookSnapshot | None = None
        self._pending_events: list[ExecutionEvent] = []

    def submit(self, intent: OrderIntent) -> OrderAck:
        order_id = uuid.uuid4().hex[:16]
        ts = self._clock.now()
        order = Order(
            order_id=order_id,
            intent=intent,
            status=OrderStatus.OPEN,
            filled_qty=Decimal(0),
            avg_price=None,
            ts_submitted=ts,
            ts_updated=ts,
        )
        self._orders[order_id] = order

        if self._snapshot is not None and isinstance(self._queue_model, _ExtendedQueueModel):
            self._queue_model.register(order, self._snapshot)

        return OrderAck(order_id=order_id, ts=ts)

    def cancel(self, order_id: str) -> CancelAck:
        ts = self._clock.now()
        order = self._orders.get(order_id)
        if order is None or order.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
            return CancelAck(order_id=order_id, success=False, ts=ts)

        order.status = OrderStatus.CANCELLED
        order.ts_updated = ts
        if isinstance(self._queue_model, _ExtendedQueueModel):
            self._queue_model.remove(order_id)
        return CancelAck(order_id=order_id, success=True, ts=ts)

    def pending_orders(self) -> list[Order]:
        return [
            o for o in self._orders.values()
            if o.status in (OrderStatus.OPEN, OrderStatus.PARTIAL)
        ]

    def pop_events(self) -> list[ExecutionEvent]:
        events = self._pending_events
        self._pending_events = []
        return events

    def on_market_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot,
    ) -> None:
        self._snapshot = snapshot

        # 1. update queue model
        if isinstance(event, TradeEvent):
            if isinstance(self._queue_model, _ExtendedQueueModel):
                self._queue_model.on_trade(event)
        elif isinstance(event, OrderBookDiffEvent):
            # ProportionalQueueModel exposes on_diff; call if available
            on_diff = getattr(self._queue_model, "on_diff", None)
            if on_diff is not None:
                on_diff(event)

        # 2. try matching pending orders
        for order in self.pending_orders():
            fill = self._try_fill(order, snapshot)
            if fill is not None:
                self._pending_events.append(fill)

    # ------------------------------------------------------------------
    def _try_fill(
        self, order: Order, snapshot: OrderBookSnapshot
    ) -> Fill | None:
        intent = order.intent
        ts = self._clock.now()

        if intent.type == OrderType.MARKET:
            return self._try_market_fill(order, intent, snapshot, ts)

        return self._try_limit_fill(order, intent, snapshot, ts)

    def _try_market_fill(
        self,
        order: Order,
        intent: OrderIntent,
        snapshot: OrderBookSnapshot,
        ts: int,
    ) -> Fill | None:
        level = snapshot.asks[0] if intent.side == OrderSide.BUY else snapshot.bids[0]
        if level is None:
            return None
        return self._record_fill(order, level.price, intent.qty, ts)

    def _try_limit_fill(
        self,
        order: Order,
        intent: OrderIntent,
        snapshot: OrderBookSnapshot,
        ts: int,
    ) -> Fill | None:
        if intent.price is None:
            return None

        state = self._queue_model.estimate(order, snapshot, [])
        if state.qty_ahead > Decimal(0):
            return None

        if intent.side == OrderSide.BUY:
            best_ask = snapshot.asks[0] if snapshot.asks else None
            if best_ask is None or best_ask.price > intent.price:
                return None
            fill_price = intent.price
        else:
            best_bid = snapshot.bids[0] if snapshot.bids else None
            if best_bid is None or best_bid.price < intent.price:
                return None
            fill_price = intent.price

        return self._record_fill(order, fill_price, intent.qty, ts)

    def _record_fill(
        self, order: Order, price: Decimal, qty: Decimal, ts: int
    ) -> Fill:
        fee = qty * price * self._fee.taker
        order.status = OrderStatus.FILLED
        order.filled_qty = qty
        order.avg_price = price
        order.ts_updated = ts

        if isinstance(self._queue_model, _ExtendedQueueModel):
            self._queue_model.remove(order.order_id)

        return Fill(
            order_id=order.order_id,
            symbol=order.intent.symbol,
            side=order.intent.side,
            price=price,
            qty=qty,
            fee=fee,
            ts=ts,
        )
