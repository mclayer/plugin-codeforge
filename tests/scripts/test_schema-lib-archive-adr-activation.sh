#!/usr/bin/env bash
# tests/scripts/test_schema-lib-archive-adr-activation.sh
# CFP-2523 / 설계 §8 Test Contract — schema-lib archive/adr existence-guard dead-path 활성 회귀 검증.
# 선행 동형: CFP-2519 test_adr-path-dead-path-sweep.sh (functional 서브클래스) → 본 Story = existence-guard 서브클래스.
#
# 대상 lib 2종 (dict 키 + `Path(prefix).exists()` 순회 = existence-guard 서브클래스):
#   scripts/lib/check_doc_frontmatter.py     — REQUIRED["archive/adr"] 키
#   scripts/lib/check_doc_section_schema.py   — REQUIRED_SECTIONS["archive/adr"] 키
#
# AC 매핑 (Story §5.1):
#   AC-4.1(a) symmetric fixture consumer (docs/adr valid)  → test_*_symmetric_consumer (TC-1)
#   AC-4.1(b) symmetric fixture wrapper  (archive/adr valid)→ test_*_symmetric_wrapper  (TC-2)
#   AC-4.2    ★키-제거 mutation (green-but-dead 봉인)        → test_*_key_removal_mutation (TC-3)
#   AC-4.3    backfill 회귀 (delimiter / heading 역전)        → test_fm_delimiter_regression (TC-4)
#                                                              test_sec_heading_regression  (TC-5)
#
# ★핵심 함정 봉인 (설계 §8.3 lib-exercise 의무):
#   existence-guard 는 `Path(prefix).exists()` + `REQUIRED.items()` 순회 계층이다. 단순 fixture
#   문자열 매칭이 아니라 lib 을 격리 temp CWD(archive/adr↔docs/adr fixture tree 포함)에서 실제
#   실행해 dict 키 추가/제거가 rglob 발동 여부까지 end-to-end exercise 한다.
#   ★fixture 는 archive/adr/ 경로 거주 필수 — 그래야 활성된 키가 도달한다.
#   ★TC-3(키-제거)이 핵심: 키 제거 시 wrapper ADR 이 다시 silent skip → invalid fixture 가
#   검증 안 됨 = 활성 되돌림이 RED 로 잡혀야 한다(mutant SURVIVED = green-but-dead = 차단).
#
# anti-theater: always-pass·tautology 0 — 각 mutation 시 RED 전환되는 load-bearing assert 만.
#   diff -q no-op guard 로 sed 미반영(vacuous 통과) 차단 (#2514 교훈 상속).
# set -e 미사용 — 각 test || true 로 partial run 허용, FAIL 카운터 집계 후 exit code 결정.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"
FM_LIB="$LIB_DIR/check_doc_frontmatter.py"
SEC_LIB="$LIB_DIR/check_doc_section_schema.py"

PYTHON="${PYTHON:-python}"
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON="python3"

PASS=0
FAIL=0

# ─── valid ADR fixture body (5 frontmatter 필드 + 5 required 섹션) ───
write_valid_adr() {
  # arg1 = 대상 .md 절대경로
  cat > "$1" <<'ADREOF'
---
adr_number: 999
title: Fixture ADR for schema-lib activation test
status: Accepted
category: governance
date: 2026-06-30
---

# ADR-999: Fixture ADR

## 상태

Accepted (fixture).

## 컨텍스트

Fixture context body.

## 결정

Fixture decision body.

## 결과

Fixture consequence body.

## 관련 파일

- `scripts/lib/check_doc_frontmatter.py`
ADREOF
}

# ─── invalid ADR fixture — frontmatter closing `---` 부재 (ADR-042-mc 형 결함 재현) ───
write_invalid_fm_adr() {
  # 종결 델리미터 없이 본문이 frontmatter 로 흡수 → yaml.safe_load 가 `**` invalid alias → ScannerError
  cat > "$1" <<'ADREOF'
---
adr_number: 998
title: Fixture invalid frontmatter (no closing delimiter)
status: Accepted
category: governance
date: 2026-06-30

# ADR-998: Fixture invalid

본문 시작 — **Accepted** markdown alias 가 frontmatter 로 흡수되어 yaml ScannerError 유발.

## 상태

x

## 컨텍스트

x

## 결정

x

## 결과

x

## 관련 파일

x
ADREOF
}

# ─── invalid ADR fixture — required 섹션 누락 (`## 관련 파일` 부재) ───
write_invalid_sec_adr() {
  cat > "$1" <<'ADREOF'
---
adr_number: 997
title: Fixture invalid section (missing 관련 파일)
status: Accepted
category: governance
date: 2026-06-30
---

# ADR-997: Fixture invalid section

## 상태

x

## 컨텍스트

x

## 결정

x

## 결과

x
ADREOF
}

# ─── lib 실행 helper — 격리 temp CWD 에서 (mutated 가능) lib 실행, exit code stdout 반환 ───
# arg1 = lib 절대경로 (원본 또는 mutated), arg2 = 실행할 sandbox 디렉터리(CWD)
run_lib_exit() {
  local lib_path="$1" sandbox="$2"
  ( cd "$sandbox" && "$PYTHON" "$lib_path" >/dev/null 2>&1 )
  echo "$?"
}

