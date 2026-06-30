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

# ═════════════════════════════════════════════════════════════════════════════
# 케이스5 — consumer-형상 --config-basedir discriminating (CFP-2527 §8.1)
#   배포 형상 재현: config 파일은 repo root(=$ROOT), stylelint toolchain 은 격리 dir
#   ($TC/node_modules)에 설치. config 의 `extends: stylelint-config-standard` 를
#   resolve 하려면 stylelint 이 격리 toolchain 의 node_modules 를 basedir 로 알아야 한다.
#   --config-basedir 없으면 config(repo root) 기준 basedir 로 extends resolve 실패
#   → ConfigurationError("Could not find stylelint-config-standard"). fix =
#   --config-basedir "$TC/node_modules" 부착. 본 케이스가 fix 의 discriminating 봉인.
#
#   3-위치 mktemp 분리(검증 형상 = 배포 형상 재현):
#     TC   = toolchain dir (격리 설치, $TC/node_modules)
#     ROOT = config + CSS dir (config=repo root 형상 재현, invoke cwd)
#     bin  = $TC/node_modules/.bin/stylelint (격리 bin 직접 호출 — npx 우회, 정확 pin·cwd 비의존)
#
#   3-case:
#     (i)   GREEN: --config + --config-basedir → print-config / lint 둘 다 exit 0 (AC-1)
#     (ii)  RED:   --config-basedir 제거 → ConfigurationError RED (AC-3)
#     (iii) half-fix 양갈래 RED: self-check 만 basedir → lint RED / lint 만 basedir → print-config RED (AC-4 / R-3)
#
#   RED 판정식 = (exit != 0) AND (stderr =~ /ConfigurationError|Could not find/).
#   exit 78 값 hard-pin 금지(stylelint 버전 robust + over-loose 차단) — 주석 관측 기록으로만
#   (관측: stylelint config-load 실패 = exit 78).
# ═════════════════════════════════════════════════════════════════════════════

# RED 판정 helper (stderr 캡처 필요 — run_stylelint_exit 는 stderr 버리므로 inline).
#   cwd = $ROOT 에서 격리 bin 직접 호출. exit != 0 AND stderr 에 ConfigurationError/Could not find 시 RED.
assert_config_red() {
  local name="$1" desc="$2"; shift 2
  local out ec=0
  out=$( ( cd "$ROOT" && timeout 180 "$TC/node_modules/.bin/stylelint" "$@" ) 2>&1 ) || ec=$?
  if [ "$ec" != "0" ] && echo "$out" | grep -Eq 'ConfigurationError|Could not find'; then
    echo "✓ PASS: $name (exit=$ec, stderr=ConfigurationError/Could not find 매칭 = RED 봉인) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name — RED 판정 불성립 (exit=$ec, stderr 매칭 실패). 출력: $out"
    FAIL=$((FAIL+1)); return 1
  fi
}

# toolchain dir — 격리 설치 ($TC/node_modules).
TC=$(mktemp -d); cd "$TC"
cat > package.json <<EOF
{"name":"cfp2527-c5-toolchain","version":"1.0.0","devDependencies":{"stylelint":"${STYLELINT_PIN}","stylelint-config-standard":"${STYLELINT_CONFIG_STANDARD_PIN}"}}
EOF
TC_OK=1
if ! ( cd "$TC" && timeout 300 npm install --no-audit --no-fund >/dev/null 2>&1 ); then TC_OK=0; fi

# config + CSS dir — config=repo root 형상 재현(toolchain 과 분리).
ROOT=$(mktemp -d)
cat > "$ROOT/.stylelintrc.json" <<'EOF'
{"extends":"stylelint-config-standard"}
EOF
printf '.foo{color:red}\n' > "$ROOT/clean.css"   # clean CSS (lint pass 대상)

# 초기화 (SKIP 시 Summary echo 가 참조).
C5_GREEN_PC="SKIP"; C5_GREEN_LINT="SKIP"

if [ "$TC_OK" -eq 0 ]; then
  note "[test-css-lint] C5 toolchain install 실패 — graceful skip. NOT a silent pass."
  echo "SKIP: C5 consumer-형상 fixture 미실행 (toolchain install 불가). CI 에서 재검증 필요."
  SKIP=$((SKIP+1))
