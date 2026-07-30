#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# reconcile_spawn_completion_count.py — hook spawn-completion COUNTER ↔ recorded row COUNT
#
# Carrier: CFP-2850 Phase 2 (구현) — Epic plugin-codeforge#2814 W1-B / §3.6 F-B / §11.6
# SSOT: docs/inter-plugin-contracts/spawn-event-v1.md §3 append_rules.writer (Amendment 4)
#       + Change Plan CFP-2850 §3.6 (F-B) / §11.6 (COUNT reconcile)
#
# 책임 (F-B — 설계리뷰 P2 흡수):
#   - SubagentStop hook 의 경량 spawn-completion COUNTER(.claude/ledger/spawn-completion.count,
#     bare append-only 라인 tally — hooks/subagent-stop 가 씀, disjoint 채널) 의 라인 수
#     ↔ task-notification-recorded spawn-event row COUNT(spawn-event.jsonl 의 spawn-event-v1
#     row, event_id read-time dedup 후) 를 COUNT-레벨로 대조한다.
#   - `hook_completion_count > recorded_row_count` gap = single-writer survivorship residual
#     (Orchestrator-side emit 실패/notification-loss) 의 crash-safe 정직 측정치.
#
# 불변식 (binding):
#   - tier = [measurement] STRICT record-only — gate/block/deny 아님(INV-5). exit 0 무조건.
#   - INV-3 disjoint 채널 — counter 는 spawn-event.jsonl 와 물리 분리(별 sidecar). 본 script 는
#     read-only 대조만(어느 파일도 write/mutate 안 함).
#   - 0 API call (ADR-163 §결정8) — local read only.
#   - honest-degrade (ADR-119): counter(hooks/subagent-stop)와 recorded row(Orchestrator)는
#     **동일 opt-in 술어**(telemetry.enabled AND channels.spawn_event)에 종속한다 —
#     CFP-2850 구현리뷰 FIX Iter 2 / F-CR-001 로 counter 가 opt-in gate 안으로 이동
#     (구 "counter 는 telemetry 설정과 무관하게 증가한다" 전제는 폐기 — 그 전제가
#      ADR-043 §결정 1 opt-in default false 위반이었음).
#     따라서 **opt-in OFF 구간은 counter 도 0** — 그 구간은 gap 이 아니라 **측정 공백**이며
#     본 reconcile 에 애초에 나타나지 않는다(no_data). 이는 gap 의 opt-in-off 오염을 제거하나,
#     동시에 **opt-in OFF 세션의 완료는 아무 것도 관측하지 못한다**는 천장을 낳는다
#     (counter 는 "모든 platform 완료 계수" 가 아니다 — over-claim 금지).
#     opt-in ON 구간에서도 gap 은 여전히 **upper-bound residual** 로만 정직 표기(단정 금지):
#     hook 발화 후 opt-in flip / gate probe fail-closed / counter 파일 소실 등이 섞일 수 있어
#     "gap = survivorship loss" 라 확정하지 않는다.
#
# 사용:
#   python3 reconcile_spawn_completion_count.py check [--count-path P] [--ledger-path P]
#                                                     [--repo-root P] [--json]
#   python3 reconcile_spawn_completion_count.py --self-test
#
# Prior art: dedup_section14_spawn_event.py (동일 채널 인접 sibling — ledger reader REUSE,
#            ADR-140 no-duplication) / aggregate_stop_event.py (record-only exit-0 + --self-test).

import argparse
import json
import os
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability — scripts/lib 관례 재사용)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── sibling REUSE (ADR-140 reuse-before-write — 동일 채널 ledger reader 재사용) ──
# ★S-4 (보안테스트 iter1) — ledger reader 는 **정본 1함수**(replay_spawn_event._read_ledger)만
#   쓴다. 구 구현은 자체 JSONL reader 사본(_read_rows fallback)을 들고 있어 행분할·decode 정책이
#   소비자마다 갈릴 여지를 남겼다 → 사본 제거 + 정본 위임 (reader 계보 물리 통합).
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
try:
    from replay_spawn_event import _read_ledger as _read_ledger_rows
except Exception:  # pragma: no cover — import 실패 시 read 불가(정직 degrade, 사본 금지)
    _read_ledger_rows = None
try:
    from dedup_section14_spawn_event import _dedup_rows
except Exception:  # pragma: no cover — dedup 은 자립 fallback 유지(본 건 대상 아님)
    _dedup_rows = None

_SPAWN_SCHEMA_VERSION = "spawn-event-v1"
_COUNT_BASENAME = "spawn-completion.count"
_LEDGER_BASENAME = "spawn-event.jsonl"
_DEFAULT_LEDGER_PARENT_REL = os.path.join(".claude", "ledger")

