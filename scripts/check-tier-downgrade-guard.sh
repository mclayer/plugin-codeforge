#!/usr/bin/env bash
# tier-downgrade guard — evidence-checks-registry.yaml 강제강도(current_tier) 무단 하향 방지
#
# 레드팀 발견: docs/evidence-checks-registry.yaml 의 current_tier 가 "검사 강제 강도"의
#   단일 출처(SSOT)인데 어떤 검사도 이 필드를 지키지 않는다 — 기존 약화방지 가드
#   (sunset-weakening-evidence / adr-077-ratchet / adr-sunset-criteria) 가 전부
#   docs/adr/ADR-*.md 경로에만 걸려 있어, registry 의 tier 하향/entry 제거는 아무도 안 본다.
#
# 본 가드 = tier 하향(blocking→warning 등) / entry 제거를 감지하고, 명시적 정당화 마커가
#   있을 때만 허용한다 — 동시에 (a) 무방비 hole 폐쇄 + (b) 정정/축소 lane 의 경량 강제 수단.
#   정책 SSOT: docs/correction-lane.md
#
# 정당화 마커 (둘 중 하나):
#   (a) 환경변수 TIER_DOWNGRADE_JUSTIFICATION (CI 가 PR body / commit msg 를 주입)
#   (b) 최신 commit message 의 `tier-downgrade-justification:` 라인
#
# exit code: 0 = 하향 없음 또는 마커로 정당화됨 / 1 = 정당화되지 않은 하향·제거 감지
#
# style: scripts/check-adr-sunset-criteria.sh 헤더 관례 답습 (warning workflow family).
set -euo pipefail

REGISTRY="docs/evidence-checks-registry.yaml"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# --- base ref 결정 -----------------------------------------------------------
git fetch -q origin main 2>/dev/null || true
BASE_REF=""
if git rev-parse --verify -q origin/main >/dev/null; then
  BASE_REF="origin/main"
elif MB="$(git merge-base origin/main HEAD 2>/dev/null)"; then
  BASE_REF="$MB"
fi

if [ -z "$BASE_REF" ]; then
  echo "ⓘ base ref(origin/main) 미가용 — 비교 생략, 통과 처리 (new repo / detached 환경)."
  exit 0
fi

# base 시점 registry 파일 자체가 없으면(신규 도입) 비교 불가 → 통과.
if ! git cat-file -e "${BASE_REF}:${REGISTRY}" 2>/dev/null; then
  echo "ⓘ base(${BASE_REF}) 에 ${REGISTRY} 부재 — 신규 도입으로 간주, 통과 처리."
  exit 0
fi

# --- name → current_tier 추출 (awk, 첫 current_tier 채택, 주석 strip) ----------
extract_pairs() {
  # stdin = registry yaml, stdout = "<name>\t<tier>" per entry
  awk '
    /^[[:space:]]*-[[:space:]]+name:[[:space:]]*/ {
      # 이전 entry flush (tier 미발견이면 빈 값)
      if (cur != "") { print cur "\t" tier }
      line = $0
      sub(/^[[:space:]]*-[[:space:]]+name:[[:space:]]*/, "", line)
      sub(/[[:space:]]*#.*$/, "", line)         # 인라인 주석 제거
      gsub(/[[:space:]]+$/, "", line)           # trailing ws
      cur = line
      tier = ""
      next
    }
    /^[[:space:]]*current_tier:[[:space:]]*/ {
      if (cur != "" && tier == "") {            # entry 당 첫 current_tier 만
        t = $0
        sub(/^[[:space:]]*current_tier:[[:space:]]*/, "", t)
        sub(/[[:space:]]*#.*$/, "", t)          # 인라인 주석 제거
        gsub(/[[:space:]]+$/, "", t)
        tier = t
      }
      next
    }
    END { if (cur != "") { print cur "\t" tier } }
  '
}

git show "${BASE_REF}:${REGISTRY}" | extract_pairs > /tmp/tier_base.txt

# head/working-tree 버전 — 작업본이 우선(아직 commit 안 된 변경 포함).
if [ -f "$REGISTRY" ]; then
  extract_pairs < "$REGISTRY" > /tmp/tier_head.txt
else
  git show "HEAD:${REGISTRY}" | extract_pairs > /tmp/tier_head.txt
fi

# --- tier rank ---------------------------------------------------------------
rank() {
  case "$1" in
    warning)           echo 1 ;;
    blocking-on-pr)    echo 2 ;;
    blocking-on-merge) echo 3 ;;
    "")                echo 0 ;;   # entry 제거(head 부재) = 0 으로 강등
    *)                 echo 0 ;;   # 미지 tier = 보수적으로 0 (downgrade 취급)
  esac
}

