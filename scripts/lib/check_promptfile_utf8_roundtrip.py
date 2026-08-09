#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2884 / ADR-081 §결정 D16 — Codex promptfile UTF-8 round-trip / 언어 구획 검증 helper (SSOT)
# CFP-2911 / ADR-081 §결정 D17 — prompt-injection 방어층 강화 (nonce 불가측성·delimiter 블록 개수/terminal·
#   술어 협착·판독측 지시 기계강제). D16(언어 축)과 disjoint 한 injection 축.
# ADR-061 §결정 1 Python-SSOT 패턴 (scripts/lib check_* 관례). "cp949 회피 = 명시 encoding='utf-8'" 는
#   ADR-061 본문 §결정이 아니라 그로부터 파생된 scripts/lib de facto 관행 (동 디렉터리 495건 실측) — 동일 원리의 새 적용처.
# ADR-170 §결정 21 (= §결정 2 표 entry 7) 동형 승계 — "argv 는 ASCII path 만, 한국어 실값·content 는 UTF-8 파일 내부".
#   argv 축은 ADR-081 §결정 D8 file-redirect 가 기차단하고, 본 helper 가 파일 **내용** 축을 완결한다.
#   nonce 는 hex(ASCII) 라 argv 안전 (emit-nonce 발급 → dispatch --nonce argv 전달).
#
# 구현 상태 = 본구현 (CFP-2884 Phase 2 + CFP-2911 Phase 2). 아래 docstring 의 CLI 계약이 **확정본 SSOT** 이며
#   본 파일 코드가 그 이행이다 (계약 변경 = Change Plan 개정 경유). 표준 라이브러리만 사용 (ADR-061 scripts/lib 관례).
"""Codex promptfile UTF-8 round-trip / 언어 구획 / prompt-injection 방어 검증 helper.

promptfile 조립 계층(L0-L1)에서 "쓴 것과 읽은 것이 같은가"(축 A) 와 "injection 방어층이 계약대로
배선됐는가"(축 injection) 를 fail-closed 로 판정한다. byte 문법 유효성 검사 단독은 금지 — cp949 오해석
재인코딩 산출물은 **valid UTF-8 인 채로 내용만** 오염되므로 문법 검사를 그대로 통과한다 (CFP-2884 발단
사고가 실증). 구분자 블록 개수 미검증·bare-substring sentinel 판정·판독측 지시 미강제는 각각 구획탈출·
born-broken 자기차단·Spotlighting 반쪽 방어를 낳는다 (CFP-2911 #2910 P1 3건이 실증).

════════════════════════════════════════════════════════════════════════════════
CLI
════════════════════════════════════════════════════════════════════════════════

    check_promptfile_utf8_roundtrip.py --mode write      --out <path> --whitelist <path> --nonce <str>
    check_promptfile_utf8_roundtrip.py --mode verify     --in  <path> --whitelist <path> [--nonce <str>]
    check_promptfile_utf8_roundtrip.py --mode emit-nonce

  --mode {write,verify,emit-nonce}   판정/발급 모드 (필수).
  --out <path>            write 모드 전용·필수 — 검증하며 기록할 promptfile 경로.
  --in <path>             verify 모드 전용·필수 — 이미 존재하는 promptfile 경로.
  --whitelist <path>      write/verify 필수 (emit-nonce 면제) — 구획 A 한글 예외 + 한글 앵커 +
                          **판독측 지시 marker** 의 SSOT
                          (`plugins/codeforge-review/templates/codex-korean-literal-whitelist.md`).
                          경로 주입 가능 = mutation/validity 테스트의 전제.
  --nonce <str>           **write 모드 필수** — 구획 B delimiter 의 per-invocation nonce.
                          nonce-결합 full-line sentinel 판정(is_sentinel_line)이 이 값을 요구하므로
                          write 경로에서 생략 불가 (nonce 진위 미검증 경로 제거 — F1-b/F2-i).
                          verify 는 선택 (생략 시 파일 첫 open 마커에서 유도 — nonce 진위 미검증,
                          검사 강도 하향, 정직 라벨).

  emit-nonce 모드: `secrets.token_hex(16)` (CSPRNG 128-bit hex, 32자) 를 stdout 에 1줄 print.
    --whitelist/--out/--in 불요. delimiter nonce 는 **보안토큰**이며 충돌회피(파일명) 토큰과 겸직
    금지 — 발급 채널을 분리해 nonce 가 파일명에 미포함(late-bound) 되게 강제한다 (CWE-330 해소;
    파일명 유일성은 dispatch 의 `TS="$(date +%s)-$$"` 가 별도 담당).

  ※ 앵커 **값** 을 주입하는 플래그는 **의도적으로 없다**. 앵커·판독측 지시 블록은 --whitelist 파일에서
    helper 가 직접 `open(..., encoding='utf-8')` 로 취득한다 (ADR-081 §결정 D16 3항·§결정 D17 R-D
    provenance). packet·argv·env 등 promptfile 본문과 같은 채널을 타고 온 값을 앵커·판독측 지시로 쓰면,
    조립 계층이 오염될 때 앵커·지시와 본문이 **같이** 깨져 자가일치로 assert 가 공허 통과한다.

════════════════════════════════════════════════════════════════════════════════
write 모드 (권장 — dispatch 경로 의무)
════════════════════════════════════════════════════════════════════════════════

  1. stdin raw **bytes** = 조립 원본을 읽는다 (텍스트 래퍼 경유 금지 — 상위 계층 디코딩 개입 차단).
  2. strict UTF-8 decode. invalid byte = 위반(exit 1).
  3. BOM(U+FEFF) 이 선두면 위반(exit 1). promptfile 은 always-UTF-8 을 mandate 하는 우리 소유
     생산-소비 폐쇄 채널이라 signature 기능이 무용하고, 앵커·골격 오프셋만 오염시킨다
     [source: RFC 3629 §6 — "A protocol SHOULD forbid use of U+FEFF as a signature for those textual
     protocol elements that the protocol mandates to be always UTF-8"]. 강도 = SHOULD (MUST 아님).
  4. `--out` 에 `encoding='utf-8', newline='\\n'` 로 write (개행 변환 0 — Windows CRLF 자동 변환은
     내용 대조를 born-broken 으로 만든다. write 측 리터럴 = CP §8.2A 문면 `newline="\\n"`).
  5. re-read: `encoding='utf-8', newline=''` 로 다시 읽는다 (read 측 리터럴 = CP §8.2A 문면
     `newline=""` — universal-newline 변환 차단).
  6. **내용 동일성 대조** — (2) 의 in-memory 원본 문자열과 (5) 의 re-read 전문이 완전히 같아야 한다.
     불일치 = 위반(exit 1). ★ 이 단계가 write 모드의 핵심 기제다 — 앵커 assert 만으로 대체하면
     본문만 변이된 경우를 놓친다 (anchor-assert-only hollow).
  7. **한글 앵커 assert** — whitelist 취득 앵커가 re-read 결과의 **블록 외부(구획 A)** scope 안에
     verbatim **정확히 1회** 존재. count scope = 구획 A 한정 — 전문(문서 전체) count 금지 (인용 diff
     안 앵커 사본을 카운트하면 ">1회" 오탐, F2-i (b)).
  8. **partition 검사** (아래 — INV-단일정본블록 + 블록 외부 한글 0) 수행.
  9. **판독측 지시 배치 검사** (assert_directive_placement — 아래) 수행.
  전부 통과 = exit 0.

  ※ (5)(6)(7) = 판별 seam `compare_roundtrip(original_text, out_path, whitelist_path) -> int` 로
    분리돼 있다 (0=통과 / 1=위반). write 모드가 내부 호출하며, §8.2 fixture ④ (content-discriminating)
    는 이 seam 을 직접 호출해 **write 완료 후 파일측**에 오염을 주입한다.

════════════════════════════════════════════════════════════════════════════════
verify 모드 (degrade — 사후 감사 한정)
════════════════════════════════════════════════════════════════════════════════

  기존 파일 strict decode + BOM + 앵커 assert + partition + 판독측 지시 배치 검사만 수행한다.
  ★ **내용 동일성은 보증하지 않는다** — 조립 원본 in-memory 텍스트가 없으므로 대조할 기준선 자체가
  없다. 따라서 verify 단독으로 AC-4(내용 동일성) 충족을 주장할 수 없다 (정직 라벨).
  허용 조건 (normative):
    (a) 조립 원본을 보유하지 않은 **사후 검증 주체** 한정 (PL 실물 확인·post-hoc 감사).
    (b) dispatch 경로는 **write 모드 의무** — dispatch 직전 검증을 verify 로 수행하면 계약 위반.

════════════════════════════════════════════════════════════════════════════════
partition 검사 (양 모드 공통)
════════════════════════════════════════════════════════════════════════════════

  구획 delimiter (ADR-081 §결정 D16 1항 / CodexReviewAgent.md §언어 구획 규약):

      BEGIN_UNTRUSTED_DATA nonce=<nonce>
      ... 구획 B (인용 원문 verbatim) ...
      END_UNTRUSTED_DATA nonce=<nonce>

  (a) **블록 구조 정합** — open/close 짝 일치 + 같은 nonce. sentinel 판정 = **nonce-결합 full-line**
      predicate `is_sentinel_line(line, expected_nonce)` (`^(BEGIN|END)_UNTRUSTED_DATA nonce=<expected>$`)
      — 인용 원문(구획 B) 안 `BEGIN_UNTRUSTED_DATA` substring 또는 다른/무 nonce full-line 은 일반
      컨텐츠로 취급(born-broken 오탐 해소, F2-i (a); bare substring 판정 폐기). 짝 불일치·중첩·
      nonce 일치 재개봉·close 선행·nonce 불일치·EOF 미닫힘 = 위반(exit 1).
  (b) **INV-단일정본블록** (F1-a) — (1) 블록 개수 정확히 **1개** (0개=미분리 / 2개+=구획탈출 표면)
      + (2) **terminal**: 유일 블록 END 이후 outside 라인에 비-whitelisted 지시성 텍스트 0 (블록이
      promptfile 최종 요소, 종결 후 빈 줄/공백만 허용). ★ 블록 개수 단독 검증은 shape-preserving
      변형(단일블록 + 종결 END 이후 trailing 영어 = forge-B)을 통과시키므로 terminal 결합 필수.
  (c) **블록 외부 한글 0** — 구획 A 영어 강제의 조립 시점 기계화.
      한글 문자 클래스 = U+AC00-D7A3 (음절) ∪ U+1100-11FF (자모) ∪ U+3130-318F (호환자모)
      ∪ U+A960-A97F, U+D7B0-D7FF (확장 A/B). `가-힣` 단독은 `ㄱ`(U+3131) 을 놓치므로 불가.
      제외는 **정확히 2종**: whitelist 리터럴(토큰 단위) / 한글 앵커 라인(줄 단위).
  비-ASCII 기호(`— § ② →` 등) 잔존은 위반이 **아니다** — floor 는 한글 0 이다.

════════════════════════════════════════════════════════════════════════════════
판독측 지시 배치 검사 (assert_directive_placement — 양 모드 공통, ADR-081 §결정 D17 R-D)
════════════════════════════════════════════════════════════════════════════════

  Spotlighting 요소②(판독측 지시)를 helper 가 기계강제한다 — 문서 선언만으론 bound=0 (S-1).
  canonical 지시 블록(whitelist `## 판독측 지시 marker` 절의 N 라인 전량, read 로 취득)이:
    · **위치** — 블록 외부(구획 A)에 존재.
    · **횟수** — 정확히 1회.
    · **순서(block-to-BEGIN adjacency)** — 마지막 라인이 유일 블록 BEGIN 직전(사이 라인 0).
    · **full-block 완결성(inter-line)** — N 라인이 구획 A 안에서 **in-order contiguous window**
      (중간 삽입 0, set-subset·reorder 금지) 로 매칭. partial-strip(N 중 1 라인 삭제) = 어떤
      contiguous window 도 SSOT 와 불일치 → 위반.
  ★ 단일 substring(예: 마지막 1줄) 매칭은 앞 요소 strip mutant 를 통과(hollow) → 금지. full-block
  완결성이 directive layer 의 load-bearing 속성(4 지시 요소 전량 존재)을 실제 falsify.
  line-count-agnostic — N = SSOT 가 담은 라인 수 그대로(하드코딩 0). provenance = SSOT 파일 read
  한정(블록 값 하드코딩·argv 금지 — 앵커 provenance 동형). 위반 = ViolationError(exit 1).

════════════════════════════════════════════════════════════════════════════════
whitelist 소비 계약
════════════════════════════════════════════════════════════════════════════════

  · 엔트리 라인 = `^<literal>\\t<근거 SSOT 경로>$` (TAB 1개 구분). 그 외 줄은 파싱 대상 아님.
  · 앵커 라인 = `^ANCHOR_LINE: ` 로 시작하는 **유일한** 줄. 0개·2개 이상 = setup error(exit 2).
  · 판독측 지시 marker = `## 판독측 지시 marker` 헤딩 직후 첫 fenced 코드블록의 content 라인 전량.
    부재·공백 = setup error(exit 2).
  · 형식 제약 위반 (길이 >32자 / 공백 포함 / 엔트리 >30 / 빈 토큰 / literal 허용 문자 클래스
    이탈) = 위반(exit 1). literal 허용 문자 = 한글 음절(U+AC00-D7A3) ∪ ASCII 영숫자 ∪ `:` `-` `_` 뿐.
  · **validity self-check** — 각 엔트리의 근거 경로 실재 ∧ 그 파일 안에 literal grep 실재 +
    **REPO_ROOT confinement**(`resolve().relative_to(REPO_ROOT)` — `../` traversal 봉쇄, P2-a).
    위반 = 위반(exit 1). 에러 메시지는 **sanitize** — literal 문자열 미노출(유무 은닉), line/ref 만 노출.
  · 엔트리 공집합 = 제외 0 (안전 방향, 정상). 단 **파일 부재 = setup error(exit 2)**.

════════════════════════════════════════════════════════════════════════════════
Exit code (closed enum — 이 밖의 값 반환 금지)
════════════════════════════════════════════════════════════════════════════════

  0 = PASS.
  1 = 검증 위반 (RED) — invalid byte / BOM / 내용 불일치 / 앵커 위반(부재 · 2회+ · 블록 내부 전용) /
      partition 위반(블록 구조 · 블록 개수≠1 · terminal · 블록 외부 한글) / 판독측 지시 위반(부재 ·
      블록 내부 relocation · partial-strip · 2회+ · adjacency) / whitelist 형식·validity·traversal 위반.
  2 = setup error — 인자 오류, whitelist 파일 부재, 앵커 라인 0개·2개+, 판독측 지시 marker 절 부재,
      빈 promptfile, --out/--in 미지정, emit-nonce 발급 실패, 파일 I/O 실패.
  ※ 호출측 (CodexReviewAgent dispatch) 은 rc != 0 이면 codex 를 호출하지 않고 dispatch 를 중단한다
    (verdict=inconclusive + marker `[promptfile-encoding-assert-failed: rc=<n>]`). 재조립 ≤1회,
    초과 = ESCALATE (자동 재시도 금지 — 입력 결함은 재시도로 낫지 않는다).

════════════════════════════════════════════════════════════════════════════════
보증 한계 (정직 천장 — ADR-119 / ADR-081 §결정 D17 honest ceiling)
════════════════════════════════════════════════════════════════════════════════

  · 본 helper 가 확보하는 것은 **conditional integrity** ("실행됐다면 L1 산출물 내용이 원본과 같고,
    injection 방어층이 계약대로 배선됐다") 이며, **실행이 실제로 있었는가**(execution existence) 는
    별개 축이다 — 후자는 promptfile·out.json 실물 + PL 독립 확인으로만 falsify 되고 기계 게이트 불가.
  · **nonce 가 실제 CSPRNG 로 생성됐는지**(distinctness·shape floor 는 검사 가능하나 생성 소스 자체는
    아님) · **codex 모델의 실 순종** · 상류 오디코딩 완전차단은 구조적 검증 불가 — 완화 상한 =
    **delimiting tier**(Spotlighting 최약, 구획 B verbatim 보존 제약상 datamarking/encoding 비채택).
    상류 결함 (openai/codex #4013, CLOSED 2026-08-05) 종결이 codex UTF-8 강제 보장은 아니다.
    "완전 차단"/"required 강제"/"완전 봉인" 서술 금지 (AC-8a grep 결박).
  · `LC_ALL`/`LANG` env 는 Python-on-Windows 파일 I/O 에 무효다 (2급 defense-in-depth).
    1급 방어는 본 helper 코드계층의 명시 `encoding='utf-8'` 이다.
"""

