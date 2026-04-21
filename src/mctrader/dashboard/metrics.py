from __future__ import annotations

import json
import os
from dataclasses import dataclass

import pyarrow.parquet as pq


@dataclass(frozen=True)
class RunMetrics:
    run_id: str
    total_fills: int
    final_equity: float
    realized_pnl: float
    total_return_pct: float | None
    max_drawdown_pct: float
    sharpe_ratio: float | None
    start_ts: int | None
    end_ts: int | None


@dataclass(frozen=True)
class EquityPoint:
    ts: int
    equity: float
    cash: float
    event_count: int


def discover_runs(result_dir: str) -> list[str]:
    """result_dir 하위에서 summary.json이 있는 디렉토리를 run으로 인식."""
    if not os.path.isdir(result_dir):
        return []
    runs = []
    for name in sorted(os.listdir(result_dir), reverse=True):
        path = os.path.join(result_dir, name)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "summary.json")):
            runs.append(name)
    return runs


def load_metrics(result_path: str) -> RunMetrics:
    run_id = os.path.basename(result_path)

    with open(os.path.join(result_path, "summary.json")) as f:
        summary = json.load(f)

    equity_series = load_equity_series(result_path)
    equities = [p.equity for p in equity_series]

    total_return_pct: float | None = None
    if len(equities) >= 2 and equities[0] > 0:
        total_return_pct = round((equities[-1] - equities[0]) / equities[0] * 100, 2)

    return RunMetrics(
        run_id=run_id,
        total_fills=summary.get("total_fills", 0),
        final_equity=float(summary.get("final_equity", 0)),
        realized_pnl=float(summary.get("realized_pnl", 0)),
        total_return_pct=total_return_pct,
        max_drawdown_pct=_compute_mdd(equities),
        sharpe_ratio=_compute_sharpe(equities),
        start_ts=summary.get("start_ts"),
        end_ts=summary.get("end_ts"),
    )


def load_equity_series(result_path: str) -> list[EquityPoint]:
    path = os.path.join(result_path, "equity_curve.parquet")
    if not os.path.exists(path):
        return []
    table = pq.read_table(path)
    if table.num_rows == 0:
        return []
    rows = table.to_pydict()
    return [
        EquityPoint(
            ts=rows["ts"][i],
            equity=float(rows["equity"][i]),
            cash=float(rows["cash"][i]),
            event_count=rows["event_count"][i],
        )
        for i in range(table.num_rows)
    ]


def load_trades(result_path: str) -> list[dict[str, object]]:
    path = os.path.join(result_path, "trades.parquet")
    if not os.path.exists(path):
        return []
    table = pq.read_table(path)
    return list(table.to_pylist())


def _compute_mdd(equities: list[float]) -> float:
    if not equities:
        return 0.0
    peak = equities[0]
    max_dd = 0.0
    for e in equities:
        if e > peak:
            peak = e
        if peak > 0:
            dd = (peak - e) / peak * 100
            if dd > max_dd:
                max_dd = dd
    return round(max_dd, 2)


def _compute_sharpe(equities: list[float]) -> float | None:
    if len(equities) < 3:
        return None
    returns = [
        (equities[i] - equities[i - 1]) / equities[i - 1]
        for i in range(1, len(equities))
        if equities[i - 1] > 0
    ]
    if len(returns) < 2:
        return None
    mean_r = sum(returns) / len(returns)
    variance = sum((r - mean_r) ** 2 for r in returns) / len(returns)
    std_r = variance ** 0.5
    if std_r == 0:
        return None
    return float(round(mean_r / std_r * (len(returns) ** 0.5), 3))
