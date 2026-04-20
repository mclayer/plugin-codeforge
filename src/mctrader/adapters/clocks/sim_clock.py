from __future__ import annotations

from mctrader.ports.clock import Clock


class SimClock(Clock):
    def __init__(self) -> None:
        self._ts: int = 0

    def set(self, ts: int) -> None:
        self._ts = ts

    def now(self) -> int:
        return self._ts
