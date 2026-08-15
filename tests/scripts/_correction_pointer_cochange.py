#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""_correction_pointer_cochange.py — 신규 정정 블록이 지목한 **선행 절의 co-change** 검사.

── 계기 (ADR-177 게이트가 원리적으로 못 잡는 재발) ─────────────────────────────
  ADR-177 ratchet 은 **한 줄 안의 어휘**(절대주장 토큰)를 본다. 이번 재발은 어휘가
  아니라 **편집 사이의 관계**다: 새 Amendment 블록이 앞 절의 결론을 뒤집는데, 그
  **앞 절에는 아무 표식도 남기지 않는다.** 독자는 뒤집힌 옛 문면을 그대로 읽는다.

  firsthand 실측(`8266e0e82`, ADR-172 Amendment 4 저작): `## Amendment 4` 헤더
  **이전 본문 전체**를 `Amendment 4|A4-` 로 grep 하면 hit 가 없다. Amd 4 는 A3-2
  대조표를 재작성하고 A3-4 의 잔여 라벨을 정정하면서 **두 절 어디에도 포인터를 남기지
  않았다.** 이 결손은 두 라운드 뒤 사람 리뷰로만 잡혔다.

  ★ ADR-177 로는 잡을 수 없다 — 빠진 것은 **어휘 토큰이 아니라 기존 줄의 부재**이고,
    신규-줄 어휘 스캐너의 정의역 밖이다(`_absolute_claim_ratchet.py::TOKENS` 실측).
    두 검사는 **정의역이 disjoint** 하다: 어휘(lexical) ↔ 관계(relational).

── 정의역 (좁게 고정) ──────────────────────────────────────────────────────────
  · 비교 축 = `origin/main...HEAD` 3-dot diff. §8.7 생성기
    (`scripts/lib/impl_manifest.py:git_diff_axis`) · ADR-177 ratchet 과 **같은 축**을
    쓴다 — 두 번째 기준을 정의하지 않는다.
  · 파일 = `archive/adr/**` 기본 (`--only` 로 조정).
  · **인용 줄**(citing line) = diff 의 **추가 줄** 중, post-image 에서 그 줄을 감싸는
    헤딩 사슬에 `## Amendment ...` 가 있는 것. 삭제 줄·문맥 줄은 인용원이 **아니다**.
    Amendment 밖의 평범한 `§결정 N` 상호참조는 같은 세대 교차참조이지 정정이 아니므로
    인용 정의역에서 뺀다(오탐원 제거).

── 절 ID 문법 (2 형태만) ───────────────────────────────────────────────────────
  · `A<n>-<m>`  — Amendment 하위 절. 꼬리 `A5-4-a` 허용.
  · `§결정 N`   — 결정 절. 소수점 `§결정 6.1` 허용.
  헤딩이 그 ID 로 **시작**할 때 그 헤딩이 해당 절을 선언한 것으로 본다
  (`### A3-2 — ...` → `A3-2` 선언).

── 판정 (인용 1건 단위) ────────────────────────────────────────────────────────
  ① 같은 줄 앞 24자 안에 **타 ADR 번호**가 붙어 있다   → `foreign`     (정의역 밖)
  ② 이 파일 헤딩으로 절 ID 가 해소되지 않는다           → `unresolved`  (정의역 밖)
  ③ 피인용 절 헤딩이 인용 줄 **뒤**에 있다              → `forward`     (통과)
  ④ 선행 절인데 같은 diff 에서 그 절이 편집됐다         → `cochanged`   (통과)
  ⑤ 선행 절인데 그 절이 **무편집**                      → `stale-pointer` (위반)

  ③이 통과인 이유: 옛 절이 뒤 Amendment 를 가리키는 것이 바로 **정정 포인터**다.
  요구하는 것은 그 반대 방향(뒤 블록이 앞 절을 지목) 뿐이다.

  ④의 "편집됐다" = 그 절의 post-image 줄 범위 안에
    (a) **공백이 아닌 추가 줄**이 있거나, (b) 삭제가 일어난 위치가 있다.
  공백만 있는 추가 줄을 빼는 이유: 블록 사이 빈 줄 하나가 직전 절 슬라이스 꼬리에
  걸려 **선행 절에 편집 공로를 헛되이 주는** 실물이 있었다(`8266e0e82` 의 `:377`
  빈 줄이 A3-5 슬라이스 `[368,378)` 꼬리에 들어갔다). 삭제 위치를 세는 이유는 그
  반대다 — 문장을 **지워서** 정정한 절이 거짓 위반이 되지 않게 한다.

