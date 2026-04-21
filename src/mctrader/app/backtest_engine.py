from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from decimal import Decimal

from mctrader.adapters.clocks.sim_clock import SimClock
from mctrader.adapters.execution.simulated import SimulatedExecutionVenue
from mctrader.app.result_recorder import ResultRecorder
from mctrader.domain.events import MarketEvent, OrderBookDiffEvent, TradeEvent
from mctrader.domain.order import OrderIntent
from mctrader.domain.orderbook import OrderBook, OrderBookSnapshot
from mctrader.domain.portfolio import Portfolio
from mctrader.domain.symbol import Symbol
from mctrader.ports.market_data import MarketDataSource
from mctrader.ports.progress import NoopProgressReporter, ProgressEvent, ProgressReporter
from mctrader.ports.strategy import CoinSelector, RiskManager, TradingStrategy

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """BacktestEngine 실행 설정."""

    symbols: list[Symbol]
    start_ts: int
    end_ts: int
    initial_cash: Decimal
    queue_model_name: str  # "naive" | "proportional"


@dataclass
class BacktestResult:
    total_trades: int
    total_fills: int
    final_equity: Decimal
    realized_pnl: Decimal
    result_path: str | None  # ResultRecorder가 저장한 경로; None이면 저장 없음


# Mapping from Symbol to its live OrderBook.
OrderBookRegistry = dict[Symbol, OrderBook]


class BacktestEngine:
    """
    단일 스레드 이벤트 루프.

    루프 순서 (이벤트 1개 처리 기준):
      1. MarketDataSource.stream()에서 이벤트 소비
      2. SimClock 업데이트
      3. OrderBookRegistry 갱신 (OrderBookDiffEvent인 경우)
      4. 갱신된 OrderBook으로 snapshot 생성
      5. SimulatedExecutionVenue.on_market_event(event, snapshot) → 미체결 매칭
      6. venue.pop_events()로 Fill 꺼내 Portfolio 업데이트
      7. Strategy.on_execution() — Fill마다 호출
      8. Strategy.on_event() → OrderIntent 목록
      9. RiskManager.check() 통과한 OrderIntent만 venue.submit()
     10. ResultRecorder에 스냅샷/Fill 기록
    """

    def __init__(
        self,
        data_source: MarketDataSource,
        venue: SimulatedExecutionVenue,
        strategy: TradingStrategy,
        clock: SimClock,
        portfolio: Portfolio,
        recorder: ResultRecorder,
        coin_selector: CoinSelector | None = None,
        risk_manager: RiskManager | None = None,
        progress_reporter: ProgressReporter | None = None,
    ) -> None:
        self._data_source = data_source
        self._venue = venue
        self._strategy = strategy
        self._clock = clock
        self._portfolio = portfolio
        self._recorder = recorder
        self._coin_selector = coin_selector
        self._risk_manager = risk_manager
        self._reporter = progress_reporter or NoopProgressReporter()

    def run(self, config: BacktestConfig) -> BacktestResult:
        orderbooks: OrderBookRegistry = {s: OrderBook(s) for s in config.symbols}

        # last known mid-price per symbol; used for equity valuation
        prices: dict[Symbol, Decimal] = {}

        event_count = 0
        total_fills = 0
        planned = tuple(s.name for s in config.symbols)

        self._reporter.report(ProgressEvent(
            phase="preparing",
            progress_pct=0.0,
            current_symbol=None,
            planned_symbols=planned,
            current_ts=None,
            start_ts=config.start_ts,
            end_ts=config.end_ts,
            event_count=0,
            total_fills=0,
        ))

        stream = self._data_source.stream(
            symbols=config.symbols,
            start_ts=config.start_ts,
            end_ts=config.end_ts,
        )

        try:
            for event in stream:
                event_count += 1

                current_sym = getattr(event, "symbol", None)
                self._reporter.report(ProgressEvent(
                    phase="replaying",
                    progress_pct=_compute_pct(event.ts, config.start_ts, config.end_ts),
                    current_symbol=current_sym.name if current_sym is not None else None,
                    planned_symbols=planned,
                    current_ts=event.ts,
                    start_ts=config.start_ts,
                    end_ts=config.end_ts,
                    event_count=event_count,
                    total_fills=total_fills,
                ))

                # 2. advance clock
                self._clock.set(event.ts)

                # 3 & 4. update OrderBook and derive snapshot
                snapshot = self._process_market_event(event, orderbooks, prices)

                # 5. match pending orders against updated book
                self._venue.on_market_event(event, snapshot)

                # 6 & 7. process fills
                for fill in self._venue.pop_events():
                    total_fills += 1
                    self._portfolio.apply_fill(fill)
                    self._recorder.on_fill(fill, self._portfolio)
                    for intent in self._strategy.on_execution(fill, self._portfolio):
                        self._submit_intent(intent)

                # 8 & 9. generate new signals → submit orders
                for intent in self._strategy.on_event(event, snapshot, self._portfolio):
                    self._submit_intent(intent)

                # 10. periodic recorder snapshot
                self._recorder.on_event(event.ts, event_count, self._portfolio, prices)

                if event_count % 100_000 == 0:
                    equity = self._portfolio.total_equity(prices)
                    logger.info(
                        "backtest progress: events=%d ts=%d equity=%s fills=%d",
                        event_count,
                        event.ts,
                        equity,
                        total_fills,
                    )

        except Exception as exc:
            self._reporter.report(ProgressEvent(
                phase="error",
                progress_pct=0.0,
                current_symbol=None,
                planned_symbols=planned,
                current_ts=None,
                start_ts=config.start_ts,
                end_ts=config.end_ts,
                event_count=event_count,
                total_fills=total_fills,
                error=str(exc),
            ))
            raise

        # --- end of stream ---
        self._reporter.report(ProgressEvent(
            phase="finalizing",
            progress_pct=99.0,
            current_symbol=None,
            planned_symbols=planned,
            current_ts=None,
            start_ts=config.start_ts,
            end_ts=config.end_ts,
            event_count=event_count,
            total_fills=total_fills,
        ))

        final_equity = self._portfolio.total_equity(prices)
        realized_pnl = _total_realized_pnl(self._portfolio)

        result_path = self._recorder.finalize()
        _write_summary(
            result_path=result_path,
            recorder=self._recorder,
            total_fills=total_fills,
            final_equity=final_equity,
            realized_pnl=realized_pnl,
        )

        self._reporter.report(ProgressEvent(
            phase="done",
            progress_pct=100.0,
            current_symbol=None,
            planned_symbols=planned,
            current_ts=None,
            start_ts=config.start_ts,
            end_ts=config.end_ts,
            event_count=event_count,
            total_fills=total_fills,
        ))

        logger.info(
            "backtest complete: events=%d fills=%d equity=%s pnl=%s",
            event_count,
            total_fills,
            final_equity,
            realized_pnl,
        )

        return BacktestResult(
            total_trades=total_fills,  # each fill corresponds to one trade leg
            total_fills=total_fills,
            final_equity=final_equity,
            realized_pnl=realized_pnl,
            result_path=result_path,
        )

    def _process_market_event(
        self,
        event: MarketEvent,
        orderbooks: OrderBookRegistry,
        prices: dict[Symbol, Decimal],
    ) -> OrderBookSnapshot:
        """Process market event: update books and derive snapshot."""
        snapshot: OrderBookSnapshot | None = None

        if isinstance(event, OrderBookDiffEvent):
            ob = orderbooks.get(event.symbol)
            if ob is not None:
                ob.apply_diff(event)
                snapshot = ob.snapshot()
                mid = _mid_from_snapshot(snapshot)
                if mid is not None:
                    prices[event.symbol] = mid
        elif isinstance(event, TradeEvent):
            prices[event.symbol] = event.price
            ob = orderbooks.get(event.symbol)
            if ob is not None:
                snapshot = ob.snapshot()

        if snapshot is None:
            snapshot = _empty_snapshot_for(event, orderbooks)

        return snapshot

    def _submit_intent(self, intent: OrderIntent) -> None:
        """Submit order intent if risk check passes."""
        if self._risk_manager is not None and not self._risk_manager.check(intent, self._portfolio):
            return
        self._venue.submit(intent)


