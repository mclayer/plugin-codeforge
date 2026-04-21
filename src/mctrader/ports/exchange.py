from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from mctrader.domain.events import MarketEvent
from mctrader.domain.symbol import FeeSchedule, Symbol


class ExchangeGateway(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def symbols(self) -> list[Symbol]: ...

    @abstractmethod
    def tick_size(self, symbol: Symbol) -> Decimal: ...

    @abstractmethod
    def fee_schedule(self, symbol: Symbol) -> FeeSchedule: ...

    @abstractmethod
    def normalize_event(self, raw: dict[str, object]) -> MarketEvent | None: ...