── 절 경계 슬라이싱 = 선례 재사용 ──────────────────────────────────────────────
  절 범위는 새로 구현하지 않고 `scripts/lib/impl_manifest.py::extract_section` 을
  import 해 쓴다. 종료조건은 **레벨 ≤ 현재 레벨**이며,
  `tests/integration/test_scheduled_task_ac_matrix.py::extract_adr_section` 이
  구현리뷰 iter5 F-CR5-02 로 정정한 것과 같은 규칙이다. 두 선례가 서로 어긋나지
  않는지는 `test_two_section_helpers_agree_on_adr172` 가 회귀로 결박한다.
  ★ 이 Story 에서 **고정 창 슬라이싱**과 **h2 맹인 종료조건**이 각각 결함이었다 —
    그래서 창작 대신 이미 오라클로 결박된 구현을 가져온다.

  diff 파싱도 마찬가지로 `_absolute_claim_ratchet.py::parse_added_lines` 라는 검증된
  선례가 있다. 본 모듈은 삭제 위치까지 필요해 한 번의 walk 로 둘을 함께 걷되,
  그 walk 의 추가-줄 출력이 선례와 **동일한지**를
  `test_walk_added_lines_match_ratchet_parser` 가 매 실행 대조한다(drift 차단).

── 정직 천장 (ADR-119 — 이 검사가 **못 하는** 것) ───────────────────────────────
  ① **co-change 는 pointer 가 아니다.** 피인용 절의 *어떤* 편집이든 ④로 통과한다 —
     그 편집이 정정 포인터인지, 오탈자 수정인지 판정하지 않는다. 이것은 ADR-177
     천장 ①(`tests/**` 동반 강제)과 **같은 약점 class 이며, 상속한다.** "이번엔
     다르다" 가 아니다. 리포트가 ④ 통과 건을 전량 열거해 이 느슨함을 로그에 남긴다.
  ② **절 ID 를 인용하지 않고 뒤집으면 미검출.** "위 표는 사실 틀렸다" 처럼 ID 없이
     앞 절을 무효화하는 서술은 이 검사의 정의역 밖이다. ADR-177 의 패러프레이즈
     false-negative 와 **동형이며, 상속한다.**
  ③ **cross-repo 공백.** Change Plan · Story 는 codeforge-internal-docs 소재라
     wrapper CI 가 도달하지 않는다. 같은 재발이 그 문서들에서 일어나면 못 잡는다.
  ④ **계측기 차원 부재 class 는 정의역 밖.** 측정기가 잰 차원 자체가 빠졌는지는
     문서 간 관계가 아니라 측정 설계의 문제다.
  ⑤ **Amendment 레벨 지시자(`Amd 2` / `Amendment 3`)는 절 ID 로 세지 않는다.**
     `A<n>-<m>` · `§결정 N` 두 형태만 본다. 산문에서 `Amd 2 본문` 은 대개 앞 절의
     **문면을 인용**하는 use/mention 이라 지목과 구분이 되지 않는다(실물:
     `b41e69af9` 의 A5-3 서술이 A4-3 의 오지목 문구를 따옴표로 인용한다).
  ⑥ 판정은 **커밋된 내용** 기준이다. 워킹트리 미커밋 수정은 3-dot diff 에 없다.
  ⑦ **참조와 뒤집기를 구분하지 못한다 — 반대 방향의 오발화.** Amendment 안에서
     앞 절을 그냥 *참조*만 해도(제약 인용·근거 인용) 같은 요구가 걸린다. 이 구분은
     어휘·의미 판정을 요구하는데 그것은 이 검사의 설계 전제(관계만 본다)를 깨므로
     하지 않는다. 실측 오발화 1건: `origin/main...b41e69af9` 축에서 `§결정 4` 가
     A1-3 `:275` · A5-4-c `:585` 의 *"「신규 플래그 0건」 정신"* 인용만으로 걸렸다
     (그 절은 뒤집히지 않았다). 같은 축의 `§결정 6` 은 반대로 **참 양성**이다 —
     Amd 1 · Amd 2 헤더가 *"§결정 6 … 좁힘"* 이라 선언했는데 그 절(`:111`-`:120`)
     에는 표식이 없고, `:249` 는 *"§결정 6 본문 행은 무편집 보존"* 이라고 적어 뒀다.
     ⇒ 이 검사의 위반 목록은 **후속 판단이 필요한 후보 목록**이지 확정 결함 목록이
       아니다. required 승격을 하지 않는 이유도 여기에 있다.

  ⇒ 이 검사가 세우는 것은 *"정정 포인터가 기계 강제된다"* 가 **아니라**
    「**절 ID 를 인용한 신규 Amendment 블록에 한해, 피인용 선행 절의 co-change 를
    요구한다**」 까지다.
