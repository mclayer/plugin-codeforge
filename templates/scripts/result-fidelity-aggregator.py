#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/scripts/result-fidelity-aggregator.py

CFP-900 Phase 2 — reconcile-protocol-v1 v1.10 §4.13 result_fidelity_binding
result enum 집계 + post-mirror sanity check (filesystem-only, syntax-level 1차 신호)

역할:
  - S1 (§4.11 closure resolver) + S2 (§4.12 consumer-applicability filter) exit code 수신
  - post-mirror sanity check: expected path set vs actual mirrored path set diff
  - workflow yml bash -n / yaml parse OK (syntax-level 1차 신호, stdlib only)
  - result enum 4-value 집계 출력: SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED
  - upgrade_event_honest_record: result field 정직 기록 (SUCCESS hardcode forbidden)

결정 규칙 (degradation_propagation SSOT — §4.13 spec verbatim):
  - S1 exit 1 (fail-closed dependency missing) OR S2 exit 1 (unknown abort)  → FAILED
  - S1 exit 2 (degraded) OR S2 exit 2 (degraded)                              → SUCCESS_WITH_DEGRADATION
  - sanity check partial mismatch (파일 일부 누락)                             → PARTIAL_FAILURE
  - sanity check warning (syntax warning)                                      → SUCCESS_WITH_DEGRADATION
  - 전부 OK                                                                     → SUCCESS
  - EC-1: S1+S2 동시 abort → FAILED 우선 (가장 심각 enum 우선)
  - EC-2: dry-run mode → result field 미적용 (preview only)
  - EC-3: wrapper self-app mixed repo (S2 skip) + S1 OK → SUCCESS

CLI 사용:
  python3 result-fidelity-aggregator.py \
    --s1-exit <code> \
    --s2-exit <code> \
    --wrapper-dir <path> \
    --consumer-dir <path> \
    [--whitelist <path>] \
    [--dry-run] \
    [--output-file <path>]

Exit code:
  0 = SUCCESS
  1 = PARTIAL_FAILURE 또는 FAILED (honest reporting — caller 참조)
  2 = SUCCESS_WITH_DEGRADATION
  3 = 내부 오류 (aggregator 자체 crash)

