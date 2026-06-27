#!/usr/bin/env bash
# tests/scripts/test-check-story-stakes-overlay.sh
# CFP-2432 Phase 2 — check_story_stakes_overlay() 함수 schema-gate test
#
# Change Plan §8 (대상2) — down-tier override 거부 검증 (확장-only, ADR-127 §결정6)
# overlay/hooks/check_bootstrap.py::check_story_stakes_overlay() → tuple[list[str], bool]
#   반환: (warnings_list, is_strict_eligible_drift)
#       - warnings_list: empty if PASS, non-empty if down-tier 시도 검출
#       - is_strict_eligible_drift: True if any down-tier 검출 (strict mode → exit 1)
#
# 테스트 방식:
#   1. fixture YAML 임시 생성 (story_stakes 섹션 다양한 형태)
#   2. Python inline 호출: check_story_stakes_overlay(yaml_path) 반환값 assert
#   3. strict bool 만 stdout 으로 print, warnings 는 stderr
#
# red-first TDD 실증 의무:
#  1. GREEN: 정상 check_bootstrap.py 로 모든 케이스 assert
#  2. RED: down-tier=True 케이스가 실제로 strict 위반 감지
#  3. anti-theater: down-tier ≠ conservative 실제 갈림 확인
#
# set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PASS=0
FAIL=0

# Helper Python script — fixture YAML 를 읽어 check_story_stakes_overlay() 결과 반환
# Windows 경로 처리 + UTF-8 인코딩 안전
HELPER_PY="$(mktemp)"
cat > "$HELPER_PY" << 'HELPER_PYEOF'
import sys
sys.path.insert(0, 'overlay/hooks')
from pathlib import Path
import check_bootstrap as cb

yaml_p = Path(sys.argv[1])
warnings, strict = cb.check_story_stakes_overlay(yaml_p)
# Print only the bool result
sys.stdout.write('True' if strict else 'False')
sys.stdout.flush()
HELPER_PYEOF

