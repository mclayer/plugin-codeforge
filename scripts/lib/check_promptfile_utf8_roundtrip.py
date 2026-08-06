#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2884 / ADR-081 Amendment 15 §결정 D16 3항 — Codex promptfile UTF-8 round-trip fail-closed 검증 helper (SSOT)
# ADR-061 §결정 1 Python-SSOT 패턴 (scripts/lib check_* 관례). "cp949 회피 = 명시 encoding='utf-8'" 는
#   ADR-061 본문 §결정이 아니라 그로부터 파생된 scripts/lib de facto 관행 (동 디렉터리 495건 실측) — 동일 원리의 새 적용처.
# ADR-170 §결정 21 (= §결정 2 표 entry 7) 동형 승계 — "argv 는 ASCII path 만, 한국어 실값·content 는 UTF-8 파일 내부".
#   argv 축은 ADR-081 §결정 D8 file-redirect 가 기차단하고, 본 helper 가 파일 **내용** 축을 완결한다.
#
# ★ 현재 상태 = STUB (CFP-2884 TDD RED baseline). 검증 로직 미구현 — argparse 통과 후 모든 실행 경로가
#   `NOT_IMPLEMENTED` 1줄을 stderr 로 내고 exit 2. 아래 docstring 의 CLI 계약은 **확정본**이며,
#   후속 구현 pass 와 self-test 는 이 계약을 SSOT 로 삼는다 (계약 변경 = Change Plan 개정 경유).
"""Codex promptfile UTF-8 round-trip / 언어 구획 검증 helper.

promptfile 조립 계층(L0-L1)에서 "쓴 것과 읽은 것이 같은가" 를 fail-closed 로 판정한다.
byte 문법 유효성 검사 단독은 금지 — cp949 오해석 재인코딩 산출물은 **valid UTF-8 인 채로 내용만**
오염되므로 문법 검사를 그대로 통과한다 (CFP-2884 발단 사고가 실증).

════════════════════════════════════════════════════════════════════════════════
CLI
════════════════════════════════════════════════════════════════════════════════

    check_promptfile_utf8_roundtrip.py --mode write  --out <path> --whitelist <path> [--nonce <str>]
    check_promptfile_utf8_roundtrip.py --mode verify --in  <path> --whitelist <path> [--nonce <str>]

  --mode {write,verify}   판정 모드 (필수).
  --out <path>            write 모드 전용·필수 — 검증하며 기록할 promptfile 경로.
  --in <path>             verify 모드 전용·필수 — 이미 존재하는 promptfile 경로.
  --whitelist <path>      양 모드 필수 — 구획 A 한글 예외 + 한글 앵커의 SSOT
                          (`plugins/codeforge-review/templates/codex-korean-literal-whitelist.md`).
                          경로 주입 가능 = AC-9 mutation/validity 테스트의 전제.
  --nonce <str>           선택 — 구획 B delimiter 의 per-invocation nonce.
                          제공 시 delimiter 의 nonce 가 이 값과 **일치**하는지까지 assert (위조 검출).
                          생략 시 파일 안 첫 open 마커에서 nonce 를 유도 — nonce 진위는 미검증
                          (정직 라벨: 생략은 검사 강도를 낮춘다).

  ※ 앵커 **값** 을 주입하는 플래그는 **의도적으로 없다**. 앵커는 --whitelist 파일에서 helper 가
    직접 `open(..., encoding='utf-8')` 로 취득한다 (ADR-081 §결정 D16 3항 앵커 provenance).
    packet·argv·env 등 promptfile 본문과 같은 채널을 타고 온 값을 앵커로 쓰면, 조립 계층이
    오염될 때 앵커와 본문이 **같이** 깨져 mojibake ↔ mojibake 자가일치로 assert 가 공허 통과한다.

════════════════════════════════════════════════════════════════════════════════
write 모드 (권장 — dispatch 경로 의무)
════════════════════════════════════════════════════════════════════════════════

  1. stdin raw **bytes** = 조립 원본을 읽는다 (텍스트 래퍼 경유 금지 — 상위 계층 디코딩 개입 차단).
  2. strict UTF-8 decode. invalid byte = 위반(exit 1).
  3. BOM(U+FEFF) 이 선두면 위반(exit 1). promptfile 은 always-UTF-8 을 mandate 하는 우리 소유
     생산-소비 폐쇄 채널이라 signature 기능이 무용하고, 앵커·골격 오프셋만 오염시킨다
     [source: RFC 3629 §6 — "A protocol SHOULD forbid use of U+FEFF as a signature for those textual
     protocol elements that the protocol mandates to be always UTF-8"]. 강도 = SHOULD (MUST 아님) —
     일부 Windows 도구의 BOM 판별 힌트 관행을 부정하지 않되, 폐쇄 채널에선 거부가 옳다.
  4. `--out` 에 `encoding='utf-8', newline=''` 로 write (개행 변환 0 — Windows CRLF 자동 변환은
     내용 대조를 born-broken 으로 만든다).
  5. re-read: `encoding='utf-8', newline=''` 로 다시 읽는다.
  6. **내용 동일성 대조** — (2) 의 in-memory 원본 문자열과 (5) 의 re-read 전문이 완전히 같아야 한다.
     불일치 = 위반(exit 1). ★ 이 단계가 write 모드의 핵심 기제다 — 앵커 assert 만으로 대체하면
     본문만 변이된 경우를 놓친다 (anchor-assert-only hollow).
  7. **한글 앵커 assert** — whitelist 파일에서 취득한 앵커 라인이 re-read 결과에 verbatim 존재.
  8. **partition 검사** (아래) 수행.
  전부 통과 = exit 0.

════════════════════════════════════════════════════════════════════════════════
verify 모드 (degrade — 사후 감사 한정)
════════════════════════════════════════════════════════════════════════════════

  기존 파일 strict decode + BOM 검사 + 앵커 assert + partition 검사만 수행한다.
  ★ **내용 동일성은 보증하지 않는다** — 조립 원본 in-memory 텍스트가 없으므로 대조할 기준선 자체가
  없다. 따라서 verify 단독으로 AC-4 충족을 주장할 수 없다 (정직 라벨).
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

  (a) **블록 구조 정합** — open/close 짝 일치 + 같은 nonce. 짝 불일치, 중첩, close 선행,
      그리고 **블록 본문 안에서의 sentinel 라인 재출현** = 위반(exit 1).
      (조립 계층에서도 동일 검출을 하지만, 조립측이 escape 를 빠뜨려도 여기서 fail-closed 된다.)
  (b) **블록 외부 텍스트 = 한글 0** — 구획 A 영어 강제의 조립 시점 기계화.
      한글 문자 클래스 = U+AC00-D7A3 (음절) ∪ U+1100-11FF (자모) ∪ U+3130-318F (호환자모)
      ∪ U+A960-A97F, U+D7B0-D7FF (확장 A/B). `가-힣` 단독은 `ㄱ`(U+3131) 을 놓치므로 불가.
      제외는 **정확히 2종**:
        · whitelist 등재 리터럴 — **토큰 단위** 제외 (줄 단위 면제 금지: 등재 토큰을 한 줄에
          끼워넣어 그 줄 전체를 면제받는 우회 차단).
        · 한글 앵커 라인 — **줄 단위** 제외 (조립 규약이 정한 고정 헤더, 별개 축).
      그 외 블록 외부 한글 = 위반(exit 1).
  비-ASCII 기호(`— § ② →` 등) 잔존은 위반이 **아니다** — floor 는 한글 0 이며, ASCII-화는
  이론 근거일 뿐 본 Story 의 달성 요구가 아니다 (ADR-081 Amendment 15-D 거절 대안).

════════════════════════════════════════════════════════════════════════════════
whitelist 소비 계약
════════════════════════════════════════════════════════════════════════════════

  · 엔트리 라인 = `^<literal>\\t<근거 SSOT 경로>$` (TAB 1개 구분). 그 외 줄은 파싱 대상 아님.
  · 앵커 라인 = `^ANCHOR_LINE: ` 로 시작하는 **유일한** 줄. 0개·2개 이상 = setup error(exit 2).
  · 형식 제약 위반 (길이 >32자 / 공백 포함 / 엔트리 >30 / 빈 토큰) = 위반(exit 1).
  · **validity self-check** — 각 엔트리의 근거 경로 실재 ∧ 그 파일 안에 literal grep 실재.
    위반(경로 소멸·리터럴 개명/삭제) = 위반(exit 1). 정직 천장: 기계 대조는 *존재·경로 실재*까지이며
    등재 리터럴이 원 SSOT 와 **의미상** 같은 것을 가리키는지는 판정 불가 (리뷰 lane 소관).
  · 엔트리 공집합 = 제외 0 (안전 방향, 정상). 단 **파일 부재 = setup error(exit 2)** —
    "제외 0 으로 계속" 금지 (whitelist 소멸이 조용히 통과되는 경로 차단).

════════════════════════════════════════════════════════════════════════════════
Exit code (closed enum — 이 밖의 값 반환 금지)
════════════════════════════════════════════════════════════════════════════════

  0 = PASS.
  1 = 검증 위반 (RED) — invalid byte / BOM / 내용 불일치 / 앵커 부재 / partition 위반 /
      whitelist 형식·validity 위반.
  2 = setup error — 인자 오류, whitelist 파일 부재, 앵커 라인 0개·2개+, 빈 promptfile
      (`"" == ""` 공허 통과 차단), --out/--in 미지정, 파일 I/O 실패.
  ※ 호출측 (CodexReviewAgent dispatch) 은 rc != 0 이면 codex 를 호출하지 않고 dispatch 를 중단한다
    (verdict=inconclusive + marker `[promptfile-encoding-assert-failed: rc=<n>]`). 재조립 ≤1회,
    초과 = ESCALATE (자동 재시도 금지 — 입력 결함은 재시도로 낫지 않는다).

════════════════════════════════════════════════════════════════════════════════
보증 한계 (정직 천장 — ADR-119)
════════════════════════════════════════════════════════════════════════════════

  · 본 helper 가 확보하는 것은 **conditional integrity** ("실행됐다면 L1 산출물 내용이 원본과 같다")
    이며, **실행이 실제로 있었는가**(execution existence) 는 별개 축이다 — 후자는 promptfile·out.json
    실물 + PL 독립 확인으로만 falsify 되고 기계 게이트 불가.
  · L3 소비자(codex CLI) 측 오디코딩 잔여 리스크는 상류 미해결 이슈(openai/codex #4013, open) 로
    남는다 — "완전 차단" 서술 금지. 도달 보증 = L1 내용 동일성 + 노출 표면 축소.
  · `LC_ALL`/`LANG` env 는 Python-on-Windows 파일 I/O 에 무효다 (2급 defense-in-depth).
    1급 방어는 본 helper 코드계층의 명시 `encoding='utf-8'` 이다.
"""

