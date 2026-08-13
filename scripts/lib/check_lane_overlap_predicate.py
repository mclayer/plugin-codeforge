#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_lane_overlap_predicate.py — CFP-2926 NG-8 lane overlap predicate (AC-16).

§7.10 이 정의한 3 술어 (prep work W 가 lane N 완료 전 착수 가능 ⟺):

    C1  read_set(W)  ∩ write_set(lane N, 미완료)             == ∅
    C2  read_set(W)  ⊆ snapshot(lane N 진입 시점 고정 SHA)
    C3  write_set(W) ∩ (하류 게이트가 이미 판정한 산출물)      == ∅

★본 모듈은 축이 2개다 — 혼동 금지★

  (a) **순수 술어 축** — `evaluate_overlap_predicate()`.
      caller 가 값을 직접 건네는 C1/C2/C3 평가. ★`identity_bearing` 아님★
      (죽을 수 있는 별도 채널이 없다). §7.10 한계 정직 ① — `read_set` 선언의
      정직성에 의존하므로 **advisory** 다.

  (b) **추출 채널 생존 축** — `main()`.
      §7.10 출처표가 `write_set` = "각 lane `CLAUDE.md` self-write 표에서
      ★기계 추출★" 이라 규정하므로 ★그 채널 자체가 조용히 죽을 수 있다★.
      경로 변경 · heading rename · 표 포맷 변경 → 추출 0행 → `write_set = ∅`
      → (C1) `read_set ∩ ∅ = ∅` ∧ (C3) `∅ ∩ … = ∅` 가 **자동 참** →
      판정이 "겹침 허용"(permissive) 으로 넘어간다 = ★silent-green★.
      ⇒ §8.0.8 NG-8 `identity_bearing: **true**` (설계리뷰 iter2 P1-B 정정).

★★P2-b (설계리뷰 iter3 blocking 승계 — 본 개정의 산출물)★★

  종전 fail-closed 는 "추출 결과 0 → `EXTRACTION_EMPTY`" ★관측치 단독★ 이었다.
  형제 행(NG-15·NG-18·NG-9·NG-16·NG-4·NG-10·NG-11·NG-20)은 전부 **기대치와 짝**
  인데 NG-8 만 짝이 없었다 ⇒ ★lane 이 열거에서 **조용히 빠지는** 형상★
  (추출 6 → 5) 은 여전히 permissive 였다 — 남은 5 lane 이 각자 표를 갖고 있으면
  `EXTRACTION_EMPTY` 는 **미발화**한다.
  본 개정은 ★**선언 SSOT 에서 유도한 기대 roster 연접**★ 을 추가한다.

★기대 roster 는 하드코딩하지 않는다★ (option A — 자기참조 절대수치는 원리적 stale):

  - **Source A(기대)** = 선언 SSOT 2곳의 `codeforge-{a,b,c}` brace 열거를 기계 파싱.
      1. `skills/lane-self-write-boundary/SKILL.md` — ★추출 채널 그 자체를 선언하는
         문장★ ("각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{…}) 참조")
      2. `CLAUDE.md` — wrapper 의 lane plugin roster 선언 ("6 lane plugin: codeforge-{…}")
     두 선언의 집합이 다르면 → RED `roster_ssot_divergence` (한쪽에서만 lane 을
     빼는 형상 차단).
  - **Source B(관측)** = `plugins/<name>/CLAUDE.md` 디렉토리 실측.
  - ★관측면을 기대치로 쓰지 않는다★ — glob 을 기대치로 쓰면 lane 디렉토리를 지울 때
    기대치도 같이 줄어드는 **tautology** 가 되어 P2-b 가 무효가 된다.

