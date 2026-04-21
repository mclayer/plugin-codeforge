"""Unit tests for Bithumb WebSocket codec (new API: ws-api.bithumb.com)."""
from __future__ import annotations

from decimal import Decimal

from mctrader.adapters.exchanges.bithumb.codec import OrderBookDiffCalculator, decode
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol

# Each test uses its own calculator instance to avoid shared state
# (the module-level _diff_calc carries history between calls).

MARKET = Market.BITHUMB
SYMBOL = Symbol(base="BTC", quote="KRW", market=MARKET)


def _calc() -> OrderBookDiffCalculator:
    return OrderBookDiffCalculator()


def _orderbook_raw(
    code: str,
    timestamp: int,
    orderbook_units: list[dict],
) -> dict:
    return {
        "type": "orderbook",
        "code": code,
        "timestamp": timestamp,
        "orderbook_units": orderbook_units,
        "stream_type": "SNAPSHOT",
    }


def _trade_raw(
    code: str,
    trade_price: int | float,
    trade_volume: float,
    ask_bid: str,
    trade_timestamp: int,
    sequential_id: int | None = None,
) -> dict:
    raw: dict = {
        "type": "trade",
        "code": code,
        "trade_price": trade_price,
        "trade_volume": trade_volume,
        "ask_bid": ask_bid,
        "trade_timestamp": trade_timestamp,
        "stream_type": "REALTIME",
    }
    if sequential_id is not None:
        raw["sequential_id"] = sequential_id
    return raw


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
    """Tests for the top-level decode() function using new API raw message dicts."""

    def test_orderbook_first_message_returns_diff_event(self) -> None:
        calc = _calc()
        raw = _orderbook_raw(
            code="KRW-BTC",
            timestamp=1_725_927_377_287,
            orderbook_units=[
                {"bid_price": 100, "bid_size": 1.0, "ask_price": 101, "ask_size": 0.5},
                {"bid_price": 99, "bid_size": 2.0, "ask_price": 102, "ask_size": 0.3},
            ],
        )
        event = decode(raw, diff_calc=calc, market=MARKET)

        assert isinstance(event, OrderBookDiffEvent)
        assert event.symbol == SYMBOL
        assert len(event.bids_delta) == 2
        assert len(event.asks_delta) == 2

    def test_orderbook_symbol_parsed_from_code(self) -> None:
        calc = _calc()
        raw = _orderbook_raw(
            code="KRW-ETH",
            timestamp=1_725_927_377_000,
            orderbook_units=[
                {"bid_price": 200, "bid_size": 1.0, "ask_price": 201, "ask_size": 0.5},
            ],
        )
        event = decode(raw, diff_calc=calc, market=MARKET)

        assert isinstance(event, OrderBookDiffEvent)
        assert event.symbol.base == "ETH"
        assert event.symbol.quote == "KRW"

    def test_orderbook_second_message_computes_diff(self) -> None:
        calc = _calc()
        # first message establishes baseline
        decode(
            _orderbook_raw(
                code="KRW-BTC",
                timestamp=1_000,
                orderbook_units=[
                    {"bid_price": 100, "bid_size": 1.0, "ask_price": 101, "ask_size": 0.5},
                ],
            ),
            diff_calc=calc,
            market=MARKET,
        )
        # second message with one changed ask level
        event = decode(
            _orderbook_raw(
                code="KRW-BTC",
                timestamp=1_001,
                orderbook_units=[
                    {"bid_price": 100, "bid_size": 1.0, "ask_price": 101, "ask_size": 3.0},
                ],
            ),
            diff_calc=calc,
            market=MARKET,
        )

        assert isinstance(event, OrderBookDiffEvent)
        ask_dict = {p: q for p, q in event.asks_delta}
        assert ask_dict[Decimal("101")] == Decimal("3.0")
        # bids unchanged
        assert event.bids_delta == ()

    def test_trade_bid_decodes_to_buy(self) -> None:
        raw = _trade_raw(
            code="KRW-BTC",
            trade_price=50000,
            trade_volume=0.5,
            ask_bid="BID",
            trade_timestamp=1_713_600_000_000,
        )
        event = decode(raw, diff_calc=_calc(), market=MARKET)

        assert isinstance(event, TradeEvent)
        assert event.symbol == SYMBOL
        assert event.price == Decimal("50000")
        assert event.qty == Decimal("0.5")
        assert event.side == "buy"
        assert event.ts == 1_713_600_000_000

    def test_trade_ask_decodes_to_sell(self) -> None:
        raw = _trade_raw(
            code="KRW-BTC",
            trade_price=49000,
            trade_volume=1.2,
            ask_bid="ASK",
            trade_timestamp=1_713_600_000_001,
        )
        event = decode(raw, diff_calc=_calc(), market=MARKET)

        assert isinstance(event, TradeEvent)
        assert event.side == "sell"

    def test_trade_sequential_id_used_as_seq(self) -> None:
        raw = _trade_raw(
            code="KRW-BTC",
            trade_price=50000,
            trade_volume=0.1,
            ask_bid="BID",
            trade_timestamp=1_713_600_000_000,
            sequential_id=999_999,
        )
        event = decode(raw, diff_calc=_calc(), market=MARKET)

        assert isinstance(event, TradeEvent)
        assert event.seq == 999_999

    def test_trade_fallback_seq_to_trade_timestamp(self) -> None:
        raw = _trade_raw(
            code="KRW-BTC",
            trade_price=50000,
            trade_volume=0.1,
            ask_bid="BID",
            trade_timestamp=1_713_600_000_000,
        )
        event = decode(raw, diff_calc=_calc(), market=MARKET)

        assert isinstance(event, TradeEvent)
        assert event.seq == 1_713_600_000_000

    def test_unknown_type_returns_none(self) -> None:
        raw: dict = {"type": "ticker", "code": "KRW-BTC"}
        result = decode(raw, diff_calc=_calc(), market=MARKET)
        assert result is None

    def test_missing_type_returns_none(self) -> None:
        raw: dict = {"code": "KRW-BTC"}
        result = decode(raw, diff_calc=_calc(), market=MARKET)
        assert result is None
