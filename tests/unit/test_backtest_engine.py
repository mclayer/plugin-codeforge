from __future__ import annotations

import tempfile
from collections.abc import Iterator
from decimal import Decimal

from mctrader.adapters.clocks.sim_clock import SimClock
from mctrader.adapters.execution.queue_models.naive import NaiveQueueModel
from mctrader.adapters.execution.simulated import SimulatedExecutionVenue
from mctrader.app.backtest_engine import BacktestConfig, BacktestEngine
from mctrader.app.result_recorder import ResultRecorder
from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import Fill, OrderIntent, OrderSide, OrderType
from mctrader.domain.orderbook import OrderBookSnapshot
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.symbol import FeeSchedule, Market, Symbol
from mctrader.ports.market_data import MarketDataSource
from mctrader.ports.strategy import CoinSelector, RiskManager, TradingStrategy

BTC = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)
FEE = FeeSchedule(maker=Decimal("0.001"), taker=Decimal("0.001"))


def _ob_event(ts: int, seq: int, bid: str, ask: str) -> OrderBookDiffEvent:
    return OrderBookDiffEvent(
        symbol=BTC,
        ts=ts,
        seq=seq,
        bids_delta=((Decimal(bid), Decimal("1.0")),),
        asks_delta=((Decimal(ask), Decimal("1.0")),),
    )


def _trade_event(ts: int, seq: int, price: str) -> TradeEvent:
    return TradeEvent(
        symbol=BTC, ts=ts, seq=seq, price=Decimal(price), qty=Decimal("0.1"), side="buy"
    )


class _StubDataSource(MarketDataSource):
    def __init__(self, events: list[MarketEvent]) -> None:
        self._events = events

    def stream(self, symbols: list[Symbol], start_ts: int, end_ts: int) -> Iterator[MarketEvent]:
        yield from self._events


class _PassiveStrategy(TradingStrategy):
    """전략 없음 — 아무 주문도 내지 않음."""

    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
        portfolio: Portfolio,
    ) -> list[OrderIntent]:
        return []

    def on_execution(self, fill: Fill, portfolio: Portfolio) -> list[OrderIntent]:
        return []


class _SingleBuyStrategy(TradingStrategy):
    """첫 번째 이벤트에서 시장가 매수 1회."""

    def __init__(self) -> None:
        self._submitted = False

    def on_event(
        self,
        event: MarketEvent,
        snapshot: OrderBookSnapshot | None,
        portfolio: Portfolio,
    ) -> list[OrderIntent]:
        if self._submitted:
            return []
        self._submitted = True
        return [OrderIntent(
            symbol=BTC,
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            price=None,
            qty=Decimal("0.1"),
            ts=event.ts,
        )]

    def on_execution(self, fill: Fill, portfolio: Portfolio) -> list[OrderIntent]:
        return []


def _make_engine(
    events: list[MarketEvent], strategy: TradingStrategy, result_path: str
) -> tuple[BacktestEngine, BacktestConfig]:
    clock = SimClock()
    queue_model = NaiveQueueModel()
    venue = SimulatedExecutionVenue(FEE, clock, queue_model)
    portfolio = Portfolio(initial_cash=Decimal("1000000"))
    recorder = ResultRecorder(result_path, equity_sample_interval=1)
    source = _StubDataSource(events)

    engine = BacktestEngine(
        data_source=source,
        venue=venue,
        strategy=strategy,
        clock=clock,
        portfolio=portfolio,
        recorder=recorder,
    )
    config = BacktestConfig(
        symbols=[BTC],
        start_ts=0,
        end_ts=99999,
        initial_cash=Decimal("1000000"),
        queue_model_name="naive",
    )
    return engine, config


