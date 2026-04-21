"""Unit tests for mctrader.domain.microstructure functions."""
from __future__ import annotations

from decimal import Decimal

import pytest

from mctrader.domain.microstructure import (
    classify_tick,
    cumulative_qty,
    imbalance,
    mid_price,
    spread_bps,
    trade_delta,
)
from mctrader.domain.orderbook import Level, OrderBookSnapshot
from mctrader.domain.symbol import Market, Symbol

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)


def _snap(
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
    ts: int = 1000,
    seq: int = 1,
) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        symbol=SYMBOL,
        ts=ts,
        seq=seq,
        bids=tuple(Level(Decimal(p), Decimal(q)) for p, q in bids),
        asks=tuple(Level(Decimal(p), Decimal(q)) for p, q in asks),
    )


class TestImbalance:
    def test_imbalance_empty_bids(self) -> None:
        snap = _snap(bids=[], asks=[("101", "1")])
        assert imbalance(snap) == -1.0

    def test_imbalance_empty_asks(self) -> None:
        snap = _snap(bids=[("100", "1")], asks=[])
        assert imbalance(snap) == 1.0

    def test_imbalance_both_empty(self) -> None:
        snap = _snap(bids=[], asks=[])
        assert imbalance(snap) == 0.0

    def test_imbalance_balanced(self) -> None:
        snap = _snap(bids=[("100", "1")], asks=[("101", "1")])
        assert imbalance(snap, depth=1) == pytest.approx(0.0)

    def test_imbalance_bid_heavy(self) -> None:
        snap = _snap(bids=[("100", "3")], asks=[("101", "1")])
        # (3-1)/(3+1) = 0.5
        assert imbalance(snap, depth=1) == pytest.approx(0.5)

    def test_imbalance_ask_heavy(self) -> None:
        snap = _snap(bids=[("100", "1")], asks=[("101", "3")])
        # (1-3)/(1+3) = -0.5
        assert imbalance(snap, depth=1) == pytest.approx(-0.5)

    def test_imbalance_depth_clamps(self) -> None:
        snap = _snap(
            bids=[("105", "1"), ("104", "1"), ("103", "1"), ("102", "1"), ("101", "1")],
            asks=[("106", "1"), ("107", "1"), ("108", "1"), ("109", "1"), ("110", "1")],
        )
        val_depth2 = imbalance(snap, depth=2)
        val_depth5 = imbalance(snap, depth=5)
        # depth=2: bid=2, ask=2 → 0.0; depth=5: bid=5, ask=5 → 0.0 (balanced)
        assert val_depth2 == pytest.approx(0.0)
        assert val_depth5 == pytest.approx(0.0)

    def test_imbalance_depth_clamps_asymmetric(self) -> None:
        snap = _snap(
            bids=[("105", "10"), ("104", "1"), ("103", "1")],
            asks=[("106", "1"), ("107", "1"), ("108", "1")],
        )
        val_depth1 = imbalance(snap, depth=1)
        val_depth3 = imbalance(snap, depth=3)
        # depth=1: bid=10, ask=1 → (10-1)/11 ≈ 0.818
        assert val_depth1 > val_depth3

    def test_imbalance_depth_exceeds_levels(self) -> None:
        snap = _snap(
            bids=[("100", "1"), ("99", "1"), ("98", "1")],
            asks=[("101", "1"), ("102", "1"), ("103", "1")],
        )
        # depth=10 but only 3 levels — should not raise, uses all 3
        result = imbalance(snap, depth=10)
        assert result == pytest.approx(0.0)


