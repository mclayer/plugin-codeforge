from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from mctrader.dashboard.server import create_app


@pytest.fixture()
def client(tmp_path: pytest.TempPathFactory) -> TestClient:
    app = create_app(result_dir=str(tmp_path))
    return TestClient(app)


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
