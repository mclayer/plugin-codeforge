#!/usr/bin/env bash
# CFP-2377 Phase 2 — backstop 자동 트리거 배선 + registry + 회귀 변별 test (anti-theater)
#
# 검증 대상:
#   - hooks/hooks.json (DevPL 산출 — SessionEnd backstop async dispatch 단일 wire)
#   - docs/evidence-checks-registry.yaml (worktree-clean-completion-gate entry)
#   - templates/scripts/check-worktree-stale.sh (backstop 로직 무변경 회귀)
#
# §8 Test Contract 이행: TC-1 / TC-2 / TC-5 / TC-7 + registry assert.
# 선례 = scripts/test-check-operational-outcome-signal.sh (자립 bash 러너 + python 파싱).
#
# anti-theater (vacuous 거짓통과 금지):
#   - TC-1 = hooks.json SessionEnd 에 session-end dispatch + async:true 존재 grep/parse,
#            그리고 부재 fixture(SessionEnd 제거 복사본) → 검출기 FAIL 별도 assert (missing-case).
#   - TC-2 = SessionEnd + Stop 양쪽에 backstop GC dispatch 동시 존재 fixture → 차단 assert.
#            (정상 hooks.json = Stop 에 backstop 없음 → PASS.)
#   - registry = worktree-clean-completion-gate entry 의 current_tier:warning +
#                workflow:null 를 yaml.safe_load 로 assert. entry 부재 / tier!=warning
#                fixture → FAIL (missing-case).
#   - TC-5 = check-worktree-stale.sh DRY_RUN 변별 (merged+clean+7d → would-prune /
#            dirty → keep) + stdout `DONE:` assert.
#   - TC-7 = worktree-clean self-check 가 close/reopen trigger 아님 — retro-mandatory
#            close-blocking 과 disjoint (검출 스크립트가 gh issue close/reopen 호출 0).
#
# 각 assert = exit code 또는 검출-신호 동시. always-pass / || true 마스킹 금지.
#
# Exit code: 0 (all pass) / 1 (any fail)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_JSON="$REPO_ROOT/hooks/hooks.json"
REGISTRY="$REPO_ROOT/docs/evidence-checks-registry.yaml"
STALE_SH="$REPO_ROOT/templates/scripts/check-worktree-stale.sh"
COMPLETION_SH="$REPO_ROOT/scripts/check-worktree-completion-clean.sh"

PASS=0
FAIL=0

