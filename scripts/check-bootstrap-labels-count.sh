#!/usr/bin/env bash
# check-bootstrap-labels-count.sh
# CFP-492 — bootstrap-labels.sh 2-way self-check lint.
# CFP-598 — 3-way parity 확장: §3 yaml hotfix-bypass:* row count 추가.
#
# 목적:
#   [2-way] dry-run stdout line count (stdout) == create_label 호출 횟수 (stderr "invocations: N")
#   [3-way] 위 2-way + §3 yaml hotfix-bypass:* row count (parse-hotfix-bypass-labels.py 출력 line count)
#
# 잠재적 drift: 신규 label 추가 시 create_label invocation 추가했으나
#               dry-run 출력 line 이 redirect / pipe 누락으로 count 불일치 발생 가능.
# 3-way 추가 drift: label-registry-v2.md §3 yaml row 추가 후
#                   bootstrap-labels.sh parse 분기 미반영 시 count mismatch.
#
# Usage:
#   bash scripts/check-bootstrap-labels-count.sh
#   bash scripts/check-bootstrap-labels-count.sh --help
#
# Exit codes:
#   0 = PASS (all parity checks pass)
#   1 = FAIL (drift detected: count mismatch)
#   2 = meta-error (bootstrap-labels.sh 부재 / 실행 실패 / stderr 패턴 미검출 / parser failure)

set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,25p' "$0" >&2
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_SCRIPT="$SCRIPT_DIR/bootstrap-labels.sh"
PARSER_SCRIPT="$SCRIPT_DIR/parse-hotfix-bypass-labels.py"
REGISTRY_MD="${REGISTRY_MD:-$SCRIPT_DIR/../docs/inter-plugin-contracts/label-registry-v2.md}"

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
if [[ "$DRY_RUN_LINE_COUNT" -ne "$INVOCATION_COUNT" ]]; then
  echo "[check-bootstrap-labels-count] FAIL (2-way) — dry-run output lines: $DRY_RUN_LINE_COUNT, create_label invocations: $INVOCATION_COUNT (불일치 — drift 가능성)" >&2
  exit 1
fi

# 3-way: §3 yaml hotfix-bypass:* row count (CFP-598)
YAML_HOTFIX_COUNT=0
if [[ -f "$PARSER_SCRIPT" && -f "$REGISTRY_MD" ]]; then
  if python -c "import yaml" 2>/dev/null; then
    # parser exit 2 = no entries (drift sentinel), exit 1/3 = meta-error
    parser_out=$(python "$PARSER_SCRIPT" "$REGISTRY_MD" 2>/dev/null) || {
      rc=$?
      if [[ $rc -eq 2 ]]; then
        YAML_HOTFIX_COUNT=0
      else
        echo "[check-bootstrap-labels-count] ERROR (3-way): parse-hotfix-bypass-labels.py 실패 (exit $rc)" >&2
        exit 2
      fi
    }
    if [[ -n "${parser_out:-}" ]]; then
      YAML_HOTFIX_COUNT="$(printf '%s\n' "$parser_out" | wc -l | tr -d ' ')"
    fi

    # dry-run 출력 안 hotfix-bypass:* line count
    DRY_HOTFIX_COUNT="$(grep -c 'hotfix-bypass:' "$TMP_STDOUT" 2>/dev/null || echo 0)"

    if [[ "$YAML_HOTFIX_COUNT" -ne "$DRY_HOTFIX_COUNT" ]]; then
      echo "[check-bootstrap-labels-count] FAIL (3-way) — yaml hotfix-bypass rows: $YAML_HOTFIX_COUNT, dry-run hotfix-bypass lines: $DRY_HOTFIX_COUNT (불일치 — bootstrap 미반영 drift)" >&2
      exit 1
    fi
    echo "[check-bootstrap-labels-count] PASS — dry-run lines: $DRY_RUN_LINE_COUNT, invocations: $INVOCATION_COUNT, yaml hotfix-bypass rows: $YAML_HOTFIX_COUNT, dry-run hotfix-bypass: $DRY_HOTFIX_COUNT (3-way 일치)"
  else
    # PyYAML 미설치 시 3-way skip (2-way PASS 만 보고)
    echo "[check-bootstrap-labels-count] PASS (2-way only — PyYAML 미설치, 3-way skip) — dry-run lines: $DRY_RUN_LINE_COUNT, invocations: $INVOCATION_COUNT"
  fi
else
  # parser 또는 registry 부재 시 2-way 만
  echo "[check-bootstrap-labels-count] PASS (2-way only — parser/registry 부재, 3-way skip) — dry-run lines: $DRY_RUN_LINE_COUNT, invocations: $INVOCATION_COUNT"
fi

exit 0
