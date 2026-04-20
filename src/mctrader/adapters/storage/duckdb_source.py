from __future__ import annotations

import glob as _glob
import os
from decimal import Decimal
from typing import Iterator

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
                symbol=_symbol_obj(symbol_name, market_str),
                ts=ts,
                seq=seq,
                price=Decimal(price),
                qty=Decimal(qty),
                side=side,
            )

    def _execute_query(
        self,
        pattern: str,
        symbols: list[Symbol],
        start_ts: int,
        end_ts: int,
        select_clause: str,
        order_clause: str,
    ) -> list[tuple]:
        """Execute DuckDB query for market data with time filtering."""
        symbol_names = [s.name for s in symbols]
        placeholders = ", ".join(f"'{n}'" for n in symbol_names)

        con = duckdb.connect()
        try:
            return con.execute(
                f"""
                {select_clause}
                FROM read_parquet('{pattern}', hive_partitioning=false)
                WHERE symbol IN ({placeholders})
                  AND ts >= {start_ts}
                  AND ts <= {end_ts}
                {order_clause}
                """
            ).fetchall()
        finally:
            con.close()


def _reconstruct_orderbook_events(
    rows: list[tuple],
) -> Iterator[OrderBookDiffEvent]:
    """
    같은 (ts, seq, symbol)의 여러 row를 하나의 OrderBookDiffEvent로 묶는다.
    rows는 (ts, seq, symbol, market, side, price, qty) 순서로 정렬되어 있어야 함.
    """
    i = 0
    while i < len(rows):
        ts, seq, symbol_name, market_str, side, price, qty = rows[i]
        group_key = (ts, seq, symbol_name)

        bids: list[tuple[Decimal, Decimal]] = []
        asks: list[tuple[Decimal, Decimal]] = []

        # consume all rows sharing the same (ts, seq, symbol)
        while i < len(rows):
            r_ts, r_seq, r_sym, r_mkt, r_side, r_price, r_qty = rows[i]
            if (r_ts, r_seq, r_sym) != group_key:
                break
            entry = (Decimal(r_price), Decimal(r_qty))
            if r_side == "bid":
                bids.append(entry)
            else:
                asks.append(entry)
            market_str = r_mkt
            i += 1

        yield OrderBookDiffEvent(
            symbol=_symbol_obj(symbol_name, market_str),
            ts=ts,
            seq=seq,
            bids_delta=tuple(bids),
            asks_delta=tuple(asks),
        )


def _merge_sorted(
    a: Iterator[MarketEvent],
    b: Iterator[MarketEvent],
) -> Iterator[MarketEvent]:
    """Merge sort two timestamp-ordered iterators into single stream."""
    sentinel = object()
    a_val = next(a, sentinel)  # type: ignore[call-overload]
    b_val = next(b, sentinel)  # type: ignore[call-overload]

    while a_val is not sentinel and b_val is not sentinel:
        if a_val.ts <= b_val.ts:  # type: ignore[union-attr]
            yield a_val  # type: ignore[misc]
            a_val = next(a, sentinel)  # type: ignore[call-overload]
        else:
            yield b_val  # type: ignore[misc]
            b_val = next(b, sentinel)  # type: ignore[call-overload]

    if a_val is not sentinel:
        yield a_val  # type: ignore[misc]
        yield from a
    if b_val is not sentinel:
        yield b_val  # type: ignore[misc]
        yield from b
