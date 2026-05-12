#!/usr/bin/env bash
# CFP-428 — install templates/.git-hooks/*.sample to .git/hooks/ as symlinks (idempotent, opt-in).
# carrier: ADR-040 Amendment 3 §결정 7.D self-application — actual wire entry point
#
# 동작:
#   - templates/.git-hooks/*.sample 를 .git/hooks/<name> 으로 symlink.
#   - 이미 symlinked → no-op (idempotent 1st guard).
#   - non-symlink file 존재 → skip + WARN (사용자 explicit conflict resolution 필요).
#   - chmod +x sample 자체 (symlink target executable bit propagation).
#
# 본 Story (CFP-428) 시점 = opt-in 시작 — 사용자 명시적 호출 전까지 wrapper 자체 git hook 미활성.
# Story 4 (CFP-429) = warning → blocking-on-pr 승격 시 install 의무화 plan 명세 (별도 carrier).
#
# 참조:
#   - ADR-013 dogfood-out
#   - CFP-429 Story 4: install 의무화 plan
#   - Pro Git book §8.3 Git Hooks
#   - pre-commit framework opt-in install pattern

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GIT_HOOKS="$REPO_ROOT/.git/hooks"
TEMPLATE_HOOKS="$REPO_ROOT/templates/.git-hooks"

if [[ ! -d "$TEMPLATE_HOOKS" ]]; then
  echo "[install-git-hooks] WARN: $TEMPLATE_HOOKS not found — nothing to install" >&2
  exit 0
fi

shopt -s nullglob
samples=("$TEMPLATE_HOOKS"/*.sample)
shopt -u nullglob

if [[ ${#samples[@]} -eq 0 ]]; then
  echo "[install-git-hooks] WARN: no .sample files found in $TEMPLATE_HOOKS" >&2
  exit 0
fi

for sample in "${samples[@]}"; do
  [[ -f "$sample" ]] || continue
  base="$(basename "$sample" .sample)"
  target="$GIT_HOOKS/$base"

  if [[ -L "$target" ]]; then
    echo "[install-git-hooks] $target already symlinked — skip"
    continue
  fi

  if [[ -e "$target" ]]; then
    echo "[install-git-hooks] WARN: $target exists (non-symlink) — skip (사용자 explicit conflict resolution 필요)" >&2
    continue
  fi

  chmod +x "$sample"
  ln -s "$sample" "$target"
  echo "[install-git-hooks] linked: $target -> $sample"
done

exit 0
