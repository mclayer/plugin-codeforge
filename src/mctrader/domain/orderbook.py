from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

from mctrader.domain.events import OrderBookDiffEvent
from mctrader.domain.symbol import Symbol


@dataclass
class Level:
    price: Decimal
    qty: Decimal


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: Symbol
    ts: int
    seq: int
    bids: tuple[Level, ...]  # descending
    asks: tuple[Level, ...]  # ascending


class OrderBook:
    def __init__(self, symbol: Symbol) -> None:
        self._symbol = symbol
        self._bids: Dict[Decimal, Decimal] = {}  # price -> qty
        self._asks: Dict[Decimal, Decimal] = {}
        self._ts: int = 0
        self._seq: int = 0

    def apply_diff(self, event: OrderBookDiffEvent) -> None:
        self._ts = event.ts
        self._seq = event.seq

        for price, qty in event.bids_delta:
            if qty == Decimal(0):
                self._bids.pop(price, None)
            else:
                self._bids[price] = qty

        for price, qty in event.asks_delta:
            if qty == Decimal(0):
                self._asks.pop(price, None)
            else:
                self._asks[price] = qty

    def snapshot(self) -> OrderBookSnapshot:
        sorted_bids = tuple(
            Level(p, q)
            for p, q in sorted(self._bids.items(), reverse=True)
        )
        sorted_asks = tuple(
            Level(p, q)
            for p, q in sorted(self._asks.items())
        )
        return OrderBookSnapshot(
            symbol=self._symbol,
            ts=self._ts,
            seq=self._seq,
            bids=sorted_bids,
            asks=sorted_asks,
        )

    @property
    def best_bid(self) -> Optional[Level]:
        if not self._bids:
            return None
        price = max(self._bids)
        return Level(price, self._bids[price])

    @property
    def best_ask(self) -> Optional[Level]:
        if not self._asks:
            return None
        price = min(self._asks)
        return Level(price, self._asks[price])

    @property
    def mid(self) -> Optional[Decimal]:
        bb = self.best_bid
        ba = self.best_ask
        if bb is None or ba is None:
            return None
        return (bb.price + ba.price) / Decimal(2)

    @property
    def spread(self) -> Optional[Decimal]:
        bb = self.best_bid
        ba = self.best_ask
        if bb is None or ba is None:
            return None
        return ba.price - bb.price
