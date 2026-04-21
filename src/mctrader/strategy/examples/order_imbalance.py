"""
Order Imbalance 전략 데모.

시그널: imbalance = (bid_qty - ask_qty) / (bid_qty + ask_qty) 상위 N 레벨 기준
- imbalance > threshold  → BUY
- imbalance < -threshold → SELL

매수: 최우선 ask 가격에 지정가 주문
매도: 최우선 bid 가격에 지정가 주문
보유 중이면 반대 시그널에 청산
"""
from __future__ import annotations

from decimal import Decimal

from mctrader.domain.events import MarketEvent, OrderBookDiffEvent
from mctrader.domain.microstructure import imbalance as _imbalance
from mctrader.domain.order import Fill, OrderIntent, OrderSide, OrderType
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.signal import Signal, SignalDirection
from mctrader.domain.symbol import Symbol
from mctrader.ports.strategy import SignalGenerator, TradingStrategy


class OrderImbalanceSignalGenerator(SignalGenerator):
    def __init__(self, levels: int = 5, threshold: float = 0.3) -> None:
        self._levels = levels
        self._threshold = threshold

    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
    ) -> list[Signal]:
        # OrderBookDiffEvent 이후 snapshot이 있을 때만 계산
        if not isinstance(event, OrderBookDiffEvent) or snapshot is None:
            return []
        if not snapshot.bids or not snapshot.asks:
            return []

        imbalance = _imbalance(snapshot, depth=self._levels)

        if imbalance > self._threshold:
            direction = SignalDirection.LONG
        elif imbalance < -self._threshold:
            direction = SignalDirection.SHORT
        else:
            return []

        return [
            Signal(
                symbol=event.symbol,
                direction=direction,
                strength=abs(imbalance),
                ts=event.ts,
                metadata={"imbalance": imbalance},
            )
        ]


class OrderImbalanceStrategy(TradingStrategy):
    def __init__(
        self,
        signal_gen: OrderImbalanceSignalGenerator | None = None,
        order_qty: Decimal | None = None,
    ) -> None:
        self._signal_gen = signal_gen or OrderImbalanceSignalGenerator()
        # None이면 on_event 시점에 가용현금의 10%로 결정
        self._fixed_qty = order_qty
        # symbol → open order_id; 이미 오픈 주문 있으면 새 주문 생성 안 함
        self._open_orders: dict[Symbol, str] = {}

    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
        portfolio: Portfolio,
    ) -> list[OrderIntent]:
        signals = self._signal_gen.on_event(event, snapshot)
        if not signals or snapshot is None:
            return []

        intents: list[OrderIntent] = []
        for signal in signals:
            symbol = signal.symbol
            pos = portfolio.position(symbol)

            # 이미 오픈 주문이 있으면 중복 제출 생략
            if symbol in self._open_orders:
                continue

            if signal.direction == SignalDirection.LONG:
                if not snapshot.asks:
                    continue
                # 매수: 최우선 ask 가격에 지정가
                price = snapshot.asks[0].price
                qty = self._resolve_qty(price, portfolio)
                if qty <= Decimal(0):
                    continue
                intents.append(
                    OrderIntent(
                        symbol=symbol,
                        side=OrderSide.BUY,
                        type=OrderType.LIMIT,
                        price=price,
                        qty=qty,
                        ts=event.ts,
                    )
                )

            elif signal.direction == SignalDirection.SHORT:
                if pos is None or pos.qty <= Decimal(0):
                    continue
                if not snapshot.bids:
                    continue
                # 청산: 최우선 bid 가격에 지정가
                price = snapshot.bids[0].price
                intents.append(
                    OrderIntent(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        type=OrderType.LIMIT,
                        price=price,
                        qty=pos.qty,
                        ts=event.ts,
                    )
                )

        # 제출할 인텐트가 생겼으면 추적용 플레이스홀더 등록 (order_id는 체결 후 확정)
        for intent in intents:
            # 실제 order_id는 venue가 부여하므로 여기서는 sentinel로 표시
            self._open_orders[intent.symbol] = "_pending_"

        return intents

    def on_execution(
        self,
        fill: Fill,
        portfolio: Portfolio,
    ) -> list[OrderIntent]:
        # 체결 완료 → 해당 심볼의 오픈 주문 추적 해제
        self._open_orders.pop(fill.symbol, None)
        return []

    def _resolve_qty(self, price: Decimal, portfolio: Portfolio) -> Decimal:
        if self._fixed_qty is not None:
            return self._fixed_qty
        # 가용 현금의 10%로 살 수 있는 수량
        budget = portfolio.cash * Decimal("0.1")
        if price == Decimal(0):
            return Decimal(0)
        return (budget / price).quantize(Decimal("0.00000001"))
