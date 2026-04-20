from __future__ import annotations

import enum
from dataclasses import dataclass, field

from mctrader.domain.symbol import Symbol


class SignalDirection(enum.Enum):
    LONG = "long"
    SHORT = "short"
    CLOSE = "close"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class Signal:
    symbol: Symbol
    direction: SignalDirection
    strength: float  # 0.0 ~ 1.0
    ts: int
    metadata: dict[str, object] = field(default_factory=dict)