import argparse
import os
import re
import secrets
import sys
from collections import namedtuple
from pathlib import Path

# Windows 콘솔 cp949 기본 인코딩에서 UTF-8 출력 실패 방지 (ADR-061 standardize).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXIT_PASS = 0
EXIT_VIOLATION = 1
EXIT_SETUP_ERROR = 2

PROG = os.path.basename(__file__)

# repo 루트 = <repo>/scripts/lib/<this file> → parents[2]. CWD 무의존 (whitelist 엔트리의
# repo-상대 근거 경로 해석 기준선 + P2-a confinement 기준선 — pytest·CI·수동 실행 어디서 호출해도 동일 판정).
REPO_ROOT = Path(__file__).resolve().parents[2]

# ── whitelist 파싱 상수 ────────────────────────────────────────────────────────
ANCHOR_PREFIX = "ANCHOR_LINE: "
DIRECTIVE_HEADING = "## 판독측 지시 marker"  # 판독측 지시 canonical 블록 SSOT 절 헤딩 (ADR-081 §결정 D17 R-D)
MAX_LITERAL_LEN = 32
MAX_ENTRIES = 30

# ── 구획 delimiter 상수 ────────────────────────────────────────────────────────
# full-line nonce-결합 매칭만 delimiter/sentinel 로 인정 (bare substring 판정 폐기 — F2-i (a)).
RE_BEGIN = re.compile(r"^BEGIN_UNTRUSTED_DATA nonce=(\S+)[ \t]*$")
RE_END = re.compile(r"^END_UNTRUSTED_DATA nonce=(\S+)[ \t]*$")

