"""/data 페이지용 DuckDB Parquet 조회 어댑터.

adapters/storage/duckdb_source.py 는 MarketEvent 스트리밍 목적으로 이벤트 재구성(
bid/ask row 묶기)까지 수행한다. 대시보드는 raw row 단위 표시가 필요하므로
별도 얇은 쿼리 함수를 제공한다. hive_partitioning=true 로 파티션 가지치기를 활용.
"""

from __future__ import annotations

import glob as _glob
import os
from dataclasses import dataclass
from typing import Any, Literal

import duckdb

DataType = Literal["orderbook_diff", "trade"]

# 대시보드에 표시되는 최대 행. 쿼리 자체에 LIMIT 을 걸어 메모리 사용을 제한.
MAX_ROWS = 200


@dataclass(frozen=True)
class QueryResult:
    rows: list[dict[str, Any]]
    total_count: int
    returned_count: int
    truncated: bool


def query(
    data_root: str,
    event_type: DataType,
    symbol: str,
    start_ts: int,
    end_ts: int,
    limit: int = MAX_ROWS,
) -> QueryResult:
    """심볼/기간 기준 Parquet 를 조회. 최대 limit 행만 반환."""
    pattern = os.path.join(
        data_root, event_type, "symbol=*", "date=*", "hour=*.parquet"
    )
    if not _glob.glob(pattern):
        return QueryResult(rows=[], total_count=0, returned_count=0, truncated=False)

    con = duckdb.connect()
    try:
        total = _count(con, pattern, symbol, start_ts, end_ts)
        if total == 0:
            return QueryResult(rows=[], total_count=0, returned_count=0, truncated=False)

        cols = _select_columns(event_type)
        order = "ORDER BY ts, seq" + (", side, price" if event_type == "orderbook_diff" else "")
        sql = f"""
            SELECT {cols}
            FROM read_parquet('{pattern}', hive_partitioning=true)
            WHERE symbol = ?
              AND ts >= ?
              AND ts <= ?
            {order}
            LIMIT {int(limit)}
        """
        result = con.execute(sql, [symbol, start_ts, end_ts])
        column_names = [d[0] for d in result.description]
        rows_raw = result.fetchall()
    finally:
        con.close()

    rows = [
        {name: _serialize(value) for name, value in zip(column_names, row, strict=True)}
        for row in rows_raw
    ]
    return QueryResult(
        rows=rows,
        total_count=total,
        returned_count=len(rows),
        truncated=total > len(rows),
    )


def _count(
    con: duckdb.DuckDBPyConnection,
    pattern: str,
    symbol: str,
    start_ts: int,
    end_ts: int,
) -> int:
    sql = f"""
        SELECT COUNT(*)
        FROM read_parquet('{pattern}', hive_partitioning=true)
        WHERE symbol = ?
          AND ts >= ?
          AND ts <= ?
    """
    row = con.execute(sql, [symbol, start_ts, end_ts]).fetchone()
    return int(row[0]) if row else 0


def _select_columns(event_type: DataType) -> str:
    if event_type == "orderbook_diff":
        return "ts, seq, symbol, market, side, price, qty"
    return "ts, seq, symbol, market, price, qty, side"


def _serialize(value: Any) -> Any:
    """DuckDB 반환 값을 JSON/Jinja 에서 다루기 쉬운 원시 타입으로 변환."""
    if value is None:
        return None
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)
