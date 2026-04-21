"""Unit tests for infra/config.py — _deep_merge and env override logic."""
from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

from mctrader.infra.config import (
    BacktestConfig,
    _deep_merge,
    load_backtest_config,
    load_collector_config,
)


class TestDeepMerge:
    def test_base_values_are_preserved(self) -> None:
        base = {"a": 1, "b": 2}
        override: dict[str, Any] = {}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 2}

    def test_override_values_replace_base(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 99}
        result = _deep_merge(base, override)
        assert result["b"] == 99
        assert result["a"] == 1

    def test_new_keys_in_override_are_added(self) -> None:
        base = {"a": 1}
        override = {"b": 2}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 2}

    def test_nested_dicts_are_merged_recursively(self) -> None:
        base = {"data": {"root_path": "/old", "trade_path": "trade"}}
        override = {"data": {"root_path": "/new"}}
        result = _deep_merge(base, override)
        # root_path is overridden, trade_path is preserved from base
        assert result["data"]["root_path"] == "/new"
        assert result["data"]["trade_path"] == "trade"

    def test_non_dict_value_overrides_dict(self) -> None:
        base = {"nested": {"a": 1}}
        override = {"nested": "flat"}
        result = _deep_merge(base, override)
        assert result["nested"] == "flat"

    def test_empty_base_with_override(self) -> None:
        result = _deep_merge({}, {"key": "val"})
        assert result == {"key": "val"}

    def test_empty_both(self) -> None:
        result = _deep_merge({}, {})
        assert result == {}

    def test_deep_nested_merge(self) -> None:
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"c": 99}}}
        result = _deep_merge(base, override)
        assert result["a"]["b"]["c"] == 99
        assert result["a"]["b"]["d"] == 2  # preserved from base

    def test_base_is_not_mutated(self) -> None:
        base = {"a": 1, "nested": {"x": 10}}
        override = {"a": 2, "nested": {"x": 20}}
        _deep_merge(base, override)
        # original base should remain unchanged
        assert base["a"] == 1
        assert base["nested"]["x"] == 10


class TestEnvOverrides:
    def test_mctrader_data_root_env_overrides_data_root_path(self) -> None:
        """MCTRADER_DATA_ROOT 환경변수가 data.root_path를 덮어써야 한다."""
        with patch.dict(os.environ, {"MCTRADER_DATA_ROOT": "/custom/data"}):
            config = load_backtest_config()
        assert config.data.root_path == "/custom/data"

    def test_mctrader_log_level_env_overrides_logging_level(self) -> None:
        """MCTRADER_LOG_LEVEL 환경변수가 logging.level을 덮어써야 한다."""
        with patch.dict(os.environ, {"MCTRADER_LOG_LEVEL": "DEBUG"}):
            config = load_backtest_config()
        assert config.logging.level == "DEBUG"

    def test_no_env_vars_uses_config_defaults(self) -> None:
        """환경변수 없이 기본 YAML 설정값이 로드되어야 한다."""
        env_without_overrides = {
            k: v for k, v in os.environ.items()
            if k not in ("MCTRADER_DATA_ROOT", "MCTRADER_LOG_LEVEL")
        }
        with patch.dict(os.environ, env_without_overrides, clear=True):
            config = load_backtest_config()
        # base.yaml has /var/data/mctrader as default
        assert config.data.root_path == "/var/data/mctrader"
        assert config.logging.level == "INFO"


class TestLoadBacktestConfig:
    def test_returns_backtest_config_dataclass(self) -> None:
        config = load_backtest_config()
        assert isinstance(config, BacktestConfig)

    def test_backtest_field_initial_cash_is_string(self) -> None:
        config = load_backtest_config()
        # initial_cash은 Decimal 변환을 위해 문자열이어야 함
        assert isinstance(config.backtest.initial_cash, str)

    def test_backtest_queue_model_default(self) -> None:
        config = load_backtest_config()
        assert config.backtest.queue_model in ("naive", "proportional")

    def test_exchange_default_is_bithumb(self) -> None:
        config = load_backtest_config()
        assert config.exchange.default == "bithumb"

    def test_logging_output_is_stdout_or_file(self) -> None:
        config = load_backtest_config()
        assert config.logging.output in ("stdout", "file", "both")


class TestLoadCollectorConfig:
    def test_bithumb_ws_url_is_set(self) -> None:
        """collector.yaml의 bithumb.ws_url 필드가 로드되어야 한다."""
        config = load_collector_config()
        # ws_url은 None이거나 빈 문자열일 수 있음 — 존재 여부만 확인
        assert hasattr(config.bithumb, "ws_url")

    def test_collector_flush_interval_is_positive(self) -> None:
        config = load_collector_config()
        assert config.collector.flush_interval_sec > 0

    def test_collector_reconnect_interval_is_positive(self) -> None:
        config = load_collector_config()
        assert config.collector.reconnect_interval_sec > 0
