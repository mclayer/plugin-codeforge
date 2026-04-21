from __future__ import annotations

import glob as _glob
import os
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

import duckdb

from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol
from mctrader.ports.market_data import MarketDataSource


def _symbol_obj(symbol_name: str, market_str: str) -> Symbol:
    base, quote = symbol_name.split("_")
    return Symbol(base=base, quote=quote, market=Market(market_str))


def _parquet_glob(root: str, event_type: str) -> str:
    return os.path.join(root, event_type, "symbol=*", "date=*", "hour=*.parquet")


class DuckDBSource(MarketDataSource):
    """
    Stream MarketEvents from Parquet files sorted by timestamp.
    Uses DuckDB for partition pruning and SQL queries.
    """

    def __init__(self, root_path: str) -> None:
        self._root = root_path

    def stream(
        self,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
    ) -> Iterator[MarketEvent]:
        ob_iter = self._query_orderbook(symbols, start_ts, end_ts)
        trade_iter = self._query_trades(symbols, start_ts, end_ts)
        yield from _merge_sorted(ob_iter, trade_iter)

    def _query_orderbook(
        self,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
    ) -> Iterator[OrderBookDiffEvent]:
        pattern = _parquet_glob(self._root, "orderbook_diff")
        if not _glob.glob(pattern):
            return

        rows = self._execute_query(
            pattern,
            symbols,
            start_ts,
            end_ts,
            "SELECT ts, seq, symbol, market, side, price, qty",
            "ORDER BY ts, seq, symbol",
        )
        yield from _reconstruct_orderbook_events(rows)

    def _query_trades(
        self,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
    ) -> Iterator[TradeEvent]:
        pattern = _parquet_glob(self._root, "trade")
        if not _glob.glob(pattern):
            return

        rows = self._execute_query(
            pattern,
            symbols,
            start_ts,
            end_ts,
            "SELECT ts, seq, symbol, market, price, qty, side",
            "ORDER BY ts, seq",
        )

        for ts, seq, symbol_name, market_str, price, qty, side in rows:
            yield TradeEvent(
                symbol=_symbol_obj(str(symbol_name), str(market_str)),
                ts=int(ts),
                seq=int(seq),
                price=Decimal(str(price)),
                qty=Decimal(str(qty)),
                side=str(side),
            )

    def _execute_query(
        self,
        pattern: str,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
        select_clause: str,
        order_clause: str,
        chunk_size: int = 5000,
    ) -> Iterator[tuple[Any, ...]]:
        """Execute DuckDB query for market data with time filtering.

        Yields rows in chunks to avoid loading full result set into memory.
        hive_partitioning=true enables partition pruning via symbol/date/hour
        path components; WHERE symbol IN (...) is kept for additional filtering.
        """
        symbol_names = [s.name for s in symbols]
        placeholders = ", ".join(f"'{n}'" for n in symbol_names)

        con = duckdb.connect()
        try:
            result = con.execute(
                f"""
                {select_clause}
                FROM read_parquet('{pattern}', hive_partitioning=true)
                WHERE symbol IN ({placeholders})
                  AND ts >= {start_ts}
                  AND ts <= {end_ts}
                {order_clause}
                """
            )
            while True:
                chunk = result.fetchmany(chunk_size)
                if not chunk:
                    break
                yield from chunk
        finally:
            con.close()


def _reconstruct_orderbook_events(
    rows: Iterator[tuple[Any, ...]],
) -> Iterator[OrderBookDiffEvent]:
    """
    같은 (ts, seq, symbol)의 여러 row를 하나의 OrderBookDiffEvent로 묶는다.
    rows는 (ts, seq, symbol, market, side, price, qty) 순서로 정렬되어 있어야 함.
    """
    current: tuple[Any, ...] | None = next(rows, None)
    if current is None:
        return

    while current is not None:
        ts_v, seq_v, symbol_name, market_str, _side, _price, _qty = current
        group_key = (ts_v, seq_v, symbol_name)

        bids: list[tuple[Decimal, Decimal]] = []
        asks: list[tuple[Decimal, Decimal]] = []

        # consume all rows sharing the same (ts, seq, symbol)
        while current is not None:
            r_ts, r_seq, r_sym, r_mkt, r_side, r_price, r_qty = current
            if (r_ts, r_seq, r_sym) != group_key:
                break
            entry = (Decimal(str(r_price)), Decimal(str(r_qty)))
            if r_side == "bid":
                bids.append(entry)
            else:
                asks.append(entry)
            market_str = r_mkt
            current = next(rows, None)

        yield OrderBookDiffEvent(
            symbol=_symbol_obj(str(symbol_name), str(market_str)),
            ts=int(ts_v),
            seq=int(seq_v),
            bids_delta=tuple(bids),
            asks_delta=tuple(asks),
        )


def _merge_sorted(
    a: Iterator[MarketEvent],
    b: Iterator[MarketEvent],
) -> Iterator[MarketEvent]:
    """Merge sort two timestamp-ordered iterators into single stream."""
    a_val: MarketEvent | None = next(a, None)
    b_val: MarketEvent | None = next(b, None)

    while a_val is not None and b_val is not None:
        if a_val.ts <= b_val.ts:
            yield a_val
            a_val = next(a, None)
        else:
            yield b_val
            b_val = next(b, None)

    if a_val is not None:
        yield a_val
        yield from a
    if b_val is not None:
        yield b_val
        yield from b
