#!/usr/bin/env bash
set -euo pipefail

# check-claude-md-line-cap.sh — CFP-506 / ADR-012 Amendment 1 §결정 6 / ADR-060 Amendment 5
# CLAUDE.md line count cap ≤320 mechanical lint (warning tier)
# exit 0: PASS / exit 1: cap 초과 / exit 2: meta-error

CAP=320

# meta-error guard: CLAUDE.md 존재 확인
if [ ! -f "CLAUDE.md" ]; then
  echo "::error::CLAUDE.md not found — check script working directory"
  exit 2
fi

COUNT=$(wc -l < CLAUDE.md)

if [ "$COUNT" -gt "$CAP" ]; then
  echo "::warning::CLAUDE.md line count $COUNT exceeds cap $CAP (ADR-012 Amendment 1 §결정 6)"
  echo "FAIL: CLAUDE.md $COUNT lines > cap $CAP"
  exit 1
fi

echo "PASS: CLAUDE.md $COUNT lines within cap $CAP"
exit 0
