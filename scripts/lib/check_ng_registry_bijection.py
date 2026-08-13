#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_ng_registry_bijection.py — X-16 완화 ⒝: registry NG 행 집합 ↔ Story §8.0.8 (1) NG 표 bijection.

CFP-2926 Phase 2 / Story §9.8 (5) 승계 blocking #1 (설계리뷰 iter3 Codex peer (A) 지목).

★ 무엇을 위한 게이트인가 (§8.0.8 정직 천장 ④) ★
    §8.0.8 의 도출 규칙 R(= S1[§7.14 G2 ∈ {✔,부분}] ∪ S2[§8.0.2 RTM tier=T1])은 "두 SSOT 를
    전수 훑었다"까지만 보증하며, ★두 SSOT 자신이 본 Story 의 모든 검사 진입점을 담고 있는지는
    보증하지 않는다★. 두 표 밖에서 태어나는 검사가 있으면 R 도 놓친다.
    완화 ⒜(규칙 R 을 기계 재도출 가능한 형태로 기술) = 설계 lane 이행 완료.
    완화 ⒝ = 본 모듈 — ``docs/evidence-checks-registry.yaml`` 등록 행과 §8.0.8 NG 표의 bijection 을
    assert 해 ★"표 밖에서 태어난 검사"가 registry 축에서 드러나게★ 한다(세 번째 대조축).

★★ 본 게이트 자신은 NG 행이 아니다 — 명시 self-exclusion declare ★★
    본 모듈은 규칙 R 의 S1(§7.14 처방표) 에도 S2(§8.0.2 RTM T1) 에도 속하지 않는 ★메타-게이트★ 다.
    따라서 ``docs/evidence-checks-registry.yaml`` 에 ``cfp2926-ng-*`` 행을 갖지 않는다 —
    등록하면 registry 측 원소가 22 가 되어 ★bijection 이 자기 자신 때문에 깨진다★.
    ⇒ 이 제외는 ★조용한 제외가 아니다★: (1) 본 docstring (2) 아래 ``SELF_EXCLUSION_DECLARE`` 상수
    (3) ★매 run 의 ``identity_probe.self_exclusion`` echo★ (4) registry 주석 블록 — 4중 기록.
    조용히 빼는 행위가 정확히 본 Story 가 추적하는 결함 class(silent-skip)이므로, 제외 사실을
    산출물 표면에 상시 노출한다. 향후 메타-게이트 행을 registry 에 등록하려면
    ``NON_NG_REGISTRY_NAMES`` 에 이름을 ★명시 추가★ 해야 하며(현재 의도적 공집합), 그 추가는
    코드 diff 로 드러난다 — 즉 "조용한 제외" 경로 자체가 존재하지 않는다.

★★ Story 파일 접근 한계 — 정직 declare (over-claim 금지) ★★
    Story SSOT(``wrapper/stories/CFP-2926.md``)는 ★별 repo(mclayer/codeforge-internal-docs)★ 에
    있다. wrapper repo CI 체크아웃에는 그 파일이 없다. ⇒ 본 모듈은 Story 를 ★fetch 하지 않는다★ —
    caller(workflow)가 materialize 한 ★로컬 경로만★ ``--story`` 로 받는다
    (선례 답습: ``.github/workflows/ac-traceability-matrix.yml`` 이 PR body ``story_uri`` 영구 ref 를
    fetch → ``ac-gate-source.md`` 로 떨어뜨린 뒤 ``--ac-source <path>`` 로 넘기는 경로와 동형).
    ``--story`` 미지정 = Story 원본 미해석 ⇒ ★``INCONCLUSIVE``(exit 3)★. bijection 을 대조할
    상대측이 없으므로 ★"PASS" 라고 말하지 않는다★. ★부재를 exit 0 으로 흡수하는 경로는 없다★:
      · ``--story`` 미지정            → INCONCLUSIVE (exit 3) — 판정 유보, GREEN 아님
      · ``--story`` 지정했으나 해석 불가 → RED (exit 1)      — 명시 입력의 미해석 = fail-closed
    ★한계 명시★: ``--story`` 를 넘기지 않는 호출에서 본 게이트는 ★bijection 을 검증하지 않는다★
    (검증했다고 주장하지도 않는다). 그 호출의 GREEN 은 원리적으로 산출 불가다.

