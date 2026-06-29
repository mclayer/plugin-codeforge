"""
scripts/lib/check_merge_gate_disposition.py
CFP-2458 Phase 2 — merge-time 적대적 반증 게이트 disposition 결정 SSOT (순수 함수)

기능:
  ProactiveCheckPacket #7 verify 결과를 입력받아, merge 보류/통과 disposition 을
  결정론적으로 산출하는 *순수 함수* SSOT. Orchestrator inline 절차 + playbook 정책이
  같은 결정 로직을 본 함수에 위임(SSOT)하고, discriminating test
  (tests/scripts/test-check-merge-gate-disposition.sh)가 INV-G1~G4 별 RED→GREEN
  변별을 강제 검증한다(anti-theater / mutation-kill).

  regex-free, deterministic, 외부 의존 0 (stdlib json/argparse/sys/os 만).

── 입력 (JSON, stdin 또는 fixture 파일 인자) ──
  {
    "findings": [
      {"severity": "P0"|"P1"|"P2",
       "evidence_present": bool,
       "verify_result": "verified"|"mismatch"|"absent"},
      ...
    ],
    "codex_available": bool,                # fail-mode 여부 (false = Codex 미가용)
    "degrade_state": {                       # codex_available=false 일 때만 참조
      "retries": int,
      "max_retries": int,
      "elapsed": number,
      "timeout": number,
      "user_notified": bool
    }
  }

── 출력 disposition enum ──
  "PASS"          — 통과(머지 가능). verified P0/P1 0 (혹은 P2-only / findings=[]).
  "BLOCKED"       — 머지 보류. verified P0/P1 1+ 검출, 또는 fail-mode 재시도 중,
                    또는 fail-mode 한도초과 + user_notified=false(silent auto-pass 차단).
  "DEGRADED_PASS" — Codex 미가용 fail-mode 한도초과 + user_notified=true 통과(하이브리드).
  "FAIL_CLOSED"   — (예약) 입력 malformed 등 안전 차단. 현 규칙세트에선 setup-error 로 처리.

── disposition 결정 규칙 (Story §8.4 invariant SSOT) ──
  INV-G1 (verified P0/P1 차단):
    verify_result=verified AND severity∈{P0,P1} 인 finding 1+ → disposition ≠ PASS (BLOCKED).
  INV-G2 (오탐 무효 폐기 — 부당 차단 0):
    evidence 부재(evidence_present=false 또는 verify_result=absent) 또는 verify_result=mismatch
    인 finding 은 머지 보류 trigger 가 아니다(해당 finding 무시). false-positive(P0 발화했으나
    mismatch)는 BLOCKED 유발 금지.
  INV-G3 (codex 미가용 하이브리드 — silent auto-pass 절대 0):
    codex_available=false →
      retries < max_retries AND elapsed < timeout                       → BLOCKED (재시도 중, 미통과)
      (retries >= max_retries OR elapsed >= timeout) AND user_notified  → DEGRADED_PASS
      (retries >= max_retries OR elapsed >= timeout) AND NOT user_notified → BLOCKED (silent auto-pass 0)
  INV-G4 (provenance 동반):
    모든 disposition 은 provenance metadata 를 동반 반환한다. artifact 없이 PASS 반환 경로 0.
  보조:
    verified P2-only (verified P0/P1 0) AND codex_available=true → PASS (P2 비차단, 기록 후 진행).
    findings=[] AND codex_available=true → PASS.

  주의(우선순위): verified P0/P1 (INV-G1) 은 codex_available 상태보다 우선한다 — 실제
  verified 결함이 있으면 fail-mode 여부와 무관하게 BLOCKED(머지 통과 금지).

── 출력 형식 ──
  stdout: JSON {"disposition": "<enum>", "provenance": {...}}  (INV-G4 — artifact 동반)
  exit:   0 = PASS / DEGRADED_PASS (머지 통과 계열 — 정상)
          1 = BLOCKED / FAIL_CLOSED (설계상 머지 보류 검출 — 테스트용 신호, non-zero)
          2 = SETUP error (입력 malformed / 파일 read 실패 / JSON decode 실패)
  (테스트는 disposition 문자열을 직접 assert 하여 exit code 모호성을 회피한다.)

Exit-code 3-tier (ADR-060 §결정 15 동형):
  0 = 통과 계열  /  1 = 보류 계열  /  2 = SETUP error

Prior art: scripts/lib/check_parallel_work_sentinel.py (reconfigure boilerplate /
  3-tier exit) + scripts/check-stakes-tier-gating.sh (fail-safe monotone 판정 SSOT).
"""