# 한글 문자 클래스 (docstring partition (c) SSOT). 범위는 **code point 정수 표**로 고정하고 문자
# 클래스를 런타임 조립한다 — 이 파일 자체가 인코딩 검증기라, 판정 상수를 raw 한글 리터럴로 두면
# 소스가 오염될 때 검사기까지 조용히 함께 깨진다 (미할당 경계 code point 는 리터럴로 쓰면 눈으로
# 검수도 불가능하다).
HANGUL_SYLLABLE_RANGE = (0xAC00, 0xD7A3)
HANGUL_RANGES = (
    HANGUL_SYLLABLE_RANGE,  # 음절
    (0x1100, 0x11FF),  # 자모
    (0x3130, 0x318F),  # 호환자모 — 음절 범위 단독이 놓치는 U+3131 (ㄱ) 포함
    (0xA960, 0xA97F),  # 확장 A
    (0xD7B0, 0xD7FF),  # 확장 B
)
HANGUL_RE = re.compile(
    "[" + "".join("%s-%s" % (chr(lo), chr(hi)) for lo, hi in HANGUL_RANGES) + "]"
)

# whitelist 엔트리 **literal 토큰**의 허용 문자 클래스 (docstring 'whitelist 소비 계약' 형식 제약
# SSOT 이행 — 선언 원본은 whitelist 템플릿 §형식 제약 3항 "공백 0 · 문장부호 0"). 허용 = 한글 음절
# ∪ ASCII 영숫자 ∪ label namespace 구분자 `:` `-` `_`; 그 외 전부 불허(= 산문 문장부호 차단).
LITERAL_DISALLOWED_RE = re.compile(
    "[^0-9A-Za-z:_\\-%s-%s]"
    % (chr(HANGUL_SYLLABLE_RANGE[0]), chr(HANGUL_SYLLABLE_RANGE[1]))
)

