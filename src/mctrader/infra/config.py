from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# resolve config/ relative to the package root (src/mctrader/ -> project root)
_CONFIG_DIR = Path(__file__).parents[3] / "config"


@dataclass
class LoggingConfig:
    level: str
    format: str
    output: str
    file_path: str


@dataclass
class DataConfig:
    root_path: str
    orderbook_diff_path: str
    trade_path: str


@dataclass
class ExchangeConfig:
    default: str


@dataclass
class BithumbConfig:
    ws_url: str


@dataclass
class CollectorServiceConfig:
    reconnect_interval_sec: int
    flush_interval_sec: int
    flush_max_mb: int
    symbols: str | list[str]
    orderbook_levels: int


@dataclass
class BacktestServiceConfig:
    initial_cash: str
    start_ts: int | None
    end_ts: int | None
    symbols: str | list[str]
    result_path: str
    queue_model: str


@dataclass
class CollectorConfig:
    logging: LoggingConfig
    data: DataConfig
    exchange: ExchangeConfig
    collector: CollectorServiceConfig
    bithumb: BithumbConfig


@dataclass
class BacktestConfig:
    logging: LoggingConfig
    data: DataConfig
    exchange: ExchangeConfig
    backtest: BacktestServiceConfig


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def _apply_env_overrides(cfg: dict[str, Any]) -> None:
    data_root = os.environ.get("MCTRADER_DATA_ROOT")
    if data_root:
        cfg.setdefault("data", {})["root_path"] = data_root

    log_level = os.environ.get("MCTRADER_LOG_LEVEL")
    if log_level:
        cfg.setdefault("logging", {})["level"] = log_level


def _merged(service_yaml: str) -> dict[str, Any]:
    base = _load_yaml(_CONFIG_DIR / "base.yaml")
    service = _load_yaml(_CONFIG_DIR / service_yaml)
    cfg = _deep_merge(base, service)
    _apply_env_overrides(cfg)
    return cfg


def load_collector_config() -> CollectorConfig:
    cfg = _merged("collector.yaml")

    logging_cfg = LoggingConfig(**cfg["logging"])
    data_cfg = DataConfig(**cfg["data"])
    exchange_cfg = ExchangeConfig(**cfg["exchange"])
    collector_cfg = CollectorServiceConfig(**cfg["collector"])
    bithumb_cfg = BithumbConfig(**cfg["bithumb"])

    return CollectorConfig(
        logging=logging_cfg,
        data=data_cfg,
        exchange=exchange_cfg,
        collector=collector_cfg,
        bithumb=bithumb_cfg,
    )


def load_backtest_config() -> BacktestConfig:
    cfg = _merged("backtest.yaml")

    logging_cfg = LoggingConfig(**cfg["logging"])
    data_cfg = DataConfig(**cfg["data"])
    exchange_cfg = ExchangeConfig(**cfg["exchange"])
    backtest_cfg = BacktestServiceConfig(**cfg["backtest"])

    return BacktestConfig(
        logging=logging_cfg,
        data=data_cfg,
        exchange=exchange_cfg,
        backtest=backtest_cfg,
    )
