#!/usr/bin/env bash
# tests/scripts/test_check-venue-shape-fidelity-presence.sh
# CFP-2504 Phase 2 / ADR-006 Amendment 1 — Discriminating self-test for
#   scripts/lib/check_venue_shape_fidelity_presence.py (venue 형상 재현 anchor-presence lint).
#
# 배경: venue 형상 재현 fidelity anchor-presence lint 가 hollow(always-PASS) 가 아님을 보증.
#   discriminating fixture = 임시 디렉터리에 project.yaml + docs/stories/*.md 를 실제로 구성하고,
#   py SSOT 가 (1) venue.applicable gating 과 (2) shape/N/A anchor 유무를 *동작으로* 구분하는지
#   exit code 로 assert.
#
# self-contained bash (bats 미사용 — test_check-force-push-base-advance.sh / test_check-responsibility-
#   topology.sh 답습). 각 케이스마다 mktemp -d 로 격리 project tree 를 만들고 --config/--stories-dir 로 호출.
#
# Discriminating 의무 (CFP-1334): 단순 "exit 0 = PASS" 는 non-discriminating → 금지.
#   ★ 핵심 discriminating 대조 (mutation 생존 0 보증):
#     - T-1 (anchor 부재 + venue.applicable:true) = exit 1 (위반 검출)  vs
#     - T-2 (shape anchor 존재) / T-3 (N/A anchor 존재) = exit 0 (clean)
#     - T-4 (venue.applicable:false, anchor 부재여도) = exit 0 (gating no-op)
#   anchor 검출 로직을 always-PASS 로 mutate 하면 T-1 이 FAIL(exit 0, 기대 1) → mutant kill.
#   gating 로직을 always-active 로 mutate 하면 T-4 가 FAIL(exit 1, 기대 0) → mutant kill.
#
# Mutation-RED 입증 (CFP-1334):
#   (수동 mutation-RED A — anchor 검출 무력화: check_venue_shape_fidelity_presence.py 의
#     run() 안 `violations.append(rel)` 줄을 `pass` 로 임시 변경 → T-1 FAIL(exit 0, 기대 1) = RED.)
#   (수동 mutation-RED B — gating 무력화: _venue_applicable() 의 `return bool(...)` 을
#     `return True, None` 로 임시 변경 → T-4 FAIL(exit 1, 기대 0) = RED.)
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates gating + shape/N/A anchor detect)
#  1 = any fixture fails (detect 가 hollow 또는 회귀)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-venue-shape-fidelity-presence.sh"
PY="$REPO_ROOT/scripts/lib/check_venue_shape_fidelity_presence.py"

PASS=0
FAIL=0

# python3 / PyYAML 미설치 = setup-error (CI 는 setup-python + pip install pyyaml 보장).
if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ FAIL: python3 미설치 — 본 discriminating test 실행 불가 (setup-error)"
  exit 1
fi
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "✗ FAIL: PyYAML 미설치 — 본 discriminating test 실행 불가 (setup-error; pip install pyyaml)"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# mk_project <applicable_bool> — 격리 project tree 생성, 루트 경로 echo.
#   .claude/_overlay/project.yaml (venue.applicable=<bool>) + docs/stories/ 빈 디렉터리.
# ─────────────────────────────────────────────────────────────────────────────
mk_project() {
  local applicable="$1"
  local root
  root="$(mktemp -d)"
  mkdir -p "$root/.claude/_overlay" "$root/docs/stories"
  cat > "$root/.claude/_overlay/project.yaml" <<EOF
project:
  name: test-venue-consumer
venue:
  applicable: ${applicable}
EOF
  echo "$root"
}

# add_story <root> <name> <s8_body> — docs/stories/<name> 작성 (frontmatter + §8 본문 주입).
add_story() {
  local root="$1" name="$2" s8body="$3"
  cat > "$root/docs/stories/$name" <<EOF
---
key: CFP-TEST
type: story
---

## §1. 목적

테스트 story.

## §8. Test Contract

${s8body}

## §9. 다음

끝.
EOF
}

