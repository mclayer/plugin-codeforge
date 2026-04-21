from __future__ import annotations

import time
from typing import Any

from mctrader.ports.progress import ProgressEvent, ProgressReporter


class JobStoreProgressReporter(ProgressReporter):
    def __init__(
        self,
        job_store: dict[str, Any],
        job_id: str,
        throttle_ms: float = 500.0,
    ) -> None:
        self._job_store = job_store
        self._job_id = job_id
        self._throttle_ms = throttle_ms
        self._last_flush: float = float("-inf")
        self._last_phase: str = ""

    def report(self, event: ProgressEvent) -> None:
        now = time.monotonic()
        phase_changed = event.phase != self._last_phase
        elapsed_ms = (now - self._last_flush) * 1000
        if not phase_changed and elapsed_ms < self._throttle_ms:
            return
        self._job_store[self._job_id]["progress"] = {
            "phase": event.phase,
            "progress_pct": round(event.progress_pct, 1),
            "current_symbol": event.current_symbol,
            "planned_symbols": list(event.planned_symbols),
            "current_ts": event.current_ts,
            "start_ts": event.start_ts,
            "end_ts": event.end_ts,
            "event_count": event.event_count,
            "total_fills": event.total_fills,
            "error": event.error,
        }
        self._last_flush = now
        self._last_phase = event.phase
