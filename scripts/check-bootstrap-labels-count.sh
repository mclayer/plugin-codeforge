#!/usr/bin/env bash
# check-bootstrap-labels-count.sh
# CFP-492 — bootstrap-labels.sh 2-way self-check lint.
#
# 목적: --dry-run 출력 line count (stdout) == create_label 호출 횟수 (stderr "invocations: N") 일치 검증.
# 잠재적 drift: 신규 label 추가 시 create_label invocation 추가했으나
#               dry-run 출력 line 이 redirect / pipe 누락으로 count 불일치 발생 가능.
#
# Usage:
#   bash scripts/check-bootstrap-labels-count.sh
#   bash scripts/check-bootstrap-labels-count.sh --help
#
# Exit codes:
#   0 = PASS (dry-run line count == create_label invocations)
#   1 = FAIL (drift detected: count mismatch)
#   2 = meta-error (bootstrap-labels.sh 부재 / 실행 실패 / stderr 패턴 미검출)

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,20p' "$0" >&2
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_SCRIPT="$SCRIPT_DIR/bootstrap-labels.sh"

# bootstrap-labels.sh 존재 확인
if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
  echo "[check-bootstrap-labels-count] ERROR: bootstrap-labels.sh 부재: $BOOTSTRAP_SCRIPT" >&2
  exit 2
fi

# --dry-run 실행 — stdout / stderr 분리 capture
TMP_STDOUT="$(mktemp -t bootstrap-check-out.XXXXXX)"
TMP_STDERR="$(mktemp -t bootstrap-check-err.XXXXXX)"
trap 'rm -f "$TMP_STDOUT" "$TMP_STDERR"' EXIT

if ! bash "$BOOTSTRAP_SCRIPT" --dry-run >"$TMP_STDOUT" 2>"$TMP_STDERR"; then
  echo "[check-bootstrap-labels-count] ERROR: bootstrap-labels.sh --dry-run 실행 실패 (exit code 비0)" >&2
  exit 2
fi

# dry-run stdout line count 추출
DRY_RUN_LINE_COUNT="$(wc -l < "$TMP_STDOUT" | tr -d ' ')"

# stderr 의 "create_label invocations: N" 패턴에서 N 추출
INVOCATION_COUNT=""
if grep -qE '\[bootstrap-labels self-check\] create_label invocations: [0-9]+' "$TMP_STDERR"; then
  INVOCATION_COUNT="$(grep -oE 'create_label invocations: [0-9]+' "$TMP_STDERR" | grep -oE '[0-9]+' | head -1)"
else
  echo "[check-bootstrap-labels-count] ERROR: stderr 에서 'create_label invocations: N' 패턴 미검출." >&2
  echo "  stderr 내용: $(cat "$TMP_STDERR")" >&2
  exit 2
fi

if [[ -z "$INVOCATION_COUNT" ]]; then
  echo "[check-bootstrap-labels-count] ERROR: invocation count 추출 실패" >&2
  exit 2
fi

# 2-way 비교
if [[ "$DRY_RUN_LINE_COUNT" -eq "$INVOCATION_COUNT" ]]; then
  echo "[check-bootstrap-labels-count] PASS — dry-run output lines: $DRY_RUN_LINE_COUNT, create_label invocations: $INVOCATION_COUNT (일치)"
  exit 0
else
  echo "[check-bootstrap-labels-count] FAIL — dry-run output lines: $DRY_RUN_LINE_COUNT, create_label invocations: $INVOCATION_COUNT (불일치 — drift 가능성)" >&2
  exit 1
fi
