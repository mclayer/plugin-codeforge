from __future__ import annotations

import asyncio
import logging
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    """
    mctrader-collector 진입점.

    usage: mctrader-collector [--config PATH] [--dry-run] [--exchange {bithumb}]
    """
    sys.stdout.reconfigure(line_buffering=True)
    import argparse

    parser = argparse.ArgumentParser(description="mctrader market data collector")
    parser.add_argument("--config", default=None, help="config directory path override")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate config + probe WS handshake without collecting",
    )
    parser.add_argument(
        "--exchange",
        type=str,
        default=None,
        choices=["bithumb"],
        help="Limit dry-run to a specific exchange (default: all)",
    )
    args = parser.parse_args()

    # --exchange without --dry-run is an error (exit 2, argparse convention)
    if args.exchange is not None and not args.dry_run:
        parser.error("--exchange requires --dry-run")

    from mctrader.infra.config import load_collector_config

    if args.config is not None:
        # Override the config directory via env var so _CONFIG_DIR picks it up.
        import os
        os.environ.setdefault("MCTRADER_CONFIG_DIR", args.config)

    if args.dry_run:
        # dry-run path: skip setup_logging (decision 3 in change plan)
        import os
        config_path = os.environ.get("MCTRADER_CONFIG_DIR", args.config or "config")

        try:
            config = load_collector_config()
        except Exception as exc:
            print(f"[dry-run:failed] {_DRY_RUN_STAGE_CONFIG_LOAD}: {exc}", file=sys.stderr)
            sys.exit(1)

        from mctrader.app.dry_run import DryRunFailed, run_dry_run

        try:
            asyncio.run(run_dry_run(config, config_path, exchange_filter=args.exchange))
        except DryRunFailed as exc:
            print(f"[dry-run:failed] {exc.stage}: {exc.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:
            print(f"[dry-run:failed] {_DRY_RUN_STAGE_CONFIG_LOAD}: {exc}", file=sys.stderr)
            sys.exit(1)

        sys.exit(0)

    # Normal collection path
    from mctrader.infra.logging import setup_logging

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


_DRY_RUN_STAGE_CONFIG_LOAD = "config_load"