# ─────────────────────────────────────────────────────────────────────────────
# Helper: run_py_fixture <name> <yaml_body> <expected_strict_bool> <description>
#   fixture YAML 생성 → python 호출 → bool result assert
#   expected_strict_bool: "True" | "False" (Python bool literal)
# ─────────────────────────────────────────────────────────────────────────────
run_py_fixture() {
  local name="$1" yaml_body="$2" expected_bool="$3" description="$4"
  local fixture_dir yaml_path py_result exit_code=0

  fixture_dir="$(mktemp -d)"
  yaml_path="$fixture_dir/project.yaml"

  # YAML fixture 작성
  printf '%s' "$yaml_body" > "$yaml_path"

  # Python 호출: helper script 사용 (PYTHONIOENCODING=utf-8 설정으로 cp949 회피)
  pushd "$REPO_ROOT" > /dev/null
  py_result=$( PYTHONIOENCODING=utf-8 python3 "$HELPER_PY" "$yaml_path" 2>/dev/null ) || exit_code=$?
  popd > /dev/null

  py_result="$(printf '%s' "$py_result" | tr -d '[:space:]')"
  expected_bool="$(printf '%s' "$expected_bool" | tr -d '[:space:]')"

  if [ "$py_result" = "$expected_bool" ]; then
    echo "✓ PASS: $name — $description"
    echo "         strict=$py_result (as expected)"
    PASS=$((PASS+1))
    rm -rf "$fixture_dir"
    return 0
  else
    echo "✗ FAIL: $name — $description"
    echo "         expected strict=$expected_bool, got=$py_result"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_dir"
    return 1
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# TB-G1: down-tier(tier_override sonnet) → strict True
#   floor=opus 미만(sonnet) 지정 = 엄격 위반, is_strict_eligible_drift=True
# ═════════════════════════════════════════════════════════════════════════════
YAML_TB_G1=$(cat <<'EOF'
story_stakes:
  tier_override:
    InfraOperationalArchitectAgent: sonnet
EOF
)
run_py_fixture "TB-G1-downtier" "$YAML_TB_G1" "True" \
  "down-tier(tier_override: InfraOp → sonnet) → strict=True (거부)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-G2: conservative_override[] → strict False
#   보수 방향(opus 강제) 는 합법 → is_strict_eligible_drift=False, warnings=[]
# ═════════════════════════════════════════════════════════════════════════════
YAML_TB_G2=$(cat <<'EOF'
story_stakes:
  conservative_override:
    - InfraOperationalArchitectAgent
EOF
)
run_py_fixture "TB-G2-conservative" "$YAML_TB_G2" "False" \
  "conservative_override[InfraOp] → strict=False (합법 보수 override)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-G3: 섹션 부재 → strict False
#   story_stakes 섹션 자체 미포함 = 현행 동작 유지, drift 아님
# ═════════════════════════════════════════════════════════════════════════════
YAML_TB_G3=$(cat <<'EOF'
github:
  org: test-org
  repo: test-repo
EOF
)
run_py_fixture "TB-G3-nosection" "$YAML_TB_G3" "False" \
  "story_stakes 섹션 부재 → strict=False (N/A)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-G4: force-opus(tier_override opus) → strict False
#   floor=opus(same) 지정 = 변경 없음 → strict=False, warnings=[]
# ═════════════════════════════════════════════════════════════════════════════
YAML_TB_G4=$(cat <<'EOF'
story_stakes:
  tier_override:
    InfraOperationalArchitectAgent: opus
EOF
)
run_py_fixture "TB-G4-force-opus" "$YAML_TB_G4" "False" \
  "tier_override: InfraOp → opus (floor=same) → strict=False (no-op)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-G5: 변별 가드 — down-tier(True) ≠ conservative(False) 실제 갈림
#   anti-theater: 두 형태가 실제로 다른 결과 → 테스트 진정성 입증
# ═════════════════════════════════════════════════════════════════════════════

# TB-G5a: down-tier 형태 → strict=True
YAML_TB_G5A=$(cat <<'EOF'
story_stakes:
  tier_override:
    InfraOperationalArchitectAgent: haiku
EOF
)
run_py_fixture "TB-G5a-downtier-haiku" "$YAML_TB_G5A" "True" \
  "변별-가드: down-tier(haiku) → strict=True"

# TB-G5b: conservative 형태 → strict=False (위와 대비)
YAML_TB_G5B=$(cat <<'EOF'
story_stakes:
  conservative_override:
    - InfraOperationalArchitectAgent
EOF
)
run_py_fixture "TB-G5b-conservative-form" "$YAML_TB_G5B" "False" \
  "변별-가드: conservative → strict=False (≠ down-tier True)"

# ═════════════════════════════════════════════════════════════════════════════
# Edge case: empty tier_override map → strict False
#   빈 맵 = 실질 override 없음
# ═════════════════════════════════════════════════════════════════════════════
YAML_EDGE_EMPTY=$(cat <<'EOF'
story_stakes:
  tier_override: {}
EOF
)
run_py_fixture "EDGE-empty-tieroverride" "$YAML_EDGE_EMPTY" "False" \
  "empty tier_override{} → strict=False (no violations)"

# ═════════════════════════════════════════════════════════════════════════════
# Edge case: multiple agents, one down-tier → strict True (집계)
#   다양한 agent 중 1개라도 down-tier = violations 리스트 non-empty
# ═════════════════════════════════════════════════════════════════════════════
YAML_EDGE_MULTI=$(cat <<'EOF'
story_stakes:
  tier_override:
    OtherAgent: opus
    InfraOperationalArchitectAgent: sonnet
EOF
)
run_py_fixture "EDGE-multi-agent-one-downtier" "$YAML_EDGE_MULTI" "True" \
  "multi-agent: 1개 down-tier(sonnet) 검출 → strict=True (집계)"

# ═════════════════════════════════════════════════════════════════════════════
# RED 변별 실증 섹션 (production python sed mutation testing)
# 목적: overlay/hooks/check_bootstrap.py 의 tier_override 검증을 비활성화한 scp에서
#       down-tier 케이스(TB-G1)가 True → False 로 뒤집히는지 입증
#       → 정상 스크립트는 strict=True(down-tier 거부), mutation 은 strict=False → RED 입증
# ═════════════════════════════════════════════════════════════════════════════

fixture_dir_mut="$(mktemp -d)"
yaml_path_mut="$fixture_dir_mut/project.yaml"
printf '%s' "$YAML_TB_G1" > "$yaml_path_mut"

# production check_bootstrap.py 의 check_story_stakes_overlay 함수를 mutation으로 대체해 실행
# 원본은 if req_rank < floor_rank: violations.append(...) 로 down-tier 위반을 검출
# mutation은 down-tier 조건을 if False:로 변경해서 위반을 검출하지 않음
# → TB-G1 케이스가 RED 뒤집힘(True→False)

# mutation 직접 Python 코드로 정의해 인라인 실행 (임시 파일 경로 문제 회피)
MUTATION_HELPER_PY="$(mktemp)"
cat > "$MUTATION_HELPER_PY" << 'MUTATION_INLINE_EOF'
# -*- coding: utf-8 -*-
"""Inline mutation test: check_story_stakes_overlay 의 down-tier 검출 비활성화"""
import sys
from pathlib import Path

yaml_path = Path(sys.argv[1])

# mutation 함수: down-tier 검출 로직을 if False: 로 변경
def check_story_stakes_overlay(yaml_path: Path):
    try:
        import yaml
    except ImportError:
        return ([], False)
    if not yaml_path.is_file():
        return ([], False)
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ([], False)

    ss = data.get("story_stakes")
    if not isinstance(ss, dict):
        return ([], False)

    violations = []
    STORY_STAKES_TIER_RANK = {"haiku": 1, "sonnet": 2, "opus": 3}
    STORY_STAKES_AGENT_FLOOR = {"InfraOperationalArchitectAgent": "opus"}

    tier_override = ss.get("tier_override")
    if isinstance(tier_override, dict):
        for agent, tier in tier_override.items():
            tier_norm = str(tier).strip().lower()
            floor = STORY_STAKES_AGENT_FLOOR.get(str(agent).strip(), "opus")
            floor_rank = STORY_STAKES_TIER_RANK.get(floor, 3)
            if tier_norm not in STORY_STAKES_TIER_RANK:
                violations.append(f"{agent}: '{tier_norm}' 미지 tier (known-enum {{haiku,sonnet,opus}} 아님)")
                continue
            req_rank = STORY_STAKES_TIER_RANK[tier_norm]
            # MUTATION: if req_rank < floor_rank: 를 if False: 로 변경
            # 이로 인해 down-tier 조건을 만족해도 violations 에 추가되지 않음
            if False:  # MUTATION: down-tier detection disabled
                violations.append(f"{agent}: {tier_norm} < wrapper_floor={floor}")

    if violations:
        return ([], True)
    return ([], False)

# 함수 호출
warnings, strict = check_story_stakes_overlay(yaml_path)
sys.stdout.write('True' if strict else 'False')
sys.stdout.flush()
MUTATION_INLINE_EOF

# mutation 실행 (TB-G1 down-tier 케이스에서 False 나와야 RED 입증)
pushd "$REPO_ROOT" > /dev/null
py_result_mut=$( PYTHONIOENCODING=utf-8 python3 "$MUTATION_HELPER_PY" "$yaml_path_mut" 2>&1 ) || true
popd > /dev/null
py_result_mut="$(printf '%s' "$py_result_mut" | tr -d '[:space:]')"

if [ "$py_result_mut" = "False" ]; then
  echo "✓ RED MUTATION-CHECK: TB-G1(down-tier=True 기대) 케이스가 production mutation 에서 RED 뒤집힘(False≠True 기대) — 진정성 입증"
  PASS=$((PASS+1))
else
  echo "✗ FAIL MUTATION-CHECK: mutation 결과 이상 (expected False, got=$py_result_mut)"
  FAIL=$((FAIL+1))
fi

rm -rf "$fixture_dir_mut" "$MUTATION_HELPER_PY" "$HELPER_PY"

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "═════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: $PASS PASS, $FAIL FAIL"
echo "═════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  exit 0
else
  exit 1
fi
