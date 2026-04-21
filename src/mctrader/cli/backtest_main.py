from __future__ import annotations

import importlib
import logging
import sys
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


def _date_to_epoch_ms(date_str: str) -> int:
    """YYYY-MM-DD 문자열을 UTC 자정 epoch ms로 변환."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def _parse_symbols(symbols_arg: str) -> list[str] | None:
    """
    "all" → None (엔진이 전체 처리).
    "BTC_KRW,ETH_KRW" → ["BTC_KRW", "ETH_KRW"] 문자열 리스트.
    """
    if symbols_arg.strip().lower() == "all":
        return None
    return [s.strip() for s in symbols_arg.split(",") if s.strip()]


def _import_strategy_class(spec: str) -> type:
    """
    "module.path:ClassName" 형식으로 전략 클래스를 동적 import.
    """
    if ":" not in spec:
        raise ValueError(f"--strategy must be 'module:ClassName', got: {spec!r}")
    module_path, class_name = spec.rsplit(":", 1)
    module = importlib.import_module(module_path)
    cls: type = getattr(module, class_name)
    return cls


def main() -> None:
    """
    mctrader-backtest 진입점.

    usage: mctrader-backtest --start YYYY-MM-DD --end YYYY-MM-DD
                             [--symbols SYM1,SYM2] [--strategy MODULE.CLASS]
    """
    import argparse

    parser = argparse.ArgumentParser(description="mctrader backtester")
    parser.add_argument("--start", required=True, help="start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="end date YYYY-MM-DD")
    parser.add_argument("--symbols", default="all")
    parser.add_argument(
        "--strategy",
        default="mctrader.strategy.examples.order_imbalance:OrderImbalanceStrategy",
    )
    args = parser.parse_args()

    from mctrader.infra.config import load_backtest_config
    from mctrader.infra.logging import setup_logging

    try:
        config = load_backtest_config()
    except Exception as exc:
        print(f"[backtest] failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.logging)

    try:
        start_ts = _date_to_epoch_ms(args.start)
        end_ts = _date_to_epoch_ms(args.end)
    except ValueError as exc:
        logger.error("invalid date format: %s", exc)
        sys.exit(1)

    # Symbol 객체 리스트 구성 (None이면 config 기본값 사용)
    raw_symbols = _parse_symbols(args.symbols)

    from mctrader.adapters.exchanges.bithumb.gateway import BithumbGateway
    from mctrader.domain.symbol import Symbol

    gateway = BithumbGateway()
    all_gateway_symbols: list[Symbol] = gateway.symbols()

    if raw_symbols is None:
        symbols = all_gateway_symbols
    else:
        name_to_sym = {s.name: s for s in all_gateway_symbols}
        symbols = []
        for name in raw_symbols:
            if name not in name_to_sym:
                logger.error("unknown symbol: %s", name)
                sys.exit(1)
            symbols.append(name_to_sym[name])

    try:
        strategy_cls = _import_strategy_class(args.strategy)
    except (ValueError, ImportError, AttributeError) as exc:
        logger.error("failed to import strategy %r: %s", args.strategy, exc)
        sys.exit(1)

    strategy = strategy_cls()

    # --- BacktestEngine 조립 ---
    from mctrader.adapters.clocks.sim_clock import SimClock
    from mctrader.adapters.execution.queue_models.naive import NaiveQueueModel
    from mctrader.adapters.execution.simulated import SimulatedExecutionVenue
    from mctrader.adapters.storage.duckdb_source import DuckDBSource
    from mctrader.app.backtest_engine import BacktestConfig as EngineConfig
    from mctrader.app.backtest_engine import BacktestEngine
    from mctrader.app.result_recorder import ResultRecorder
    from mctrader.domain.portfolio import Portfolio

    clock = SimClock()
    queue_model = NaiveQueueModel()
    # fee schedule은 Bithumb에서 모든 심볼 동일; 첫 번째 심볼로 조회
    ref_symbol = symbols[0] if symbols else all_gateway_symbols[0]
    fee_schedule = gateway.fee_schedule(ref_symbol)
    venue = SimulatedExecutionVenue(
        fee_schedule=fee_schedule,
        clock=clock,
        queue_model=queue_model,
    )
    data_source = DuckDBSource(root_path=config.data.root_path)
    initial_cash = Decimal(config.backtest.initial_cash)
    portfolio = Portfolio(initial_cash=initial_cash)
    recorder = ResultRecorder(result_path=config.backtest.result_path)

    engine = BacktestEngine(
        data_source=data_source,
        venue=venue,
        strategy=strategy,
        clock=clock,
        portfolio=portfolio,
        recorder=recorder,
    )

    engine_config = EngineConfig(
        symbols=symbols,
        start_ts=start_ts,
        end_ts=end_ts,
        initial_cash=initial_cash,
        queue_model_name=config.backtest.queue_model,
    )

    try:
        result = engine.run(engine_config)
    except Exception:
        logger.exception("backtest terminated with error")
        sys.exit(1)

    print(f"total_trades  : {result.total_trades}")
    print(f"total_fills   : {result.total_fills}")
    print(f"final_equity  : {result.final_equity}")
    print(f"realized_pnl  : {result.realized_pnl}")
    if result.result_path:
        print(f"result_path   : {result.result_path}")
