#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/ac_pr_markers.py
CFP-2659 / ADR-145 §결정 11 Amendment 5 — PR body 마커 파싱 pure leaf.

본 모듈 = ac-traceability 게이트 어댑터가 소비하는 **PR body 마커 추출 SSOT**.
`.github/workflows/ac-traceability-matrix.yml` 의 inline-JS 정규식 3개를 여기로 추출했다
(decoupling refactor — `ac_id.py` 형제 leaf).

leaf 불변식: 역방향 의존만 — `check_ac_traceability_matrix` 를 import 하지 않는다(순환 금지).
pure: 네트워크 0, 파일 I/O 0(파일 읽기는 하단 CLI 층 전용). 순수 파싱 의존은 `re` 뿐.

추출한 사실 ≠ verdict (CRITICAL — 경계):
  본 모듈은 마커의 **기계적 존재/값**만 보고한다. 적용성 verdict(precedence / none 위장 /
  surface-override 판별)는 core `check_ac_traceability_matrix.classify_ac_source` 단일소유 —
  여기서 재구현하지 않는다. `both_absent` 조차 "마커 0개"라는 추출 사실이지 판정이 아니다.

F1 (marker-format false-red) — 본 모듈이 봉인하는 결함:
  구 inline-JS `body.match(/story_uri:\s*(\S+)/)` 는 markdown 장식 마커를 놓쳤다.
  `**story_uri**:` (키 bold) / `- **story_uri**:` (list+bold) → NO match → both-absent →
  정상 PR 이 false-red FAIL (실측 2/7 PR). 장식-tolerant 파싱으로 정정한다.

  단 tolerance 가 false-green 을 열면 안 된다 — **line-start anchor** 로 산문 언급
  (`여기서 story_uri: 필드가 필요`) 은 계속 미매치한다.

ReDoS-safe (비협상 — §7.6 S7-5):
  어댑터 job 은 fork PR body 를 **토큰 확인 이전**에 파싱한다(pre-auth 도달면).
  ∴ 모든 수량자는 bounded(`\*{0,2}`) + per-line `^` anchor. 인접/중첩 unbounded 수량자 0
  (catastrophic backtracking 경로 부재 — 매칭은 라인 길이에 선형).

ADR refs: ADR-145 §결정 11 Amendment 5 (marker-format false-red 정정 + 파싱 pure 모듈 추출) /
  ADR-145 §결정 9 (ac_applicability: none 마커 — INPUT, verdict=core) / ADR-061 §결정 1
  (Python SSOT leaf + thin bash wrapper).
