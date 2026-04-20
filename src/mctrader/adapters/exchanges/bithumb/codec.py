from __future__ import annotations

import time
from decimal import Decimal

from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol


class OrderBookDiffCalculator:
    def __init__(self) -> None:
        # symbol_name -> {"bids": {price_str: qty_str}, "asks": {price_str: qty_str}}
        self._prev: dict[str, dict[str, dict[str, str]]] = {}

    def compute_diff(
        self,
        symbol_name: str,
        new_bids: dict[str, str],
        new_asks: dict[str, str],
        ts: int,
        seq: int,
        symbol: Symbol,
    ) -> OrderBookDiffEvent:
        prev = self._prev.get(symbol_name)

        if prev is None:
            # first snapshot: treat everything as new
            bids_delta = tuple(
                (Decimal(p), Decimal(q)) for p, q in new_bids.items()
            )
            asks_delta = tuple(
                (Decimal(p), Decimal(q)) for p, q in new_asks.items()
            )
        else:
            bids_delta = _calc_side_diff(prev["bids"], new_bids)
            asks_delta = _calc_side_diff(prev["asks"], new_asks)

        self._prev[symbol_name] = {"bids": dict(new_bids), "asks": dict(new_asks)}

        return OrderBookDiffEvent(
            symbol=symbol,
            ts=ts,
            seq=seq,
            bids_delta=bids_delta,
            asks_delta=asks_delta,
        )


def _calc_side_diff(
    prev: dict[str, str], new: dict[str, str]
) -> tuple[tuple[Decimal, Decimal], ...]:
    delta: list[tuple[Decimal, Decimal]] = []

    for price, qty in new.items():
        if price not in prev or prev[price] != qty:
            delta.append((Decimal(price), Decimal(qty)))

    # levels that disappeared get qty=0 (remove signal)
    for price in prev:
        if price not in new:
            delta.append((Decimal(price), Decimal(0)))

    return tuple(delta)


# module-level calculator instance — one per process; sufficient for single-exchange use
_diff_calc = OrderBookDiffCalculator()


def decode(raw: dict, market: Market = Market.BITHUMB) -> MarketEvent | None:
    msg_type = raw.get("type")
    data = raw.get("data", {})

    if msg_type == "ORDERBOOK":
        symbol_name: str = data["s"]
        base, quote = symbol_name.split("_")
        symbol = Symbol(base=base, quote=quote, market=market)

        seq = int(data["ver"])
        ts = int(time.time_ns() // 1_000_000)

        # raw lists → price→qty dicts (preserving string representation for diff comparison)
        new_bids: dict[str, str] = {row[0]: row[1] for row in data["b"]}
        new_asks: dict[str, str] = {row[0]: row[1] for row in data["a"]}

        return _diff_calc.compute_diff(symbol_name, new_bids, new_asks, ts, seq, symbol)

    if msg_type == "TRADE":
        symbol_name = data["s"]
        base, quote = symbol_name.split("_")
        symbol = Symbol(base=base, quote=quote, market=market)

        return TradeEvent(
            symbol=symbol,
            ts=int(data["t"]),
            seq=int(data["t"]),  # bithumb trade has no separate seq; use timestamp
            price=Decimal(data["p"]),
            qty=Decimal(data["v"]),
            side=data["side"],
        )

    return None