# BOM = U+FEFF. escape 표기 고정 — raw 로 두면 소스에서 보이지 않아 검수·diff 가 불가능하다.
BOM = "\ufeff"

# whitelist 는 한 프로세스 안에서 main 과 seam(compare_roundtrip) 이 각각 필요로 하므로 1회 read 후 재사용.
_WHITELIST_CACHE = {}

# 구획 분해 seam 반환 구조 (F1-a — block_count·block_spans 확장). 전 소비자(assert_anchor·
# check_partition·assert_directive_placement)가 이 단일 seam 을 공유 → 판정 drift 0 (파서 2벌 금지).
#   outside      = 블록 외부(구획 A) 라인 [(lineno, line)]
#   block_count  = 감지된 UNTRUSTED 블록 개수 (INV-단일정본블록 (1))
#   block_spans  = [(start_lineno, end_lineno)] — BEGIN/END 라인 번호 (terminal·adjacency 판정 재료)
PartitionResult = namedtuple("PartitionResult", ["outside", "block_count", "block_spans"])


class SetupError(Exception):
    """exit 2 계열 — 검증 판정 자체가 성립하지 않는 상태 (인자·파일 부재·I/O)."""


class ViolationError(Exception):
    """exit 1 계열 — 검증 위반 (RED)."""


def split_lines(text):
    """개행 분해 = `\\n` 단일 기준.

    `str.splitlines()` 는 U+2028·U+000B·U+000C 등도 줄 경계로 취급하므로, 임의 입력에서
    줄 판정이 흔들려 partition 결과가 입력 의존적으로 달라진다. 여기서는 `\\n` 만 경계로 쓰고
    CRLF 수용을 위해 각 줄 끝의 CR 하나만 떼어낸다 (내용 대조는 원문 문자열로 별도 수행하므로
    이 정규화가 round-trip 판정에 영향을 주지 않는다).
    """
    out = []
    for line in text.split("\n"):
        out.append(line[:-1] if line.endswith("\r") else line)
    return out


def _parse_entries(lines):
    """TAB 포함 줄 = 엔트리 후보. 형식 제약 위반 = ViolationError. 반환 = [(literal, ref, lineno)].

    "그 외 줄은 파싱 대상 아님" 의 기계 판정선 = TAB 유무. TAB 이 있는데 형식이 어긋나면 조용히
    무시하지 않고 위반으로 올린다 — 무시하면 형식 제약 5종이 전부 공허해진다.

    집행 5종 = 빈 토큰 / 공백 포함(literal·ref 양측) / literal 허용 문자 클래스(literal 한정 —
    산문 문장부호 차단) / literal 길이 ≤ MAX_LITERAL_LEN / 총 엔트리 ≤ MAX_ENTRIES.
    """
    entries = []
    for lineno, line in enumerate(lines, 1):
        if "\t" not in line:
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            raise ViolationError(
                f"whitelist line {lineno}: TAB 구분자 1개 아님 ({len(parts) - 1}개)"
            )
        literal, ref = parts
        if not literal or not ref:
            raise ViolationError(f"whitelist line {lineno}: 빈 토큰")
        if any(ch.isspace() for ch in literal) or any(ch.isspace() for ch in ref):
            raise ViolationError(f"whitelist line {lineno}: 토큰 내 공백 포함")
        # 공백 검사 뒤에 둔다 — 공백은 이 클래스에도 걸리지만, 더 구체적인 위 진단을 보존한다.
        bad = LITERAL_DISALLOWED_RE.search(literal)
        if bad is not None:
            raise ViolationError(
                f"whitelist line {lineno}: literal 허용 문자 클래스 이탈 — {bad.group(0)!r} "
                "(허용: 한글 음절 · ASCII 영숫자 · `:` `-` `_`; 산문 문장부호 불가)"
            )
        if len(literal) > MAX_LITERAL_LEN:
            raise ViolationError(
                f"whitelist line {lineno}: literal 길이 {len(literal)} > {MAX_LITERAL_LEN}"
            )
        entries.append((literal, ref, lineno))
    if len(entries) > MAX_ENTRIES:
        raise ViolationError(f"whitelist 엔트리 {len(entries)}개 > {MAX_ENTRIES}")
    return entries


