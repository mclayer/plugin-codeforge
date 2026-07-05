#!/usr/bin/env bash
# tests/scripts/test_aggregate-stop-event.sh
# CFP-2573 Phase 2 (구현 lane) — QADev execution-backed test for
#   scripts/lib/aggregate_stop_event.py (L5 stop-event 원장 aggregate — record-only measurement).
#
# 계약 SSOT: docs/inter-plugin-contracts/stop-event-v1.md §5.1 (v1.2) / ADR-144 §결정 5 (L5, GAP-7 aggregate 부재).
#
# 검증 원칙 (execution-backed, hollow 금지):
#   - real invocation: 실제 synthetic ledger 파일 emit → `python3 aggregate_stop_event.py --json` 실행
#       → observed JSON 필드 대조 (presence-grep oracle 아님, 실 산출값 assert).
#   - distinct-marker 의무 (exit-code-only 금지): aggregate 는 record-only 라 **항상 exit 0** → 통과 판정을
#       도메인 고유 stdout JSON 필드(reason_class_counts / ratio / honesty_notes …)로만 한다. 미 fork 시
#       python 은 exit 2 + 빈 stdout → JSON parse 실패 → RED (silent false-positive 차단).
#   - 하드코딩 방어: per-class count 는 2-fixture cross-run(B = A + vague 1개)로 delta==+1 falsify.
#   - record-only INV: aggregate 실행 전후 원장 sha256 byte-identical (IN-PLACE EDIT 금지 falsify).
#
# self-contained pure-bash (tests/scripts 관례 — test_check-subagent-wait-liveness-presence.sh 모델 답습).
# ★ Windows 네이티브 python: MSYS 는 **인자로 넘긴** 경로만 Windows 형으로 mangle → 모든 python helper 는
#   경로를 sys.argv 로 받는다 (python -c 코드 문자열에 /tmp 경로 임베드 금지).
# Exit 0 = 전 케이스 PASS.

set -uo pipefail

# Windows 로컬 견고성: python helper stdout 를 utf-8 로 고정 (em-dash 등 — CI=Linux 는 utf-8 기본).
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGG="$REPO_ROOT/scripts/lib/aggregate_stop_event.py"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

assert_eq()  { if [ "$2" = "$3" ]; then pass "$1 [$2]"; else fail "$1" "expected [$3] got [$2] — ${4:-}"; fi; }
assert_ge()  { if [ "$2" -ge "$3" ] 2>/dev/null; then pass "$1 [$2>=$3]"; else fail "$1" "expected >=$3 got [$2]"; fi; }
assert_has() { case "$2" in *"$3"*) pass "$1";; *) fail "$1" "missing substring [$3] in output";; esac; }
assert_nothas() { case "$2" in *"$3"*) fail "$1" "raw payload echo detected [$3]";; *) pass "$1";; esac; }

# ── JSON 필드 추출 (경로 = argv → MSYS mangle 안전) ──────────────────────────────────
jget() {  # jget <json_file> <dotted.path>
  python3 - "$1" "$2" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
for k in sys.argv[2].split("."):
    d = d[k]
print(d)
PY
}
sha256_of() {  # sha256_of <file>
  python3 - "$1" <<'PY'
import hashlib, sys
print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())
PY
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

MALFORMED_SENTINEL="MALFORMED_RAW_ECHO_SENTINEL_zzq"

# ── fixture emit (composition-driven — 경로는 argv[1]) ────────────────────────────────
python3 - "$WORK" "$MALFORMED_SENTINEL" <<'PY'
import json, os, sys
work, sentinel = sys.argv[1], sys.argv[2]
def row(sr, i):
    return {"timestamp_kst": "2026-07-05T10:00:00+09:00", "hook_source": "stop",
            "hook_decision": "record-only", "session_id": f"sess-{i}", "stop_reason": sr}
# mixed: vague_pause×3 / legit×2 / escalation×1 + legacy(무매핑)×2 = 8 valid
comp = [("stop_vague_pause", 3), ("stop_user_complete", 2), ("stop_escalation", 1),
        ("stop_legacy_a", 1), ("stop_legacy_b", 1)]
rows, i = [], 0
for sr, rep in comp:
    for _ in range(rep):
        rows.append(row(sr, i)); i += 1
lines = [json.dumps(r, ensure_ascii=False) for r in rows]
malformed = "}{ this is not json :: " + sentinel        # malformed × 1 (raw sentinel echo 금지 검증용)
lines_a = lines + [malformed, ""]                        # + 빈 줄(무시)
open(os.path.join(work, "ledger_a.jsonl"), "w", encoding="utf-8").write("\n".join(lines_a) + "\n")
# B = A + vague 1개 (cross-run delta 검증 — 하드코딩 방어)
rows_b = rows + [row("stop_vague_pause", 999)]
lines_b = [json.dumps(r, ensure_ascii=False) for r in rows_b] + [malformed, ""]
open(os.path.join(work, "ledger_b.jsonl"), "w", encoding="utf-8").write("\n".join(lines_b) + "\n")
# classification-map sidecar (PMO retro artifact)
cmap = {"stop_vague_pause": "policy_violation", "stop_user_complete": "user_stop_legitimate",
        "stop_escalation": "decider_escalation_required"}
