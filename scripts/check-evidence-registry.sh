#!/usr/bin/env bash
# CFP-881 / ADR-060 Amendment 26 — evidence-checks-registry.yaml 구조 무결성 게이트 (thin wrapper).
# Python SSOT: scripts/lib/check_evidence_registry.py (yaml.safe_load strict-verify + collecting
# UniqueKeyLoader duplicate-key surface). ADR-061 thin bash wrapper 관례.
#
# Exit code 3-tier (ADR-060 Amendment 2 §결정 15):
#   0 = PASS (구조 무결)
#   1 = validation FAIL (문법/스키마/name-unique/duplicate-key surface)
#   2 = meta-error (python·PyYAML 부재 — 본 pre-guard / registry 파일 부재 — Python SSOT)
set -euo pipefail

PY_BIN="${PYTHON:-python3}"

# meta-error pre-guard: python interpreter 부재
if ! command -v "$PY_BIN" >/dev/null 2>&1; then
  echo "::error::meta-error — python not found (binary: ${PY_BIN}). PyYAML required for evidence-registry structure verify." >&2
  exit 2
fi

# meta-error pre-guard: PyYAML 미설치
if ! "$PY_BIN" -c "import yaml" >/dev/null 2>&1; then
  echo "::error::meta-error — PyYAML not installed. Run: pip install pyyaml" >&2
  exit 2
fi

exec "$PY_BIN" "$(dirname "$0")/lib/check_evidence_registry.py" "$@"
