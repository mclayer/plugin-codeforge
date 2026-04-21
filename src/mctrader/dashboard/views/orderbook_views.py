from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from mctrader.dashboard.data_query import query
from mctrader.dashboard.views.view_models import ImbalancePoint, LevelView, SnapshotView
from mctrader.domain import microstructure
from mctrader.domain.events import OrderBookDiffEvent
from mctrader.domain.orderbook import OrderBook
from mctrader.domain.symbol import Market, Symbol


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
    result = query(data_root, "orderbook_diff", symbol, start_ts=0, end_ts=as_of_ts, limit=100_000)
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


def build_imbalance_series(
    data_root: str,
    symbol: str,
    market: str,
    start_ts: int,
    end_ts: int,
    bucket_ms: int = 250,
    imbalance_depth: int = 5,
) -> list[ImbalancePoint]:
    result = query(data_root, "orderbook_diff", symbol, start_ts=start_ts, end_ts=end_ts, limit=500_000)
    if not result.rows:
        return []

    rows = sorted(result.rows, key=lambda r: (int(r["ts"]), int(r["seq"])))
    sym = _make_symbol(symbol, market)
    book = OrderBook(sym)

    points: list[ImbalancePoint] = []
    bucket_start = start_ts
    row_idx = 0
    all_events = _rows_to_diff_events(rows)

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
