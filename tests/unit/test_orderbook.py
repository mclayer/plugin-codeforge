"""Unit tests for OrderBook domain logic."""
from __future__ import annotations

from decimal import Decimal

from mctrader.domain.events import OrderBookDiffEvent
from mctrader.domain.orderbook import Level, OrderBook
from mctrader.domain.symbol import Market, Symbol

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)


def _diff(
    bids: list[tuple[str, str]],
    asks: list[tuple[str, str]],
    *,
    ts: int = 1_000,
    seq: int = 1,
) -> OrderBookDiffEvent:
    return OrderBookDiffEvent(
        symbol=SYMBOL,
        ts=ts,
        seq=seq,
        bids_delta=tuple((Decimal(p), Decimal(q)) for p, q in bids),
        asks_delta=tuple((Decimal(p), Decimal(q)) for p, q in asks),
    )


class TestOrderBookApplyDiff:
    def test_initial_empty_state_add_levels(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("100", "1.0"), ("99", "2.0")],
            asks=[("101", "0.5"), ("102", "3.0")],
        ))

        snap = book.snapshot()
        assert len(snap.bids) == 2
        assert len(snap.asks) == 2

    def test_update_existing_level_qty(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(bids=[("100", "1.0")], asks=[], seq=1))
        book.apply_diff(_diff(bids=[("100", "5.0")], asks=[], seq=2))

        snap = book.snapshot()
        assert snap.bids[0].qty == Decimal("5.0")

    def test_delete_level_with_zero_qty(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("100", "1.0"), ("99", "2.0")],
            asks=[],
            seq=1,
        ))
        book.apply_diff(_diff(bids=[("100", "0")], asks=[], seq=2))

        snap = book.snapshot()
        # price 100 is removed; only price 99 remains
        prices = [lvl.price for lvl in snap.bids]
        assert Decimal("100") not in prices
        assert Decimal("99") in prices

    def test_best_bid_returns_highest_price(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("100", "1.0"), ("99", "2.0"), ("98", "3.0")],
            asks=[],
        ))
        assert book.best_bid == Level(Decimal("100"), Decimal("1.0"))

    def test_best_ask_returns_lowest_price(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[],
            asks=[("102", "1.0"), ("101", "2.0"), ("103", "0.5")],
        ))
        assert book.best_ask == Level(Decimal("101"), Decimal("2.0"))

    def test_mid_price(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("100", "1.0")],
            asks=[("102", "1.0")],
        ))
        assert book.mid == Decimal("101")

    def test_spread(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("100", "1.0")],
            asks=[("103", "1.0")],
        ))
        assert book.spread == Decimal("3")

    def test_best_bid_none_when_empty(self) -> None:
        book = OrderBook(SYMBOL)
        assert book.best_bid is None

    def test_best_ask_none_when_empty(self) -> None:
        book = OrderBook(SYMBOL)
        assert book.best_ask is None

    def test_mid_none_when_no_asks(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(bids=[("100", "1.0")], asks=[]))
        assert book.mid is None

    def test_spread_none_when_no_bids(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(bids=[], asks=[("101", "1.0")]))
        assert book.spread is None

    def test_snapshot_bids_descending(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[("98", "1.0"), ("100", "2.0"), ("99", "3.0")],
            asks=[],
        ))
        snap = book.snapshot()
        prices = [lvl.price for lvl in snap.bids]
        assert prices == sorted(prices, reverse=True)

    def test_snapshot_asks_ascending(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(
            bids=[],
            asks=[("103", "1.0"), ("101", "2.0"), ("102", "3.0")],
        ))
        snap = book.snapshot()
        prices = [lvl.price for lvl in snap.asks]
        assert prices == sorted(prices)

    def test_snapshot_contains_ts_and_seq(self) -> None:
        book = OrderBook(SYMBOL)
        book.apply_diff(_diff(bids=[("100", "1")], asks=[], ts=9999, seq=42))
        snap = book.snapshot()
        assert snap.ts == 9999
        assert snap.seq == 42
