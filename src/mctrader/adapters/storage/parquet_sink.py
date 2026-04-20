from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq

from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.ports.market_data import MarketDataSink

ORDERBOOK_DIFF_SCHEMA = pa.schema([
    pa.field("ts", pa.int64(), nullable=False),
    pa.field("seq", pa.int64(), nullable=False),
    pa.field("symbol", pa.string(), nullable=False),
    pa.field("market", pa.string(), nullable=False),
    pa.field("side", pa.string(), nullable=False),
    pa.field("price", pa.string(), nullable=False),
    pa.field("qty", pa.string(), nullable=False),
])

TRADE_SCHEMA = pa.schema([
    pa.field("ts", pa.int64(), nullable=False),
    pa.field("seq", pa.int64(), nullable=False),
    pa.field("symbol", pa.string(), nullable=False),
    pa.field("market", pa.string(), nullable=False),
    pa.field("price", pa.string(), nullable=False),
    pa.field("qty", pa.string(), nullable=False),
    pa.field("side", pa.string(), nullable=False),
])

# Rough per-row byte estimate used for flush_max_mb check. Exact measurement
# would require serialising the buffer; this is good enough for back-pressure.
_APPROX_BYTES_PER_ROW = 128


def _partition_key(event_type: str, symbol: str, ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return f"{event_type}/{symbol}/{dt.strftime('%Y-%m-%d')}/{dt.strftime('%H')}"


def _parquet_path(root: str, key: str) -> str:
    """Build parquet file path from partition key."""
    parts = key.split("/")
    event_type, symbol, date, hour = parts
    return os.path.join(
        root,
        event_type,
        f"symbol={symbol}",
        f"date={date}",
        f"hour={hour}.parquet",
    )


class ParquetSink(MarketDataSink):
    """
    Buffer market events in memory and flush to Parquet files.
    File path: {root}/{type}/symbol={symbol}/date={date}/hour={hour}.parquet
    """

    def __init__(
        self,
        root_path: str,
        flush_interval_sec: int = 60,
        flush_max_mb: int = 50,
    ) -> None:
        self._root = root_path
        self._flush_interval_sec = flush_interval_sec
        self._flush_max_bytes = flush_max_mb * 1024 * 1024
        self._buf: dict[str, list[dict]] = {}
        self._buf_row_count = 0
        self._last_flush_ts = time.monotonic()

    def write_orderbook_diff(self, event: OrderBookDiffEvent) -> None:
        key = _partition_key("orderbook_diff", event.symbol.name, event.ts)
        rows = self._buf.setdefault(key, [])
        base_row = self._base_row(event)

        for price, qty in event.bids_delta:
            rows.append({**base_row, "side": "bid", "price": str(price), "qty": str(qty)})
            self._buf_row_count += 1

        for price, qty in event.asks_delta:
            rows.append({**base_row, "side": "ask", "price": str(price), "qty": str(qty)})
            self._buf_row_count += 1

        if self._should_flush():
            self.flush()

    def write_trade(self, event: TradeEvent) -> None:
        key = _partition_key("trade", event.symbol.name, event.ts)
        rows = self._buf.setdefault(key, [])
        rows.append({
            "ts": event.ts,
            "seq": event.seq,
            "symbol": event.symbol.name,
            "market": event.symbol.market.value,
            "price": str(event.price),
            "qty": str(event.qty),
            "side": event.side,
        })
        self._buf_row_count += 1

        if self._should_flush():
            self.flush()

    def _base_row(self, event: OrderBookDiffEvent) -> dict:
        """Create base row dict common to all order book diff entries."""
        return {
            "ts": event.ts,
            "seq": event.seq,
            "symbol": event.symbol.name,
            "market": event.symbol.market.value,
        }

    def flush(self) -> None:
        for key, rows in self._buf.items():
            if not rows:
                continue
            path = _parquet_path(self._root, key)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            event_type = key.split("/")[0]
            schema = ORDERBOOK_DIFF_SCHEMA if event_type == "orderbook_diff" else TRADE_SCHEMA

            table = pa.Table.from_pylist(rows, schema=schema)
            pq.write_table(table, path, compression="snappy")

        self._buf.clear()
        self._buf_row_count = 0
        self._last_flush_ts = time.monotonic()

    def close(self) -> None:
        self.flush()

    def _should_flush(self) -> bool:
        elapsed = time.monotonic() - self._last_flush_ts
        if elapsed >= self._flush_interval_sec:
            return True
        estimated_bytes = self._buf_row_count * _APPROX_BYTES_PER_ROW
        return estimated_bytes >= self._flush_max_bytes
