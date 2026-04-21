from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mctrader.domain.order import Fill, OrderSide
from mctrader.domain.symbol import Symbol


@dataclass
class Position:
    symbol: Symbol
    qty: Decimal
    avg_price: Decimal
    realized_pnl: Decimal


class Portfolio:
    def __init__(self, initial_cash: Decimal) -> None:
        self._cash: Decimal = initial_cash
        self._positions: dict[Symbol, Position] = {}

    @property
    def cash(self) -> Decimal:
        return self._cash

    def position(self, symbol: Symbol) -> Position | None:
        return self._positions.get(symbol)

    def all_positions(self) -> dict[Symbol, Position]:
        return dict(self._positions)

    def apply_fill(self, fill: Fill) -> None:
        pos = self._positions.get(fill.symbol)

        if fill.side == OrderSide.BUY:
            cost = fill.price * fill.qty + fill.fee
            self._cash -= cost

            if pos is None:
                self._positions[fill.symbol] = Position(
                    symbol=fill.symbol,
                    qty=fill.qty,
                    avg_price=fill.price,
                    realized_pnl=Decimal(0),
                )
            else:
                total_cost = pos.avg_price * pos.qty + fill.price * fill.qty
                new_qty = pos.qty + fill.qty
                pos.avg_price = total_cost / new_qty
                pos.qty = new_qty

        elif fill.side == OrderSide.SELL:
            proceeds = fill.price * fill.qty - fill.fee
            self._cash += proceeds

            if pos is not None:
                # realized pnl = (sell_price - avg_price) * qty
                realized = (fill.price - pos.avg_price) * fill.qty
                pos.realized_pnl += realized
                pos.qty -= fill.qty

                if pos.qty <= Decimal(0):
                    # position fully closed; retain for pnl record but zero qty
                    pos.qty = Decimal(0)
                    pos.avg_price = Decimal(0)

    def unrealized_pnl(self, symbol: Symbol, current_price: Decimal) -> Decimal:
        pos = self._positions.get(symbol)
        if pos is None or pos.qty == Decimal(0):
            return Decimal(0)
        return (current_price - pos.avg_price) * pos.qty

    def total_equity(self, prices: dict[Symbol, Decimal]) -> Decimal:
        equity = self._cash
        for symbol, pos in self._positions.items():
            if pos.qty > Decimal(0):
                current_price = prices.get(symbol, pos.avg_price)
                equity += current_price * pos.qty
        return equity