def _validate_entries(entries):
    """validity self-check — 근거 경로 실재 ∧ literal 이 그 파일 안에 실재 + REPO_ROOT confinement (P2-a).

    에러 메시지는 sanitize 한다 — literal 문자열을 노출하지 않고 (literal 유무 은닉) line/ref 만 노출.
    traversal(`../` 로 REPO_ROOT 밖 지시)은 `resolve().relative_to(REPO_ROOT)` 로 봉쇄 (Python 3.9
    호환 = `is_relative_to` 대신 try/except ValueError).
    """
    text_cache = {}
    for literal, ref, lineno in entries:
        path = Path(ref)
        if not path.is_absolute():
            path = REPO_ROOT / ref
        # P2-a confinement — resolve 후 REPO_ROOT 하위 여부. 밖이면 traversal 차단(literal 미노출).
        try:
            path.resolve().relative_to(REPO_ROOT)
        except ValueError:
            raise ViolationError(
                f"whitelist validity: line {lineno} 근거 경로가 REPO_ROOT 밖 (traversal 차단) — ref {ref}"
            )
        if not path.is_file():
            raise ViolationError(
                f"whitelist validity: line {lineno} 근거 경로 비실재 — ref {ref}"
            )
        key = str(path)
        if key not in text_cache:
            try:
                text_cache[key] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise ViolationError(
                    f"whitelist validity: line {lineno} 근거 파일 read 실패 — ref {ref}: {exc}"
                ) from exc
        if literal not in text_cache[key]:
            raise ViolationError(
                f"whitelist validity: line {lineno} literal 미실재 — ref {ref}"
            )


def _parse_directive_block(lines):
    """`## 판독측 지시 marker` 절의 첫 fenced 코드블록 content 라인 전량을 리스트로 반환.

    ADR-081 §결정 D17 R-D provenance — canonical 판독측 지시 블록의 SSOT read 채널. `load_whitelist`
    의 단일 read 로 얻은 lines 를 재파싱하므로 **신규 read 채널 0** (앵커 provenance 동형).
    부재·공백 = SetupError(exit 2 — whitelist 소멸 조용히 통과 차단 축 동형).
    """
    heading_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == DIRECTIVE_HEADING:
            heading_idx = idx
            break
    if heading_idx is None:
        raise SetupError(f"whitelist `{DIRECTIVE_HEADING}` 절 부재 (판독측 지시 marker SSOT 없음)")

    fence_open = None
    for idx in range(heading_idx + 1, len(lines)):
        if lines[idx].startswith("```"):
            fence_open = idx
            break
    if fence_open is None:
        raise SetupError(f"`{DIRECTIVE_HEADING}` 절에 fenced 코드블록 부재")

    content = []
    fence_close = None
    for idx in range(fence_open + 1, len(lines)):
        if lines[idx].startswith("```"):
            fence_close = idx
            break
        content.append(lines[idx])
    if fence_close is None:
        raise SetupError(f"`{DIRECTIVE_HEADING}` fenced 코드블록 미종결")
    if not content:
        raise SetupError(f"`{DIRECTIVE_HEADING}` fenced 코드블록 비어 있음 (판독측 지시 라인 0)")
    return content


