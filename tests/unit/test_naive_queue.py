"""Unit tests for NaiveQueueModel — validates QueuePositionModel port contract.

These tests pin down the post-ADR contract: every adapter of
``QueuePositionModel`` MUST implement the full lifecycle (register, on_trade,
on_diff, remove, estimate).  ``NaiveQueueModel.on_diff`` is specifically a
no-op — this file asserts that behavior so regressions are caught.
"""
from __future__ import annotations

import inspect
from decimal import Decimal

from mctrader.adapters.execution.queue_models.naive import NaiveQueueModel
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Order, OrderIntent, OrderSide, OrderStatus, OrderType
from mctrader.domain.orderbook import Level, OrderBookSnapshot
from mctrader.domain.symbol import Market, Symbol
from mctrader.ports.queue_model import QueuePositionModel

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)


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


def _order(order_id: str, side: OrderSide, price: str) -> Order:
    intent = OrderIntent(
        symbol=SYMBOL,
        side=side,
        type=OrderType.LIMIT,
        price=Decimal(price),
        qty=Decimal("1.0"),
        ts=1_000,
    )
    return Order(
        order_id=order_id,
        intent=intent,
        status=OrderStatus.OPEN,
        filled_qty=Decimal("0"),
        avg_price=None,
        ts_submitted=1_000,
        ts_updated=1_000,
    )


def _diff_event(
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
) -> OrderBookDiffEvent:
    return OrderBookDiffEvent(
        symbol=SYMBOL,
        ts=1_000,
        seq=1,
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


class TestNaiveQueueModelPortContract:
    """Verifies NaiveQueueModel satisfies the QueuePositionModel port contract.

    The port declares five abstract methods — register, on_trade, on_diff,
    remove, estimate.  If any is missing, abstractmethod enforcement will
    raise at instantiation.  This test freezes the contract explicitly so
    future port changes are caught by CI rather than at runtime in the venue.
    """

    def test_is_subclass_of_port(self) -> None:
        assert issubclass(NaiveQueueModel, QueuePositionModel)

    def test_can_instantiate_without_abstract_errors(self) -> None:
        # If any abstractmethod is unimplemented, this raises TypeError.
        NaiveQueueModel()

    def test_implements_all_port_methods(self) -> None:
        required = {"register", "on_trade", "on_diff", "remove", "estimate"}
        members = {
            name for name, _ in inspect.getmembers(NaiveQueueModel, inspect.isfunction)
        }
        missing = required - members
        assert not missing, f"NaiveQueueModel missing port methods: {missing}"


class TestNaiveQueueModelOnDiff:
    """on_diff is explicitly a no-op on NaiveQueueModel."""

    def test_on_diff_does_not_change_qty_ahead(self) -> None:
        model = NaiveQueueModel()
        snap = _snapshot(bids=[("100", "10")], asks=[])
        order = _order("o1", OrderSide.BUY, "100")

        model.register(order, snap)
        assert model.estimate(order, snap, []).qty_ahead == Decimal("10")

        # Even a diff that halves the level has no effect under the naive model.
        model.on_diff(_diff_event(bids=[("100", "5")], asks=[]))

        assert model.estimate(order, snap, []).qty_ahead == Decimal("10")

    def test_on_diff_does_not_raise_on_unknown_level(self) -> None:
        model = NaiveQueueModel()
        # No orders registered, no meta — should still be callable.
        model.on_diff(_diff_event(bids=[("100", "0")], asks=[("101", "3")]))

    def test_on_diff_returns_none(self) -> None:
        model = NaiveQueueModel()
        result = model.on_diff(_diff_event(bids=[], asks=[]))
        assert result is None


class TestNaiveQueueModelLifecycle:
    """End-to-end lifecycle: register -> on_trade -> estimate -> remove."""

    def test_full_lifecycle_buy_side(self) -> None:
        model = NaiveQueueModel()
        snap = _snapshot(bids=[("100", "7")], asks=[])
        order = _order("o1", OrderSide.BUY, "100")

        model.register(order, snap)
        assert model.estimate(order, snap, []).qty_ahead == Decimal("7")

        model.on_trade(_trade("100", "4", "buy"))
        assert model.estimate(order, snap, []).qty_ahead == Decimal("3")

        model.on_trade(_trade("100", "10", "buy"))  # over-drains -> clamp to 0
        assert model.estimate(order, snap, []).qty_ahead == Decimal("0")

        model.remove(order.order_id)
        # After remove, estimate falls back to the default zero state.
        assert model.estimate(order, snap, []).qty_ahead == Decimal("0")

    def test_remove_nonexistent_is_idempotent(self) -> None:
        model = NaiveQueueModel()
        model.remove("never-registered")  # should not raise
