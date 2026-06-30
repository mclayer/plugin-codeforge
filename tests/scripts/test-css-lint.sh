#!/usr/bin/env bash
# tests/scripts/test-css-lint.sh
# CFP-2505 Phase 2 — Discriminating self-test for D1 구조적 CSS lint (ADR-136 §8 D1).
#
# css-lint.yml 의 discriminating test job 이 호출(InfraEngineerAgent 가
#   `if: github.repository == 'mclayer/plugin-codeforge'` job 에서 `bash tests/scripts/test-css-lint.sh`).
# 선례 = tests/scripts/test_check-responsibility-topology.sh (mktemp fixture-root + run helper 답습).
#
# 본 test 가 검증하는 ADR-136 invariant:
#  - 결정4-A (parser-level invariant): 미닫힌 brace = stylelint CssSyntaxError(rule 평가 *이전*
#    단계, rule 무관) → stylelint non-zero exit = CI fail. WEB-033 류 brace 결함의 1급 방어.
#    [source: stylelint.io/user-guide/errors/]
#  - 결정4-B (rule-level floor): config-standard 가 effective-config 에서 floor rule(block-no-empty 등)
#    active 인지.
#  - 결정4 floor 축소불가 (effective-config self-check): overlay 가 `rules:{X:null}` 로 floor rule 을
#    기술적 disable 하면 `stylelint --print-config` 가 검출(anti-hollow). [source: stylelint.io/user-guide/configure/]
#  - 결정3 graceful no-op: CSS 파일 0개 → 차단 아님(exit 0).
#
# ── anti-theater (비협상) ────────────────────────────────────────────────────
#  - 케이스1(미닫힌 brace) 과 케이스2(clean) 가 반드시 다른 결과(discriminating). 둘 다 PASS 면 hollow
#    → 본 test 가 FAIL. `|| true` masking 금지 — 실 npx stylelint 실행 결과로만 단정.
#  - parser-level 케이스는 minimal inline config(extends 없음)로 구동 — extends 미설치 시 BOTH 케이스가
#    config-load 에러(exit 78)로 동일 실패하는 hollow 함정 회피(검증됨: extends 미설치 → 양 케이스 exit78
#    = non-discriminating). parser-level CssSyntaxError 는 rule/extends 무관이라 minimal config 로 충분.
#
# ── stylelint pin (InfraEngineer css-lint.yml/.stylelintrc 와 cross-ref — 일치 확정) ──
#  STYLELINT_PIN / STYLELINT_CONFIG_STANDARD_PIN env 로 override. default = InfraEngineer 의
#  css-lint.yml(stylelint 17.13.0 / config-standard 40.0.0) + .stylelintrc.json(extends config-standard
#  40.0.0, peer stylelint ^17) 와 일치. css-lint.yml line 199 가 env 무설정으로 본 test 를 호출하므로
#  default 가 CI pin 과 정확히 같아야 함(불일치 시 다른 버전 회귀). 검증됨: 17.13.0 도 parser-level
#  CssSyntaxError(bad exit 2 / clean exit 0) + effective-config floor active 동일 동작.
#
# ── graceful skip (로컬 Windows / offline) ────────────────────────────────────
#  npx 부재 또는 stylelint install 실패(offline) 시 silent pass 위장 금지 → 명시 ::notice:: 로그 후
#  exit 0. CI(ubuntu)는 setup-node 후 실 실행 전제. skip 도 명시적 로그로 구분.
#
# Exit code:
#  0 = all discriminating cases pass (또는 명시적 graceful skip)
#  1 = any case fails (lint 동작 / discrimination 깨짐)

set -uo pipefail

STYLELINT_PIN="${STYLELINT_PIN:-17.13.0}"               # css-lint.yml / .stylelintrc.json 과 일치
STYLELINT_CONFIG_STANDARD_PIN="${STYLELINT_CONFIG_STANDARD_PIN:-40.0.0}"  # config-standard (peer stylelint ^17)

PASS=0
FAIL=0
SKIP=0

note() { echo "::notice::$*"; }

# ─────────────────────────────────────────────────────────────────────────────
# Precondition: npx 존재 확인. 부재 시 전체 graceful skip(명시 로그) + exit 0.
# ─────────────────────────────────────────────────────────────────────────────
if ! command -v npx >/dev/null 2>&1; then
  note "[test-css-lint] npx 미설치 — 로컬 graceful skip (CI ubuntu setup-node 후 실 실행 전제). NOT a silent pass."
  echo "SKIP: npx 부재 (0 discriminating case 실행). CI 에서 재검증 필요."
  exit 0
fi