open(os.path.join(work, "cmap.json"), "w", encoding="utf-8").write(json.dumps(cmap, ensure_ascii=False))
# dedup: byte-identical row × 2
dup = json.dumps(row("stop_vague_pause", 0), ensure_ascii=False)
open(os.path.join(work, "dup.jsonl"), "w", encoding="utf-8").write(dup + "\n" + dup + "\n")
# empty ledger
open(os.path.join(work, "empty.jsonl"), "w", encoding="utf-8").write("")
# emission-liveness base (1 row → 이후 append 로 landing 관측)
open(os.path.join(work, "emit.jsonl"), "w", encoding="utf-8").write(
    json.dumps(row("stop_user_complete", 0), ensure_ascii=False) + "\n")
print("fixtures-ready")
PY

LA="$WORK/ledger_a.jsonl"
LB="$WORK/ledger_b.jsonl"
CMAP="$WORK/cmap.json"

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2573 AC-4: stop-event aggregate — execution-backed (real invocation)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ── 케이스 1: classification-map 有 → per-reason_class count + ratio ──────────────────
OUT_A="$WORK/out_a.json"; EC=0
python3 "$AGG" --ledger "$LA" --classification-map "$CMAP" --json > "$OUT_A" 2>"$WORK/a.err" || EC=$?
assert_eq "map有: exit 0 (record-only non-blocking)" "$EC" "0" "aggregate 는 항상 exit 0"
# distinct-marker: JSON schema_note 필드 존재 = 실제 aggregate fork 관측 (미 fork 시 빈 stdout → 아래 전부 RED)
assert_has "map有: distinct-marker (schema_note 필드)" "$(cat "$OUT_A")" "stop-event-v1 §5.1 aggregate"
assert_eq "map有: policy_violation count" "$(jget "$OUT_A" reason_class_counts.policy_violation)" "3"
assert_eq "map有: user_stop_legitimate count" "$(jget "$OUT_A" reason_class_counts.user_stop_legitimate)" "2"
assert_eq "map有: decider_escalation_required count" "$(jget "$OUT_A" reason_class_counts.decider_escalation_required)" "1"
assert_eq "map有: unclassified (legacy 무매핑 2)" "$(jget "$OUT_A" unclassified_total)" "2"
assert_eq "map有: illegitimate_total" "$(jget "$OUT_A" illegitimate_total)" "3"
assert_eq "map有: legitimate_total" "$(jget "$OUT_A" legitimate_total)" "3"
assert_eq "map有: ratio 부당:정당 관측값" "$(jget "$OUT_A" ratio_illegitimate_to_legitimate)" "3:3"
assert_eq "map有: rows_total (valid dict 8)" "$(jget "$OUT_A" rows_total)" "8"
assert_eq "map有: classification_map_present" "$(jget "$OUT_A" classification_map_present)" "True"

# ── 하드코딩 방어: 2-fixture cross-run (B = A + vague 1개 → policy_violation delta == +1) ──
OUT_B="$WORK/out_b.json"; EC=0
python3 "$AGG" --ledger "$LB" --classification-map "$CMAP" --json > "$OUT_B" 2>/dev/null || EC=$?
PV_A="$(jget "$OUT_A" reason_class_counts.policy_violation)"
PV_B="$(jget "$OUT_B" reason_class_counts.policy_violation)"
assert_eq "cross-run: policy_violation delta (falsify 하드코딩)" "$((PV_B - PV_A))" "1" "B=A+vague1 → +1"
assert_eq "cross-run: ratio B shift 4:3 (관측값 변화)" "$(jget "$OUT_B" ratio_illegitimate_to_legitimate)" "4:3"

# ── 케이스 2: classification-map 無 → all-unclassified + "측정 ≠ 분류" honesty + ratio N/A ──
OUT_N="$WORK/out_n.json"; EC=0
python3 "$AGG" --ledger "$LA" --json > "$OUT_N" 2>/dev/null || EC=$?
assert_eq "map無: exit 0" "$EC" "0"
assert_eq "map無: classified_total 0" "$(jget "$OUT_N" classified_total)" "0"
assert_eq "map無: unclassified_total 8 (all)" "$(jget "$OUT_N" unclassified_total)" "8"
assert_eq "map無: classification_map_present" "$(jget "$OUT_N" classification_map_present)" "False"
assert_has "map無: ratio N/A (분류 없음)" "$(jget "$OUT_N" ratio_illegitimate_to_legitimate)" "N/A"
# "측정 ≠ 분류" honesty 서술 present (binding emit 의무 — stop-event-v1 §5.1)
assert_has "map無: '측정 ≠ 분류' honesty 서술 present" "$(cat "$OUT_N")" "측정 ≠ 분류"