# run_case <name> <root> <expected_exit> <description>
run_case() {
  local name="$1" root="$2" expected_exit="$3" description="$4"
  local out ec=0
  out=$( cd "$root" && python3 "$PY" 2>&1 ) || ec=$?
  if [ "$ec" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $ec) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name — expected exit $expected_exit, got $ec"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# T-1 (anchor 부재 VIOLATION): venue.applicable:true + §8 에 형상 anchor/N/A 둘 다 부재 → exit 1.
#   합성-only 서술만 있는 §8 (균일 +1 seq 언급하나 captured-golden/실형상/N/A anchor 없음).
# ═════════════════════════════════════════════════════════════════════════════
R1="$(mk_project true)"
add_story "$R1" "cfp-violation.md" "단위 테스트로 +1 seq 합성 fixture 를 사용해 ordering 을 검증한다. 커버리지 90%."
run_case "T-1-anchor-absent" "$R1" 1 \
  "venue.applicable:true + §8 형상 anchor/N/A 둘 다 부재 → 위반 검출 (exit 1)"

# ═════════════════════════════════════════════════════════════════════════════
# T-2 (shape-declaration anchor GREEN): §8 에 captured-golden 선언 존재 → exit 0.
# ═════════════════════════════════════════════════════════════════════════════
R2="$(mk_project true)"
add_story "$R2" "cfp-shape.md" "실 venue tap 으로 captured-golden fixture 를 녹화해 형상 재현을 보장한다 (μs-as-seq snapshot 형상)."
run_case "T-2-shape-anchor" "$R2" 0 \
  "venue.applicable:true + captured-golden/형상 재현 anchor 존재 → clean GREEN (exit 0)"

# ═════════════════════════════════════════════════════════════════════════════
# T-3 (N/A anchor GREEN): §8 에 venue 미접촉 N/A 사유 존재 → exit 0.
# ═════════════════════════════════════════════════════════════════════════════
R3="$(mk_project true)"
add_story "$R3" "cfp-na.md" "N/A — 외부 venue 미접촉 (메모리-only 결정론 변환, 외부 stream 미의존). venue 미접촉."
run_case "T-3-na-anchor" "$R3" 0 \
  "venue.applicable:true + N/A(venue 미접촉) anchor 존재 → clean GREEN (exit 0)"

# ═════════════════════════════════════════════════════════════════════════════
# T-4 (gating no-op GREEN): venue.applicable:false → anchor 부재여도 검사 비대상 (exit 0).
#   ★ T-1 과 동일한 anchor-부재 §8 인데 flag 만 false — gating 이 hollow 아님을 대조 입증.
# ═════════════════════════════════════════════════════════════════════════════
R4="$(mk_project false)"
add_story "$R4" "cfp-violation.md" "단위 테스트로 +1 seq 합성 fixture 를 사용해 ordering 을 검증한다. 커버리지 90%."
run_case "T-4-gating-noop" "$R4" 0 \
  "venue.applicable:false → anchor 부재여도 no-op PASS (gating, exit 0) — T-1 과 flag 만 다름"

# ═════════════════════════════════════════════════════════════════════════════
# T-1↔T-4 discriminating 대조: 동일 §8(anchor 부재)이 flag=true 면 exit1, flag=false 면 exit0.
#   무차별이면 gating hollow. 두 동작 차이가 함께여야 PASS.
# ═════════════════════════════════════════════════════════════════════════════
ec_on=0;  ( cd "$R1" && python3 "$PY" >/dev/null 2>&1 ) || ec_on=$?
ec_off=0; ( cd "$R4" && python3 "$PY" >/dev/null 2>&1 ) || ec_off=$?
if [ "$ec_on" -eq 1 ] && [ "$ec_off" -eq 0 ]; then
  echo "✓ PASS: T-gating-discriminating — applicable:true=exit1 ∧ applicable:false=exit0 (gating hollow 아님)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-gating-discriminating — gating 무차별 (true=$ec_on false=$ec_off, 기대 1/0) = hollow"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# T-5 (§8 본문 부재 = data-absence honest skip): venue.applicable:true 이나 §8 헤딩 부재 story.
#   §8 구조 결손은 story-section-schema.yml 관할 (중복 차단) — 본 lint 는 §8 본문 존재 시만 anchor 검사.
#   해당 story 는 skip, 위반 0 → exit 0.
# ═════════════════════════════════════════════════════════════════════════════
R5="$(mk_project true)"
cat > "$R5/docs/stories/cfp-no-s8.md" <<'EOF'
---
key: CFP-TEST
type: story
---

## §1. 목적

§8 헤딩이 없는 story.

## §9. 다음

끝.
EOF
run_case "T-5-no-s8-skip" "$R5" 0 \
  "venue.applicable:true + §8 헤딩 부재 → data-absence honest skip (story-section-schema 관할, exit 0)"

# ═════════════════════════════════════════════════════════════════════════════
# T-6 (venue 섹션 미주입 = default-false no-op): project.yaml 에 venue 섹션 자체 부재 → exit 0.
#   안전 방향 default false (ADR-136 frontend.applicable 동형) — anchor 부재여도 비대상.
# ═════════════════════════════════════════════════════════════════════════════
R6="$(mktemp -d)"
mkdir -p "$R6/.claude/_overlay" "$R6/docs/stories"
cat > "$R6/.claude/_overlay/project.yaml" <<'EOF'
project:
  name: no-venue-section
EOF
add_story "$R6" "cfp-violation.md" "합성 fixture 만 사용. anchor 없음."
run_case "T-6-venue-section-absent" "$R6" 0 \
  "venue 섹션 미주입 → default-false no-op PASS (ADR-136 동형, exit 0)"

# ═════════════════════════════════════════════════════════════════════════════
# T-7 (config 부재 = data-absence fail-open): project.yaml 자체 부재 (wrapper self / pre-init).
# ═════════════════════════════════════════════════════════════════════════════
R7="$(mktemp -d)"
mkdir -p "$R7/docs/stories"
add_story "$R7" "cfp-violation.md" "anchor 없음."
run_case "T-7-config-absent" "$R7" 0 \
  "project.yaml 부재 → data-absence fail-open (wrapper self / pre-init, exit 0)"

# ═════════════════════════════════════════════════════════════════════════════
# T-8 (setup-error fail-closed): project.yaml YAML parse 실패 → exit 2.
# ═════════════════════════════════════════════════════════════════════════════
R8="$(mktemp -d)"
mkdir -p "$R8/.claude/_overlay" "$R8/docs/stories"
printf 'project:\n  name: broken\nvenue:\n  applicable: true\n  bad: [unterminated\n' > "$R8/.claude/_overlay/project.yaml"
run_case "T-8-setup-error" "$R8" 2 \
  "project.yaml YAML parse 실패 → setup-error fail-closed (exit 2)"

# ═════════════════════════════════════════════════════════════════════════════
# T-9 (thin wrapper passthrough): bash thin wrapper 가 py exit code 를 그대로 전달하는지.
# ═════════════════════════════════════════════════════════════════════════════
ec=0; ( cd "$R1" && bash "$SCRIPT" >/dev/null 2>&1 ) || ec=$?
if [ "$ec" -eq 1 ]; then
  echo "✓ PASS: T-9-wrapper (exit 1) — thin wrapper(ADR-061) exit code passthrough"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-9-wrapper — expected exit 1 passthrough, got $ec"
  FAIL=$((FAIL+1))
fi

# cleanup
rm -rf "$R1" "$R2" "$R3" "$R4" "$R5" "$R6" "$R7" "$R8"

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2504 Phase 2 venue 형상 재현 anchor-presence lint)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (CFP-1334 — hollow 검사 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation A (anchor 검출 무력화: run() 의 violations.append(rel) → pass)"
  echo "  → T-1-anchor-absent FAIL (exit 0, 기대 1) = RED"
  echo "  → T-gating-discriminating FAIL (true 도 exit 0 = 무차별) = RED"
  echo "  → T-2/T-3/T-4 GREEN 유지 = 케이스 분리 (hollow 아님 증명)"
  echo "Mutation B (gating 무력화: _venue_applicable() → return True, None)"
  echo "  → T-4-gating-noop FAIL (exit 1, 기대 0) = RED"
  echo "  → T-6/T-7 FAIL (false/부재인데 검사 active) = RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
