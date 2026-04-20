from __future__ import annotations

import time

from mctrader.ports.clock import Clock


class WallClock(Clock):
    def now(self) -> int:
        return time.time_ns() // 1_000_000
