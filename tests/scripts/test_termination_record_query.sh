#!/usr/bin/env bash
# tests/scripts/test_termination_record_query.sh
# CFP-2984 Phase 2 (구현 lane) — AC-11 discriminating self-test.
#
# AC-11: 비정상 종료 픽스처 1건이 입력될 때 조회 경로를 실행하면, 현행 스키마에
#        이미 존재하는 종료원인과 마지막 진행시각 2개 값이 구조화 레코드 1행으로 반환된다.
#
# ★ 스키마 수정 0 (비협상): `spawn-event-v1` · `stop-event-v1` 은 READ only.
#   - 종료원인   = `termination_cause` (spawn-event-v1 closed enum)
#   - 진행시각   = `timestamp` (spawn-event-v1) / `timestamp_kst` (stop-event-v1)
#   두 필드 모두 **현행 스키마에 이미 존재**한다 — 신규 필드 0.
#   enum 값공간은 하드코딩 사본이 아니라 `scripts/lib/append_spawn_event.py` 의
#   `_TERMINATION_CAUSES` 를 **파싱해** 얻는다 (fixture-vs-SSOT drift 차단).
#
# ★ '마지막 진행시각' 의 정의 (모호 제거): 종료 레코드 **자신을 제외한** 나머지 행 중
#   최대 timestamp. 종료 시각과 구별해야 소각 span 추정이 가능하다.
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): baseline 픽스처가 **정확한 2값**을 담은
#   레코드 1행을 내는 것을 먼저 확인한다(대조군). 항상-ERROR 구현은 baseline 에서,
#   항상-RECORD 구현은 결손 픽스처에서 깨진다.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCHEMA_PY="$REPO_ROOT/scripts/lib/append_spawn_event.py"
PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/query.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-11 종료 레코드 조회. usage: query.py <fixture.jsonl> <schema.py> [variant]

stdout 계약 (정확히 1줄):
  RECORD termination_cause=<enum> last_progress_at=<KST ISO>   rc=0
  NONE no-abnormal-termination                                 rc=2
  ERROR <reason>                                               rc=1
"""
import datetime
import json
import re
import sys

# 조회 필드 키 동의어 (스키마 키 매핑 — 개명 후에도 동일 필드로 조회된다).
CAUSE_KEYS = ("termination_cause", "exit_reason", "종료원인")
TS_KEYS = ("timestamp", "timestamp_kst", "ts", "occurred_at")
KST = datetime.timezone(datetime.timedelta(hours=9))


def load_enum(schema_path):
    """현행 스키마 파일에서 termination_cause closed enum 을 파싱 (하드코딩 사본 금지)."""
    src = open(schema_path, encoding="utf-8").read()
    m = re.search(r"_TERMINATION_CAUSES\s*=\s*\{([^}]*)\}", src)
    if not m:
        return None
    return {v.strip().strip('"').strip("'") for v in m.group(1).split(",") if v.strip()}


def pick(row, keys, variant):
    if variant == "mut-no-key-mapping":
        keys = keys[:1]          # 리터럴 1개 키만 인식 (동의어 개명 미해소)
    for k in keys:
        if k in row:
            return row[k]
    return None


def parse_ts(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    if s.isdigit():
        n = float(s)
        return n / 1000.0 if len(s) >= 13 else n
    try:
        return datetime.datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def emit(line, rc):
    print(line)
    return rc


def main():
    fixture, schema_path = sys.argv[1], sys.argv[2]
    variant = sys.argv[3] if len(sys.argv) > 3 else "ref"

    enum = load_enum(schema_path)
    if not enum:
        return emit("ERROR schema-enum-unreadable", 1)
    abnormal = {e for e in enum if e != "normal"}
    if not abnormal:
        return emit("ERROR schema-enum-degenerate", 1)

    rows = []
    for ln in open(fixture, encoding="utf-8").read().split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except ValueError:
            return emit("ERROR unparseable-row", 1)
    if not rows:
        return emit("ERROR empty-fixture", 1)

    term_idx, cause = None, None
    for i, r in enumerate(rows):
        c = pick(r, CAUSE_KEYS, variant)
        if c is None:
            continue
        term_idx, cause = i, c
        break

    if term_idx is None:
        return emit("ERROR missing-termination-cause", 1)
    if not isinstance(cause, str) or not cause:
        return emit("ERROR missing-termination-cause", 1)
    if cause not in enum:
        return emit("ERROR invalid-termination-cause", 1)
    if cause not in abnormal:
        return emit("NONE no-abnormal-termination", 2)

    progress = []
    for i, r in enumerate(rows):
        if i == term_idx:
            continue                      # 종료 레코드 자신은 진행시각이 아니다
        t = parse_ts(pick(r, TS_KEYS, variant))
        if t is not None:
            progress.append(t)
    if not progress:
        return emit("ERROR missing-progress-timestamp", 1)

    last = datetime.datetime.fromtimestamp(max(progress), KST).isoformat()
    return emit("RECORD termination_cause=%s last_progress_at=%s" % (cause, last), 0)


sys.exit(main())
PY

cat > "$WORK/gen.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-11 fixture generator. usage: gen.py <dst> <op>"""
import json
import sys

