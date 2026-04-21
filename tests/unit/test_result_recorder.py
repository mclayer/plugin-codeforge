from __future__ import annotations

import json
import tempfile
from decimal import Decimal

import pyarrow.parquet as pq

from mctrader.app.result_recorder import ResultRecorder
from mctrader.domain.order import Fill, OrderSide
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.symbol import Market, Symbol

BTC = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)


def _make_fill(ts: int = 1000, price: str = "50000", qty: str = "0.1") -> Fill:
    return Fill(
        order_id="ord-1",
        symbol=BTC,
        side=OrderSide.BUY,
        price=Decimal(price),
        qty=Decimal(qty),
        fee=Decimal("0.001"),
        ts=ts,
    )


def _make_portfolio(cash: str = "1000000") -> Portfolio:
    return Portfolio(initial_cash=Decimal(cash))


class TestResultRecorderOnFill:
    def test_records_fill_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp)
            portfolio = _make_portfolio()
            rec.on_fill(_make_fill(), portfolio)
            rec.on_fill(_make_fill(), portfolio)
            assert rec.total_fills == 2

    def test_fill_data_written_to_parquet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp)
            portfolio = _make_portfolio()
            fill = _make_fill(ts=5000, price="50000", qty="0.2")
            rec.on_fill(fill, portfolio)
            rec.finalize()

            table = pq.read_table(f"{tmp}/trades.parquet")
            assert table.num_rows == 1
            row = table.to_pydict()
            assert row["ts"][0] == 5000
            assert row["price"][0] == "50000"
            assert row["qty"][0] == "0.2"
            assert row["side"][0] == "buy"


class TestResultRecorderOnEvent:
    def test_records_start_and_end_ts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp, equity_sample_interval=1)
            portfolio = _make_portfolio()
            rec.on_event(1000, 1, portfolio, {})
            rec.on_event(2000, 2, portfolio, {})
            assert rec.start_ts == 1000
            assert rec.end_ts == 2000

    def test_samples_equity_on_interval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp, equity_sample_interval=2)
            portfolio = _make_portfolio()
            rec.on_event(1000, 1, portfolio, {})  # no sample
            rec.on_event(2000, 2, portfolio, {})  # sample
            rec.on_event(3000, 3, portfolio, {})  # no sample
            rec.on_event(4000, 4, portfolio, {})  # sample
            rec.finalize()

            table = pq.read_table(f"{tmp}/equity_curve.parquet")
            assert table.num_rows == 2
            tss = table.to_pydict()["ts"]
            assert tss == [2000, 4000]


class TestResultRecorderFinalize:
    def test_creates_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result_dir = f"{tmp}/nested/results"
            rec = ResultRecorder(result_dir)
            rec.finalize()
            import os
            assert os.path.isdir(result_dir)

    def test_writes_all_three_files(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp)
            rec.finalize()
            assert os.path.exists(f"{tmp}/trades.parquet")
            assert os.path.exists(f"{tmp}/equity_curve.parquet")
            assert os.path.exists(f"{tmp}/summary.json")

    def test_summary_json_contains_expected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp, equity_sample_interval=1)
            portfolio = _make_portfolio()
            rec.on_fill(_make_fill(ts=1000), portfolio)
            rec.on_event(1000, 1, portfolio, {})
            rec.on_event(2000, 2, portfolio, {})
            rec.finalize()

            with open(f"{tmp}/summary.json") as f:
                summary = json.load(f)

            assert summary["total_fills"] == 1
            assert summary["start_ts"] == 1000
            assert summary["end_ts"] == 2000

    def test_empty_run_writes_empty_parquet_with_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rec = ResultRecorder(tmp)
            rec.finalize()

            trades = pq.read_table(f"{tmp}/trades.parquet")
            equity = pq.read_table(f"{tmp}/equity_curve.parquet")
            assert trades.num_rows == 0
            assert equity.num_rows == 0
            assert "ts" in trades.schema.names
            assert "ts" in equity.schema.names
