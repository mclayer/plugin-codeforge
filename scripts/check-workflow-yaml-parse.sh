#!/usr/bin/env bash
# CFP-583 / ADR-060 Amendment 9 §결정 22 — workflow yml yaml parse + actionlint dual validation
# Exit code 3-tier (ADR-060 Amendment 2 §결정 15):
#   0 = PASS (all file PyYAML + actionlint clean)
#   1 = validation FAIL (yaml parse fail OR actionlint warning)
#   2 = meta-error (PyYAML 미설치 / python binary 부재)
set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-.}"
FAILED_YAML=()
FAILED_ACTIONLINT=()
PY_BIN="${PYTHON:-python}"

# meta-error guard: PyYAML 설치 확인
if ! command -v "$PY_BIN" >/dev/null 2>&1; then
  echo "::error::meta-error — python not found (binary: ${PY_BIN}). PyYAML required for workflow yaml parse."
  exit 2
fi

if ! "$PY_BIN" -c "import yaml" 2>/dev/null; then
  echo "::error::meta-error — PyYAML not installed. Run: pip install pyyaml"
  exit 2
fi

# Glob scope: .github/workflows/*.yml + templates/github-workflows/*.yml
for file in "$ROOT/.github/workflows"/*.yml "$ROOT/templates/github-workflows"/*.yml; do
  [ -e "$file" ] || continue

  # (1) PyYAML safe_load — strict parse
  if ! "$PY_BIN" -c "import yaml, sys; yaml.safe_load(open(sys.argv[1], encoding='utf-8'))" "$file" 2>/dev/null; then
    FAILED_YAML+=("$file")
    continue
  fi

  # (2) actionlint (Go binary, GitHub Actions parser semantics) — optional, skip if not installed
  if command -v actionlint >/dev/null 2>&1; then
    if ! actionlint "$file" >/dev/null 2>&1; then
      FAILED_ACTIONLINT+=("$file")
    fi
  fi
done

if [ ${#FAILED_YAML[@]} -gt 0 ]; then
  echo "::error::workflow yaml parse FAIL — ${#FAILED_YAML[@]} file(s) failed PyYAML safe_load:"
  printf '  %s\n' "${FAILED_YAML[@]}"
fi

if [ ${#FAILED_ACTIONLINT[@]} -gt 0 ]; then
  echo "::error::actionlint FAIL — ${#FAILED_ACTIONLINT[@]} file(s) failed actionlint:"
  printf '  %s\n' "${FAILED_ACTIONLINT[@]}"
fi

if [ ${#FAILED_YAML[@]} -gt 0 ] || [ ${#FAILED_ACTIONLINT[@]} -gt 0 ]; then
  exit 1
fi

echo "workflow-yaml-parse PASS — all workflow yml parse clean (PyYAML safe_load OK)"
exit 0
