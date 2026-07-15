#!/usr/bin/env bash
# tests/scripts/test_aggregate-dev-process-event.sh
# CFP-2688 Phase 2 (구현 lane) — QADev execution-backed self-test wrapper for
#   scripts/lib/aggregate_dev_process_event.py (B lane — dev-process 지표 aggregate, record-only measurement)
#   + scripts/lib/check_dev_process_aggregate_honesty.py (honest-degrade/산식-parity lint).
#
# 계약 SSOT: docs/change-plans/2026-07-15-cfp-2688-dev-process-metrics.md §8.1/§8.6/§11.6
#   + docs/inter-plugin-contracts/dev-process-event-v1.md §9 (A substrate, FROZEN, read-only 소비).
#
# 검증 원칙 (execution-backed, hollow 금지 — CFP-2635/CFP-2545):
#   - real invocation: aggregator `--self-test` + lint `--selftest`(negative-control) + lint `check`
#       (실 query_with_stats round-trip, mock-seam 금지) 를 exit-code gated 로 구동.
#   - ★distinct-marker 의무 (exit-code-only 금지 — QADev subprocess-fork 진정성): 각 fork 통과 판정을
#       exit code + **도메인 고유 stdout sentinel** 을 병행 assert. 미 fork 시 python 은 exit 2 + 빈
#       stdout → sentinel assert 자연 실패 (silent false-positive 차단). 도메인 exit(0)과 표준 exit 우연
#       일치 방어.
#   - real e2e: synthetic dev-process ledger emit → CLI `--ledger … --kpi-dir …` 실행 → KPI dual-file
#       산출 + measured-0≠dormant(empty→pending) + record-only INV(원장 byte-identical) + idempotency
#       (same-input 2-run → history +0) 관측.
#
# ★exit-masking / mock-seam BAN (ADR-060 Amd22 / CFP-2635) — 본 wrapper 준수:
#   - 모든 `|| EC=$?` 는 counter-backed(직후 assert_eq 로 EC 판정) — bare `cmd || true` 무.
#   - mock-seam env(_*MOCK*=) 미사용 — 실 port round-trip(§8.1) 만.
#
# ★Windows/Git-Bash (MEMORY CFP-2659): mktemp -d 사용(하드코딩 /tmp 금지). 로컬 Git-Bash 에서 /tmp→C:\tmp
#   path artifact 로 false-FAIL 가능 → CI ubuntu authoritative. python helper 경로는 argv 로 전달(MSYS
#   mangle 안전 — python -c 코드 문자열에 경로 임베드 금지).
# Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

# python3 우선(CI ubuntu authoritative), 부재 시 python fallback(로컬 Windows 견고성).
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGG="$REPO_ROOT/scripts/lib/aggregate_dev_process_event.py"
LINT="$REPO_ROOT/scripts/lib/check_dev_process_aggregate_honesty.py"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

assert_eq()  { if [ "$2" = "$3" ]; then pass "$1 [$2]"; else fail "$1" "expected [$3] got [$2] — ${4:-}"; fi; }
assert_ge()  { if [ "$2" -ge "$3" ] 2>/dev/null; then pass "$1 [$2>=$3]"; else fail "$1" "expected >=$3 got [$2]"; fi; }
assert_has() { case "$2" in *"$3"*) pass "$1";; *) fail "$1" "missing substring [$3] in output";; esac; }

