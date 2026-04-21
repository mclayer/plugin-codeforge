from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

Phase = Literal["queued", "preparing", "replaying", "finalizing", "done", "error"]


@dataclass(frozen=True)
class ProgressEvent:
    phase: Phase
    progress_pct: float
    current_symbol: str | None
    planned_symbols: tuple[str, ...]
    current_ts: int | None
    start_ts: int | None
    end_ts: int | None
    event_count: int
    total_fills: int
    error: str | None = None


class ProgressReporter(ABC):
    @abstractmethod
    def report(self, event: ProgressEvent) -> None: ...


class NoopProgressReporter(ProgressReporter):
    def report(self, event: ProgressEvent) -> None:
        return
