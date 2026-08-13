#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# check_census_oracle.py — AC-4 content-level 검사량 oracle (L1 정합 + L2 보존)
#
# Carrier: CFP-2926 Phase 2 (구현) / Story NG-1
# SSOT: docs/adr/ADR-154-amendment-1.md §AC-4 (검사량)
#
# 책임:
#   - 소스 disjoint: D (모델 선언) vs X (실행 — CI check-run 이름 + tool_call blob)
#     * X 소스 근거: repo-relative 스크립트 경로는 redaction 되지 않음 (dev-process-event-v1)
#     * ⇒ 모델이 쓰지 않는 소스
#   - 키 = (lane, check_class, target) — 3 성분 전건 보존
#   - 술어 (L1 상시 / L2 조건부 — caller 가 before 스냅샷을 줄 때만 측정):
#     * L1 정합: D(after) ⊆ X(after) → M1 declared-but-not-executed 죽이기
#     * L2 보존: X(before) ⊆ X(after) — ★`--executed-before` / `executed_before=` 로
#       before 스냅샷이 주어진 경우에만 측정★. 미제공 시 상수 True 로 위장하지 않고
#       `l2_pass = None` + `l2_status = "not_measured"` 로 방출한다 (기계 채널 정직성 —
#       하류가 "검증됨" 과 "안 셈" 을 구별할 수 있어야 한다. F-CR-003 봉합).
#       ⇒ before 미제공 경로(= 현 CI 호출 형상)에서 L2 는 M2(D·X 동시 삭제)를 죽이지 못한다.
#         그 경로의 M2 는 선언 D 에 흔적이 남을 때만 L1 이 부수적으로 잡는다.
#   - mutant 축 귀속 = 아래 "mutant 축 귀속 표" (★실행 열까지 명시★ — 구 헤더의
#     "5 mutant 축 귀속 (docstring 에 표 명시)" 는 표가 없었고 실행 mutant 도 2개뿐이었다.
#     F-CR-008 봉합: 문면을 실물에 맞춘다)
#   - oracle self-test (ⓐ 항등성 / ⓑ-lane / ⓑ-check_class / ⓑ-target / ⓒ 빈입력
#     / ⓓ vacuous-D floor / M1 / M2(before 제공) / M4 / INPUT 4종 + 양성대조 / 정상)
#   - empty-target: D·X 공집합 → INCONCLUSIVE (ⓒ)
#   - vacuous-D floor: D = ∅ 이면 L1(D ⊆ X) 이 공허참 → PASS 금지, INCONCLUSIVE (ⓓ)
#   - unknown-input: 미분류 → exit≠0 (축 불명 자동제거 금지)
#   - 입력 fail-closed: 경로 부재 / 미지원 확장자 / 읽기 실패 / 파싱 실패 / 형상 위반
#     → 전부 RED (exit 1). ★경로 오타 1회로 GREEN 이 나오는 경로 0★ (F-CR-001 봉합)
#
# mutant 축 귀속 표 (★"self-test 실행" 열 = 이 파일 안에서 실제로 돌려 본 것만 ✔★):
#
#   | mutant | 내용                                        | 죽이는 leg        | self-test 실행 |
#   |--------|---------------------------------------------|-------------------|----------------|
#   | M1     | declared-but-not-executed                   | L1                | ✔ `res_m1`     |
#   | M2     | 검사 unit 통째 삭제 (D·X 동시)              | L2 (before 필요)  | ✔ `res_m2_before` — ★before 제공 경로 한정★. before 미제공 경로에서는 ✘ (미검출, 위 술어 항 자인) |
#   | M3     | ★본 파일에 정의 없음★ — 구 헤더의 "5 mutant" 는 M3 의 정의도 실행도 동반하지 않았다. 외부 SSOT(Story §8) 축이라면 그 축은 본 oracle 관측면 밖이다 | — | ✘ (미정의·미실행) |
#   | M4     | 유령 선언 (D 에만 있고 X 에 없음)           | L1                | ✔ `res_m4`     |
#   | M5′    | canonicalizer 성분 탈락 (lane/check_class/target) | 키 정규화 3성분 | ✔ ⓑ-lane / ⓑ-check_class / ⓑ-target |
#   | INPUT  | ★본 FIX 신설 (F-CR-001)★ — loader fail-open (경로 오타·미지원 확장자·형상 위반이 GREEN) | 입력 fail-closed | ✔ INPUT 4종 + 양성대조 |
#
# 불변식:
#   - 3-state: PASS / RED / INCONCLUSIVE
#   - stdout 단일 JSON 라인 + sys.exit(n)
#   - oracle 은 기계 실행 가능 검사 단위만 본다 (AC-4)
#   - "peer 가 실제로 읽었는가" 는 관측면 밖 (판별력만 보증, 검사 품질 보증 안 함)
#   - Python 3.9 + stdlib only + UTF-8
#     ⇒ ★YAML 입력은 지원하지 않는다★ (pyyaml = stdlib 밖). 구 `--help` 의
#       "JSON 리스트 또는 YAML" 광고는 실제 능력(.json 전용)과 불일치였고, 본 FIX 는
#       stdlib-only 불변식을 지키는 쪽(= help 정정 + 미지원 확장자 RED)으로 일치시킨다.
#
# 정직 천장 (docstring):
#   - census 대상 집합의 완전성은 보증 밖 — oracle 이 "검사 단위"로 세지 않기로 한 것은
#     애초에 관측되지 않는다. 판별력만 보증하고 검사 품질은 보증하지 않는다.
#   - 입력 fail-closed 는 ★해석 가능성★ 만 보증한다. 해석된 목록이 진짜 D/X 인지
#     (누가 무엇을 넣었는지) 는 여전히 caller 신뢰이며 본 oracle 관측면 밖이다.
#   - L2 는 caller 가 before 스냅샷을 줄 때만 산다. CI 는 주지 않으므로 CI 경로의
#     verdict 는 ★사실상 L1 1-leg★ 이다 — JSON 이 이를 `l2_status` 로 자백한다.
#     ("2-leg 술어처럼 읽히는데 실효는 1-leg" 라는 사실을 가리지 않고 매 run 방출한다.)
#
# ★설계 축 경계 (본 FIX 가 ★결정하지 않은★ 것)★:
#   "NG-1 이 애초에 2-leg 술어여야 하는가 / 프로덕션에서 X(before) 를 ★무엇이 공급하는가★"
#   는 ArchitectPL 판정 대기 중인 ★별 축★ 이며 본 파일은 그 답을 주장하지 않는다.
#   본 FIX 가 한 것은 정직성 3항뿐이다:
#     (1) 미측정 leg 을 미측정이라 방출 (`l2_pass: null` + `l2_status`)  … F-CR-003
#     (2) 도달 불가였던 L2-RED 분기를 self-test 가 실제로 밟게 함 (dead code 해소) … F-CR-004
#     (3) mutant 축 귀속 문면을 실물에 일치 … F-CR-008
#   `--executed-before` 는 NG-5·NG-13 과 동형의 ★caller-supplied optional★ 이다
#   (identity_bearing: false, CI 배선 0 — 현 CI 호출은 `--self-test` 단일). 계약 문서·
#   호출자·workflow 무변경. 설계 판정이 다른 입력 구조를 택하면 이 파라미터가 교체 대상이다.
#
# 사용:
#   python3 check_census_oracle.py [--declared-spec D.json] [--executed-manifest X.json]
#                                  [--executed-before X_BEFORE.json]
#   python3 check_census_oracle.py --self-test
#

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


