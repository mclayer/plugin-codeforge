from __future__ import annotations

import json
import logging
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    """
    mctrader-backtest 진입점.

    usage: mctrader-backtest --start YYYY-MM-DD --end YYYY-MM-DD
                             [--symbols SYM1,SYM2] [--strategy MODULE:CLASS]
                             [--queue-model naive|proportional]
                             [--initial-cash AMOUNT]
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
    parser.add_argument("--queue-model", default="naive", dest="queue_model")
    parser.add_argument("--initial-cash", default=None, dest="initial_cash")
    args = parser.parse_args()

    from mctrader.infra.config import load_backtest_config
    from mctrader.infra.logging import setup_logging

    try:
        config = load_backtest_config()
    except Exception as exc:
        print(f"[backtest] failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.logging)

    from mctrader.dashboard.backtest_runner import BacktestRunParams, run_backtest

    params = BacktestRunParams(
        start_date=args.start,
        end_date=args.end,
        symbols=args.symbols,
        strategy=args.strategy,
        queue_model=args.queue_model,
        initial_cash=args.initial_cash,
    )

    try:
        run_id = run_backtest(params)
    except Exception:
        logger.exception("backtest terminated with error")
        sys.exit(1)

    # 결과 summary.json 읽어서 stdout 출력
    import os

    summary_path = os.path.join(config.backtest.result_path, run_id, "summary.json")
    try:
        with open(summary_path) as f:
            summary = json.load(f)
        print(f"total_trades  : {summary.get('total_trades', 'N/A')}")
        print(f"total_fills   : {summary.get('total_fills', 'N/A')}")
        print(f"final_equity  : {summary.get('final_equity', 'N/A')}")
        print(f"realized_pnl  : {summary.get('realized_pnl', 'N/A')}")
        print(f"result_path   : {os.path.join(config.backtest.result_path, run_id)}")
    except Exception:
        print(f"result_path   : {os.path.join(config.backtest.result_path, run_id)}")
