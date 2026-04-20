from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union

from mctrader.domain.symbol import Symbol


class OrderSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(enum.Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OrderIntent:
    symbol: Symbol
    side: OrderSide
    type: OrderType
    price: Optional[Decimal]  # required for LIMIT
    qty: Decimal
    ts: int


@dataclass
class Order:
    order_id: str
    intent: OrderIntent
    status: OrderStatus
    filled_qty: Decimal
    avg_price: Optional[Decimal]
    ts_submitted: int
    ts_updated: int


@dataclass(frozen=True)
class Fill:
    order_id: str
    symbol: Symbol
    side: OrderSide
    price: Decimal
    qty: Decimal
    fee: Decimal
    ts: int


ExecutionEvent = Union[Fill]  # PartialFill, Reject 추가 가능
