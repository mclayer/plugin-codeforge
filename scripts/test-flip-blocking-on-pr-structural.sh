#!/usr/bin/env bash
# CFP-2594 Phase 2 (Stage 3 flip) — flip mutation-killer structural test (anti-theater).
#
# 검증 대상 (Stage 3 Tier flip 활성 구조 불변):
#   (a) 2 워크플로에 active `continue-on-error: true` 부재 (재삽입 mutation → RED)
#       - .github/workflows/deferred-followup-reconcile.yml
#       - .github/workflows/deferral-carrier-declared.yml
#   (b) docs/evidence-checks-registry.yaml 의 2 entry current_tier == blocking-on-pr
#       (+ promoted_by == CFP-2594 provenance) — warning 회귀 mutation → RED
#   (c) deferred-followup-reconcile.yml author-verify step 의 exit 문이 `exit $status`
#       (D-5 forcing) — `exit 0` 회귀 mutation → RED
#
# 선례 = scripts/test-worktree-backstop-wire.sh (자립 bash 러너 + python 파싱 + mutation fixture).
#
# anti-theater (vacuous 거짓통과 금지): 각 assert 마다 mutation fixture 를 만들어 검출기가
#   실제로 회귀를 잡는지 별도 assert (positive + mutation-catch 쌍). always-pass / || true 마스킹 금지.
#
# honest ceiling: 본 test 는 flip **구조**(config)만 assert 한다 — 실 red-X hard-block 여부는
#   GitHub Actions 런타임 + branch-protection(6-tuple 무변경, non-required) 소관. structural-only.
#
# Exit code: 0 (all pass) / 1 (any fail)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WF_RECONCILE="$REPO_ROOT/.github/workflows/deferred-followup-reconcile.yml"
WF_CARRIER="$REPO_ROOT/.github/workflows/deferral-carrier-declared.yml"
REGISTRY="$REPO_ROOT/docs/evidence-checks-registry.yaml"

PASS=0
FAIL=0

