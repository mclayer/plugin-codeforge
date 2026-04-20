from __future__ import annotations

from decimal import Decimal

from mctrader.adapters.exchanges.bithumb import codec
from mctrader.domain.events import MarketEvent
from mctrader.domain.symbol import FeeSchedule, Market, Symbol
from mctrader.ports.exchange import ExchangeGateway

_MAKER_FEE = Decimal("0.0004")
_TAKER_FEE = Decimal("0.0004")

_COINS = [
    "BTC", "ETH", "XRP", "ADA", "SOL", "DOGE", "MATIC", "DOT", "AVAX", "LINK",
    "SAND", "MANA", "ATOM", "NEAR", "FTM", "ALGO", "VET", "TRX", "EOS", "LTC",
]

_TICK_SIZES: dict[str, Decimal] = {
    "BTC_KRW": Decimal("1000"),
    "ETH_KRW": Decimal("10"),
}


class BithumbGateway(ExchangeGateway):
    @property
    def name(self) -> str:
        return "bithumb"

    def symbols(self) -> list[Symbol]:
        return [
            Symbol(base=coin, quote="KRW", market=Market.BITHUMB)
            for coin in _COINS
        ]

    def tick_size(self, symbol: Symbol) -> Decimal:
        return _TICK_SIZES.get(symbol.name, Decimal("1"))

    def fee_schedule(self, symbol: Symbol) -> FeeSchedule:
        return FeeSchedule(maker=_MAKER_FEE, taker=_TAKER_FEE)

    def normalize_event(self, raw: dict) -> MarketEvent | None:
        return codec.decode(raw, market=Market.BITHUMB)