def load_whitelist(whitelist_path):
    """whitelist 를 read 해 (anchor_value, literals, directive_block) 를 돌려준다.

    SetupError = 파일 부재 / decode 실패 / 앵커 라인 0개·2개+ / 판독측 지시 marker 절 부재·공백 (exit 2).
    ViolationError = 엔트리 형식·validity·traversal 위반 (exit 1).
    directive_block = tuple(라인) — `## 판독측 지시 marker` 절 canonical 블록 N 라인 전량.
    """
    key = os.path.abspath(str(whitelist_path))
    if key in _WHITELIST_CACHE:
        return _WHITELIST_CACHE[key]

    path = Path(key)
    if not path.is_file():
        raise SetupError(f"whitelist 파일 부재: {whitelist_path}")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SetupError(f"whitelist read 실패: {whitelist_path}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SetupError(f"whitelist strict UTF-8 decode 실패: {whitelist_path}: {exc}") from exc

    lines = split_lines(text)
    anchor_lines = [ln for ln in lines if ln.startswith(ANCHOR_PREFIX)]
    if len(anchor_lines) != 1:
        raise SetupError(
            f"whitelist 앵커 라인(`{ANCHOR_PREFIX}`) {len(anchor_lines)}개 — 정확히 1개 필요"
        )
    anchor_value = anchor_lines[0][len(ANCHOR_PREFIX):].strip()
    if not anchor_value:
        raise SetupError("whitelist 앵커 값이 비어 있음")

    entries = _parse_entries(lines)
    _validate_entries(entries)
    directive_block = _parse_directive_block(lines)

    result = (
        anchor_value,
        tuple(literal for literal, _, _ in entries),
        tuple(directive_block),
    )
    _WHITELIST_CACHE[key] = result
    return result


def is_sentinel_line(line, expected_nonce):
    """nonce-결합 full-line sentinel 판정 (F2-i (a) — bare substring 판정 폐기).

    `^(BEGIN|END)_UNTRUSTED_DATA nonce=<expected_nonce>$` full-line 만 sentinel 로 인정한다.
    인용 원문(구획 B) 안의 `BEGIN_UNTRUSTED_DATA` substring, 또는 **다른/무 nonce** full-line 은
    일반 컨텐츠로 판정 (born-broken 오탐 해소 — sentinel/앵커 리터럴을 품은 diff 를 리뷰해도 rc=1 오차단
    아님). CSPRNG nonce 불가측성이 이 협착의 안전 전제다 (F1-b 선행 — §순서 불변식).

    expected_nonce=None (verify --nonce 생략, 검사 강도 하향 경로) 이면 임의 nonce full-line 을
    sentinel 로 인정 — 첫 open 마커 유도 전 misplaced sentinel 검출 유지 (블록 내부는 진입 시 nonce
    확정되므로 이 관용은 블록 밖 pre-open 영역 한정, born-broken 재유입 아님).
    """
    m = RE_BEGIN.match(line) or RE_END.match(line)
    if m is None:
        return False
    if expected_nonce is None:
        return True
    return m.group(1) == expected_nonce


def _split_partition(text, expected_nonce=None):
    """구획 분해 **공유 seam** — 블록 구조를 1회 파싱해 PartitionResult 반환.

    구조 위반 (짝 불일치 · 중첩·nonce 일치 재개봉 · close 선행 · nonce 불일치 · EOF 미닫힘) =
    ViolationError. 블록 **내부** 라인은 outside 에 담지 않는다 (구획 B = 인용 원문 verbatim 구역).

    `assert_anchor`·`check_partition`·`assert_directive_placement` 이 **같은** A/B 경계를 보도록
    분해 로직을 단일화한 지점이다 — 파서를 2벌 두면 판정 경계가 조용히 갈라진다 (drift 표면).
    """
    lines = split_lines(text)

    in_block = False
    block_nonce = None
    file_nonce = expected_nonce  # --nonce 제공 시 그 값이 기준, 아니면 첫 open 마커에서 유도
    block_start_lineno = None
    outside = []
    block_count = 0
    block_spans = []

    for lineno, line in enumerate(lines, 1):
        m_begin = RE_BEGIN.match(line)
        m_end = RE_END.match(line)

        if in_block:
            if m_end and m_end.group(1) == block_nonce:
                in_block = False
                block_spans.append((block_start_lineno, lineno))
                block_start_lineno = None
                block_nonce = None
                continue
            if is_sentinel_line(line, file_nonce):
                raise ViolationError(
                    f"line {lineno}: 블록 본문 내 sentinel 재출현 "
                    "(nonce-결합 full-line — 중첩 · nonce 일치 재개봉 포함)"
                )
            continue

        if m_begin:
            nonce = m_begin.group(1)
            if file_nonce is None:
                file_nonce = nonce
            elif nonce != file_nonce:
                raise ViolationError(
                    f"line {lineno}: 블록 nonce 불일치 (기대 `{file_nonce}`, 실제 `{nonce}`)"
                )
            in_block = True
            block_nonce = nonce
            block_start_lineno = lineno
            block_count += 1
            continue

        if is_sentinel_line(line, file_nonce):
            raise ViolationError(
                f"line {lineno}: 블록 밖 sentinel (close 선행 / delimiter 형식 위반)"
            )

        outside.append((lineno, line))

    if in_block:
        raise ViolationError("EOF: 미닫힌 UNTRUSTED 블록 (close sentinel 부재)")

    return PartitionResult(outside, block_count, block_spans)


def assert_anchor(text, anchor_value, expected_nonce=None):
    """한글 앵커 assert — 앵커가 **블록 외부(구획 A) scope** 안에 verbatim **정확히 1회** 존재.

    기계화 대상 문면 = whitelist 템플릿 §한글 앵커 **조립 규약** ("promptfile 헤더에 위
    `ANCHOR_LINE:` 줄을 **verbatim 1회** 포함") + CP §8.4 '앵커 라인 부재 = RED'.

    count scope = **구획 A(블록 외부) 한정** (F2-i (b) — 전문 count 폐기). 전문 substring count 는:
      · **위치** — 앵커가 untrusted block **안에만** 있어도 통과 (헤더 앵커 부재를 블록 안 사본이 은폐).
      · **횟수** — 인용 원문(구획 B) 안 앵커 사본이 카운트돼 ">1회" 오탐 (born-broken).
    outside scope count 는 두 축을 동시에 닫는다 — 블록 내부 사본은 세지 않으므로 구획 B verbatim 무손상.
    """
    partition = _split_partition(text, expected_nonce)
    total = sum(line.count(anchor_value) for _, line in partition.outside)
    if total == 0:
        raise ViolationError(
            "한글 앵커 부재 — whitelist 취득 앵커 값이 promptfile **구획 A(블록 외부)** 안에 verbatim "
            "없음 (블록 안에만 있으면 헤더 앵커 부재를 인용 사본이 은폐 — 조립 규약: 헤더에 "
            "`ANCHOR_LINE:` 줄 verbatim 1회 포함 의무)"
        )
    if total > 1:
        raise ViolationError(
            f"한글 앵커 구획 A 안 {total}회 출현 — 조립 규약은 **verbatim 1회** "
            "(고정 헤더 중복 = 헤더 판정 불능 · 사본 하나만 pristine 이면 나머지 오염 은폐)"
        )


def check_partition(text, anchor_value, literals, expected_nonce=None):
    """구획 검사 — (a) 블록 구조 정합 + (b) INV-단일정본블록(개수 1 + terminal) + (c) 블록 외부 한글 0.

    위반 = ViolationError. (a) 는 `_split_partition` 파싱 자체가 raise 하고, 본 함수는 (b)(c) 를 집행한다.
    """
    partition = _split_partition(text, expected_nonce)

    # (b) INV-단일정본블록 (1) 블록 개수 == 1
    if partition.block_count != 1:
        raise ViolationError(
            f"UNTRUSTED 블록 개수 {partition.block_count} — 정확히 1개 필요 "
            "(INV-단일정본블록 (1): 0개=미분리 / 2개+=구획탈출 표면)"
        )
    # (2) terminal 기준선 = 유일 블록의 END 라인 번호
    block_end_lineno = partition.block_spans[0][1]

    # 긴 리터럴 우선 제거 — `phase:요구사항` 을 먼저 지우면 `phase:요구사항-리뷰` 의 `-리뷰` 가
    # 잔여 한글로 남아 오탐이 된다.
    ordered = sorted(literals, key=len, reverse=True)
    for lineno, line in partition.outside:
        if anchor_value and anchor_value in line:
            continue  # 앵커 라인 = 줄 단위 제외 (terminal·한글 검사 공통, 제외 2종 중 하나)
        probe = line
        for literal in ordered:
            if literal in probe:
                probe = probe.replace(literal, " ")  # whitelist 리터럴 = 토큰 단위 제외
        # (b) (2) terminal — 블록 END 이후 비-whitelisted 지시성 잔여 = 구획탈출 변형형(forge-B) 차단
        if lineno > block_end_lineno and probe.strip():
            raise ViolationError(
                f"line {lineno}: 블록 종결 후 비-whitelisted 지시성 텍스트 "
                "(INV-단일정본블록 (2) terminal 위반 — 블록이 promptfile 최종 요소여야 함)"
            )
        # (c) 블록 외부 한글 0
        match = HANGUL_RE.search(probe)
        if match:
            raise ViolationError(
                f"line {lineno}: 블록 외부 한글 (제외 2종 미해당) — {match.group(0)!r}"
            )


def assert_directive_placement(text, directive_block, expected_nonce=None):
    """판독측 지시 배치 기계강제 (S-1 / ADR-081 §결정 D17 R-D) — assert_anchor 와 분리된 신규 함수(SRP).

    canonical 지시 블록(whitelist `## 판독측 지시 marker` 절의 N 라인 전량)이 promptfile 안에서:
      · **위치** — 블록 외부(구획 A)에 존재.
      · **횟수** — 정확히 1회.
      · **순서(block-to-BEGIN adjacency)** — 마지막 라인이 유일 블록 BEGIN 직전(사이 라인 0).
      · **full-block 완결성(inter-line)** — N 라인이 구획 A 안에서 in-order contiguous window 로 매칭
        (중간 삽입 0, set-subset·reorder 금지). partial-strip(1 라인 삭제)은 어떤 contiguous window
        도 SSOT 와 불일치 → 위반.
    단일 substring 매칭은 앞 요소 strip mutant 를 통과(hollow) → full-block 이 directive layer 의
    load-bearing 속성(4 지시 요소 전량)을 실제 falsify 한다. line-count-agnostic (N = SSOT 저장 라인 수).
    """
    directive = list(directive_block)
    n = len(directive)
    if n == 0:
        raise SetupError(
            f"판독측 지시 marker SSOT 가 비어 있음 (whitelist `{DIRECTIVE_HEADING}` 절 라인 0)"
        )

    # 블록 개수(==1) 강제는 본 함수 소관 아님 — INV-단일정본블록 = check_partition 단일 소유
    # (§3.1). 본 함수는 위치·횟수·순서·full-block 4속성만 검증하며, adjacency 판정에 필요한 블록
    # BEGIN 은 (파이프라인상 check_partition 이 선행해 이미 1개로 확정된) block_spans[0] 에서 취한다.
    partition = _split_partition(text, expected_nonce)

    outside_lines = [line for _, line in partition.outside]
    outside_linenos = [lineno for lineno, _ in partition.outside]

    # full-block 완결성 — 구획 A 안 in-order contiguous window 매칭 위치 수집.
    match_starts = [
        i
        for i in range(len(outside_lines) - n + 1)
        if outside_lines[i:i + n] == directive
    ]
    if len(match_starts) == 0:
        raise ViolationError(
            "판독측 지시 부재/불완전 — canonical N-라인 in-order contiguous window 미존재 "
            "(부재 · 블록 내부 relocation · partial-strip · reorder 중 하나)"
        )
    if len(match_starts) > 1:
        raise ViolationError(
            f"판독측 지시 {len(match_starts)}회 — 정확히 1회 필요"
        )

    # 순서(block-to-BEGIN adjacency) — canonical 블록 마지막 라인이 (첫)블록 BEGIN 직전.
    if not partition.block_spans:
        raise ViolationError(
            "판독측 지시 순서 판정 불능 — UNTRUSTED 블록 부재 (직전 adjacency 대상 없음)"
        )
    start_idx = match_starts[0]
    last_directive_lineno = outside_linenos[start_idx + n - 1]
    block_begin_lineno = partition.block_spans[0][0]
    if last_directive_lineno + 1 != block_begin_lineno:
        raise ViolationError(
            "판독측 지시 순서 위반 — canonical 블록 마지막 라인이 UNTRUSTED 블록 BEGIN 직전이 아님 "
            f"(마지막 지시 line {last_directive_lineno}, BEGIN line {block_begin_lineno} — 사이 라인 존재)"
        )


def _first_diff_index(left, right):
    limit = min(len(left), len(right))
    for idx in range(limit):
        if left[idx] != right[idx]:
            return idx
    return limit


def compare_roundtrip(original_text, out_path, whitelist_path):
    """write 모드의 **내용 동일성 대조 + 앵커 assert** 판별 seam. 0 = 통과 / 1 = 위반.

    write 모드가 파일 기록 직후 호출한다. 별도 함수로 노출한 이유 = CP §8.2 fixture ④
    (content-discriminating) 의 precondition ⓑ — 오염 주입이 **write 완료 후 파일측**이어야
    correct 구현과 anchor-assert-only hollow 구현이 갈린다.

    whitelist setup 문제(부재·앵커 라인 개수·판독측 지시 marker 절)는 SetupError 로 상위에 전파한다.
    """
    try:
        with open(out_path, "r", encoding="utf-8", newline="") as handle:
            re_read = handle.read()
    except UnicodeDecodeError as exc:
        print(f"VIOLATION: re-read strict UTF-8 decode 실패: {out_path}: {exc}", file=sys.stderr)
        return EXIT_VIOLATION
    except OSError as exc:
        raise SetupError(f"re-read 실패: {out_path}: {exc}") from exc

    if re_read != original_text:
        idx = _first_diff_index(re_read, original_text)
        print(
            "VIOLATION: 내용 동일성 대조 실패 — in-memory 원본 ↔ re-read 불일치 "
            f"(첫 불일치 offset {idx}, 원본 {len(original_text)}자 / re-read {len(re_read)}자)",
            file=sys.stderr,
        )
        return EXIT_VIOLATION

    anchor_value, _, _ = load_whitelist(whitelist_path)
    try:
        # expected_nonce 미전달 = 블록 경계를 파일 첫 open 마커에서 유도 (seam 의 3-인자 계약 보존).
        # nonce **위조** 검출은 이 seam 이 아니라 run_write 가 `--nonce` 를 넘겨 부르는 check_partition
        # /assert_directive_placement 소유다 (책임 분리, 검사 누락 0).
        assert_anchor(re_read, anchor_value)
    except ViolationError as exc:
        print(f"VIOLATION: {exc}", file=sys.stderr)
        return EXIT_VIOLATION

    return EXIT_PASS


def _decode_strict(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ViolationError(f"strict UTF-8 decode 실패: {exc}") from exc


def _reject_bom(text):
    if text.startswith(BOM):
        raise ViolationError(
            "BOM(U+FEFF) 선두 — always-UTF-8 폐쇄 채널에서 signature 금지 "
            "[source: RFC 3629 §6 SHOULD forbid]"
        )


def run_emit_nonce():
    """emit-nonce 모드 — CSPRNG 128-bit hex(32자) 를 stdout 1줄 print (F1-b nonce 발급 seam).

    delimiter nonce 는 **보안토큰** — 충돌회피(파일명) 토큰과 겸직 금지. 발급 채널 분리로 nonce 가
    파일명에 미포함(late-bound) 되게 강제한다 (CWE-330 해소). token_hex 실패(엔트로피 소스 부재)는
    main 의 포괄 except 가 SETUP_ERROR(exit 2) 로 귀속.
    """
    print(secrets.token_hex(16))
    return EXIT_PASS


def run_write(out_path, whitelist_path, nonce):
    """write 모드 — docstring 'write 모드' 1~9 단계 이행."""
    stdin_buffer = getattr(sys.stdin, "buffer", None)
    if stdin_buffer is None:
        raise SetupError("stdin binary 스트림 부재 (raw byte read 불가)")
    raw = stdin_buffer.read()
    if raw == b"":
        raise SetupError('빈 promptfile (stdin 0 byte) — `"" == ""` 공허 통과 차단')

    text = _decode_strict(raw)
    _reject_bom(text)

    # 기록 전 whitelist 확정 — 형식·validity·판독측 지시 marker 위반이면 side effect 없이 중단.
    anchor_value, literals, directive_block = load_whitelist(whitelist_path)

    try:
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except OSError as exc:
        raise SetupError(f"write 실패: {out_path}: {exc}") from exc

    rc = compare_roundtrip(text, out_path, whitelist_path)
    if rc != EXIT_PASS:
        return rc

    check_partition(text, anchor_value, literals, nonce)
    assert_directive_placement(text, directive_block, nonce)

    print(
        f"PASS: write 모드 — round-trip 내용 동일성·앵커·partition·판독측 지시 전건 통과 ({out_path})"
    )
    return EXIT_PASS


def run_verify(in_path, whitelist_path, nonce):
    """verify 모드 — decode + BOM + 앵커 + partition + 판독측 지시 만 (내용 동일성 미보증)."""
    path = Path(in_path)
    if not path.is_file():
        raise SetupError(f"--in 파일 부재: {in_path}")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SetupError(f"--in read 실패: {in_path}: {exc}") from exc
    if raw == b"":
        raise SetupError('빈 promptfile — `"" == ""` 공허 통과 차단')

    text = _decode_strict(raw)
    _reject_bom(text)

    anchor_value, literals, directive_block = load_whitelist(whitelist_path)
    assert_anchor(text, anchor_value, nonce)
    check_partition(text, anchor_value, literals, nonce)
    assert_directive_placement(text, directive_block, nonce)

    print(
        f"PASS: verify 모드 — decode·앵커·partition·판독측 지시 통과 ({in_path}) "
        "[내용 동일성 미보증 — dispatch 경로는 write 모드 의무]"
    )
    return EXIT_PASS


def build_parser():
    """CLI 계약 (module docstring SSOT) 의 argparse 구현."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Codex promptfile UTF-8 round-trip / 언어 구획 / injection 방어 검증 "
            "(ADR-081 §결정 D16·D17)."
        ),
        epilog=(
            "exit: 0=PASS / 1=검증 위반 / 2=setup error. "
            "앵커·판독측 지시 값 주입 플래그는 의도적으로 없다 — --whitelist 파일에서 직접 취득한다. "
            "nonce 는 emit-nonce 모드가 CSPRNG 로 발급한다 (--mode emit-nonce)."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("write", "verify", "emit-nonce"),
        required=True,
        help="write = stdin 조립 원본을 검증하며 --out 에 기록 (dispatch 경로 의무) / "
             "verify = 기존 --in 파일 사후 감사 (내용 동일성 미보증) / "
             "emit-nonce = CSPRNG 128-bit hex nonce 발급 (stdout)",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="write 모드 필수 — 검증하며 기록할 promptfile 경로",
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        metavar="PATH",
        help="verify 모드 필수 — 이미 존재하는 promptfile 경로",
    )
    parser.add_argument(
        "--whitelist",
        metavar="PATH",
        help="write/verify 필수 (emit-nonce 면제) — 구획 A 한글 예외 + 한글 앵커 + 판독측 지시 marker "
             "SSOT (파일 부재 = exit 2)",
    )
    parser.add_argument(
        "--nonce",
        metavar="STR",
        default=None,
        help="구획 B delimiter 의 per-invocation nonce. **write 모드 필수** (nonce-결합 full-line "
             "sentinel 판정이 요구) / verify 는 선택 (생략 시 파일에서 유도 — 검사 강도 하향)",
    )
    return parser


def validate_mode_args(parser, args):
    """모드별 필수 인자 상호 배제 검증 — 위반 시 argparse 경유 exit 2."""
    if args.mode == "emit-nonce":
        return  # --whitelist/--out/--in/--nonce 전부 불요 (self-contained CSPRNG 발급)
    if not args.whitelist:
        parser.error("--mode {write,verify} 는 --whitelist <path> 필수")
    if args.mode == "write":
        if not args.out:
            parser.error("--mode write 는 --out <path> 필수")
        if args.in_path:
            parser.error("--mode write 에 --in 사용 불가 (조립 원본은 stdin)")
        if not args.nonce:
            parser.error("--mode write 는 --nonce <str> 필수 (nonce 진위 미검증 경로 제거 — F1-b/F2-i)")
    else:  # verify
        if not args.in_path:
            parser.error("--mode verify 는 --in <path> 필수")
        if args.out:
            parser.error("--mode verify 에 --out 사용 불가 (write 금지 모드)")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_mode_args(parser, args)

    try:
        if args.mode == "emit-nonce":
            return run_emit_nonce()
        if args.mode == "write":
            return run_write(args.out, args.whitelist, args.nonce)
        return run_verify(args.in_path, args.whitelist, args.nonce)
    except ViolationError as exc:
        print(f"VIOLATION: {exc}", file=sys.stderr)
        return EXIT_VIOLATION
    except SetupError as exc:
        print(f"SETUP_ERROR: {exc}", file=sys.stderr)
        return EXIT_SETUP_ERROR
    except Exception as exc:  # noqa: BLE001 — exit enum {0,1,2} 폐쇄 보증 (uncaught 전파 금지)
        print(
            f"SETUP_ERROR: 예기치 못한 내부 오류: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return EXIT_SETUP_ERROR


if __name__ == "__main__":
    sys.exit(main())