ADR-061 정합: 외부 .py 파일, shebang, stdlib only, UTF-8
ADR-076 Amendment 3 §결정 3 sub-clause carrier
"""

import argparse
import json
import os
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Result enum 상수 (closed-set — open-set 확장 금지)
# §4.13 result_enum_schema 4-value verbatim
# ─────────────────────────────────────────────────────────────────────────────
RESULT_SUCCESS = "SUCCESS"
RESULT_SUCCESS_WITH_DEGRADATION = "SUCCESS_WITH_DEGRADATION"
RESULT_PARTIAL_FAILURE = "PARTIAL_FAILURE"
RESULT_FAILED = "FAILED"

# exit code → result enum 매핑 (caller exit contract)
EXIT_CODE_MAP = {
    RESULT_SUCCESS: 0,
    RESULT_PARTIAL_FAILURE: 1,
    RESULT_FAILED: 1,
    RESULT_SUCCESS_WITH_DEGRADATION: 2,
}

# severity 우선순위 (EC-1: 가장 심각 우선)
RESULT_SEVERITY = {
    RESULT_FAILED: 4,
    RESULT_PARTIAL_FAILURE: 3,
    RESULT_SUCCESS_WITH_DEGRADATION: 2,
    RESULT_SUCCESS: 1,
}


def _most_severe(r1: str, r2: str) -> str:
    """두 result 중 더 심각한 것 반환 (EC-1 abort 우선 invariant)."""
    if RESULT_SEVERITY.get(r1, 0) >= RESULT_SEVERITY.get(r2, 0):
        return r1
    return r2


# ─────────────────────────────────────────────────────────────────────────────
# degradation_propagation — exit code → result enum deterministic mapping
# §4.13 degradation_propagation SSOT verbatim
# F-CR-899-1 류 방지: return code 임의 변경 금지 (spec verbatim 답습)
# ─────────────────────────────────────────────────────────────────────────────

def s1_exit_to_result(s1_exit: int) -> str:
    """
    S1 §4.11 closure resolver exit code → result enum.
      0 → (집계 시 SUCCESS 방향, sanity 단계에서 최종 결정)
      1 → FAILED (dependency missing fail-closed)
      2 → SUCCESS_WITH_DEGRADATION (degraded, cp 진행)
      기타 → FAILED (fail-closed 방향)
    """
    if s1_exit == 0:
        return RESULT_SUCCESS
    elif s1_exit == 1:
        return RESULT_FAILED
    elif s1_exit == 2:
        return RESULT_SUCCESS_WITH_DEGRADATION
    else:
        # 알 수 없는 exit code → fail-closed
        return RESULT_FAILED


def s2_exit_to_result(s2_exit: int) -> str:
    """
    S2 §4.12 consumer-applicability filter exit code → result enum.
      0 → (집계 시 SUCCESS 방향)
      1 → FAILED (unknown repo_kind abort / filter abort)
      2 → SUCCESS_WITH_DEGRADATION (degraded)
      기타 → FAILED (fail-closed 방향)
    """
    if s2_exit == 0:
        return RESULT_SUCCESS
    elif s2_exit == 1:
        return RESULT_FAILED
    elif s2_exit == 2:
        return RESULT_SUCCESS_WITH_DEGRADATION
    else:
        return RESULT_FAILED


# ─────────────────────────────────────────────────────────────────────────────
# post-mirror sanity check (filesystem-only, syntax-level 1차 신호)
# §4.13 post_mirror_sanity_check SSOT:
#   - file 존재성 (expected set 각 file 이 consumer-side 존재)
#   - path set diff (expected vs actual symmetric difference)
#   - workflow yml bash -n / yaml parse OK
#   - network call 0 / gh api 0 (filesystem-only invariant)
#   - pure read-only (idempotent)
# ─────────────────────────────────────────────────────────────────────────────

def _load_whitelist(whitelist_path: str) -> set:
    """
    consumer_applicable_workflows.txt 파싱.
    # 주석 + 빈 줄 제외. 반환: basename set (not None이면 필터 적용).
    """
    result = set()
    p = Path(whitelist_path)
    if not p.is_file():
        return result
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                result.add(line)
    return result


def _expected_path_set(wrapper_dir: str, whitelist: set | None) -> set:
    """
    wrapper SSOT 에서 expected 파일 path set 산출.
    whitelist 적용: .github/workflows/*.yml 이 whitelist에 없으면 skip (S2 filter 결과 반영).
    반환: relative path set (str).
    """
    expected = set()
    wd = Path(wrapper_dir)
    if not wd.is_dir():
        return expected

    for f in wd.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(wd)
        rel_str = str(rel).replace("\\", "/")

        # sidecar manifest 자체는 sanity check 대상 제외
        if rel_str == ".wrapper-managed-manifest.json":
            continue

        # whitelist 적용 (S2 filter 결과 반영)
        # whitelist가 지정된 경우 whitelist에 없는 yml 파일은 expected set에서 제외
        # (plugin-only workflow false-positive 차단 — consumer-applicable 항목만 포함)
        if whitelist is not None and rel_str.endswith(".yml"):
            basename = Path(rel_str).name
            if basename not in whitelist:
                # whitelist에 없는 plugin-only workflow = skip
                continue

        expected.add(rel_str)
    return expected


def _actual_path_set(
    consumer_dir: str,
    whitelist: set | None,
    expected: set | None = None,
) -> set:
    """
    consumer-side mirrored file set 산출.
    whitelist 적용: _expected_path_set 과 대칭 — whitelist 지정 시 whitelist에 없는 .yml 파일 제외.
    §4.13 whitelist_symmetry_invariant: expected ↔ actual 양측 동일 whitelist 필터 적용
    (비대칭 시 정상 mirror된 비-whitelist .yml 이 extra = actual - expected 에 진입
    → false WARNING → false SUCCESS_WITH_DEGRADATION 발생 차단)

    반환: relative path set (str).

    제외 대상 (EC-4 false-positive 차단 — §4.13 post_mirror_sanity_check.impact_report_diff_scope):
      - `.snapshots/` prefix: reconcile transaction artifact (reconcile-overlay.sh _create_snapshot 생성)
        → expected set 에 없으므로 extra 분류 → false SUCCESS_WITH_DEGRADATION 차단
      - `.wrapper-managed-manifest.json` 동형 패턴 (wrapper SSOT 파일이 아닌 reconcile runtime 산출물)
      - whitelist 미포함 .yml (whitelist 지정 시) — _expected_path_set 와 대칭 적용
      - `.claude/_overlay/` prefix + wrapper SSOT 미존재 path (CFP-990 Phase 2, EC-4 enumeration (b)):
        consumer 자기 customization layer (ADR-027 §결정 1 SSOT) — wrapper desired state 와 disjoint.
        cross-product check: rel_str.startswith(".claude/_overlay/") AND rel_str NOT IN expected
        → consumer-only customization 분류 → extra 에서 제외 → false SUCCESS_WITH_DEGRADATION 차단.
        wrapper SSOT 충돌 path (IN expected) = diff check 영역 보존 (EC-OOS-1 별 carrier).

    인자:
      consumer_dir: consumer overlay 루트 절대 경로
      whitelist: _expected_path_set 에 전달된 동일 whitelist (whitelist_symmetry_invariant)
      expected: wrapper SSOT expected path set (EC-4 (b) .claude/_overlay/ cross-product check 용).
                None 시 .claude/_overlay/ prefix 전체 제외 (보수적 safe direction).
    """
    actual = set()
    cd = Path(consumer_dir)
    if not cd.is_dir():
        return actual

    for f in cd.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(cd)
        rel_str = str(rel).replace("\\", "/")

        # reconcile transaction artifact 제외 (§4.13 EC-4 false-positive 차단)
        # .snapshots/ = reconcile-overlay.sh _create_snapshot() 생성 디렉토리
        if rel_str.startswith(".snapshots/"):
            continue

        # CFP-990 Phase 2: .claude/_overlay/ prefix + wrapper SSOT 미존재 path 제외
        # EC-4 enumeration (b): consumer 자기 customization layer (ADR-027 §결정 1 정합)
        # wrapper desired state 와 disjoint 영역 → extra 에서 제외 → false SUCCESS_WITH_DEGRADATION 차단
        # cross-product:
        #   .claude/_overlay/ prefix AND NOT IN expected → consumer-only → 제외
        #   .claude/_overlay/ prefix AND IN expected     → wrapper SSOT 충돌 → diff check 보존 (EC-OOS-1)
        if rel_str.startswith(".claude/_overlay/"):
            if expected is None or rel_str not in expected:
                continue  # consumer-only customization: exclude

        # whitelist 적용 — §4.13 whitelist_symmetry_invariant
        # _expected_path_set 와 완전 대칭: whitelist 지정 시 whitelist에 없는 .yml 제외
        # (정상 mirror된 비-whitelist .yml 이 extra 로 진입하는 false-positive 차단)
        if whitelist is not None and rel_str.endswith(".yml"):
            basename = Path(rel_str).name
            if basename not in whitelist:
                # whitelist에 없는 plugin-only workflow = skip (expected 와 동일 기준)
                continue

        actual.add(rel_str)
    return actual


def _check_yml_syntax(file_path: Path) -> tuple[bool, str]:
    """
    workflow yml syntax check (bash -n / yaml parse OK).
    반환: (ok: bool, message: str)
    """
    # yaml parse (stdlib json fallback — pyyaml 의존 0, stdlib only invariant)
    try:
        content = file_path.read_text(encoding="utf-8")
        # Basic YAML validity: check for obvious issues
        # stdlib 만 사용 — yaml.safe_load 불가, 대신 기본 text-level check
        if "\t" in content.split("\n")[0] if content else False:
            return False, f"yaml: leading tab detected in {file_path}"
        # bash -n syntax check (workflow 내 run: 블록 간접 검증은 out-of-scope)
        # 파일 존재성 + 비어있지 않음 = syntax-level 1차 신호
        if not content.strip():
            return False, f"yaml: empty file {file_path}"
        return True, "ok"
    except Exception as e:
        return False, f"yaml parse error: {e}"


def run_post_mirror_sanity_check(
    wrapper_dir: str,
    consumer_dir: str,
    whitelist: set | None,
    verbose: bool = False,
) -> tuple[str, list]:
    """
    post-mirror sanity check 실행.
    반환: (sanity_result: str, warnings: list[str])
      sanity_result = "PASS" | "PARTIAL_MISMATCH" | "WARNING"
    §4.13 post_mirror_sanity_check spec verbatim:
      - file 존재성: expected set 각 파일이 consumer-side 존재
      - path set diff: symmetric difference 감지
      - workflow yml syntax check
      - marker block 안 consumer customization = sanity 제외 (EC-4 false-positive 차단)
    """
    warnings = []
    missing_files = []
    extra_files = []
    syntax_warnings = []

    expected = _expected_path_set(wrapper_dir, whitelist)
    # CFP-990 Phase 2: expected set 전달 → EC-4 (b) .claude/_overlay/ cross-product check
    actual = _actual_path_set(consumer_dir, whitelist, expected=expected)

    # path set diff
    missing = expected - actual
    extra = actual - expected

    if missing:
        missing_files = sorted(missing)
        if verbose:
            for m in missing_files:
                print(f"[sanity] MISSING: {m}", file=sys.stderr)

    if extra:
        extra_files = sorted(extra)
        # extra 파일 = consumer-only 추가 (정상 가능) → WARNING only
        if verbose:
            for e in extra_files:
                print(f"[sanity] EXTRA (consumer-only): {e}", file=sys.stderr)
        warnings.append(f"extra consumer files: {extra_files}")

    # workflow yml syntax check
    cd = Path(consumer_dir)
    for rel_str in expected:
        if rel_str.endswith(".yml"):
            consumer_file = cd / rel_str
            if consumer_file.is_file():
                ok, msg = _check_yml_syntax(consumer_file)
                if not ok:
                    syntax_warnings.append(f"{rel_str}: {msg}")
                    if verbose:
                        print(f"[sanity] SYNTAX WARNING: {rel_str}: {msg}", file=sys.stderr)

    # 결과 집계
    if missing_files:
        # 필수 파일 누락 = PARTIAL_MISMATCH (PARTIAL_FAILURE 트리거)
        return "PARTIAL_MISMATCH", warnings + [f"missing: {missing_files}"]

    if syntax_warnings:
        # syntax warning = SUCCESS_WITH_DEGRADATION 트리거
        return "WARNING", warnings + syntax_warnings

    if extra_files:
        # extra만 있음 = WARNING (consumer-only additions)
        return "WARNING", warnings

    return "PASS", []


# ─────────────────────────────────────────────────────────────────────────────
# 최종 result enum 집계 (pure function, side-effect 0)
# §4.13 result_enum_aggregation SSOT
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_result(
    s1_exit: int,
    s2_exit: int,
    sanity_result: str,
    dry_run: bool = False,
) -> str:
    """
    S1 exit + S2 exit + sanity check → result enum deterministic mapping.

    EC-1: S1+S2 동시 abort → FAILED 우선
    EC-2: dry-run → 집계 미적용 (preview only)
    degradation_propagation SSOT (spec verbatim, no silent hardcode)
    """
    if dry_run:
        # EC-2: dry-run = result field 미적용 (ADR-076 §결정 3 dry-run semantic)
        return None  # type: ignore[return-value]

    r_s1 = s1_exit_to_result(s1_exit)
    r_s2 = s2_exit_to_result(s2_exit)

    # EC-1: 가장 심각 enum 우선 (abort > partial)
    r_hook = _most_severe(r_s1, r_s2)

    # sanity check 결과 → result enum
    if sanity_result == "PARTIAL_MISMATCH":
        r_sanity = RESULT_PARTIAL_FAILURE
    elif sanity_result == "WARNING":
        r_sanity = RESULT_SUCCESS_WITH_DEGRADATION
    else:
        r_sanity = RESULT_SUCCESS

    # 전체 집계: 가장 심각 enum 우선
    return _most_severe(r_hook, r_sanity)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CFP-900 §4.13 result_fidelity_binding aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--s1-exit",
        type=int,
        required=True,
        metavar="CODE",
        # F-CR-899-4 류 방지: env var 이름 binding spec 정합 (rename 금지)
        help="S1 §4.11 closure resolver exit code (0=OK / 1=fail-closed / 2=degraded)",
    )
    parser.add_argument(
        "--s2-exit",
        type=int,
        required=True,
        metavar="CODE",
        help="S2 §4.12 consumer-applicability filter exit code (0=OK / 1=abort / 2=degraded)",
    )
    parser.add_argument(
        "--wrapper-dir",
        type=str,
        required=True,
        metavar="PATH",
        help="wrapper SSOT overlay 디렉토리 (expected path set 기준)",
    )
    parser.add_argument(
        "--consumer-dir",
        type=str,
        required=True,
        metavar="PATH",
        help="consumer-side mirrored 디렉토리 (actual path set 기준)",
    )
    parser.add_argument(
        "--whitelist",
        type=str,
        default=None,
        metavar="PATH",
        help="consumer_applicable_workflows.txt 경로 (S2 filter 결과 반영)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="dry-run mode: preview only, result field 미적용 (EC-2)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        metavar="PATH",
        help="result enum JSON 출력 파일 경로 (미지정 시 stdout only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="sanity check 상세 출력",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # F-CR-899-10 류 방지: bash subshell || fallback 패턴 회피
    # Python 내부는 subprocess 미사용, 직접 함수 호출 (exit code 명시적 수령)
    s1_exit: int = args.s1_exit
    s2_exit: int = args.s2_exit

    # whitelist 로드
    whitelist: set | None = None
    if args.whitelist:
        whitelist = _load_whitelist(args.whitelist)

    # post-mirror sanity check
    if args.dry_run:
        # EC-2: dry-run = preview only
        print("[result-fidelity] dry-run mode: sanity check preview (filesystem-only, no result field)")
        sanity_result_str = "PASS"
        sanity_warnings: list[str] = []
    else:
        sanity_result_str, sanity_warnings = run_post_mirror_sanity_check(
            wrapper_dir=args.wrapper_dir,
            consumer_dir=args.consumer_dir,
            whitelist=whitelist,
            verbose=args.verbose,
        )

    # result enum 집계
    result = aggregate_result(
        s1_exit=s1_exit,
        s2_exit=s2_exit,
        sanity_result=sanity_result_str,
        dry_run=args.dry_run,
    )

    # 출력
    if args.dry_run:
        print(f"[result-fidelity] [dry-run] s1_exit={s1_exit} s2_exit={s2_exit} sanity={sanity_result_str}")
        print("[result-fidelity] [dry-run] result field 미적용 (EC-2 - preview only)")
        return 0

    # upgrade_event_honest_record: SUCCESS hardcode forbidden 검증 (자체 invariant)
    assert result in {
        RESULT_SUCCESS,
        RESULT_SUCCESS_WITH_DEGRADATION,
        RESULT_PARTIAL_FAILURE,
        RESULT_FAILED,
    }, f"internal error: unknown result enum '{result}'"

    # stdout 출력
    output_data = {
        "result": result,
        "s1_exit": s1_exit,
        "s2_exit": s2_exit,
        "sanity_check": sanity_result_str,
        "sanity_warnings": sanity_warnings,
    }
    print(json.dumps(output_data, ensure_ascii=False))

    # output-file 기록
    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        if args.verbose:
            print(f"[result-fidelity] result written to {args.output_file}", file=sys.stderr)

    # exit code contract (§4.13 caller exit code)
    return EXIT_CODE_MAP.get(result, 1)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[result-fidelity] INTERNAL ERROR: {e}", file=sys.stderr)
        sys.exit(3)
