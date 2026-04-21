"""Collector 프로세스 상태 및 Parquet 수집 통계 조회.

대시보드 /collector 페이지용. Hexagonal 관점에서 UI 어댑터 계층에 속하며,
domain/ports 를 수정하지 않고 파일시스템과 `ps` 명령만 사용한다.
"""

from __future__ import annotations

import glob as _glob
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

import duckdb  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CollectorProcessInfo:
    running: bool
    pid: int | None
    cmdline: str | None
    detection: str  # "ps" | "unknown"


@dataclass(frozen=True)
class SymbolStats:
    symbol: str
    orderbook_row_count: int  # note: side 당 1 row 이므로 level 수만큼 증폭됨
    trade_count: int
    last_orderbook_ts: int | None
    last_trade_ts: int | None

    @property
    def last_received_ts(self) -> int | None:
        candidates = [v for v in (self.last_orderbook_ts, self.last_trade_ts) if v is not None]
        return max(candidates) if candidates else None


@dataclass(frozen=True)
class ParquetFileInfo:
    event_type: str
    symbol: str
    date: str
    hour: str
    file_name: str
    rel_path: str
    size_bytes: int
    mtime_ts: float


@dataclass(frozen=True)
class CollectorStatus:
    process: CollectorProcessInfo
    symbols: list[SymbolStats]
    today_files: list[ParquetFileInfo]
    data_root: str
    today: str
    event_types: tuple[str, ...] = field(default_factory=lambda: ("orderbook_diff", "trade"))


# ---------------------------------------------------------------------------
# Process detection
# ---------------------------------------------------------------------------

def detect_collector_process() -> CollectorProcessInfo:
    """`ps` 명령으로 collector 프로세스를 찾는다.

    ADR-008(Linux + systemd) 기준으로 Linux/macOS 에서 동작하도록 `ps` 를 사용.
    실패 시 unknown 상태를 반환해 대시보드가 죽지 않게 한다.
    """
    try:
        output = subprocess.check_output(
            ["ps", "-axo", "pid,command"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return CollectorProcessInfo(running=False, pid=None, cmdline=None, detection="unknown")

    for line in output.splitlines()[1:]:
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(None, 1)
        if len(parts) < 2:
            continue
        pid_s, cmd = parts
        if _looks_like_collector(cmd):
            try:
                pid = int(pid_s)
            except ValueError:
                continue
            return CollectorProcessInfo(running=True, pid=pid, cmdline=cmd, detection="ps")

    return CollectorProcessInfo(running=False, pid=None, cmdline=None, detection="ps")


def _looks_like_collector(cmd: str) -> bool:
    """Collector 프로세스 판별. CLI 엔트리포인트 및 collector_service 모두 감지."""
    needles = ("mctrader-collector", "mctrader.app.collector_service", "run_collector")
    return any(needle in cmd for needle in needles)


# ---------------------------------------------------------------------------
# Symbol discovery
# ---------------------------------------------------------------------------

def discover_symbols(data_root: str) -> list[str]:
    """data_root 하위의 Parquet 파티션에서 심볼 목록을 추출해 정렬 반환."""
    names: set[str] = set()
    for event_type in ("orderbook_diff", "trade"):
        base = os.path.join(data_root, event_type)
        if not os.path.isdir(base):
            continue
        for entry in os.listdir(base):
            if entry.startswith("symbol="):
                names.add(entry[len("symbol="):])
    return sorted(names)


# ---------------------------------------------------------------------------
# Aggregate stats via DuckDB
# ---------------------------------------------------------------------------

def aggregate_symbol_stats(data_root: str) -> list[SymbolStats]:
    """DuckDB 로 심볼별 row count + 최신 ts 를 한 쿼리로 집계."""
    ob_stats = _aggregate_one(data_root, "orderbook_diff")
    trade_stats = _aggregate_one(data_root, "trade")

    symbols = sorted(set(ob_stats.keys()) | set(trade_stats.keys()))
    result: list[SymbolStats] = []
    for sym in symbols:
        ob = ob_stats.get(sym)
        tr = trade_stats.get(sym)
        result.append(
            SymbolStats(
                symbol=sym,
                orderbook_row_count=ob[0] if ob else 0,
                trade_count=tr[0] if tr else 0,
                last_orderbook_ts=ob[1] if ob else None,
                last_trade_ts=tr[1] if tr else None,
            )
        )
    return result


def _aggregate_one(data_root: str, event_type: str) -> dict[str, tuple[int, int | None]]:
    """Return {symbol: (count, max_ts)} for a single event type."""
    pattern = os.path.join(
        data_root, event_type, "symbol=*", "date=*", "hour=*.parquet"
    )
    if not _glob.glob(pattern):
        return {}

    con = duckdb.connect()
    try:
        rows = con.execute(
            f"""
            SELECT symbol, COUNT(*) AS cnt, MAX(ts) AS max_ts
            FROM read_parquet('{pattern}', hive_partitioning=true)
            GROUP BY symbol
            """
        ).fetchall()
    finally:
        con.close()

    return {
        str(sym): (int(cnt), int(max_ts) if max_ts is not None else None)
        for sym, cnt, max_ts in rows
    }


# ---------------------------------------------------------------------------
# Today's files
# ---------------------------------------------------------------------------

def list_today_files(data_root: str, today_utc: str | None = None) -> list[ParquetFileInfo]:
    """오늘(UTC) 디렉토리의 Parquet 파일 목록을 수집.

    파티션 구조: {root}/{event_type}/symbol=X/date=YYYY-MM-DD/hour=HH_*.parquet
    """
    today = today_utc or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out: list[ParquetFileInfo] = []

    for event_type in ("orderbook_diff", "trade"):
        base = os.path.join(data_root, event_type)
        if not os.path.isdir(base):
            continue
        for symbol_dir in sorted(os.listdir(base)):
            if not symbol_dir.startswith("symbol="):
                continue
            symbol = symbol_dir[len("symbol="):]
            date_path = os.path.join(base, symbol_dir, f"date={today}")
            if not os.path.isdir(date_path):
                continue
            for name in sorted(os.listdir(date_path)):
                if not name.endswith(".parquet"):
                    continue
                hour = _extract_hour(name)
                full = os.path.join(date_path, name)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                out.append(
                    ParquetFileInfo(
                        event_type=event_type,
                        symbol=symbol,
                        date=today,
                        hour=hour,
                        file_name=name,
                        rel_path=os.path.relpath(full, data_root),
                        size_bytes=st.st_size,
                        mtime_ts=st.st_mtime,
                    )
                )

    # 최신 수정 파일 먼저
    out.sort(key=lambda f: f.mtime_ts, reverse=True)
    return out


def _extract_hour(parquet_name: str) -> str:
    """`hour=01_1776734786508.parquet` -> "01" """
    if parquet_name.startswith("hour="):
        rest = parquet_name[len("hour="):]
        return rest.split("_", 1)[0]
    return "?"


# ---------------------------------------------------------------------------
# Facade
# ---------------------------------------------------------------------------

def build_collector_status(data_root: str) -> CollectorStatus:
    """대시보드가 호출하는 단일 진입점."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return CollectorStatus(
        process=detect_collector_process(),
        symbols=aggregate_symbol_stats(data_root),
        today_files=list_today_files(data_root, today),
        data_root=data_root,
        today=today,
    )
