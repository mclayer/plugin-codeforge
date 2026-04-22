"""DuckDB 프로세스 싱글톤 연결 모듈.

FastAPI lifespan에서 초기화/정리되는 read-only 연결을 제공한다.
`con.cursor()`는 DuckDB 내부 락으로 thread-safe하므로 요청마다 cursor를 파생해
사용하면 안전하다.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator

import duckdb

_lock = threading.Lock()
_connection: duckdb.DuckDBPyConnection | None = None


def init_duckdb() -> None:
    """FastAPI lifespan startup에서 호출. 프로세스-싱글톤 in-memory 연결을 초기화."""
    global _connection
    with _lock:
        if _connection is None:
            # read_only=False: in-memory 연결은 read_only 불필요.
            # Parquet 조회는 read_parquet()로 수행하므로 DB 파일 없음.
            _connection = duckdb.connect()


def close_duckdb() -> None:
    """FastAPI lifespan shutdown에서 호출."""
    global _connection
    with _lock:
        if _connection is not None:
            _connection.close()
            _connection = None


def get_duckdb() -> duckdb.DuckDBPyConnection:
    """싱글톤 연결 반환. lifespan 초기화 전에 호출하면 RuntimeError."""
    if _connection is None:
        raise RuntimeError(
            "DuckDB connection is not initialised. "
            "Call init_duckdb() before get_duckdb()."
        )
    return _connection


@contextmanager
def cursor() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """싱글톤 연결에서 cursor를 파생해 컨텍스트 매니저로 제공.

    요청마다 독립된 cursor를 사용하므로 동시 요청에서도 안전하다.
    cursor는 별도로 close()하지 않아도 GC가 처리하지만,
    with 블록 종료 시 명시적으로 close한다.
    """
    con = get_duckdb()
    cur = con.cursor()
    try:
        yield cur
    finally:
        cur.close()
