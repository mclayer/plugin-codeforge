#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_ci_run_completeness.py — CFP-2926 NG-18 CI run completeness check.

기대 workflow 수 vs 실제 실행 run 수 대조:
  - Expected: `.github/workflows/*.yml` 파일 수 (push-triggered workflows)
  - Actual: `gh run list --commit <sha>` 로부터 실제 run 수
  - ★500+ run queue drop (>500 workflow runs queued → no further queuing): 큐에 들어가지도
    않아 로그에 오류가 안 뜬다 → run 수 대조만 유일 경로

CI tier (branch protection): **warning** (non-required, ADR-154 §결정 8)
  - 본 게이트는 신규 required context 가 아니다 (8-tuple unchanged)
  - gh CLI 미설치·미인증·오프라인 환경에서 상시 RED → warning tier 로 차단 없음
  - ★정직(honest ceiling)★: 오프라인 환경에서는 항상 RED 를 낸다. PR 을 차단하지 않으므로
    required 로 승격할 근거가 없다 (branch protection 정책 변경 대상 아님)

규정:
  - empty-target: expected 0 (workflow 없음) → INCONCLUSIVE (F-6′)
  - unknown-input: gh run list 조회 실패 → fail-closed RED (exec 실패, network 등)
  - PASS: expected == actual
  - RED: actual < expected (큐 drop 의심)

불변식:
  - --expected / --actual 주입 경로로 결정론 테스트 가능해야 함
  - commit SHA 미제공 → INCONCLUSIVE (없는 데 비교 불가)

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import glob
import json
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    yaml = None

from gate_verdict import (
    GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-18"


def _count_workflows(repo_root):
    """workflows 디렉토리에서 파일 개수 카운트.

    Returns: count of .yml/.yaml files
    """
    workflows_dir = os.path.join(repo_root, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        return 0

    workflows = glob.glob(os.path.join(workflows_dir, "*.yml")) + glob.glob(
        os.path.join(workflows_dir, "*.yaml")
    )
    return len(workflows)


def _get_actual_runs(commit_sha):
    """gh run list --commit <sha> 로부터 실제 run 수.

    Returns: (run_count, error_reason or None)
    """
    if not commit_sha:
        return 0, "commit_sha_not_provided"

    try:
        result = subprocess.run(
            ["gh", "run", "list", "--commit", commit_sha, "--json", "name"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
        )
        if result.returncode != 0:
            # gh command 실패 → unknown-input (network, auth 등)
            return 0, f"gh_command_failed: {result.stderr[:80]}"

        try:
            runs = json.loads(result.stdout)
            if isinstance(runs, list):
                return len(runs), None
            else:
                return 0, "gh_payload_invalid_type"
        except json.JSONDecodeError:
            return 0, "gh_payload_json_decode_error"

    except subprocess.TimeoutExpired:
        return 0, "gh_command_timeout"
    except FileNotFoundError:
        return 0, "gh_cli_not_found"
    except Exception as e:
        return 0, f"gh_command_error: {str(e)[:50]}"


def main(argv=None):
    """Main entry point.

    CLI:
      python check_ci_run_completeness.py --repo-root <path> [--commit <sha>] \
        [--expected <N>] [--actual <N>]

    Exit codes:
      0 = PASS (expected == actual)
      1 = RED (actual < expected or gh_command_failed)
      3 = INCONCLUSIVE (expected 0 / commit_sha 미제공)
    """
    parser = argparse.ArgumentParser(
        prog="check_ci_run_completeness.py",
        description="CI run completeness check (expected vs actual).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--commit", default=None, help="Git commit SHA")
    parser.add_argument(
        "--expected", type=int, default=None, help="Expected run count (override)"
    )
    parser.add_argument(
        "--actual", type=int, default=None, help="Actual run count (override)"
    )

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)

    # Expected count
    if args.expected is not None:
        expected_count = args.expected
    else:
        expected_count = _count_workflows(repo_root)

    # empty-target: expected 0 → INCONCLUSIVE (F-6′ 형판)
    if expected_count == 0:
        result = empty_target(
            gate_id=GATE_ID,
            reason="no_workflows_found",
            trace={"expected_count": 0},
            identity_probe={"repo_root": repo_root},
        )
        return emit(result)

    # Actual count: commit SHA 필요
    if args.actual is not None:
        actual_count = args.actual
        actual_error = None
    else:
        if not args.commit:
            result = empty_target(
                gate_id=GATE_ID,
                reason="commit_sha_not_provided",
                trace={"expected_count": expected_count},
                identity_probe={"repo_root": repo_root},
            )
            return emit(result)

        actual_count, actual_error = _get_actual_runs(args.commit)

    # unknown-input: gh command 실패
    if actual_error and args.actual is None:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=actual_error,
            trace={
                "expected_count": expected_count,
                "actual_count": actual_count,
            },
            identity_probe={
                "repo_root": repo_root,
                "commit": args.commit or "N/A",
            },
        )
        return emit(result)

    trace = {
        "expected_count": expected_count,
        "actual_count": actual_count,
    }
    if actual_error:
        trace["actual_error"] = actual_error

    # Comparison
    if actual_count < expected_count:
        # RED: 큐 drop 의심
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="ci_run_count_mismatch",
            trace=trace,
            identity_probe={
                "repo_root": repo_root,
                "commit": args.commit or "N/A",
            },
        )
        return emit(result)

    # PASS: expected == actual (또는 actual > expected 허용)
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="ci_run_count_complete",
        trace=trace,
        identity_probe={
            "repo_root": repo_root,
            "commit": args.commit or "N/A",
        },
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
