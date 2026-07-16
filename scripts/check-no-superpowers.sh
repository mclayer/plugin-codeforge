#!/usr/bin/env bash
# superpowers-allow lint — allowlist 외 라이브 superpowers: 호출 감지 (warning tier)
# ADR-122 회귀 방지 gate — superpowers 의존 완전 제거 후 토큰 재유입 차단
#
# CFP-2704 Phase 2 — thin wrapper 축소: archive/adr grep-hit 은 status-aware lib
#   (scripts/lib/check_superpowers_status_aware.py) 로 위임 (retired=EXEMPT /
#   live·unknown = scanned + 13-signature grandfather 차감). 나머지 파티션
#   (CHANGELOG-legacy·prune·self = wholesale EXEMPT / 그 외 = passthrough) 은 본 wrapper 유지.
#
# Layer 2 (lint grep 라이브 호출 governance):
#   - grep 패턴 = superpowers:[a-z][a-z0-9-]+ (literal `docs/superpowers/**` 경로 제외 — 두 축 분리)
#   - exit 1 = warning tier (CI 미wire, ADR-122 회귀 방지)
set -euo pipefail

# SCAN_ROOT 환경변수로 스캔 기준경로 override 가능 (test fixture 용)
REPO_ROOT="${SCAN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

# lib 경로는 SCRIPT 위치 기준 (SCAN_ROOT 아님) — test SCAN_ROOT sandbox 에서도 실 repo lib 참조 가능.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB="$SCRIPT_DIR/lib/check_superpowers_status_aware.py"

NL=$'\n'

# ── 라이브 superpowers: 호출 grep (토큰 재유입 감지 — 회귀 방지) ──────────────────
# 정규식: superpowers:[a-z][a-z0-9-]+ (콜론 즉시 후 소문자로 시작하는 skill 호출)
HITS=$(grep -rEn 'superpowers:[a-z][a-z0-9-]+' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.sh' \
  --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
  . 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "✓ superpowers-allow: 라이브 superpowers: 호출 없음 (OK)"
  exit 0
fi

# ── 파티션 루프 ──────────────────────────────────────────────────────────────
#   archive/adr/**                     → ADR_HITS (status-aware lib 위임)
#   CHANGELOG-legacy / prune / self    → wholesale EXEMPT (drop, DT-7 무변경)
#   그 외                               → NON_ARCHIVE_VIOLATIONS (DT-8 passthrough)
ADR_HITS=""
NON_ARCHIVE_VIOLATIONS=""
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  file="${line%%:*}"
  file="${file#./}"

  if [[ "$file" == archive/adr/* ]]; then
    ADR_HITS="${ADR_HITS:+$ADR_HITS$NL}$line"
  elif [[ "$file" == "archive/CHANGELOG-legacy.md" ]] \
    || [[ "$file" == archive/prune-2026-06/* ]] \
    || [[ "$file" == "scripts/check-no-superpowers.sh" ]] \
    || [[ "$file" == "scripts/test-check-no-superpowers.sh" ]]; then
    :  # wholesale EXEMPT (drop)
  else
    NON_ARCHIVE_VIOLATIONS="${NON_ARCHIVE_VIOLATIONS:+$NON_ARCHIVE_VIOLATIONS$NL}$line"
  fi
done <<< "$HITS"

# ── archive/adr grep-hit → status-aware lib 위임 (python 항상 exit 0 → set -e 안전) ──
ADR_VIOLATIONS=""
if [[ -n "$ADR_HITS" ]]; then
  ADR_VIOLATIONS=$(printf '%s\n' "$ADR_HITS" | python3 "$LIB")
fi

# ── RESIDUAL = NON_ARCHIVE_VIOLATIONS + ADR_VIOLATIONS (개행 join, 빈 값 제거) ──
RESIDUAL=$(printf '%s\n%s\n' "$NON_ARCHIVE_VIOLATIONS" "$ADR_VIOLATIONS" | grep -v '^$' || true)

if [[ -z "$RESIDUAL" ]]; then
  echo "✓ superpowers-allow: 라이브 호출은 EXEMPT 영역에만 존재 (OK)"
  exit 0
fi

echo "⚠ superpowers-allow warning: EXEMPT 외 라이브 superpowers: 호출 발견 (warning tier — ADR-122 회귀 gate)"
echo "$RESIDUAL"
exit 1