ADR-154 self-verification 번들 (본 메타-게이트 자신에게도 적용 — §결정 7 재귀 자기적용):
    [154-AC-3]  empty-target  : registry NG 행 0 ∨ Story NG 행 0 → ★명시 분기 RED★.
                                ∅ ↔ ∅ 를 "bijection 성립" 으로 읽지 않는다(vacuous 참 봉인).
    [154-AC-4]  unknown-input : registry unparseable / ``introduced_by: CFP-2926`` 인데 NG 이름
                                패턴 밖 / Story 경로 미해석 / §8.0.8 섹션·표 앵커 미발견 → RED.
                                ★행을 조용히 제외한 뒤 통과시키는 경로 0★.
    [154-AC-5]  trace         : registry entry 총수 · CFP-2926 행 수 · NG 행 수 · Story 스캔 줄 수 ·
                                섹션 줄 수 · 표 행 수 · Story NG 수 · 차집합 양방향 수 (전건 numeric).
    [154-AC-13] identity_probe: resolved-target echo — 실제로 판독한 registry/Story 절대경로,
                                §8.0.8 섹션·표 앵커의 ★실 줄번호와 원문★, 양측 NG id 목록,
                                self-exclusion declare. 추출 수 0 → ``EXTRACTION_EMPTY`` fail-closed.

정직 천장 (ADR-154 §결정 4 INV-5 / ADR-151 §결정 7 상속):
    본 게이트는 ★행 집합의 bijection★ 까지만 보증한다. 등록된 행의 ★내용 적절성★(description 이
    실제 게이트를 옳게 기술하는가), Story NG 표 자신의 ★완전성★(규칙 R 이 두 SSOT 를 완전히 덮는가
    = 정직 천장 ④ 의 상위 명제), 각 게이트의 ★detection sufficiency★ 는 검증하지 않는다.
    "표 밖 검사 전부 검출"·"완전 봉인" 주장 부재 — registry 축에 ★드러날 기회를 만드는★ 것이 전부다.
    detect 대상 module 파일의 실재 여부는 trace 로 ★echo 만★ 하고 verdict 축에 넣지 않는다
    (모듈 부재는 cfp-2926-phase2-gates.yml 의 해당 step 이 실행 시점에 non-zero 로 표면화 —
    disjoint 축의 중복 강제 회피).

reuse-before-write (ADR-140 / ADR-061):
    · ``gate_verdict`` (3-state verdict/exit/emit) — 신규 verdict 체계 발명 0
    · ``check_deferred_followup_reconcile.load_registry_entries`` + ``DEFAULT_REGISTRY_REL``
      — registry loader/경로 리터럴 중복 유입 0 (check_evidence_registry.py 와 동일 SSOT 재사용)
    · ``check_fanout_subject_prose.resolve_repo_root`` / ``normalize_rel`` / ``read_lines``
      / ``UnparseableDocError`` — 형제 게이트가 노출한 문서 스캔 primitive 재사용

Usage:
    python3 scripts/lib/check_ng_registry_bijection.py --repo-root . \\
        [--registry docs/evidence-checks-registry.yaml] [--story <local path to CFP-2926.md>]

ADR refs: ADR-154 (§결정 3·5·7·8) / ADR-171 / ADR-151 / ADR-140 / ADR-119
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

import gate_verdict as gv  # noqa: E402
from check_deferred_followup_reconcile import (  # noqa: E402  reuse-before-write
    DEFAULT_REGISTRY_REL,
    load_registry_entries,
)
from check_fanout_subject_prose import (  # noqa: E402  reuse-before-write
    UnparseableDocError,
    normalize_rel,
    read_lines,
    resolve_repo_root,
)

# Windows cp949 회피 — 한글 reason/probe print 시 mojibake 차단 (check_evidence_registry.py 관용구).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── 상수 ─────────────────────────────────────────────────────────────────────

#: 본 게이트 id. ★"NG-n" 이 아니다★ — NG 인벤토리 밖 메타-게이트임을 id 자체로 표시한다.
GATE_ID = "X-16:ng-registry-bijection"

#: Story key — registry 행 선택 정의역.
STORY_KEY = "CFP-2926"

#: registry 측 NG 행 이름 규약. ``cfp2926-ng-<n>-<slug>`` — <n> 이 곧 Story 측 ``NG-<n>``.
#: zero-padding 금지(정규화 층 = 추가 실패면) — Story 표기 ``NG-1`` 과 1:1.
REGISTRY_NG_NAME_RE = re.compile(r"^cfp2926-ng-(\d{1,2})-[a-z0-9][a-z0-9-]*$")

