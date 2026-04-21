"""Unit tests for ProportionalQueueModel — fractional qty_ahead reduction logic."""
from __future__ import annotations

from decimal import Decimal

from mctrader.adapters.execution.queue_models.proportional import ProportionalQueueModel
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Order, OrderIntent, OrderSide, OrderStatus, OrderType
from mctrader.domain.orderbook import Level, OrderBookSnapshot
from mctrader.domain.symbol import FeeSchedule, Market, Symbol

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)
FEE = FeeSchedule(maker=Decimal("0.002"), taker=Decimal("0.002"))


def _snapshot(
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
) -> OrderBookSnapshot:
    sorted_bids = tuple(
        Level(Decimal(p), Decimal(q))
        for p, q in sorted(bids, key=lambda x: Decimal(x[0]), reverse=True)
    )
    sorted_asks = tuple(
        Level(Decimal(p), Decimal(q))
        for p, q in sorted(asks, key=lambda x: Decimal(x[0]))
    )
    return OrderBookSnapshot(
        symbol=SYMBOL,
        ts=1_000,
        seq=1,
        bids=sorted_bids,
        asks=sorted_asks,
    )


def _order(
    order_id: str,
    side: OrderSide,
    price: str,
    ts: int = 1_000,
) -> Order:
    intent = OrderIntent(
        symbol=SYMBOL,
        side=side,
        type=OrderType.LIMIT,
        price=Decimal(price),
        qty=Decimal("1.0"),
        ts=ts,
    )
    return Order(
        order_id=order_id,
        intent=intent,
        status=OrderStatus.OPEN,
        filled_qty=Decimal("0"),
        avg_price=None,
        ts_submitted=ts,
        ts_updated=ts,
    )


def _diff_event(
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
    seq: int = 1,
) -> OrderBookDiffEvent:
    return OrderBookDiffEvent(
        symbol=SYMBOL,
        ts=1_000,
        seq=seq,
        bids_delta=tuple((Decimal(p), Decimal(q)) for p, q in bids),
        asks_delta=tuple((Decimal(p), Decimal(q)) for p, q in asks),
    )


def _trade(price: str, qty: str, side: str = "buy") -> TradeEvent:
    return TradeEvent(
        symbol=SYMBOL,
        ts=1_000,
        seq=1,
        price=Decimal(price),
        qty=Decimal(qty),
        side=side,
    )


class TestProportionalQueueModelRegister:
    def test_register_sets_qty_ahead_from_level(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("10.0")

    def test_register_market_order_has_zero_qty_ahead(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        intent = OrderIntent(
            symbol=SYMBOL, side=OrderSide.BUY, type=OrderType.MARKET,
            price=None, qty=Decimal("1.0"), ts=1_000,
        )
        order = Order(
            order_id="o1", intent=intent, status=OrderStatus.OPEN,
            filled_qty=Decimal("0"), avg_price=None,
            ts_submitted=1_000, ts_updated=1_000,
        )

        model.register(order, snap)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("0")

    def test_register_price_not_in_book_has_zero_qty_ahead(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("49000", "5.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")  # price not in book

        model.register(order, snap)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("0")


class TestProportionalQueueModelOnDiff:
    def test_level_decrease_reduces_qty_ahead_proportionally(self) -> None:
        """When level qty decreases from 10 to 6 (40% removed),
        an order with 8.0 qty_ahead should decrease by 40% → 4.8."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)
        assert model.estimate(order, snap, []).qty_ahead == Decimal("10.0")

        # Level drops from 10 to 6: removed = 4, fraction = 4/10 = 0.4
        event = _diff_event(bids=[("50000", "6.0")], asks=[])
        model.on_diff(event)

        state = model.estimate(order, snap, [])
        # qty_ahead was 10.0, reduced by 40% → 6.0
        assert state.qty_ahead == Decimal("6.0")

    def test_level_disappears_clears_qty_ahead(self) -> None:
        """When level qty drops to 0, qty_ahead becomes 0."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        # Level disappears entirely
        event = _diff_event(bids=[("50000", "0.0")], asks=[])
        model.on_diff(event)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("0")

    def test_level_increase_does_not_change_qty_ahead(self) -> None:
        """When level qty increases, qty_ahead should remain unchanged."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        # Level grows from 10 to 15
        event = _diff_event(bids=[("50000", "15.0")], asks=[])
        model.on_diff(event)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("10.0")

    def test_unrelated_level_change_does_not_affect_order(self) -> None:
        """A diff at a different price should not affect our order's qty_ahead."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0"), ("49000", "5.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        # Different price level drops
        event = _diff_event(bids=[("49000", "0.0")], asks=[])
        model.on_diff(event)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("10.0")

    def test_multiple_diffs_accumulate_correctly(self) -> None:
        """Sequential diffs should each proportionally reduce qty_ahead."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "100.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        # First diff: 100 → 80 (20% removed), qty_ahead: 100 → 80
        model.on_diff(_diff_event(bids=[("50000", "80.0")], asks=[]))
        # Second diff: 80 → 60 (25% removed), qty_ahead: 80 → 60
        model.on_diff(_diff_event(bids=[("50000", "60.0")], asks=[]))

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("60.0")

    def test_ask_side_order_tracks_ask_level(self) -> None:
        """An ask-side order should track ask level changes."""
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[], asks=[("50100", "8.0")])
        order = _order("o1", OrderSide.SELL, "50100")

        model.register(order, snap)
        assert model.estimate(order, snap, []).qty_ahead == Decimal("8.0")

        # Ask level drops from 8 to 4 (50% removed)
        event = _diff_event(bids=[], asks=[("50100", "4.0")])
        model.on_diff(event)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("4.0")


class TestProportionalQueueModelOnTrade:
    def test_trade_at_matching_price_reduces_qty_ahead(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        trade = _trade("50000", "3.0", "buy")
        model.on_trade(trade)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("7.0")

    def test_trade_at_different_price_does_not_affect_order(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        trade = _trade("49000", "5.0", "buy")
        model.on_trade(trade)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("10.0")

    def test_qty_ahead_cannot_go_below_zero(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "5.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)

        # Trade exceeds current qty_ahead
        trade = _trade("50000", "20.0", "buy")
        model.on_trade(trade)

        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("0")


class TestProportionalQueueModelRemove:
    def test_remove_cleans_up_order(self) -> None:
        model = ProportionalQueueModel()
        snap = _snapshot(bids=[("50000", "10.0")], asks=[])
        order = _order("o1", OrderSide.BUY, "50000")

        model.register(order, snap)
        model.remove(order.order_id)

        # After removal, estimate returns default zero state
        state = model.estimate(order, snap, [])
        assert state.qty_ahead == Decimal("0")

    def test_remove_nonexistent_order_does_not_raise(self) -> None:
        model = ProportionalQueueModel()
        model.remove("nonexistent-order-id")  # should not raise