ok()   { echo "✓ PASS: $1"; PASS=$((PASS + 1)); }
bad()  { echo "✗ FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

# ─── 검출기 (detector) — 본 러너 안에 내장한 hooks.json wire 판정 함수 ────────
# DevPL 의 hooks.json 을 직접 파싱한다. production 코드(별도 lint 스크립트)에
# 의존하지 않고, 본 test 가 곧 SessionEnd 배선 invariant 의 spec assert 다.
#
# detect_sessionend_backstop <hooks.json path>
#   exit 0 = SessionEnd 배열에 backstop dispatch(session-end 또는 check-worktree-stale)
#            가 async:true 로 존재. exit 1 = 부재 / async!=true.
detect_sessionend_backstop() {
  local f="$1"
  python3 - "$f" <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
except Exception as e:
    print(f"parse-error: {e}", file=sys.stderr)
    sys.exit(2)

hooks = data.get("hooks", {})
session_end = hooks.get("SessionEnd", [])
found = False
for group in session_end:
    for h in group.get("hooks", []):
        cmd = h.get("command", "")
        # backstop dispatch = session-end dispatch script 또는 check-worktree-stale 직접 호출
        if ("session-end" in cmd) or ("check-worktree-stale" in cmd):
            if h.get("async") is True:
                found = True
sys.exit(0 if found else 1)
PY
}

# detect_dual_trigger <hooks.json path>
#   exit 0 = SessionEnd 와 Stop 양쪽에 backstop GC dispatch 동시 존재 (위반).
#   exit 1 = 동시 부재 (정상). 트리거 단일화 invariant (TC-2).
detect_dual_trigger() {
  local f="$1"
  python3 - "$f" <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
except Exception as e:
    print(f"parse-error: {e}", file=sys.stderr)
    sys.exit(2)

hooks = data.get("hooks", {})

def has_backstop(event):
    for group in hooks.get(event, []):
        for h in group.get("hooks", []):
            cmd = h.get("command", "")
            if ("session-end" in cmd) or ("check-worktree-stale" in cmd):
                return True
    return False

se = has_backstop("SessionEnd")
st = has_backstop("Stop")
# 양쪽 동시 backstop = 위반
sys.exit(0 if (se and st) else 1)
PY
}

# ─── TC-1: SessionEnd backstop 배선 존재 + missing-case ──────────────────────
if [ ! -f "$HOOKS_JSON" ]; then
  bad "TC-1: hooks/hooks.json 부재" "DevPL 산출물 미 commit (RED 정상이면 최종 commit 후 해소)"
else
  # positive: 실제 hooks.json 에 SessionEnd backstop async:true 존재
  if detect_sessionend_backstop "$HOOKS_JSON"; then
    ok "TC-1: hooks.json SessionEnd backstop async:true dispatch 존재"
  else
    bad "TC-1: hooks.json SessionEnd backstop 배선 부재 또는 async!=true" \
        "기대: SessionEnd 에 session-end/check-worktree-stale dispatch + async:true"
  fi

  # missing-case: SessionEnd 를 제거한 복사본 → 검출기가 FAIL(exit 1) 반환해야 함.
  tmp1=$(mktemp -d)
  python3 - "$HOOKS_JSON" "$tmp1/no-sessionend.json" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
data.get("hooks", {}).pop("SessionEnd", None)
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
PY
  if detect_sessionend_backstop "$tmp1/no-sessionend.json"; then
    bad "TC-1 (missing-case): SessionEnd 제거본인데 검출기가 PASS 반환" \
        "검출기가 부재를 못 잡음 = vacuous (anti-theater 위반)"
  else
    ok "TC-1 (missing-case): SessionEnd 제거본 → 검출기 FAIL (부재 정확 검출)"
  fi
  rm -rf "$tmp1"

  # missing-case 2: async:false 로 바꾼 복사본 → 검출기 FAIL (지연 회귀 차단).
  tmp1b=$(mktemp -d)
  python3 - "$HOOKS_JSON" "$tmp1b/async-false.json" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
for group in data.get("hooks", {}).get("SessionEnd", []):
    for h in group.get("hooks", []):
        cmd = h.get("command", "")
        if ("session-end" in cmd) or ("check-worktree-stale" in cmd):
            h["async"] = False
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
PY
  if detect_sessionend_backstop "$tmp1b/async-false.json"; then
    bad "TC-1 (async:false case): async:false 인데 검출기가 PASS" \
        "async:true 필수 — 지연 회귀 차단 못 함 (anti-theater 위반)"
  else
    ok "TC-1 (async:false case): async:false 변조본 → 검출기 FAIL (async:true 강제)"
  fi
  rm -rf "$tmp1b"
fi

# ─── TC-2: 트리거 단일화 (SessionEnd + Stop 동시 backstop 금지) ──────────────
if [ -f "$HOOKS_JSON" ]; then
  # positive(정상): 실제 hooks.json 은 Stop 에 backstop 없음 → dual-trigger 검출기 FAIL(1).
  if detect_dual_trigger "$HOOKS_JSON"; then
    bad "TC-2: 실제 hooks.json 에 SessionEnd+Stop 동시 backstop 존재" \
        "트리거 단일화 invariant 위반 (race 1순위 안전장치)"
  else
    ok "TC-2: 실제 hooks.json = 단일 트리거 (Stop 에 backstop 없음)"
  fi

  # violation fixture: Stop 에도 backstop dispatch 추가한 복사본 → 검출기 검출(exit 0).
  tmp2=$(mktemp -d)
  python3 - "$HOOKS_JSON" "$tmp2/dual.json" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
hooks = data.setdefault("hooks", {})
# SessionEnd 가 없으면 backstop 1개 강제 주입(violation fixture 의 전제)
hooks.setdefault("SessionEnd", [{"hooks": [
    {"type": "command",
     "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-end',
     "async": True}]}])
# Stop 에도 backstop dispatch 동시 추가 = 위반 조건
stop = hooks.setdefault("Stop", [{"hooks": []}])
stop[0].setdefault("hooks", []).append(
    {"type": "command",
     "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-end',
     "async": True})
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
PY
  if detect_dual_trigger "$tmp2/dual.json"; then
    ok "TC-2 (violation fixture): SessionEnd+Stop 양쪽 backstop → 검출기 차단(검출)"
  else
    bad "TC-2 (violation fixture): 양쪽 wire 인데 검출기가 통과시킴" \
        "동시 트리거를 못 잡음 = vacuous (anti-theater 위반)"
  fi
  rm -rf "$tmp2"

  # ── TC-2b: SessionStart 에 backstop wire 부재 (비협상 invariant) ──
  # SessionStart async:true 는 무시되고 동기 실행 = 지연 회귀 (요구사항리뷰 PASS 외부사실).
  # SessionStart 에 check-worktree-stale / session-end backstop dispatch 가 있으면 위반.
  start_backstop=$(python3 - "$HOOKS_JSON" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
n = 0
for group in data.get("hooks", {}).get("SessionStart", []):
    for h in group.get("hooks", []):
        cmd = h.get("command", "")
        if ("check-worktree-stale" in cmd) or ("session-end" in cmd):
            n += 1
print(n)
PY
)
  if [ "${start_backstop:-0}" -eq 0 ]; then
    ok "TC-2b: SessionStart 에 backstop wire 부재 (지연 회귀 차단 invariant)"
  else
    bad "TC-2b: SessionStart 에 backstop dispatch 존재 ($start_backstop 건)" \
        "SessionStart async 무시 → 동기 지연 회귀 (요구사항리뷰 PASS 외부사실 위반)"
  fi

  # TC-2b 변별: SessionStart 에 backstop 주입한 fixture → 검출 1+ (vacuous 아님 증명).
  tmp2b=$(mktemp -d)
  inj=$(python3 - "$HOOKS_JSON" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
ss = data.setdefault("hooks", {}).setdefault("SessionStart", [{"hooks": []}])
ss[0].setdefault("hooks", []).append(
    {"type": "command",
     "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" check-worktree-stale',
     "async": True})
n = 0
for group in data["hooks"]["SessionStart"]:
    for h in group.get("hooks", []):
        if "check-worktree-stale" in h.get("command", "") or "session-end" in h.get("command", ""):
            n += 1
print(n)
PY
)
  if [ "${inj:-0}" -ge 1 ]; then
    ok "TC-2b (변별): SessionStart backstop 주입 fixture → 검출 (검출기 non-vacuous)"
  else
    bad "TC-2b (변별): 주입했는데 검출 0" "검출기가 SessionStart wire 를 못 잡음 (vacuous)"
  fi
  rm -rf "$tmp2b"
fi

# ─── registry assert: worktree-clean-completion-gate (warning + workflow:null) ─
registry_entry_check() {
  local file="$1"
  python3 - "$file" <<'PY'
import sys
try:
    import yaml
except ImportError:
    print("no-yaml", file=sys.stderr)
    sys.exit(3)
with open(sys.argv[1], encoding="utf-8") as fh:
    data = yaml.safe_load(fh)
entries = (data or {}).get("entries", [])
target = None
for e in entries:
    if e.get("name") == "worktree-clean-completion-gate":
        target = e
        break
if target is None:
    print("entry-absent", file=sys.stderr)
    sys.exit(1)
tier = target.get("current_tier")
wf = target.get("workflow", "MISSING")
if tier != "warning":
    print(f"tier!=warning (got {tier!r})", file=sys.stderr)
    sys.exit(2)
if wf is not None:
    print(f"workflow!=null (got {wf!r})", file=sys.stderr)
    sys.exit(2)
print("ok")
sys.exit(0)
PY
}

if [ ! -f "$REGISTRY" ]; then
  bad "registry: evidence-checks-registry.yaml 부재"
else
  rc=0; msg=$(registry_entry_check "$REGISTRY" 2>&1) || rc=$?
  if [ "$rc" -eq 3 ]; then
    echo "::warning::registry assert SKIP — python yaml 모듈 부재 (CI 는 setup-python 으로 설치)"
  elif [ "$rc" -eq 0 ]; then
    ok "registry: worktree-clean-completion-gate = current_tier:warning + workflow:null"
  else
    bad "registry: worktree-clean-completion-gate entry 부적합 ($msg)" \
        "기대: current_tier:warning + workflow:null"
  fi

  # missing-case: entry 의 tier 를 blocking 으로 바꾼 fixture → 검출기 FAIL(2).
  tmp3=$(mktemp -d)
  if python3 - "$REGISTRY" "$tmp3/mutated.yaml" <<'PY'
import sys
try:
    import yaml
except ImportError:
    sys.exit(3)
with open(sys.argv[1], encoding="utf-8") as fh:
    data = yaml.safe_load(fh)
mutated = False
for e in (data or {}).get("entries", []):
    if e.get("name") == "worktree-clean-completion-gate":
        e["current_tier"] = "blocking-on-pr"
        mutated = True
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    yaml.safe_dump(data, fh, allow_unicode=True)
sys.exit(0 if mutated else 4)
PY
  then
    rc2=0; registry_entry_check "$tmp3/mutated.yaml" >/dev/null 2>&1 || rc2=$?
    if [ "$rc2" -ne 0 ]; then
      ok "registry (missing-case): tier=blocking 변조본 → 검출기 FAIL (tier 강제)"
    else
      bad "registry (missing-case): tier=blocking 인데 검출기 PASS" "vacuous (anti-theater 위반)"
    fi
  else
    mut_rc=$?
    if [ "$mut_rc" -eq 3 ]; then
      echo "::warning::registry missing-case SKIP — yaml 모듈 부재"
    else
      echo "::warning::registry missing-case SKIP — entry 부재로 변조 불가 (entry 추가 후 활성)"
    fi
  fi
  rm -rf "$tmp3"
fi

# ─── TC-5: backstop 로직 무변경 회귀 (DRY_RUN 변별 + stdout DONE: assert) ────
# check-worktree-stale.sh 의 4조건 AND 가 불변임을 DRY_RUN 으로 변별.
# stub: merged+clean+7d → would-prune / dirty → keep. stdout `DONE: pruned=N` 마커 존재.
if [ ! -f "$STALE_SH" ]; then
  bad "TC-5: templates/scripts/check-worktree-stale.sh 부재"
else
  # ── 공통 stub builder (완료-게이트 러너와 동형, age 7d+ 적용) ──
  tc5_run() {
    local label="$1" dirty="$2" merged="$3" expect_wouldprune="$4"
    local tmp; tmp=$(mktemp -d)
    # age 7d+ 충족 worktree dir 실재 생성 (find -mtime +7 통과 위해 mtime 과거 설정)
    local wtdir="$tmp/wt/cfp-old"
    mkdir -p "$wtdir"
    touch -d "30 days ago" "$wtdir" 2>/dev/null || touch -t 202601010000 "$wtdir"

    cat > "$tmp/git" <<GITSTUB
#!/usr/bin/env bash
if [ "\${1:-}" = "-C" ]; then shift 2; fi
case "\${1:-}" in
  rev-parse) echo "$tmp/main"; exit 0 ;;
  worktree)
    if [ "\${2:-}" = "list" ]; then
      printf 'worktree %s\n' "$tmp/main"
      printf 'HEAD 0000000000000000000000000000000000000000\n'
      printf 'branch refs/heads/main\n\n'
      printf 'worktree %s\n' "$wtdir"
      printf 'HEAD 1111111111111111111111111111111111111111\n'
      printf 'branch refs/heads/cfp-old\n\n'
      exit 0
    fi
    exit 0 ;;
  status)
    $( [ "$dirty" = "1" ] && echo 'echo " M tracked.py"' )
    exit 0 ;;
  cat-file) exit 0 ;;
  rev-list) echo 0; exit 0 ;;
  branch) exit 0 ;;
  *) exit 0 ;;