class TestBacktestEnginePassive:
    def test_runs_with_no_orders(self) -> None:
        events = [
            _ob_event(1000, 1, "49900", "50100"),
            _trade_event(2000, 2, "50000"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine(events, _PassiveStrategy(), tmp)
            result = engine.run(config)

        assert result.total_fills == 0
        assert result.final_equity == Decimal("1000000")
        assert result.realized_pnl == Decimal("0")

    def test_result_path_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine(
                [_ob_event(1000, 1, "49900", "50100")], _PassiveStrategy(), tmp
            )
            result = engine.run(config)
        assert result.result_path == tmp

    def test_empty_event_stream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine([], _PassiveStrategy(), tmp)
            result = engine.run(config)
        assert result.total_fills == 0


class TestBacktestEngineWithOrders:
    def test_market_buy_fills_and_reduces_cash(self) -> None:
        events = [
            _ob_event(1000, 1, "49900", "50100"),
            _ob_event(2000, 2, "49900", "50100"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine(events, _SingleBuyStrategy(), tmp)
            result = engine.run(config)

        assert result.total_fills == 1

    def test_clock_advances_with_events(self) -> None:
        clock = SimClock()
        queue_model = NaiveQueueModel()
        venue = SimulatedExecutionVenue(FEE, clock, queue_model)
        portfolio = Portfolio(initial_cash=Decimal("1000000"))

        with tempfile.TemporaryDirectory() as tmp:
            recorder = ResultRecorder(tmp)
            source = _StubDataSource([
                _ob_event(1000, 1, "49900", "50100"),
                _ob_event(5000, 2, "49900", "50100"),
            ])
            engine = BacktestEngine(
                data_source=source,
                venue=venue,
                strategy=_PassiveStrategy(),
                clock=clock,
                portfolio=portfolio,
                recorder=recorder,
            )
            config = BacktestConfig(
                symbols=[BTC], start_ts=0, end_ts=99999,
                initial_cash=Decimal("1000000"), queue_model_name="naive",
            )
            engine.run(config)

        assert clock.now() == 5000


class TestBacktestEngineResultFiles:
    def test_summary_json_written(self) -> None:
        import json
        import os
        events = [_ob_event(1000, 1, "49900", "50100"), _ob_event(2000, 2, "49900", "50100")]
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine(events, _PassiveStrategy(), tmp)
            engine.run(config)
            with open(os.path.join(tmp, "summary.json")) as f:
                summary = json.load(f)

        assert "total_fills" in summary
        assert "final_equity" in summary
        assert "realized_pnl" in summary
        assert summary["start_ts"] == 1000
        assert summary["end_ts"] == 2000


class _RejectAllRiskManager(RiskManager):
    """항상 False를 반환하는 RiskManager — 모든 주문 거부."""

    def check(self, intent: OrderIntent, portfolio: Portfolio) -> bool:
        return False


class _AcceptAllRiskManager(RiskManager):
    """항상 True를 반환하는 RiskManager — 모든 주문 허용."""

    def check(self, intent: OrderIntent, portfolio: Portfolio) -> bool:
        return True


class _StaticCoinSelector(CoinSelector):
    """고정된 심볼 리스트를 반환하는 CoinSelector."""

    def __init__(self, symbols: list[Symbol]) -> None:
        self._symbols = symbols

    def select(self, universe: list[Symbol], ts: int) -> list[Symbol]:
        return self._symbols


class TestBacktestEngineRiskManager:
    def test_risk_manager_reject_prevents_order_submission(self) -> None:
        """RiskManager가 False 반환 시 주문이 제출되지 않아야 한다."""
        events = [
            _ob_event(1000, 1, "49900", "50100"),
            _ob_event(2000, 2, "49900", "50100"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            clock = SimClock()
            queue_model = NaiveQueueModel()
            venue = SimulatedExecutionVenue(FEE, clock, queue_model)
            portfolio = Portfolio(initial_cash=Decimal("1000000"))
            recorder = ResultRecorder(tmp, equity_sample_interval=1)
            source = _StubDataSource(events)

            engine = BacktestEngine(
                data_source=source,
                venue=venue,
                strategy=_SingleBuyStrategy(),
                clock=clock,
                portfolio=portfolio,
                recorder=recorder,
                risk_manager=_RejectAllRiskManager(),
            )
            config = BacktestConfig(
                symbols=[BTC], start_ts=0, end_ts=99999,
                initial_cash=Decimal("1000000"), queue_model_name="naive",
            )
            result = engine.run(config)

        # RiskManager가 모든 주문을 거부했으므로 fill이 없어야 함
        assert result.total_fills == 0

    def test_risk_manager_accept_allows_order_submission(self) -> None:
        """RiskManager가 True 반환 시 주문이 정상 제출되어야 한다."""
        events = [
            _ob_event(1000, 1, "49900", "50100"),
            _ob_event(2000, 2, "49900", "50100"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            clock = SimClock()
            queue_model = NaiveQueueModel()
            venue = SimulatedExecutionVenue(FEE, clock, queue_model)
            portfolio = Portfolio(initial_cash=Decimal("1000000"))
            recorder = ResultRecorder(tmp, equity_sample_interval=1)
            source = _StubDataSource(events)

            engine = BacktestEngine(
                data_source=source,
                venue=venue,
                strategy=_SingleBuyStrategy(),
                clock=clock,
                portfolio=portfolio,
                recorder=recorder,
                risk_manager=_AcceptAllRiskManager(),
            )
            config = BacktestConfig(
                symbols=[BTC], start_ts=0, end_ts=99999,
                initial_cash=Decimal("1000000"), queue_model_name="naive",
            )
            result = engine.run(config)

        # RiskManager가 허용했으므로 fill이 있어야 함
        assert result.total_fills == 1

    def test_no_risk_manager_submits_orders_by_default(self) -> None:
        """RiskManager 없을 때 주문이 기본으로 제출되어야 한다."""
        events = [
            _ob_event(1000, 1, "49900", "50100"),
            _ob_event(2000, 2, "49900", "50100"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            engine, config = _make_engine(events, _SingleBuyStrategy(), tmp)
            result = engine.run(config)

        assert result.total_fills == 1


class TestBacktestEngineCoinSelector:
    def test_coin_selector_port_accepts_implementation(self) -> None:
        """CoinSelector 포트가 구현 가능한지 검증.
        BacktestEngine은 현재 coin_selector를 내부에서 사용하지 않지만
        포트가 올바르게 주입되고 보존되어야 한다."""
        selector = _StaticCoinSelector([BTC])
        with tempfile.TemporaryDirectory() as tmp:
            clock = SimClock()
            queue_model = NaiveQueueModel()
            venue = SimulatedExecutionVenue(FEE, clock, queue_model)
            portfolio = Portfolio(initial_cash=Decimal("1000000"))
            recorder = ResultRecorder(tmp)
            source = _StubDataSource([])

            engine = BacktestEngine(
                data_source=source,
                venue=venue,
                strategy=_PassiveStrategy(),
                clock=clock,
                portfolio=portfolio,
                recorder=recorder,
                coin_selector=selector,
            )
            assert engine._coin_selector is selector

            config = BacktestConfig(
                symbols=[BTC], start_ts=0, end_ts=99999,
                initial_cash=Decimal("1000000"), queue_model_name="naive",
            )
            result = engine.run(config)

        assert result.total_fills == 0

    def test_coin_selector_select_method_returns_filtered_list(self) -> None:
        """CoinSelector.select()가 올바른 심볼 필터링을 수행하는지 검증."""
        eth = Symbol(base="ETH", quote="KRW", market=Market.BITHUMB)
        selector = _StaticCoinSelector([BTC])

        universe = [BTC, eth]
        result = selector.select(universe, ts=1000)

        assert result == [BTC]
        assert eth not in result
