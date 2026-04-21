from __future__ import annotations

from decimal import Decimal
from typing import Any

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


def _from_exchange_code(code: str, market: Market) -> Symbol:
    """KRW-BTC -> Symbol(base=BTC, quote=KRW)"""
    quote, base = code.split("-")
    return Symbol(base=base, quote=quote, market=market)


def decode(
    raw: dict[str, object],
    diff_calc: OrderBookDiffCalculator,
    market: Market = Market.BITHUMB,
) -> MarketEvent | None:
    msg_type = raw.get("type")

    if msg_type == "orderbook":
        code = str(raw["code"])
        symbol = _from_exchange_code(code, market)
        ts = int(raw["timestamp"]) // 1000  # microseconds → milliseconds
        seq = ts
        units: Any = raw["orderbook_units"]
        new_bids: dict[str, str] = {
            str(unit["bid_price"]): str(unit["bid_size"]) for unit in units
        }
        new_asks: dict[str, str] = {
            str(unit["ask_price"]): str(unit["ask_size"]) for unit in units
        }
        return diff_calc.compute_diff(symbol.name, new_bids, new_asks, ts, seq, symbol)

    if msg_type == "trade":
        code = str(raw["code"])
        symbol = _from_exchange_code(code, market)
        ask_bid = str(raw["ask_bid"])
        side = "buy" if ask_bid == "BID" else "sell"
        return TradeEvent(
            symbol=symbol,
            ts=int(raw["trade_timestamp"]),  # type: ignore[arg-type]
            seq=int(raw.get("sequential_id", raw["trade_timestamp"])),  # type: ignore[arg-type]
            price=Decimal(str(raw["trade_price"])),
            qty=Decimal(str(raw["trade_volume"])),
            side=side,
        )

    return None