dst, op = sys.argv[1], sys.argv[2]

C_KEY = "termination_cause"
T_KEY = "timestamp"


def base(cause="timeout", cause_key=C_KEY, ts_key=T_KEY):
    return [
        {"schema_version": "spawn-event-v1", "event_id": "ev-1", ts_key: "2026-08-15T21:40:00+09:00",
         "agent_type": "DeveloperAgent", "story_key": "CFP-2984", "event_type": "spawn"},
        {"schema_version": "spawn-event-v1", "event_id": "ev-1", ts_key: "2026-08-15T21:52:30+09:00",
         "agent_type": "DeveloperAgent", "story_key": "CFP-2984", "event_type": "progress"},
        {"schema_version": "spawn-event-v1", "event_id": "ev-1", ts_key: "2026-08-15T21:58:10+09:00",
         "agent_type": "DeveloperAgent", "story_key": "CFP-2984", "event_type": "stop",
         "outcome": "failure", cause_key: cause},
    ]


if op == "abnormal-timeout":
    rows = base("timeout")
elif op == "abnormal-cancelled":
    rows = base("cancelled")
elif op == "normal":
    rows = base("normal")
elif op == "drop-cause-field":
    # (1) 제거 — 조회 필드(종료원인) 삭제
    rows = base("timeout")
    del rows[2][C_KEY]
elif op == "drop-progress-rows":
    # (1) 제거 — 진행 행 삭제 (종료 행만 남음 → 마지막 진행시각 조회 불가)
    rows = [base("timeout")[2]]
elif op == "null-cause":
    # (2) 주입 — 필드 결손 픽스처 (키는 있고 값이 null)
    rows = base("timeout")
    rows[2][C_KEY] = None
elif op == "out-of-enum-cause":
    # (2) 주입 — 현행 closed enum 밖 값
    rows = base("exploded")
elif op == "synonym-keys":
    # (3) 등가변형(GREEN) — 조회 2필드를 동의 키명으로 개명 (스키마 키 매핑으로 해소)
    rows = base("timeout", cause_key="exit_reason", ts_key="ts")
elif op == "synonym-keys-drop-cause":
    # (3) 등가변형(RED) — 동의어 개명 + 종료원인 삭제 (표기 회피로 결함을 숨기려는 변이)
    rows = base("timeout", cause_key="exit_reason", ts_key="ts")
    del rows[2]["exit_reason"]
elif op == "multi-progress":
    # 다행 픽스처 — 반환은 여전히 구조화 레코드 '1행' 이어야 한다
    rows = base("timeout")
    rows.insert(2, {"schema_version": "spawn-event-v1", "event_id": "ev-1",
                    T_KEY: "2026-08-15T21:55:00+09:00", "agent_type": "DeveloperAgent",
                    "story_key": "CFP-2984", "event_type": "progress"})
else:
    raise SystemExit("unknown op: %s" % op)

with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
PY

cat > "$WORK/schema_mut.py" <<'PY'
# -*- coding: utf-8 -*-
"""현행 스키마 사본에서 enum 값 1개 제거. usage: schema_mut.py <src> <dst> <value>"""
import re
import sys

src, dst, val = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()
m = re.search(r"_TERMINATION_CAUSES\s*=\s*\{([^}]*)\}", s)
assert m, "enum anchor not found"
inner = m.group(1)
new_inner = ", ".join(v.strip() for v in inner.split(",")
                      if v.strip() and v.strip().strip('"').strip("'") != val)
s = s[:m.start(1)] + new_inner + s[m.end(1):]
with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s)
PY