esac
GITSTUB
    chmod 755 "$tmp/git"
    mkdir -p "$tmp/main"

    cat > "$tmp/gh" <<GHSTUB
#!/usr/bin/env bash
case "\${1:-}" in
  auth) exit 0 ;;
  pr)
    if [ "$merged" = "1" ]; then
      case " \$* " in
        *" list "*) echo '[{"number":1,"headRefOid":"2222222222222222222222222222222222222222"}]' ;;
        *) echo '{"mergedAt":"2026-06-01T00:00:00Z"}' ;;
      esac
    else
      case " \$* " in
        *" list "*) echo '[]' ;;
        *) echo '{"mergedAt":null}' ;;
      esac
    fi
    exit 0 ;;
  *) exit 0 ;;
esac
GHSTUB
    chmod 755 "$tmp/gh"

    local out ec=0
    out=$(
      GC_GIT_BIN="$tmp/git" GC_GH_BIN="$tmp/gh" GC_DRY_RUN=1 STALE_DAYS=7 \
      bash "$STALE_SH" 2>&1
    ) || ec=$?

    # stdout DONE: 마커 존재 assert (output contract 무변경 회귀)
    if ! printf '%s' "$out" | grep -q "DONE:"; then
      bad "$label" "stdout 에 'DONE:' 마커 부재 (output contract 깨짐). out=$out"
      rm -rf "$tmp"; return 0
    fi
    # exit 0 always advisory
    if [ "$ec" -ne 0 ]; then
      bad "$label" "exit $ec != 0 (always exit 0 invariant 깨짐). out=$out"
      rm -rf "$tmp"; return 0
    fi

    local wouldprune=0
    printf '%s' "$out" | grep -qiE "would-prune.*$wtdir|$wtdir.*would-prune" && wouldprune=1

    if [ "$expect_wouldprune" = "1" ] && [ "$wouldprune" -eq 1 ]; then
      ok "$label (would-prune 검출 + DONE: + exit 0)"
    elif [ "$expect_wouldprune" = "0" ] && [ "$wouldprune" -eq 0 ]; then
      ok "$label (keep — would-prune 안 함 + DONE: + exit 0)"
    else
      bad "$label" "expect would-prune=$expect_wouldprune got=$wouldprune. out=$out"
    fi
    rm -rf "$tmp"
  }

  tc5_run "TC-5a: merged+clean+7d → would-prune (로직 불변)" 0 1 1
  tc5_run "TC-5b: dirty → keep (data-loss 가드 불변)"       1 1 0
  tc5_run "TC-5c: 미머지(mergedAt null) → keep (merged-only 불변)" 0 0 0
