from __future__ import annotations

import importlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


@dataclass
class BacktestRunParams:
    start_date: str  # "YYYY-MM-DD"
    end_date: str  # "YYYY-MM-DD"
    symbols: str  # "all" 또는 "BTC_KRW,ETH_KRW"
    strategy: str  # "module.path:ClassName"
    queue_model: str  # "naive" | "proportional"
    initial_cash: str | None  # None이면 config 기본값 사용


def _datetime_to_epoch_ms(dt_str: str) -> int:
    """
    날짜/시각 문자열을 UTC epoch ms로 변환.

    지원 포맷:
      YYYY-MM-DD               → 해당 날짜 UTC 자정
      YYYY-MM-DDTHH:MM         → HTML datetime-local 입력값
      YYYY-MM-DDTHH:MM:SS
      YYYY-MM-DD HH:MM:SS
    """
    dt_str = dt_str.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    raise ValueError(f"날짜/시각 형식을 파싱할 수 없습니다: {dt_str!r}")


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


def run_backtest(params: BacktestRunParams) -> str:
    """백테스트를 동기 실행하고 run_id(result_path basename)를 반환."""
    from mctrader.adapters.clocks.sim_clock import SimClock
    from mctrader.adapters.exchanges.bithumb.gateway import BithumbGateway
    from mctrader.adapters.execution.queue_models.naive import NaiveQueueModel
    from mctrader.adapters.execution.queue_models.proportional import ProportionalQueueModel
    from mctrader.adapters.execution.simulated import SimulatedExecutionVenue
    from mctrader.adapters.storage.duckdb_source import DuckDBSource
    from mctrader.app.backtest_engine import BacktestConfig as EngineConfig
    from mctrader.app.backtest_engine import BacktestEngine
    from mctrader.app.result_recorder import ResultRecorder
    from mctrader.domain.portfolio import Portfolio
    from mctrader.domain.symbol import Symbol
    from mctrader.infra.config import load_backtest_config

    config = load_backtest_config()

    start_ts = _datetime_to_epoch_ms(params.start_date)
    end_ts = _datetime_to_epoch_ms(params.end_date)

    gateway = BithumbGateway()
    all_symbols: list[Symbol] = gateway.symbols()
    raw_symbols = _parse_symbols(params.symbols)
    if raw_symbols is None:
        symbols = all_symbols
    else:
        name_to_sym = {s.name: s for s in all_symbols}
        symbols = [name_to_sym[n] for n in raw_symbols if n in name_to_sym]

    strategy_cls = _import_strategy_class(params.strategy)
    strategy = strategy_cls()

    if params.queue_model == "proportional":
        queue_model = ProportionalQueueModel()
    else:
        queue_model = NaiveQueueModel()

    clock = SimClock()
    ref_symbol = symbols[0] if symbols else all_symbols[0]
    fee_schedule = gateway.fee_schedule(ref_symbol)
    venue = SimulatedExecutionVenue(fee_schedule=fee_schedule, clock=clock, queue_model=queue_model)
    data_source = DuckDBSource(root_path=config.data.root_path)
    initial_cash = Decimal(params.initial_cash or config.backtest.initial_cash)
    portfolio = Portfolio(initial_cash=initial_cash)
    run_id = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    run_path = os.path.join(config.backtest.result_path, run_id)
    recorder = ResultRecorder(result_path=run_path)

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
        queue_model_name=params.queue_model,
    )
    engine.run(engine_config)
    return run_id
