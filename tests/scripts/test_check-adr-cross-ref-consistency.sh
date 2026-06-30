#!/usr/bin/env bats
# tests/scripts/test_check-adr-cross-ref-consistency.sh
# CFP-2478 Phase 2 — bats RED→GREEN discriminating fixture for check-adr-cross-ref-consistency.sh
#
# 계약 SSOT: layerA-contract.md §"bats fixture (QADev)" + Change Plan §8.1 TC-1~TC-6 + TC-3b
# CLI: bash scripts/check-adr-cross-ref-consistency.sh [--repo-root ROOT] [paths...]
#      (exit 0=PASS / 1=위반 / 2=setup)
#
# 중요 환경 요건:
#  - PYTHONIOENCODING=utf-8 필수 (Windows CP949 에서 한글 출력 UnicodeEncodeError 방지)
#  - --repo-root "$FX" 지정 필수 (기본 CWD=실제 워크트리라 archive/adr 가 실 ADR 로드됨)
#  - archive/adr 디렉터리 fixture 안에 존재해야 (a)(b) 검사 발동
#
# ─────────────────────────────────────────────────────────────────────────────
# Mutation 표 (어떤 구현 결함이 어느 TC 를 RED 로 만드는지)
# ─────────────────────────────────────────────────────────────────────────────
#
#  Mutation-A (TC-1): ENUM_SSOT['adr039_inline_whitelist_count'] 삭제 또는
#                     ordinal > count 검사 제거 → TC-1-RED 통과 = 결함 미검출
#
#  Mutation-B (TC-2): ENUM_SSOT['adr052_touchpoint'] 삭제 또는
#                     _TOUCHPOINT_PATTERN 제거 → TC-2-RED 통과 = stale enum 미검출
#
#  Mutation-C (TC-3): _CITATION_PATTERN 제거 또는 phantom-ID 검사 분기 제거
#                     → TC-3-RED 통과 = ADR-077 I-4 phantom 미검출
#
#  Mutation-D (TC-3b ★핵심): _I_DEFINE_PATTERN 을 행두-only (`^(I-\d+)`) 로 변경
#                     → ADR-068 `**I-7:**` bold-prefix 줄 미색인 → phantom 오판 → exit 1
#                     → TC-3b 가 exit 1(RED) 로 나오면 Mutation-D 결함 노출
#                     (정상 구현: prefix-허용 regex `^\s*(?:...|\*\*)?` → GREEN)
#
#  Mutation-E (TC-4): _check_content_anchor 로직 제거 (_QUOTED_TEXT_PATTERN scan 삭제)
#                     → TC-4-RED 통과 = 텍스트 부재 미검출
#
#  Mutation-F (TC-5/TC-6): 추상 주장에 finding emit 시 (INV-3 위반)
#                     → TC-5/TC-6 이 exit 1 로 나오면 over-extraction 결함 노출
#
# Exit code:
#  0 = all fixtures pass
#  1 = any fixture fails

# bats 1.13.0 — @test 형식, run + status/output 내장 변수 사용

# ─────────────────────────────────────────────────────────────────────────────
# setup_file: worktree 루트 + wrapper 경로 결정
# ─────────────────────────────────────────────────────────────────────────────
setup_file() {
  # BATS_TEST_DIRNAME = tests/scripts/
  export WT_ROOT
  WT_ROOT="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  export WRAPPER="${WT_ROOT}/scripts/check-adr-cross-ref-consistency.sh"
  # Windows CP949 환경 대응 — Python lib 한글 출력 UnicodeEncodeError 방지
  export PYTHONIOENCODING=utf-8
}

# ─────────────────────────────────────────────────────────────────────────────
# setup/teardown: 각 TC 마다 격리된 fixture-root mktemp
# ─────────────────────────────────────────────────────────────────────────────
setup() {
  FX=$(mktemp -d)
  export FX
  # (a)(b) 검사 발동 전제: archive/adr 디렉터리 실존
  mkdir -p "$FX/archive/adr"
  # dummy ADR 파일: load_existing_adrs 가 adr_dir 로드 성공하도록
  printf '# ADR-001 dummy\n' > "$FX/archive/adr/ADR-001-dummy.md"
}

