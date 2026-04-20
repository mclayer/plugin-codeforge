from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mctrader.domain.symbol import Symbol


@dataclass(frozen=True)
class OrderBookDiffEvent:
    symbol: Symbol
    ts: int
    seq: int
    bids_delta: tuple[tuple[Decimal, Decimal], ...]  # (price, qty), qty=0 means remove
    asks_delta: tuple[tuple[Decimal, Decimal], ...]


@dataclass(frozen=True)
class TradeEvent:
    symbol: Symbol
    ts: int
    seq: int
    price: Decimal
    qty: Decimal
    side: str  # "buy" | "sell"


@dataclass(frozen=True)
class ClockTickEvent:
    ts: int


MarketEvent = Union[OrderBookDiffEvent, TradeEvent, ClockTickEvent]