import argparse
import json
import sys
from typing import Any

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_merge_gate_disposition"

# disposition enum
PASS = "PASS"
BLOCKED = "BLOCKED"
DEGRADED_PASS = "DEGRADED_PASS"
FAIL_CLOSED = "FAIL_CLOSED"

# 통과 계열(exit 0) vs 보류 계열(exit 1)
_PASS_FAMILY = (PASS, DEGRADED_PASS)

# severity 차단 대상 (INV-G1)
_BLOCKING_SEVERITIES = frozenset({"P0", "P1"})


# ---------------------------------------------------------------------------
# 순수 결정 함수 (SSOT) — 부수효과 0, 입력 dict → (disposition, provenance) 튜플
# ---------------------------------------------------------------------------
def decide_disposition(packet: dict) -> tuple[str, dict]:
    """ProactiveCheckPacket #7 verify 결과 → (disposition, provenance) 결정.

    순수 함수 — I/O / 전역 상태 / 시간 의존 0. 같은 입력 → 항상 같은 출력.
    INV-G1~G4 의 단일 출처.

    Args:
        packet: 입력 dict (findings / codex_available / degrade_state).

    Returns:
        (disposition_enum, provenance_dict).
        provenance 는 INV-G4 — 모든 disposition 에 동반 (artifact 없이 PASS 경로 0).

    Raises:
        ValueError: 입력 malformed (CLI 가 exit 2 SETUP error 로 변환).
    """
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")

    findings = packet.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")

    codex_available = packet.get("codex_available", True)
    if not isinstance(codex_available, bool):
        raise ValueError("codex_available must be a boolean")

    # ── INV-G1 / INV-G2: verified P0/P1 검출 (오탐·evidence부재·mismatch 는 무시) ──
    #   머지 보류 trigger 자격 = verify_result == "verified" AND severity ∈ {P0,P1}
    #     AND evidence_present == true.
    #   verify_result ∈ {mismatch, absent} 또는 evidence_present=false 인 finding 은
    #   INV-G2 에 의해 폐기(차단 유발 금지) — false-positive 부당 차단 0.
    blocking_findings: list[dict] = []
    ignored_findings: list[dict] = []
    for f in findings:
        if not isinstance(f, dict):
            raise ValueError("each finding must be a JSON object")
        severity = f.get("severity")
        evidence_present = f.get("evidence_present")
        verify_result = f.get("verify_result")

        is_blocking_severity = severity in _BLOCKING_SEVERITIES
        is_verified = verify_result == "verified"
        # evidence 부재 = evidence_present false 거나 verify_result == absent (INV-G2)
        evidence_ok = (evidence_present is True) and (verify_result != "absent")

        if is_blocking_severity and is_verified and evidence_ok:
            blocking_findings.append(f)
        else:
            # INV-G2: 오탐(mismatch) / evidence 부재(absent or false) / P2 = 무시
            ignored_findings.append(f)

    verified_blocking_count = len(blocking_findings)

    # ── INV-G1 우선: verified P0/P1 1+ → BLOCKED (codex 상태 무관) ──
    if verified_blocking_count > 0:
        provenance = _provenance(
            rule="INV-G1",
            reason=(
                f"verified P0/P1 finding {verified_blocking_count}건 검출 "
                f"→ BLOCKED (머지 통과 금지)"
            ),
            blocking_findings=blocking_findings,
            ignored_findings=ignored_findings,
            codex_available=codex_available,
            degrade_state=None,
        )
        return BLOCKED, provenance

    # 여기 도달 = verified P0/P1 0 (P2-only / 오탐만 / findings=[] / evidence 부재만)

    # ── INV-G3: codex 미가용 하이브리드 (verified 차단 결함이 없을 때만) ──
    if codex_available is False:
        return _decide_fail_mode(packet, ignored_findings)

    # ── codex 가용 + verified P0/P1 0 → PASS (P2 비차단 / findings=[] 포함) ──
    provenance = _provenance(
        rule="INV-G2/보조",
        reason=(
            "verified P0/P1 finding 0 (P2-only / 오탐폐기 / findings=[]) "
            "AND codex_available=true → PASS"
        ),
        blocking_findings=[],
        ignored_findings=ignored_findings,
        codex_available=codex_available,
        degrade_state=None,
    )
    return PASS, provenance