teardown() {
  rm -rf "$FX"
}

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼: fixture-root 안에 파일 생성 (부모 디렉터리 자동 생성)
# write_fx <relative-path> <line1> [line2 ...]
# ─────────────────────────────────────────────────────────────────────────────
write_fx() {
  local rel="$1"; shift
  local path="$FX/$rel"
  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$@" > "$path"
}

# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼: 스크립트 실행 — --repo-root FX 지정 (ADR 디렉터리 격리)
# run_wrapper <paths...>
# ─────────────────────────────────────────────────────────────────────────────
run_wrapper() {
  run bash "$WRAPPER" --repo-root "$FX" "$@"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-1-RED: entry-count drift — "5번째 entry" (실 closed 4) → exit 1 + marker
#
# 검사 발동: (c) ENUM_SSOT['adr039_inline_whitelist_count']=4 + ordinal > count
# 결함 제거 시 GREEN 전환: "4번째 entry" 로 정정 → ordinal ≤ 4 → exit 0
# Mutation-A: ordinal-vs-count 검사 제거 시 이 TC 가 RED 로 통과 (결함 미검출)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-1-RED: entry-count drift — ADR-039 5번째 entry (실 closed 4) → exit 1" {
  write_fx "archive/adr/ADR-039-orchestrator-inline-whitelist.md" \
    "# ADR-039" \
    "" \
    "§결정 2 inline whitelist (closed, 4 entries):" \
    "1. 사용자 대화" \
    "2. TodoWrite" \
    "3. 읽기전용 Q&A" \
    "4. 상태 보고"

  # 인용 문서: ordinal 5 > closed 4
  write_fx "docs/stories/CFP-TEST-TC1-bad.md" \
    "# Test Story" \
    "" \
    "ADR-039 §결정 2 inline whitelist 의 5번째 entry 에 해당한다."

  run_wrapper "$FX"
  [ "$status" -eq 1 ]
  # finding marker: ordinal drift 관련 출력 (check=c, ordinal 관련)
  [[ "$output" =~ "ADR-039" ]] || [[ "$output" =~ "entry" ]] || \
    [[ "$output" =~ "ordinal" ]] || [[ "$output" =~ "5" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-1-GREEN: "4번째 entry" 로 정정 → exit 0
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-1-GREEN: entry-count drift 정정 — 4번째 entry → exit 0" {
  write_fx "archive/adr/ADR-039-orchestrator-inline-whitelist.md" \
    "# ADR-039" \
    "" \
    "§결정 2 inline whitelist (closed, 4 entries):" \
    "1. 사용자 대화" \
    "2. TodoWrite" \
    "3. 읽기전용 Q&A" \
    "4. 상태 보고"

  # 정정: "4번째 entry" — ordinal ≤ 4
  write_fx "docs/stories/CFP-TEST-TC1-ok.md" \
    "# Test Story" \
    "" \
    "ADR-039 §결정 2 inline whitelist 의 4번째 entry 에 해당한다."

  run_wrapper "$FX"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-2-RED: enum-literal drift — touchpoint <1..6> (정본 <1|2|3|4|5|6|7|8>) → exit 1
#
# 검사 발동: (c) ENUM_SSOT['adr052_touchpoint'] = '<1|2|3|4|5|6|7|8>' 대조
# 결함 제거 시 GREEN 전환: 정본 `<1|2|3|4|5|6|7|8>` 으로 교체 시 exit 0
# Mutation-B: enum 비교 로직 제거 시 이 TC 가 RED 로 통과 (stale 미검출)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-2-RED: enum-literal drift — touchpoint <1..6> stale → exit 1" {
  # ADR-052 fixture: 정본 SSOT 줄 (self-정의 → _TOUCHPOINT_SSOT_VALUE == token → skip)
  write_fx "archive/adr/ADR-052-codex-proactive-check.md" \
    "# ADR-052" \
    "" \
    "touchpoint: <1|2|3|4|5|6|7|8>"

  # 인용 문서: stale enum <1..6>
  write_fx "docs/stories/CFP-TEST-TC2-bad.md" \
    "# Test" \
    "" \
    "ADR-052 touchpoint <1..6> 항목을 대상으로 실행된다."

  run_wrapper "$FX"
  [ "$status" -eq 1 ]
  # enum drift finding marker
  [[ "$output" =~ "touchpoint" ]] || [[ "$output" =~ "enum" ]] || \
    [[ "$output" =~ "ADR-052" ]] || [[ "$output" =~ "1..6" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-2-GREEN: 정본 enum 일치 → exit 0
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-2-GREEN: enum-literal 정본 일치 — <1|2|3|4|5|6|7|8> → exit 0" {
  write_fx "archive/adr/ADR-052-codex-proactive-check.md" \
    "# ADR-052" \
    "" \
    "touchpoint: <1|2|3|4|5|6|7|8>"

  # 정본과 동일 형태 인용
  write_fx "docs/stories/CFP-TEST-TC2-ok.md" \
    "# Test" \
    "" \
    "ADR-052 touchpoint <1|2|3|4|5|6|7|8> 항목을 대상으로 실행된다."

  run_wrapper "$FX"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-3-RED: phantom ID — "ADR-077 I-4" (ADR-077 I-* set=∅) → exit 1
#
# 검사 발동: (b) phantom-ID — ADR-077 에 I-* 0개인데 I-4 인용
# 결함 제거 시 GREEN 전환: "ADR-068 I-4" 로 정정 + ADR-068 에 I-4 정의 시 exit 0
# Mutation-C: phantom-ID 검사 제거 시 이 TC 가 RED 로 통과 (phantom 미검출)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-3-RED: phantom ID — ADR-077 I-4 (ADR-077 I-* 없음) → exit 1" {
  # ADR-077 fixture: I-* 정의 0개
  write_fx "archive/adr/ADR-077-placeholder.md" \
    "# ADR-077" \
    "" \
    "이 ADR 에는 I-* 정의가 없다."

  # 인용 문서: ADR-077 I-4 phantom 인용
  write_fx "docs/stories/CFP-TEST-TC3-bad.md" \
    "# Test" \
    "" \
    "ADR-077 I-4 에 따라 cross-module propagation 을 검증한다."

  run_wrapper "$FX"
  [ "$status" -eq 1 ]
  # phantom finding marker
  [[ "$output" =~ "ADR-077" ]] || [[ "$output" =~ "I-4" ]] || \
    [[ "$output" =~ "phantom" ]] || [[ "$output" =~ "소유" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-3-GREEN: phantom 정정 — ADR-068 I-4 (ADR-068 에 I-4 실소유) → exit 0
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-3-GREEN: phantom ID 정정 — ADR-068 I-4 실소유 → exit 0" {
  # ADR-068 fixture: I-4 정의 bold prefix 형태 (실 ADR-068 패턴)
  write_fx "archive/adr/ADR-068-cross-module-propagation-invariant.md" \
    "# ADR-068" \
    "" \
    "**I-1:** 재현성 invariant" \
    "**I-2:** 추출 정확성" \
    "**I-3:** completeness" \
    "**I-4:** disjoint 무중복" \
    "**I-5:** empirical grounding"

  # 정정된 인용: ADR-068 I-4
  write_fx "docs/stories/CFP-TEST-TC3-ok.md" \
    "# Test" \
    "" \
    "ADR-068 I-4 에 따라 cross-module propagation 을 검증한다."

  run_wrapper "$FX"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-3b ★ cry-wolf 차단: "ADR-068 I-7" bold prefix `**I-7:**` 정의 → exit 0 (GREEN 의무)
#
# 이 TC 가 CFP-2478 Mutation-D 핵심 discriminating 케이스:
#   - 행두-only grep (`^I-7`) 구현 → `**I-7:**` 줄 미색인 → phantom 오판 → exit 1 (FAIL)
#   - prefix-허용 regex `^\s*(?:[-*]\s+|#{1,6}\s+|\|\s*|\*\*)?(I-\d+)` 구현 → GREEN
# 만약 스크립트가 행두-only 이면 이 TC 가 exit 1 로 나타나 Mutation-D 결함 노출.
# 결함 제거 시 GREEN: _I_DEFINE_PATTERN 이 bold prefix 형태를 허용하면 GREEN.
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-3b: prefix-form 실소유 cry-wolf 차단 — ADR-068 I-7 bold prefix → exit 0 (GREEN)" {
  # ADR-068 fixture: I-7 을 bold `**I-7:**` prefix 형태로 정의 (실 ADR-068 I-1~I-8 패턴)
  write_fx "archive/adr/ADR-068-cross-module-propagation-invariant.md" \
    "# ADR-068" \
    "" \
    "**I-1:** 재현성" \
    "**I-2:** 추출 정확성" \
    "**I-3:** completeness" \
    "**I-4:** disjoint 무중복" \
    "**I-5:** empirical grounding" \
    "**I-6:** layer boundary" \
    "**I-7:** Tier D QADev test-assert-time" \
    "**I-8:** 측정 assertion 위치 명시"

  # 인용 문서: ADR-068 I-7
  write_fx "docs/stories/CFP-TEST-TC3b.md" \
    "# Test" \
    "" \
    "ADR-068 I-7 에 따라 Tier D QADev 검증을 수행한다."

  run_wrapper "$FX"
  # GREEN 의무: prefix-허용 grep 이면 I-7 ∈ owned set → exit 0
  # 실패(exit 1) 시 = 행두-only grep 결함 노출 = Mutation-D
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-4-RED: content-anchor drift — 인용 텍스트가 대상 file 부재 → exit 1
#
# 검사 발동: (e) content-anchor — 큰따옴표 인용구 (8+ chars) + (path) 참조
#            → target = Path(path_only) → path 가 실존할 때만 grep
#            → 인용 텍스트가 target 파일에 없으면 finding
#
# 결함 제거 시 GREEN 전환: 인용 텍스트가 대상 파일에 실존하면 exit 0
# Mutation-E: _check_content_anchor 로직 제거 시 이 TC 가 RED 로 통과 (미검출)
#
# fixture 설계: Python lib 이 Windows POSIX path (/tmp/...) 를 pathlib.Path() 로
#   변환 시 Windows 백슬래시 경로로 resolve — is_file()=False 로 path 실존 확인 실패.
#   이 TC 는 스크립트 구현 결함 (Windows POSIX path 미지원)을 노출하는 discriminating TC.
#
# ★ 스크립트 결함 분류: Windows 환경에서 mktemp POSIX path (/tmp) 가 Python pathlib.Path()
#   에서 Windows 경로로 오변환 → is_file()=False → (e) 검사 skip → exit 0 (false-negative).
#   --self-test 에서는 Python 인라인 fixture 가 pathlib 없이 직접 is-file 확인해서 동작.
#   이 TC 가 현재 RED(exit 0 ≠ expected 1) 인 이유 = 스크립트 결함, 아래 TC 는 스크립트
#   수정(Windows path 정규화) 후 GREEN 전환 대상.
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-4-RED: content-anchor drift — 인용 텍스트 대상 file 부재 → exit 1" {
  # 대상 파일: 짧은 내용 (인용 텍스트 없음)
  local target_path="$FX/docs/domain-knowledge/concept/policy-propagation.md"
  write_fx "docs/domain-knowledge/concept/policy-propagation.md" \
    "# Policy Propagation" \
    "" \
    "이 문서는 정책 전파 채널을 설명한다."

  # 인용 문서: 존재하지 않는 긴 인용 텍스트 (8+ chars) + 절대경로 참조
  write_fx "docs/stories/CFP-TEST-TC4-bad.md" \
    "# Test" \
    "" \
    "설계 결정은 \"존재하지않는긴인용텍스트입니다\" ($target_path) 를 따른다."

  run_wrapper "$FX"
  # 스크립트 Windows POSIX path 수정 후 exit 1 기대.
  # 현재 Windows 환경에서 pathlib.Path('/tmp/...').is_file()=False 로 skip → exit 0 (스크립트 결함).
  [ "$status" -eq 1 ]
  # content-anchor finding marker
  [[ "$output" =~ "anchor" ]] || [[ "$output" =~ "content" ]] || \
    [[ "$output" =~ "존재하지" ]] || [[ "$output" =~ "policy-propagation" ]] || \
    [[ "$output" =~ "(e)" ]] || [[ "$output" =~ "(E)" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-4-GREEN: content-anchor 실존 — 인용 텍스트 대상 file 존재 → exit 0
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-4-GREEN: content-anchor 실존 — 인용 텍스트 대상 file 존재 → exit 0" {
  # 대상 파일: 인용 텍스트 포함
  local target_path="$FX/docs/domain-knowledge/concept/policy-propagation.md"
  write_fx "docs/domain-knowledge/concept/policy-propagation.md" \
    "# Policy Propagation" \
    "" \
    "overlay 주입 방식을 사용한다."

  # 인용 문서: 실존 텍스트 + 절대경로 참조
  write_fx "docs/stories/CFP-TEST-TC4-ok.md" \
    "# Test" \
    "" \
    "설계 결정은 \"overlay 주입 방식을 사용한다\" ($target_path) 를 따른다."

  run_wrapper "$FX"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-5: over-extraction 차단 — abstract/inferred 주장만 (verbatim cross-ref 0)
#       → finding 0 (exit 0)
#
# layer A 는 verbatim grep 만 수행 (추론 주장 skip = INV-3 over-extraction 차단)
# Mutation-F: abstract 주장에 finding emit 시 이 TC 가 exit 1 로 나와 결함 노출
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-5: over-extraction 차단 — abstract inferred 주장 → finding 0 (exit 0)" {
  # abstract 주장만 — ADR-NNN 인용·enum 리터럴·quoted anchor 없음
  write_fx "docs/stories/CFP-TEST-TC5.md" \
    "# Test" \
    "" \
    "이 변경은 전반적인 모듈성을 향상시키고 시스템 결합도를 낮춘다." \
    "레이어 간 의존성이 줄어들어 유지보수성이 개선될 것이다." \
    "설계 원칙에 따라 경계를 명확히 한다."

  run_wrapper "$FX"
  # layer A 는 abstract 주장에 finding 안 냄 → exit 0
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-6: abstention — "모듈성 향상" 류 추상 주장만 → skip (exit 0)
#       cry-wolf 차단 (INV-3)
#
# Mutation-F: over-extraction 시 exit 1 로 나와 결함 노출
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-6: abstention — 추상 주장 모듈성 향상 → skip exit 0 (cry-wolf 차단)" {
  # 추상 주장 — cross-ADR 인용 없음, enum 토큰 없음, quoted path ref 없음
  mkdir -p "$FX/docs/change-plans"
  write_fx "docs/change-plans/CFP-TEST-abstract.md" \
    "# Change Plan CFP-TEST" \
    "" \
    "§1 요약" \
    "본 변경은 모듈성 향상을 목적으로 한다." \
    "" \
    "§2 동기" \
    "현재 구조는 결합도가 높아 유지보수성이 떨어진다." \
    "리팩터링을 통해 독립성을 높인다." \
    "" \
    "§3 결정" \
    "공통 인터페이스를 추출하고 의존성을 역전시킨다."

  run_wrapper "$FX"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# 보조 TC: ADR 파일 부재 시 (a) finding — exit 1
# --repo-root FX 지정 + archive/adr 에 ADR-001 만 존재 → ADR-099 부재 → finding
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-aux-ADR-absent: archive/adr 에 ADR-099 부재 → exit 1 (a) finding" {
  # setup 에서 ADR-001-dummy.md 이미 생성 (ADR-099 는 없음)
  write_fx "docs/stories/CFP-TEST-absent.md" \
    "# Test" \
    "" \
    "ADR-099 참조한다."

  run_wrapper "$FX/docs/stories/CFP-TEST-absent.md"
  # ADR-099 파일 부재 → (a) finding → exit 1
  [ "$status" -eq 1 ]
  [[ "$output" =~ "ADR-099" ]] || [[ "$output" =~ "부재" ]] || \
    [[ "$output" =~ "(a)" ]] || [[ "$output" =~ "(A)" ]]
}

# ─────────────────────────────────────────────────────────────────────────────
# 보조 TC: sentinel ADR (>=900) 는 (a)(b) skip — finding 미발생 (exit 0)
# L1_SENTINEL_THRESHOLD = 900
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-aux-sentinel-skip: sentinel ADR-900 인용 → (a)(b) skip → exit 0" {
  # ADR-900 파일 없음 — sentinel 번호 ≥ 900 → skip
  write_fx "docs/stories/CFP-TEST-sentinel.md" \
    "# Test" \
    "" \
    "ADR-900 §결정 1 는 테스트 전용 sentinel 번호이다."

  run_wrapper "$FX"
  # sentinel skip → finding 없음 → exit 0
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# 보조 TC: tests/** path 는 (a)(b) 검사 제외 (INV-4 disjoint + L1_EXEMPT_PATH_PARTS)
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-aux-tests-skip: tests/ 안 phantom 인용 → (a)(b) skip → exit 0" {
  # ADR-088 파일: I-* 없음
  write_fx "archive/adr/ADR-088-deploy-lane.md" \
    "# ADR-088" \
    "" \
    "배포 레인 정의."

  # tests/ 경로에 있는 파일은 L1_EXEMPT_PATH_PARTS('tests') 에 의해 (a)(b) skip
  write_fx "tests/unit/test_something.md" \
    "# Unit Test" \
    "" \
    "ADR-088 I-99 는 테스트용 phantom 인용이다."

  run_wrapper "$FX"
  # tests/** skip → finding 없음 → exit 0
  [ "$status" -eq 0 ]
}

# ─────────────────────────────────────────────────────────────────────────────
# 보조 TC: INV-1 재현성 — 동일 입력 2회 실행 = 동일 exit code
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-inv1-reproducibility: 동일 입력 2회 = 동일 exit code" {
  # 위반 있는 fixture (TC-2 RED 패턴)
  write_fx "archive/adr/ADR-052-codex-proactive-check.md" \
    "# ADR-052" \
    "touchpoint: <1|2|3|4|5|6|7|8>"

  write_fx "docs/stories/CFP-TEST-repro.md" \
    "# Test" \
    "" \
    "ADR-052 touchpoint <1..6> 항목을 대상으로 실행된다."

  run_wrapper "$FX"
  local first_status="$status"

  run_wrapper "$FX"
  # 동일 exit code 의무 (INV-1 재현성)
  [ "$status" -eq "$first_status" ]
}

# ─────────────────────────────────────────────────────────────────────────────
# 보조 TC: --self-test flag — exit 0 (Python inline fixture 전 GREEN)
# PYTHONIOENCODING=utf-8 환경에서 --self-test 실행
# ─────────────────────────────────────────────────────────────────────────────
@test "TC-self-test: --self-test flag → exit 0" {
  run bash "$WRAPPER" --self-test
  [ "$status" -eq 0 ]
}