# ── record-only INV: aggregate 실행 전후 원장 byte-identical (sha256) ──────────────────
SHA_BEFORE="$(sha256_of "$LA")"
python3 "$AGG" --ledger "$LA" --classification-map "$CMAP" >/dev/null 2>&1     # render mode
python3 "$AGG" --ledger "$LA" --classification-map "$CMAP" --json >/dev/null 2>&1  # json mode
SHA_AFTER="$(sha256_of "$LA")"
assert_eq "record-only INV: 원장 sha256 byte-identical (IN-PLACE EDIT 금지)" "$SHA_BEFORE" "$SHA_AFTER" \
  "aggregate 는 원장 read-only — 변경 시 record-only INV 위반"

# ── row-hash dedup: 동일 row 2회 → duplicates_collapsed ≥ 1 + rows_deduped 관측 ─────────
OUT_D="$WORK/out_d.json"; EC=0
python3 "$AGG" --ledger "$WORK/dup.jsonl" --classification-map "$CMAP" --json > "$OUT_D" 2>/dev/null || EC=$?
assert_eq "dedup: rows_total 2" "$(jget "$OUT_D" rows_total)" "2"
assert_ge "dedup: duplicates_collapsed >=1" "$(jget "$OUT_D" duplicates_collapsed)" "1"
assert_eq "dedup: rows_deduped 1 (병합 후)" "$(jget "$OUT_D" rows_deduped)" "1"

# ── malformed → skip+count (crash 0, raw payload echo 0) ─────────────────────────────
assert_eq "malformed: malformed_skipped 1" "$(jget "$OUT_A" malformed_skipped)" "1"
# raw payload echo 0 — malformed 원문 sentinel 이 어떤 출력에도 새어나오지 않음 (record-only sanitize)
RENDER_A="$(python3 "$AGG" --ledger "$LA" --classification-map "$CMAP" 2>&1)"
assert_nothas "malformed: raw payload echo 0 (render)" "$RENDER_A" "$MALFORMED_SENTINEL"
assert_nothas "malformed: raw payload echo 0 (json)" "$(cat "$OUT_A")" "$MALFORMED_SENTINEL"

# ── empty / 부재 ledger → zero-count exit 0 ──────────────────────────────────────────
OUT_E="$WORK/out_e.json"; EC=0
python3 "$AGG" --ledger "$WORK/empty.jsonl" --json > "$OUT_E" 2>/dev/null || EC=$?
assert_eq "empty: exit 0" "$EC" "0"
assert_eq "empty: rows_total 0" "$(jget "$OUT_E" rows_total)" "0"
assert_eq "empty: malformed_skipped 0" "$(jget "$OUT_E" malformed_skipped)" "0"
OUT_ABS="$WORK/out_abs.json"; EC=0
python3 "$AGG" --ledger "$WORK/does-not-exist.jsonl" --json > "$OUT_ABS" 2>/dev/null || EC=$?
assert_eq "absent: exit 0 (non-blocking honest)" "$EC" "0"
assert_eq "absent: rows_total 0" "$(jget "$OUT_ABS" rows_total)" "0"

# ── emission-liveness: 실 emit(synthetic append) → aggregate 가 그 row 를 실제 집계(landing) ──
OUT_M1="$WORK/out_m1.json"; python3 "$AGG" --ledger "$WORK/emit.jsonl" --json > "$OUT_M1" 2>/dev/null
assert_eq "emission-liveness: pre-append rows_total 1" "$(jget "$OUT_M1" rows_total)" "1"
# stop-event 실 emit 모사 — 신규 row append (vague_pause)
python3 - "$WORK/emit.jsonl" <<'PY'
import json, sys
row = {"timestamp_kst": "2026-07-05T10:05:00+09:00", "hook_source": "stop",
       "hook_decision": "record-only", "session_id": "sess-emit-1", "stop_reason": "stop_vague_pause"}
with open(sys.argv[1], "a", encoding="utf-8") as f:
    f.write(json.dumps(row, ensure_ascii=False) + "\n")
PY
OUT_M2="$WORK/out_m2.json"; python3 "$AGG" --ledger "$WORK/emit.jsonl" --classification-map "$CMAP" --json > "$OUT_M2" 2>/dev/null
assert_eq "emission-liveness: post-append rows_total 2 (landing 관측)" "$(jget "$OUT_M2" rows_total)" "2"
assert_eq "emission-liveness: appended row frequency 집계" "$(jget "$OUT_M2" stop_reason_frequency.stop_vague_pause)" "1"
assert_eq "emission-liveness: appended row 분류 (policy_violation +1)" "$(jget "$OUT_M2" reason_class_counts.policy_violation)" "1"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — aggregate-stop-event (AC-4)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — emission-liveness + record-only INV + dedup honest-count + '측정≠분류' honesty 실증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