def _decide_fail_mode(packet: dict, ignored_findings: list[dict]) -> tuple[str, dict]:
    """INV-G3 — codex_available=false 하이브리드 disposition.

    silent auto-pass 절대 0: 한도초과여도 user_notified=false 면 BLOCKED.
    """
    degrade = packet.get("degrade_state")
    if not isinstance(degrade, dict):
        raise ValueError(
            "codex_available=false 시 degrade_state(JSON object) 필수"
        )

    try:
        retries = int(degrade["retries"])
        max_retries = int(degrade["max_retries"])
        elapsed = float(degrade["elapsed"])
        timeout = float(degrade["timeout"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            f"degrade_state 필드 누락/형식오류: {exc}"
        ) from exc

    user_notified = degrade.get("user_notified")
    if not isinstance(user_notified, bool):
        raise ValueError("degrade_state.user_notified must be a boolean")

    # 한도초과 = 재시도 한도 OR 시간 한도 중 하나라도 도달
    over_limit = (retries >= max_retries) or (elapsed >= timeout)

    if not over_limit:
        # 재시도 여력 남음 → BLOCKED (아직 미통과, 재시도 중)
        provenance = _provenance(
            rule="INV-G3",
            reason=(
                f"codex 미가용 + 한도 미초과 (retries={retries}<{max_retries} "
                f"AND elapsed={elapsed}<{timeout}) → BLOCKED (재시도 중)"
            ),
            blocking_findings=[],
            ignored_findings=ignored_findings,
            codex_available=False,
            degrade_state=degrade,
        )
        return BLOCKED, provenance

    # 한도초과 — user_notified 분기 (silent auto-pass 차단 지점)
    if user_notified is True:
        provenance = _provenance(
            rule="INV-G3",
            reason=(
                "codex 미가용 + 한도초과 + user_notified=true "
                "→ DEGRADED_PASS (하이브리드 통과)"
            ),
            blocking_findings=[],
            ignored_findings=ignored_findings,
            codex_available=False,
            degrade_state=degrade,
        )
        return DEGRADED_PASS, provenance

    # 한도초과 AND user_notified=false → BLOCKED (silent auto-pass 0)
    provenance = _provenance(
        rule="INV-G3",
        reason=(
            "codex 미가용 + 한도초과 이나 user_notified=false "
            "→ BLOCKED (silent auto-pass 0 — 사용자 알림 없이 통과 불가)"
        ),
        blocking_findings=[],
        ignored_findings=ignored_findings,
        codex_available=False,
        degrade_state=degrade,
    )
    return BLOCKED, provenance


def _provenance(
    *,
    rule: str,
    reason: str,
    blocking_findings: list[dict],
    ignored_findings: list[dict],
    codex_available: bool,
    degrade_state: Any,
) -> dict:
    """INV-G4 — disposition 동반 provenance metadata 구성.

    모든 disposition 경로가 본 함수를 거쳐 artifact 를 동반 — artifact 없이
    반환되는 경로 0.
    """
    return {
        "script": SCRIPT_NAME,
        "rule": rule,
        "reason": reason,
        "verified_blocking_count": len(blocking_findings),
        "ignored_count": len(ignored_findings),
        "codex_available": codex_available,
        "degrade_state": degrade_state,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _read_input(path: str | None) -> str:
    """fixture 파일 인자가 있으면 파일에서, 없으면 stdin 에서 raw JSON 읽기."""
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="merge-gate 적대적 반증 disposition 결정 SSOT (CFP-2458)",
    )
    parser.add_argument(
        "fixture",
        nargs="?",
        default=None,
        help="입력 JSON 파일 경로 (미지정 시 stdin 에서 읽음)",
    )
    args = parser.parse_args(argv)

    # ── 입력 read + parse (SETUP error = exit 2) ──
    try:
        raw = _read_input(args.fixture)
    except OSError as exc:
        print(
            json.dumps({"error": f"입력 파일 read 실패: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    try:
        packet = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"error": f"JSON decode 실패: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    # ── 결정 (malformed 입력 = ValueError → exit 2 SETUP error) ──
    try:
        disposition, provenance = decide_disposition(packet)
    except ValueError as exc:
        print(
            json.dumps({"error": f"입력 malformed: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    # ── 출력 (INV-G4 — provenance artifact 동반) ──
    print(json.dumps({"disposition": disposition, "provenance": provenance}))

    # ── exit code (3-tier) ──
    if disposition in _PASS_FAMILY:
        return 0  # PASS / DEGRADED_PASS = 통과 계열
    return 1  # BLOCKED / FAIL_CLOSED = 보류 계열 (non-zero 신호)


if __name__ == "__main__":
    sys.exit(main())