# ─── archive/adr 키 제거 mutant lib 생성 (활성 되돌림) ───
# fm: REQUIRED 의 archive/adr 1줄 제거. sec: REQUIRED_SECTIONS 의 archive/adr 5줄 블록 제거.
make_fm_key_removed() {
  # arg1 = 원본 fm lib, arg2 = 대상 mutant 경로
  sed '/^    "archive\/adr":       {"adr_number", "title", "status", "category", "date"},$/d' "$1" > "$2"
}
make_sec_key_removed() {
  # arg1 = 원본 sec lib, arg2 = 대상 mutant 경로. archive/adr 키 + 5 패턴 + 닫는 ], = 7줄 블록 제거.
  "$PYTHON" - "$1" "$2" <<'PYEOF'
import sys, re
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
# "archive/adr": [ ... 5 patterns ... ], 블록 제거 (non-greedy, 한 occurrence)
pattern = re.compile(
    r'    "archive/adr": \[\n'
    r'        r"\^## 상태",\n'
    r'        r"\^## 컨텍스트",\n'
    r'        r"\^## 결정",\n'
    r'        r"\^## 결과",\n'
    r'        r"\^## 관련 파일",\n'
    r'    \],\n'
)
new, n = pattern.subn("", text, count=1)
if n != 1:
    sys.stderr.write(f"MUTATION_DEFINITION_ERROR: archive/adr block not matched (n={n})\n")
    sys.exit(2)
open(dst, "w", encoding="utf-8").write(new)
PYEOF
}

