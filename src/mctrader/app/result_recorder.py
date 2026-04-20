from __future__ import annotations

import json
import os
from decimal import Decimal
from typing import Optional

import pyarrow as pa
import pyarrow.parquet as pq

from mctrader.domain.order import Fill
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.symbol import Symbol


# Parquet schemas are defined once to avoid repeated construction.
_TRADES_SCHEMA = pa.schema([
    ("ts", pa.int64()),
    ("order_id", pa.string()),
    ("symbol", pa.string()),
    ("side", pa.string()),
    ("price", pa.string()),
    ("qty", pa.string()),
    ("fee", pa.string()),
])

_EQUITY_SCHEMA = pa.schema([
    ("ts", pa.int64()),
    ("equity", pa.string()),
    ("cash", pa.string()),
    ("event_count", pa.int64()),
])


class ResultRecorder:
    """
    Accumulates fill and equity records during a backtest run and persists them
    as Parquet + JSON once finalize() is called.

    Files written:
      {result_path}/trades.parquet
      {result_path}/equity_curve.parquet
      {result_path}/summary.json
    """

    def __init__(self, result_path: str, equity_sample_interval: int = 1000) -> None:
        self._result_path = result_path
        self._equity_sample_interval = equity_sample_interval

        self._trade_rows: list[dict] = []
        self._equity_rows: list[dict] = []

        # summary counters updated incrementally to avoid O(n) scans at finalize
        self._total_fills: int = 0
        self._start_ts: Optional[int] = None
        self._end_ts: Optional[int] = None

    # ------------------------------------------------------------------
    # Hot-path callbacks

    def on_fill(self, fill: Fill, portfolio: Portfolio) -> None:
        self._total_fills += 1
        self._trade_rows.append({
            "ts": fill.ts,
            "order_id": fill.order_id,
            "symbol": str(fill.symbol),
            "side": fill.side.value,
            "price": str(fill.price),
            "qty": str(fill.qty),
            "fee": str(fill.fee),
        })

    def on_event(
        self,
        ts: int,
        event_count: int,
        portfolio: Portfolio,
        prices: dict[Symbol, Decimal],
    ) -> None:
        if self._start_ts is None:
            self._start_ts = ts
        self._end_ts = ts

        if event_count % self._equity_sample_interval != 0:
            return

        equity = portfolio.total_equity(prices)
        self._equity_rows.append({
            "ts": ts,
            "equity": str(equity),
            "cash": str(portfolio.cash),
            "event_count": event_count,
        })

    # ------------------------------------------------------------------

    def finalize(self) -> str:
        os.makedirs(self._result_path, exist_ok=True)

        _write_parquet(
            os.path.join(self._result_path, "trades.parquet"),
            _TRADES_SCHEMA,
            self._trade_rows,
        )
        _write_parquet(
            os.path.join(self._result_path, "equity_curve.parquet"),
            _EQUITY_SCHEMA,
            self._equity_rows,
        )

        # The engine supplies final_equity and realized_pnl via summary.json;
        # we write what we know here and the engine overwrites with richer data.
        summary = {
            "total_fills": self._total_fills,
            "start_ts": self._start_ts,
            "end_ts": self._end_ts,
        }
        summary_path = os.path.join(self._result_path, "summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        return self._result_path

    # ------------------------------------------------------------------
    # Accessors used by BacktestEngine to enrich summary.json

    @property
    def total_fills(self) -> int:
        return self._total_fills

    @property
    def start_ts(self) -> Optional[int]:
        return self._start_ts

    @property
    def end_ts(self) -> Optional[int]:
        return self._end_ts


# ------------------------------------------------------------------
# helpers

def _write_parquet(path: str, schema: pa.Schema, rows: list[dict]) -> None:
    if rows:
        table = pa.Table.from_pylist(rows, schema=schema)
    else:
        # Write an empty table with the correct schema so downstream readers
        # never receive a missing file.
        table = pa.table({name: pa.array([], type=schema.field(name).type)
                          for name in schema.names})
    pq.write_table(table, path)