# ------------------------------------------------------------------
# module-level helpers (no external state)


def _compute_pct(current_ts: int, start_ts: int, end_ts: int) -> float:
    span = end_ts - start_ts
    if span <= 0:
        return 100.0
    pct = (current_ts - start_ts) / span * 100.0
    return max(0.0, min(100.0, pct))


def _mid_from_snapshot(snapshot: OrderBookSnapshot) -> Decimal | None:
    """Calculate midprice from best bid and ask, or return None if unavailable."""
    if snapshot.bids and snapshot.asks:
        return (snapshot.bids[0].price + snapshot.asks[0].price) / Decimal(2)
    return None


def _empty_snapshot_for(
    event: MarketEvent,
    orderbooks: OrderBookRegistry,
) -> OrderBookSnapshot:
    """Return a snapshot for the event's symbol when no update occurred this tick."""
    symbol: Symbol | None = getattr(event, "symbol", None)
    if symbol is not None:
        ob = orderbooks.get(symbol)
        if ob is not None:
            return ob.snapshot()

    # ClockTickEvent has no symbol; return a sentinel with the first known book.
    if orderbooks:
        return next(iter(orderbooks.values())).snapshot()

    raise RuntimeError("No OrderBook available to produce a snapshot")


def _total_realized_pnl(portfolio: Portfolio) -> Decimal:
    """Sum realized P&L across all positions."""
    return sum(
        (pos.realized_pnl for pos in portfolio.all_positions().values()),
        Decimal(0),
    )


def _write_summary(
    result_path: str,
    recorder: ResultRecorder,
    total_fills: int,
    final_equity: Decimal,
    realized_pnl: Decimal,
) -> None:
    """Write backtest summary to summary.json with engine-enriched metrics."""
    summary = {
        "total_trades": total_fills,
        "total_fills": total_fills,
        "final_equity": str(final_equity),
        "realized_pnl": str(realized_pnl),
        "start_ts": recorder.start_ts,
        "end_ts": recorder.end_ts,
    }
    summary_path = os.path.join(result_path, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
