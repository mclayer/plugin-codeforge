from __future__ import annotations

import os
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mctrader.dashboard.collector_status import (
    CollectorProcessInfo,
    aggregate_symbol_stats,
    build_collector_status,
    detect_collector_process,
    discover_symbols,
    list_today_files,
)

# ---------------------------------------------------------------------------
# Parquet fixture helpers
# ---------------------------------------------------------------------------


def _write_ob_parquet(root: str, symbol: str, date: str, hour: str, rows: list[dict]) -> str:
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("side", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
    ])
    dir_path = os.path.join(
        root, "orderbook_diff", f"symbol={symbol}", f"date={date}"
    )
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"hour={hour}_001.parquet")
    pq.write_table(pa.Table.from_pylist(rows, schema=schema), path)
    return path


def _write_trade_parquet(root: str, symbol: str, date: str, hour: str, rows: list[dict]) -> str:
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
        ("side", pa.string()),
    ])
    dir_path = os.path.join(
        root, "trade", f"symbol={symbol}", f"date={date}"
    )
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"hour={hour}_001.parquet")
    pq.write_table(pa.Table.from_pylist(rows, schema=schema), path)
    return path


@pytest.fixture()
def populated_root(tmp_path):
    root = str(tmp_path)
    _write_ob_parquet(root, "BTC_KRW", "2026-04-21", "00", [
        {"ts": 1776700000000, "seq": 1, "symbol": "BTC_KRW", "market": "bithumb",
         "side": "bid", "price": "100", "qty": "1"},
        {"ts": 1776700001000, "seq": 2, "symbol": "BTC_KRW", "market": "bithumb",
         "side": "ask", "price": "101", "qty": "2"},
    ])
    _write_trade_parquet(root, "BTC_KRW", "2026-04-21", "00", [
        {"ts": 1776700002000, "seq": 3, "symbol": "BTC_KRW", "market": "bithumb",
         "price": "100.5", "qty": "0.1", "side": "buy"},
    ])
    _write_ob_parquet(root, "ETH_KRW", "2026-04-21", "01", [
        {"ts": 1776703600000, "seq": 10, "symbol": "ETH_KRW", "market": "bithumb",
         "side": "bid", "price": "5000", "qty": "3"},
    ])
    return root


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDiscoverSymbols:
    def test_empty_root(self, tmp_path):
        assert discover_symbols(str(tmp_path)) == []

    def test_sorted_unique(self, populated_root):
        assert discover_symbols(populated_root) == ["BTC_KRW", "ETH_KRW"]


class TestAggregateSymbolStats:
    def test_empty_root(self, tmp_path):
        assert aggregate_symbol_stats(str(tmp_path)) == []

    def test_counts_and_max_ts(self, populated_root):
        stats = aggregate_symbol_stats(populated_root)
        by_symbol = {s.symbol: s for s in stats}

        btc = by_symbol["BTC_KRW"]
        assert btc.orderbook_row_count == 2
        assert btc.trade_count == 1
        assert btc.last_orderbook_ts == 1776700001000
        assert btc.last_trade_ts == 1776700002000
        assert btc.last_received_ts == 1776700002000

        eth = by_symbol["ETH_KRW"]
        assert eth.orderbook_row_count == 1
        assert eth.trade_count == 0
        assert eth.last_trade_ts is None


class TestListTodayFiles:
    def test_includes_files_with_today(self, populated_root):
        files = list_today_files(populated_root, today_utc="2026-04-21")
        paths = {(f.event_type, f.symbol, f.hour) for f in files}
        assert ("orderbook_diff", "BTC_KRW", "00") in paths
        assert ("trade", "BTC_KRW", "00") in paths
        assert ("orderbook_diff", "ETH_KRW", "01") in paths

    def test_excludes_other_dates(self, populated_root):
        files = list_today_files(populated_root, today_utc="2026-04-22")
        assert files == []

    def test_size_and_mtime_populated(self, populated_root):
        files = list_today_files(populated_root, today_utc="2026-04-21")
        assert files
        for f in files:
            assert f.size_bytes > 0
            assert f.mtime_ts > 0


class TestDetectCollectorProcess:
    def test_matches_known_cmdline(self):
        fake_output = (
            "  PID COMMAND\n"
            " 12345 /usr/bin/python -c from mctrader.app.collector_service import x\n"
            " 12346 /bin/zsh\n"
        )
        with patch("subprocess.check_output", return_value=fake_output):
            info = detect_collector_process()
        assert info.running is True
        assert info.pid == 12345
        assert info.detection == "ps"

    def test_no_match(self):
        fake_output = (
            "  PID COMMAND\n"
            " 100 /sbin/launchd\n"
        )
        with patch("subprocess.check_output", return_value=fake_output):
            info = detect_collector_process()
        assert info.running is False
        assert info.detection == "ps"

    def test_ps_unavailable(self):
        with patch("subprocess.check_output", side_effect=FileNotFoundError):
            info = detect_collector_process()
        assert info == CollectorProcessInfo(
            running=False, pid=None, cmdline=None, detection="unknown"
        )


class TestBuildCollectorStatus:
    def test_composes_all_fields(self, populated_root):
        status = build_collector_status(populated_root)
        assert status.data_root == populated_root
        assert len(status.symbols) == 2
        # today_files is date-sensitive; guard on presence of list
        assert isinstance(status.today_files, list)