★정직 천장 — 본 게이트가 **검출하지 못하는** 축★ (숨기지 않고 적는다):

  - 선언 SSOT 2곳과 디렉토리를 ★한꺼번에 일관되게★ 바꾸면 검출 0
    — 정당한 roster 변경과 기계적으로 구별 불가하다(구별 불가가 정답인 경우).
  - self-write 표 **행의 내용**은 검증하지 않는다 — 경로 문자열의 실재·정합·glob
    의미론 미검사. 표가 있고 행도 있으나 **내용이 틀린** 경우 검출 0.
    ★귀결(과소서술 금지)★: 실 경로 행을 전부 지우고 슬래시/별표를 포함한 임의 행 1개만
    남기면 `extraction_empty`(0행)에 걸리지 않은 채 write_set 이 1원소로 줄어 **PASS** 한다
    = 자기 doc 편집만으로 겹침 검사 이탈 가능.
    ★이 축은 원소 유효성 검사로 닫히지 않는다★ — **실재하는 유효 경로**도 같은 효과를 내므로,
    닫으려면 "표가 lane 의 실제 write 전량인가"라는 **완전성** ground truth 가 필요하고
    그 채널은 없다. 원소 유효성만 추가하면 닫힌 것처럼 보이는 hollow gate 가 된다.
  - lane 이 `CLAUDE.md` 가 **아닌 다른 경로**로 self-write 를 선언하면 미탐.
  - 겹침 판정은 ★문자열 집합 연산★ 이다 — `docs/**` 와 `docs/stories/x.md` 는
    서로 다른 문자열이므로 **겹치지 않는 것으로 취급**된다(glob 확장 미적용).
  - "100% 기계강제" 아님 — (a) 축은 advisory 이며 (b) 축만 기계 검출 가능하다.

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import os
import re
import sys

