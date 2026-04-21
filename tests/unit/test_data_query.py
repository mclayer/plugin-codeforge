from __future__ import annotations

import os

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mctrader.dashboard.data_query import MAX_ROWS, query


def _write_parquet(path: str, rows: list[dict], schema: pa.Schema) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows, schema=schema), path)


@pytest.fixture()
def orderbook_root(tmp_path):
    root = str(tmp_path)
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("side", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
    ])
    rows = [
        {"ts": 1000 + i, "seq": i, "symbol": "BTC_KRW", "market": "bithumb",
         "side": "bid" if i % 2 == 0 else "ask",
         "price": str(100 + i), "qty": str(i + 1)}
        for i in range(5)
    ]
    path = os.path.join(
        root, "orderbook_diff", "symbol=BTC_KRW", "date=2026-04-21",
        "hour=00_001.parquet",
    )
    _write_parquet(path, rows, schema)
    return root


@pytest.fixture()
def trade_root(tmp_path):
    root = str(tmp_path)
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
        ("side", pa.string()),
    ])
    rows = [
        {"ts": 2000 + i, "seq": i, "symbol": "ETH_KRW", "market": "bithumb",
         "price": str(5000 + i), "qty": "1", "side": "buy" if i % 2 == 0 else "sell"}
        for i in range(3)
    ]
    path = os.path.join(
        root, "trade", "symbol=ETH_KRW", "date=2026-04-21",
        "hour=00_001.parquet",
    )
    _write_parquet(path, rows, schema)
    return root


class TestQueryOrderbook:
    def test_no_files(self, tmp_path):
        result = query(str(tmp_path), "orderbook_diff", "BTC_KRW", 0, 9999)
        assert result.total_count == 0
        assert result.returned_count == 0
        assert result.rows == []
        assert result.truncated is False

    def test_returns_matching_rows(self, orderbook_root):
        result = query(orderbook_root, "orderbook_diff", "BTC_KRW", 1000, 1002)
        assert result.total_count == 3
        assert result.returned_count == 3
        assert [r["ts"] for r in result.rows] == [1000, 1001, 1002]
        first = result.rows[0]
        assert first["side"] == "bid"
        assert first["price"] == "100"

    def test_respects_limit(self, orderbook_root):
        result = query(orderbook_root, "orderbook_diff", "BTC_KRW", 1000, 9999, limit=2)
        assert result.total_count == 5
        assert result.returned_count == 2
        assert result.truncated is True

    def test_filters_by_symbol(self, orderbook_root):
        result = query(orderbook_root, "orderbook_diff", "ETH_KRW", 0, 9999)
        assert result.total_count == 0


class TestQueryTrade:
    def test_returns_trade_rows(self, trade_root):
        result = query(trade_root, "trade", "ETH_KRW", 2000, 2002)
        assert result.total_count == 3
        assert result.returned_count == 3
        first = result.rows[0]
        assert "price" in first
        assert "side" in first
        assert first["side"] in ("buy", "sell")


class TestMaxRows:
    def test_default_limit_constant(self):
        assert MAX_ROWS == 200