class TestCumulativeQty:
    def test_cumulative_empty(self) -> None:
        assert cumulative_qty(()) == []

    def test_cumulative_single(self) -> None:
        levels = (Level(Decimal("100"), Decimal("2.5")),)
        assert cumulative_qty(levels) == [Decimal("2.5")]

    def test_cumulative_multiple(self) -> None:
        levels = (
            Level(Decimal("100"), Decimal("1")),
            Level(Decimal("99"), Decimal("2")),
            Level(Decimal("98"), Decimal("3")),
        )
        assert cumulative_qty(levels) == [Decimal("1"), Decimal("3"), Decimal("6")]

    def test_cumulative_decimal_precision(self) -> None:
        qty = Decimal("0.00000001")
        levels = (
            Level(Decimal("100"), qty),
            Level(Decimal("99"), qty),
        )
        result = cumulative_qty(levels)
        assert result[0] == qty
        assert result[1] == Decimal("0.00000002")


class TestClassifyTick:
    def test_classify_first_tick_up(self) -> None:
        assert classify_tick(Decimal("100"), None, None) == "UP"

    def test_classify_first_tick_prev_dir_none(self) -> None:
        # prev_price=None always returns UP regardless of prev_dir
        assert classify_tick(Decimal("50000"), None, "DOWN") == "UP"

    def test_classify_uptick(self) -> None:
        assert classify_tick(Decimal("101"), Decimal("100"), "UP") == "UP"

    def test_classify_downtick(self) -> None:
        assert classify_tick(Decimal("99"), Decimal("100"), "UP") == "DOWN"

    def test_classify_zero_uptick(self) -> None:
        assert classify_tick(Decimal("100"), Decimal("100"), "UP") == "ZERO_UP"

    def test_classify_zero_uptick_from_zero_up(self) -> None:
        assert classify_tick(Decimal("100"), Decimal("100"), "ZERO_UP") == "ZERO_UP"

    def test_classify_zero_downtick(self) -> None:
        assert classify_tick(Decimal("100"), Decimal("100"), "DOWN") == "ZERO_DOWN"

    def test_classify_zero_downtick_from_zero_down(self) -> None:
        assert classify_tick(Decimal("100"), Decimal("100"), "ZERO_DOWN") == "ZERO_DOWN"

    def test_classify_chain_sequence(self) -> None:
        prices = [Decimal("100"), Decimal("101"), Decimal("101"), Decimal("99"), Decimal("99")]
        expected = ["UP", "UP", "ZERO_UP", "DOWN", "ZERO_DOWN"]

        results = []
        prev_price = None
        prev_dir = None
        for price in prices:
            d = classify_tick(price, prev_price, prev_dir)
            results.append(d)
            prev_price = price
            prev_dir = d

        assert results == expected


class TestSpreadBps:
    def test_spread_bps_normal(self) -> None:
        snap = _snap(bids=[("10000", "1")], asks=[("10001", "1")])
        result = spread_bps(snap)
        assert result is not None
        # spread=1, mid=10000.5 → bps ≈ 1/10000.5*10000 ≈ 1.0
        assert result == pytest.approx(1.0, abs=0.01)

    def test_spread_bps_one_sided_bids_only(self) -> None:
        snap = _snap(bids=[("10000", "1")], asks=[])
        assert spread_bps(snap) is None

    def test_spread_bps_one_sided_asks_only(self) -> None:
        snap = _snap(bids=[], asks=[("10000", "1")])
        assert spread_bps(snap) is None

    def test_spread_bps_both_empty(self) -> None:
        snap = _snap(bids=[], asks=[])
        assert spread_bps(snap) is None


class TestTradeDelta:
    def test_delta_buy(self) -> None:
        assert trade_delta("buy", Decimal("1.5")) == Decimal("1.5")

    def test_delta_sell(self) -> None:
        assert trade_delta("sell", Decimal("1.5")) == Decimal("-1.5")

    def test_delta_invalid_side(self) -> None:
        assert trade_delta("unknown", Decimal("1.0")) == Decimal("0")

    def test_delta_buy_zero(self) -> None:
        assert trade_delta("buy", Decimal("0")) == Decimal("0")

    def test_delta_sell_small(self) -> None:
        assert trade_delta("sell", Decimal("0.00000001")) == Decimal("-0.00000001")