#: ``introduced_by: CFP-2926`` 이면서 NG 행이 아님이 ★명시 허용★ 된 registry 이름들.
#: ★의도적 공집합★ — 현 시점 본 메타-게이트를 포함해 registry 에 등록된 비-NG CFP-2926 행은 없다.
#: 여기 넣지 않은 CFP-2926 행이 NG 이름 규약을 벗어나면 ``UNCLASSIFIED_REGISTRY_ROW`` RED 다
#: (조용한 skip 경로 부재 — 제외하려면 코드 diff 로 이름을 명시해야 한다).
NON_NG_REGISTRY_NAMES = frozenset()

#: 매 run identity_probe 에 echo 되는 self-exclusion 정직 문구 (docstring §self-exclusion 요약).
SELF_EXCLUSION_DECLARE = (
    "본 bijection 게이트(check_ng_registry_bijection.py) 자신은 NG 행이 아니다 — "
    "규칙 R(S1=§7.14 G2∈{✔,부분} ∪ S2=§8.0.2 RTM tier=T1) 어디에서도 파생되지 않는 메타-게이트이며, "
    "registry 에 등록하면 자기 때문에 bijection 이 깨진다. 조용한 제외가 아니라 명시 declare 이며 "
    "(docstring + SELF_EXCLUSION_DECLARE 상수 + 본 probe echo + registry 주석 4중 기록), "
    "향후 제외 확장은 NON_NG_REGISTRY_NAMES 코드 diff 로만 가능하다."
)

#: Story §8.0.8 섹션 앵커 (heading level 무관 — 번호가 앵커).
STORY_SECTION_RE = re.compile(r"^#{2,6}\s*8\.0\.8(\s|$)")
#: markdown heading 일반형 — §8.0.8 섹션의 끝 판정.
STORY_HEADING_RE = re.compile(r"^#{1,6}\s")
#: §8.0.8 안에서 "(1) 신규 게이트 인벤토리 × 번들 매핑" 표를 여는 줄.
#: ★heading/문면 rename → 앵커 미발견 → RED★ (0행 vacuous pass 봉인 — NG-21 과 동형 추출 축).
STORY_TABLE_ANCHOR_RE = re.compile(r"\(1\).*신규 게이트 인벤토리")
#: 표 셀 장식 strip 대상 — ★(U+2605) ☆(U+2606) 강조 ** 백틱 공백.
CELL_DECORATION_RE = re.compile(r"[★☆*`\s]+")
#: 장식 strip 후 첫 셀이 정확히 ``NG-<n>`` 일 때만 NG 행으로 인정 (부분일치 금지 — anchored).
STORY_NG_CELL_RE = re.compile(r"^NG-(\d{1,2})$")


# ── registry 축 ───────────────────────────────────────────────────────────────

def extract_registry_ng(entries: List[dict]) -> Tuple[Dict[int, str], List[str], List[int]]:
    """registry entries[] → (ng_id → entry name, 미분류 CFP-2926 이름들, 중복 ng_id 들).

    선택 정의역 = ``introduced_by == CFP-2926`` 인 행 ★전부★. 그 중 NG 이름 규약을 벗어난 행은
    ★버리지 않고 unclassified 로 수집★ 한다([154-AC-4] — 조용한 행 제외 금지).
    """
    ng: Dict[int, str] = {}
    unclassified: List[str] = []
    dup_ids: List[int] = []
    for entry in entries:
        if not isinstance(entry, dict):
            unclassified.append("<non-mapping entry>")
            continue
        if str(entry.get("introduced_by", "")).strip() != STORY_KEY:
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            unclassified.append("<name 부재/비문자열>")
            continue
        name = name.strip()
        if name in NON_NG_REGISTRY_NAMES:
            continue
        m = REGISTRY_NG_NAME_RE.match(name)
        if not m:
            unclassified.append(name)
            continue
        ng_id = int(m.group(1))
        if ng_id in ng:
            dup_ids.append(ng_id)
        else:
            ng[ng_id] = name
    return ng, unclassified, sorted(set(dup_ids))


