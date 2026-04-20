from __future__ import annotations

from mctrader.ports.clock import Clock


class SimClock(Clock):
    """Simulated clock for backtesting. Timestamp can be manually set."""

    def __init__(self) -> None:
        self._ts: int = 0

    def set(self, ts: int) -> None:
        """Set the current timestamp in milliseconds."""
        self._ts = ts

    def now(self) -> int:
        """Return the current simulated timestamp in milliseconds."""
        return self._ts
