#!/usr/bin/env bash
# superpowers-allow lint — allowlist 외 라이브 superpowers: 호출 감지 (warning tier)
# ADR-122 회귀 방지 gate — superpowers 의존 완전 제거 후 토큰 재유입 차단
#
# Layer 2 (lint grep 라이브 호출 governance):
#   - grep 패턴 = superpowers:[a-z][a-z0-9-]+ (literal `docs/superpowers/**` 경로 제외 — 두 축 분리)
#   - EXEMPT (이력 보존): archive/adr/** + archive/CHANGELOG-legacy.md + archive/prune-2026-06/**
#   - exit 1 = warning tier (CI 미wire, ADR-122 회귀 방지)
set -euo pipefail

# SCAN_ROOT 환경변수로 스캔 기준경로 override 가능 (test fixture 용)
REPO_ROOT="${SCAN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

# ── 라이브 superpowers: 호출 grep (토큰 재유입 감지 — 회귀 방지) ──────────────────
# 정규식: superpowers:[a-z][a-z0-9-]+ (콜론 즉시 후 소문자로 시작하는 skill 호출)
# 매칭: superpowers:brainstorming, [superpowers:xxx], "superpowers:yyy" 등 모든 형식
HITS=$(grep -rEn 'superpowers:[a-z][a-z0-9-]+' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.sh' \
  --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
  . 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "✓ superpowers-allow: 라이브 superpowers: 호출 없음 (OK)"
  exit 0
fi

# ── EXEMPT 필터 (ADR-122 회귀 방지 설계) ───────────────────────────────────────
# EXEMPT 경로: archive/adr/** + archive/CHANGELOG-legacy.md + archive/prune-2026-06/**
# + 스크립트 자신 (정규식 문자열 포함 시 self-match 회피)
FILTERED=$(echo "$HITS" | while IFS= read -r line; do
  file="${line%%:*}"
  file="${file#./}"
  EXEMPT=false

  # archive/adr/** 이력 보존
  if [[ "$file" == archive/adr/* ]]; then
    EXEMPT=true
  fi

  # archive/CHANGELOG-legacy.md 이력 보존
  if [[ "$file" == "archive/CHANGELOG-legacy.md" ]]; then
    EXEMPT=true
  fi

  # archive/prune-2026-06/** 이력 보존
  if [[ "$file" == archive/prune-2026-06/* ]]; then
    EXEMPT=true
  fi

  # 본 스크립트 + test fixture (정규식 문자열 self-reference 회피)
  if [[ "$file" == "scripts/check-no-superpowers.sh" ]] || [[ "$file" == "scripts/test-check-no-superpowers.sh" ]]; then
    EXEMPT=true
  fi

  if ! $EXEMPT; then echo "$line"; fi
done)

if [[ -z "$FILTERED" ]]; then
  echo "✓ superpowers-allow: 라이브 호출은 EXEMPT 영역에만 존재 (OK)"
  exit 0
fi

echo "⚠ superpowers-allow warning: EXEMPT 외 라이브 superpowers: 호출 발견 (warning tier — ADR-122 회귀 gate)"
echo "$FILTERED"
exit 1
