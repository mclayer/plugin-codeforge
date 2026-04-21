from __future__ import annotations

import pytest

from mctrader.dashboard.backtest_runner import (
    BacktestRunParams,
    _date_to_epoch_ms,
    _import_strategy_class,
    _parse_symbols,
)


class TestDateToEpochMs:
    def test_known_date(self) -> None:
        # 2024-01-01 UTC midnight = 1704067200000 ms
        assert _date_to_epoch_ms("2024-01-01") == 1_704_067_200_000

    def test_returns_int(self) -> None:
        result = _date_to_epoch_ms("2023-06-15")
        assert isinstance(result, int)

    def test_epoch_origin(self) -> None:
        # 1970-01-01 UTC = 0 ms
        assert _date_to_epoch_ms("1970-01-01") == 0


class TestParseSymbols:
    def test_all_returns_none(self) -> None:
        assert _parse_symbols("all") is None

    def test_all_case_insensitive(self) -> None:
        assert _parse_symbols("ALL") is None
        assert _parse_symbols("All") is None

    def test_all_with_whitespace(self) -> None:
        assert _parse_symbols("  all  ") is None

    def test_single_symbol(self) -> None:
        result = _parse_symbols("BTC_KRW")
        assert result == ["BTC_KRW"]

    def test_multiple_symbols(self) -> None:
        result = _parse_symbols("BTC_KRW,ETH_KRW")
        assert result == ["BTC_KRW", "ETH_KRW"]

    def test_strips_whitespace_around_symbols(self) -> None:
        result = _parse_symbols("BTC_KRW , ETH_KRW")
        assert result == ["BTC_KRW", "ETH_KRW"]

    def test_empty_string_returns_empty_list(self) -> None:
        result = _parse_symbols("")
        assert result == []


class TestImportStrategyClass:
    def test_invalid_spec_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="module:ClassName"):
            _import_strategy_class("no_colon_here")

    def test_valid_spec_imports_class(self) -> None:
        # Use a stdlib class as an easy target
        cls = _import_strategy_class("pathlib:Path")
        from pathlib import Path
        assert cls is Path

    def test_nonexistent_module_raises(self) -> None:
        with pytest.raises((ImportError, ModuleNotFoundError)):
            _import_strategy_class("nonexistent.module.xyz:SomeClass")

    def test_nonexistent_class_raises(self) -> None:
        with pytest.raises(AttributeError):
            _import_strategy_class("pathlib:NonExistentClass999")


class TestBacktestRunParams:
    def test_all_fields_assignable(self) -> None:
        params = BacktestRunParams(
            start_date="2024-01-01",
            end_date="2024-03-31",
            symbols="all",
            strategy="module:Class",
            queue_model="naive",
            initial_cash=None,
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-03-31"
        assert params.symbols == "all"
        assert params.strategy == "module:Class"
        assert params.queue_model == "naive"
        assert params.initial_cash is None

    def test_initial_cash_can_be_string(self) -> None:
        params = BacktestRunParams(
            start_date="2024-01-01",
            end_date="2024-03-31",
            symbols="BTC_KRW",
            strategy="module:Class",
            queue_model="proportional",
            initial_cash="5000000",
        )
        assert params.initial_cash == "5000000"
