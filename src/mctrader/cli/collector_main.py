from __future__ import annotations

import asyncio
import logging
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    """
    mctrader-collector 진입점.

    usage: mctrader-collector [--config PATH]
    """
    sys.stdout.reconfigure(line_buffering=True)
    import argparse

    parser = argparse.ArgumentParser(description="mctrader market data collector")
    parser.add_argument("--config", default=None, help="config directory path override")
    args = parser.parse_args()

    from mctrader.infra.config import load_collector_config
    from mctrader.infra.logging import setup_logging

    if args.config is not None:
        # Override the config directory via env var so _CONFIG_DIR picks it up.
        import os
        os.environ.setdefault("MCTRADER_CONFIG_DIR", args.config)

    try:
        config = load_collector_config()
    except Exception as exc:
        # Logging not yet configured; write to stderr directly.
        print(f"[collector] failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.logging)

    from mctrader.app.collector_service import run_collector

    try:
        asyncio.run(run_collector(config))
    except Exception:
        logger.exception("collector terminated with error")
        sys.exit(1)
