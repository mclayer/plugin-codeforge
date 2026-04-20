from __future__ import annotations

import time

from mctrader.ports.clock import Clock


class WallClock(Clock):
    """System wall clock. Returns current time in milliseconds since Unix epoch."""

    def now(self) -> int:
        """Return current system time in milliseconds since Unix epoch."""
        return time.time_ns() // 1_000_000
