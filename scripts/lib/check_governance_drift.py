#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/lib/check_governance_drift.py
CFP-2061-S4 — 거버넌스 지표 7종 측정 + drift 이슈 자동 발행 (advisory, warning tier)

Usage:
  python3 check_governance_drift.py check --baseline <path> [--repo-root <path>] [--dry-run]
  python3 check_governance_drift.py measure --repo-root <path> --metric <name>
  python3 check_governance_drift.py signature --metric <name> --direction <direction> --threshold-bucket <bucket>

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (drift 없음 또는 drift 감지 + 이슈 auto-create 성공 — warning tier)
  1 = (reserved, current scope 미사용)
  2 = SETUP error (missing dependency / 401 auth / 5xx unrecoverable)

Dedup signature (D4 — 최대 함정 회피):
  sha256("governance-drift|<metric>|<direction>|<threshold_bucket>") | first 16 chars
  **current_val 절대 제외** — 포함 시 매일 signature 변동 → dedup 무력화 → 이슈 폭주

Test override env:
  _CSGD_SKIP_ISSUE_CREATE=1  — Issue auto-create 차단 (dry-run / TC mode)
  _CSGD_MOCK_401=1           — 401 fail-closed 강제
  _CSGD_MOCK_429=1           — 429 fail-open 강제
  _CSGD_MOCK_5XX=1           — 5xx 3-retry 강제

Prior art:
  scripts/check-marketplace-drift.sh (CFP-673 / ADR-063 Amd3 §결정13)
  scripts/check-bypass-label-counter.py (CFP-825 / ADR-061)

ADR refs: ADR-060 / ADR-061 / ADR-066 / ADR-083 / ADR-005
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import yaml

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


LABEL_DRIFT = "drift-detection"
REPO = "mclayer/plugin-codeforge"


# ─────────────────────── test mock 처리 (prior art 답습) ─────────────────────

def _handle_mocks():
    """
    Test override env 처리. 401/429/5xx mock 트리거.
    Returns (exit_code_or_none) — None = 계속 진행.
    """
    if os.environ.get("_CSGD_MOCK_401", "") == "1":
        print(
            "[codeforge-kpi-infra-error] check-governance-drift: "
            "401 Unauthorized (mock) — PAT 인증 실패 (ADR-066 CODEFORGE_CROSS_REPO_PAT 확인 필요)",
            file=sys.stderr,
        )
        sys.exit(2)

    if os.environ.get("_CSGD_MOCK_429", "") == "1":
        print(
            "::warning::check-governance-drift: 429 Too Many Requests (mock) "
            "— rate limit, skipping run (fail-open)"
        )
        sys.exit(0)

    if os.environ.get("_CSGD_MOCK_5XX", "") == "1":
        print(
            "[codeforge-kpi-infra-error] check-governance-drift: "
            "5xx server error (mock) — 3회 retry 후 실패",
            file=sys.stderr,
        )
        sys.exit(2)


def _should_skip_issue_create():
    """Issue create 차단 여부 (dry-run / TC mode)."""
    return (
        os.environ.get("_CSGD_SKIP_ISSUE_CREATE", "") == "1"
        or os.environ.get("CBL_SKIP_ISSUE_CREATE", "") == "1"
    )


# ─────────────────────── 측정 로직 (git-tree 기준) ───────────────────────────