#: 입력 loader 가 해석할 수 있는 확장자 (★closed★ — 그 외는 RED).
#: YAML 부재는 누락이 아니라 stdlib-only 불변식의 귀결이다 (헤더 §불변식).
SUPPORTED_INPUT_SUFFIXES = (".json", ".jsonl")


class InputError(Exception):
    """입력 해석 실패 — ★fail-closed★. 빈 리스트로 눕히지 않고 RED 로 올린다.

    구 판본은 `except Exception: pass` 로 삼켜서 경로 오타 1회면 D = [] 가 되고
    L1(∅ ⊆ X) 이 공허참이 되어 ``verdict: PASS`` 가 나왔다 (F-CR-001, 1단계 gaming).
    """

    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _canonicalize_key(lane, check_class, target):
    """키 정규화 (3 성분 전건 보존)."""
    return (str(lane), str(check_class), str(target))


def _coerce_unit(raw, label, idx):
    """단일 원소 → (lane, check_class, target). 형상 위반 = InputError (조용한 skip 0)."""
    if isinstance(raw, dict):
        missing = [k for k in ("lane", "check_class", "target") if k not in raw]
        if missing:
            raise InputError(
                "INPUT_SHAPE_INVALID",
                "%s[%d] dict 필수 키 부재: %s" % (label, idx, ", ".join(missing)),
            )
        return (raw["lane"], raw["check_class"], raw["target"])
    if isinstance(raw, (list, tuple)):
        if len(raw) != 3:
            raise InputError(
                "INPUT_SHAPE_INVALID",
                "%s[%d] 원소 %d개 ≠ 3 (lane, check_class, target)" % (label, idx, len(raw)),
            )
        return (raw[0], raw[1], raw[2])
    raise InputError(
        "INPUT_SHAPE_INVALID",
        "%s[%d] 타입 %s — list/tuple/dict 만 허용" % (label, idx, type(raw).__name__),
    )