_HONESTY = (
    "[measurement] STRICT record-only — gap = upper-bound residual(단정 금지), gate 아님. "
    "hook counter 와 recorded row 는 **동일 opt-in 술어**(telemetry.enabled AND "
    "channels.spawn_event)에 종속한다 → **opt-in OFF 구간은 counter 자체가 증가하지 않으므로** "
    "그 구간의 hook_count vs recorded_count 비교는 성립하지 않는다(둘 다 0 = no_data — gap 이 "
    "아니라 측정 공백). 그 구간의 완료는 아무 것도 관측되지 않는다 — counter 는 '모든 platform "
    "완료 계수' 가 아니다(over-claim 금지). opt-in ON 구간의 gap>0 = single-writer emit 실패/"
    "notification-loss 의 upper-bound 관측(crash-safe), 인과 확정 아님 — 구간 중 opt-in flip / "
    "gate probe fail-closed / counter 파일 소실도 같은 gap 으로 보인다(honest-degrade). "
    "예외 — writer 가 CLI opt-in flag(--telemetry-enabled/--spawn-event-enabled)로 config "
    "를 우회해 write 하면 hook counter(config 술어)와 recorded row(flag 술어)가 **불일치**할 "
    "수 있다: 이때 recorded > hook 이 되어 recorded_excess 로 표기된다(gap 의 역방향). "
    "counter line append 원자성 = 로컬 FS best-effort(network-share 무보장)."
)


# ─────────────────────── count 산출 (read-only) ──────────────────────────────

def _resolve_count_path(count_path_arg, repo_root):
    if count_path_arg:
        return count_path_arg
    base = repo_root or os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return os.path.join(base, _DEFAULT_LEDGER_PARENT_REL, _COUNT_BASENAME)


def _resolve_ledger_path(ledger_path_arg, repo_root):
    if ledger_path_arg:
        return ledger_path_arg
    base = repo_root or os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return os.path.join(base, _DEFAULT_LEDGER_PARENT_REL, _LEDGER_BASENAME)


def count_hook_completions(count_path):
    """spawn-completion.count 의 non-empty 라인 수 = hook 완료 계수. 부재 → 0 (graceful)."""
    if not os.path.isfile(count_path):
        return 0
    n = 0
    try:
        with open(count_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    n += 1
    except OSError:
        return n
    return n


def count_recorded_rows(ledger_path):
    """spawn-event.jsonl 의 spawn-event-v1 row 수(event_id dedup 후 — self-context-v1 제외).

    ledger reader = dedup_section14 sibling REUSE. import 실패 시 자립 fallback.
    """
    rows = _read_rows(ledger_path)
    # spawn-event-v1 row 만(self-context-v1 등 disjoint record type 제외)
    spawn_rows = [r for r in rows if r.get("schema_version") == _SPAWN_SCHEMA_VERSION]
    deduped = _dedup(spawn_rows)
    return len(deduped)


def _read_rows(ledger_path):
    """ledger read — 정본(`replay_spawn_event._read_ledger`) 위임 (S-4 reader 통일).

    정본 import 실패 = 사본으로 때우지 않고 **빈 결과 + WARN**(정직 degrade). 사본을 두면
    행분할(\\n vs splitlines)·decode 정책이 다시 갈라져 같은 원장을 읽는 reader 끼리 row 수가
    발산한다 — 그 발산이 본 건(S-4)의 결함 본체였다.
    """
    if _read_ledger_rows is None:
        print(
            "[codeforge-spawn-event] WARN: ledger reader 정본(replay_spawn_event) import 실패 "
            "— recorded_row_count=0 으로 정직 degrade (사본 reader 금지, S-4)",
            file=sys.stderr,
        )
        return []
    return _read_ledger_rows(ledger_path)


def _dedup(rows):
    if _dedup_rows is not None:
        return _dedup_rows(rows)
    seen = set()
    out = []
    for r in rows:
        eid = r.get("event_id")
        if eid is not None:
            if eid in seen:
                continue
            seen.add(eid)
        out.append(r)
    return out


# ─────────────────────── reconcile (record-only) ─────────────────────────────

def reconcile(count_path, ledger_path):
    """COUNT-레벨 대조 (record-only). Returns dict.

    status:
      - no_data      = counter 0 ∧ recorded 0 (관측 대상 없음 — 정상).
      - aligned      = counter == recorded (gap 0).
      - gap_observed = counter > recorded (survivorship residual upper-bound 관측).
      - recorded_excess = recorded > counter (opt-in ON + hook 미발화/counter 소실 등 — 정직 표기).
    """
    hook_count = count_hook_completions(count_path)
    recorded = count_recorded_rows(ledger_path)
    gap = hook_count - recorded

    if hook_count == 0 and recorded == 0:
        status = "no_data"
    elif gap == 0:
        status = "aligned"
    elif gap > 0:
        status = "gap_observed"
    else:
        status = "recorded_excess"

    return {
        "status": status,
        "hook_completion_count": hook_count,
        "recorded_row_count": recorded,
        "gap": gap,                       # hook - recorded (>0 = survivorship residual upper-bound)
        "count_path": count_path,
        "ledger_path": ledger_path,
        "honesty_note": _HONESTY,
    }


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    count_path = _resolve_count_path(args.count_path, repo_root)
    ledger_path = _resolve_ledger_path(args.ledger_path, repo_root)

    result = reconcile(count_path, ledger_path)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "reconcile-spawn-completion-count: %s — hook_completion_count=%d / "
            "recorded_row_count=%d / gap=%d"
            % (result["status"], result["hook_completion_count"],
               result["recorded_row_count"], result["gap"])
        )
        if result["status"] == "gap_observed":
            print(
                "  ::notice:: gap=%d = single-writer survivorship residual upper-bound "
                "(Orchestrator emit 실패/notification-loss 관측 — record-only, gate 아님)."
                % result["gap"]
            )
        print("  HONESTY: %s" % _HONESTY)

    # record-only — 항상 exit 0 (gate 아님, INV-5). gap 은 관측치이지 실패 판정 아님.
    sys.exit(0)