def registry_module_paths(entries: List[dict], ng_names: Dict[int, str]) -> Dict[str, str]:
    """NG 행의 ``detect_command`` 에서 ``scripts/lib/*.py`` 모듈 경로를 추출 (trace echo 전용)."""
    by_name = {e.get("name"): e for e in entries if isinstance(e, dict)}
    out: Dict[str, str] = {}
    mod_re = re.compile(r"(scripts/lib/[A-Za-z0-9_./-]+\.py)")
    for ng_id, name in sorted(ng_names.items()):
        cmd = by_name.get(name, {}).get("detect_command")
        if isinstance(cmd, str):
            m = mod_re.search(cmd)
            if m:
                out["NG-%d" % ng_id] = m.group(1)
    return out


# ── Story 축 ─────────────────────────────────────────────────────────────────

class StoryParseError(Exception):
    """Story 측 앵커/표 해석 실패 — fail-closed 사상용 (reason code 동반)."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def extract_story_ng(lines: List[str]) -> Tuple[Dict[int, int], dict]:
    """Story 본문 줄들 → (ng_id → 표 줄번호(1-based), probe/trace 부속 정보).

    Raises:
        StoryParseError: 섹션 앵커 미발견 / 표 앵커 미발견 / 표 행 0 / 추출 NG 0.
    """
    start = next((i for i, ln in enumerate(lines) if STORY_SECTION_RE.match(ln)), None)
    if start is None:
        raise StoryParseError(
            "SECTION_ANCHOR_NOT_FOUND",
            "§8.0.8 섹션 heading 미발견 — Story 판본 불일치 또는 섹션 rename",
        )
    end = next(
        (j for j in range(start + 1, len(lines)) if STORY_HEADING_RE.match(lines[j])),
        len(lines),
    )
    anchor = next(
        (j for j in range(start, end) if STORY_TABLE_ANCHOR_RE.search(lines[j])), None
    )
    if anchor is None:
        raise StoryParseError(
            "TABLE_ANCHOR_NOT_FOUND",
            "§8.0.8 안에서 '(1) … 신규 게이트 인벤토리' 표 앵커 미발견 — 문면 rename 의심",
        )

    table_rows: List[Tuple[int, str]] = []
    in_table = False
    for j in range(anchor + 1, end):
        stripped = lines[j].strip()
        if stripped.startswith("|"):
            in_table = True
            table_rows.append((j, stripped))
        elif in_table and stripped == "":
            break
    if not table_rows:
        raise StoryParseError(
            "TABLE_EMPTY", "표 앵커 직후 markdown 표 행 0 — 표가 사라졌거나 형식 변경"
        )

    ng: Dict[int, int] = {}
    dup_ids: List[int] = []
    for lineno, row in table_rows:
        cells = row.split("|")
        if len(cells) < 3:
            continue
        first = CELL_DECORATION_RE.sub("", cells[1])
        m = STORY_NG_CELL_RE.match(first)
        if not m:
            continue
        ng_id = int(m.group(1))
        if ng_id in ng:
            dup_ids.append(ng_id)
        else:
            ng[ng_id] = lineno + 1
    if not ng:
        raise StoryParseError(
            "EXTRACTION_EMPTY",
            "표 행 %d 개를 읽었으나 'NG-<n>' 첫 셀 0건 — 셀 형식 변경 시 vacuous pass 가 되는 지점"
            % (len(table_rows),),
        )

    info = {
        "section_anchor_line": start + 1,
        "section_anchor_text": lines[start].strip()[:120],
        "section_end_line": end,
        "table_anchor_line": anchor + 1,
        "table_anchor_text": lines[anchor].strip()[:120],
        "table_rows": len(table_rows),
        "duplicate_ng_ids": sorted(set(dup_ids)),
    }
    return ng, info


# ── 평가 ─────────────────────────────────────────────────────────────────────

def evaluate(repo_root: Path, registry_path: Path, story_path: Optional[Path]) -> gv.GateResult:
    """registry ↔ Story bijection 판정. RED 조건이 INCONCLUSIVE 보다 우선한다(fail-closed 우선)."""
    trace: Dict[str, object] = {}
    probe: Dict[str, object] = {
        "registry_path": normalize_rel(repo_root, registry_path),
        "registry_path_abs": str(registry_path),
        "story_path": normalize_rel(repo_root, story_path) if story_path else None,
        "story_path_abs": str(story_path) if story_path else None,
        "self_exclusion": SELF_EXCLUSION_DECLARE,
        "non_ng_registry_names_allowed": sorted(NON_NG_REGISTRY_NAMES),
    }

    # ── (a) registry 축 — [154-AC-4] 파싱 실패 = fail-closed ─────────────────
    try:
        entries = load_registry_entries(str(registry_path))
    except Exception as exc:  # FileNotFoundError / yaml.YAMLError / ValueError
        return gv.unknown_input(
            GATE_ID,
            "REGISTRY_UNPARSEABLE — registry 판독 실패: %s: %s" % (type(exc).__name__, exc),
            trace={"registry_entries_total": 0},
            identity_probe=probe,
        )

    reg_ng, unclassified, reg_dups = extract_registry_ng(entries)
    trace["registry_entries_total"] = len(entries)
    trace["registry_cfp2926_rows"] = len(reg_ng) + len(unclassified)
    trace["registry_ng_count"] = len(reg_ng)
    trace["registry_unclassified_count"] = len(unclassified)
    probe["registry_ng_ids"] = ["NG-%d" % n for n in sorted(reg_ng)]
    probe["registry_unclassified_names"] = unclassified

    modules = registry_module_paths(entries, reg_ng)
    missing_modules = sorted(
        ng for ng, rel in modules.items() if not (repo_root / rel).is_file()
    )
    # ★verdict 축 아님 — echo 만★ (모듈 부재는 gates workflow step 이 실행 시점에 표면화).
    trace["registry_modules_declared"] = len(modules)
    trace["registry_modules_missing"] = len(missing_modules)
    probe["registry_modules_missing_ids"] = missing_modules

    if unclassified:
        return gv.unknown_input(
            GATE_ID,
            "UNCLASSIFIED_REGISTRY_ROW — introduced_by=%s 인데 NG 이름 규약(cfp2926-ng-<n>-<slug>) "
            "밖 행 %d 건: %s. ★조용히 제외하지 않는다★ — NG 행이면 이름을 규약에 맞추고, "
            "비-NG 메타 행이면 NON_NG_REGISTRY_NAMES 에 명시 추가하라."
            % (STORY_KEY, len(unclassified), ", ".join(unclassified[:8])),
            trace=trace,
            identity_probe=probe,
        )
    if reg_dups:
        return gv.unknown_input(
            GATE_ID,
            "REGISTRY_DUPLICATE_NG — 같은 NG id 를 가진 registry 행 중복: %s "
            "(집합 비교가 중복을 흡수해 bijection 을 거짓 성립시키는 지점)"
            % (", ".join("NG-%d" % n for n in reg_dups),),
            trace=trace,
            identity_probe=probe,
        )
    if not reg_ng:
        # [154-AC-3] ★명시 분기★ — ∅ ↔ ∅ 를 "bijection 성립" 으로 읽지 않는다.
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "REGISTRY_NG_EMPTY — registry 에 introduced_by=%s NG 행 0건. §11.A.9 (h) 미이행이며, "
            "빈 집합끼리의 bijection 을 vacuous 참으로 읽지 않는다." % (STORY_KEY,),
            trace=trace,
            identity_probe=probe,
        )

    # ── (b) Story 축 — 부재/미해석을 exit 0 으로 흡수하지 않는다 ──────────────
    if story_path is None:
        return gv.empty_target(
            GATE_ID,
            "STORY_SOURCE_UNRESOLVED — --story 미지정. Story SSOT 는 별 repo"
            "(mclayer/codeforge-internal-docs)에 있고 본 모듈은 fetch 하지 않는다"
            "(caller 가 materialize 한 로컬 경로만 받는다 — ac-traceability-matrix.yml 선례 동형). "
            "대조 상대가 없으므로 ★bijection 을 검증하지 않았고 PASS 라고 말하지 않는다★. "
            "registry 측 NG %d 건은 판독했다(위 probe echo)." % (len(reg_ng),),
            trace=trace,
            identity_probe=probe,
        )

    if not story_path.is_file():
        return gv.unknown_input(
            GATE_ID,
            "STORY_PATH_UNRESOLVED — --story 로 명시된 경로가 파일이 아니다: %s. "
            "명시 입력의 미해석은 fail-closed RED 다(경로 오지정을 '대조 대상 없음'으로 흡수 금지)."
            % (story_path,),
            trace=trace,
            identity_probe=probe,
        )
    try:
        lines = read_lines(story_path, normalize_rel(repo_root, story_path))
    except UnparseableDocError as exc:
        return gv.unknown_input(
            GATE_ID,
            "STORY_UNPARSEABLE — Story 판독 실패: %s" % (exc,),
            trace=trace,
            identity_probe=probe,
        )
    trace["story_lines_scanned"] = len(lines)

    try:
        story_ng, info = extract_story_ng(lines)
    except StoryParseError as exc:
        trace["story_table_rows"] = 0
        trace["story_ng_count"] = 0
        return gv.unknown_input(
            GATE_ID,
            "%s — %s" % (exc.code, exc.detail),
            trace=trace,
            identity_probe=probe,
        )

    trace["story_section_lines"] = info["section_end_line"] - info["section_anchor_line"] + 1
    trace["story_table_rows"] = info["table_rows"]
    trace["story_ng_count"] = len(story_ng)
    probe["story_section_anchor_line"] = info["section_anchor_line"]
    probe["story_section_anchor_text"] = info["section_anchor_text"]
    probe["story_table_anchor_line"] = info["table_anchor_line"]
    probe["story_table_anchor_text"] = info["table_anchor_text"]
    probe["story_ng_ids"] = ["NG-%d" % n for n in sorted(story_ng)]

    if info["duplicate_ng_ids"]:
        return gv.unknown_input(
            GATE_ID,
            "STORY_DUPLICATE_NG — §8.0.8 (1) 표에 같은 NG id 행 중복: %s"
            % (", ".join("NG-%d" % n for n in info["duplicate_ng_ids"]),),
            trace=trace,
            identity_probe=probe,
        )

    # ── (c) bijection ────────────────────────────────────────────────────────
    missing_in_registry = sorted(set(story_ng) - set(reg_ng))
    extra_in_registry = sorted(set(reg_ng) - set(story_ng))
    trace["missing_in_registry"] = len(missing_in_registry)
    trace["extra_in_registry"] = len(extra_in_registry)

    if missing_in_registry or extra_in_registry:
        parts = []
        if missing_in_registry:
            parts.append(
                "Story 표에 있으나 registry 미등록 %d 건: %s"
                % (
                    len(missing_in_registry),
                    ", ".join("NG-%d(§8.0.8:%d)" % (n, story_ng[n]) for n in missing_in_registry),
                )
            )
        if extra_in_registry:
            parts.append(
                "registry 에 있으나 Story 표 밖 %d 건: %s ★두 SSOT 밖에서 태어난 검사 후보★"
                % (
                    len(extra_in_registry),
                    ", ".join("NG-%d(%s)" % (n, reg_ng[n]) for n in extra_in_registry),
                )
            )
        return gv.GateResult(
            GATE_ID,
            gv.RED,
            "BIJECTION_MISMATCH — " + " / ".join(parts),
            trace=trace,
            identity_probe=probe,
        )

    return gv.GateResult(
        GATE_ID,
        gv.PASS,
        "BIJECTION_OK — registry NG %d 행 ↔ Story §8.0.8 (1) NG %d 행 1:1 일치. "
        "★행 집합 일치까지만 보증★ — 행 내용 적절성·규칙 R 자신의 완전성·detection sufficiency 는 "
        "본 게이트 밖(정직 천장)." % (len(reg_ng), len(story_ng)),
        trace=trace,
        identity_probe=probe,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="X-16 — evidence-checks-registry NG 행 ↔ Story §8.0.8 (1) NG 표 bijection assert"
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--registry",
        default=None,
        help="registry yaml 경로 (기본 <repo-root>/%s)" % (DEFAULT_REGISTRY_REL.replace("\\", "/"),),
    )
    parser.add_argument(
        "--story",
        default=None,
        help="Story CFP-2926.md 의 ★로컬★ 경로. 미지정 = INCONCLUSIVE(exit 3, GREEN 아님). "
             "본 모듈은 원격 fetch 를 하지 않는다 — caller(workflow)가 materialize 한다.",
    )
    args = parser.parse_args(argv)

    repo_root = resolve_repo_root(args.repo_root)
    registry_path = (
        Path(args.registry)
        if args.registry
        else repo_root / DEFAULT_REGISTRY_REL.replace("\\", "/")
    )
    story_path = Path(args.story) if args.story else None
    result = evaluate(repo_root, registry_path, story_path)
    return gv.emit(result)


if __name__ == "__main__":
    sys.exit(main())
