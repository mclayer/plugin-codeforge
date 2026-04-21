from __future__ import annotations

from decimal import Decimal
from typing import Literal

from mctrader.domain.orderbook import Level, OrderBookSnapshot

TickDir = Literal["UP", "DOWN", "ZERO_UP", "ZERO_DOWN"]


def imbalance(snapshot: OrderBookSnapshot, depth: int = 5) -> float:
    bid_qty = sum(lvl.qty for lvl in snapshot.bids[:depth])
    ask_qty = sum(lvl.qty for lvl in snapshot.asks[:depth])
    total = bid_qty + ask_qty
    if total == Decimal(0):
        return 0.0
    return float((bid_qty - ask_qty) / total)


def mid_price(snapshot: OrderBookSnapshot) -> Decimal | None:
    if not snapshot.bids or not snapshot.asks:
        return None
    return (snapshot.bids[0].price + snapshot.asks[0].price) / Decimal(2)


def spread(snapshot: OrderBookSnapshot) -> Decimal | None:
    if not snapshot.bids or not snapshot.asks:
        return None
    return snapshot.asks[0].price - snapshot.bids[0].price


def spread_bps(snapshot: OrderBookSnapshot) -> float | None:
    mid = mid_price(snapshot)
    if mid is None or mid == Decimal(0):
        return None
    s = spread(snapshot)
    if s is None:
        return None
    return float(s / mid * Decimal(10_000))


def cumulative_qty(levels: tuple[Level, ...]) -> list[Decimal]:
    result: list[Decimal] = []
    running = Decimal(0)
    for lvl in levels:
        running += lvl.qty
        result.append(running)
    return result


def classify_tick(
    price: Decimal,
    prev_price: Decimal | None,
    prev_dir: TickDir | None,
) -> TickDir:
    if prev_price is None:
        return "UP"
    if price > prev_price:
        return "UP"
    if price < prev_price:
        return "DOWN"
    # price == prev_price
    if prev_dir in ("UP", "ZERO_UP"):
        return "ZERO_UP"
    return "ZERO_DOWN"


def trade_delta(side: Literal["buy", "sell"], qty: Decimal) -> Decimal:
    if side == "buy":
        return qty
    if side == "sell":
        return -qty
    return Decimal(0)
