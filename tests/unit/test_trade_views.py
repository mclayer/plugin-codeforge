"""Unit tests for dashboard trade view builders."""
from __future__ import annotations

import os
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mctrader.dashboard.views.trade_views import build_cvd, build_tape

_TRADE_SCHEMA = pa.schema([
    pa.field("ts", pa.int64()),
    pa.field("seq", pa.int64()),
    pa.field("symbol", pa.string()),
    pa.field("market", pa.string()),
    pa.field("price", pa.string()),
    pa.field("qty", pa.string()),
    pa.field("side", pa.string()),
])


def _write_trade_parquet(
    tmp_path,
    rows: list[dict],
    symbol: str = "BTC_KRW",
    market: str = "bithumb",
    date: str = "2026-04-21",
) -> str:
    root = str(tmp_path)
    dir_path = os.path.join(root, "trade", f"symbol={symbol}", f"date={date}")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, "hour=00.parquet")
    pq.write_table(pa.Table.from_pylist(rows, schema=_TRADE_SCHEMA), path)
    return root


def _trade_row(
    ts: int,
    seq: int,
    price: str,
    qty: str,
    side: str = "buy",
    symbol: str = "BTC_KRW",
    market: str = "bithumb",
) -> dict:
    return {
        "ts": ts,
        "seq": seq,
        "symbol": symbol,
        "market": market,
        "price": price,
        "qty": qty,
        "side": side,
    }


class TestBuildTape:
    def test_tape_size_bucket_distribution(self, tmp_path) -> None:
        # notionals: 100x4, 200x3, 500x2, 10000x1
        rows = [
            _trade_row(ts=1000 + i, seq=i, price="100", qty="1")   for i in range(4)
        ] + [
            _trade_row(ts=1010 + i, seq=10 + i, price="200", qty="1") for i in range(3)
        ] + [
            _trade_row(ts=1020 + i, seq=20 + i, price="500", qty="1") for i in range(2)
        ] + [
            _trade_row(ts=1030, seq=30, price="10000", qty="1"),
        ]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999, limit=500)

        assert len(entries) == 10

        notional_to_bucket = {e.notional: e.size_bucket for e in entries}
        # notional=100 (smallest) → "small"
        assert notional_to_bucket["100"] == "small"
        # notional=10000 (top 10%) → "large" or "whale"
        assert notional_to_bucket["10000"] in ("large", "whale")

    def test_tape_size_bucket_single_row(self, tmp_path) -> None:
        rows = [_trade_row(ts=1000, seq=1, price="50000", qty="0.1")]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)

        assert len(entries) == 1
        assert entries[0].size_bucket == "small"

    def test_tape_tick_dir_sequence(self, tmp_path) -> None:
        rows = [
            _trade_row(ts=1000, seq=1, price="50000", qty="1"),
            _trade_row(ts=1001, seq=2, price="51000", qty="1"),
            _trade_row(ts=1002, seq=3, price="51000", qty="1"),
            _trade_row(ts=1003, seq=4, price="49000", qty="1"),
        ]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)

        tick_dirs = [e.tick_dir for e in entries]
        assert tick_dirs == ["UP", "UP", "ZERO_UP", "DOWN"]

    def test_tape_limit(self, tmp_path) -> None:
        rows = [_trade_row(ts=1000 + i, seq=i, price="50000", qty="1") for i in range(20)]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999, limit=5)

        assert len(entries) == 5

    def test_tape_notional_calculation(self, tmp_path) -> None:
        rows = [_trade_row(ts=1000, seq=1, price="50000", qty="0.1")]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)

        assert entries[0].notional == "5000.0"

    def test_tape_empty_data(self, tmp_path) -> None:
        root = str(tmp_path)
        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)
        assert entries == []

    def test_tape_entry_fields_present(self, tmp_path) -> None:
        rows = [_trade_row(ts=1000, seq=1, price="50000", qty="0.5", side="sell")]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)

        e = entries[0]
        assert e.ts == 1000
        assert e.seq == 1
        assert e.symbol == "BTC_KRW"
        assert e.market == "bithumb"
        assert e.price == "50000"
        assert e.qty == "0.5"
        assert e.side == "sell"
        assert e.tick_dir in ("UP", "DOWN", "ZERO_UP", "ZERO_DOWN")
        assert e.size_bucket in ("small", "medium", "large", "whale")

    def test_tape_buy_sell_sides_preserved(self, tmp_path) -> None:
        rows = [
            _trade_row(ts=1000, seq=1, price="50000", qty="1", side="buy"),
            _trade_row(ts=1001, seq=2, price="50100", qty="1", side="sell"),
        ]
        root = _write_trade_parquet(tmp_path, rows)

        entries = build_tape(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)

        assert entries[0].side == "buy"
        assert entries[1].side == "sell"


class TestBuildCvd:
    def test_cvd_returns_empty_list(self, tmp_path) -> None:
        root = str(tmp_path)
        result = build_cvd(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)
        assert result == []

    def test_cvd_returns_list_type(self, tmp_path) -> None:
        rows = [_trade_row(ts=1000, seq=1, price="50000", qty="1", side="buy")]
        root = _write_trade_parquet(tmp_path, rows)

        result = build_cvd(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)
        assert isinstance(result, list)
