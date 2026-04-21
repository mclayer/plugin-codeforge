from __future__ import annotations

from decimal import Decimal

from mctrader.dashboard.data_query import query
from mctrader.dashboard.views.view_models import CVDPoint, TapeEntryView
from mctrader.domain.microstructure import TickDir, classify_tick


def _size_bucket(notional: Decimal, p75: Decimal, p95: Decimal, p99: Decimal) -> str:
    if notional >= p99:
        return "whale"
    if notional >= p95:
        return "large"
    if notional >= p75:
        return "medium"
    return "small"


def _percentile(sorted_vals: list[Decimal], pct: float) -> Decimal:
    if not sorted_vals:
        return Decimal(0)
    idx = int(len(sorted_vals) * pct / 100)
    idx = min(idx, len(sorted_vals) - 1)
    return sorted_vals[idx]


def build_tape(
    data_root: str,
    symbol: str,
    market: str,
    start_ts: int,
    end_ts: int,
    limit: int = 500,
) -> list[TapeEntryView]:
    result = query(data_root, "trade", symbol, start_ts=start_ts, end_ts=end_ts, limit=limit)
    if not result.rows:
        return []

    rows = sorted(result.rows, key=lambda r: (int(r["ts"]), int(r["seq"])))

    notionals = sorted(
        Decimal(str(r["price"])) * Decimal(str(r["qty"])) for r in rows
    )

    if len(notionals) < 2:
        p75 = p95 = p99 = notionals[0] if notionals else Decimal(0)
    else:
        p75 = _percentile(notionals, 75)
        p95 = _percentile(notionals, 95)
        p99 = _percentile(notionals, 99)

    entries: list[TapeEntryView] = []
    prev_price: Decimal | None = None
    prev_dir: TickDir | None = None

    for row in rows:
        price = Decimal(str(row["price"]))
        qty = Decimal(str(row["qty"]))
        notional = price * qty
        side = str(row.get("side", "")).lower()

        tick_dir = classify_tick(price, prev_price, prev_dir)
        prev_price = price
        prev_dir = tick_dir

        bucket = _size_bucket(notional, p75, p95, p99)

        entries.append(
            TapeEntryView(
                ts=int(row["ts"]),
                seq=int(row["seq"]),
                symbol=str(row.get("symbol", symbol)),
                market=str(row.get("market", market)),
                price=str(price),
                qty=str(qty),
                side=side,
                tick_dir=tick_dir,
                size_bucket=bucket,
                notional=str(notional),
            )
        )

    return entries


def build_cvd(
    data_root: str,
    symbol: str,
    market: str,
    start_ts: int,
    end_ts: int,
) -> list[CVDPoint]:
    # TODO: Phase 3 구현 예정
    return []
