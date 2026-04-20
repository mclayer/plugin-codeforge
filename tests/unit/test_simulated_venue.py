"""Unit tests for SimulatedExecutionVenue."""
from __future__ import annotations

from decimal import Decimal

import pytest

from mctrader.adapters.execution.queue_models.naive import NaiveQueueModel
from mctrader.adapters.execution.simulated import SimulatedExecutionVenue
from mctrader.domain.events import OrderBookDiffEvent
from mctrader.domain.order import Fill, OrderIntent, OrderSide, OrderStatus, OrderType
from mctrader.domain.orderbook import Level, OrderBook, OrderBookSnapshot
from mctrader.domain.symbol import FeeSchedule, Market, Symbol
from mctrader.ports.clock import Clock

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)
FEE = FeeSchedule(maker=Decimal("0.002"), taker=Decimal("0.002"))


class FixedClock(Clock):
    """Deterministic clock for tests."""

    def __init__(self, ts: int = 1_000) -> None:
        self._ts = ts

    def now(self) -> int:
        return self._ts


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


def _venue() -> SimulatedExecutionVenue:
    return SimulatedExecutionVenue(
        fee_schedule=FEE,
        clock=FixedClock(),
        queue_model=NaiveQueueModel(),
    )


def _limit_intent(side: OrderSide, price: str, qty: str = "1") -> OrderIntent:
    return OrderIntent(
        symbol=SYMBOL,
        side=side,
        type=OrderType.LIMIT,
        price=Decimal(price),
        qty=Decimal(qty),
        ts=1_000,
    )


def _market_intent(side: OrderSide, qty: str = "1") -> OrderIntent:
    return OrderIntent(
        symbol=SYMBOL,
        side=side,
        type=OrderType.MARKET,
        price=None,
        qty=Decimal(qty),
        ts=1_000,
    )