else
  STYLELINT_BIN="$TC/node_modules/.bin/stylelint"

  # ── (i) GREEN: --config + --config-basedir → print-config / lint 둘 다 exit 0 (AC-1) ──
  C5_GREEN_PC=0
  ( cd "$ROOT" && timeout 180 "$STYLELINT_BIN" --config "$ROOT/.stylelintrc.json" --config-basedir "$TC/node_modules" --print-config "$ROOT/clean.css" >/dev/null 2>&1 ) || C5_GREEN_PC=$?
  assert_eq "C5-i-a-green-print-config" "0" "$C5_GREEN_PC" "basedir 부착 → --print-config exit 0 (extends resolve 성공, AC-1)"

  C5_GREEN_LINT=0
  ( cd "$ROOT" && timeout 180 "$STYLELINT_BIN" --config "$ROOT/.stylelintrc.json" --config-basedir "$TC/node_modules" "$ROOT/clean.css" >/dev/null 2>&1 ) || C5_GREEN_LINT=$?
  assert_eq "C5-i-b-green-lint" "0" "$C5_GREEN_LINT" "basedir 부착 → clean.css lint exit 0 (extends resolve 성공 + clean pass, AC-1)"

  # ── (ii) RED: --config-basedir 제거 → ConfigurationError RED (AC-3) ──
  assert_config_red "C5-ii-a-red-no-basedir-print-config" \
    "basedir 제거(--config 만) → --print-config 가 extends resolve 실패 ConfigurationError (AC-3)" \
    --config "$ROOT/.stylelintrc.json" --print-config "$ROOT/clean.css"
  assert_config_red "C5-ii-b-red-no-basedir-lint" \
    "basedir 제거(--config 만) → lint 가 extends resolve 실패 ConfigurationError (AC-3)" \
    --config "$ROOT/.stylelintrc.json" "$ROOT/clean.css"

  # ── (iii) half-fix 양갈래 RED (AC-4 / R-3) ──
  #  (iii-a) self-check(--print-config) 에만 basedir, lint 엔 미부착 → lint 호출이 RED.
  C5_HALFA_PC=0
  ( cd "$ROOT" && timeout 180 "$STYLELINT_BIN" --config "$ROOT/.stylelintrc.json" --config-basedir "$TC/node_modules" --print-config "$ROOT/clean.css" >/dev/null 2>&1 ) || C5_HALFA_PC=$?
  assert_eq "C5-iii-a-selfcheck-green" "0" "$C5_HALFA_PC" "half-fix(iii-a): self-check 에만 basedir → print-config 자체는 exit 0 (lint 가 RED 여야 함)"
  assert_config_red "C5-iii-a-red-lint-no-basedir" \
    "half-fix(iii-a): self-check 만 basedir 부착, lint 엔 미부착 → lint 호출이 ConfigurationError RED (AC-4 / R-3)" \
    --config "$ROOT/.stylelintrc.json" "$ROOT/clean.css"

  #  (iii-b) lint 에만 basedir, self-check(--print-config) 엔 미부착 → print-config 호출이 RED.
  C5_HALFB_LINT=0
  ( cd "$ROOT" && timeout 180 "$STYLELINT_BIN" --config "$ROOT/.stylelintrc.json" --config-basedir "$TC/node_modules" "$ROOT/clean.css" >/dev/null 2>&1 ) || C5_HALFB_LINT=$?
  assert_eq "C5-iii-b-lint-green" "0" "$C5_HALFB_LINT" "half-fix(iii-b): lint 에만 basedir → lint 자체는 exit 0 (print-config 가 RED 여야 함)"
  assert_config_red "C5-iii-b-red-print-config-no-basedir" \
    "half-fix(iii-b): lint 만 basedir 부착, self-check 엔 미부착 → --print-config 호출이 ConfigurationError RED (AC-4 / R-3)" \
    --config "$ROOT/.stylelintrc.json" --print-config "$ROOT/clean.css"

  # ── anti-theater discriminating: (i) GREEN exit 0 ≠ (ii) RED exit (둘이 같으면 hollow) ──
  C5_RED_EC=0
  ( cd "$ROOT" && timeout 180 "$STYLELINT_BIN" --config "$ROOT/.stylelintrc.json" --print-config "$ROOT/clean.css" >/dev/null 2>&1 ) || C5_RED_EC=$?
  if [ "$C5_GREEN_PC" = "$C5_RED_EC" ]; then
    echo "✗ FAIL: ANTI-THEATER (C5) — GREEN print-config exit($C5_GREEN_PC) == RED no-basedir exit($C5_RED_EC) = non-discriminating hollow"
    FAIL=$((FAIL+1))
  else
    echo "✓ PASS: ANTI-THEATER discriminating (C5) — GREEN(basedir) exit=$C5_GREEN_PC ≠ RED(no-basedir) exit=$C5_RED_EC (관측: RED config-load 실패 = exit 78)"
    PASS=$((PASS+1))
  fi
fi
cd /; rm -rf "$TC" "$ROOT"

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
echo "  C5 consumer-형상: GREEN(basedir 부착) print-config=exit${C5_GREEN_PC:-SKIP}/lint=exit${C5_GREEN_LINT:-SKIP} ≠ RED(basedir 제거)=ConfigurationError(관측 exit 78)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
