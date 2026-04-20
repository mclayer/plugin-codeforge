from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal


class Market(enum.Enum):
    BITHUMB = "bithumb"
    UPBIT = "upbit"
    BINANCE = "binance"


@dataclass(frozen=True)
class Symbol:
    base: str
    quote: str
    market: Market

    @property
    def name(self) -> str:
        return f"{self.base}_{self.quote}"

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class FeeSchedule:
    maker: Decimal
    taker: Decimal