# stylelint 설치 가능성 probe (offline 이면 install 실패 → graceful skip).
PROBE_DIR=$(mktemp -d)
if ! ( cd "$PROBE_DIR" && timeout 240 npx --yes "stylelint@${STYLELINT_PIN}" --version >/dev/null 2>&1 ); then
  rm -rf "$PROBE_DIR"
  note "[test-css-lint] stylelint@${STYLELINT_PIN} install 실패(offline 추정) — graceful skip. NOT a silent pass."
  echo "SKIP: stylelint install 불가 (0 discriminating case 실행). CI 에서 재검증 필요."
  exit 0
fi
rm -rf "$PROBE_DIR"
note "[test-css-lint] stylelint@${STYLELINT_PIN} 가용 — 실 실행 모드."

# ─────────────────────────────────────────────────────────────────────────────
# run_stylelint <fixture-dir> <css-glob> → echo exit code (stdout 으로 반환).
#   --no-install 강제 — fixture dir 의 node_modules 또는 npx cache 의 pinned 버전 사용.
# ─────────────────────────────────────────────────────────────────────────────
run_stylelint_exit() {
  local dir="$1" glob="$2" ec=0
  ( cd "$dir" && timeout 180 npx --yes "stylelint@${STYLELINT_PIN}" "$glob" >/dev/null 2>&1 ) || ec=$?
  echo "$ec"
}