import argparse
import os
import sys

# Windows 콘솔 cp949 기본 인코딩에서 UTF-8 출력 실패 방지 (ADR-061 standardize).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXIT_PASS = 0
EXIT_VIOLATION = 1
EXIT_SETUP_ERROR = 2

STUB_MESSAGE = "NOT_IMPLEMENTED (stub — CFP-2884 TDD RED baseline)"

PROG = os.path.basename(__file__)


def build_parser():
    """CLI 계약 (module docstring SSOT) 의 argparse 구현."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Codex promptfile UTF-8 round-trip / 언어 구획 검증 "
            "(ADR-081 §결정 D16 3항). 현재 = STUB — 모든 실행 경로 exit 2."
        ),
        epilog=(
            "exit: 0=PASS / 1=검증 위반 / 2=setup error. "
            "앵커 값 주입 플래그는 의도적으로 없다 — 앵커는 --whitelist 파일에서 직접 취득한다."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("write", "verify"),
        required=True,
        help="write = stdin 조립 원본을 검증하며 --out 에 기록 (dispatch 경로 의무) / "
             "verify = 기존 --in 파일 사후 감사 (내용 동일성 미보증)",
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
        required=True,
        help="구획 A 한글 예외 + 한글 앵커 SSOT (파일 부재 = exit 2)",
    )
    parser.add_argument(
        "--nonce",
        metavar="STR",
        default=None,
        help="구획 B delimiter 의 per-invocation nonce. 제공 시 nonce 일치까지 assert "
             "(생략 시 파일에서 유도 — nonce 진위 미검증, 검사 강도 하향)",
    )
    return parser


def validate_mode_args(parser, args):
    """모드별 필수 인자 상호 배제 검증 — 위반 시 argparse 경유 exit 2."""
    if args.mode == "write":
        if not args.out:
            parser.error("--mode write 는 --out <path> 필수")
        if args.in_path:
            parser.error("--mode write 에 --in 사용 불가 (조립 원본은 stdin)")
    else:  # verify
        if not args.in_path:
            parser.error("--mode verify 는 --in <path> 필수")
        if args.out:
            parser.error("--mode verify 에 --out 사용 불가 (write 금지 모드)")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_mode_args(parser, args)

    # ── STUB ──────────────────────────────────────────────────────────────────
    # 검증 로직 미구현. 계약(docstring)만 확정된 TDD RED baseline 상태이며,
    # write/verify 어느 경로든 PASS(0)·위반(1) 을 반환하지 않는다 — 공허 GREEN 차단.
    print(STUB_MESSAGE, file=sys.stderr)
    return EXIT_SETUP_ERROR


if __name__ == "__main__":
    sys.exit(main())
