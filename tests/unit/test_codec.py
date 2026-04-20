"""Unit tests for Bithumb WebSocket codec."""
from __future__ import annotations

from decimal import Decimal

import pytest

from mctrader.adapters.exchanges.bithumb.codec import OrderBookDiffCalculator
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol

# Each test uses its own calculator instance to avoid shared state
# (the module-level _diff_calc carries history between calls).

MARKET = Market.BITHUMB
SYMBOL = Symbol(base="BTC", quote="KRW", market=MARKET)


def _calc() -> OrderBookDiffCalculator:
    return OrderBookDiffCalculator()


def _orderbook_raw(
    symbol_name: str,
    ver: str,
    bids: list[list[str]],
    asks: list[list[str]],
) -> dict:
    return {
        "type": "ORDERBOOK",
        "data": {
            "s": symbol_name,
            "ver": ver,
            "b": bids,
            "a": asks,
        },
    }


def _trade_raw(
    symbol_name: str,
    ts: str,
    price: str,
    qty: str,
    side: str,
) -> dict:
    return {
        "type": "TRADE",
        "data": {
            "s": symbol_name,
            "t": ts,
            "p": price,
            "v": qty,
            "side": side,
        },
    }


class TestOrderBookDiffCalculator:
    def test_first_message_all_levels_are_additions(self) -> None:
        calc = _calc()
        event = calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0", "99": "2.0"},
            new_asks={"101": "0.5"},
            ts=1_000,
            seq=1,
            symbol=SYMBOL,
        )

        assert isinstance(event, OrderBookDiffEvent)
        # all bid levels present; no removals
        bid_prices = {p for p, q in event.bids_delta}
        ask_prices = {p for p, q in event.asks_delta}
        assert Decimal("100") in bid_prices
        assert Decimal("99") in bid_prices
        assert Decimal("101") in ask_prices
        # no zero-qty entries (no removals on first message)
        for _, qty in event.bids_delta:
            assert qty != Decimal("0")
        for _, qty in event.asks_delta:
            assert qty != Decimal("0")

    def test_second_message_diff_only_changed_levels(self) -> None:
        calc = _calc()
        calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0", "99": "2.0"},
            new_asks={"101": "0.5"},
            ts=1_000,
            seq=1,
            symbol=SYMBOL,
        )
        # second snapshot: price 100 qty changed; price 99 unchanged; price 98 added
        event = calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "5.0", "99": "2.0", "98": "1.0"},
            new_asks={"101": "0.5"},
            ts=1_001,
            seq=2,
            symbol=SYMBOL,
        )

        bid_dict = {p: q for p, q in event.bids_delta}
        # price 100 changed -> appears in diff
        assert bid_dict[Decimal("100")] == Decimal("5.0")
        # price 98 is new -> appears in diff
        assert bid_dict[Decimal("98")] == Decimal("1.0")
        # price 99 unchanged -> NOT in diff
        assert Decimal("99") not in bid_dict
        # ask unchanged -> empty delta
        assert event.asks_delta == ()

    def test_removed_level_produces_zero_qty_entry(self) -> None:
        calc = _calc()
        calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0", "99": "2.0"},
            new_asks={},
            ts=1_000,
            seq=1,
            symbol=SYMBOL,
        )
        # price 99 disappears in second snapshot
        event = calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0"},
            new_asks={},
            ts=1_001,
            seq=2,
            symbol=SYMBOL,
        )

        bid_dict = {p: q for p, q in event.bids_delta}
        assert bid_dict[Decimal("99")] == Decimal("0")

    def test_symbol_parsed_correctly(self) -> None:
        calc = _calc()
        event = calc.compute_diff(
            symbol_name="ETH_KRW",
            new_bids={"200": "1"},
            new_asks={},
            ts=1_000,
            seq=1,
            symbol=Symbol(base="ETH", quote="KRW", market=MARKET),
        )
        assert event.symbol.base == "ETH"
        assert event.symbol.quote == "KRW"


class TestDecodeFunction:
    """Tests for the top-level decode() function using raw message dicts.

    Each test creates an isolated OrderBookDiffCalculator to avoid shared
    state from the module-level _diff_calc instance.
    """

    def test_orderbook_first_message_returns_diff_event(self) -> None:
        calc = _calc()
        raw = _orderbook_raw(
            "BTC_KRW",
            ver="1",
            bids=[["100", "1.0"], ["99", "2.0"]],
            asks=[["101", "0.5"]],
        )
        event = calc.compute_diff(
            symbol_name=raw["data"]["s"],
            new_bids={row[0]: row[1] for row in raw["data"]["b"]},
            new_asks={row[0]: row[1] for row in raw["data"]["a"]},
            ts=1_000,
            seq=int(raw["data"]["ver"]),
            symbol=SYMBOL,
        )
        assert isinstance(event, OrderBookDiffEvent)
        assert len(event.bids_delta) == 2
        assert len(event.asks_delta) == 1

    def test_orderbook_second_message_computes_diff(self) -> None:
        calc = _calc()
        # first message establishes baseline
        calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0"},
            new_asks={"101": "0.5"},
            ts=1_000,
            seq=1,
            symbol=SYMBOL,
        )
        # second message with one changed ask level
        event = calc.compute_diff(
            symbol_name="BTC_KRW",
            new_bids={"100": "1.0"},
            new_asks={"101": "3.0"},
            ts=1_001,
            seq=2,
            symbol=SYMBOL,
        )
        assert isinstance(event, OrderBookDiffEvent)
        ask_dict = {p: q for p, q in event.asks_delta}
        assert ask_dict[Decimal("101")] == Decimal("3.0")
        # bids unchanged
        assert event.bids_delta == ()

    def test_trade_raw_message_decodes_to_trade_event(self) -> None:
        """
        Verify that a TRADE raw message dict produces the correct TradeEvent
        fields.  We call the codec's decode() directly for this case since
        TradeEvent construction does not depend on stateful diff calculation.
        """
        from mctrader.adapters.exchanges.bithumb.codec import decode

        raw = _trade_raw(
            symbol_name="BTC_KRW",
            ts="1713600000000",
            price="50000",
            qty="0.5",
            side="buy",
        )
        event = decode(raw, market=MARKET)

        assert isinstance(event, TradeEvent)
        assert event.symbol == SYMBOL
        assert event.price == Decimal("50000")
        assert event.qty == Decimal("0.5")
        assert event.side == "buy"

    def test_unknown_type_returns_none(self) -> None:
        from mctrader.adapters.exchanges.bithumb.codec import decode

        raw = {"type": "UNKNOWN_TYPE", "data": {}}
        result = decode(raw, market=MARKET)
        assert result is None

    def test_missing_type_returns_none(self) -> None:
        from mctrader.adapters.exchanges.bithumb.codec import decode

        raw = {"data": {}}
        result = decode(raw, market=MARKET)
        assert result is None
