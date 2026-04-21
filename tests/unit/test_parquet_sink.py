"""Unit tests for ParquetSink — flush 파일명 중복 방지 검증."""
from __future__ import annotations

import os
import tempfile
from decimal import Decimal
from unittest.mock import patch

from mctrader.adapters.storage.parquet_sink import ParquetSink, _parquet_path
from mctrader.domain.events import OrderBookDiffEvent, TradeEvent
from mctrader.domain.symbol import Market, Symbol

SYMBOL = Symbol(base="BTC", quote="KRW", market=Market.BITHUMB)

# 2024-04-25 00:00:00 UTC (epoch ms)
_TS_MS = 1714003200000


def _orderbook_diff(ts: int = _TS_MS) -> OrderBookDiffEvent:
    return OrderBookDiffEvent(
        symbol=SYMBOL,
        ts=ts,
        seq=1,
        bids_delta=((Decimal("100"), Decimal("1")),),
        asks_delta=((Decimal("101"), Decimal("0.5")),),
    )


def _trade(ts: int = _TS_MS) -> TradeEvent:
    return TradeEvent(
        symbol=SYMBOL,
        ts=ts,
        seq=1,
        price=Decimal("100"),
        qty=Decimal("1"),
        side="buy",
    )


class TestParquetPathFlushTimestamp:
    """_parquet_path 헬퍼가 flush_ts_ms를 파일명에 포함하는지 확인."""

    def test_filename_contains_flush_ts_ms(self) -> None:
        key = "orderbook_diff/BTC_KRW/2024-04-25/00"
        path = _parquet_path("/data", key, flush_ts_ms=1714000000000)
        filename = os.path.basename(path)
        assert "1714000000000" in filename
        assert filename == "hour=00_1714000000000.parquet"

    def test_different_flush_ts_ms_produces_different_paths(self) -> None:
        key = "orderbook_diff/BTC_KRW/2024-04-25/00"
        path1 = _parquet_path("/data", key, flush_ts_ms=1714000000000)
        path2 = _parquet_path("/data", key, flush_ts_ms=1714000060000)
        assert path1 != path2

    def test_same_flush_ts_ms_produces_same_path(self) -> None:
        key = "orderbook_diff/BTC_KRW/2024-04-25/00"
        path1 = _parquet_path("/data", key, flush_ts_ms=1714000000000)
        path2 = _parquet_path("/data", key, flush_ts_ms=1714000000000)
        assert path1 == path2


class TestFlushNoDuplication:
    """동일 hour 파티션에 재플러시 시 이전 파일을 덮어쓰지 않고 새 파일을 생성."""

    def test_two_flushes_create_two_distinct_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sink = ParquetSink(
                root_path=tmpdir,
                flush_interval_sec=9999,  # 자동 플러시 비활성화
                flush_max_mb=9999,
            )

            # 1차 플러시
            sink.write_orderbook_diff(_orderbook_diff())
            with patch("mctrader.adapters.storage.parquet_sink.time") as mock_time:
                mock_time.time.return_value = 1714000000.0
                mock_time.monotonic.return_value = 0.0
                sink.flush()

            # 2차 플러시 (같은 hour 파티션, 다른 timestamp)
            sink.write_orderbook_diff(_orderbook_diff())
            with patch("mctrader.adapters.storage.parquet_sink.time") as mock_time:
                mock_time.time.return_value = 1714000060.0
                mock_time.monotonic.return_value = 60.0
                sink.flush()

            # 두 parquet 파일이 서로 다른 이름으로 존재해야 한다
            written_files = []
            for dirpath, _, filenames in os.walk(tmpdir):
                for fname in filenames:
                    if fname.endswith(".parquet"):
                        written_files.append(fname)

            assert len(written_files) == 2, (
                f"플러시 2회에 파일 2개가 생성돼야 하지만 {len(written_files)}개: {written_files}"
            )
            assert written_files[0] != written_files[1]

    def test_flush_file_contains_correct_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sink = ParquetSink(root_path=tmpdir, flush_interval_sec=9999, flush_max_mb=9999)
            sink.write_orderbook_diff(_orderbook_diff())

            fixed_ts_ms = 1714003200123
            with patch("mctrader.adapters.storage.parquet_sink.time") as mock_time:
                mock_time.time.return_value = fixed_ts_ms / 1000
                mock_time.monotonic.return_value = 0.0
                sink.flush()

            written_files = []
            for dirpath, _, filenames in os.walk(tmpdir):
                for fname in filenames:
                    if fname.endswith(".parquet"):
                        written_files.append(fname)

            assert len(written_files) == 1
            assert str(fixed_ts_ms) in written_files[0]


class TestFlushTradeEvent:
    """TradeEvent도 flush_ts_ms 기반 파일명으로 저장되는지 확인."""

    def test_trade_flush_creates_timestamped_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sink = ParquetSink(root_path=tmpdir, flush_interval_sec=9999, flush_max_mb=9999)
            sink.write_trade(_trade())

            fixed_ts_ms = 1714000000999
            with patch("mctrader.adapters.storage.parquet_sink.time") as mock_time:
                mock_time.time.return_value = fixed_ts_ms / 1000
                mock_time.monotonic.return_value = 0.0
                sink.flush()

            written_files = []
            for dirpath, _, filenames in os.walk(tmpdir):
                for fname in filenames:
                    if fname.endswith(".parquet"):
                        written_files.append(fname)

            assert len(written_files) == 1
            assert str(fixed_ts_ms) in written_files[0]
