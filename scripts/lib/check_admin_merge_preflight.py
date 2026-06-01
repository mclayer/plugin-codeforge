#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CFP-1564 / ADR-113 Wave 2 mechanical wire — admin-merge pre-flight gate.

ADR-113 §결정 1 (5-step procedure) mechanical SSOT. ADR-073 §결정 1
verify-before-assert transition trigger `admin_merge_attempt` sub-domain
instantiation. ADR-045 §D-9 pattern_count 3 reach (CFP-1334 / CFP-1318 /
CFP-1495 super-class `admin_merge_action_required_force_attempt`) Mandatory
ADR escalation 산물.

Tier: warning (ADR-060 §결정 5 default — exit 0 on gate-block, advisory).

Mechanically implements ADR-113 §결정 1 5-step (Orchestrator `gh pr merge --admin`
attempt 직전 pre-flight gate):

  Step 1 — required check state enum fetch
      `gh pr checks <PR> --json name,state,bucket,link,description`
      모든 check state=SUCCESS (bucket=pass) → ALLOW. 비어있지 않으면 Step 2.
  Step 2 — ACTION_REQUIRED detection + 10-value abort_states_enum (closed-set)
      1+ check state 가 abort enum 영역 → ABORT.
      closed-set 외 value → fail-closed semantic (ABORT, fail-2).
  Step 3 — fresh commit trigger recovery procedure (output 으로 surface)
  Step 4 — re-verify (≤60s) — runtime Orchestrator 영역 (본 script = pre-flight
      single-shot verdict; re-verify loop 은 Orchestrator instrumentation/hook 영역)
  Step 5 — attempt cap=3 dual scope (per-PR AND per-Story) STOP + escalate

Head SHA verify (ADR-113 §결정 1 Step 1 verify-before-trust primitive):
  --head-sha 제공 시 PR head (gh pr view <PR> --json headRefOid) 와 비교.
  mismatch → ABORT (stale check — green checks 가 다른 commit 대상일 수 있음).

Bypass channel (ADR-113 §결정 4 / ADR-024 Amendment 6/8 §결정 6.A):
  `hotfix-bypass:admin-merge-preflight-gate` label 부착 시 → ALLOW + audit marker.
  5 lint chain (bypass-label-counter / per-plugin-cumulative-counter /
  bypass-justification-marker / cross-repo-bypass-counter /
  check-bypass-audit-comment.sh) 자동 covered (별 lint 신설 0).

Failure mode enum (ADR-113 §결정 5):
  fail-1 API call failure (gh unavailable / network / token / 429) → exit 2 meta-error
  fail-2 state enum unknown (closed-set 외) → fail-closed ABORT
  fail-3 re-trigger 후 ACTION_REQUIRED 잔존 → Step 5 attempt cap (Orchestrator loop)
  fail-4 silent bypass attempt → 5 lint chain 자동 covered (별 mechanism 0)

ADR-061 §결정 1 — Python SSOT (heredoc 금지). Amendment 3 §결정 11 — JSON
parse only (no multi-line regex backtracking; gh --json 출력 = JSON, ReDoS 무관).

Exit code (ADR-060 §결정 15 3-tier):
  0 — gate verdict 도달 (ALLOW / ABORT / STOP 모두 warning-tier exit 0)
  2 — meta-error (gh CLI 미설치 / API call failure fail-1 — setup error)

Usage:
  python3 check_admin_merge_preflight.py --pr <N> [--story CFP-NNN] [--head-sha SHA]
  Options:
    --pr N            PR number (required)
    --story CFP-NNN   carrier story key (per-Story attempt counter scope)
    --head-sha SHA    expected PR head SHA (verify-before-trust Step 1)
    --attempt-file P  per-PR/per-Story attempt counter JSON file
                      (default: env ADMIN_MERGE_ATTEMPT_FILE or skip if absent)
    --no-count        do not increment attempt counter (dry-run verify)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import List, Tuple

# Windows Git Bash / cp949 console — force UTF-8 to avoid UnicodeEncodeError
# on em-dash (U+2014) and Korean output (CFP-418 cross-OS encoding evidence).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

SCRIPT_NAME = "[admin-merge-preflight]"
BYPASS_LABEL = "hotfix-bypass:admin-merge-preflight-gate"
ATTEMPT_CAP = 3  # ADR-113 §결정 2 — attempt cap=3 dual scope (per-PR AND per-Story)