ok()   { echo "✓ PASS: $1"; PASS=$((PASS + 1)); }
bad()  { echo "✗ FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

# ─── 검출기 (a): active continue-on-error: true ──────────────────────────────
# detect_active_continue_on_error <yml path>
#   exit 0 = 파일에 active(비-주석) `continue-on-error: true` YAML 키 존재.
#   exit 1 = 부재 (주석/prose 안 문자열은 무시 — lstrip 후 '#' 로 시작하는 라인 제외).
detect_active_continue_on_error() {
  local f="$1"
  python3 - "$f" <<'PY'
import re, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        lines = fh.readlines()
except Exception as e:
    print(f"read-error: {e}", file=sys.stderr)
    sys.exit(2)
found = False
for raw in lines:
    s = raw.lstrip()
    if s.startswith("#"):
        continue  # 주석 라인 — active 키 아님
    if re.match(r"continue-on-error:\s*true\b", s):
        found = True
        break
sys.exit(0 if found else 1)
PY
}

# ─── 검출기 (c): author-verify exit $status forcing ──────────────────────────
# detect_exit_status_forcing <yml path>
#   exit 0 = 파일에 active(비-주석) `exit $status` 라인 존재.
#   exit 1 = 부재.
detect_exit_status_forcing() {
  local f="$1"
  python3 - "$f" <<'PY'
import re, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        lines = fh.readlines()
except Exception as e:
    print(f"read-error: {e}", file=sys.stderr)
    sys.exit(2)
found = False
for raw in lines:
    s = raw.lstrip()
    if s.startswith("#"):
        continue
    # `exit $status` (주석 붙어도 OK): 라인이 exit $status 로 시작
    if re.match(r"exit\s+\$status\b", s):
        found = True
        break
sys.exit(0 if found else 1)
PY
}

# ─── 검출기 (b): registry entry current_tier == blocking-on-pr ────────────────
# registry_tier_check <registry path> <entry name>
#   exit 0 = entry.current_tier == blocking-on-pr AND entry.promoted_by == CFP-2594
#   exit 1 = entry 부재 / tier!=blocking-on-pr / promoted_by 불일치
#   exit 3 = yaml 모듈 부재 (CI 는 setup-python 으로 설치 — SKIP 처리)
registry_tier_check() {
  local file="$1" name="$2"
  python3 - "$file" "$name" <<'PY'
import sys
try:
    import yaml
except ImportError:
    print("no-yaml", file=sys.stderr)
    sys.exit(3)
with open(sys.argv[1], encoding="utf-8") as fh:
    data = yaml.safe_load(fh)
name = sys.argv[2]
target = None
for e in (data or {}).get("entries", []):
    if e.get("name") == name:
        target = e
        break
if target is None:
    print("entry-absent", file=sys.stderr)
    sys.exit(1)
tier = target.get("current_tier")
promoted_by = target.get("promoted_by")
if tier != "blocking-on-pr":
    print(f"tier!=blocking-on-pr (got {tier!r})", file=sys.stderr)
    sys.exit(1)
if promoted_by != "CFP-2594":
    print(f"promoted_by!=CFP-2594 (got {promoted_by!r})", file=sys.stderr)
    sys.exit(1)
print("ok")
sys.exit(0)
PY
}

# ═══════════════════════════════════════════════════════════════════════════
# (a) active continue-on-error: true 부재 — 2 워크플로
# ═══════════════════════════════════════════════════════════════════════════
for wf in "$WF_RECONCILE" "$WF_CARRIER"; do
  base="$(basename "$wf")"
  if [ ! -f "$wf" ]; then
    bad "(a) $base 부재"
    continue
  fi
  # positive: active continue-on-error: true 부재여야 함 (검출기 exit 1)
  if detect_active_continue_on_error "$wf"; then
    bad "(a) $base 에 active continue-on-error: true 잔존" \
        "Stage 3 flip 위반 — continue-on-error 제거되어야 함"
  else
    ok "(a) $base = active continue-on-error: true 부재 (flip surfacing 활성)"
  fi

  # mutation fixture: active continue-on-error: true 재삽입 → 검출기 검출(exit 0) 해야 함.
  tmp=$(mktemp -d)
  mut="$tmp/mutated.yml"
  python3 - "$wf" "$mut" <<'PY'
import sys
with open(sys.argv[1], encoding="utf-8") as fh:
    txt = fh.read()
# steps 블록 안에 active 키 재삽입 (mutation — 회귀 재현)
txt += "\n        continue-on-error: true\n"
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    fh.write(txt)
PY
  if detect_active_continue_on_error "$mut"; then
    ok "(a) $base (mutation): continue-on-error: true 재삽입 → 검출기 RED (non-vacuous)"
  else
    bad "(a) $base (mutation): 재삽입했는데 검출기 통과" \
        "검출기가 continue-on-error 재삽입을 못 잡음 = vacuous (anti-theater 위반)"
  fi
  rm -rf "$tmp"
done

# ═══════════════════════════════════════════════════════════════════════════
# (b) registry 2 entry current_tier == blocking-on-pr (+ promoted_by CFP-2594)
# ═══════════════════════════════════════════════════════════════════════════
if [ ! -f "$REGISTRY" ]; then
  bad "(b) evidence-checks-registry.yaml 부재"
else
  for name in deferred-followup-reconcile deferral-carrier-declared; do
    rc=0; msg=$(registry_tier_check "$REGISTRY" "$name" 2>&1) || rc=$?
    if [ "$rc" -eq 3 ]; then
      echo "::warning::(b) $name SKIP — python yaml 모듈 부재 (CI 는 setup-python 으로 설치)"
    elif [ "$rc" -eq 0 ]; then
      ok "(b) $name = current_tier:blocking-on-pr + promoted_by:CFP-2594"
    else
      bad "(b) $name entry 부적합 ($msg)" "기대: current_tier:blocking-on-pr + promoted_by:CFP-2594"
    fi

    # mutation fixture: tier 를 warning 으로 되돌린 복사본 → 검출기 FAIL(1) 해야 함.
    tmp=$(mktemp -d)
    if python3 - "$REGISTRY" "$tmp/mut.yaml" "$name" <<'PY'
import sys
try:
    import yaml
except ImportError:
    sys.exit(3)
with open(sys.argv[1], encoding="utf-8") as fh:
    data = yaml.safe_load(fh)
name = sys.argv[3]
mutated = False
for e in (data or {}).get("entries", []):
    if e.get("name") == name:
        e["current_tier"] = "warning"  # flip 회귀 mutation
        mutated = True
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    yaml.safe_dump(data, fh, allow_unicode=True)
sys.exit(0 if mutated else 4)
PY
    then
      rc2=0; registry_tier_check "$tmp/mut.yaml" "$name" >/dev/null 2>&1 || rc2=$?
      if [ "$rc2" -eq 1 ]; then
        ok "(b) $name (mutation): tier→warning 회귀 → 검출기 RED (non-vacuous)"
      else
        bad "(b) $name (mutation): tier→warning 인데 검출기 통과 (rc=$rc2)" "vacuous (anti-theater 위반)"
      fi
    else
      mrc=$?
      if [ "$mrc" -eq 3 ]; then
        echo "::warning::(b) $name mutation SKIP — yaml 모듈 부재"
      else
        echo "::warning::(b) $name mutation SKIP — entry 부재로 변조 불가"
      fi
    fi
    rm -rf "$tmp"
  done
fi

# ═══════════════════════════════════════════════════════════════════════════
# (c) author-verify step 의 exit $status forcing (D-5)
# ═══════════════════════════════════════════════════════════════════════════
if [ ! -f "$WF_RECONCILE" ]; then
  bad "(c) deferred-followup-reconcile.yml 부재"
else
  # positive: exit $status 존재
  if detect_exit_status_forcing "$WF_RECONCILE"; then
    ok "(c) deferred-followup-reconcile.yml = author-verify exit \$status forcing 존재 (D-5)"
  else
    bad "(c) deferred-followup-reconcile.yml 에 exit \$status 부재" \
        "D-5 위반 — author-verify step 이 exit 0(비차단)으로 회귀"
  fi

  # mutation fixture: exit $status → exit 0 회귀 복사본 → 검출기 FAIL(1) 해야 함.
  tmp=$(mktemp -d)
  mut="$tmp/mut.yml"
  python3 - "$WF_RECONCILE" "$mut" <<'PY'
import re, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    lines = fh.readlines()
out = []
for raw in lines:
    s = raw.lstrip()
    if not s.startswith("#") and re.match(r"exit\s+\$status\b", s):
        indent = raw[: len(raw) - len(raw.lstrip())]
        out.append(indent + "exit 0\n")  # 회귀 mutation
    else:
        out.append(raw)
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    fh.writelines(out)
PY
  if detect_exit_status_forcing "$mut"; then
    bad "(c) (mutation): exit \$status→exit 0 인데 검출기 통과" "vacuous (anti-theater 위반)"
  else
    ok "(c) (mutation): exit \$status→exit 0 회귀 → 검출기 RED (non-vacuous)"
  fi
  rm -rf "$tmp"
fi

# ─── 요약 ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (flip structural — (a) continue-on-error 부재 / (b) tier blocking-on-pr / (c) exit \$status)."
  exit 0
else
  echo "Some tests failed (Stage 3 flip 구조 invariant 위반)."
  exit 1
fi
