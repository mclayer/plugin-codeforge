from __future__ import annotations

import dataclasses
import json
import os
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mctrader.dashboard.backtest_runner import BacktestRunParams, run_backtest
from mctrader.dashboard.progress_reporter import JobStoreProgressReporter
from mctrader.dashboard.collector_status import build_collector_status, discover_symbols
from mctrader.dashboard.data_query import MAX_ROWS, QueryResult, query
from mctrader.dashboard.views import build_cvd, build_imbalance_series, build_snapshot_view, build_tape
from mctrader.dashboard.metrics import (
    discover_runs,
    load_equity_series,
    load_metrics,
    load_trades,
)
from mctrader.infra.config import _CONFIG_DIR, load_collector_config

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_QUEUE_MODELS = ("naive", "proportional")
_DEFAULT_DATA_ROOT = "./data"
_DATA_TYPES = ("orderbook_diff", "trade")
_SUPPORTED_TZ = {"UTC", "Asia/Seoul"}
_TZ_ABBREV = {"UTC": "UTC", "Asia/Seoul": "KST"}


def _ts_fmt(value: Any, tz_name: str = "UTC") -> str:
    if value is None:
        return "—"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    seconds = v / 1000.0 if v > 1e12 else v
    try:
        if tz_name not in _SUPPORTED_TZ:
            tz_name = "UTC"
        tz = ZoneInfo(tz_name)
        dt = datetime.fromtimestamp(seconds, tz=tz)
    except (OverflowError, OSError, ValueError, ZoneInfoNotFoundError):
        return str(value)
    abbrev = _TZ_ABBREV.get(tz_name, tz_name)
    return dt.strftime("%Y-%m-%d %H:%M:%S") + f" {abbrev}"


def _resolve_data_root() -> str:
    """수집기 설정과 동일한 data.root_path 를 사용해 일관성 유지."""
    try:
        cfg = load_collector_config()
        return cfg.data.root_path
    except Exception:
        return _DEFAULT_DATA_ROOT


def _parse_datetime_local(value: str, tz_name: str = "UTC") -> int | None:
    """'YYYY-MM-DDTHH:MM[SS]' in given timezone -> epoch milliseconds."""
    if not value:
        return None
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        try:
            dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None
    tz = ZoneInfo(tz_name) if tz_name in _SUPPORTED_TZ else ZoneInfo("UTC")
    return int(dt.replace(tzinfo=tz).timestamp() * 1000)


def _default_range(tz_name: str = "UTC") -> tuple[str, str]:
    """Today 00:00 ~ now (minute-truncated) in given timezone for form defaults."""
    tz = ZoneInfo(tz_name) if tz_name in _SUPPORTED_TZ else ZoneInfo("UTC")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    start = now.replace(hour=0, minute=0)
    fmt = "%Y-%m-%dT%H:%M"
    return start.strftime(fmt), now.strftime(fmt)


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
    reporter = JobStoreProgressReporter(job_store=job_store, job_id=job_id)
    try:
        run_id = run_backtest(params, progress_reporter=reporter)
        job_store[job_id]["status"] = "done"
        job_store[job_id]["result_run_id"] = run_id
    except Exception as exc:
        job_store[job_id]["status"] = "error"
        job_store[job_id]["error"] = str(exc)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def _get_tz(request: Request) -> str:
    tz = request.cookies.get("tz", "UTC")
    return tz if tz in _SUPPORTED_TZ else "UTC"


_STATIC_DIR = Path(__file__).parent / "static"