class TestLimitBuy:
    def test_no_fill_when_best_ask_above_limit_price(self) -> None:
        venue = _venue()
        # best ask = 102, limit buy = 100: condition not met
        snap = _snapshot(bids=[("99", "1")], asks=[("102", "1")])
        intent = _limit_intent(OrderSide.BUY, price="100")
        venue.submit(intent)

        event = _diff_event(bids=[("99", "1")], asks=[("102", "1")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert fills == []
        assert len(venue.pending_orders()) == 1

    def test_fill_when_best_ask_at_or_below_limit_price(self) -> None:
        venue = _venue()
        # best ask = 100, limit buy = 100: condition met
        snap = _snapshot(bids=[("99", "1")], asks=[("100", "5")])
        intent = _limit_intent(OrderSide.BUY, price="100")
        venue.submit(intent)

        event = _diff_event(bids=[("99", "1")], asks=[("100", "5")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert len(fills) == 1
        fill = fills[0]
        assert isinstance(fill, Fill)
        assert fill.side == OrderSide.BUY
        assert fill.price == Decimal("100")
        assert fill.qty == Decimal("1")

    def test_fill_clears_pending_orders(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "1")], asks=[("100", "5")])
        venue.submit(_limit_intent(OrderSide.BUY, price="100"))

        event = _diff_event(bids=[("99", "1")], asks=[("100", "5")])
        venue.on_market_event(event, snap)
        venue.pop_events()

        assert venue.pending_orders() == []


class TestLimitSell:
    def test_no_fill_when_best_bid_below_limit_price(self) -> None:
        venue = _venue()
        # best bid = 98, limit sell = 100: condition not met
        snap = _snapshot(bids=[("98", "1")], asks=[("102", "1")])
        intent = _limit_intent(OrderSide.SELL, price="100")
        venue.submit(intent)

        event = _diff_event(bids=[("98", "1")], asks=[("102", "1")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert fills == []

    def test_fill_when_best_bid_at_or_above_limit_price(self) -> None:
        venue = _venue()
        # best bid = 100, limit sell = 100: condition met
        snap = _snapshot(bids=[("100", "5")], asks=[("102", "1")])
        intent = _limit_intent(OrderSide.SELL, price="100")
        venue.submit(intent)

        event = _diff_event(bids=[("100", "5")], asks=[("102", "1")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert len(fills) == 1
        fill = fills[0]
        assert fill.side == OrderSide.SELL
        assert fill.price == Decimal("100")


class TestMarketOrder:
    def test_market_buy_fills_immediately_at_best_ask(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "1")], asks=[("101", "10")])
        intent = _market_intent(OrderSide.BUY, qty="1")
        venue.submit(intent)

        event = _diff_event(bids=[("99", "1")], asks=[("101", "10")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert len(fills) == 1
        assert fills[0].price == Decimal("101")
        assert fills[0].side == OrderSide.BUY

    def test_market_sell_fills_immediately_at_best_bid(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "10")], asks=[("101", "1")])
        intent = _market_intent(OrderSide.SELL, qty="1")
        venue.submit(intent)

        event = _diff_event(bids=[("99", "10")], asks=[("101", "1")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        assert len(fills) == 1
        assert fills[0].price == Decimal("99")
        assert fills[0].side == OrderSide.SELL

    def test_fill_fee_calculated_from_taker_rate(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "10")], asks=[("100", "10")])
        venue.submit(_market_intent(OrderSide.BUY, qty="2"))

        event = _diff_event(bids=[("99", "10")], asks=[("100", "10")])
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        expected_fee = Decimal("2") * Decimal("100") * Decimal("0.002")
        assert fills[0].fee == expected_fee


class TestCancel:
    def test_cancel_removes_order_from_pending(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "1")], asks=[("102", "1")])
        ack = venue.submit(_limit_intent(OrderSide.BUY, price="100"))

        # make the snapshot known to venue so cancel has a valid state
        event = _diff_event(bids=[("99", "1")], asks=[("102", "1")])
        venue.on_market_event(event, snap)
        # no fill yet
        venue.pop_events()
        assert len(venue.pending_orders()) == 1

        cancel_ack = venue.cancel(ack.order_id)
        assert cancel_ack.success is True
        assert venue.pending_orders() == []

    def test_cancel_unknown_order_returns_failure(self) -> None:
        venue = _venue()
        cancel_ack = venue.cancel("nonexistent_id")
        assert cancel_ack.success is False

    def test_cancel_already_filled_order_returns_failure(self) -> None:
        venue = _venue()
        snap = _snapshot(bids=[("99", "1")], asks=[("100", "5")])
        ack = venue.submit(_limit_intent(OrderSide.BUY, price="100"))

        event = _diff_event(bids=[("99", "1")], asks=[("100", "5")])
        venue.on_market_event(event, snap)
        venue.pop_events()  # consume fill

        cancel_ack = venue.cancel(ack.order_id)
        assert cancel_ack.success is False


class TestNaiveQueueModel:
    def test_no_fill_when_qty_ahead_positive(self) -> None:
        """
        NaiveQueueModel registers qty_ahead from the existing level depth.
        If qty_ahead > 0, the limit order must not be filled.
        """
        venue = _venue()
        # best ask = 100 with qty=10: the order arrives and sees 10 ahead
        snap = _snapshot(bids=[("99", "1")], asks=[("100", "10")])
        # submit and register while snapshot is known
        event = _diff_event(bids=[("99", "1")], asks=[("100", "10")])
        venue.on_market_event(event, snap)

        ack = venue.submit(_limit_intent(OrderSide.BUY, price="100"))

        # fire another market event with same snapshot: qty_ahead still 10
        venue.on_market_event(event, snap)

        fills = venue.pop_events()
        # qty_ahead = 10 > 0, so no fill
        assert fills == []
        assert len(venue.pending_orders()) == 1

    def test_fill_after_queue_drains_via_trades(self) -> None:
        """
        Sending a TradeEvent at the limit price reduces qty_ahead.
        Once qty_ahead reaches 0 the limit order can be matched.
        """
        from mctrader.domain.events import TradeEvent

        venue = _venue()
        snap = _snapshot(bids=[("99", "1")], asks=[("100", "3")])

        # register the order against a snapshot showing qty=3 ahead
        setup_event = _diff_event(bids=[("99", "1")], asks=[("100", "3")])
        venue.on_market_event(setup_event, snap)

        ack = venue.submit(_limit_intent(OrderSide.BUY, price="100"))

        # simulate trades draining all 3 units ahead of our order
        trade = TradeEvent(
            symbol=SYMBOL,
            ts=1_001,
            seq=2,
            price=Decimal("100"),
            qty=Decimal("3"),
            side="buy",
        )
        venue.on_market_event(trade, snap)

        fills = venue.pop_events()
        assert len(fills) == 1
        assert fills[0].order_id == ack.order_id
