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


# Parquet schemas defined once at module level to avoid repeated construction.
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

_SUMMARY_FILENAME = "summary.json"
_TRADES_FILENAME = "trades.parquet"
_EQUITY_FILENAME = "equity_curve.parquet"


class ResultRecorder:
    """
    Accumulates fill and equity records during a backtest run and persists them
    as Parquet + JSON once finalize() is called.

    Files written:
      {result_path}/trades.parquet
      {result_path}/equity_curve.parquet
      {result_path}/summary.json

    Args:
        result_path: Directory to store backtest results
        equity_sample_interval: Record equity every N events (default 1000)
    """

    def __init__(self, result_path: str, equity_sample_interval: int = 1000) -> None:
        self._result_path = result_path
        self._equity_sample_interval = equity_sample_interval

        self._trade_rows: list[dict] = []
        self._equity_rows: list[dict] = []

        self._total_fills: int = 0
        self._start_ts: Optional[int] = None
        self._end_ts: Optional[int] = None

    # ------------------------------------------------------------------
    # Hot-path callbacks

    def on_fill(self, fill: Fill, portfolio: Portfolio) -> None:
        """Record a fill event to trades buffer."""
        self._total_fills += 1
        self._trade_rows.append(self._fill_to_row(fill))

    @staticmethod
    def _fill_to_row(fill: Fill) -> dict:
        """Convert Fill to Parquet row dict."""
        return {
            "ts": fill.ts,
            "order_id": fill.order_id,
            "symbol": str(fill.symbol),
            "side": fill.side.value,
            "price": str(fill.price),
            "qty": str(fill.qty),
            "fee": str(fill.fee),
        }

    def on_event(
        self,
        ts: int,
        event_count: int,
        portfolio: Portfolio,
        prices: dict[Symbol, Decimal],
    ) -> None:
        """Record event; sample equity on interval."""
        if self._start_ts is None:
            self._start_ts = ts
        self._end_ts = ts

        if event_count % self._equity_sample_interval != 0:
            return

        equity = portfolio.total_equity(prices)
        self._equity_rows.append(self._equity_to_row(ts, equity, portfolio, event_count))

    @staticmethod
    def _equity_to_row(ts: int, equity: Decimal, portfolio: Portfolio, event_count: int) -> dict:
        """Convert equity snapshot to Parquet row dict."""
        return {
            "ts": ts,
            "equity": str(equity),
            "cash": str(portfolio.cash),
            "event_count": event_count,
        }

    # ------------------------------------------------------------------

    def finalize(self) -> str:
        """Write accumulated records to Parquet and JSON files."""
        os.makedirs(self._result_path, exist_ok=True)

        trades_path = os.path.join(self._result_path, _TRADES_FILENAME)
        equity_path = os.path.join(self._result_path, _EQUITY_FILENAME)
        summary_path = os.path.join(self._result_path, _SUMMARY_FILENAME)

        _write_parquet(trades_path, _TRADES_SCHEMA, self._trade_rows)
        _write_parquet(equity_path, _EQUITY_SCHEMA, self._equity_rows)

        summary = {
            "total_fills": self._total_fills,
            "start_ts": self._start_ts,
            "end_ts": self._end_ts,
        }
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
    """Write rows to Parquet file, ensuring schema even if empty."""
    if rows:
        table = pa.Table.from_pylist(rows, schema=schema)
    else:
        table = _empty_table(schema)
    pq.write_table(table, path)


def _empty_table(schema: pa.Schema) -> pa.Table:
    """Create empty PyArrow table with correct schema."""
    return pa.table({
        name: pa.array([], type=schema.field(name).type)
        for name in schema.names
    })
