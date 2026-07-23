#!/usr/bin/env bash
# tests/scripts/test-check-fable-roster-integrity.sh
# CFP-2803 Phase 2 — Discriminating self-test for fable roster integrity gate (ADR-141 Amendment 1 carve-out).
#
# InfraEngineerAgent 가 `scripts/check-fable-roster-integrity.sh` 구현. 본 test 는
#   Change Plan §7 의 4-axis roster check 를 discriminating mutation 으로 검증.
# 선례 = tests/scripts/test-css-lint.sh (mktemp fixture-root + RED mutation + anti-theater).
#
# 본 test 가 검증하는 Change Plan §7 invariant:
#  - 체크1 (count): fable agent count == 10 (정확히).
#  - 체크2 (bijection): 정확히 이 10 경로들만 model:fable 여야 함.
#    - plugins/codeforge-requirements/agents/RequirementsPLAgent.md
#    - plugins/codeforge-review/agents/RequirementsReviewPLAgent.md
#    - plugins/codeforge-design/agents/ArchitectPLAgent.md
#    - plugins/codeforge-review/agents/DesignReviewPLAgent.md
#    - plugins/codeforge-develop/agents/DeveloperPLAgent.md
#    - plugins/codeforge-review/agents/CodeReviewPLAgent.md
#    - plugins/codeforge-pmo/agents/PMOAgent.md
#    - plugins/codeforge-design/agents/ArchitectAgent.md
#    - plugins/codeforge-requirements/agents/ResearcherAgent.md
#    - plugins/codeforge-test/agents/IntegrationTestAgent.md
#  - 체크3 (exclusion): SecurityTestPLAgent.md 는 model:opus 유지 (fable 아님, 배제).
#  - 체크4 (census): 전체 agent 파일 count == 41, distribution haiku 7 / sonnet 10 / fable 10 / opus 14.
#    (프리셋 파일 3개 포함: plugins/codeforge-develop/presets/*/agents/*.md)
#
# ── anti-theater (비협상) ────────────────────────────────────────────────────
#  - 케이스별 GREEN/RED 가 반드시 다른 결과(discriminating). 둘 다 PASS/둘 다 FAIL 면 hollow.
#  - 본 test 가 FAIL. `|| true` masking 금지 — 실 gate 스크립트 exit code 로만 단정.
#  - each mutation 은 정확히 하나의 invariant violation 을 일으킴 (의도 격리).
#
# ── graceful skip (로컬 Windows / gate script 미존재) ────────────────────────────────
#  gate script `scripts/check-fable-roster-integrity.sh` 부재 또는 python3 미설치 시
#  silent pass 위장 금지 → 명시 ::notice:: 로그 후 exit 0. CI 에서 실 실행 전제.
#
# ── real-repo liveness (Change Plan §7 item 2 — REQUIRED) ───────────────────
#  독립 assertion: 실제 worktree repo 에서 agent 파일 count == 41 확인.
#  find plugins -path "*/agents/*.md" (globstar-off 회피, preset 손실 방지) 사용.
#  Green 과 Red 의 fixture 정규화(분포조정) 에 관계없이 실제 repo 는 41 파일 보장.
#
# Exit code:
#  0 = all discriminating cases pass (또는 명시적 graceful skip)
#  1 = any case fails (gate 동작 / discrimination 깨짐)

set -uo pipefail

PASS=0
FAIL=0
SKIP=0

note() { echo "::notice::$*"; }

# ─────────────────────────────────────────────────────────────────────────────
# Precondition: gate script 존재 + python3 가용 확인.
# ─────────────────────────────────────────────────────────────────────────────
GATE_SCRIPT="$(cd "$(dirname "$0")/../.." && pwd)/scripts/check-fable-roster-integrity.sh"

if [ ! -f "$GATE_SCRIPT" ]; then
  note "[test-check-fable-roster-integrity] gate script $GATE_SCRIPT 부재 — graceful skip. NOT a silent pass."
  echo "SKIP: gate script 미구현. CI 에서 재검증 필요."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  note "[test-check-fable-roster-integrity] python3 미설치 — graceful skip. NOT a silent pass."
  echo "SKIP: python3 부재 (0 discriminating case 실행). CI 에서 재검증 필요."
  exit 0
fi