# --- downgrade 탐지 ----------------------------------------------------------
DOWNGRADES=""
DOWNGRADE_COUNT=0

while IFS=$'\t' read -r name base_tier; do
  [ -z "$name" ] && continue
  # head 에서 동일 name 의 tier 조회
  head_tier="$(awk -F'\t' -v n="$name" '$1==n {print $2; exit}' /tmp/tier_head.txt)"
  present_in_head="no"
  if grep -qxF -- "$name	$head_tier" /tmp/tier_head.txt 2>/dev/null; then
    present_in_head="yes"
  fi
  # head 부재 판정: name 자체가 없으면 제거
  if ! awk -F'\t' -v n="$name" '$1==n {found=1} END{exit !found}' /tmp/tier_head.txt; then
    head_tier=""            # 제거됨
  fi

  base_rank="$(rank "$base_tier")"
  head_rank="$(rank "$head_tier")"

  if [ "$head_rank" -lt "$base_rank" ]; then
    DOWNGRADE_COUNT=$((DOWNGRADE_COUNT + 1))
    if [ "$head_rank" -eq 0 ] && [ -z "$head_tier" ]; then
      DOWNGRADES="${DOWNGRADES}  - ${name}: [REMOVED]  (base tier=${base_tier} → entry 제거)"$'\n'
    else
      DOWNGRADES="${DOWNGRADES}  - ${name}: ${base_tier} → ${head_tier}  (강제강도 하향)"$'\n'
    fi
  fi
done < /tmp/tier_base.txt

# --- 결과 판정 ---------------------------------------------------------------
if [ "$DOWNGRADE_COUNT" -eq 0 ]; then
  echo "✓ tier-downgrade guard — no tier weakening detected (하향/제거 0건)."
  exit 0
fi

echo "=== tier-downgrade guard — 강제강도 하향/entry 제거 감지 (${DOWNGRADE_COUNT}건) ==="
printf '%s' "$DOWNGRADES"
echo "==="

# --- 정당화 마커 탐색 --------------------------------------------------------
JUSTIFICATION=""
if [ -n "${TIER_DOWNGRADE_JUSTIFICATION:-}" ]; then
  # env 값에서 마커 라인 우선, 없으면 전체 값을 근거로 사용.
  marker_line="$(printf '%s\n' "$TIER_DOWNGRADE_JUSTIFICATION" | grep -m1 'tier-downgrade-justification:' || true)"
  if [ -n "$marker_line" ]; then
    JUSTIFICATION="$marker_line"
  else
    JUSTIFICATION="$TIER_DOWNGRADE_JUSTIFICATION"
  fi
fi

if [ -z "$JUSTIFICATION" ]; then
  COMMIT_MSG="$(git log -1 --format=%B 2>/dev/null || true)"
  marker_line="$(printf '%s\n' "$COMMIT_MSG" | grep -m1 'tier-downgrade-justification:' || true)"
  [ -n "$marker_line" ] && JUSTIFICATION="$marker_line"
fi

if [ -n "$JUSTIFICATION" ]; then
  echo ""
  echo "✓ 정정/축소 lane 마커 확인 — 하향 허용 (docs/correction-lane.md)."
  echo "  justification: ${JUSTIFICATION}"
  exit 0
fi

echo ""
echo "✗ 정당화되지 않은 강제강도 하향/제거 — FAIL."
echo "  강제강도를 낮추거나 거버넌스를 제거하려면 '정정/축소 lane' 마커가 필요합니다:"
echo "    - commit message 또는 PR body 에 다음 라인 추가:"
echo "        tier-downgrade-justification: <근거 (red-team/audit 증거 인용)>"
echo "  정책 SSOT: docs/correction-lane.md"
exit 1