"""

import argparse
import os
import re
import subprocess
import sys
from collections import namedtuple

COCHANGE_VERSION = "correction-pointer-cochange v1"

# 기본 파일 정의역. ADR 이 이 절 ID 문법의 소재지다.
DEFAULT_PREFIXES = ("archive/adr/",)

# ── 절 ID 문법 ──────────────────────────────────────────────────────────────────
# `A<n>-<m>[-<letter>]` 와 `§결정 N[.M]`. Amendment 레벨 지시자는 담지 않는다(천장 ⑤).
_SEC_ID_ALT = r"(?<![0-9A-Za-z])A\d+-\d+(?:-[a-z])?(?![0-9A-Za-z])|§결정\s*\d+(?:\.\d+)?"
_SECTION_ID_RE = re.compile(_SEC_ID_ALT)
# 헤딩이 선언하는 절 ID — `#` 들과 강조기호를 지난 **선두**에서만 읽는다.
_HEADING_ID_RE = re.compile(r"^#{1,6}[ \t]+[*_ \t]*(" + _SEC_ID_ALT + r")")
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+\S")
# `## Amendment 4 ...` / `## Amd 4 ...` — 인용 정의역의 울타리.
_AMENDMENT_HEADING_RE = re.compile(r"^#{1,6}[ \t]+[*_ \t]*(?:Amendment|Amd)\b")
# 타 ADR 지목 판별 (같은 줄 앞쪽 좁은 창).
_ADR_REF_RE = re.compile(r"ADR-(\d+)")
_ADR_IN_PATH_RE = re.compile(r"ADR-(\d+)")
FOREIGN_LOOKBACK = 24

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_DIFF_GIT_RE = re.compile(r"^diff --git ")

AddedLine = namedtuple("AddedLine", "path lineno text")
Heading = namedtuple("Heading", "lineno level raw sec_id is_amendment")
Citation = namedtuple("Citation", "path lineno sec_id target_lineno disposition reason text")

FAIL_DISPOSITIONS = ("stale-pointer",)
UNDECIDED_DISPOSITIONS = ("undecidable",)

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_BASE_UNRESOLVED = 2


# ═══════════════════════════ diff walk (pure) ═══════════════════════════════════
def _strip_ab_prefix(spec):
    """`b/path` · `a/path` → `path`. `/dev/null` → None."""
    spec = spec.strip()
    if spec == "/dev/null":
        return None
    for pre in ("a/", "b/"):
        if spec.startswith(pre):
            return spec[len(pre):]
    return spec or None


def walk_diff(diff_text):
    """unified diff → `(added, deleted_anchors, touched_paths)` 한 번의 walk.

    · `added`            = `[AddedLine(path, post-image lineno, text)]`
    · `deleted_anchors`  = `{path: {post-image position, ...}}` — 삭제가 일어난 자리.
                           삭제 줄은 post-image 행번호가 없으므로 **삭제 시점의 새
                           파일 커서 위치**를 앵커로 쓴다.
    · `touched_paths`    = diff 가 건드린 경로 집합.

    hunk 헤더의 **행수를 소진**하며 읽는다 — `+`/`-` 접두만 보고 갈라내면 hunk 본문의
    `--- x` / `+++ y` 내용 줄을 파일 헤더로 오인한다(`_absolute_claim_ratchet` 선례의
    같은 주의). 문맥 줄은 새 파일 행번호를 전진시키는 역할만 하며 결과에 담지 않는다.
    """
    added = []
    deleted = {}
    touched = set()
    path = None
    prev_minus = None
    new_lineno = 0
    old_rem = new_rem = 0
    in_hunk = False

    for raw in diff_text.splitlines():
        if in_hunk and (old_rem > 0 or new_rem > 0):
            if raw.startswith("\\"):            # "\ No newline at end of file"
                continue
            if raw.startswith("+"):
                if path is not None:
                    added.append(AddedLine(path, new_lineno, raw[1:]))
                new_lineno += 1
                new_rem -= 1
            elif raw.startswith("-"):
                if path is not None:
                    deleted.setdefault(path, set()).add(new_lineno)
                old_rem -= 1
            else:                                # 문맥 줄 (" " 접두 또는 빈 줄)
                new_lineno += 1
                new_rem -= 1
                old_rem -= 1
            if old_rem <= 0 and new_rem <= 0:
                in_hunk = False
            continue

        in_hunk = False
        m = _HUNK_RE.match(raw)
        if m:
            new_lineno = int(m.group(3))
            old_rem = int(m.group(2)) if m.group(2) is not None else 1
            new_rem = int(m.group(4)) if m.group(4) is not None else 1
            in_hunk = old_rem > 0 or new_rem > 0
            continue
        if _DIFF_GIT_RE.match(raw):
            path = None
            prev_minus = None
            continue
        if raw.startswith("--- "):
            prev_minus = _strip_ab_prefix(raw[4:])
            continue
        if raw.startswith("+++ "):
            path = _strip_ab_prefix(raw[4:])
            if path:
                touched.add(path)
            elif prev_minus:
                touched.add(prev_minus)         # 삭제된 파일은 `a/` 쪽에서 건진다
            prev_minus = None
            continue
    return added, deleted, touched


# ═══════════════════════════ 헤딩 색인 (pure) ════════════════════════════════════
def normalize_sec_id(sec_id):
    """`§결정  9` · `§결정9` → `§결정 9`. `A3-2` 는 그대로."""
    s = sec_id.strip()
    if s.startswith("§결정"):
        digits = s[len("§결정"):].strip()
        return "§결정 %s" % digits
    return s


def build_heading_index(text):
    """문서 텍스트 → `[Heading]` (문서 순서). 줄번호는 1-based."""
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = _HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        idm = _HEADING_ID_RE.match(line)
        sec_id = normalize_sec_id(idm.group(1)) if idm else None
        out.append(Heading(i, level, line, sec_id,
                           bool(_AMENDMENT_HEADING_RE.match(line))))
    return out


def _load_extract_section():
    """절 슬라이싱은 **선례를 import** 한다 — 새로 구현하지 않는다.

    `scripts/lib/impl_manifest.py::extract_section` 의 종료조건(레벨 ≤ 현재 레벨)은
    `test_scheduled_task_ac_matrix.py::extract_adr_section` 이 iter5 F-CR5-02 로
    정정한 규칙과 같다. 두 helper 는 이미 회귀 오라클로 결박돼 있다."""
    lib = os.path.join(repo_root_from(), "scripts", "lib")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    from impl_manifest import extract_section
    return extract_section


def section_span(text, heading, extract_section=None):
    """`Heading` → post-image 줄 범위 `(start, end)` (end 배타, 1-based).

    끝 경계는 직접 계산하지 않고 선례 슬라이서가 돌려준 **줄 수**로 얻는다."""
    extract = extract_section or _load_extract_section()
    sec = extract(text, heading.raw)
    if sec is None:
        return None
    return heading.lineno, heading.lineno + len(sec.splitlines())


# ═══════════════════════════ 인용 추출 (pure) ════════════════════════════════════
def cited_ids(line_text, own_adr=None):
    """줄 텍스트 → `[(sec_id, is_foreign)]`.

    `is_foreign` = 같은 줄 앞 `FOREIGN_LOOKBACK` 자 안에 **다른 ADR 번호**가 있다.
    `ADR-171 §결정 5` 를 이 파일의 `§결정 5` 로 오해석하는 것을 막는다."""
    out = []
    for m in _SECTION_ID_RE.finditer(line_text):
        start = m.start()
        window = line_text[max(0, start - FOREIGN_LOOKBACK):start]
        refs = _ADR_REF_RE.findall(window)
        foreign = bool(refs) and (own_adr is None or int(refs[-1]) != own_adr)
        out.append((normalize_sec_id(m.group(0)), foreign))
    return out


def own_adr_number(path):
    """`archive/adr/ADR-172-....md` → 172. 형식 밖이면 None."""
    m = _ADR_IN_PATH_RE.search(os.path.basename(path or ""))
    return int(m.group(1)) if m else None


def amendment_line_ranges(text, headings=None, extract_section=None):
    """`## Amendment ...` 절들이 덮는 줄 범위 목록 — 인용 정의역의 울타리."""
    heads = headings if headings is not None else build_heading_index(text)
    spans = []
    for h in heads:
        if not h.is_amendment:
            continue
        span = section_span(text, h, extract_section)
        if span:
            spans.append(span)
    return spans


def in_any_span(lineno, spans):
    return any(a <= lineno < b for a, b in spans)


# ═══════════════════════════ 판정 (pure) ════════════════════════════════════════
def is_preceding(target_lineno, citing_lineno):
    """피인용 절이 인용 줄보다 **앞**에 있는가 = 뒤집기 방향인가.

    같은 줄(자기 헤딩이 자기 ID 를 담는 경우)은 앞이 아니다. 뒤에 있는 절을 가리키는
    것은 정정 포인터 그 자체이므로 요구 대상이 아니다(판정 ③)."""
    return target_lineno < citing_lineno


def section_is_cochanged(span, added_linenos, deleted_anchors):
    """절 범위가 같은 diff 에서 편집됐는가.

    공백만 있는 추가 줄은 증거로 세지 않는다(절 사이 빈 줄이 직전 절 꼬리에 걸려
    헛된 공로를 준다). 삭제 앵커는 센다(지워서 한 정정이 거짓 위반이 되지 않게)."""
    a, b = span
    if any(a <= n < b for n in added_linenos):
        return True
    return any(a <= n < b for n in deleted_anchors)


def evaluate(diff_text, post_images, only_prefixes=DEFAULT_PREFIXES, extract_section=None):
    """diff + post-image 본문 → 판정 결과 dict (순수 — git 호출 없음).

    `post_images` = `{path: 파일 전체 텍스트}`. 정의역 안 경로인데 본문이 없으면
    **조용히 통과시키지 않고** `undecidable` 로 남긴다."""
    extract = extract_section or _load_extract_section()
    added, deleted, touched = walk_diff(diff_text)

    by_path = {}
    for a in added:
        if only_prefixes and not any(a.path.startswith(p) for p in only_prefixes):
            continue
        by_path.setdefault(a.path, []).append(a)

    citations = []
    for path, lines in sorted(by_path.items()):
        text = post_images.get(path)
        if text is None:
            citations.append(Citation(path, 0, "-", None, "undecidable",
                                      "post-image 본문 미해소 — 절 경계를 잴 수 없다", ""))
            continue

        headings = build_heading_index(text)
        # 절 ID → 첫 선언 헤딩 (중복 선언 시 선두 채택)
        decl = {}
        for h in headings:
            if h.sec_id and h.sec_id not in decl:
                decl[h.sec_id] = h
        amd_spans = amendment_line_ranges(text, headings, extract)

        content_added = {a.lineno for a in lines if a.text.strip()}
        del_anchors = deleted.get(path, set())

        for a in lines:
            if not in_any_span(a.lineno, amd_spans):
                continue                        # Amendment 밖 = 인용 정의역 밖
            own = own_adr_number(path)
            for sec_id, foreign in cited_ids(a.text, own):
                if foreign:
                    citations.append(Citation(path, a.lineno, sec_id, None, "foreign",
                                              "타 ADR 지목 — 이 문서의 절이 아니다", a.text))
                    continue
                target = decl.get(sec_id)
                if target is None:
                    citations.append(Citation(path, a.lineno, sec_id, None, "unresolved",
                                              "이 문서 헤딩으로 해소되지 않는다", a.text))
                    continue
                if target.lineno == a.lineno:
                    continue                    # 헤딩이 자기 ID 를 담은 것 — 인용이 아니다
                if not is_preceding(target.lineno, a.lineno):
                    citations.append(Citation(path, a.lineno, sec_id, target.lineno, "forward",
                                              "피인용 절이 뒤에 있다 — 정정 포인터 방향",
                                              a.text))
                    continue
                span = section_span(text, target, extract)
                if span is None:
                    citations.append(Citation(path, a.lineno, sec_id, target.lineno,
                                              "undecidable", "절 범위 슬라이싱 실패", a.text))
                    continue
                if section_is_cochanged(span, content_added, del_anchors):
                    citations.append(Citation(
                        path, a.lineno, sec_id, target.lineno, "cochanged",
                        "선행 절 %s (`:%d`-`:%d`) 이 같은 diff 에서 편집됨 — 편집 종류는 "
                        "판정하지 않는다" % (sec_id, span[0], span[1] - 1), a.text))
                else:
                    citations.append(Citation(
                        path, a.lineno, sec_id, target.lineno, "stale-pointer",
                        "선행 절 %s (`:%d`-`:%d`) 무편집 — 뒤집힌 옛 문면이 표식 없이 "
                        "남는다" % (sec_id, span[0], span[1] - 1), a.text))

    # 같은 (경로, 절 ID) 위반은 한 건으로 접어 보고한다(줄마다 반복 금지).
    violations = []
    seen = set()
    for c in citations:
        if c.disposition not in FAIL_DISPOSITIONS:
            continue
        key = (c.path, c.sec_id)
        if key in seen:
            continue
        seen.add(key)
        violations.append(c)

    return {
        "version": COCHANGE_VERSION,
        "changed_files": sorted(touched),
        "added_lines": len(added),
        "citations": citations,
        "violations": violations,
        "undecidable": [c for c in citations if c.disposition in UNDECIDED_DISPOSITIONS],
    }


def format_report(result, show_passed=True):
    """판정 결과 → 사람이 읽는 줄 목록. ④(co-change 통과)도 열거해 느슨함을 드러낸다."""
    lines = []
    order = {"stale-pointer": 0, "undecidable": 1, "cochanged": 2,
             "forward": 3, "unresolved": 4, "foreign": 5}
    shown = set()
    # 위반은 (경로, 절 ID) 1건으로 접고 **인용한 줄을 전부** 붙인다 — 같은 절을 여러 줄이
    # 지목해도 고칠 곳은 하나(그 절)이므로, 줄마다 반복하면 리포트가 부풀 뿐이다.
    cite_lines = {}
    for c in result["citations"]:
        if c.disposition in FAIL_DISPOSITIONS:
            cite_lines.setdefault((c.path, c.sec_id), []).append(c.lineno)
    for c in sorted(result["citations"],
                    key=lambda c: (order.get(c.disposition, 9), c.path, c.lineno, c.sec_id)):
        fail = c.disposition in FAIL_DISPOSITIONS
        if not fail and not show_passed:
            continue
        key = (c.disposition, c.path, c.sec_id)         # 같은 절 반복 인용은 1줄로
        if key in shown:
            continue
        shown.add(key)
        if fail:
            at = sorted(set(cite_lines.get((c.path, c.sec_id), [])))
            where = ",".join(str(n) for n in at)
            lines.append("FAIL %s  [인용: %s @ %s]  %s" % (c.path, c.sec_id, where, c.reason))
        else:
            lines.append("ok   %s:%d  [인용: %s]  %s" % (c.path, c.lineno, c.sec_id, c.reason))
    tally = {}
    for c in result["citations"]:
        tally[c.disposition] = tally.get(c.disposition, 0) + 1
    n_co = tally.get("cochanged", 0)
    lines.append("요약: 위반 %d · cochanged %d · forward %d · unresolved %d · foreign %d "
                 "(추가줄 %d 중 인용 %d)"
                 % (len(result["violations"]), n_co, tally.get("forward", 0),
                    tally.get("unresolved", 0), tally.get("foreign", 0),
                    result["added_lines"], len(result["citations"])))
    if n_co:
        lines.append("주의: cochanged %d 건은 **피인용 절에 어떤 편집이든 있었다**는 뜻이며, "
                     "그 편집이 정정 포인터인지는 이 검사가 판정하지 않는다(천장 ①)." % n_co)
    return lines


# ═══════════════════════════ git 실측 (impure) ═══════════════════════════════════
def _run(cmd, cwd, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def repo_root_from(start=None):
    if start:
        return os.path.abspath(start)
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def diff_text_from_git(repo_root=None, base_ref="origin/main", head="HEAD"):
    """`git diff -U0 <base>...<head>` 원문. base 미해소 시 `None`(조용한 통과 금지)."""
    root = repo_root_from(repo_root)
    probe = _run(["git", "rev-parse", "--verify", "--quiet", base_ref + "^{commit}"], root)
    if probe.returncode != 0:
        return None
    cp = _run(["git", "diff", "--no-color", "--no-ext-diff", "-U0",
               "%s...%s" % (base_ref, head)], root)
    if cp.returncode != 0:
        return None
    return cp.stdout or ""


def post_images_from_git(paths, repo_root=None, rev="HEAD"):
    """`{path: <rev> 시점 본문}`. 해당 rev 에 없는 경로(삭제 등)는 담지 않는다."""
    root = repo_root_from(repo_root)
    out = {}
    for p in paths:
        cp = _run(["git", "show", "%s:%s" % (rev, p)], root)
        if cp.returncode == 0:
            out[p] = cp.stdout
    return out


def run_git(repo_root=None, base_ref="origin/main", head="HEAD",
            only_prefixes=DEFAULT_PREFIXES):
    """git 실측 → `evaluate` 결과. base 미해소면 `None`."""
    root = repo_root_from(repo_root)
    diff = diff_text_from_git(root, base_ref, head)
    if diff is None:
        return None
    added, _deleted, _touched = walk_diff(diff)
    want = sorted({a.path for a in added
                   if not only_prefixes or any(a.path.startswith(p) for p in only_prefixes)})
    images = post_images_from_git(want, root, head)
    return evaluate(diff, images, only_prefixes)


# ═══════════════════════════ CLI ════════════════════════════════════════════════
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="신규 정정 블록이 지목한 선행 절의 co-change 검사 (diff-scoped)")
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--base-ref", default="origin/main")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--only", action="append", default=None,
                    help="경로 접두 필터 (반복 가능, 기본 archive/adr/)")
    ap.add_argument("--quiet-passed", action="store_true", help="통과 건 열거 생략")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):      # cp949 콘솔에서 한글이 깨지지 않게
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    root = repo_root_from(args.repo_root)
    prefixes = tuple(args.only) if args.only else DEFAULT_PREFIXES
    result = run_git(root, args.base_ref, args.head, prefixes)
    if result is None:
        print("[%s] base ref 미해소: %s — **미판정**으로 종료한다 "
              "(shallow clone 이면 fetch-depth: 0 필요)" % (COCHANGE_VERSION, args.base_ref))
        return EXIT_BASE_UNRESOLVED

    head_sha = _run(["git", "rev-parse", "--short", args.head], root).stdout.strip()
    print("[%s] base=%s head=%s only=%s"
          % (COCHANGE_VERSION, args.base_ref, head_sha, ",".join(prefixes)))
    for ln in format_report(result, show_passed=not args.quiet_passed):
        print(ln)
    if result["undecidable"]:
        print("미판정 %d 건 — 조용한 통과를 막기 위해 종료코드 %d 로 끝낸다"
              % (len(result["undecidable"]), EXIT_BASE_UNRESOLVED))
        return EXIT_BASE_UNRESOLVED
    return EXIT_VIOLATION if result["violations"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
