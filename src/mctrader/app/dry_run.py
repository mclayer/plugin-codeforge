from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mctrader.infra.config import CollectorConfig

# ---------------------------------------------------------------------------
# Stage constants
# ---------------------------------------------------------------------------

DRY_RUN_STAGE_CONFIG_LOAD: str = "config_load"
DRY_RUN_STAGE_CONFIG_VALIDATE: str = "config_validate"
DRY_RUN_STAGE_SYMBOL_RESOLVE: str = "symbol_resolve"
DRY_RUN_STAGE_WEBSOCKET_HANDSHAKE: str = "websocket_handshake"


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class DryRunFailed(Exception):
    """Raised when a dry-run stage fails."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(f"{stage}: {reason}")
        self.stage = stage
        self.reason = reason


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def run_dry_run(
    config: CollectorConfig,
    config_path: str,
    exchange_filter: str | None = None,
) -> None:
    """Execute dry-run validation: config load + symbol resolve + WS handshake.

    Prints stage-by-stage checklist to stdout.
    Raises DryRunFailed on any stage failure.
    """
    from mctrader.adapters.exchanges.bithumb.gateway import BithumbGateway
    from mctrader.adapters.exchanges.bithumb.ws_client import BithumbWsClient
    from mctrader.app.collector_service import filter_symbols

    # -- CONFIG_LOAD ----------------------------------------------------------
    print(f"[dry-run] config loaded: {config_path}")

    # -- CONFIG_VALIDATE ------------------------------------------------------
    # Argparse already rejects unknown exchange values, but we validate
    # runtime config fields that argparse cannot check.
    if not config.bithumb.ws_url:
        raise DryRunFailed(
            DRY_RUN_STAGE_CONFIG_VALIDATE,
            "bithumb.ws_url is empty in config",
        )

    # Build exchange list to probe (currently only bithumb is supported).
    exchanges: list[str] = ["bithumb"]
    if exchange_filter is not None:
        if exchange_filter not in exchanges:
            raise DryRunFailed(
                DRY_RUN_STAGE_CONFIG_VALIDATE,
                f"unknown exchange: {exchange_filter}",
            )
        exchanges = [exchange_filter]

    for exchange_name in exchanges:
        # -- SYMBOL_RESOLVE ---------------------------------------------------
        gateway = BithumbGateway()
        symbol_objs = filter_symbols(gateway.symbols(), config.collector.symbols)

        if not symbol_objs:
            raise DryRunFailed(
                DRY_RUN_STAGE_SYMBOL_RESOLVE,
                f"no symbols resolved for exchange={exchange_name}",
            )

        ws_symbols = [s.name for s in symbol_objs]
        csv = ",".join(ws_symbols)
        n = len(ws_symbols)
        print(f"[dry-run] exchange={exchange_name} symbols=[{csv}] ({n} symbols)")

        # -- WEBSOCKET_HANDSHAKE ----------------------------------------------
        ws_url = config.bithumb.ws_url
        probe_client = BithumbWsClient(symbols=[], ws_url=ws_url)
        try:
            elapsed = await probe_client.probe_handshake()
        except Exception as exc:
            raise DryRunFailed(DRY_RUN_STAGE_WEBSOCKET_HANDSHAKE, str(exc)) from exc

        elapsed_ms = int(round(elapsed))
        print(f"[dry-run] websocket handshake: OK ({ws_url}, {elapsed_ms}ms)")

    print("[dry-run] OK")
