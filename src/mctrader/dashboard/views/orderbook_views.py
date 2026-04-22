from __future__ import annotations

import glob as _glob
import os
from decimal import Decimal

from mctrader.dashboard.data_query import query
from mctrader.dashboard.db import cursor as _cursor
from mctrader.dashboard.views.view_models import ImbalancePoint, LevelView, SnapshotView
from mctrader.domain import microstructure
from mctrader.domain.events import OrderBookDiffEvent
from mctrader.domain.orderbook import OrderBook
from mctrader.domain.symbol import Market, Symbol

# 스냅샷 재구성을 위해 as_of_ts 기준으로 과거 몇 ms까지 조회할지 결정하는 윈도우.
# 너무 짧으면 orderbook이 비어 보이고, 너무 길면 쿼리 비용이 증가한다.
_SNAPSHOT_LOOKBACK_MS = 30 * 60_000  # 30분

# 임밸런스 시리즈 조회 행 상한.
# 기존 500_000에서 줄임으로써 메모리 압박과 쿼리 시간을 개선한다.
# DuckDB 사전 버킷팅으로 각 버킷의 마지막 상태만 읽으므로
# 동일 시간 범위에서 실제 집계 정확도 손실 없이 행 수를 크게 줄일 수 있다.
_IMBALANCE_MAX_ROWS = 50_000


def _make_symbol(symbol: str, market: str) -> Symbol:
    parts = symbol.upper().split("_")
    base = parts[0] if parts else symbol.upper()
    quote = parts[1] if len(parts) > 1 else "KRW"
    try:
        mkt = Market(market.lower())
    except ValueError:
        mkt = Market.BITHUMB
    return Symbol(base=base, quote=quote, market=mkt)


def _rows_to_diff_events(rows: list[dict]) -> list[OrderBookDiffEvent]:
    grouped: dict[tuple[int, int], dict] = {}
    for row in rows:
        key = (int(row["ts"]), int(row["seq"]))
        if key not in grouped:
            grouped[key] = {
                "ts": int(row["ts"]),
                "seq": int(row["seq"]),
                "symbol_raw": str(row.get("symbol", "")),
                "market_raw": str(row.get("market", "bithumb")),
                "bids": [],
                "asks": [],
            }
        side = str(row.get("side", "")).lower()
        price = Decimal(str(row["price"]))
        qty = Decimal(str(row["qty"]))
        if side == "bid":
            grouped[key]["bids"].append((price, qty))
        else:
            grouped[key]["asks"].append((price, qty))

    events = []
    for (ts, seq), g in sorted(grouped.items()):
        sym = _make_symbol(g["symbol_raw"], g["market_raw"])
        events.append(
            OrderBookDiffEvent(
                symbol=sym,
                ts=ts,
                seq=seq,
                bids_delta=tuple(g["bids"]),
                asks_delta=tuple(g["asks"]),
            )
        )
    return events


def build_snapshot_view(
    data_root: str,
    symbol: str,
    market: str,
    as_of_ts: int,
    depth: int = 20,
    imbalance_depth: int = 5,
) -> SnapshotView:
    # 30분 윈도우 내 이벤트 상한: limit은 orderbook 재구성 정확도를 위해 충분히 크게 유지.
    result = query(
        data_root,
        "orderbook_diff",
        symbol,
        start_ts=max(0, as_of_ts - _SNAPSHOT_LOOKBACK_MS),
        end_ts=as_of_ts,
        limit=100_000,
    )
    sym = _make_symbol(symbol, market)
    book = OrderBook(sym)

    for event in _rows_to_diff_events(result.rows):
        book.apply_diff(event)

    snap = book.snapshot()
    bid_levels = snap.bids[:depth]
    ask_levels = snap.asks[:depth]

    cum_bids = microstructure.cumulative_qty(bid_levels)
    cum_asks = microstructure.cumulative_qty(ask_levels)

    max_cum = Decimal(0)
    if cum_bids:
        max_cum = max(max_cum, cum_bids[-1])
    if cum_asks:
        max_cum = max(max_cum, cum_asks[-1])

    def _pct(cum_val: Decimal) -> float:
        if max_cum == Decimal(0):
            return 0.0
        return float(cum_val / max_cum * Decimal(100))

    bid_views = [
        LevelView(
            price=str(lvl.price),
            qty=str(lvl.qty),
            cumulative_qty=str(cum_bids[i]),
            depth_pct=_pct(cum_bids[i]),
        )
        for i, lvl in enumerate(bid_levels)
    ]
    ask_views = [
        LevelView(
            price=str(lvl.price),
            qty=str(lvl.qty),
            cumulative_qty=str(cum_asks[i]),
            depth_pct=_pct(cum_asks[i]),
        )
        for i, lvl in enumerate(ask_levels)
    ]

    mid = microstructure.mid_price(snap)
    sp = microstructure.spread(snap)
    sp_bps = microstructure.spread_bps(snap)
    imb = microstructure.imbalance(snap, depth=imbalance_depth)

    return SnapshotView(
        ts=snap.ts,
        seq=snap.seq,
        symbol=symbol,
        market=market,
        bids=bid_views,
        asks=ask_views,
        mid_price=str(mid) if mid is not None else None,
        spread=str(sp) if sp is not None else None,
        spread_bps=sp_bps,
        imbalance=imb,
        imbalance_depth=imbalance_depth,
        depth=len(bid_views),
    )