"""

import argparse
import json
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# 마커 문법 SSOT — 장식 tolerance (bounded, marker-anchored).
#
#   ^[ \t]*            라인 선두 들여쓰기만 허용 (per-line anchor — 산문 중간 매칭 금지 = false-green 차단).
#   (?:[-*][ \t]+)?    markdown list 마커 (`- ` / `* `) optional.
#   \*{0,2}            markdown bold 여는 마커 — **bounded**(최대 2). `\*+` 류 unbounded 금지(ReDoS).
#   <key>              마커 키 리터럴.
#   \*{0,2}            키-bold 닫는 마커 (`**story_uri**:` 형).
#   [ \t]*:[ \t]*      콜론 주변 공백 변이 수용.
#   (\S+)              값 캡처. 값-bold 두 형(`**story_uri: url**` = trailing `**` 혼입 / `story_uri: **url**`
#                      = leading+trailing `**` 혼입)을 _strip_bold_decor() 로 양방향 clean-strip (dirty `**` 혼입 0).
#
# 수용 형태: plain / 키bold / 값bold / list / list+bold / 공백 변이.
# 미수용(의도적): 산문 중간 언급(line-start 아님) / 값 부재(`story_uri**:`) → 미인식 → both_absent 경로.
#   → 미인식은 FAIL 방향(fail-closed)이지 PASS 방향이 아니다 (false-green 안 열림).
# ─────────────────────────────────────────────────────────────────────────────
_STORY_URI_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?\*{0,2}story_uri\*{0,2}[ \t]*:[ \t]*(\S+)", re.MULTILINE
)
_RTM_URI_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?\*{0,2}rtm_uri\*{0,2}[ \t]*:[ \t]*(\S+)", re.MULTILINE
)
# `ac_applicability: none — <사유>` (ADR-145 §결정 9). 값 `none` 만 정의 —
#   skip / n/a / false 는 **미인식**(none 아님 → both_absent 경로). 구 inline-JS `none\b` 와 동형
#   (AC-10 원 규약 보존 — 본 Story 는 장식 tolerance 만 추가, 값 판별 규약 무변경).
_NONE_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?\*{0,2}ac_applicability\*{0,2}[ \t]*:[ \t]*none\b[ \t]*[—–-]?[ \t]*(.*)",
    re.MULTILINE,
)

# 값-bold clean-strip 상한 — markdown strong 마커 `**` = 최대 2 asterisk (방향당).
#   무제한 strip 대신 양방향 bounded loop(leading+trailing, 방향당 ≤2)로 정규식 `\*{0,2}` tolerance 와 대칭을 유지한다.
_MAX_BOLD_ASTERISKS = 2


def _strip_bold_decor(value):
    r"""캡처값 앞뒤의 markdown bold 마커 제거 (값-bold clean capture, 양방향 대칭).

    whole-marker-bold(`**story_uri: url**`) → 캡처 `url**` → trailing strip → `url`.
    value-only-bold(`story_uri: **url**`)   → 캡처 `**url**` → trailing+leading strip → `url`.
    bounded — 방향당 최대 _MAX_BOLD_ASTERISKS(2) (정규식 `\*{0,2}` tolerance 와 대칭).
    순수 슬라이스(방향당 ≤2회 char 검사) — 상수시간, regex 무변경(ReDoS 무관).
    """
    if not value:
        return value
    out = value
    for _ in range(_MAX_BOLD_ASTERISKS):   # trailing (기존)
        if out.endswith("*"):
            out = out[:-1]
        else:
            break
    for _ in range(_MAX_BOLD_ASTERISKS):   # leading (신규 대칭)
        if out.startswith("*"):
            out = out[1:]
        else:
            break
    return out


def _extract_uri(pattern, body):
    """URI 마커 1종 추출 — 첫 유효 매치 우선(.search). 미발견/빈 값 = None.

    빈 값 정규화: `story_uri: **` 같은 degenerate 캡처는 strip 후 빈 문자열이 되므로 None 으로
      환원한다 (URI 부재 = both_absent 경로 = fail-closed. 빈 문자열을 URI 로 흘리지 않음).
    """
    m = pattern.search(body)
    if not m:
        return None
    uri = _strip_bold_decor(m.group(1))
    return uri if uri else None


def parse_pr_body(body):
    """PR body 에서 마커 3종 추출 (pure — verdict 아님, 기계적 추출 사실만).

    Args:
      body: PR body 원문(str). str 아님/None = 빈 body 취급(마커 0개).

    Returns:
      dict:
        story_uri     : str | None   — 장식 strip 후 clean URI (미발견 = None).
        none_declared : bool         — `ac_applicability: none` 마커 존재.
        none_reason   : str          — none 마커 뒤 사유 (없으면 ""). 빈 사유 검증은 core(AC-2).
        rtm_uri       : str | None   — 장식 strip 후 clean URI (미발견 = None).
        both_absent   : bool         — story_uri 부재 ∧ none 미선언 (마커 0개 = 기계적 사실).

    경계 (재확인 — 본 모듈은 thin extractor):
      `both_absent` 는 **추출 사실**이지 verdict 가 아니다. 적용성 판정(precedence / none 위장 /
      surface-override)은 core `classify_ac_source` 단일소유 — 어댑터는 flag forward 만 한다.
    """
    if not isinstance(body, str):
        body = ""

    story_uri = _extract_uri(_STORY_URI_RE, body)
    rtm_uri = _extract_uri(_RTM_URI_RE, body)

    none_m = _NONE_RE.search(body)
    none_declared = none_m is not None
    none_reason = ""
    if none_m:
        # 값-bold(`**ac_applicability: none — 사유**`) 꼬리 `**` 제거 후 공백 정리.
        none_reason = _strip_bold_decor((none_m.group(1) or "").strip()).strip()

    return {
        "story_uri": story_uri,
        "none_declared": none_declared,
        "none_reason": none_reason,
        "rtm_uri": rtm_uri,
        "both_absent": story_uri is None and not none_declared,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI 층 (additive) — 파일 I/O 는 여기서만. 어댑터(github-script)가 JSON 1 object 를 소비한다.
#   호출: python3 scripts/lib/ac_pr_markers.py --parse-pr-body <FILE>
#   injection 가드(§7.6 S7-3): PR body 는 attacker-controlled → argv 아닌 **파일**로 전달받는다.
#     어댑터는 execFileSync arg-array(셸 미경유)로 호출한다.
#   본 CLI 는 기존 게이트 CLI(check_ac_traceability_matrix.py 2-value exit)를 침범하지 않는 별 leaf.
# ─────────────────────────────────────────────────────────────────────────────
def _main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ac_pr_markers.py",
        description="PR body 마커(story_uri / ac_applicability:none / rtm_uri) 추출 → JSON stdout.",
    )
    parser.add_argument(
        "--parse-pr-body",
        dest="pr_body_file",
        metavar="FILE",
        required=True,
        help="PR body 원문 파일 경로 (argv 직접 전달 금지 — injection 가드).",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.pr_body_file, "r", encoding="utf-8") as fh:
            body = fh.read()
    except OSError as exc:
        print(f"ac_pr_markers: PR body 파일 읽기 실패 — {exc}", file=sys.stderr)
        return 1

    json.dump(parse_pr_body(body), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