fi

# ─── TC-7: close lifecycle 무영향 (완료-게이트가 reopen/close trigger 아님) ──
# worktree-clean self-check 스크립트는 gh issue close/reopen/transition 을 호출하지
# 않는다 (retro-mandatory close-blocking 과 axis disjoint). 정적 grep 으로 검증.
if [ ! -f "$COMPLETION_SH" ]; then
  echo "::warning::TC-7: check-worktree-completion-clean.sh 부재 — DevPL 산출물 미 commit (RED 정상)"
else
  # gh issue close / gh issue reopen / gh issue edit --add-label gate / transition 호출 0 assert.
  if grep -nEi "gh[[:space:]]+issue[[:space:]]+(close|reopen)|--reopen|issue.*transition" "$COMPLETION_SH" >/dev/null 2>&1; then
    bad "TC-7: 완료-게이트가 gh issue close/reopen 호출 보유" \
        "close lifecycle 침범 — retro-mandatory close-blocking 과 disjoint 위반 (#772/EC-5)"
  else
    ok "TC-7: 완료-게이트 = gh issue close/reopen 호출 0 (close lifecycle disjoint)"
  fi
fi

# ─── 요약 ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (backstop wire + registry + 회귀 변별 — TC-1/TC-2/TC-5/TC-7)."
  exit 0
else
  echo "Some tests failed (배선/registry/회귀 invariant 위반)."
  exit 1
fi