def create_app(result_dir: str) -> FastAPI:
    app = FastAPI(title="mctrader Dashboard")
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    templates.env.filters["ts_fmt"] = _ts_fmt
    templates.env.filters["ts_iso"] = _ts_fmt  # backward compat alias

    # In-memory job store; reset on process restart
    _job_store: dict[str, Any] = {}

    # -----------------------------------------------------------------------
    # Existing routes
    # -----------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        tz = _get_tz(request)
        run_ids = discover_runs(result_dir)
        runs = []
        for run_id in run_ids:
            try:
                runs.append(load_metrics(os.path.join(result_dir, run_id)))
            except Exception:
                pass
        return templates.TemplateResponse(request, "index.html", {"runs": runs, "tz": tz})

    @app.get("/run/{run_id}", response_class=HTMLResponse)
    async def run_detail(request: Request, run_id: str) -> HTMLResponse:
        tz = _get_tz(request)
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
            "tz": tz,
        })

    @app.get("/compare", response_class=HTMLResponse)
    async def compare(request: Request, runs: str = "") -> HTMLResponse:
        tz = _get_tz(request)
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
            "tz": tz,
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
        tz = _get_tz(request)
        cfg = _load_config_file("base.yaml")
        return templates.TemplateResponse(request, "admin.html", {
            "cfg": cfg,
            "saved": saved == "1",
            "tz": tz,
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
        tz = _get_tz(request)
        tz_abbrev = _TZ_ABBREV.get(tz, tz)
        return templates.TemplateResponse(request, "backtest.html", {
            "queue_models": _QUEUE_MODELS,
            "tz": tz,
            "tz_abbrev": tz_abbrev,
        })

    # -----------------------------------------------------------------------
    # Backtest API routes
    # -----------------------------------------------------------------------

    @app.post("/api/backtest/run")
    async def api_backtest_run(
        request: Request,
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
        tz = _get_tz(request)
        job_id = uuid.uuid4().hex
        params = BacktestRunParams(
            start_date=start_date,
            end_date=end_date,
            symbols=symbols,
            strategy=strategy,
            queue_model=queue_model,
            initial_cash=initial_cash or None,
            tz=tz,
        )
        _planned = [] if params.symbols.strip().lower() == "all" else [
            s.strip() for s in params.symbols.split(",") if s.strip()
        ]
        _job_store[job_id] = {
            "status": "pending",
            "result_run_id": None,
            "error": None,
            "progress": {
                "phase": "queued",
                "progress_pct": 0.0,
                "current_symbol": None,
                "planned_symbols": _planned,
                "current_ts": None,
                "start_ts": None,
                "end_ts": None,
                "event_count": 0,
                "total_fills": 0,
                "error": None,
            },
        }
        background_tasks.add_task(_run_job, job_id, params, _job_store)
        return JSONResponse({"job_id": job_id})

    @app.get("/api/backtest/status/{job_id}")
    async def api_backtest_status(job_id: str) -> JSONResponse:
        if job_id not in _job_store:
            return JSONResponse({"error": "job not found"}, status_code=404)
        return JSONResponse(_job_store[job_id])

    # -----------------------------------------------------------------------
    # Collector status routes
    # -----------------------------------------------------------------------

    @app.get("/collector", response_class=HTMLResponse)
    async def collector_page(request: Request) -> HTMLResponse:
        tz = _get_tz(request)
        data_root = _resolve_data_root()
        status = build_collector_status(data_root)
        return templates.TemplateResponse(request, "collector.html", {
            "status": status,
            "tz": tz,
        })

    @app.get("/api/collector/status")
    async def api_collector_status() -> JSONResponse:
        data_root = _resolve_data_root()
        status = build_collector_status(data_root)
        return JSONResponse({
            "process": {
                "running": status.process.running,
                "pid": status.process.pid,
                "cmdline": status.process.cmdline,
                "detection": status.process.detection,
            },
            "data_root": status.data_root,
            "today": status.today,
            "symbols": [
                {
                    "symbol": s.symbol,
                    "orderbook_row_count": s.orderbook_row_count,
                    "trade_count": s.trade_count,
                    "last_orderbook_ts": s.last_orderbook_ts,
                    "last_trade_ts": s.last_trade_ts,
                    "last_received_ts": s.last_received_ts,
                }
                for s in status.symbols
            ],
            "today_files": [
                {
                    "event_type": f.event_type,
                    "symbol": f.symbol,
                    "hour": f.hour,
                    "file_name": f.file_name,
                    "rel_path": f.rel_path,
                    "size_bytes": f.size_bytes,
                    "mtime_ts": f.mtime_ts,
                }
                for f in status.today_files
            ],
        })

    # -----------------------------------------------------------------------
    # Data query routes
    # -----------------------------------------------------------------------

    @app.get("/data", response_class=HTMLResponse)
    async def data_page(
        request: Request,
        symbol: str = "",
        event_type: str = "orderbook_diff",
        start: str = "",
        end: str = "",
    ) -> HTMLResponse:
        tz = _get_tz(request)
        data_root = _resolve_data_root()
        symbols = discover_symbols(data_root)

        default_start, default_end = _default_range(tz)
        selected = {
            "symbol": symbol or (symbols[0] if symbols else ""),
            "event_type": event_type if event_type in _DATA_TYPES else "orderbook_diff",
            "start": start or default_start,
            "end": end or default_end,
        }

        result: QueryResult | None = None
        error: str | None = None

        # 파라미터가 모두 들어왔을 때만 조회 (초기 진입 시 빈 상태)
        if symbol and start and end and symbols:
            start_ts = _parse_datetime_local(start, tz)
            end_ts = _parse_datetime_local(end, tz)
            if start_ts is None or end_ts is None:
                error = "Invalid datetime format."
            elif start_ts > end_ts:
                error = "Start must be before end."
            else:
                try:
                    result = query(
                        data_root=data_root,
                        event_type=selected["event_type"],  # type: ignore[arg-type]
                        symbol=symbol,
                        start_ts=start_ts,
                        end_ts=end_ts,
                        limit=MAX_ROWS,
                    )
                except Exception as exc:  # pragma: no cover - surface in UI
                    error = f"Query failed: {exc}"

        return templates.TemplateResponse(request, "data.html", {
            "symbols": symbols,
            "selected": selected,
            "result": result,
            "error": error,
            "max_rows": MAX_ROWS,
            "data_root": data_root,
            "tz": tz,
        })

    @app.get("/api/data/query")
    async def api_data_query(
        symbol: str,
        event_type: str = "orderbook_diff",
        start: str = "",
        end: str = "",
    ) -> JSONResponse:
        if event_type not in _DATA_TYPES:
            return JSONResponse({"error": "invalid event_type"}, status_code=400)
        start_ts = _parse_datetime_local(start)
        end_ts = _parse_datetime_local(end)
        if start_ts is None or end_ts is None:
            return JSONResponse({"error": "invalid datetime"}, status_code=400)

        data_root = _resolve_data_root()
        result = query(
            data_root=data_root,
            event_type=event_type,  # type: ignore[arg-type]
            symbol=symbol,
            start_ts=start_ts,
            end_ts=end_ts,
            limit=MAX_ROWS,
        )
        return JSONResponse({
            "total_count": result.total_count,
            "returned_count": result.returned_count,
            "truncated": result.truncated,
            "rows": result.rows,
        })

    # -----------------------------------------------------------------------
    # OrderBook / Trade microstructure API routes
    # -----------------------------------------------------------------------

    @app.get("/api/data/orderbook/snapshot")
    async def api_orderbook_snapshot(
        symbol: str,
        market: str = "bithumb",
        ts: int = 0,
        depth: int = 20,
        imbalance_depth: int = 5,
    ) -> JSONResponse:
        if not symbol:
            raise HTTPException(400, "symbol required")
        data_root = _resolve_data_root()
        as_of = ts if ts > 0 else int(time.time() * 1000)
        view = build_snapshot_view(data_root, symbol, market, as_of, depth, imbalance_depth)
        return JSONResponse(dataclasses.asdict(view))

    @app.get("/api/data/orderbook/imbalance-series")
    async def api_imbalance_series(
        symbol: str,
        market: str = "bithumb",
        start_ts: int = 0,
        end_ts: int = 0,
        bucket_ms: int = 250,
        imbalance_depth: int = 5,
    ) -> JSONResponse:
        if not symbol:
            raise HTTPException(400, "symbol required")
        data_root = _resolve_data_root()
        effective_end = end_ts if end_ts > 0 else int(time.time() * 1000)
        points = build_imbalance_series(
            data_root, symbol, market, start_ts, effective_end, bucket_ms, imbalance_depth
        )
        return JSONResponse([dataclasses.asdict(p) for p in points])

    @app.get("/api/data/trades/tape")
    async def api_trades_tape(
        symbol: str,
        market: str = "bithumb",
        start_ts: int = 0,
        end_ts: int = 0,
        limit: int = 500,
    ) -> JSONResponse:
        if not symbol:
            raise HTTPException(400, "symbol required")
        data_root = _resolve_data_root()
        effective_end = end_ts if end_ts > 0 else int(time.time() * 1000)
        entries = build_tape(data_root, symbol, market, start_ts, effective_end, limit)
        return JSONResponse([dataclasses.asdict(e) for e in entries])

    @app.get("/api/data/trades/cvd")
    async def api_trades_cvd(
        symbol: str,
        market: str = "bithumb",
        start_ts: int = 0,
        end_ts: int = 0,
    ) -> JSONResponse:
        if not symbol:
            raise HTTPException(400, "symbol required")
        data_root = _resolve_data_root()
        effective_end = end_ts if end_ts > 0 else int(time.time() * 1000)
        points = build_cvd(data_root, symbol, market, start_ts, effective_end)
        return JSONResponse([dataclasses.asdict(p) for p in points])

    return app
