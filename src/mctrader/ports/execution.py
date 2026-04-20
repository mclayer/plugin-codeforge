from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from mctrader.domain.order import ExecutionEvent, Order, OrderIntent


@dataclass
class OrderAck:
    order_id: str
    ts: int


@dataclass
class CancelAck:
    order_id: str
    success: bool
    ts: int


class ExecutionVenue(ABC):
    @abstractmethod
    def submit(self, order: OrderIntent) -> OrderAck: ...

    @abstractmethod
    def cancel(self, order_id: str) -> CancelAck: ...

    @abstractmethod
    def pending_orders(self) -> list[Order]: ...

    @abstractmethod
    def pop_events(self) -> list[ExecutionEvent]:
        # pull 방식: 체결/거부 이벤트를 꺼내감
        ...
