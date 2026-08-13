#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""gate_verdict.py — CFP-2926 신규 게이트 21종 공유 3-state verdict + execution-trace emit 헬퍼.

CFP-2926 / ADR-154 §결정 2·3 (3-way taxonomy 사상 — 신규 taxonomy 발명 아님)

책임:
    - PASS / RED / INCONCLUSIVE 3-state verdict 값 객체(GateResult) + exit code 매핑.
    - INCONCLUSIVE 는 절대 GREEN(exit 0) 이 아니다 — non-GREEN unknown 상태를 exit 0 으로
      흡수하는 경로를 만들지 않는다 ([154-AC-3]).
    - unknown-input 은 fail-closed RED 로 사상한다 ([154-AC-4]).
    - trace(검사 대상 수 등 numeric — [154-AC-5])·identity_probe(resolved-target echo —
      [154-AC-13]) 를 verdict 와 함께 단일 라인 JSON 으로 emit.

외부 의존 0 — 표준 라이브러리(json, sys, typing)만 사용.
"""

import json
import sys
from typing import Optional

PASS = "PASS"
RED = "RED"
INCONCLUSIVE = "INCONCLUSIVE"

_VALID_VERDICTS = (PASS, RED, INCONCLUSIVE)

EXIT_PASS = 0
EXIT_RED = 1
EXIT_INCONCLUSIVE = 3

EXIT_BY_VERDICT = {
    PASS: EXIT_PASS,
    RED: EXIT_RED,
    INCONCLUSIVE: EXIT_INCONCLUSIVE,
}


class GateResult:
    """verdict + reason + trace + identity_probe 를 담는 값 객체."""

    def __init__(
        self,
        gate_id: str,
        verdict: str,
        reason: str = "",
        trace: Optional[dict] = None,
        identity_probe: Optional[dict] = None,
    ) -> None:
        if verdict not in _VALID_VERDICTS:
            raise ValueError(
                "GateResult.verdict 는 PASS/RED/INCONCLUSIVE 중 하나여야 한다 (got: %r)"
                % (verdict,)
            )
        self.gate_id = gate_id
        self.verdict = verdict
        self.reason = reason
        self.trace = trace if trace is not None else {}
        self.identity_probe = identity_probe if identity_probe is not None else {}

    @property
    def exit_code(self) -> int:
        return EXIT_BY_VERDICT[self.verdict]

    def to_json(self) -> str:
        """단일 라인 JSON. key 순서 고정: gate_id, verdict, reason, trace, identity_probe."""
        payload = {
            "gate_id": self.gate_id,
            "verdict": self.verdict,
            "reason": self.reason,
            "trace": self.trace,
            "identity_probe": self.identity_probe,
        }
        return json.dumps(payload, ensure_ascii=False)


def emit(result: GateResult, stream=None) -> int:
    """result 를 단일 JSON 라인으로 stream(기본 sys.stdout)에 쓰고 exit_code 를 반환한다.

    ★반드시 반환만 한다 — sys.exit() 를 호출하지 않는다 (테스트에서 직접 호출 가능해야 함).★
    """
    if stream is None:
        stream = sys.stdout
    stream.write(result.to_json() + "\n")
    return result.exit_code


def empty_target(
    gate_id: str,
    reason: str,
    trace: Optional[dict] = None,
    identity_probe: Optional[dict] = None,
) -> GateResult:
    """[154-AC-3] empty-target 헬퍼 — 항상 INCONCLUSIVE 를 만든다. GREEN 생성 경로 없음."""
    return GateResult(
        gate_id=gate_id,
        verdict=INCONCLUSIVE,
        reason=reason,
        trace=trace,
        identity_probe=identity_probe,
    )


def unknown_input(
    gate_id: str,
    reason: str,
    trace: Optional[dict] = None,
    identity_probe: Optional[dict] = None,
) -> GateResult:
    """[154-AC-4] unknown-input fail-closed 헬퍼 — 항상 RED 를 만든다."""
    return GateResult(
        gate_id=gate_id,
        verdict=RED,
        reason=reason,
        trace=trace,
        identity_probe=identity_probe,
    )
