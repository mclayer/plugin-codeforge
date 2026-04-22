"""Unit tests for dashboard orderbook view builders."""
from __future__ import annotations

import os
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mctrader.dashboard.db import close_duckdb, init_duckdb
from mctrader.dashboard.views.orderbook_views import (
    build_imbalance_series,
    build_snapshot_view,
)


@pytest.fixture(autouse=True)
def _duckdb_lifecycle():
    """build_imbalance_series가 get_duckdb()를 직접 사용하므로 각 테스트마다 초기화/정리."""
    init_duckdb()
    yield
    close_duckdb()

_OB_SCHEMA = pa.schema([
    pa.field("ts", pa.int64()),
    pa.field("seq", pa.int64()),
    pa.field("symbol", pa.string()),
    pa.field("market", pa.string()),
    pa.field("side", pa.string()),
    pa.field("price", pa.string()),
    pa.field("qty", pa.string()),
])


def _write_orderbook_parquet(
    tmp_path,
    rows: list[dict],
    symbol: str = "BTC_KRW",
    market: str = "bithumb",
    date: str = "2026-04-21",
) -> str:
    root = str(tmp_path)
    dir_path = os.path.join(root, "orderbook_diff", f"symbol={symbol}", f"date={date}")
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, "hour=00.parquet")
    pq.write_table(pa.Table.from_pylist(rows, schema=_OB_SCHEMA), path)
    return root


def _ob_row(
    ts: int,
    seq: int,
    side: str,
    price: str,
    qty: str,
    symbol: str = "BTC_KRW",
    market: str = "bithumb",
) -> dict:
    return {
        "ts": ts,
        "seq": seq,
        "symbol": symbol,
        "market": market,
        "side": side,
        "price": price,
        "qty": qty,
    }


class TestBuildSnapshotView:
    def test_snapshot_view_basic(self, tmp_path) -> None:
        rows = [
            # seq=1: add bid 100000 qty=1, ask 101000 qty=2
            _ob_row(ts=1000, seq=1, side="bid", price="100000", qty="1"),
            _ob_row(ts=1000, seq=1, side="ask", price="101000", qty="2"),
            # seq=2: add bid 99000 qty=3, ask 102000 qty=1
            _ob_row(ts=2000, seq=2, side="bid", price="99000", qty="3"),
            _ob_row(ts=2000, seq=2, side="ask", price="102000", qty="1"),
            # seq=3: remove bid 100000 (qty=0)
            _ob_row(ts=3000, seq=3, side="bid", price="100000", qty="0"),
        ]
        root = _write_orderbook_parquet(tmp_path, rows)

        view = build_snapshot_view(root, "BTC_KRW", "bithumb", as_of_ts=3000)

        bid_prices = [lvl.price for lvl in view.bids]
        ask_prices = [lvl.price for lvl in view.asks]

        assert "100000" not in bid_prices
        assert "99000" in bid_prices
        assert "101000" in ask_prices
        assert "102000" in ask_prices
        # asks total=3, bids total=3 → balanced or ask-heavy (99000 qty=3 vs asks total=3)
        assert view.imbalance is not None

    def test_snapshot_view_cumulative_qty(self, tmp_path) -> None:
        rows = [
            _ob_row(ts=1000, seq=1, side="bid", price="103000", qty="1"),
            _ob_row(ts=1000, seq=1, side="bid", price="102000", qty="2"),
            _ob_row(ts=1000, seq=1, side="bid", price="101000", qty="3"),
            _ob_row(ts=1000, seq=1, side="ask", price="104000", qty="1"),
        ]
        root = _write_orderbook_parquet(tmp_path, rows)

        view = build_snapshot_view(root, "BTC_KRW", "bithumb", as_of_ts=1000, depth=3)

        assert len(view.bids) == 3
        assert view.bids[0].cumulative_qty == "1"
        assert view.bids[1].cumulative_qty == "3"
        assert view.bids[2].cumulative_qty == "6"
        assert view.bids[-1].depth_pct == pytest.approx(100.0, abs=0.1)

    def test_snapshot_view_symbol_and_market_in_result(self, tmp_path) -> None:
        rows = [_ob_row(ts=1000, seq=1, side="bid", price="50000", qty="1")]
        root = _write_orderbook_parquet(tmp_path, rows)

        view = build_snapshot_view(root, "BTC_KRW", "bithumb", as_of_ts=1000)

        assert view.symbol == "BTC_KRW"
        assert view.market == "bithumb"

    def test_snapshot_view_mid_price_present(self, tmp_path) -> None:
        rows = [
            _ob_row(ts=1000, seq=1, side="bid", price="100000", qty="1"),
            _ob_row(ts=1000, seq=1, side="ask", price="100200", qty="1"),
        ]
        root = _write_orderbook_parquet(tmp_path, rows)

        view = build_snapshot_view(root, "BTC_KRW", "bithumb", as_of_ts=1000)

        assert view.mid_price is not None
        assert view.spread is not None
        assert view.spread_bps is not None

    def test_snapshot_view_no_data_returns_empty_book(self, tmp_path) -> None:
        root = str(tmp_path)
        # No parquet files written → empty book
        view = build_snapshot_view(root, "BTC_KRW", "bithumb", as_of_ts=9999)

        assert view.bids == []
        assert view.asks == []
        assert view.mid_price is None
        assert view.spread is None
        assert view.imbalance == 0.0


class TestBuildImbalanceSeries:
    def test_imbalance_series_empty_range(self, tmp_path) -> None:
        root = str(tmp_path)
        result = build_imbalance_series(root, "BTC_KRW", "bithumb", start_ts=0, end_ts=9999)
        assert result == []

    def test_imbalance_series_two_buckets(self, tmp_path) -> None:
        rows = [
            # bucket at 0ms
            _ob_row(ts=500, seq=1, side="bid", price="100000", qty="2"),
            _ob_row(ts=500, seq=1, side="ask", price="101000", qty="1"),
            # bucket at 1000ms
            _ob_row(ts=1500, seq=2, side="bid", price="99000", qty="1"),
            _ob_row(ts=1500, seq=2, side="ask", price="102000", qty="3"),
        ]
        root = _write_orderbook_parquet(tmp_path, rows)

        result = build_imbalance_series(
            root, "BTC_KRW", "bithumb",
            start_ts=0, end_ts=2000,
            bucket_ms=1000,
        )

        assert len(result) >= 1
        # Each point has ts and imbalance
        for point in result:
            assert isinstance(point.ts, int)
            assert isinstance(point.imbalance, float)

    def test_imbalance_series_returns_imbalance_point_type(self, tmp_path) -> None:
        rows = [
            _ob_row(ts=100, seq=1, side="bid", price="100000", qty="3"),
            _ob_row(ts=100, seq=1, side="ask", price="101000", qty="1"),
        ]
        root = _write_orderbook_parquet(tmp_path, rows)

        result = build_imbalance_series(
            root, "BTC_KRW", "bithumb",
            start_ts=0, end_ts=500,
            bucket_ms=250,
        )

        assert len(result) >= 1
        # bid heavy → positive imbalance
        assert result[0].imbalance > 0.0