assert_eq() {
  local name="$1" expected="$2" actual="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then
    echo "✓ PASS: $name (got $actual) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected $expected, got $actual"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

assert_nonzero() {
  local name="$1" actual="$2" desc="$3"
  if [ "$actual" != "0" ]; then
    echo "✓ PASS: $name (got non-zero exit $actual = 차단) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected non-zero (차단), got 0 (통과) — RED 보장 깨짐"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# 케이스1 — 미닫힌 brace .css → non-zero exit (parser-level CssSyntaxError, 차단)
#   minimal inline config(extends 없음) — parser-level invariant 는 rule/extends 무관(ADR-136 결정4-A).
# ═════════════════════════════════════════════════════════════════════════════
C1=$(mktemp -d)
cat > "$C1/.stylelintrc.json" <<'EOF'
{ "rules": { "block-no-empty": true } }
EOF
printf '.terminal-controls .tt-live {\n  color: red;\n' > "$C1/bad.css"  # 미닫힌 brace (WEB-033 재현)
EC1=$(run_stylelint_exit "$C1" "bad.css")
assert_nonzero "C1-unclosed-brace-blocks" "$EC1" "미닫힌 brace .css = CssSyntaxError → non-zero exit (CI 차단). WEB-033 1급 방어"
rm -rf "$C1"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스2 — clean .css → pass (exit 0)
#   동일 minimal config. C1 ↔ C2 결과 상이 = discriminating 증거(anti-theater).
# ═════════════════════════════════════════════════════════════════════════════
C2=$(mktemp -d)
cat > "$C2/.stylelintrc.json" <<'EOF'
{ "rules": { "block-no-empty": true } }
EOF
printf '.foo {\n  color: red;\n}\n' > "$C2/good.css"
EC2=$(run_stylelint_exit "$C2" "good.css")
assert_eq "C2-clean-passes" "0" "$EC2" "올바른 .css = stylelint exit 0 (통과)"
rm -rf "$C2"

# ── anti-theater discriminating 검증: C1 != C2 (둘 다 PASS 면 hollow) ──
if [ "$EC1" = "$EC2" ]; then
  echo "✗ FAIL: ANTI-THEATER — C1(brace, exit=$EC1) 과 C2(clean, exit=$EC2) 결과 동일 = non-discriminating hollow gate"
  FAIL=$((FAIL+1))
else
  echo "✓ PASS: ANTI-THEATER discriminating — C1(brace, exit=$EC1) ≠ C2(clean, exit=$EC2)"
  PASS=$((PASS+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# 케이스3 — CSS 0개 → graceful (차단 아님)
#   ADR-136 결정3: CSS 파일 부재 시 graceful no-op. stylelint 가 매칭 0 시 동작(no-files-found 처리).
#   css-lint.yml 의 job-level if: hashFiles(...) 또는 in-job exit 0 이 graceful 보장 — 본 test 는
#   stylelint 가 매칭 0 케이스를 "차단(non-zero with hard-fail)" 으로 오판하지 않음을 확인.
#   stylelint v16 default: 매칭 파일 0 → exit 0 (--allow-empty-input 불요. 단 버전별 상이 가능 →
#   --allow-empty-input 명시로 graceful 보장 — css-lint.yml in-job fast-exit 와 동형).
# ═════════════════════════════════════════════════════════════════════════════
C3=$(mktemp -d)
cat > "$C3/.stylelintrc.json" <<'EOF'
{ "rules": { "block-no-empty": true } }
EOF
# CSS 파일 0개 — 다른 파일만 존재
echo "no css here" > "$C3/README.md"
EC3=0
( cd "$C3" && timeout 180 npx --yes "stylelint@${STYLELINT_PIN}" --allow-empty-input "**/*.css" "**/*.scss" >/dev/null 2>&1 ) || EC3=$?
assert_eq "C3-no-css-graceful" "0" "$EC3" "CSS 0개 + --allow-empty-input = graceful exit 0 (차단 아님 — ADR-136 결정3)"
rm -rf "$C3"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스4 — effective-config floor 축소불가 self-check (ADR-136 결정4 floor 축소불가)
#   preset(config-standard extends) 설치 필요. overlay 가 floor rule(block-no-empty)을
#   `null` 로 disable → `stylelint --print-config` 가 검출(active=False). default 는 active=True.
#   C4a(default, floor active) ↔ C4b(null override, floor disabled) discriminating.
#   InfraEngineer css-lint.yml 의 self-check step 과 매핑.
# ═════════════════════════════════════════════════════════════════════════════
C4=$(mktemp -d); cd "$C4"
cat > package.json <<EOF
{ "name":"cfp2505-fixture","version":"1.0.0","devDependencies":{"stylelint":"${STYLELINT_PIN}","stylelint-config-standard":"${STYLELINT_CONFIG_STANDARD_PIN}"} }
EOF
PRESET_OK=1
if ! timeout 300 npm install --no-audit --no-fund >/dev/null 2>&1; then
  PRESET_OK=0
fi

floor_active() {
  # $1 = config json file. echo "true"/"false" — block-no-empty 가 effective-config 에 active 한가.
  local cfg="$1"
  ( cd "$C4" && cp "$cfg" .stylelintrc.json && printf '.x{color:red}\n' > probe.css && \
    timeout 120 npx --no-install stylelint --print-config probe.css 2>/dev/null ) | python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    print("ERR"); sys.exit(0)
v=d.get("rules",{}).get("block-no-empty","ABSENT")
active = v not in ("ABSENT", None, False) and not (isinstance(v,list) and (len(v)==0 or v[0] in (None,False)))
print("true" if active else "false")
'
}

if [ "$PRESET_OK" -eq 1 ]; then
  cat > "$C4/cfg-default.json" <<EOF
{ "extends": "stylelint-config-standard" }
EOF
  cat > "$C4/cfg-null.json" <<EOF
{ "extends": "stylelint-config-standard", "rules": { "block-no-empty": null } }
EOF
  FA_DEFAULT=$(floor_active "$C4/cfg-default.json")
  FA_NULL=$(floor_active "$C4/cfg-null.json")
  assert_eq "C4a-floor-active-default" "true" "$FA_DEFAULT" "config-standard default = floor rule(block-no-empty) effective-config active"
  assert_eq "C4b-floor-disabled-detected" "false" "$FA_NULL" "overlay rules:{block-no-empty:null} = floor disabled 검출(self-check 차단 신호) — ADR-136 결정4 floor 축소불가"
  if [ "$FA_DEFAULT" = "$FA_NULL" ]; then
    echo "✗ FAIL: ANTI-THEATER (C4) — default($FA_DEFAULT) == null-override($FA_NULL) = effective-config self-check non-discriminating"
    FAIL=$((FAIL+1))
  else
    echo "✓ PASS: ANTI-THEATER discriminating (C4) — default floor=$FA_DEFAULT ≠ null-override floor=$FA_NULL"
    PASS=$((PASS+1))
  fi
else
  note "[test-css-lint] stylelint-config-standard install 실패 — C4 effective-config self-check graceful skip. NOT a silent pass."
  echo "SKIP: C4 preset install 불가 (effective-config self-check 미실행). CI 에서 재검증 필요."
  SKIP=$((SKIP+1))
fi
cd /; rm -rf "$C4"

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2505 D1 css-lint)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
echo "TOTAL ASSERT: $((PASS + FAIL))"
echo "stylelint pin: ${STYLELINT_PIN} / config-standard pin: ${STYLELINT_CONFIG_STANDARD_PIN}"
echo ""
echo "Discriminating evidence (anti-theater):"
echo "  C1 미닫힌 brace exit=$EC1 (non-zero=차단) ≠ C2 clean exit=$EC2 (0=통과)"
echo "  C4 effective-config: default floor=${FA_DEFAULT:-SKIP} ≠ null-override floor=${FA_NULL:-SKIP}"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