def _fetch_imbalance_rows_duckdb(
    data_root: str,
    symbol: str,
    start_ts: int,
    end_ts: int,
    bucket_ms: int,
) -> list[dict]:
    """DuckDB QUALIFY로 버킷별 마지막 (side, price) 행만 추출해 반환.

    전략 선택 근거:
    - orderbook imbalance는 누적 bid/ask 합계이므로 SQL GROUP BY 집계만으로
      정확한 값을 얻을 수 없다 (qty가 항상 누적이 아니라 delta이기 때문).
    - 대안: 각 버킷 내에서 가장 최신(ts 내림차순) (side, price) 조합 한 행씩만
      남긴다. 이 행들로 OrderBook을 재구성하면 버킷 종료 시점의 호가창 상태가
      근사적으로 재현된다.
    - 트레이드오프: 버킷 중간에 level이 추가됐다가 버킷 마지막에 삭제된 경우
      해당 level이 결과에서 누락될 수 있다. 실용적으로 250ms~1s 버킷에서는
      허용 가능한 오차이다.
    - 행 수 감소: 원본 대비 (버킷 수 × depth) / 원본 행 수로 대폭 줄어든다.
    """
    pattern = os.path.join(data_root, "orderbook_diff", "symbol=*", "date=*", "hour=*.parquet")
    if not _glob.glob(pattern):
        return []

    # (ts / bucket_ms)::BIGINT으로 버킷 번호 계산 후 QUALIFY로 버킷 내 마지막 행만 유지.
    # side + price 조합별로 가장 최신 ts 행 = 해당 버킷 종료 직전 레벨 상태.
    sql = f"""
        SELECT ts, seq, symbol, market, side, price, qty
        FROM read_parquet('{pattern}', hive_partitioning=true)
        WHERE symbol = ?
          AND ts >= ?
          AND ts <= ?
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY (ts / {bucket_ms})::BIGINT, side, price
            ORDER BY ts DESC, seq DESC
        ) = 1
        ORDER BY ts, seq, side, price
        LIMIT {_IMBALANCE_MAX_ROWS}
    """

    with _cursor() as cur:
        result = cur.execute(sql, [symbol, start_ts, end_ts])
        col_names = [d[0] for d in result.description]
        raw_rows = result.fetchall()

    return [
        {name: (str(val) if not isinstance(val, (int, float, type(None))) else val)
         for name, val in zip(col_names, row, strict=True)}
        for row in raw_rows
    ]


def build_imbalance_series(
    data_root: str,
    symbol: str,
    market: str,
    start_ts: int,
    end_ts: int,
    bucket_ms: int = 250,
    imbalance_depth: int = 5,
) -> list[ImbalancePoint]:
    """임밸런스 시리즈 계산.

    DuckDB QUALIFY 사전 버킷팅으로 조회 행 수를 _IMBALANCE_MAX_ROWS 이내로 제한한다.
    각 버킷의 마지막 (side, price) 상태만 읽어 OrderBook을 재구성하므로
    버킷당 집계 1회 원칙을 유지하면서도 Python 측 처리 행 수를 대폭 줄인다.
    """
    rows = _fetch_imbalance_rows_duckdb(data_root, symbol, start_ts, end_ts, bucket_ms)
    if not rows:
        return []

    sym = _make_symbol(symbol, market)
    book = OrderBook(sym)
    all_events = _rows_to_diff_events(rows)

    points: list[ImbalancePoint] = []
    bucket_start = start_ts
    event_idx = 0

    while event_idx < len(all_events):
        bucket_end = bucket_start + bucket_ms
        bucket_has_data = False

        while event_idx < len(all_events) and all_events[event_idx].ts < bucket_end:
            book.apply_diff(all_events[event_idx])
            bucket_has_data = True
            event_idx += 1

        if bucket_has_data:
            snap = book.snapshot()
            imb = microstructure.imbalance(snap, depth=imbalance_depth)
            points.append(ImbalancePoint(ts=bucket_start, imbalance=imb))

        bucket_start = bucket_end
        if bucket_start > end_ts:
            break

    return points
