"""
scripts/lib/check_mutation_disposition.py
CFP-2464 Phase 2 — mutation peer (touchpoint #8) surviving-mutant disposition 결정 SSOT (순수 함수)

기능:
  ProactiveCheckPacket #8 (mutation peer) 의 surviving-mutant 주장 + PL/QADev 재현
  결과를 입력받아, 3-상태 disposition 을 결정론적으로 산출하는 *순수 함수* SSOT.
  구현리뷰 lane worker (CodexReviewAgent 동형 Bash dispatch) 가 Codex 로부터 받은
  surviving-mutant finding 을 lane(QADev/CodeReviewPL)이 재현 falsify 한 뒤, 그 재현
  결과를 본 함수에 위임(SSOT)해 disposition 을 확정한다. discriminating test
  (tests/scripts/test-check-mutation-disposition.sh)가 INV-M1~M5 별 RED→GREEN
  변별을 강제 검증한다(anti-theater / mutation-kill).

  regex-free, deterministic, 외부 의존 0 (stdlib json/argparse/sys 만).

  Story A(CFP-2458) check_merge_gate_disposition.py 패턴 답습 — 단, disposition
  axis 가 다르다: A = merge-time fail-mode disposition (PASS/BLOCKED/DEGRADED_PASS,
  ADR-070 Amd 9 §결정 D7), 본 파일 = mutation surviving-mutant disposition
  (hollow_gate_verified/undetermined/rejected_false_positive, ADR-070 Amd 10 §결정 D8).
  두 axis 는 disjoint (cause ↔ merge-disposition ↔ mutation-disposition).

── 입력 (JSON, stdin 또는 fixture 파일 인자) ──
  {
    "mutants": [
      {
        "id": "<mutant 식별자>",
        "location": "<file:line>",            # Codex 발화 mutant 위치 (evidence)
        "evidence_matches_ground_truth": bool,  # PL verify-before-trust: 위치/baseline 이 실제 코드와 일치하는가
        "survived": bool,                       # mutant 적용 후 suite 가 여전히 PASS 인가 (true=surviving, false=killed)
        "observable_behavior_diff": bool,       # 어떤 입력에서 관측 가능한 동작 차이가 있는가 (false=equivalent 의심)
        "deterministic": bool,                  # 동일 mutant 다회 실행 결정론 확인 (false=flaky 의심)
        "reproduced_pass": bool,                # PL/QADev 가 해당 mutant 실제 적용 후 suite PASS 재현 통과
        "severity": "P0"|"P1"|"P2"|null         # critic 발화 severity (hollow_gate_verified 한정 부여)
      },
      ...
    ],
    "codex_available": bool                      # fail-mode 여부 (false = Codex 미가용 → lane-time fail-open)
  }

── 출력 disposition enum (ADR-070 Amd 10 §결정 D8 — 3-상태 closed enum) ──
  "hollow_gate_verified"     — 진짜 검사연극. surviving + 재현 통과 + 관측 동작차이 +
                               결정론 확인 + evidence ground-truth 일치. severity 부여 →
                               ADR-081 Amd 10 D11 severity rubric (P0/P1 FIX / P2 기록).
  "undetermined"             — equivalent 의심(동작차이 0, undecidable) 또는 flaky 의심
                               (다회 실행 비결정). 자동 hollow-gate 승격 금지 + 자동 reject
                               도 아님 — '불확정' 보류 (Story §9 기록, 사람 검토 후보).
                               severity 미부여. cry-wolf 차단 (충족 불가능한 요구 금지).
  "rejected_false_positive"  — evidence 가 ground truth 와 mismatch (D3 reject), 또는
                               mutant 가 killed (suite 가 RED = 테스트가 실제로 잡음 →
                               hollow-gate 주장 자체가 틀림). finding reject + false-positive tally.

── disposition 결정 규칙 (Story §8 invariant SSOT — ADR-070 Amd 10 §결정 D8 / ADR-081 Amd 10 D11) ──
  INV-M1 (hollow_gate_verified 승격 — verified hollow-gate 한정):
    evidence_matches_ground_truth=true AND survived=true AND observable_behavior_diff=true
    AND deterministic=true AND reproduced_pass=true 인 mutant → hollow_gate_verified.
    이 5-AND 충족 mutant 만 severity 부여 대상 (ADR-081 D11.a step 2).
  INV-M2 (undetermined 보류 — equivalent/flaky 양면 보존):
    evidence_matches_ground_truth=true AND survived=true 이나
      (i) observable_behavior_diff=false (equivalent 의심, undecidable) OR
      (ii) deterministic=false (flaky 의심)
    → undetermined. 자동 hollow-gate 승격 금지 AND 자동 reject 금지 (양면 보존).
    severity 미부여 (불확정 보류).
  INV-M3 (rejected_false_positive — mismatch 또는 killed):
    evidence_matches_ground_truth=false (D3 reject 흐름) → rejected_false_positive.
    OR survived=false (mutant killed = suite 가 RED = 테스트가 실제로 잡음 →
      surviving-mutant/hollow-gate 주장 자체가 틀림) → rejected_false_positive.
    (severity 미부여 — 차단 trigger 아님)
  INV-M4 (severity 부여 = hollow_gate_verified 한정 + P2 비차단):
    severity (P0/P1/P2) 는 hollow_gate_verified mutant 에만 부여.
    undetermined / rejected_false_positive 는 severity 미부여 (None).
    P2 = 비차단 (기록 후 진행, cry-wolf 차단 — ADR-081 D11.b).
  INV-M5 (provenance 동반):
    모든 disposition 은 provenance metadata 를 동반 반환한다. artifact 없이 disposition
    반환 경로 0.

  우선순위 (각 mutant 별 독립 판정): INV-M3 (mismatch/killed reject) → INV-M2
    (equivalent/flaky 불확정) → INV-M1 (verified). evidence mismatch 또는 killed 가
    최우선 (그 mutant 의 hollow-gate 주장 자체가 무효). 그 다음 equivalent/flaky 의심
    필터 (undecidable 보류), 마지막으로 5-AND 충족 시 verified.

── 출력 형식 ──
  stdout: JSON {"dispositions": [{"id", "disposition", "severity"}], "provenance": {...}}
          (INV-M5 — provenance artifact 동반)
  exit:   0 = hollow_gate_verified 0건 (차단 trigger 없음 — undetermined/reject/clean)
          1 = hollow_gate_verified 1+ (재현된 hollow-gate 검출 — 테스트용 신호, non-zero)
          2 = SETUP error (입력 malformed / 파일 read 실패 / JSON decode 실패)
  (테스트는 disposition 문자열을 직접 assert 하여 exit code 모호성을 회피한다.)

Exit-code 3-tier (ADR-060 §결정 15 동형):
  0 = 차단 trigger 없음  /  1 = hollow-gate 검출  /  2 = SETUP error

  주의: lane-time fail-open (ADR-070 Amd 10 §결정 D8 (c), Q-B) — Codex 미가용
    (codex_available=false) 시 mutation 미수행 marker 기록 후 lane 진행. 본 SSOT 는
    codex_available=false 입력에 대해 빈 disposition + fail-open marker provenance 반환
    (lane 진행 = exit 0). merge-time #7 의 fail-closed 와 disjoint.

Prior art: scripts/lib/check_merge_gate_disposition.py (CFP-2458 — 3-tier exit /
  순수 결정 함수 / provenance 동반 / reconfigure boilerplate).
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
SCRIPT_NAME = "check_mutation_disposition"

# disposition enum (ADR-070 Amd 10 §결정 D8 — 3-상태 closed enum)
HOLLOW_GATE_VERIFIED = "hollow_gate_verified"
UNDETERMINED = "undetermined"
REJECTED_FALSE_POSITIVE = "rejected_false_positive"

# severity 부여 대상 (INV-M4 — hollow_gate_verified 한정)
_VALID_SEVERITIES = frozenset({"P0", "P1", "P2"})

# lane-time fail-open marker (ADR-070 Amd 10 §결정 D8 (c) — Q-B)
_FAIL_OPEN_MARKER = "mutation-peer-fallback"


# ---------------------------------------------------------------------------
# 순수 결정 함수 (SSOT) — 부수효과 0, 입력 dict → (dispositions, provenance) 튜플
# ---------------------------------------------------------------------------
def decide_dispositions(packet: dict) -> tuple[list[dict], dict]:
    """ProactiveCheckPacket #8 mutation 재현 결과 → (dispositions, provenance) 결정.

    순수 함수 — I/O / 전역 상태 / 시간 의존 0. 같은 입력 → 항상 같은 출력.
    INV-M1~M5 의 단일 출처.

    Args:
        packet: 입력 dict (mutants / codex_available).

    Returns:
        (dispositions_list, provenance_dict).
        dispositions_list = [{"id", "disposition", "severity"}] (mutant 별 독립 판정).
        provenance 는 INV-M5 — 모든 경로에 동반 (artifact 없이 반환하는 경로 0).

    Raises:
        ValueError: 입력 malformed (CLI 가 exit 2 SETUP error 로 변환).
    """
    if not isinstance(packet, dict):
        raise ValueError("packet must be a JSON object")

    codex_available = packet.get("codex_available", True)
    if not isinstance(codex_available, bool):
        raise ValueError("codex_available must be a boolean")

    mutants = packet.get("mutants", [])
    if not isinstance(mutants, list):
        raise ValueError("mutants must be a list")

    # ── lane-time fail-open (ADR-070 Amd 10 §결정 D8 (c) — Q-B) ──
    #   Codex 미가용 시 mutation 미수행 marker 기록 후 lane 진행 (빈 disposition).
    #   merge-time #7 의 fail-closed 와 disjoint — lane-time = 마지막 방어선 아님.
    if codex_available is False:
        provenance = _provenance(
            rule="INV-D8(c)/fail-open",
            reason=(
                "codex_available=false → lane-time fail-open "
                f"(marker `[{_FAIL_OPEN_MARKER}: disposition=open]` 기록 후 lane 진행, "
                "mutation 미수행 — ADR-070 Amd 10 §결정 D8 (c) Q-B)"
            ),
            mutants_attempted=len(mutants),
            verified_count=0,
            undetermined_count=0,
            rejected_count=0,
            codex_available=False,
            fail_open=True,
        )
        return [], provenance

    # ── mutant 별 독립 disposition 판정 ──
    dispositions: list[dict] = []
    verified_count = 0
    undetermined_count = 0
    rejected_count = 0

    for m in mutants:
        if not isinstance(m, dict):
            raise ValueError("each mutant must be a JSON object")

        disposition, severity = _decide_one(m)
        dispositions.append(
            {
                "id": m.get("id"),
                "disposition": disposition,
                "severity": severity,
            }
        )

        if disposition == HOLLOW_GATE_VERIFIED:
            verified_count += 1
        elif disposition == UNDETERMINED:
            undetermined_count += 1
        else:  # REJECTED_FALSE_POSITIVE
            rejected_count += 1

    provenance = _provenance(
        rule="INV-M1/M2/M3",
        reason=(
            f"mutant {len(mutants)}건 판정 → "
            f"hollow_gate_verified={verified_count} / "
            f"undetermined={undetermined_count} / "
            f"rejected_false_positive={rejected_count}"
        ),
        mutants_attempted=len(mutants),
        verified_count=verified_count,
        undetermined_count=undetermined_count,
        rejected_count=rejected_count,
        codex_available=True,
        fail_open=False,
    )
    return dispositions, provenance


def _decide_one(m: dict) -> tuple[str, Any]:
    """단일 mutant → (disposition, severity) 판정.

    우선순위 (INV-M3 → INV-M2 → INV-M1):
      1. evidence mismatch OR killed → rejected_false_positive (severity 미부여)
      2. equivalent 의심(동작차이 0) OR flaky 의심(비결정) → undetermined (severity 미부여)
      3. 5-AND 충족 → hollow_gate_verified (severity 부여 — INV-M4)
    """
    evidence_ok = m.get("evidence_matches_ground_truth")
    survived = m.get("survived")
    observable_diff = m.get("observable_behavior_diff")
    deterministic = m.get("deterministic")
    reproduced_pass = m.get("reproduced_pass")

    # ── INV-M3 (최우선): evidence mismatch 또는 killed → reject ──
    #   evidence 가 ground truth 와 불일치 (D3 reject) — hollow-gate 주장 자체 무효.
    if evidence_ok is False:
        return REJECTED_FALSE_POSITIVE, None
    #   mutant killed (suite 가 RED = 테스트가 실제로 잡음) — surviving 주장 틀림.
    if survived is False:
        return REJECTED_FALSE_POSITIVE, None

    # 여기 도달 = evidence_ok=true AND survived=true (= surviving mutant 후보)

    # ── INV-M2: equivalent 의심(동작차이 0) 또는 flaky 의심(비결정) → undetermined ──
    #   undecidable — 자동 hollow-gate 승격 금지 + 자동 reject 도 아님 (양면 보존).
    if observable_diff is not True:
        return UNDETERMINED, None  # equivalent 의심 (동작차이 0)
    if deterministic is not True:
        return UNDETERMINED, None  # flaky 의심 (다회 실행 비결정)

    # ── INV-M1: 5-AND 충족 확인 (reproduced_pass) → hollow_gate_verified ──
    #   evidence_ok ∧ survived ∧ observable_diff ∧ deterministic ∧ reproduced_pass.
    #   재현 미통과면 hollow-gate 승격 불가 → undetermined 보류 (자동 reject 아님).
    if reproduced_pass is not True:
        return UNDETERMINED, None

    # 5-AND 전부 충족 → 재현된 hollow-gate (INV-M4 — severity 부여)
    severity = _normalize_severity(m.get("severity"))
    return HOLLOW_GATE_VERIFIED, severity


def _normalize_severity(severity: Any) -> str:
    """hollow_gate_verified mutant 의 severity 정규화 (INV-M4).

    유효 severity (P0/P1/P2) 면 그대로, 아니면 ValueError.
    hollow_gate_verified 는 ADR-081 Amd 10 D11 severity rubric 대상 — severity 의무.
    """
    if severity not in _VALID_SEVERITIES:
        raise ValueError(
            f"hollow_gate_verified mutant 는 severity (P0/P1/P2) 의무 — got {severity!r}"
        )
    return severity


def _provenance(
    *,
    rule: str,
    reason: str,
    mutants_attempted: int,
    verified_count: int,
    undetermined_count: int,
    rejected_count: int,
    codex_available: bool,
    fail_open: bool,
) -> dict:
    """INV-M5 — disposition 동반 provenance metadata 구성.

    모든 경로가 본 함수를 거쳐 artifact 를 동반 — artifact 없이 반환되는 경로 0.
    """
    return {
        "script": SCRIPT_NAME,
        "rule": rule,
        "reason": reason,
        "mutants_attempted": mutants_attempted,
        "verified_count": verified_count,
        "undetermined_count": undetermined_count,
        "rejected_count": rejected_count,
        "codex_available": codex_available,
        "fail_open": fail_open,
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
        description="mutation peer (touchpoint #8) surviving-mutant disposition SSOT (CFP-2464)",
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
        dispositions, provenance = decide_dispositions(packet)
    except ValueError as exc:
        print(
            json.dumps({"error": f"입력 malformed: {exc}", "exit_code": 2}),
            file=sys.stderr,
        )
        return 2

    # ── 출력 (INV-M5 — provenance artifact 동반) ──
    print(json.dumps({"dispositions": dispositions, "provenance": provenance}))

    # ── exit code (3-tier): hollow_gate_verified 1+ 면 차단 trigger (non-zero) ──
    if provenance["verified_count"] > 0:
        return 1  # 재현된 hollow-gate 검출 (보류 계열 신호)
    return 0  # 차단 trigger 없음 (undetermined / reject / clean / fail-open)


if __name__ == "__main__":
    sys.exit(main())
