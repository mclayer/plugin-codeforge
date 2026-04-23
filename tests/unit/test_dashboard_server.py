from __future__ import annotations

import os
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from fastapi.testclient import TestClient

from mctrader.dashboard.server import _ts_fmt, create_app


@pytest.fixture()
def client(tmp_path: pytest.TempPathFactory):
    app = create_app(result_dir=str(tmp_path))
    # lifespan(init_duckdb/close_duckdb)을 실행하려면 컨텍스트 매니저 형태로 사용해야 한다.
    with TestClient(app) as c:
        yield c


def _write_sample_orderbook(data_root: str) -> None:
    schema = pa.schema([
        ("ts", pa.int64()),
        ("seq", pa.int64()),
        ("symbol", pa.string()),
        ("market", pa.string()),
        ("side", pa.string()),
        ("price", pa.string()),
        ("qty", pa.string()),
    ])
    rows = [{
        "ts": 1776700000000, "seq": 1, "symbol": "BTC_KRW", "market": "bithumb",
        "side": "bid", "price": "100", "qty": "1",
    }]
    path = os.path.join(
        data_root, "orderbook_diff", "symbol=BTC_KRW", "date=2026-04-21",
        "hour=00_001.parquet",
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows, schema=schema), path)


class TestAdminGet:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/admin")
        assert response.status_code == 200

    def test_contains_form(self, client: TestClient) -> None:
        response = client.get("/admin")
        assert b"<form" in response.content


class TestBacktestGet:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/backtest")
        assert response.status_code == 200

    def test_contains_form(self, client: TestClient) -> None:
        response = client.get("/backtest")
        assert b"<form" in response.content


class TestBacktestStatusNonexistent:
    def test_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/backtest/status/nonexistent_job_id")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestBacktestRun:
    def test_returns_job_id(self, client: TestClient) -> None:
        with patch("mctrader.dashboard.server.run_backtest", return_value="run_001"):
            response = client.post(
                "/api/backtest/run",
                data={
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                    "symbols": "all",
                    "strategy": "pathlib:Path",
                    "queue_model": "naive",
                    "initial_cash": "",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert isinstance(data["job_id"], str)
        assert len(data["job_id"]) == 32  # uuid4().hex

    def test_job_appears_in_store(self, client: TestClient) -> None:
        """After POST, job_id is visible via status endpoint."""
        with patch("mctrader.dashboard.server.run_backtest", return_value="run_001"):
            post_resp = client.post(
                "/api/backtest/run",
                data={
                    "start_date": "2024-01-01",
                    "end_date": "2024-03-31",
                },
            )
        job_id = post_resp.json()["job_id"]
        # Status endpoint must not return 404 for this job
        status_resp = client.get(f"/api/backtest/status/{job_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert "status" in status_data
        assert status_data["status"] in ("pending", "running", "done", "error")


class TestCollectorPage:
    def test_get_returns_200(self, tmp_path, client: TestClient) -> None:
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get("/collector")
        assert r.status_code == 200
        assert b"Collector Status" in r.content

    def test_api_status_returns_expected_keys(self, tmp_path, client: TestClient) -> None:
        _write_sample_orderbook(str(tmp_path))
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get("/api/collector/status")
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {
            "process", "data_root", "today", "symbols", "today_files",
        }
        assert any(s["symbol"] == "BTC_KRW" for s in body["symbols"])


class TestDataPage:
    def test_get_without_params_returns_200(self, tmp_path, client: TestClient) -> None:
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get("/data")
        assert r.status_code == 200
        assert b"Data Query" in r.content

    def test_get_with_params_returns_rows(self, tmp_path, client: TestClient) -> None:
        _write_sample_orderbook(str(tmp_path))
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get(
                "/data",
                params={
                    "symbol": "BTC_KRW",
                    "event_type": "orderbook_diff",
                    "start": "2026-04-20T00:00",
                    "end": "2026-04-21T23:59",
                },
            )
        assert r.status_code == 200
        # row price 문자열이 HTML 에 표시
        assert b"100" in r.content

    def test_api_data_query_returns_rows(self, tmp_path, client: TestClient) -> None:
        _write_sample_orderbook(str(tmp_path))
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get(
                "/api/data/query",
                params={
                    "symbol": "BTC_KRW",
                    "event_type": "orderbook_diff",
                    "start": "2026-04-20T00:00",
                    "end": "2026-04-21T23:59",
                },
            )
        assert r.status_code == 200
        body = r.json()
        # total_count는 LIMIT+1 기법 도입으로 None 반환
        assert body["total_count"] is None
        assert body["returned_count"] >= 1

    def test_api_data_query_rejects_invalid_type(self, client: TestClient) -> None:
        r = client.get(
            "/api/data/query",
            params={
                "symbol": "BTC_KRW",
                "event_type": "bogus",
                "start": "2026-04-21T00:00",
                "end": "2026-04-21T23:59",
            },
        )
        assert r.status_code == 400


class TestNavigation:
    def test_index_has_new_links(self, client: TestClient) -> None:
        r = client.get("/")
        assert r.status_code == 200
        assert b'href="/collector"' in r.content
        assert b'href="/data"' in r.content


class TestTsFmt:
    # 2025-04-21 00:00:00 UTC = 1745193600000 ms
    _TS_MS = 1745193600000

    def test_utc_format(self) -> None:
        result = _ts_fmt(self._TS_MS, "UTC")
        assert result == "2025-04-21 00:00:00 UTC"

    def test_kst_offset(self) -> None:
        # KST = UTC+9, so same instant is 2025-04-21 09:00:00
        result = _ts_fmt(self._TS_MS, "Asia/Seoul")
        assert result == "2025-04-21 09:00:00 KST"

    def test_none_returns_dash(self) -> None:
        assert _ts_fmt(None) == "—"

    def test_invalid_tz_falls_back_to_utc(self) -> None:
        result = _ts_fmt(self._TS_MS, "Invalid/Zone")
        assert result.endswith("UTC")

    def test_seconds_epoch_also_works(self) -> None:
        # Values <= 1e12 are treated as seconds
        result = _ts_fmt(1745193600.0, "UTC")
        assert result == "2025-04-21 00:00:00 UTC"


class TestTzCookie:
    def test_navbar_shows_utc_by_default(self, client: TestClient) -> None:
        r = client.get("/")
        assert r.status_code == 200
        assert b"UTC" in r.content

    def test_navbar_shows_kst_when_cookie_set(self, client: TestClient) -> None:
        r = client.get("/", cookies={"tz": "Asia/Seoul"})
        assert r.status_code == 200
        assert b"Asia/Seoul" in r.content

    def test_invalid_tz_cookie_falls_back_to_utc(self, client: TestClient) -> None:
        r = client.get("/", cookies={"tz": "Evil/Zone"})
        assert r.status_code == 200
        assert b"UTC" in r.content

    def test_collector_shows_tz_in_header(self, tmp_path, client: TestClient) -> None:
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get("/collector", cookies={"tz": "Asia/Seoul"})
        assert r.status_code == 200
        assert b"KST" in r.content

    def test_data_page_shows_tz_column_header(self, tmp_path, client: TestClient) -> None:
        with patch(
            "mctrader.dashboard.server._resolve_data_root",
            return_value=str(tmp_path),
        ):
            r = client.get("/data", cookies={"tz": "Asia/Seoul"})
        assert r.status_code == 200
        assert b"Asia/Seoul" in r.content