# ─────────────────────────────────────────────────────────────────────────────
query_case() {
  local name="$1" expected_rc="$2" expected_out="$3" fixture="$4" schema="$5" variant="${6:-ref}"
  local rc=0 out lines ok=1
  out=$("$PYBIN" "$WORK/query.py" "$fixture" "$schema" "$variant" 2>&1) || rc=$?
  lines=$(printf '%s\n' "$out" | grep -c . || true)
  [ "$rc" -eq "$expected_rc" ] || ok=0
  [ "$out" = "$expected_out" ] || ok=0
  [ "$lines" -eq 1 ] || ok=0
  if [ "$ok" -eq 1 ]; then
    echo "OK   $name — rc=$rc out='$out'"
    PASS=$((PASS+1))
  else
    echo "FAIL $name"
    echo "       expected rc=$expected_rc out='$expected_out' (1 line)"
    echo "       actual   rc=$rc out='$out' (lines=$lines)"
    FAIL=$((FAIL+1))
  fi
}

gen() {
  "$PYBIN" "$WORK/gen.py" "$WORK/$1.jsonl" "$1"
}

echo "── AC-11 termination record query ──"

for op in abnormal-timeout abnormal-cancelled normal drop-cause-field drop-progress-rows \
          null-cause out-of-enum-cause synonym-keys synonym-keys-drop-cause multi-progress; do
  gen "$op"
done

REC_TIMEOUT="RECORD termination_cause=timeout last_progress_at=2026-08-15T21:52:30+09:00"

# 대조군 (INV-T4) — 비정상 종료 픽스처 1건 → 2값을 담은 구조화 레코드 정확히 1행.
query_case "baseline: 비정상 종료(timeout) 픽스처" 0 "$REC_TIMEOUT" \
           "$WORK/abnormal-timeout.jsonl" "$SCHEMA_PY"
query_case "baseline2: 비정상 종료(cancelled)" 0 \
           "RECORD termination_cause=cancelled last_progress_at=2026-08-15T21:52:30+09:00" \
           "$WORK/abnormal-cancelled.jsonl" "$SCHEMA_PY"
query_case "negative control: 정상 종료 → 레코드 날조 금지" 2 "NONE no-abnormal-termination" \
           "$WORK/normal.jsonl" "$SCHEMA_PY"
query_case "다행 픽스처에서도 반환은 레코드 1행" 0 \
           "RECORD termination_cause=timeout last_progress_at=2026-08-15T21:55:00+09:00" \
           "$WORK/multi-progress.jsonl" "$SCHEMA_PY"

# ① 제거
query_case "M1 제거: 종료원인 필드 삭제" 1 "ERROR missing-termination-cause" \
           "$WORK/drop-cause-field.jsonl" "$SCHEMA_PY"
query_case "M2 제거: 진행 행 삭제(진행시각 조회 불가)" 1 "ERROR missing-progress-timestamp" \
           "$WORK/drop-progress-rows.jsonl" "$SCHEMA_PY"
# ② 주입
query_case "M3 주입: 종료원인 null (필드 결손)" 1 "ERROR missing-termination-cause" \
           "$WORK/null-cause.jsonl" "$SCHEMA_PY"
query_case "M4 주입: 현행 enum 밖 값" 1 "ERROR invalid-termination-cause" \
           "$WORK/out-of-enum-cause.jsonl" "$SCHEMA_PY"
# ③ 등가변형
query_case "M5 등가변형(GREEN): 2필드 동의 키명 개명" 0 "$REC_TIMEOUT" \
           "$WORK/synonym-keys.jsonl" "$SCHEMA_PY"
query_case "M6 등가변형(RED): 동의어 개명 + 종료원인 삭제" 1 "ERROR missing-termination-cause" \
           "$WORK/synonym-keys-drop-cause.jsonl" "$SCHEMA_PY"
# 키 매핑이 load-bearing 임을 증명 (제거하면 M5 가 깨진다)
query_case "M7 impl: 키 매핑 제거 시 동의어 픽스처 판독 불가" 1 "ERROR missing-termination-cause" \
           "$WORK/synonym-keys.jsonl" "$SCHEMA_PY" mut-no-key-mapping
# enum 을 스키마 파일에서 읽는다는 증명 (하드코딩 사본이면 이 케이스가 GREEN 으로 샌다)
if "$PYBIN" "$WORK/schema_mut.py" "$SCHEMA_PY" "$WORK/schema-no-timeout.py" timeout >/dev/null 2>&1; then
  query_case "M8 스키마 앵커: enum 에서 timeout 제거 → 값공간 밖" 1 "ERROR invalid-termination-cause" \
             "$WORK/abnormal-timeout.jsonl" "$WORK/schema-no-timeout.py"
else
  echo "FAIL M8 스키마 앵커 — enum 앵커 파싱 실패"
  FAIL=$((FAIL+1))
fi

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
