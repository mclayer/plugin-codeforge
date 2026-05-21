#!/usr/bin/env bash
# templates/deployment/auto-version-bump.sh
# CFP-1059-S6 — Epic close -> semver bump + git tag = Docker tag (ADR-026 + ADR-063)
#
# §3.1: Epic close detect -> repo별 semver bump + git tag (= Docker tag = container name 1:1)
# §11.6 idempotency: git tag 존재 시 skip (재실행 = no-op)
# §7.5 secret: DOCKER_HUB_TOKEN = env var only (no echo/log)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VERSION_PY="${WORKTREE_ROOT}/scripts/auto_version_bump.py"

REPO_PATH=""
CURRENT_VERSION=""
BUMP_TYPE="minor"

usage() {
  echo "Usage: $0 --repo-path <path> --current-version <ver> --bump-type <major|minor|patch>"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-path)       REPO_PATH="$2";       shift 2 ;;
    --current-version) CURRENT_VERSION="$2"; shift 2 ;;
    --bump-type)       BUMP_TYPE="$2";       shift 2 ;;
    --help|-h)         usage ;;
    *)                 echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO_PATH}" || -z "${CURRENT_VERSION}" ]]; then
  echo "[ERROR] --repo-path, --current-version 필수" >&2
  exit 1
fi

MOCK_GIT="${_CFP1059_MOCK_GIT:-0}"

echo "=== auto-version-bump.sh ==="
echo "repo-path=${REPO_PATH} current=${CURRENT_VERSION} bump-type=${BUMP_TYPE}"

if [[ -f "${VERSION_PY}" ]]; then
  PYTHONUTF8=1 python3 "${VERSION_PY}" \
    --repo-path "${REPO_PATH}" \
    --current-version "${CURRENT_VERSION}" \
    --bump-type "${BUMP_TYPE}" \
    --mock-git "${MOCK_GIT}"
else
  echo "[ERROR] auto_version_bump.py 부재 — ADR-061 Python 로직 파일 필요" >&2
  exit 1
fi
