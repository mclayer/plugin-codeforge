from __future__ import annotations

import os
import tempfile
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq

from mctrader.adapters.storage.duckdb_source import DuckDBSource, _merge_sorted
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol

BTC = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)


def _ob_row(ts: int, seq: int, side: str, price: str, qty: str) -> dict[str, object]:
    return {
        "ts": ts, "seq": seq, "symbol": "BTC_KRW", "market": "bithumb",
        "side": side, "price": price, "qty": qty,
    }


def _tr_row(ts: int, seq: int, price: str, qty: str, side: str) -> dict[str, object]:
    return {
        "ts": ts, "seq": seq, "symbol": "BTC_KRW", "market": "bithumb",
        "price": price, "qty": qty, "side": side,
    }


def _write_orderbook_parquet(root: str, rows: list[dict]) -> None:
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("side", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
    ])
    path = os.path.join(root, "orderbook_diff", "symbol=BTC_KRW", "date=20240101")
    os.makedirs(path, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, os.path.join(path, "hour=00.parquet"))


def _write_trade_parquet(root: str, rows: list[dict]) -> None:
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
        ("side", pa.string()),
    ])
    path = os.path.join(root, "trade", "symbol=BTC_KRW", "date=20240101")
    os.makedirs(path, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, os.path.join(path, "hour=00.parquet"))


class TestDuckDBSourceOrderbook:
    def test_streams_orderbook_diff_events(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write_orderbook_parquet(root, [
                _ob_row(1000, 1, "bid", "50000", "1.0"),
                _ob_row(1000, 1, "ask", "50100", "0.5"),
            ])
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 0, 9999))

        assert len(events) == 1
        assert isinstance(events[0], OrderBookDiffEvent)
        assert events[0].ts == 1000
        assert events[0].bids_delta == ((Decimal("50000"), Decimal("1.0")),)
        assert events[0].asks_delta == ((Decimal("50100"), Decimal("0.5")),)

    def test_groups_same_ts_seq_into_one_event(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write_orderbook_parquet(root, [
                _ob_row(1000, 1, "bid", "50000", "1.0"),
                _ob_row(1000, 1, "bid", "49900", "2.0"),
                _ob_row(2000, 2, "ask", "50100", "0.5"),
            ])
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 0, 9999))

        assert len(events) == 2
        assert len(events[0].bids_delta) == 2
        assert len(events[1].asks_delta) == 1

    def test_filters_by_time_range(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write_orderbook_parquet(root, [
                _ob_row(500, 1, "bid", "50000", "1.0"),
                _ob_row(1500, 2, "bid", "50000", "1.0"),
                _ob_row(3000, 3, "bid", "50000", "1.0"),
            ])
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 1000, 2000))

        assert len(events) == 1
        assert events[0].ts == 1500

    def test_returns_empty_when_no_parquet_files(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 0, 9999))
        assert events == []


class TestDuckDBSourceTrades:
    def test_streams_trade_events(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write_trade_parquet(root, [
                _tr_row(1000, 1, "50000", "0.1", "buy"),
            ])
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 0, 9999))

        assert len(events) == 1
        assert isinstance(events[0], TradeEvent)
        assert events[0].price == Decimal("50000")
        assert events[0].qty == Decimal("0.1")
        assert events[0].side == "buy"


class TestDuckDBSourceMerge:
    def test_orderbook_and_trade_merged_by_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            _write_orderbook_parquet(root, [
                _ob_row(2000, 1, "bid", "50000", "1.0"),
            ])
            _write_trade_parquet(root, [
                _tr_row(1000, 1, "50000", "0.1", "buy"),
                _tr_row(3000, 2, "50000", "0.1", "sell"),
            ])
            source = DuckDBSource(root)
            events = list(source.stream([BTC], 0, 9999))

        assert len(events) == 3
        assert isinstance(events[0], TradeEvent)       # ts=1000
        assert isinstance(events[1], OrderBookDiffEvent)  # ts=2000
        assert isinstance(events[2], TradeEvent)       # ts=3000


class TestMergeSorted:
    def test_merges_two_sorted_iterators(self) -> None:
        def _ob(ts: int) -> OrderBookDiffEvent:
            return OrderBookDiffEvent(symbol=BTC, ts=ts, seq=0, bids_delta=(), asks_delta=())

        def _tr(ts: int) -> TradeEvent:
            return TradeEvent(
                symbol=BTC, ts=ts, seq=0, price=Decimal(1), qty=Decimal(1), side="buy"
            )

        result = list(_merge_sorted(iter([_ob(1), _ob(3)]), iter([_tr(2), _tr(4)])))
        assert [e.ts for e in result] == [1, 2, 3, 4]

    def test_handles_empty_first_iterator(self) -> None:
        def _tr(ts: int) -> TradeEvent:
            return TradeEvent(
                symbol=BTC, ts=ts, seq=0, price=Decimal(1), qty=Decimal(1), side="buy"
            )

        result = list(_merge_sorted(iter([]), iter([_tr(1), _tr(2)])))
        assert len(result) == 2

    def test_handles_empty_second_iterator(self) -> None:
        def _ob(ts: int) -> OrderBookDiffEvent:
            return OrderBookDiffEvent(symbol=BTC, ts=ts, seq=0, bids_delta=(), asks_delta=())

        result = list(_merge_sorted(iter([_ob(1), _ob(2)]), iter([])))
        assert len(result) == 2