# ADR-113 §결정 1 Step 2 / §결정 5 — 10-value abort_states_enum (closed-set,
# open_extension: false). state value 를 lower-snake 정규화 후 매칭.
# gh pr checks 의 `state` field 는 대문자 (SUCCESS/FAILURE/...) 또는 bucket 영역
# (pass/fail/pending/skipping/cancel) 으로 올 수 있음 → 양쪽 모두 정규화.
ABORT_STATES_ENUM: List[str] = [
    "action_required",  # primary block — manual approval needed
    "failure",          # explicit fail
    "cancelled",        # workflow cancelled, indeterminate
    "timed_out",        # CI timeout, retry candidate
    "stale",            # stale check, fresh commit re-trigger needed
    "pending",          # in-progress, retry-wait
    "in_progress",      # in-progress alias
    "skipped",          # workflow conditional skip
    "neutral",          # neutral state, Orchestrator manual judgment
    "unknown",          # closed-set 외 value → fail-closed semantic
]

# SUCCESS / pass-equivalent normalized values (gate ALLOW 후보).
SUCCESS_STATES = {"success", "completed", "pass", "neutral_success"}

# gh `state` ↔ bucket alias 정규화 map (대문자/소문자/공백 모두 흡수).
STATE_ALIAS = {
    "success": "success",
    "completed": "success",
    "pass": "success",
    "action_required": "action_required",
    "actionrequired": "action_required",
    "failure": "failure",
    "fail": "failure",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "cancel": "cancelled",
    "timed_out": "timed_out",
    "timedout": "timed_out",
    "stale": "stale",
    "pending": "pending",
    "queued": "pending",
    "in_progress": "in_progress",
    "inprogress": "in_progress",
    "started": "in_progress",
    "stalled": "in_progress",
    "skipped": "skipped",
    "skipping": "skipped",
    "neutral": "neutral",
    "expected": "pending",
    "waiting": "pending",
    "requested": "pending",
}


def normalize_state(raw: str) -> str:
    """gh state/bucket value 를 closed-set enum 으로 정규화.

    closed-set 외 value → 'unknown' (fail-closed semantic, ADR-113 §결정 5 fail-2).
    """
    if raw is None:
        return "unknown"
    key = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    if key in STATE_ALIAS:
        return STATE_ALIAS[key]
    if key in SUCCESS_STATES:
        return "success"
    if key in ABORT_STATES_ENUM:
        return key
    # closed-set 외 → fail-closed
    return "unknown"


def gh_cmd(args: List[str]) -> Tuple[int, str, str]:
    """gh CLI 호출 (offline test injection 지원).

    GH_CLI_BIN_OVERRIDE_MODE=python_shim → GH_SHIM_SCRIPT 를 python3 로 실행 (bats fixture).
    default → GH_CLI_BIN env (or 'gh') 직접 실행.

    Returns (returncode, stdout, stderr). gh 미설치/실행불가 시 returncode=127.
    """
    override_mode = os.environ.get("GH_CLI_BIN_OVERRIDE_MODE", "")
    if override_mode == "python_shim":
        shim = os.environ.get("GH_SHIM_SCRIPT", "")
        cmd = [sys.executable, shim] + args
    else:
        gh_bin = os.environ.get("GH_CLI_BIN", "gh")
        cmd = [gh_bin] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "gh CLI not available (FileNotFoundError)"
    except subprocess.TimeoutExpired:
        return 124, "", "gh CLI timeout after 30s"
    return result.returncode, result.stdout or "", result.stderr or ""


def fetch_checks(pr: int) -> Tuple[List[dict], str]:
    """gh pr checks <PR> --json ... 호출. Returns (checks_list, status).

    status: 'ok' | 'meta-error: <msg>' (fail-1 API call failure → exit 2).
    """
    rc, out, err = gh_cmd([
        "pr", "checks", str(pr),
        "--json", "name,state,bucket,link,description",
    ])
    if rc == 127 or rc == 124:
        return [], f"meta-error: {err.strip() or 'gh unavailable'}"
    if rc != 0:
        # gh pr checks returns non-zero when checks are pending/failing — that is
        # NOT a meta-error; output may still carry the JSON. Try parse first.
        try:
            data = json.loads(out) if out.strip() else []
            if isinstance(data, list):
                return data, "ok"
        except json.JSONDecodeError:
            pass
        return [], f"meta-error: gh pr checks rc={rc} {err.strip()[:200]}"
    try:
        data = json.loads(out) if out.strip() else []
    except json.JSONDecodeError as exc:
        return [], f"meta-error: gh pr checks JSON parse 실패: {exc}"
    if not isinstance(data, list):
        return [], "meta-error: gh pr checks output 가 JSON array 아님"
    return data, "ok"


