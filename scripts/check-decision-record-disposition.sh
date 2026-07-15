#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# scripts/check-decision-record-disposition.sh
# CFP-2697 / Epic #2696 (canary artifact D6) — decision-record cardinal disposition CLI.
#
# born-alive: 두 pure 모듈(decision_record_disposition.py / reference_integrity_guard.py)을
#   실제로 import·구동하는 실행 가능 CLI. 3 모드.
#
# 모드:
#   (default) --self-apply [FILE...]      : oracle census — 각 `N-tuple`/cardinal 라인을 분류,
#                                           조치-필요(un-dispositioned present-normative) 잔여를 리포트.
#                                           PL 이 in-file split-brain=0 dogfood 에 사용.
#   --guard --target F --row R --disposition D : reference-integrity 4-check, exit 0/1.
#   --smoke                               : 두 모듈 import + classify() on 5 표준 literal
#                                           (P-1/2/3→correct, N-1 homonym→no_action, N-2 dated→no_action).
#
# anti-overfit: 분류 로직은 python 모듈이 라인 FEATURE 로만 판정한다. 본 CLI 는 fixture 신원
#   하드코딩 없이 파일 목록을 데이터로 넘길 뿐이다(default target set 은 governance config).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export PYTHONIOENCODING=utf-8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIB="${SCRIPT_DIR}/lib"
ORACLE="${LIB}/decision_record_disposition.py"
GUARD="${LIB}/reference_integrity_guard.py"
PY="${PYTHON:-python}"

die() { echo "ERROR: $*" >&2; exit 2; }

[ -f "${ORACLE}" ] || die "oracle 모듈 부재: ${ORACLE}"
[ -f "${GUARD}" ] || die "guard 모듈 부재: ${GUARD}"

MODE="self-apply"
TARGET=""
ROW=""
DISPOSITION=""
STRICT=0
FILES=()

while [ $# -gt 0 ]; do
  case "$1" in
    --smoke)       MODE="smoke"; shift ;;
    --guard)       MODE="guard"; shift ;;
    --self-apply)  MODE="self-apply"; shift ;;
    --target)      TARGET="${2:-}"; shift 2 ;;
    --row)         ROW="${2:-}"; shift 2 ;;
    --disposition) DISPOSITION="${2:-}"; shift 2 ;;
    --strict)      STRICT=1; shift ;;
    -h|--help)
      echo "usage: $0 [--self-apply [FILE...]] | --guard --target F --row R --disposition D | --smoke"
      exit 0 ;;
    --) shift; while [ $# -gt 0 ]; do FILES+=("$1"); shift; done ;;
    -*) die "알 수 없는 옵션: $1" ;;
    *)  FILES+=("$1"); shift ;;
  esac
done

# ─────────────────────────────────────────────────────────────────────────────
# smoke — 두 모듈 import + 5 표준 literal classify
# ─────────────────────────────────────────────────────────────────────────────
if [ "${MODE}" = "smoke" ]; then
  "${PY}" - "${LIB}" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import decision_record_disposition as oracle          # 모듈 ① import (born-alive)
import reference_integrity_guard as guard             # 모듈 ② import (born-alive)
assert callable(oracle.classify) and callable(guard.run_guard)
rc = 0
for label, text, expected in oracle.SMOKE_CASES:      # 5 inline literal (SSOT)
    got = oracle.classify(text)["disposition"]
    ok = "OK" if got == expected else "MISMATCH"
    if got != expected:
        rc = 1
    print("[%s] expect=%s got=%s %s :: %s" % (label, expected, got, ok, text))
sys.exit(rc)
PY
  exit $?
fi

# ─────────────────────────────────────────────────────────────────────────────
# guard — reference-integrity 4-check
# ─────────────────────────────────────────────────────────────────────────────
if [ "${MODE}" = "guard" ]; then
  [ -n "${TARGET}" ] || die "--guard 는 --target 필요"
  [ -n "${DISPOSITION}" ] || die "--guard 는 --disposition 필요"
  "${PY}" "${GUARD}" --guard \
    --target "${TARGET}" \
    --row "${ROW}" \
    --disposition "${DISPOSITION}" \
    --repo-root "${REPO_ROOT}"
  exit $?
fi

# ─────────────────────────────────────────────────────────────────────────────
# self-apply — oracle census (default)
# ─────────────────────────────────────────────────────────────────────────────
if [ "${#FILES[@]}" -eq 0 ]; then
  # default target set (governance decision-record 파일 — 신원 하드코딩 아닌 census config).
  DEFAULT_FILES=("${REPO_ROOT}/CLAUDE.md" "${REPO_ROOT}/docs/security/branch-protection-audit.md")
  for f in "${DEFAULT_FILES[@]}"; do
    [ -f "$f" ] && FILES+=("$f")
  done
  # 모든 ADR 파일 추가(oracle 은 `N-tuple` 라인만 분류하므로 스캔 안전).
  if [ -d "${REPO_ROOT}/archive/adr" ]; then
    while IFS= read -r adr; do FILES+=("$adr"); done \
      < <(find "${REPO_ROOT}/archive/adr" -name 'ADR-*.md' -type f | sort)
  fi
fi

[ "${#FILES[@]}" -gt 0 ] || die "census 대상 파일 없음"

STRICT_ARG=()
[ "${STRICT}" -eq 1 ] && STRICT_ARG=(--strict)

# oracle census: stdout=JSON report (조치-필요 present-normative cardinal 잔여), stderr=SUMMARY 1줄.
# exit 0(리포트) / --strict 시 잔여>0 이면 exit 1.
CENSUS_RC=0
"${PY}" "${ORACLE}" --census "${STRICT_ARG[@]}" "${FILES[@]}" || CENSUS_RC=$?
exit "${CENSUS_RC}"
