from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml
from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from mctrader.dashboard.backtest_runner import BacktestRunParams, run_backtest
from mctrader.dashboard.metrics import (
    discover_runs,
    load_equity_series,
    load_metrics,
    load_trades,
)
from mctrader.infra.config import _CONFIG_DIR

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_QUEUE_MODELS = ("naive", "proportional")


# ---------------------------------------------------------------------------
# YAML config helpers
# ---------------------------------------------------------------------------

def _load_config_file(name: str) -> dict[str, Any]:
    path = _CONFIG_DIR / name
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _save_config_file(name: str, data: dict[str, Any]) -> None:
    path = _CONFIG_DIR / name
    with path.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# Background job runner
# ---------------------------------------------------------------------------

def _run_job(job_id: str, params: BacktestRunParams, job_store: dict[str, Any]) -> None:
    job_store[job_id]["status"] = "running"
    try:
        run_id = run_backtest(params)
        job_store[job_id]["status"] = "done"
        job_store[job_id]["result_run_id"] = run_id
    except Exception as exc:
        job_store[job_id]["status"] = "error"
        job_store[job_id]["error"] = str(exc)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(result_dir: str) -> FastAPI:
    app = FastAPI(title="mctrader Dashboard")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    # In-memory job store; reset on process restart
    _job_store: dict[str, Any] = {}

    # -----------------------------------------------------------------------
    # Existing routes
    # -----------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        run_ids = discover_runs(result_dir)
        runs = []
        for run_id in run_ids:
            try:
                runs.append(load_metrics(os.path.join(result_dir, run_id)))
            except Exception:
                pass
        return templates.TemplateResponse(request, "index.html", {"runs": runs})

    @app.get("/run/{run_id}", response_class=HTMLResponse)
    async def run_detail(request: Request, run_id: str) -> HTMLResponse:
        result_path = os.path.join(result_dir, run_id)
        metrics = load_metrics(result_path)
        equity_series = load_equity_series(result_path)
        trades = load_trades(result_path)

        equity_json = json.dumps([
            {"ts": p.ts, "equity": p.equity, "cash": p.cash}
            for p in equity_series
        ])
        return templates.TemplateResponse(request, "run_detail.html", {
            "metrics": metrics,
            "equity_json": equity_json,
            "trades": trades[:200],
        })

    @app.get("/compare", response_class=HTMLResponse)
    async def compare(request: Request, runs: str = "") -> HTMLResponse:
        all_runs = discover_runs(result_dir)
        selected = [r.strip() for r in runs.split(",") if r.strip()] if runs else all_runs[:5]

        series = []
        for run_id in selected:
            try:
                equity = load_equity_series(os.path.join(result_dir, run_id))
                series.append({
                    "run_id": run_id,
                    "data": [{"ts": p.ts, "equity": p.equity} for p in equity],
                })
            except Exception:
                pass

        return templates.TemplateResponse(request, "compare.html", {
            "series_json": json.dumps(series),
            "all_runs": all_runs,
            "selected_runs": selected,
        })

    @app.get("/api/runs")
    async def api_runs() -> JSONResponse:
        run_ids = discover_runs(result_dir)
        result = []
        for run_id in run_ids:
            try:
                result.append(asdict(load_metrics(os.path.join(result_dir, run_id))))
            except Exception:
                pass
        return JSONResponse(result)

    @app.get("/api/run/{run_id}/equity")
    async def api_equity(run_id: str) -> JSONResponse:
        equity = load_equity_series(os.path.join(result_dir, run_id))
        return JSONResponse([{"ts": p.ts, "equity": p.equity, "cash": p.cash} for p in equity])

    @app.get("/api/run/{run_id}/trades")
    async def api_trades(run_id: str) -> JSONResponse:
        trades = load_trades(os.path.join(result_dir, run_id))
        return JSONResponse(trades)

    # -----------------------------------------------------------------------
    # Admin routes
    # -----------------------------------------------------------------------

    @app.get("/admin", response_class=HTMLResponse)
    async def admin_get(request: Request, saved: str = "") -> HTMLResponse:
        cfg = _load_config_file("base.yaml")
        return templates.TemplateResponse(request, "admin.html", {
            "cfg": cfg,
            "saved": saved == "1",
        })

    @app.post("/admin")
    async def admin_post(
        request: Request,
        log_level: str = Form("INFO"),
        log_format: str = Form("json"),
        log_output: str = Form("stdout"),
        log_file_path: str = Form("/var/log/mctrader/app.log"),
        data_root_path: str = Form("/var/data/mctrader"),
        data_orderbook_diff_path: str = Form("orderbook_diff"),
        data_trade_path: str = Form("trade"),
        backtest_initial_cash: str = Form("1000000"),
        backtest_result_path: str = Form("/var/data/mctrader/results"),
        backtest_queue_model: str = Form("naive"),
        backtest_symbols: str = Form("all"),
    ) -> RedirectResponse:
        # Load original to preserve untouched sections (bithumb, collector, etc.)
        original = _load_config_file("base.yaml")
        original["logging"] = {
            "level": log_level,
            "format": log_format,
            "output": log_output,
            "file_path": log_file_path,
        }
        original["data"] = {
            "root_path": data_root_path,
            "orderbook_diff_path": data_orderbook_diff_path,
            "trade_path": data_trade_path,
        }
        original.setdefault("backtest", {}).update({
            "initial_cash": backtest_initial_cash,
            "result_path": backtest_result_path,
            "queue_model": backtest_queue_model,
            "symbols": backtest_symbols,
        })
        _save_config_file("base.yaml", original)
        return RedirectResponse(url="/admin?saved=1", status_code=303)

    # -----------------------------------------------------------------------
    # Backtest UI route
    # -----------------------------------------------------------------------

    @app.get("/backtest", response_class=HTMLResponse)
    async def backtest_get(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "backtest.html", {
            "queue_models": _QUEUE_MODELS,
        })

    # -----------------------------------------------------------------------
    # Backtest API routes
    # -----------------------------------------------------------------------

    @app.post("/api/backtest/run")
    async def api_backtest_run(
        background_tasks: BackgroundTasks,
        symbols: str = Form("all"),
        start_date: str = Form(...),
        end_date: str = Form(...),
        strategy: str = Form(
            "mctrader.strategy.examples.order_imbalance:OrderImbalanceStrategy"
        ),
        queue_model: str = Form("naive"),
        initial_cash: str = Form(""),
    ) -> JSONResponse:
        job_id = uuid.uuid4().hex
        params = BacktestRunParams(
            start_date=start_date,
            end_date=end_date,
            symbols=symbols,
            strategy=strategy,
            queue_model=queue_model,
            initial_cash=initial_cash or None,
        )
        _job_store[job_id] = {"status": "pending", "result_run_id": None, "error": None}
        background_tasks.add_task(_run_job, job_id, params, _job_store)
        return JSONResponse({"job_id": job_id})

    @app.get("/api/backtest/status/{job_id}")
    async def api_backtest_status(job_id: str) -> JSONResponse:
        if job_id not in _job_store:
            return JSONResponse({"error": "job not found"}, status_code=404)
        return JSONResponse(_job_store[job_id])

    return app
