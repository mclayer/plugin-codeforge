"""Unit tests for Portfolio domain logic."""
from __future__ import annotations

from decimal import Decimal

from mctrader.domain.order import Fill, OrderSide
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.symbol import Market, Symbol

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)
INITIAL_CASH = Decimal("1_000_000")


def _fill(
    side: OrderSide,
    price: str,
    qty: str,
    fee: str = "0",
    order_id: str = "oid1",
) -> Fill:
    return Fill(
        order_id=order_id,
        symbol=SYMBOL,
        side=side,
        price=Decimal(price),
        qty=Decimal(qty),
        fee=Decimal(fee),
        ts=1_000,
    )


class TestPortfolioApplyFill:
    def test_buy_fill_decreases_cash(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1"))

        # cost = 50000 * 1 + 0 fee
        assert portfolio.cash == INITIAL_CASH - Decimal("50000")

    def test_buy_fill_includes_fee_in_cash_deduction(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", fee="100"))

        assert portfolio.cash == INITIAL_CASH - Decimal("50100")

    def test_buy_fill_creates_position(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="2"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.qty == Decimal("2")
        assert pos.avg_price == Decimal("50000")

    def test_additional_buy_updates_weighted_avg_price(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        # first buy: 1 BTC @ 50000
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", order_id="a"))
        # second buy: 1 BTC @ 60000  →  avg = (50000 + 60000) / 2 = 55000
        portfolio.apply_fill(_fill(OrderSide.BUY, price="60000", qty="1", order_id="b"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.qty == Decimal("2")
        assert pos.avg_price == Decimal("55000")

    def test_additional_buy_unequal_qty_weighted_avg(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        # 2 BTC @ 40000  +  1 BTC @ 70000  →  avg = (80000+70000)/3
        portfolio.apply_fill(_fill(OrderSide.BUY, price="40000", qty="2", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.BUY, price="70000", qty="1", order_id="b"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.qty == Decimal("3")
        expected_avg = (Decimal("40000") * 2 + Decimal("70000") * 1) / Decimal("3")
        assert pos.avg_price == expected_avg

    def test_sell_fill_increases_cash(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", order_id="b"))

        # proceeds = 55000 * 1 - 0 fee
        expected_cash = INITIAL_CASH - Decimal("50000") + Decimal("55000")
        assert portfolio.cash == expected_cash

    def test_sell_fill_includes_fee_in_proceeds(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", fee="200", order_id="b"))

        expected_cash = INITIAL_CASH - Decimal("50000") + (Decimal("55000") - Decimal("200"))
        assert portfolio.cash == expected_cash

    def test_sell_fill_decreases_position_qty(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="3", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", order_id="b"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.qty == Decimal("2")

    def test_sell_fill_records_realized_pnl(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", order_id="a"))
        # realized pnl = (55000 - 50000) * 1 = 5000
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", order_id="b"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.realized_pnl == Decimal("5000")

    def test_sell_fill_partial_position_accumulates_realized_pnl(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="2", order_id="a"))
        # first partial sell: (55000-50000)*1 = 5000
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", order_id="b"))
        # second partial sell: (60000-50000)*1 = 10000
        portfolio.apply_fill(_fill(OrderSide.SELL, price="60000", qty="1", order_id="c"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.realized_pnl == Decimal("15000")

    def test_full_sell_zeroes_position_qty(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="2", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="2", order_id="b"))

        pos = portfolio.position(SYMBOL)
        assert pos is not None
        assert pos.qty == Decimal("0")
        assert pos.avg_price == Decimal("0")

    def test_unrealized_pnl_positive(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1"))

        pnl = portfolio.unrealized_pnl(SYMBOL, Decimal("55000"))
        assert pnl == Decimal("5000")

    def test_unrealized_pnl_negative(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="2"))

        pnl = portfolio.unrealized_pnl(SYMBOL, Decimal("45000"))
        assert pnl == Decimal("-10000")

    def test_unrealized_pnl_zero_when_no_position(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        assert portfolio.unrealized_pnl(SYMBOL, Decimal("50000")) == Decimal("0")

    def test_unrealized_pnl_zero_after_full_sell(self) -> None:
        portfolio = Portfolio(INITIAL_CASH)
        portfolio.apply_fill(_fill(OrderSide.BUY, price="50000", qty="1", order_id="a"))
        portfolio.apply_fill(_fill(OrderSide.SELL, price="55000", qty="1", order_id="b"))

        assert portfolio.unrealized_pnl(SYMBOL, Decimal("60000")) == Decimal("0")
