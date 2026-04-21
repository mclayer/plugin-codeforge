from __future__ import annotations

import json
import os
import tempfile

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mctrader.dashboard.metrics import (
    _compute_mdd,
    _compute_sharpe,
    discover_runs,
    load_equity_series,
    load_metrics,
    load_trades,
)


def _write_summary(path: str, **kwargs: object) -> None:
    os.makedirs(path, exist_ok=True)
    defaults = {
        "total_fills": 5, "final_equity": "1100000", "realized_pnl": "50000",
        "start_ts": 1000, "end_ts": 9000,
    }
    defaults.update(kwargs)
    with open(os.path.join(path, "summary.json"), "w") as f:
        json.dump(defaults, f)


def _write_equity(path: str, rows: list[dict]) -> None:
    schema = pa.schema([
        ("ts", pa.int64()), ("equity", pa.string()),
        ("cash", pa.string()), ("event_count", pa.int64()),
    ])
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, os.path.join(path, "equity_curve.parquet"))


def _write_trades(path: str, rows: list[dict]) -> None:
    schema = pa.schema([
        ("ts", pa.int64()), ("order_id", pa.string()), ("symbol", pa.string()),
        ("side", pa.string()), ("price", pa.string()), ("qty", pa.string()), ("fee", pa.string()),
    ])
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, os.path.join(path, "trades.parquet"))


class TestDiscoverRuns:
    def test_finds_dirs_with_summary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_summary(os.path.join(tmp, "run_001"))
            _write_summary(os.path.join(tmp, "run_002"))
            os.makedirs(os.path.join(tmp, "not_a_run"))
            runs = discover_runs(tmp)
        assert "run_001" in runs
        assert "run_002" in runs
        assert "not_a_run" not in runs

    def test_returns_empty_for_missing_dir(self) -> None:
        assert discover_runs("/nonexistent/path") == []

    def test_returns_sorted_descending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for name in ["run_a", "run_b", "run_c"]:
                _write_summary(os.path.join(tmp, name))
            runs = discover_runs(tmp)
        assert runs == sorted(runs, reverse=True)


class TestLoadMetrics:
    def test_loads_basic_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run_001")
            _write_summary(path, total_fills=10, final_equity="1200000", realized_pnl="80000")
            _write_equity(path, [])
            m = load_metrics(path)
        assert m.run_id == "run_001"
        assert m.total_fills == 10
        assert m.final_equity == 1200000.0
        assert m.realized_pnl == 80000.0

    def test_computes_total_return(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run_001")
            _write_summary(path)
            _write_equity(path, [
                {"ts": 1000, "equity": "1000000", "cash": "1000000", "event_count": 1000},
                {"ts": 2000, "equity": "1100000", "cash": "900000", "event_count": 2000},
            ])
            m = load_metrics(path)
        assert m.total_return_pct == pytest.approx(10.0)

    def test_total_return_none_for_single_equity_point(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run_001")
            _write_summary(path)
            _write_equity(path, [
                {"ts": 1000, "equity": "1000000", "cash": "1000000", "event_count": 1000},
            ])
            m = load_metrics(path)
        assert m.total_return_pct is None


class TestLoadEquitySeries:
    def test_parses_equity_points(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_equity(tmp, [
                {"ts": 1000, "equity": "1000000", "cash": "800000", "event_count": 1000},
                {"ts": 2000, "equity": "1050000", "cash": "750000", "event_count": 2000},
            ])
            series = load_equity_series(tmp)
        assert len(series) == 2
        assert series[0].ts == 1000
        assert series[0].equity == 1000000.0
        assert series[1].cash == 750000.0

    def test_returns_empty_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            assert load_equity_series(tmp) == []


class TestLoadTrades:
    def test_parses_trade_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _write_trades(tmp, [
                {
                    "ts": 1000, "order_id": "ord-1", "symbol": "BTC_KRW",
                    "side": "buy", "price": "50000", "qty": "0.1", "fee": "5",
                },
            ])
            trades = load_trades(tmp)
        assert len(trades) == 1
        assert trades[0]["side"] == "buy"

    def test_returns_empty_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            assert load_trades(tmp) == []


class TestComputeMdd:
    def test_flat_equity_has_zero_mdd(self) -> None:
        assert _compute_mdd([1000.0, 1000.0, 1000.0]) == 0.0

    def test_always_rising_has_zero_mdd(self) -> None:
        assert _compute_mdd([1000.0, 1100.0, 1200.0]) == 0.0

    def test_drawdown_from_peak(self) -> None:
        # 1000 → 1200 (peak) → 900: dd = (1200-900)/1200 = 25%
        assert _compute_mdd([1000.0, 1200.0, 900.0]) == pytest.approx(25.0)

    def test_multiple_drawdowns_returns_max(self) -> None:
        # global peak=1200, final trough=800 → mdd=(1200-800)/1200=33.33%
        assert _compute_mdd([1000.0, 1200.0, 900.0, 1000.0, 800.0]) == pytest.approx(33.33)

    def test_empty_returns_zero(self) -> None:
        assert _compute_mdd([]) == 0.0


class TestComputeSharpe:
    def test_returns_none_for_insufficient_data(self) -> None:
        assert _compute_sharpe([]) is None
        assert _compute_sharpe([1000.0]) is None
        assert _compute_sharpe([1000.0, 1100.0]) is None

    def test_returns_none_for_zero_std(self) -> None:
        # 수익률이 정확히 동일한 경우 (2배씩 증가) → std=0 → None
        assert _compute_sharpe([1000.0, 2000.0, 4000.0, 8000.0]) is None

    def test_positive_for_upward_trend_with_variance(self) -> None:
        equities = [1000.0, 1050.0, 980.0, 1100.0, 1080.0, 1200.0]
        sharpe = _compute_sharpe(equities)
        assert sharpe is not None
        assert sharpe > 0