def fetch_pr_head(pr: int) -> Tuple[str, str]:
    """gh pr view <PR> --json headRefOid. Returns (sha, status)."""
    rc, out, err = gh_cmd(["pr", "view", str(pr), "--json", "headRefOid", "--jq", ".headRefOid"])
    if rc == 127 or rc == 124:
        return "", f"meta-error: {err.strip() or 'gh unavailable'}"
    sha = out.strip()
    # gh --json headRefOid --jq → raw sha string; tolerate JSON object form too.
    if sha.startswith("{"):
        try:
            sha = json.loads(sha).get("headRefOid", "").strip()
        except json.JSONDecodeError:
            pass
    return sha, "ok"


def fetch_labels(pr: int) -> List[str]:
    """gh pr view <PR> --json labels. Returns list of label names (best-effort)."""
    rc, out, err = gh_cmd(["pr", "view", str(pr), "--json", "labels", "--jq", "[.labels[].name]"])
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        # `--jq "[.labels[].name]"` → flat name list; but tolerate raw label
        # objects ([{"name": ...}]) for defensiveness.
        names: List[str] = []
        for x in data:
            if isinstance(x, dict):
                names.append(str(x.get("name", "")))
            else:
                names.append(str(x))
        return names
    if isinstance(data, dict) and "labels" in data:
        return [str(l.get("name", "")) for l in data["labels"]]
    return []


def load_attempts(path: str) -> dict:
    if not path or not os.path.isfile(path):
        return {"per_pr": {}, "per_story": {}}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("per_pr", {})
        data.setdefault("per_story", {})
        return data
    except (json.JSONDecodeError, OSError):
        return {"per_pr": {}, "per_story": {}}


