from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from mctrader.dashboard.metrics import (
    discover_runs,
    load_equity_series,
    load_metrics,
    load_trades,
)

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def create_app(result_dir: str) -> FastAPI:
    app = FastAPI(title="mctrader Dashboard")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

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

    return app