# ════════════════════════════════════════════════════════════════════════════
# TC-1 — symmetric fixture (consumer docs/adr valid) → 양 lib PASS (기존 동작 보존)
# ════════════════════════════════════════════════════════════════════════════
test_symmetric_consumer() {
  local n="TC-1-symmetric-consumer"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/docs/adr"
  write_valid_adr "$sbx/docs/adr/ADR-999-fixture.md"
  local fm_exit sec_exit
  fm_exit=$(run_lib_exit "$FM_LIB" "$sbx")
  sec_exit=$(run_lib_exit "$SEC_LIB" "$sbx")
  rm -rf "$sbx"
  if [ "$fm_exit" -eq 0 ] && [ "$sec_exit" -eq 0 ]; then
    echo "PASS: $n -- docs/adr valid fixture 검증 진입 후 PASS (fm=$fm_exit sec=$sec_exit) — consumer 기존 동작 보존"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- fm_exit=$fm_exit sec_exit=$sec_exit (기대 0/0)"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# TC-2 — symmetric fixture (wrapper archive/adr valid) → 양 lib PASS (신규 커버)
# ════════════════════════════════════════════════════════════════════════════
test_symmetric_wrapper() {
  local n="TC-2-symmetric-wrapper"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/archive/adr"
  write_valid_adr "$sbx/archive/adr/ADR-999-fixture.md"
  local fm_exit sec_exit
  fm_exit=$(run_lib_exit "$FM_LIB" "$sbx")
  sec_exit=$(run_lib_exit "$SEC_LIB" "$sbx")
  rm -rf "$sbx"
  if [ "$fm_exit" -eq 0 ] && [ "$sec_exit" -eq 0 ]; then
    echo "PASS: $n -- archive/adr valid fixture 검증 진입 후 PASS (fm=$fm_exit sec=$sec_exit) — 활성 키가 wrapper ADR 커버"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- fm_exit=$fm_exit sec_exit=$sec_exit (기대 0/0) — archive/adr 키 미활성 의심"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# TC-3 — ★키-제거 mutation (green-but-dead 봉인 핵심)
#   invalid archive/adr 픽스처를 두고: 키 present → lib FAIL(exit 1, 잡음) / 키 removed →
#   lib silent skip(exit 0, mutant SURVIVED = dead). 키가 load-bearing 임을 입증.
# ════════════════════════════════════════════════════════════════════════════
test_fm_key_removal_mutation() {
  local n="TC-3-fm-key-removal-mutation"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/archive/adr"
  write_invalid_fm_adr "$sbx/archive/adr/ADR-bad.md"

  # (a) 키 present (현행 활성 lib) → invalid fixture 잡힘 = exit 1
  local exit_present; exit_present=$(run_lib_exit "$FM_LIB" "$sbx")

  # (b) 키 removed (mutation = 활성 되돌림)
  local mdir mlib; mdir="$(mktemp -d)"; mlib="$mdir/lib.py"
  make_fm_key_removed "$FM_LIB" "$mlib"
  local mutated=0
  if diff -q "$FM_LIB" "$mlib" >/dev/null 2>&1; then
    echo "FAIL: $n -- sed no-op (archive/adr REQUIRED 키 라인 미제거 — mutant 정의 오류)"
    FAIL=$((FAIL+1)); rm -rf "$sbx" "$mdir"; return
  fi
  mutated=1
  local exit_removed; exit_removed=$(run_lib_exit "$mlib" "$sbx")
  rm -rf "$sbx" "$mdir"

  # 기대: present=1 (invalid 잡음) / removed=0 (silent skip = 키가 load-bearing)
  if [ "$exit_present" -eq 1 ] && [ "$exit_removed" -eq 0 ] && [ "$mutated" -eq 1 ]; then
    echo "PASS: $n -- mutant KILLED (키 present exit=1 invalid 검출 / 키 removed exit=0 silent skip = archive/adr 키 load-bearing, green-but-dead 봉인)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- exit_present=$exit_present exit_removed=$exit_removed (기대 1/0 — present 가 0 이면 fixture 가 invalid 아님 / removed 가 1 이면 키 제거가 다른 경로로 잡힘=mutant 정의 오류)"
    FAIL=$((FAIL+1))
  fi
}

test_sec_key_removal_mutation() {
  local n="TC-3-sec-key-removal-mutation"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/archive/adr"
  write_invalid_sec_adr "$sbx/archive/adr/ADR-bad.md"

  local exit_present; exit_present=$(run_lib_exit "$SEC_LIB" "$sbx")

  local mdir mlib; mdir="$(mktemp -d)"; mlib="$mdir/lib.py"
  make_sec_key_removed "$SEC_LIB" "$mlib"
  if diff -q "$SEC_LIB" "$mlib" >/dev/null 2>&1; then
    echo "FAIL: $n -- sed/py no-op (archive/adr REQUIRED_SECTIONS 블록 미제거 — mutant 정의 오류)"
    FAIL=$((FAIL+1)); rm -rf "$sbx" "$mdir"; return
  fi
  local exit_removed; exit_removed=$(run_lib_exit "$mlib" "$sbx")
  rm -rf "$sbx" "$mdir"

  if [ "$exit_present" -eq 1 ] && [ "$exit_removed" -eq 0 ]; then
    echo "PASS: $n -- mutant KILLED (키 present exit=1 섹션누락 검출 / 키 removed exit=0 silent skip = archive/adr 키 load-bearing, green-but-dead 봉인)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- exit_present=$exit_present exit_removed=$exit_removed (기대 1/0)"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# TC-4 — frontmatter backfill 회귀 (ADR-042-mc closing `---` 제거 시 ScannerError 포착)
# ════════════════════════════════════════════════════════════════════════════
test_fm_delimiter_regression() {
  local n="TC-4-fm-delimiter-regression"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/archive/adr"
  # valid (closing delimiter 有) → PASS, invalid (delimiter 부재) → FAIL 양쪽 대조
  write_valid_adr "$sbx/archive/adr/ADR-good.md"
  local exit_good; exit_good=$(run_lib_exit "$FM_LIB" "$sbx")
  # 이제 delimiter-부재 fixture 추가 → 회귀
  write_invalid_fm_adr "$sbx/archive/adr/ADR-nodelim.md"
  local exit_bad; exit_bad=$(run_lib_exit "$FM_LIB" "$sbx")
  rm -rf "$sbx"
  if [ "$exit_good" -eq 0 ] && [ "$exit_bad" -eq 1 ]; then
    echo "PASS: $n -- closing delimiter 有 exit=0 / 부재(역전) exit=1 = backfill 회귀(ADR-042-mc 형 결함) 포착"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- exit_good=$exit_good exit_bad=$exit_bad (기대 0/1)"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# TC-5 — section backfill 회귀 (표준 heading 역전 / 누락 시 section lib 포착)
# ════════════════════════════════════════════════════════════════════════════
test_sec_heading_regression() {
  local n="TC-5-sec-heading-regression"
  local sbx; sbx="$(mktemp -d)"
  mkdir -p "$sbx/archive/adr"
  write_valid_adr "$sbx/archive/adr/ADR-good.md"
  local exit_good; exit_good=$(run_lib_exit "$SEC_LIB" "$sbx")
  # heading 역전: `## 관련 파일` 누락 fixture (backfill 되돌림)
  write_invalid_sec_adr "$sbx/archive/adr/ADR-missing-heading.md"
  local exit_bad; exit_bad=$(run_lib_exit "$SEC_LIB" "$sbx")
  rm -rf "$sbx"
  if [ "$exit_good" -eq 0 ] && [ "$exit_bad" -eq 1 ]; then
    echo "PASS: $n -- 표준 heading 完備 exit=0 / 누락(역전) exit=1 = backfill 회귀(heading drift) 포착"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- exit_good=$exit_good exit_bad=$exit_bad (기대 0/1)"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2523 Phase 2: schema-lib archive/adr existence-guard dead-path 활성 회귀 검증"
echo "symmetric fixture + ★키-제거 mutation(green-but-dead 봉인) + backfill 회귀 — CFP-2519 후속"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

test_symmetric_consumer       || true; echo ""
test_symmetric_wrapper        || true; echo ""
test_fm_key_removal_mutation  || true; echo ""
test_sec_key_removal_mutation || true; echo ""
test_fm_delimiter_regression  || true; echo ""
test_sec_heading_regression   || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED"
  exit 0
else
  echo "Some tests FAILED"
  exit 1
fi