def save_attempts(path: str, data: dict) -> None:
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def recovery_procedure(pr: int, story: str) -> str:
    """ADR-113 §결정 1 Step 3 fresh commit trigger recovery procedure."""
    cfp = story or "CFP-NNN"
    return (
        "\n[Step 3 recovery — fresh commit trigger]\n"
        "  ACTION_REQUIRED 잔존 시 fresh commit 으로 workflow re-trigger:\n"
        f'    git -C "<worktree_abs_path>" commit --allow-empty -m "[{cfp}] '
        're-trigger required checks (admin-merge preflight Step 3)"\n'
        '    git -C "<worktree_abs_path>" push origin <branch>\n'
        "  Step 4 (≤60s re-verify) → ALLOW; 잔존 시 Step 5 attempt cap.\n"
        "  phase-gate-mergeable.yml workflow_dispatch 부재 (Wave 4 carrier) — fresh commit = primary recovery.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ADR-113 admin-merge pre-flight gate (CFP-1564 Wave 2 mechanical wire)."
    )
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--story", default="", help="carrier story key (CFP-NNN)")
    parser.add_argument("--head-sha", default="", help="expected PR head SHA (verify-before-trust)")
    parser.add_argument(
        "--attempt-file",
        default=os.environ.get("ADMIN_MERGE_ATTEMPT_FILE", ""),
        help="attempt counter JSON file (per-PR + per-Story scope)",
    )
    parser.add_argument("--no-count", action="store_true", help="do not increment attempt counter")
    args = parser.parse_args()

    pr = args.pr
    story = args.story
    pr_key = str(pr)

    # ── Step 5 pre-check — attempt cap dual scope (per-PR AND per-Story) ───────
    attempts = load_attempts(args.attempt_file)
    per_pr = int(attempts["per_pr"].get(pr_key, 0))
    per_story = int(attempts["per_story"].get(story, 0)) if story else 0

    if per_pr >= ATTEMPT_CAP or (story and per_story >= ATTEMPT_CAP):
        scope = "per-PR" if per_pr >= ATTEMPT_CAP else "per-Story"
        count = per_pr if per_pr >= ATTEMPT_CAP else per_story
        print(f"{SCRIPT_NAME} STOP — attempt cap reach ({scope} {count}/{ATTEMPT_CAP})")
        print(
            "  ADR-113 §결정 2/§결정 5 fail-3 — workflow self-error 추정. "
            "사용자 escalation 의무 (auto-retry 무한 loop 차단, Threat A counter reset abuse mitigation)."
        )
        print("  Workflow log direct verify:")
        print('    gh run list --workflow="phase-gate-mergeable.yml" --branch=<branch> --limit 10')
        return 0  # warning-tier exit 0

    # ── Step 1 — required check state enum fetch ──────────────────────────────
    checks, status = fetch_checks(pr)
    if status.startswith("meta-error"):
        # fail-1 API call failure (gh unavailable / network / token / 429)
        print(f"{SCRIPT_NAME} meta-error (fail-1 API call failure): {status}")
        print(
            "  ADR-113 §결정 5 fail-1 — retry exp-backoff 3회 + codeforge:rate-limit-429-mitigation "
            "skill cross-ref + ADR-066 PAT 만료 check (90d rotation invariant)."
        )
        return 2

    # ── head SHA verify (Step 1 verify-before-trust primitive, ADR-073 §결정 1) ──
    if args.head_sha:
        pr_head, head_status = fetch_pr_head(pr)
        if head_status.startswith("meta-error"):
            print(f"{SCRIPT_NAME} meta-error (fail-1) — PR head fetch 실패: {head_status}")
            return 2
        if pr_head and pr_head != args.head_sha:
            print(
                f"{SCRIPT_NAME} ABORT — head SHA mismatch "
                f"(provided={args.head_sha[:12]} != PR head={pr_head[:12]})"
            )
            print(
                "  green checks 가 stale commit 대상일 수 있음 (verify-before-trust ADR-073 §결정 1). "
                "fresh fetch 후 재verify 의무 — admin merge 차단."
            )
            return 0  # warning-tier

    # ── Step 2 — ACTION_REQUIRED detection + 10-value abort_states_enum ────────
    aborts: List[Tuple[str, str, str]] = []  # (name, raw_state, normalized)
    unknowns: List[Tuple[str, str]] = []     # (name, raw_state)
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        name = str(chk.get("name", "(unnamed)"))
        raw_state = chk.get("state", "") or chk.get("bucket", "")
        norm = normalize_state(raw_state)
        if norm == "success":
            continue
        if norm == "unknown":
            unknowns.append((name, str(raw_state)))
            aborts.append((name, str(raw_state), "unknown"))
        elif norm in ABORT_STATES_ENUM:
            aborts.append((name, str(raw_state), norm))

    # ── bypass channel (ADR-113 §결정 4) ──────────────────────────────────────
    labels = fetch_labels(pr)
    bypass_active = BYPASS_LABEL in labels

    if not aborts:
        # Step 1 empty (모든 required check success) → ALLOW
        print(f"{SCRIPT_NAME} ALLOW — PASS (모든 required check success, admin merge 진행 가능)")
        print(f"  checks verified: {len(checks)} (all state=success/pass)")
        return 0

    # aborts non-empty → gate would ABORT. bypass label 가 있으면 ALLOW + audit.
    if bypass_active:
        print(f"{SCRIPT_NAME} ALLOW — bypass label 부착 ({BYPASS_LABEL})")
        ts_note = ", ".join(f"{n}:{s}" for n, s, _ in aborts)
        print(
            f"  [admin-merge-preflight-audit] PR={pr} story={story or '(none)'} "
            f"bypassed_states=[{ts_note}]"
        )
        print(
            "  ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered "
            "(bypass-label-counter / per-plugin-cumulative-counter / bypass-justification-marker / "
            "cross-repo-bypass-counter / check-bypass-audit-comment.sh). "
            "`[bypass-justification]` PR comment marker 의무."
        )
        return 0

    # ── ABORT verdict ─────────────────────────────────────────────────────────
    has_unknown = bool(unknowns)
    print(f"{SCRIPT_NAME} ABORT — ACTION_REQUIRED / non-success check detected (admin merge 차단)")
    for name, raw, norm in aborts:
        tag = " [fail-closed]" if norm == "unknown" else ""
        print(f"  - {name}: state={raw} → {norm}{tag}")
    if has_unknown:
        print(
            f"\n  fail-2 (ADR-113 §결정 5) — state enum 'unknown' (closed-set 10-value 외): "
            "fail-closed semantic. admin merge 차단 + 사용자 escalation. "
            "enum extension 시 ADR Amendment 의무 (open_extension: false)."
        )

    # increment attempt counter (per-PR + per-Story) unless --no-count
    if not args.no_count:
        attempts["per_pr"][pr_key] = per_pr + 1
        if story:
            attempts["per_story"][story] = per_story + 1
        save_attempts(args.attempt_file, attempts)
        new_pr = attempts["per_pr"][pr_key]
        new_story = attempts["per_story"].get(story, 0) if story else 0
        print(
            f"\n  attempt count: per-PR {new_pr}/{ATTEMPT_CAP}"
            + (f", per-Story {new_story}/{ATTEMPT_CAP}" if story else "")
        )

    # Step 3 recovery procedure surface
    print(recovery_procedure(pr, story))
    return 0  # warning-tier exit 0


if __name__ == "__main__":
    sys.exit(main())
