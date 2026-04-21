from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LevelView:
    price: str
    qty: str
    cumulative_qty: str
    depth_pct: float


@dataclass(frozen=True)
class SnapshotView:
    ts: int
    seq: int
    symbol: str
    market: str
    bids: list[LevelView]
    asks: list[LevelView]
    mid_price: str | None
    spread: str | None
    spread_bps: float | None
    imbalance: float
    imbalance_depth: int
    depth: int


@dataclass(frozen=True)
class ImbalancePoint:
    ts: int
    imbalance: float


@dataclass(frozen=True)
class TapeEntryView:
    ts: int
    seq: int
    symbol: str
    market: str
    price: str
    qty: str
    side: str
    tick_dir: str
    size_bucket: str
    notional: str


@dataclass(frozen=True)
class CVDPoint:
    ts: int
    cvd: str