from gate_verdict import (
    GateResult, emit, RED, PASS, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-8"

# ★P2-b Source A★ — 기대 lane roster 를 유도하는 **선언 SSOT** 목록.
# 여기 있는 것은 lane 이름 목록이 아니라 ★lane 이름 목록이 적힌 파일의 경로★ 다
# (roster 자체를 박아두면 그 숫자가 곧 stale 되는 자기참조가 된다).
_ROSTER_SSOT_SOURCES = (
    "skills/lane-self-write-boundary/SKILL.md",
    "CLAUDE.md",
)

# `codeforge-{requirements, design, review, develop, test, pmo}` brace 열거
_ROSTER_BRACE_RE = re.compile(r"codeforge-\{([^}\n]+)\}")

# lane 이름 허용 문자 — 밖이면 unknown-input fail-closed
_LANE_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")

_LANE_PREFIX = "codeforge-"
_PLUGINS_DIRNAME = "plugins"
_LANE_DOC_BASENAME = "CLAUDE.md"

# self-write 표 heading — 부재(미선언)와 존재-후-0행(추출 사망)을 **분리**하는 앵커
_SELF_WRITE_HEADING_RE = re.compile(r"(?m)^##\s+(?:Self-write|소유\s*파일)")
_NEXT_H2_RE = re.compile(r"(?m)^##\s")
_TABLE_ROW_RE = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|", re.MULTILINE)
_BACKTICK_RE = re.compile(r"`")

#: ★명시적 empty write-set sentinel★ — self-write 표 안에 이 토큰이 있고
#: ★그 lane 이 `_DECLARED_EMPTY_ALLOWLIST` 에 등재돼 있어야만★
#: "write_set = ∅" 이 **정당 선언**으로 인정된다 (`declared_empty`).
#:
#: 왜 필요한가: write set 이 빈 lane(= 파일 write 권한이 구조적으로 부재한 lane)은
#: 겹침이 원천 불가능한 ★최선★ 사례인데, sentinel 이 없으면 그 lane 이
#: `extraction_empty` RED(표가 깨져 추출 0행)와 구별되지 않아 **처벌**당한다.
#: 반대로 sentinel 없이 0행을 GREEN 으로 승격하면 표 파손이 조용히 통과한다
#: (공허참 승격 = fail-closed teeth 상실). ⇒ ★적극적 토큰이 있을 때만 GREEN★.
#:
#: ★토큰 단독으로는 승격되지 않는다★ — 토큰은 피검사자(untrusted lane doc)의
#: **주장 표식**이고, 승격 권한은 아래 allowlist(검사자 측)에 있다.
_EMPTY_WRITE_SET_SENTINEL = "EMPTY-WRITE-SET(synthesis-only)"
_EMPTY_SENTINEL_RE = re.compile(re.escape(_EMPTY_WRITE_SET_SENTINEL))

#: ★sentinel 사용 자격 allowlist★ — 토큰은 피검사자(untrusted lane doc)의 **주장 표식**일 뿐이고,
#: 그 주장을 GREEN 으로 **승격시키는 권한은 검사자 측(본 코드)** 에 있다.
#: allowlist 밖 lane 이 토큰을 달면 RED — "실 write 행을 지우고 토큰을 넣는" 우회로 봉인.
#: 선례 형상 = check_ng_registry_bijection.py NON_NG_REGISTRY_NAMES frozenset
#:            / cfp-2926-phase2-gates.yml CI_RC3_FROZEN (확장하려면 코드 diff 필수).
#: ★정직 천장★: 코드 diff 권한자는 여전히 명단을 늘릴 수 있다 — 본 장치는 "봉인"이 아니라
#:   ★자기선언 승격 경로 제거(승격을 리뷰 표면으로 강제)★ 까지가 보증 범위다.
_DECLARED_EMPTY_ALLOWLIST = frozenset({"codeforge-review"})


# ---------------------------------------------------------------------------
# (a) 순수 술어 축 — §7.10 C1/C2/C3. caller 공급 입력 위에서만 평가한다.
# ---------------------------------------------------------------------------

def evaluate_overlap_predicate(
    w_read_set,
    w_write_set,
    lane_write_set,
    snapshot_paths,
    downstream_artifacts,
):
    """§7.10 C1·C2·C3 를 문자열 집합 연산으로 평가하는 **순수 함수**.

    Args:
        w_read_set:           read_set(W) — packet `scope_globs` (§7.12)
        w_write_set:          write_set(W) — W 가 새로 쓰는 산출물
        lane_write_set:       write_set(lane N, 미완료) — 기계 추출값
        snapshot_paths:       snapshot(lane N 진입 시점 고정 SHA) 가 덮는 경로 집합
        downstream_artifacts: 하류 게이트가 **이미 판정한** 산출물

    Returns:
        dict — `c1`/`c2`/`c3` (bool) · `c1_violations`/`c2_violations`/
        `c3_violations` (sorted list) · `allowed` (= C1 ∧ C2 ∧ C3)

    ★identity_bearing 아님★ — 전 인자가 caller 공급이라 "죽을 수 있는 별도 채널"이
    없다(§8.0.8 NG-5·NG-13 과 동류). 채널이 죽는 쪽은 `lane_write_set` 을 만들어
    내는 추출 경로이며 그것은 `main()` 축이 담당한다.

    ★한계★ — glob 확장 의미론을 적용하지 않는다. `docs/**` 와 `docs/a.md` 는
    문자열이 다르므로 겹치지 않는 것으로 판정된다(포함관계 미판정).
    """
    read_s = set(w_read_set or ())
    write_s = set(w_write_set or ())
    lane_s = set(lane_write_set or ())
    snap_s = set(snapshot_paths or ())
    down_s = set(downstream_artifacts or ())

    c1_violations = sorted(read_s & lane_s)
    c2_violations = sorted(read_s - snap_s)
    c3_violations = sorted(write_s & down_s)

    c1 = not c1_violations
    c2 = not c2_violations
    c3 = not c3_violations

    return {
        "c1": c1,
        "c2": c2,
        "c3": c3,
        "c1_violations": c1_violations,
        "c2_violations": c2_violations,
        "c3_violations": c3_violations,
        "allowed": c1 and c2 and c3,
    }


# ---------------------------------------------------------------------------
# (b) 추출 채널 생존 축 — Source A(선언 roster) / Source B(관측) / 추출
# ---------------------------------------------------------------------------

def _parse_declared_roster(repo_root):
    """★P2-b Source A★ — 선언 SSOT 에서 기대 lane roster 를 기계 유도한다.

    Returns:
        (roster_or_None, per_source_dict, error_reason_or_None)

        roster = {"codeforge-design", ...} (full plugin 디렉토리 이름)

    fail-closed 사유 3종 (전부 조용한 통과 금지):
      - `roster_ssot_unreadable:<path>`   — 선언 파일 자체가 없거나 못 읽음
      - `roster_ssot_unparseable:<path>`  — brace 열거 0건 (문장 rename 등)
      - `roster_ssot_ambiguous:<path>`    — brace 열거 2건 이상 (어느 것이 정본인지
                                            기계가 못 고름 — §8.0.9 ANCHOR_AMBIGUOUS 동형)
      - `roster_ssot_bad_lane_name:...`   — lane 이름이 허용 문자 밖
    """
    per_source = {}

    for rel in _ROSTER_SSOT_SOURCES:
        path = os.path.join(repo_root, rel)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            return None, per_source, "roster_ssot_unreadable:%s (%s)" % (rel, str(e)[:60])

        matches = _ROSTER_BRACE_RE.findall(text)
        if not matches:
            return None, per_source, "roster_ssot_unparseable:%s" % rel
        if len(matches) > 1:
            return None, per_source, "roster_ssot_ambiguous:%s (matches=%d)" % (
                rel, len(matches)
            )

        names = []
        for raw in matches[0].split(","):
            name = _BACKTICK_RE.sub("", raw).strip()
            if not name:
                continue
            if not _LANE_NAME_RE.match(name):
                return None, per_source, "roster_ssot_bad_lane_name:%s/%r" % (rel, name[:30])
            names.append(_LANE_PREFIX + name)

        if not names:
            return None, per_source, "roster_ssot_unparseable:%s (empty brace)" % rel

        per_source[rel] = sorted(set(names))

    rosters = [frozenset(v) for v in per_source.values()]
    if len(set(rosters)) != 1:
        return None, per_source, "roster_ssot_divergence"

    return set(rosters[0]), per_source, None


def _discover_lane_dirs(repo_root):
    """★Source B(관측)★ — `plugins/<name>/CLAUDE.md` 실측.

    Returns: dict {plugin_dir_name → CLAUDE.md 절대경로}
    ★기대치가 아니라 관측치다★ — 기대치는 `_parse_declared_roster()` 소관.
    """
    observed = {}
    plugins_root = os.path.join(repo_root, _PLUGINS_DIRNAME)
    if not os.path.isdir(plugins_root):
        return observed
    for entry in sorted(os.listdir(plugins_root)):
        doc = os.path.join(plugins_root, entry, _LANE_DOC_BASENAME)
        if os.path.isfile(doc):
            observed[entry] = doc
    return observed


def _extract_self_write_table(claude_text):
    """lane `CLAUDE.md` 의 self-write 표에서 `write_set` 을 기계 추출한다.

    Returns:
        (has_section: bool, write_set: set, empty_sentinel: bool)

    ★세 상태를 분리해서 돌려준다★ (§8.0.8 NG-8 / `ADR-154:149` 의
    "target 0건 = 정당 no-op" vs "target 존재하나 unparseable = fail-closed" 경계):
      - `has_section=False`                        → **미선언** (별 상태 — non-GREEN)
      - `has_section=True, ∅, sentinel=False`      → ★추출만 0★ = `EXTRACTION_EMPTY` fail-closed
      - `has_section=True, ∅, sentinel=True`       → ★공집합 **주장**★ (승격 여부는 caller 판정 —
        `_DECLARED_EMPTY_ALLOWLIST` 등재 lane 만 `declared_empty`, 밖이면 RED)
      - `has_section=True, 비어있지 않음, sentinel=True` → ★모순★ (caller 가 RED 처리)

    ★왜 세 번째 상태가 필요한가★: write set 이 빈 lane 은 겹침이 원천 불가능한 **최선**
    사례다. 그런데 sentinel 없이 "없음" 이라고 표를 쓰면 셀에 `/`·`*` 가 없어 추출 0행이
    되고 `extraction_empty` RED 로 **처벌**된다 (설계 역전). 그렇다고 0행을 무조건
    GREEN 으로 올리면 표 파손이 조용히 통과한다. ⇒ **적극적 sentinel 토큰이 있고**
    ★그 lane 이 검사자 측 allowlist 에 등재돼 있을 때만★ GREEN 으로 승격하고,
    토큰 없는 0행은 종전대로 RED 를 유지한다. ★토큰 자체는 피검사자 본문(untrusted)이라
    자기 verdict 를 승격시킬 권한이 없다★ — 승격 권한은 `main()` 의 allowlist 조회에 있다.

    grep-oracle(presence 만 확인)이 아니라 **실제 표 parsing** 이므로 표 포맷
    변화에 민감하다 — 그 민감성이 곧 채널 생존 검출력이다.
    """
    if not claude_text:
        return False, set(), False

    heading = _SELF_WRITE_HEADING_RE.search(claude_text)
    if not heading:
        return False, set(), False

    section_start = heading.end()
    next_heading = _NEXT_H2_RE.search(claude_text[section_start:])
    section_end = (
        section_start + next_heading.start() if next_heading else len(claude_text)
    )
    section_text = claude_text[section_start:section_end]

    # ★sentinel 은 반드시 ★표 행 셀★ 안에 있어야 한다★ — 섹션 산문(설명 blockquote 등)에
    #   토큰이 등장하는 것만으로는 인정하지 않는다. 산문 전역 검색으로 두면 표 행을 지워도
    #   설명 문장만 남아 GREEN 이 유지되는 우회로가 생긴다 (실측으로 확인된 구멍).
    empty_sentinel = False

    write_set = set()
    for cell1, cell2 in _TABLE_ROW_RE.findall(section_text):
        for cell in (cell1.strip(), cell2.strip()):
            if _EMPTY_SENTINEL_RE.search(cell):
                empty_sentinel = True
                continue  # sentinel 행은 write_set 원소가 아니다
            if "/" in cell or "*" in cell:
                cell = _BACKTICK_RE.sub("", cell).strip()
                if cell:
                    write_set.add(cell)

    return True, write_set, empty_sentinel


def main(argv=None):
    """Main entry point — (b) 추출 채널 생존 축.

    CLI:
      python check_lane_overlap_predicate.py --repo-root <path>

    판정 순서 (전건 **명시 분기** — "우연히 RED" 에 의존하지 않는다):
      1. 선언 SSOT 해석 실패/모호/불일치        → RED   (unknown-input, [154-AC-4])
      2. ★기대 roster ≠ 관측 lane★              → RED   ★P2-b 연접★
           - 개수 불일치        → `lane_count_mismatch`   (6 → 5 형상)
           - 개수 같고 집합 다름 → `lane_roster_mismatch`  (swap 형상)
      3. lane `CLAUDE.md` 읽기 실패             → RED   (unknown-input)
      4. self-write 표 존재 + 추출 0행 + ★sentinel 부재★ → RED `extraction_empty`
         (sentinel 이 있고 lane 이 allowlist 등재면 `declared_empty` = 정당 공집합 →
          4번 우회, PASS 적격)
      4b. sentinel 이 있는데 write_set 이 ★비어있지 않음★ → RED `empty_sentinel_contradiction`
          (실제로 쓰는 lane 에 sentinel 을 붙여 검사를 무력화하는 경로 봉인)
      4c. sentinel 이 있는데 lane 이 ★`_DECLARED_EMPTY_ALLOWLIST` 밖★ → RED
          `sentinel_not_allowlisted` — 피검사자 본문의 토큰이 자기 verdict 를 GREEN 으로
          승격시키는 경로 제거(승격 권한 = 검사자 측 코드). ★순서 고정★: 4b → 4c →
          `extraction_empty`. 4c 를 4b 앞에 두면 "allowlist 밖 lane 의 실경로+sentinel"
          모순이 4c 로 새어 `empty_sentinel_contradiction` 이 관측 불가가 된다.
      5. lane 간 `write_set` 겹침               → RED   `lane_write_set_overlap`
      6. self-write 표 **미선언** lane 존재     → INCONCLUSIVE `write_set_undeclared`
                                                  (non-GREEN — 4번과 **별 상태**)
      7. 그 외                                   → PASS
    """
    parser = argparse.ArgumentParser(
        prog="check_lane_overlap_predicate.py",
        description="lane overlap predicate — write_set 추출 채널 생존 검사 (AC-16 / NG-8).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)

    # --- 1. Source A: 선언 SSOT 에서 기대 roster 유도 (하드코딩 아님) -------
    declared, per_source, roster_error = _parse_declared_roster(repo_root)
    if roster_error is not None:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=roster_error,
            trace={
                "roster_ssot_source_count": len(_ROSTER_SSOT_SOURCES),
                "roster_ssot_parsed_count": len(per_source),
            },
            identity_probe={
                "repo_root": repo_root,
                "roster_ssot_paths": list(_ROSTER_SSOT_SOURCES),
                "per_source_roster": per_source,
            },
        )
        return emit(result)

    expected_lane_count = len(declared)

    # --- 2. Source B: 관측 + ★P2-b 기대 lane 수 연접★ -----------------------
    observed = _discover_lane_dirs(repo_root)
    discovered_lane_count = len(observed)

    missing = sorted(declared - set(observed))
    undeclared_dirs = sorted(set(observed) - declared)

    base_trace = {
        "expected_lane_count": expected_lane_count,
        "discovered_lane_count": discovered_lane_count,
        "roster_ssot_source_count": len(_ROSTER_SSOT_SOURCES),
    }
    base_probe = {
        "repo_root": repo_root,
        "roster_ssot_paths": list(_ROSTER_SSOT_SOURCES),
        "declared_roster": sorted(declared),
        "resolved_lane_docs": [observed[k] for k in sorted(observed)],
    }

    if missing or undeclared_dirs:
        trace = dict(base_trace)
        trace["missing_lane_count"] = len(missing)
        trace["undeclared_lane_dir_count"] = len(undeclared_dirs)
        probe = dict(base_probe)
        probe["missing_lanes"] = missing
        probe["undeclared_lane_dirs"] = undeclared_dirs
        # 개수 불일치(누락/추가) 와 개수 동일-집합 상이(swap) 를 명시 분기로 나눈다
        reason = (
            "lane_count_mismatch"
            if expected_lane_count != discovered_lane_count
            else "lane_roster_mismatch"
        )
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED, reason=reason,
            trace=trace, identity_probe=probe,
        ))

    # --- 3-4. 추출 ----------------------------------------------------------
    write_sets = {}          # lane → write_set (표 존재 ∧ 1행 이상, 또는 정당 공집합)
    undeclared_lanes = []    # self-write 표 자체 부재 (미선언)
    extraction_empty = []    # 표는 있는데 추출 0행 ∧ sentinel 부재 (채널 사망)
    declared_empty = []      # 표 존재 ∧ 추출 0행 ∧ sentinel ∧ ★allowlist 등재★ = 정당 공집합
    sentinel_contradiction = []  # sentinel 있는데 write_set 비어있지 않음
    sentinel_not_allowlisted = []  # sentinel 있는데 lane 이 allowlist 밖 (자기선언 승격 시도)
    read_errors = {}

    for lane in sorted(observed):
        try:
            with open(observed[lane], "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            read_errors[lane] = str(e)[:60]
            continue

        has_section, write_set, empty_sentinel = _extract_self_write_table(text)
        if not has_section:
            undeclared_lanes.append(lane)
        elif empty_sentinel and write_set:
            # ★모순★ — "쓰는 게 없다" 고 선언해 놓고 실제 경로를 나열했다.
            sentinel_contradiction.append(lane)
        elif not write_set:
            if empty_sentinel:
                # ★승격 권한은 검사자 측★ — 토큰(피검사자 본문)은 "∅ 를 주장한다" 는
                #   표식일 뿐이고, GREEN 승격은 allowlist 등재 lane 에만 부여한다.
                if lane in _DECLARED_EMPTY_ALLOWLIST:
                    # ★정당 공집합★ — 겹침 판정에는 ∅ 로 참여한다 (trivially disjoint).
                    declared_empty.append(lane)
                    write_sets[lane] = set()
                else:
                    sentinel_not_allowlisted.append(lane)
            else:
                extraction_empty.append(lane)
        else:
            write_sets[lane] = write_set

    extracted_lane_count = len(write_sets)
    write_set_element_total = sum(len(v) for v in write_sets.values())
    lane_pairs_compared = extracted_lane_count * (extracted_lane_count - 1) // 2

    full_trace = dict(base_trace)
    full_trace.update({
        "extracted_lane_count": extracted_lane_count,
        "write_set_element_total": write_set_element_total,
        "lane_pairs_compared": lane_pairs_compared,
        "undeclared_lane_count": len(undeclared_lanes),
        "extraction_empty_lane_count": len(extraction_empty),
        "declared_empty_lane_count": len(declared_empty),
        "sentinel_contradiction_lane_count": len(sentinel_contradiction),
        "sentinel_not_allowlisted_lane_count": len(sentinel_not_allowlisted),
    })
    full_probe = dict(base_probe)
    full_probe["write_set_size_by_lane"] = {k: len(v) for k, v in sorted(write_sets.items())}
    if declared_empty:
        full_probe["declared_empty_lanes"] = sorted(declared_empty)

    if read_errors:
        probe = dict(full_probe)
        probe["unreadable_lanes"] = sorted(read_errors)
        trace = dict(full_trace)
        trace["unreadable_lane_count"] = len(read_errors)
        return emit(unknown_input(
            gate_id=GATE_ID,
            reason="lane_claude_md_unreadable",
            trace=trace,
            identity_probe=probe,
        ))

    if sentinel_contradiction:
        # ★sentinel 오남용 봉인★ — 실제로 쓰는 lane 이 "쓰는 게 없다" 를 선언해
        #   겹침 검사에서 자기를 빼는 경로. 조용히 넘기면 sentinel 이 escape-hatch 가 된다.
        probe = dict(full_probe)
        probe["sentinel_contradiction_lanes"] = sorted(sentinel_contradiction)
        trace = dict(full_trace)
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED, reason="empty_sentinel_contradiction",
            trace=trace, identity_probe=probe,
        ))

    if sentinel_not_allowlisted:
        # ★자기선언 승격 봉인★ — 피검사자 lane doc(untrusted body)에 토큰만 달아서
        #   자기 verdict 를 GREEN 으로 올리는 경로. 승격 자격은 검사자 측 allowlist 소관이며
        #   확장하려면 본 코드 diff(=리뷰 표면)를 거쳐야 한다.
        #   ★정직 천장★: 코드 diff 권한자는 명단을 늘릴 수 있다 — "봉인" 아님.
        probe = dict(full_probe)
        probe["sentinel_not_allowlisted_lanes"] = sorted(sentinel_not_allowlisted)
        probe["declared_empty_allowlist"] = sorted(_DECLARED_EMPTY_ALLOWLIST)
        trace = dict(full_trace)
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED, reason="sentinel_not_allowlisted",
            trace=trace, identity_probe=probe,
        ))

    if extraction_empty:
        # ★설계리뷰 iter2 P1-B★ — 선언은 됐고 추출만 0. 미선언과 **별 상태**.
        # ★sentinel 이 있는 lane 은 여기 오지 않는다★ (allowlist 등재면 declared_empty,
        #   밖이면 위 `sentinel_not_allowlisted` 로 분기) — 그러나 sentinel 없는 0행은
        #   종전대로 RED 다 (표 파손의 조용한 통과 봉인).
        probe = dict(full_probe)
        probe["extraction_empty_lanes"] = extraction_empty
        return emit(unknown_input(
            gate_id=GATE_ID,
            reason="extraction_empty",
            trace=full_trace,
            identity_probe=probe,
        ))

    # --- 5. lane 간 write_set 겹침 (C1/C3 가 의미를 갖기 위한 전제) ---------
    overlaps = []
    lane_names = sorted(write_sets)
    for i, lane1 in enumerate(lane_names):
        for lane2 in lane_names[i + 1:]:
            shared = write_sets[lane1] & write_sets[lane2]
            if shared:
                overlaps.append((lane1, lane2, sorted(shared)))

    if overlaps:
        trace = dict(full_trace)
        trace["overlap_pair_count"] = len(overlaps)
        probe = dict(full_probe)
        probe["overlap_pairs"] = ["%s|%s" % (a, b) for a, b, _ in overlaps[:5]]
        probe["overlapped_paths"] = overlaps[0][2][:5]
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED, reason="lane_write_set_overlap",
            trace=trace, identity_probe=probe,
        ))

    full_trace["overlap_pair_count"] = 0

    # --- 6. 미선언 lane (non-GREEN — 겹침 판정을 vacuous 참으로 넘기지 않는다) --
    if undeclared_lanes:
        probe = dict(full_probe)
        probe["undeclared_lanes"] = undeclared_lanes
        return emit(empty_target(
            gate_id=GATE_ID,
            reason="write_set_undeclared",
            trace=full_trace,
            identity_probe=probe,
        ))

    # --- 7. PASS ------------------------------------------------------------
    return emit(GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="roster_matched_and_no_overlap",
        trace=full_trace,
        identity_probe=full_probe,
    ))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