# ─────────────────────── self-test (execution-backed, independent-oracle) ─────

def _self_test():
    import tempfile

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    def _spawn_row(eid):
        return json.dumps({"schema_version": _SPAWN_SCHEMA_VERSION, "event_id": eid,
                           "lane_label": "구현"}, ensure_ascii=False)

    with tempfile.TemporaryDirectory() as d:
        count_path = os.path.join(d, _COUNT_BASENAME)
        ledger_path = os.path.join(d, _LEDGER_BASENAME)

        # ── no_data: 둘 다 부재 ──
        r = reconcile(count_path, ledger_path)
        check(r["status"] == "no_data" and r["gap"] == 0, "[no_data] %s" % r)

        # ── counter 3 completions ──
        with open(count_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("2026-07-27T10:00:00Z\n2026-07-27T10:01:00Z\n2026-07-27T10:02:00Z\n")
        # recorded 1 spawn-event-v1 row + 1 self-context-v1(제외) + 1 dup event_id(dedup)
        with open(ledger_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(_spawn_row("e1") + "\n")
            f.write(_spawn_row("e1") + "\n")  # dup event_id → dedup
            f.write(json.dumps({"schema_version": "self-context-v1", "session_id": "x"}) + "\n")

        r2 = reconcile(count_path, ledger_path)
        # composition-derived expected: hook=3, recorded=1(dedup+self-context 제외), gap=2
        check(r2["hook_completion_count"] == 3, "[count] hook %s != 3" % r2["hook_completion_count"])
        check(r2["recorded_row_count"] == 1,
              "[count] recorded %s != 1 (dedup+self-context 제외)" % r2["recorded_row_count"])
        check(r2["gap"] == 2 and r2["status"] == "gap_observed", "[gap] %s" % r2)

        # ── metamorphic: recorded +1 distinct → gap -1 ──
        with open(ledger_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(_spawn_row("e2") + "\n")
        r3 = reconcile(count_path, ledger_path)
        check(r3["recorded_row_count"] == 2 and r3["gap"] == 1,
              "[metamorphic] recorded delta → gap 감소 아님: %s" % r3)

        # ── aligned: counter == recorded ──
        with open(count_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("a\nb\n")
        r4 = reconcile(count_path, ledger_path)
        check(r4["status"] == "aligned" and r4["gap"] == 0, "[aligned] %s" % r4)

        # ── recorded_excess: recorded > counter ──
        with open(count_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("only-one\n")
        r5 = reconcile(count_path, ledger_path)
        check(r5["status"] == "recorded_excess" and r5["gap"] == -1, "[recorded_excess] %s" % r5)

        # ── read-only INV: reconcile 전후 파일 byte-identical (mutate 금지) ──
        before = open(ledger_path, "rb").read()
        reconcile(count_path, ledger_path)
        after = open(ledger_path, "rb").read()
        check(before == after, "[read-only] ledger mutated (record-only INV 위반)")

    if failures:
        print("reconcile_spawn_completion_count SELF-TEST: FAIL (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        sys.exit(1)
    print("reconcile_spawn_completion_count SELF-TEST: PASS (no_data/gap/aligned/excess/"
          "metamorphic/read-only)")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="hook spawn-completion COUNTER ↔ recorded row COUNT reconcile "
                    "(CFP-2850 F-B — record-only)"
    )
    parser.add_argument("--self-test", action="store_true", help="내장 self-test 실행")
    subparsers = parser.add_subparsers(dest="command")

    check_p = subparsers.add_parser("check", help="COUNT-레벨 reconcile (record-only, exit 0)")
    check_p.add_argument("--count-path", default="",
                         help="spawn-completion.count 경로 (default: <root>/.claude/ledger/...)")
    check_p.add_argument("--ledger-path", default="",
                         help="spawn-event.jsonl 경로 (default: <root>/.claude/ledger/...)")
    check_p.add_argument("--repo-root", default=".", help="repo root (default 현재 디렉터리)")
    check_p.add_argument("--json", action="store_true", help="JSON 출력")

    args = parser.parse_args()
    if args.self_test:
        _self_test()
    if args.command == "check":
        cmd_check(args)
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