# ── JSON 필드 추출 (경로 = argv → MSYS mangle 안전) ──────────────────────────────────
jget() {  # jget <json_file> <dotted.path>
  "$PY" - "$1" "$2" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
for k in sys.argv[2].split("."):
    d = d[k]
print(d)
PY
}
sha256_of() {  # sha256_of <file>
  "$PY" - "$1" <<'PY'
import hashlib, sys
print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())
PY
}
count_lines() {  # count_lines <file> — 비-빈 줄 수
  "$PY" - "$1" <<'PY'
import sys
n = sum(1 for ln in open(sys.argv[1], encoding="utf-8") if ln.strip())
print(n)
PY
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2688 B lane — dev-process aggregate + honest-degrade lint (execution-backed)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ══ 케이스 1: aggregator --self-test (embedded AC-4~23 fixtures) — exit 0 + distinct-marker ══
OUT1="$WORK/agg_selftest.out"; EC=0
"$PY" "$AGG" --self-test > "$OUT1" 2>&1 || EC=$?
assert_eq "aggregator --self-test: exit 0" "$EC" "0" "embedded self-test PASS 이어야"
# distinct-marker: 도메인 고유 PASS sentinel (미 fork 시 exit 2 + 빈 stdout → 아래 전부 RED)
assert_has "aggregator --self-test: distinct-marker (AC-7 anchor-priority)" "$(cat "$OUT1")" "AC-7 anchor-priority"
assert_has "aggregator --self-test: distinct-marker (measured-0≠dormant)" "$(cat "$OUT1")" "measured-0≠dormant"
assert_has "aggregator --self-test: distinct-marker (idem-2axis)" "$(cat "$OUT1")" "idem-2axis"

# ══ 케이스 2: lint --selftest (discriminating negative-control) — exit 0 + distinct-marker ══
OUT2="$WORK/lint_selftest.out"; EC=0
"$PY" "$LINT" --selftest > "$OUT2" 2>&1 || EC=$?
assert_eq "lint --selftest: exit 0 (positive GREEN + NC1~NC10 RED)" "$EC" "0" "판별성 실증 이어야"
assert_has "lint --selftest: distinct-marker (discriminating)" "$(cat "$OUT2")" "discriminating"
assert_has "lint --selftest: NC10 order-preserving RED 관측" "$(cat "$OUT2")" "NC10"
assert_has "lint --selftest: positive GREEN + NC RED 종합" "$(cat "$OUT2")" "NC1~NC10 전부 RED"

# ══ 케이스 3: lint check (real query_with_stats round-trip) — exit 0 + distinct-marker ══
OUT3="$WORK/lint_check.out"; EC=0
"$PY" "$LINT" > "$OUT3" 2>&1 || EC=$?
assert_eq "lint check: exit 0 (실 산출 honest-degrade GREEN)" "$EC" "0" "실 port round-trip GREEN 이어야"
assert_has "lint check: distinct-marker (real port round-trip)" "$(cat "$OUT3")" "real query_with_stats round-trip"
assert_has "lint check: execution-backed(not presence-grep) 서술" "$(cat "$OUT3")" "presence-grep false-oracle 아님"

# ══ 케이스 4: real e2e — synthetic ledger → CLI aggregate → KPI dual-file 산출 ══
# fixture emit (composition-driven, 경로 argv[1]) — cycletime handoff + defect 재발
"$PY" - "$WORK" <<'PY'
import json, os, sys
work = sys.argv[1]
def row(et, sk, lane, eid, ts, defect_id=None, family=None, dtype=None, dl=None, ttd=None):
    return {"event_id": eid, "schema_version": "dev-process-event-v1", "event_type": et,
            "emit_source": "agent", "timestamp_utc": ts, "story_key": sk, "lane_label": lane,
            "consumer_scope": "wrapper", "defect_id": defect_id, "fix_id": None, "blob_ref": None,
            "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],
            "defect_family": family, "defect_type": dtype, "time_to_detection": ttd,
            "detecting_lane": dl}
rows = [
    row("lane_transition", "S1", "설계", "e1", "2026-07-15T10:00:00Z"),
    row("lane_transition", "S1", "설계-리뷰", "e2", "2026-07-15T10:00:10Z"),
    row("final_artifact", "S1", "설계-리뷰", "e3", "2026-07-15T10:00:40Z"),
    row("defect_finding", "S1", "구현", "e4", "2026-07-15T10:01:00Z",
        defect_id="D1", family="doc-integrity", dtype="section", dl="설계-리뷰", ttd="1"),
]
with open(os.path.join(work, "valid.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
open(os.path.join(work, "empty.jsonl"), "w", encoding="utf-8", newline="\n").write("")
print("fixtures-ready")
PY
assert_has "e2e: fixture emit" "$(cat "$WORK/valid.jsonl" | head -c 20)" "event_id"

LA="$WORK/valid.jsonl"
KDIR="$WORK/kpi1"
NOSPAWN="$WORK/no-spawn.jsonl"   # 부재 → replay reader [] (hermetic, 실 spawn ledger 미read)
OUT4="$WORK/agg_render.out"; EC=0
"$PY" "$AGG" --ledger "$LA" --kpi-dir "$KDIR" --spawn-ledger "$NOSPAWN" > "$OUT4" 2>&1 || EC=$?
assert_eq "e2e: aggregate exit 0 (record-only non-blocking)" "$EC" "0" "always exit 0"
# distinct-marker: render header 도메인 sentinel
assert_has "e2e: distinct-marker (render header)" "$(cat "$OUT4")" "dev-process-event 지표 aggregate"
# KPI dual-file 산출 (6 metric snapshot present)
CT_SNAP="$KDIR/dev-process-cycletime-snapshot.json"
CT_HIST="$KDIR/dev-process-cycletime-history.jsonl"
assert_eq "e2e: cycletime snapshot status=measured" "$(jget "$CT_SNAP" status)" "measured"
assert_eq "e2e: cycletime label='lane residency' (NOT time-to-PASS)" "$(jget "$CT_SNAP" overall.label)" "lane residency"
assert_eq "e2e: cycletime closed_interval_count 2 (S1 설계=10s + 설계-리뷰=30s)" "$(jget "$CT_SNAP" overall.closed_interval_count)" "2"
assert_eq "e2e: trend pattern_status uncomputable_missing_key (AC-19 DEFAULT)" "$(jget "$KDIR/dev-process-trend-snapshot.json" pattern_status)" "uncomputable_missing_key"
assert_eq "e2e: trend pattern_count null (AC-19)" "$(jget "$KDIR/dev-process-trend-snapshot.json" pattern_count)" "None"
assert_eq "e2e: token-cost honest-null status" "$(jget "$KDIR/dev-process-token-cost-snapshot.json" overall.token_cost_status)" "honest_null"

# ══ 케이스 5: record-only INV — aggregate 전후 원장 sha256 byte-identical ══
SHA_BEFORE="$(sha256_of "$LA")"
"$PY" "$AGG" --ledger "$LA" --kpi-dir "$KDIR" --spawn-ledger "$NOSPAWN" >/dev/null 2>&1   # 재실행
SHA_AFTER="$(sha256_of "$LA")"
assert_eq "record-only INV: 원장 sha256 byte-identical (IN-PLACE EDIT 금지)" "$SHA_BEFORE" "$SHA_AFTER" \
  "aggregate 는 port read-only — 변경 시 record-only INV(§11.6) 위반"

# ══ 케이스 6: idempotency — same-input 2-run → history +0 (dedup, §11.6/AC-6) ══
# (위 케이스 4·5 에서 KDIR 에 이미 2회 run 됨 → history 는 첫 run 에서 +1, 이후 +0)
H_AFTER_2RUN="$(count_lines "$CT_HIST")"
"$PY" "$AGG" --ledger "$LA" --kpi-dir "$KDIR" --spawn-ledger "$NOSPAWN" >/dev/null 2>&1   # 3rd run (same input)
H_AFTER_3RUN="$(count_lines "$CT_HIST")"
assert_ge "idempotency: history >=1 (첫 run append)" "$H_AFTER_2RUN" "1"
assert_eq "idempotency: same-input 재실행 → history +0 (dedup, generated_at_kst strip)" "$H_AFTER_3RUN" "$H_AFTER_2RUN" \
  "content-hash(EXCLUDING generated_at_kst) dedup — unchanged ledger 재실행 시 append 0"

# ══ 케이스 7: measured-0 ≠ dormant — empty ledger → status pending + measured_at null (AC-5) ══
KDIR2="$WORK/kpi2"; EC=0
"$PY" "$AGG" --ledger "$WORK/empty.jsonl" --kpi-dir "$KDIR2" --spawn-ledger "$NOSPAWN" >/dev/null 2>&1 || EC=$?
assert_eq "measured-0≠dormant: empty aggregate exit 0" "$EC" "0"
assert_eq "measured-0≠dormant: empty → status pending" "$(jget "$KDIR2/dev-process-cycletime-snapshot.json" status)" "pending"
assert_eq "measured-0≠dormant: empty → measured_at null (dormant 위장 금지)" "$(jget "$KDIR2/dev-process-cycletime-snapshot.json" measured_at)" "None"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — aggregate-dev-process-event (CFP-2688 B lane)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — aggregator self-test + lint discriminating negative-control + real e2e"
  echo "  (KPI dual-file + record-only INV + idempotency +0 + measured-0≠dormant), distinct-marker gated."
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