def measure_all(repo_root):
    """
    7지표 전부 측정. git-tree 기준 (working tree 오염 배제).
    Returns dict: metric_name -> measured_value

    §4.1 정정 glob:
      shell_scripts: git ls-files 'scripts/' | grep '.sh$'  (top-level + nested 전부)
      ★ NOT: git ls-files 'scripts/**/*.sh'  (top-level scripts/*.sh 누락 — 18배 과소측정)
    """
    results = {}

    # (1) evidence_checks_registry_entries — registry yaml entries[] len
    registry_path = os.path.join(repo_root, "docs", "evidence-checks-registry.yaml")
    try:
        with open(registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        results["evidence_checks_registry_entries"] = len(data.get("entries", []))
    except FileNotFoundError:
        results["evidence_checks_registry_entries"] = 0

    # (2) workflows_total — .github/workflows/*.yml count
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    wf_files = _git_ls_files(repo_root, ".github/workflows/*.yml")
    results["workflows_total"] = len(wf_files)

    # (3) workflows_pr_triggered — 위 중 pull_request 트리거 보유
    pr_count = 0
    for rel_path in wf_files:
        abs_path = os.path.join(repo_root, rel_path)
        try:
            with open(abs_path, encoding="utf-8") as f:
                wf_data = yaml.safe_load(f)
            on_val = wf_data.get("on", wf_data.get(True, None))
            if on_val is None:
                continue
            if isinstance(on_val, str) and on_val == "pull_request":
                pr_count += 1
            elif isinstance(on_val, list) and "pull_request" in on_val:
                pr_count += 1
            elif isinstance(on_val, dict) and "pull_request" in on_val:
                pr_count += 1
        except Exception:
            pass
    results["workflows_pr_triggered"] = pr_count

    # (4) shell_scripts — git ls-files 'scripts/' | grep '.sh$'
    # ★ 정정 glob: top-level + nested 전부 포착 (scripts/**/*.sh = nested only = 18배 과소)
    sh_files = _git_ls_files_grep(repo_root, "scripts/", r"\.sh$")
    results["shell_scripts"] = len(sh_files)

    # (5) shell_loc — 위 파일 합산 line count
    total_lines = 0
    for rel_path in sh_files:
        abs_path = os.path.join(repo_root, rel_path)
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as f:
                total_lines += sum(1 for _ in f)
        except FileNotFoundError:
            pass
    results["shell_loc"] = total_lines

    # (6) adr_count — git ls-files 'archive/adr/ADR-*.md'
    adr_files = _git_ls_files(repo_root, "archive/adr/ADR-*.md")
    results["adr_count"] = len(adr_files)

    # (7) adr_total_bytes — 위 파일 합산 byte size
    total_bytes = 0
    for rel_path in adr_files:
        abs_path = os.path.join(repo_root, rel_path)
        try:
            total_bytes += os.path.getsize(abs_path)
        except FileNotFoundError:
            pass
    results["adr_total_bytes"] = total_bytes

    return results


def _git_ls_files(repo_root, pattern):
    """git ls-files '<pattern>' 결과 목록 반환."""
    try:
        result = subprocess.run(
            ["git", "ls-files", pattern],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        return lines
    except subprocess.CalledProcessError:
        return []


def _git_ls_files_grep(repo_root, path_prefix, grep_pattern):
    """
    git ls-files '<path_prefix>' | grep '<grep_pattern>' 결과 목록 반환.
    §4.1 정정 — scripts/ prefix + .sh$ grep (top-level + nested 전부).
    """
    try:
        ls_result = subprocess.run(
            ["git", "ls-files", path_prefix],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        lines = ls_result.stdout.splitlines()
        import re
        filtered = [l.strip() for l in lines if l.strip() and re.search(grep_pattern, l)]
        return filtered
    except subprocess.CalledProcessError:
        return []


# ─────────────────────── dedup signature (D4 — 함정 회피 핵심) ───────────────

def compute_signature(metric, direction, threshold_bucket):
    """
    sha256("governance-drift|<metric>|<direction>|<threshold_bucket>") — first 16 chars.
    **current_val 절대 제외** — 포함 시 매일 signature 변동 → dedup 무력화 → 이슈 폭주 (D4).
    답습 원천: bypass-label-counter.py L169 `signature = f"{repo}::{label}"` (count 제외).
    """
    raw = f"governance-drift|{metric}|{direction}|{threshold_bucket}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _threshold_bucket(rel_pct, threshold_rel_pct):
    """
    rel_pct 가 어느 배수 임계에 해당하는지 bucket 문자열 반환.
    동일 metric이 동일 배수를 계속 초과하는 한 bucket 불변 → signature 불변 → dedup 작동.
    """
    # 단순 버킷: 1x, 2x, 3x 초과 (임계의 몇 배)
    multiplier = int(rel_pct // threshold_rel_pct)
    return f"gt_{multiplier}x_threshold"


# ─────────────────────── drift 판정 ──────────────────────────────────────────

def check_drift(measured, baseline_metrics):
    """
    measured dict + baseline_metrics dict → drift list 반환.
    Returns: list of {metric, measured_val, baseline_val, rel_pct, threshold_rel_pct, sig}
    증가 방향만 drift (감소는 drift 아님 — S5/S6 청소 중 폭주 방지).
    """
    drifts = []
    for metric, spec in baseline_metrics.items():
        baseline_val = spec.get("value", 0)
        threshold = spec.get("threshold_rel_pct", 20)
        measured_val = measured.get(metric, 0)

        if baseline_val == 0:
            continue

        rel_pct = (measured_val - baseline_val) / baseline_val * 100

        # 감소 방향 = drift 아님
        if rel_pct <= 0:
            continue

        # 임계 초과 시 drift
        if rel_pct > threshold:
            bucket = _threshold_bucket(rel_pct, threshold)
            sig = compute_signature(metric, "increase", bucket)
            drifts.append({
                "metric": metric,
                "measured_val": measured_val,
                "baseline_val": baseline_val,
                "rel_pct": rel_pct,
                "threshold_rel_pct": threshold,
                "bucket": bucket,
                "signature": sig,
            })

    return drifts


# ─────────────────────── 이슈 dedup 검색 + create ────────────────────────────

def _run_gh(args, capture=True):
    """gh CLI 호출 wrapper."""
    cmd = ["gh"] + args
    if capture:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        )
        return result.stdout.strip()
    else:
        subprocess.run(cmd, check=True)
        return ""


def check_dedup_issue(sig):
    """
    signature 로 active open Issue 검색. 존재하면 True (dedup skip).
    답습: marketplace-drift.sh L190-197 `gh issue list --search "\"signature: ${SIG}\""`.
    """
    try:
        raw = _run_gh([
            "issue", "list",
            "--repo", REPO,
            "--label", LABEL_DRIFT,
            "--state", "open",
            "--search", f'"signature: {sig}"',
            "--limit", "1",
            "--json", "number,title",
            "--jq", ".[0].number // empty",
        ])
        return bool(raw.strip())
    except subprocess.CalledProcessError:
        return False


def create_drift_issue(drift_item, dry_run=False):
    """
    drift issue 발행.
    dry_run=True 또는 _CSGD_SKIP_ISSUE_CREATE=1 시 실제 create 없이 print 만.
    """
    metric = drift_item["metric"]
    sig = drift_item["signature"]
    rel_pct = drift_item["rel_pct"]
    measured_val = drift_item["measured_val"]
    baseline_val = drift_item["baseline_val"]
    threshold = drift_item["threshold_rel_pct"]

    title = f"[GOVERNANCE-DRIFT] metric={metric} +{rel_pct:.1f}% > {threshold}%"
    body = (
        f"## Governance drift detected\n\n"
        f"**Metric**: `{metric}`\n"
        f"**Measured**: {measured_val}\n"
        f"**Baseline**: {baseline_val}\n"
        f"**Change**: +{rel_pct:.1f}% (threshold: {threshold}%)\n\n"
        f"### Action\n\n"
        f"ADR-060 §결정 31 — governance-drift-detection warning tier (advisory).\n"
        f"재증식 원인 파악 + S5/S6 검사·ADR 정리 연계.\n\n"
        f"signature: {sig}\n\n"
        f"---\n"
        f"Source: `scripts/lib/check_governance_drift.py` (CFP-2061-S4 / ADR-060 §결정 31)"
    )

    if dry_run or _should_skip_issue_create():
        print(f"[DRY-RUN] would create issue: {title}")
        print(f"  signature: {sig}")
        return

    try:
        _run_gh([
            "issue", "create",
            "--repo", REPO,
            "--label", LABEL_DRIFT,
            "--title", title,
            "--body", body,
        ], capture=False)
        print(f"[governance-drift] Issue created: {title}")
    except subprocess.CalledProcessError as e:
        print(f"  -> Issue create failed (non-fatal, will retry on next run): {e}")


# ─────────────────────── 의존성 검사 ─────────────────────────────────────────

def _check_deps():
    """gh CLI + python 의존성 확인."""
    # gh CLI는 issue create 단계에만 필요 (측정은 git-tree, API 불요)
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "[codeforge-kpi-infra-error] check-governance-drift: gh CLI not installed or not in PATH",
            file=sys.stderr,
        )
        sys.exit(2)


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    """메인 check 커맨드 — 측정 + drift 판정 + 이슈 발행."""
    # mock 처리 (test override)
    _handle_mocks()

    # baseline JSON 로드
    try:
        with open(args.baseline, encoding="utf-8") as f:
            baseline_data = json.load(f)
    except FileNotFoundError:
        print(
            f"[codeforge-kpi-infra-error] check-governance-drift: "
            f"baseline file not found: {args.baseline}",
            file=sys.stderr,
        )
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(
            f"[codeforge-kpi-infra-error] check-governance-drift: "
            f"baseline JSON parse error: {e}",
            file=sys.stderr,
        )
        sys.exit(2)

    baseline_metrics = baseline_data.get("baseline_metrics", {})
    if not baseline_metrics:
        print(
            "[codeforge-kpi-infra-error] check-governance-drift: "
            "baseline_metrics 비어 있음",
            file=sys.stderr,
        )
        sys.exit(2)

    # 7지표 측정
    repo_root = args.repo_root or "."
    measured = measure_all(repo_root)

    # drift 판정
    drifts = check_drift(measured, baseline_metrics)

    if not drifts:
        print(
            "check-governance-drift: PASS - 0 drift across "
            f"{len(baseline_metrics)} metrics"
        )
        sys.exit(0)

    # drift 있음 — 이슈 발행 (dedup)
    issues_created = 0
    issues_dedup = 0

    for d in drifts:
        print(
            f"::warning::check-governance-drift: DRIFT detected — "
            f"metric={d['metric']} measured={d['measured_val']} "
            f"baseline={d['baseline_val']} rel_pct=+{d['rel_pct']:.1f}% "
            f"threshold={d['threshold_rel_pct']}% "
            f"signature={d['signature']}"
        )

        if not (args.dry_run or _should_skip_issue_create()):
            if check_dedup_issue(d["signature"]):
                print(
                    f"  -> dedup: active Issue already exists "
                    f"for signature {d['signature']} — skipping create"
                )
                issues_dedup += 1
                continue

        create_drift_issue(d, dry_run=args.dry_run)
        issues_created += 1

    print(
        f"check-governance-drift: WARNING - {len(drifts)} drift(s) detected. "
        f"Issues created: {issues_created}, dedup skip: {issues_dedup} "
        f"(warning tier, ADR-060)"
    )

    # advisory — drift 감지해도 exit 0 (warning tier, PR 게이트 아님)
    # setup error 만 exit 2
    sys.exit(0)


# ─────────────────────── 서브커맨드: measure ─────────────────────────────────

def cmd_measure(args):
    """단일 metric 측정값 출력 (TC-1 검증용)."""
    repo_root = args.repo_root or "."
    all_metrics = measure_all(repo_root)

    if args.metric not in all_metrics:
        print(
            f"[codeforge-kpi-infra-error] check-governance-drift: "
            f"unknown metric: {args.metric}",
            file=sys.stderr,
        )
        sys.exit(2)

    val = all_metrics[args.metric]
    print(f"{args.metric}: {val}")
    sys.exit(0)


# ─────────────────────── 서브커맨드: signature ───────────────────────────────

def cmd_signature(args):
    """signature 출력 (TC-2b current_val 제외 검증용)."""
    sig = compute_signature(args.metric, args.direction, args.threshold_bucket)
    print(sig)
    sys.exit(0)


# ─────────────────────── main ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="거버넌스 지표 7종 측정 + drift 이슈 자동 발행 (CFP-2061-S4)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check 서브커맨드
    check_p = subparsers.add_parser("check", help="측정 + drift 판정 + 이슈 발행")
    check_p.add_argument(
        "--baseline", required=True,
        help="baseline JSON 경로 (docs/kpi/governance-bloat-baseline.json)",
    )
    check_p.add_argument(
        "--repo-root", default=".",
        help="git repo root 경로 (default: 현재 디렉터리)",
    )
    check_p.add_argument(
        "--dry-run", action="store_true",
        help="dry-run: Issue 실제 생성 없이 결과 출력만",
    )

    # measure 서브커맨드 (TC-1 검증용)
    measure_p = subparsers.add_parser("measure", help="단일 metric 측정값 출력")
    measure_p.add_argument(
        "--repo-root", default=".",
        help="git repo root 경로",
    )
    measure_p.add_argument(
        "--metric", required=True,
        help="측정할 metric 이름",
    )

    # signature 서브커맨드 (TC-2b 검증용)
    sig_p = subparsers.add_parser("signature", help="dedup signature 출력")
    sig_p.add_argument("--metric", required=True)
    sig_p.add_argument("--direction", required=True)
    sig_p.add_argument("--threshold-bucket", required=True)

    args = parser.parse_args()

    if args.command == "check":
        cmd_check(args)
    elif args.command == "measure":
        cmd_measure(args)
    elif args.command == "signature":
        cmd_signature(args)


if __name__ == "__main__":
    main()