def load_units(path_str, label):
    """단위 목록 로드 — ★fail-closed★. 실패는 예외이지 빈 리스트가 아니다.

    RED 사유 5종: 미지원 확장자 / 경로 부재 / 읽기 실패 / 파싱 실패 / 형상 위반.
    """
    path = Path(path_str)
    if path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
        raise InputError(
            "INPUT_UNSUPPORTED_SUFFIX",
            "%s=%s — 지원 확장자는 %s 뿐 (YAML 미지원: stdlib-only 불변식)"
            % (label, path_str, "/".join(SUPPORTED_INPUT_SUFFIXES)),
        )
    if not path.is_file():
        raise InputError(
            "INPUT_MISSING",
            "%s=%s 경로 부재 — ★경로 오타는 RED 이지 GREEN 이 아니다★" % (label, path_str),
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("INPUT_UNREADABLE", "%s=%s 읽기 실패: %s" % (label, path_str, exc))

    try:
        raw = json.loads(text)
    except ValueError:
        # JSONL fallback — 한 줄이라도 깨지면 RED (부분 파싱 후 조용한 계속 금지)
        rows = []
        for lineno, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError as exc:
                raise InputError(
                    "INPUT_UNPARSEABLE",
                    "%s=%s JSON/JSONL 파싱 실패 (line %d): %s" % (label, path_str, lineno, exc),
                )
        raw = rows

    if not isinstance(raw, list):
        raise InputError(
            "INPUT_SHAPE_INVALID",
            "%s=%s 최상위 타입 %s — JSON 리스트여야 함" % (label, path_str, type(raw).__name__),
        )
    return [_coerce_unit(item, label, i) for i, item in enumerate(raw)]


def check_census_oracle(declared_units, executed_units, source_info=None, executed_before=None):
    """AC-4 검사량 oracle (L1 정합 상시 + L2 보존 조건부).

    입력:
      declared_units: [(lane, check_class, target), ...] — 모델 선언 D(after)
      executed_units: [(lane, check_class, target), ...] — 실행 기록 X(after)
      source_info: dict, identity_probe 용 (선택사항)
      executed_before: [(lane, check_class, target), ...] | None — X(before) 스냅샷.
        ★None 이면 L2 를 측정하지 않는다★ (상수 True 위장 금지 — `l2_pass = None`).

    반환: {
      "verdict": "PASS" | "RED" | "INCONCLUSIVE",
      "reason": str,
      "l1_pass": bool | None,          # None = 미산출 (D = ∅ 등)
      "l2_pass": bool | None,          # None = ★미측정★ (측정값 아님)
      "l2_status": "measured" | "not_measured",
      "trace": {
        "declared_count": int,
        "executed_count": int,
        "executed_before_count": int | None,   # None = before 미제공
        "lane_count": int,
      },
      "identity_probe": dict,
    }
    """
    if source_info is None:
        source_info = {
            "source": "tool_call blob",
            "count_declared": len(declared_units),
            "count_executed": len(executed_units),
            "count_executed_before": (None if executed_before is None else len(executed_before)),
        }

    # 정규화
    d_set = set(_canonicalize_key(l, c, t) for l, c, t in declared_units)
    x_set = set(_canonicalize_key(l, c, t) for l, c, t in executed_units)
    b_set = (
        None if executed_before is None
        else set(_canonicalize_key(l, c, t) for l, c, t in executed_before)
    )

    l2_measured = b_set is not None
    l2_status = "measured" if l2_measured else "not_measured"

    # L1 정합: D(after) ⊆ X(after). D = ∅ 이면 공허참이라 ★산출하지 않는다★ (None).
    l1_pass = d_set.issubset(x_set) if d_set else None
    # L2 보존: X(before) ⊆ X(after). before 미제공 = 미측정 (None).
    l2_pass = b_set.issubset(x_set) if l2_measured else None

    trace = {
        "declared_count": len(d_set),
        "executed_count": len(x_set),
        "executed_before_count": (len(b_set) if l2_measured else None),
        "lane_count": len(set(k[0] for k in d_set | x_set)),
    }

    if not d_set and not x_set:
        verdict = "INCONCLUSIVE"
        reason = "D·X 공집합 (empty-target, ⓒ). ★PASS 아님★"
    elif not d_set:
        # ★vacuous-D floor (ⓓ)★ — D = ∅ 이면 L1(D ⊆ X) 이 무조건 참이라 판별력이 0 이다.
        # 구 판본은 여기서 PASS 를 냈고, 그것이 loader fail-open 의 GREEN 출구였다.
        verdict = "INCONCLUSIVE"
        reason = (
            "D = ∅ — L1(D ⊆ X) 이 공허참이라 판정 불가 (vacuous-D floor, ⓓ). ★PASS 아님★"
        )
    elif not l1_pass:
        verdict = "RED"
        reason = "L1 정합 실패 (declared-but-not-executed: %d 건)" % len(d_set - x_set)
    elif l2_pass is False:
        verdict = "RED"
        reason = "L2 보존 실패 (X(before) 에 있었으나 X(after) 에 없음: %d 건)" % len(b_set - x_set)
    elif l2_measured:
        verdict = "PASS"
        reason = "L1 정합 OK, L2 보존 OK (양 leg 실측)"
    else:
        verdict = "PASS"
        reason = "L1 정합 OK. ★L2 는 미측정(not_measured) — before 스냅샷 미제공★"

    return {
        "verdict": verdict,
        "reason": reason,
        "l1_pass": l1_pass,
        "l2_pass": l2_pass,
        "l2_status": l2_status,
        "trace": trace,
        "identity_probe": source_info,
    }


def gate_result_to_json(result):
    """gate_verdict 패턴 준수 JSON 렌더.

    ``l2_pass: null`` + ``l2_status: "not_measured"`` 조합이 ★미측정★ 의 기계 표현이다.
    하류는 이 두 필드로 "검증됨" 과 "안 셈" 을 구별한다 (F-CR-003).
    """
    verdict_map = {"PASS": 0, "RED": 1, "INCONCLUSIVE": 3}
    return {
        "gate_id": "NG-1",
        "verdict": result["verdict"],
        "exit_code": verdict_map.get(result["verdict"], 3),
        "reason": result["reason"],
        "l1_pass": result["l1_pass"],
        "l2_pass": result["l2_pass"],
        "l2_status": result["l2_status"],
        "trace": result["trace"],
        "identity_probe": result["identity_probe"],
    }


def _self_test():
    """oracle self-test 5항 (ⓐ-ⓒ) + mutant kill 실증.

    5항:
      ⓐ 항등성 — 같은 검사의 두 표기 → 같은 키
      ⓑ-lane — lane 만 다른 쌍 → 다른 키
      ⓑ-check_class — check_class 만 다른 쌍 → 다른 키
      ⓑ-target — target 만 다른 쌍 → 다른 키
      ⓒ 빈 입력 → INCONCLUSIVE
    """
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ────────────────────── ⓐ 항등성 ──────────────────────
    k1 = _canonicalize_key("구현", "lint", "main.py")
    k2 = _canonicalize_key("구현", "lint", "main.py")
    check(k1 == k2, "[ⓐ] 항등성 실패 (같은 표기 다른 키)")

    # ────────────────────── ⓑ-lane ──────────────────────
    k_lane1 = _canonicalize_key("구현", "lint", "main.py")
    k_lane2 = _canonicalize_key("요구사항", "lint", "main.py")
    check(k_lane1 != k_lane2, "[ⓑ-lane] lane 성분 탈락 (동일 키)")

    # ────────────────────── ⓑ-check_class ──────────────────────
    k_check1 = _canonicalize_key("구현", "lint", "main.py")
    k_check2 = _canonicalize_key("구현", "test", "main.py")
    check(k_check1 != k_check2, "[ⓑ-check_class] check_class 성분 탈락")

    # ────────────────────── ⓑ-target ──────────────────────
    k_target1 = _canonicalize_key("구현", "lint", "main.py")
    k_target2 = _canonicalize_key("구현", "lint", "utils.py")
    check(k_target1 != k_target2, "[ⓑ-target] target 성분 탈락")

    # ────────────────────── ⓒ 빈 입력 ──────────────────────
    res_empty = check_census_oracle([], [])
    check(res_empty["verdict"] == "INCONCLUSIVE",
          f"[ⓒ] empty 입력 verdict {res_empty['verdict']} != INCONCLUSIVE (GREEN 금지)")

    # ────────────────────── M1: declared-but-not-executed ──────────────────────
    # D = {A, B}, X = {A} → L1 실패 (RED)
    declared = [("구현", "lint", "main.py"), ("구현", "test", "main.py")]
    executed = [("구현", "lint", "main.py")]
    res_m1 = check_census_oracle(declared, executed)
    check(res_m1["verdict"] == "RED" and not res_m1["l1_pass"],
          f"[M1] verdict {res_m1['verdict']} != RED | L1 {res_m1['l1_pass']} != False")

    # ────────────────────── ⓓ vacuous-D floor ──────────────────────
    # D = ∅, X = {A} → L1 이 공허참이므로 PASS 금지 (loader fail-open 의 구 GREEN 출구)
    res_vac = check_census_oracle([], [("구현", "lint", "main.py")])
    check(res_vac["verdict"] == "INCONCLUSIVE",
          f"[ⓓ] D=∅ verdict {res_vac['verdict']} != INCONCLUSIVE (vacuous PASS 재발)")
    check(res_vac["l1_pass"] is None,
          f"[ⓓ] D=∅ l1_pass {res_vac['l1_pass']!r} != None (공허참을 측정값처럼 방출)")

    # ────────────────────── M2: unit 통째 삭제 (D·X 동시) ──────────────────────
    # ★before 스냅샷을 줄 때만 L2 가 산다★ — X(before)={A,B}, X(after)={A}, D={A}
    #   → L1 은 통과(D⊆X)하지만 L2 가 B 소실을 잡아 RED.
    declared_m2 = [("구현", "lint", "main.py")]
    executed_after_m2 = [("구현", "lint", "main.py")]
    executed_before_m2 = [("구현", "lint", "main.py"), ("구현", "test", "main.py")]
    res_m2_before = check_census_oracle(
        declared_m2, executed_after_m2, executed_before=executed_before_m2
    )
    check(res_m2_before["verdict"] == "RED" and res_m2_before["l2_pass"] is False,
          f"[M2/before] verdict {res_m2_before['verdict']} != RED | L2 {res_m2_before['l2_pass']!r} != False")
    check(res_m2_before["l2_status"] == "measured",
          f"[M2/before] l2_status {res_m2_before['l2_status']!r} != 'measured'")
    # 대조군 — before 미제공이면 같은 삭제를 ★못 잡는다★ (정직 자인의 실증)
    res_m2_nobefore = check_census_oracle(declared_m2, executed_after_m2)
    check(res_m2_nobefore["verdict"] == "PASS" and res_m2_nobefore["l2_pass"] is None,
          f"[M2/no-before] 대조군 형상 변화: {res_m2_nobefore['verdict']} / {res_m2_nobefore['l2_pass']!r}")
    check(res_m2_nobefore["l2_status"] == "not_measured",
          f"[M2/no-before] l2_status {res_m2_nobefore['l2_status']!r} != 'not_measured' (미측정 은폐)")

    # M4: 유령 선언
    # D = {유령}, X = {} → L1 실패
    declared_ghost = [("구현", "fake-check", "phantom.py")]
    executed_none = []
    res_m4 = check_census_oracle(declared_ghost, executed_none)
    check(res_m4["verdict"] == "RED" and not res_m4["l1_pass"],
          f"[M4] 유령 선언 미검출: verdict {res_m4['verdict']} != RED")

    # ────────────────────── 정상 케이스 (M5′ 제외: target 성분 탈락 canonicalizer) ──────────────────────
    # D = {(구현, lint, main.py), (구현, test, main.py)}
    # X = {(구현, lint, main.py), (구현, test, main.py)}
    # → L1 OK, 판정 PASS
    declared_ok = [("구현", "lint", "main.py"), ("구현", "test", "main.py")]
    executed_ok = [("구현", "lint", "main.py"), ("구현", "test", "main.py")]
    res_ok = check_census_oracle(declared_ok, executed_ok)
    check(res_ok["verdict"] == "PASS" and res_ok["l1_pass"],
          f"[정상] verdict {res_ok['verdict']} != PASS")
    check(res_ok["l2_pass"] is None and res_ok["l2_status"] == "not_measured",
          f"[정상] 미측정 L2 가 측정값처럼 방출됨: {res_ok['l2_pass']!r} / {res_ok['l2_status']!r}")

    # ────────────────────── INPUT: loader fail-closed (F-CR-001) ──────────────────────
    # ★negative control★ — 미지원 확장자 / 경로 부재 / 형상 위반 / 파싱 실패 어느 것도
    #   PASS(exit 0) 가 아님을 exit code 로 실증한다. 양성 대조로 정상 입력은 여전히 판정된다
    #   (fail-closed 가 전부를 RED 로 뭉개는 무차별 게이트가 아님을 보인다).
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        good_payload = json.dumps([["구현", "lint", "main.py"]], ensure_ascii=False)
        good = tdp / "d.json"
        good.write_text(good_payload, encoding="utf-8")
        yaml_like = tdp / "d.yaml"          # 내용 동일, 확장자만 미지원
        yaml_like.write_text(good_payload, encoding="utf-8")
        bad_shape = tdp / "bad.json"        # 2 성분 (3 성분 위반)
        bad_shape.write_text(json.dumps([["구현", "lint"]], ensure_ascii=False), encoding="utf-8")
        broken = tdp / "broken.json"        # JSON 도 JSONL 도 아님
        broken.write_text("{not json", encoding="utf-8")
        empty_list = tdp / "empty.json"     # 해석은 되지만 D = ∅
        empty_list.write_text("[]", encoding="utf-8")

        def _run(argv):
            """main() 을 stdout 격리 실행 → exit code 만 회수."""
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(argv)
            return rc

        for label, path in (
            ("미지원 확장자(.yaml)", yaml_like),
            ("경로 부재", tdp / "nope.json"),
            ("형상 위반(2성분)", bad_shape),
            ("파싱 실패", broken),
        ):
            rc_bad = _run(["--declared-spec", str(path), "--executed-manifest", str(good)])
            check(rc_bad == 1,
                  f"[INPUT] {label} → exit {rc_bad} != 1 (loader fail-open 재발)")

        rc_empty = _run(["--declared-spec", str(empty_list), "--executed-manifest", str(good)])
        check(rc_empty == 3,
              f"[INPUT] 빈 리스트 → exit {rc_empty} != 3 (vacuous PASS 재발)")

        rc_pos = _run(["--declared-spec", str(good), "--executed-manifest", str(good)])
        check(rc_pos == 0,
              f"[INPUT] 양성 대조(정상 입력) → exit {rc_pos} != 0 (무차별 RED)")

    if failures:
        print("[check_census_oracle --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[check_census_oracle --self-test] PASS "
        "(ⓐ=항등 OK; ⓑ-lane=다름 OK; ⓑ-check_class=다름 OK; ⓑ-target=다름 OK; "
        "ⓒ=INCONCLUSIVE OK; ⓓ=vacuous-D INCONCLUSIVE OK; M1=RED OK; "
        "M2/before=RED OK & M2/no-before=미검출 자인 OK; M4=RED OK; 정상=PASS(L2 not_measured) OK; "
        "INPUT=미지원확장자/부재/형상/파싱 4종 exit1 OK & 빈리스트 exit3 OK & 양성대조 exit0 OK)"
    )
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="AC-4 검사량 oracle (L1 정합 + L2 보존)"
    )
    p.add_argument("--declared-spec", default=None,
                   help="모델 선언 D — JSON 리스트 또는 JSONL (.json/.jsonl). "
                        "★YAML 미지원★ (stdlib-only 불변식). 해석 실패 = RED")
    p.add_argument("--executed-manifest", default=None,
                   help="실행 기록 X(after) — JSON 리스트 또는 JSONL (.json/.jsonl). 해석 실패 = RED")
    p.add_argument("--executed-before", default=None,
                   help="실행 기록 X(before) 스냅샷 (.json/.jsonl). "
                        "주면 L2 보존을 ★실측★, 안 주면 L2 = not_measured")
    p.add_argument("--self-test", action="store_true", help="oracle self-test")

    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    # ★fail-closed 로드★ — 구 판본의 `except Exception: pass` 삼킴을 제거했다.
    #   경로 오타 / 미지원 확장자 / 파싱 실패 / 형상 위반은 전부 RED(exit 1) 이며,
    #   해석은 됐는데 D 가 비면 vacuous-D floor 가 INCONCLUSIVE(exit 3) 를 낸다.
    try:
        declared = load_units(args.declared_spec, "--declared-spec") if args.declared_spec else []
        executed = load_units(args.executed_manifest, "--executed-manifest") if args.executed_manifest else []
        before = load_units(args.executed_before, "--executed-before") if args.executed_before else None
    except InputError as exc:
        json_err = {
            "gate_id": "NG-1",
            "verdict": "RED",
            "exit_code": 1,
            "reason": "INPUT_UNRESOLVED — %s" % exc,
            "l1_pass": None,
            "l2_pass": None,
            "l2_status": "not_measured",
            "trace": {
                "declared_count": None,
                "executed_count": None,
                "executed_before_count": None,
                "lane_count": None,
                "input_error_code": exc.code,
            },
            "identity_probe": {"source": "cli", "input_error": exc.detail},
        }
        print(json.dumps(json_err, ensure_ascii=False), file=sys.stdout)
        return 1

    result = check_census_oracle(declared, executed, executed_before=before)
    json_out = gate_result_to_json(result)
    print(json.dumps(json_out, ensure_ascii=False), file=sys.stdout)

    return json_out["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