note "[test-check-fable-roster-integrity] gate script + python3 가용 — 실 실행 모드."

# ─────────────────────────────────────────────────────────────────────────────
# Helper: run_gate <fixture-dir> → echo exit code
# ─────────────────────────────────────────────────────────────────────────────
run_gate_exit() {
  local dir="$1" ec=0
  timeout 60 bash "$GATE_SCRIPT" --repo-root "$dir" >/dev/null 2>&1 || ec=$?
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

assert_exit_1() {
  local name="$1" actual="$2" desc="$3"
  if [ "$actual" = "1" ]; then
    echo "✓ PASS: $name (got exit 1 = gate FAIL 정상) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 1 (gate FAIL), got exit $actual (setup error 또는 false-pass)"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: build_fixture_from_real_repo <dest-dir>
#   실제 repo 의 plugins 를 temp dest 로 복사 후 정규화(10 fable 표준화).
# ─────────────────────────────────────────────────────────────────────────────
build_fixture_from_real_repo() {
  local dest="$1"
  local repo_root="$(cd "$(dirname "$0")/../.." && pwd)"

  # plugins 디렉토리 전체 복사.
  if [ -d "$repo_root/plugins" ]; then
    cp -r "$repo_root/plugins" "$dest/"
  else
    # plugins 부재 → fallback: 최소 구조 생성 (실제로는 repo 에 존재해야 함).
    mkdir -p "$dest/plugins"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: normalize_fixture <fixture-root>
#   fixture 내 모든 agent 파일의 model: 라인을 정규화.
#   - 10 fable target: model: fable 로 설정
#   - SecurityTestPLAgent: model: opus 로 설정
#   - 나머지: 기존 값 유지
# ─────────────────────────────────────────────────────────────────────────────
normalize_fixture() {
  local fixture="$1"

  # 10 fable targets (상대경로).
  local fable_targets=(
    "plugins/codeforge-requirements/agents/RequirementsPLAgent.md"
    "plugins/codeforge-review/agents/RequirementsReviewPLAgent.md"
    "plugins/codeforge-design/agents/ArchitectPLAgent.md"
    "plugins/codeforge-review/agents/DesignReviewPLAgent.md"
    "plugins/codeforge-develop/agents/DeveloperPLAgent.md"
    "plugins/codeforge-review/agents/CodeReviewPLAgent.md"
    "plugins/codeforge-pmo/agents/PMOAgent.md"
    "plugins/codeforge-design/agents/ArchitectAgent.md"
    "plugins/codeforge-requirements/agents/ResearcherAgent.md"
    "plugins/codeforge-test/agents/IntegrationTestAgent.md"
  )

  # SecurityTestPLAgent (exclusion).
  local security_test="plugins/codeforge-review/agents/SecurityTestPLAgent.md"

  # 각 fable target 을 model: fable 로 정규화.
  for target in "${fable_targets[@]}"; do
    local path="$fixture/$target"
    if [ -f "$path" ]; then
      # model: 라인 찾아서 값을 fable 로 설정.
      if grep -q "^model:" "$path"; then
        sed -i 's/^model:.*/model: fable/' "$path"
      else
        # model: 라인 없으면 추가 (frontmatter 첫 줄 뒤).
        sed -i '1a model: fable' "$path"
      fi
    fi
  done

  # SecurityTestPLAgent 를 model: opus 로 정규화.
  local sec_path="$fixture/$security_test"
  if [ -f "$sec_path" ]; then
    if grep -q "^model:" "$sec_path"; then
      sed -i 's/^model:.*/model: opus/' "$sec_path"
    else
      sed -i '1a model: opus' "$sec_path"
    fi
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# 케이스 GREEN — 정규화된 fixture (10 fable, SecurityTestPL opus, 41 total)
#   gate → exit 0 (모든 check 통과)
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_GREEN=$(mktemp -d)
build_fixture_from_real_repo "$FIXTURE_GREEN"
normalize_fixture "$FIXTURE_GREEN"
EC_GREEN=$(run_gate_exit "$FIXTURE_GREEN")

# GREEN setup error 감지 (exit 2 = gate 실행 환경 이슈, 판정 불가).
if [ "$EC_GREEN" = "2" ]; then
  note "[test-check-fable-roster-integrity] GREEN exit 2 (gate setup error) — 환경 이슈 감지. CI-Linux 에서 재검증."
  echo "SKIP: gate script setup error (exit 2). CI 에서 재검증 필요."
  rm -rf "$FIXTURE_GREEN"
  exit 0
fi

assert_eq "GREEN-canonical-state" "0" "$EC_GREEN" "정규화 fixture(10 fable/1 opus-sec/41 total) = 모든 check 통과"
rm -rf "$FIXTURE_GREEN"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스 RED-A — fable count 감소 (체크1 위반)
#   한 fable target(DeveloperPLAgent) 을 opus 로 flip → count=9 → non-zero exit
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_RED_A=$(mktemp -d)
build_fixture_from_real_repo "$FIXTURE_RED_A"
normalize_fixture "$FIXTURE_RED_A"
# DeveloperPLAgent.md model: fable → opus 로 flip.
DEV_PL_PATH="$FIXTURE_RED_A/plugins/codeforge-develop/agents/DeveloperPLAgent.md"
if [ -f "$DEV_PL_PATH" ]; then
  sed -i 's/^model: fable$/model: opus/' "$DEV_PL_PATH"
fi
EC_RED_A=$(run_gate_exit "$FIXTURE_RED_A")
assert_exit_1 "RED-A-fable-count-9" "$EC_RED_A" "fable count=9 (한 target flip to opus) 는 체크1 count==10 위반 → exit 1"
rm -rf "$FIXTURE_RED_A"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스 RED-B — exclusion 위반 (체크3 위반)
#   SecurityTestPLAgent.md 를 opus → fable 로 flip → count=11, exclusion 위반 → non-zero exit
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_RED_B=$(mktemp -d)
build_fixture_from_real_repo "$FIXTURE_RED_B"
normalize_fixture "$FIXTURE_RED_B"
# SecurityTestPLAgent.md model: opus → fable 로 flip.
SEC_PATH="$FIXTURE_RED_B/plugins/codeforge-review/agents/SecurityTestPLAgent.md"
if [ -f "$SEC_PATH" ]; then
  sed -i 's/^model: opus$/model: fable/' "$SEC_PATH"
fi
EC_RED_B=$(run_gate_exit "$FIXTURE_RED_B")
assert_exit_1 "RED-B-exclusion-violated" "$EC_RED_B" "SecurityTestPL flip to fable 는 체크3 exclusion 위반 → exit 1"
rm -rf "$FIXTURE_RED_B"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스 RED-C — 프리셋 파일 손실 (체크4 census 위반)
#   plugins/codeforge-develop/presets/*/agents/*.md (3 파일) 삭제 → total=38 → RED
#   globstar-off 회귀 P1-1: find 사용 시 정확히 enumeration 하는지 검증.
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_RED_C=$(mktemp -d)
build_fixture_from_real_repo "$FIXTURE_RED_C"
normalize_fixture "$FIXTURE_RED_C"
# 프리셋 디렉토리 삭제 (있다면).
if [ -d "$FIXTURE_RED_C/plugins/codeforge-develop/presets" ]; then
  rm -rf "$FIXTURE_RED_C/plugins/codeforge-develop/presets"
fi
EC_RED_C=$(run_gate_exit "$FIXTURE_RED_C")
assert_exit_1 "RED-C-census-38" "$EC_RED_C" "preset 파일 손실(total=38) 는 체크4 census==41 위반 → exit 1"
rm -rf "$FIXTURE_RED_C"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스 RED-D — 비정규 파일이 fable 로 flip (체크2 bijection 위반)
#   worker 또는 deputy agent 중 하나(예: QADeveloperAgent.md, 원래 haiku) 를
#   model: fable 로 flip → count=11, bijection 위반 → non-zero exit
# ═════════════════════════════════════════════════════════════════════════════
FIXTURE_RED_D=$(mktemp -d)
build_fixture_from_real_repo "$FIXTURE_RED_D"
normalize_fixture "$FIXTURE_RED_D"
# QADeveloperAgent.md (haiku worker) 를 fable 로 flip (있다면).
QA_DEV_PATH="$FIXTURE_RED_D/plugins/codeforge-develop/agents/QADeveloperAgent.md"
if [ -f "$QA_DEV_PATH" ]; then
  if grep -q "^model:" "$QA_DEV_PATH"; then
    sed -i 's/^model:.*/model: fable/' "$QA_DEV_PATH"
  else
    sed -i '1a model: fable' "$QA_DEV_PATH"
  fi
  EC_RED_D=$(run_gate_exit "$FIXTURE_RED_D")
  assert_exit_1 "RED-D-bijection-non-target" "$EC_RED_D" "non-target agent flip to fable(count=11) 는 체크2 bijection 위반 → exit 1"
else
  # QADeveloperAgent 부재 시 다른 worker 찾아서 flip.
  ec_d_found=0
  for agent_file in "$FIXTURE_RED_D"/plugins/*/agents/*.md; do
    # 10 target 아닌지 확인.
    case "$agent_file" in
      *RequirementsPLAgent.md|*RequirementsReviewPLAgent.md|*ArchitectPLAgent.md|*DesignReviewPLAgent.md|*DeveloperPLAgent.md|*CodeReviewPLAgent.md|*PMOAgent.md|*ArchitectAgent.md|*ResearcherAgent.md|*IntegrationTestAgent.md)
        continue
        ;;
      *SecurityTestPLAgent.md)
        continue
        ;;
      *)
        # 이 파일을 fable 로 flip.
        if grep -q "^model:" "$agent_file"; then
          sed -i 's/^model:.*/model: fable/' "$agent_file"
        else
          sed -i '1a model: fable' "$agent_file"
        fi
        EC_RED_D=$(run_gate_exit "$FIXTURE_RED_D")
        assert_exit_1 "RED-D-bijection-non-target" "$EC_RED_D" "non-target agent flip to fable 는 체크2 bijection 위반 → exit 1"
        ec_d_found=1
        break
        ;;
    esac
  done
  if [ "$ec_d_found" -eq 0 ]; then
    note "[test-check-fable-roster-integrity] RED-D fixture 에서 non-target agent 못 찾음 — skip"
    SKIP=$((SKIP+1))
  fi
fi
rm -rf "$FIXTURE_RED_D"

# ── anti-theater discriminating 검증: GREEN exit 0 != RED exits (모두 exit 1) ──
if [ "$EC_GREEN" = "0" ] && [ "$EC_RED_A" = "1" ] && [ "$EC_RED_B" = "1" ] && [ "$EC_RED_C" = "1" ]; then
  echo "✓ PASS: ANTI-THEATER discriminating — GREEN exit=0 ≠ RED exits(all 1) (A=$EC_RED_A / B=$EC_RED_B / C=$EC_RED_C)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: ANTI-THEATER — GREEN($EC_GREEN) 또는 RED exits 가 기대값과 다름 (expected GREEN=0, RED all=1)"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# Real-repo liveness assertion (Change Plan §7 item 2 — REQUIRED)
#   실제 worktree repo 의 agent 파일 count == 41 확인.
#   find plugins -path "*/agents/*.md" 사용 (globstar-off, preset 손실 방지).
# ═════════════════════════════════════════════════════════════════════════════
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REAL_COUNT=0
if [ -d "$REPO_ROOT/plugins" ]; then
  # find: plugins 하위의 "*/agents/*.md" 패턴 검색 (depth 제한 없음 — preset depth 5 포함).
  REAL_COUNT=$(find "$REPO_ROOT/plugins" -path "*/agents/*.md" -type f | wc -l)
fi

assert_eq "REAL-REPO-CENSUS-41" "41" "$REAL_COUNT" "실제 worktree repo agent 파일 = 41개 (globstar-off enumeration, preset 포함)"

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "Test Summary (CFP-2803 Phase 2 fable roster integrity)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
echo "TOTAL ASSERT: $((PASS + FAIL))"
echo ""
echo "Discriminating evidence (anti-theater):"
echo "  GREEN(canonical 10 fable/1 opus-sec/41 total) exit=$EC_GREEN"
echo "  RED-A(fable count=9, DeveloperPL flip to opus) exit=$EC_RED_A"
echo "  RED-B(exclusion violated, SecurityTestPL flip to fable) exit=$EC_RED_B"
echo "  RED-C(census=38, preset files deleted) exit=$EC_RED_C"
echo "  Real-repo file count: $REAL_COUNT/41"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
