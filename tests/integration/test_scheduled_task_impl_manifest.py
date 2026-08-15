#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_impl_manifest.py
#   — Story §8.7 Impl Manifest **수기 사본 폐기** 오라클 (구현리뷰 iter5 F-CR5-01)
#
# ── 계기 ──────────────────────────────────────────────────────────────────────────
#   §8.7 은 `git diff --stat` 총계 · 파일별 행수 · 테스트 수집 수 · 스위트 결과를
#   **손으로 옮겨 적어** 유지했다. 커밋이 얹힐 때마다 사본은 stale 이 되고, 같은 절이
#   *"manifest 는 Story 의 마지막 커밋 이후 갱신한다"* 는 **행위 규율**을 명문화한
#   바로 다음 라운드에 그 규율을 깼다(iter3 F-A → iter5 F-CR5-01, 3회차 발현).
#   ⇒ 사람 규율을 강화하는 대신 **수치를 기계가 생성**하고, 선언과 실측이 어긋나면
#     이 파일이 **RED** 가 된다.
#
# ── 층 3개 (각 층이 무엇을 지고 있는가) ───────────────────────────────────────────
#   ① 판별력 층 (hermetic, 항상 실행): 동결 스냅샷 fixture 로 **비교기가 실제로
#      불일치를 잡는지** 확인한다. 대조군(일치 자료 → 위반 0)이 짝으로 붙어 있어
#      "무조건 위반" 비교기는 통과하지 못한다.
#   ② 생성기 생존 층 (항상 실행): 생성기가 **상수를 뱉는 죽은 계측**이 아님을 실
#      git · 실 pytest 수집으로 확인한다.
#   ③ live 대조 층 (Story 경로 주입 시): 실 Story §8.7 과 실측을 대조한다.
#
# ── 정직 천장 (ADR-119 — 은폐 금지) ───────────────────────────────────────────────
#   · Story(§8.7 보유 문서)는 **다른 repo**(codeforge-internal-docs)에 있다. wrapper
#     CI 체크아웃에는 그 파일이 없으므로 ③ 은 CI 에서 **돌지 않는다**. 즉 "다음 커밋이
#     §8.7 을 stale 하게 만들면 CI 가 즉시 잡는다" 고 말할 수 없다 — 잡는 주체는
#     `CFP2949_STORY_FILE` 을 주입해 돌리는 로컬·오케스트레이터 실행이다.
#     ①② 는 그 조건 없이 CI 에서 항상 돌며, ③ 이 잡을 수 있는 상태를 유지시킨다.
#   · 본 파일은 §8.7 의 **수치**만 판정한다. 역할 서술·정직 천장 문단의 타당성은
#     판정하지 않는다(리뷰 소관).

import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

import impl_manifest as man                                        # noqa: E402

SNAPSHOT = REPO_ROOT / "tests" / "fixtures" / "cfp_2949" / "impl-manifest-story-snapshot.md"

# 동결 스냅샷이 선언하는 값 (fixture 를 **읽어서** 나오는 값 — 여기 박은 건 기대치다).
#   ★ 이 기대치는 fixture 와 함께 동결된다. fixture 를 갱신하면 판별 근거가 사라지므로
#     갱신하지 않는다(fixture 헤더 참조).
FROZEN_DECLARED = {
    "files_changed": 20,
    "insertions": 6155,
    "deletions": 8,
    "ci_files": 7,
    "collect_total": 99,
    "collect_selected": 98,
    "collect_deselected": 1,
    "suite_passed": 98,
    "suite_skipped": 0,      # 2-슬롯 선언 → 미기재 슬롯은 0 (FIX6-b 하위호환)
    "suite_deselected": 1,
}


@pytest.fixture(scope="module")
def snapshot_text():
    assert SNAPSHOT.is_file(), f"동결 스냅샷 부재: {SNAPSHOT}"
    return SNAPSHOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def declared(snapshot_text):
    d = man.parse_manifest_section(snapshot_text)
    assert d is not None, "§8.7 절 파싱 실패 — 스냅샷에 헤딩이 없다"
    return d


@pytest.fixture(scope="module")
def live_manifest():
    """실 repo 실측 manifest (git + pytest 수집). 모듈 1회만 계산."""
    return man.generate_manifest(str(REPO_ROOT))


# ═══════════════ ① 판별력 층 — 비교기가 실제로 stale 을 잡는가 ═══════════════════
def test_impl_manifest_parser_reads_frozen_snapshot(declared):
    """파서가 동결 스냅샷의 선언 수치를 **값으로** 읽어낸다.

    ★ 이 단언이 없으면 뒤의 비교 테스트가 "파서가 아무것도 못 읽어서" 통과할 수 있다
      (선언 부재 → 비교 대상 없음 → 조용한 통과). 값 앵커를 먼저 세운다.
    """
    for key, expected in FROZEN_DECLARED.items():
        assert declared.get(key) == expected, (
            f"§8.7 스냅샷 파싱값 불일치 {key}: {declared.get(key)!r} (기대 {expected!r})"
        )

    rows = declared.get("file_changed_lines") or {}
    assert len(rows) == 20, f"표 데이터 행 {len(rows)}개 (기대 20)"
    # `N행` 이 실제로 붙어 있는 행 (버전 bump 행은 행수 미기재 = None)
    assert rows.get("scripts/lib/scheduled_task_reconcile.py") == 829
    assert rows.get("tests/integration/test_scheduled_task_watchdog_hook.py") == 276
    assert rows.get(".claude-plugin/plugin.json") is None, (
        "행수 미기재 행은 None 으로 남아야 한다 (계약 밖 — 잘못된 0 계상 금지)"
    )

    # 스위트 선언 정의역 (FIX6-b) — 절 안 canonical span 은 **2개**(현재 98 · 선행 84),
    # 값 판정은 **첫** 선언만. 이력 서술 `83 passed, 1 failed` 는 `deselected` 슬롯이
    # 없어 canonical 정의역 밖이며 미인식으로 올라오지 **않는다**(선언된 천장).
    decls = declared.get("suite_declarations") or []
    assert [d["passed"] for d in decls] == [98, 84], decls
    assert declared.get("suite_unparsed") is None, declared.get("suite_unparsed")

    aliases = declared.get("collect_per_alias") or {}
    assert aliases == {
        "ac_matrix": 21, "dispatch_path": 7, "dynamic_roster": 14,
        "stateful": 13, "watchdog_hook": 5, "stop_flag": 9, "unit": 30,
    }, f"수집 별칭 파싱 불일치: {aliases!r}"


def test_impl_manifest_comparator_flags_stale_declaration(declared):
    """**판별 케이스** — 실측이 선언과 다르면 비교기가 그 축을 지목한다.

    generated 는 FIX6 시점 실측을 본뜬 **고정 자료**다(테스트를 git 상태에 결합시키지
    않기 위해 — 결합시키면 커밋마다 기대 문자열이 흔들려 오라클이 못 쓰게 된다).

    mutant kill: `compare_manifest` 의 `_cmp` 를 no-op 으로 바꾸면 위반 0 ⇒ RED.
    """
    generated = {
        "version": man.MANIFEST_VERSION,
        "base_ref": "origin/main", "head": "deadbee",
        "files_changed": 20, "insertions": 6581, "deletions": 8,
        "file_changed_lines": {p: n for p, n in (declared["file_changed_lines"] or {}).items()},
        "ci_files": 7,
        "collect_total": 102, "collect_selected": 101, "collect_deselected": 1,
        "ci_test_files": [
            "tests/test_scheduled_task_stop_flag.py",
            "tests/unit/test_scheduled_task_reconcile_unit.py",
            "tests/integration/test_scheduled_task_ac_matrix.py",
            "tests/integration/test_scheduled_task_dispatch_path.py",
            "tests/integration/test_scheduled_task_dynamic_roster.py",
            "tests/integration/test_scheduled_task_stateful.py",
            "tests/integration/test_scheduled_task_watchdog_hook.py",
        ],
        "collect_per_file": {
            "tests/test_scheduled_task_stop_flag.py": 9,
            "tests/unit/test_scheduled_task_reconcile_unit.py": 30,
            "tests/integration/test_scheduled_task_ac_matrix.py": 21,
            "tests/integration/test_scheduled_task_dispatch_path.py": 10,
            "tests/integration/test_scheduled_task_dynamic_roster.py": 14,
            "tests/integration/test_scheduled_task_stateful.py": 13,
            "tests/integration/test_scheduled_task_watchdog_hook.py": 5,
        },
    }
    viol = man.compare_manifest(generated, declared)
    joined = "\n".join(viol)

    # 축별로 **지목됐는지** 확인한다 (개수만 세면 어느 축이 죽었는지 안 보인다)
    assert any(v.startswith("insertions:") for v in viol), joined
    assert any(v.startswith("collect_total:") for v in viol), joined
    assert any(v.startswith("collect_selected:") for v in viol), joined
    assert any("dispatch_path" in v and "수집" in v for v in viol), joined
    assert any(v.startswith("suite_passed:") for v in viol), joined
    # 일치하는 축은 지목되지 않는다 (무차별 위반 배제)
    assert not any(v.startswith("files_changed:") for v in viol), joined
    assert not any(v.startswith("deletions:") for v in viol), joined
    assert not any("watchdog_hook" in v and "수집" in v for v in viol), joined


def test_impl_manifest_comparator_is_silent_when_declaration_is_current(declared):
    """**대조군** — 선언과 실측이 같으면 위반 **0**.

    ★ 이 케이스가 앞 테스트의 비공허성을 짊어진다. 없으면 `compare_manifest` 가
      무조건 위반을 뱉어도 판별 테스트가 통과한다.
    """
    files = [
        "tests/test_scheduled_task_stop_flag.py",
        "tests/unit/test_scheduled_task_reconcile_unit.py",
        "tests/integration/test_scheduled_task_ac_matrix.py",
        "tests/integration/test_scheduled_task_dispatch_path.py",
        "tests/integration/test_scheduled_task_dynamic_roster.py",
        "tests/integration/test_scheduled_task_stateful.py",
        "tests/integration/test_scheduled_task_watchdog_hook.py",
    ]
    alias_to_file = {man.alias_of(f): f for f in files}
    per_file = {}
    for alias, n in (declared["collect_per_alias"] or {}).items():
        hits = [f for f in files if man.alias_of(f) == alias] or \
               [f for f in files if man.alias_of(f).endswith("_" + alias)]
        assert len(hits) == 1, f"별칭 {alias!r} 해석 실패: {hits!r} (map={alias_to_file!r})"
        per_file[hits[0]] = n

    generated = {
        "files_changed": declared["files_changed"],
        "insertions": declared["insertions"],
        "deletions": declared["deletions"],
        "file_changed_lines": dict(declared["file_changed_lines"] or {}),
        "ci_files": declared["ci_files"],
        "collect_total": declared["collect_total"],
        "collect_selected": declared["collect_selected"],
        "collect_deselected": declared["collect_deselected"],
        "ci_test_files": files,
        "collect_per_file": per_file,
    }
    viol = man.compare_manifest(generated, declared)
    assert viol == [], "일치 자료인데 위반이 나왔다 (무차별 위반 비교기):\n" + "\n".join(viol)


# ═══════════ ①-b skip 슬롯 층 — 미주입(= wrapper CI 기본) 형상을 읽는가 ══════════
#
#   계기(FIX6-b): 설계 lane 이 비교기를 실사용하다 사각 2건을 실측 발견했다.
#     ① `_SUITE_RE` 에 `skipped` 슬롯이 없어 미주입 실행 결과
#        (`112 passed, 1 skipped, 1 deselected`)를 **조용히 건너뛴다**
#     ② 파생 불변식이 `passed == collect_selected` 로 **skip 0 을 가정**한다
#   ⇒ §8.7 에 skip 을 포함한 **stale** 선언을 적어도 위반 0 이 나오는 형상이었다.
#
#   ★ 미주입 실행에 skip 이 생기는 이유는 결함이 아니다 —
#     `test_impl_manifest_live_story_declaration_matches` 가 Story 경로 부재를
#     **자기 정의역 밖으로 선언하며** skip 하는 것이다(실패 아님).

_SUITE_SECTION_TMPL = man.SECTION_HEADING + """

**테스트 수집** (`pytest --collect-only -q` 파일별 실측, 동결 HEAD `deadbee`): \
1 파일 **%(total)d건** = stop_flag %(total)d. CI 인자 `-m "not requires_golden"` 적용 시 \
**선택 %(sel)d / deselected %(desel)d**.

스위트 실행: %(decl)s

## 다음 절
"""


def _suite_case(declaration, collect_selected=113, collect_deselected=1):
    """스위트 선언 줄 하나만 바꾼 §8.7 축소본 → (generated, declared) 쌍.

    ★ 수집 축 수치는 generated 와 **일치시킨다** — 교란 제거. 어긋나게 두면 위반이
      나와도 그 원인이 수집 축인지 스위트 축인지 갈리지 않아, 스위트 축이 죽어도
      테스트가 통과할 수 있다.
    """
    total = collect_selected + collect_deselected
    declared = man.parse_manifest_section(_SUITE_SECTION_TMPL % {
        "decl": declaration, "sel": collect_selected,
        "desel": collect_deselected, "total": total,
    })
    generated = {
        "collect_total": total,
        "collect_selected": collect_selected,
        "collect_deselected": collect_deselected,
    }
    return generated, declared


def test_impl_manifest_parser_reads_skipped_slot():
    """`N passed, M skipped, K deselected` 를 **값으로** 읽는다 (구판은 못 읽었다)."""
    _, declared = _suite_case("`112 passed, 1 skipped, 1 deselected`")
    assert declared.get("suite_passed") == 112, declared
    assert declared.get("suite_skipped") == 1, declared
    assert declared.get("suite_deselected") == 1, declared
    assert declared.get("suite_unparsed") is None, (
        "canonical 선언인데 미인식으로 분류됐다: %r" % declared.get("suite_unparsed")
    )


def test_impl_manifest_parser_keeps_legacy_two_slot_declaration():
    """**하위호환** — `skipped` 미기재 선언은 그대로 읽히고 skip 은 0 으로 간주된다."""
    _, declared = _suite_case("`113 passed, 1 deselected`")
    assert declared.get("suite_passed") == 113, declared
    assert declared.get("suite_skipped") == 0, "미기재 슬롯은 0 이어야 한다"
    assert declared.get("suite_deselected") == 1, declared


def test_impl_manifest_comparator_accepts_skip_bearing_declaration():
    """**대조군 + M-SKIP-INVARIANT kill** — 정직한 skip 선언은 위반 **0**.

    `선택 113 = 112 passed + 1 skipped` (skip 은 deselected 와 달리 selected 에 포함).

    mutant kill: 불변식을 `suite_passed == collect_selected` 로 되돌리면
    `112 != 113` 이라 위반이 나온다 ⇒ RED.
    """
    generated, declared = _suite_case("`112 passed, 1 skipped, 1 deselected`")
    viol = man.compare_manifest(generated, declared)
    assert viol == [], (
        "정직한 skip-포함 선언이 구조적 위반이 됐다 (skip 0 가정 잔존):\n"
        + "\n".join(viol)
    )


def test_impl_manifest_comparator_flags_stale_skip_bearing_declaration():
    """**M-SUITE-BLIND kill (판별 케이스)** — skip 을 포함한 **stale** 선언을 잡는다.

    ★ 이 케이스가 사각 ①의 실물이다. `_SUITE_RE` 에 `skipped` 슬롯이 없으면 파서가
      이 줄을 통째로 건너뛰어 `suite_passed` 키가 안 생기고, 키가 없으면 비교기가
      비교를 건너뛰어 **위반 0 으로 조용히 통과**한다(= mutant 생존).
    """
    generated, declared = _suite_case("`112 passed, 1 skipped, 1 deselected`",
                                      collect_selected=999)
    viol = man.compare_manifest(generated, declared)
    assert any(v.startswith("suite_passed:") for v in viol), (
        "stale 한 skip-포함 선언이 조용히 통과했다:\n" + "\n".join(viol)
    )
    # 교란 없음 — 어긋난 축은 스위트 하나뿐이므로 위반도 하나뿐이어야 한다
    assert len(viol) == 1, "스위트 축 외 위반이 섞였다 (통제 실패):\n" + "\n".join(viol)


def test_impl_manifest_comparator_flags_unparsed_suite_line():
    """**M-SUITE-UNPARSED kill** — 스위트 줄이 있는데 **못 읽으면** 그 자체가 위반.

    ★ 구판은 **미인식**과 **부재**가 같은 경로였다(둘 다 키 부재 → 비교 skip →
      무결 통과). 검사기가 "선언 없음" 과 "선언 불일치" 를 구분하지 못하는 형상이다.
    """
    for corrupted in ("`112 passed / 1 skipped / 1 deselected`",
                      "`113 passed, 1 deselected, 2 xfailed`",
                      "`113 passed,1deselected`"):
        generated, declared = _suite_case(corrupted)
        viol = man.compare_manifest(generated, declared)
        assert any("미인식" in v for v in viol), (
            "못 읽는 스위트 줄이 무결로 통과했다 (%s):\n%s" % (corrupted, "\n".join(viol))
        )


def test_impl_manifest_comparator_flags_absent_suite_line():
    """**부재 경로 분리** — 스위트 줄을 통째로 지워도 조용히 통과하지 않는다."""
    declared = man.parse_manifest_section(
        _SUITE_SECTION_TMPL.replace("스위트 실행: %s", "(스위트 줄 없음)")
    )
    assert declared.get("suite_passed") is None
    viol = man.compare_manifest({"collect_selected": 113}, declared)
    assert any(v.startswith("suite_passed: 선언 부재") for v in viol), viol
    # 부재와 미인식은 **다른 메시지**여야 한다 (같은 경로로 뭉개지 않는다)
    assert not any("미인식" in v for v in viol), viol


def test_impl_manifest_comparator_flags_missing_section():
    """§8.7 자체가 사라지면 **조용히 통과하지 않는다**."""
    assert man.parse_manifest_section("# 다른 문서\n\n본문뿐\n") is None
    viol = man.compare_manifest({"files_changed": 1}, None)
    assert viol and "§8.7 절 부재" in viol[0], viol


# ═══════════════ ② 생성기 생존 층 — 상수를 뱉는 죽은 계측이 아닌가 ════════════════
def test_impl_manifest_ci_file_list_is_read_from_workflow():
    """CI 인자 목록의 SSOT = workflow YAML (파이썬 상수 사본 0)."""
    files = man.ci_test_files(str(REPO_ROOT))
    assert files, "workflow 에서 테스트 인자를 하나도 읽지 못했다"
    for f in files:
        assert (REPO_ROOT / f).is_file(), f"workflow 인자가 실재하지 않는 파일: {f}"
    # 본 파일 자신이 CI 인자에 있어야 한다 — born-dead 차단
    assert "tests/integration/test_scheduled_task_impl_manifest.py" in files, (
        "본 오라클이 CI 인자 목록에 없다 — 배선되지 않은 테스트는 존재해도 돌지 않는다"
    )


def test_impl_manifest_generator_collect_axis_is_live(live_manifest):
    """수집 축이 **실 pytest 수집**에서 왔는가 (상수·0 배제)."""
    assert "collect_axis_unavailable" not in live_manifest, live_manifest.get(
        "collect_axis_unavailable")
    per = live_manifest["collect_per_file"]
    assert set(per) == set(live_manifest["ci_test_files"]), "파일별 수집 정의역 불일치"
    assert all(isinstance(v, int) and v > 0 for v in per.values()), (
        f"수집 0건 파일이 있다 (born-dead 의심): {per!r}"
    )
    # 비공허 앵커: 파일별 합 == 총계 (총계가 상수라면 이 등식이 깨진다)
    assert sum(per.values()) == live_manifest["collect_total"], (
        f"파일별 합 {sum(per.values())} ≠ 총계 {live_manifest['collect_total']}"
    )
    assert live_manifest["collect_selected"] + live_manifest["collect_deselected"] \
        == live_manifest["collect_total"], "선택 + 제외 ≠ 총계"
    assert live_manifest["collect_deselected"] >= 1, (
        "requires_golden 마커가 하나도 제외되지 않았다 — AC-1 live 축(§8.4)이 "
        "사라졌거나 mark 인자가 무력화됐다"
    )


def test_impl_manifest_generator_git_axis_is_live_or_declares_why(live_manifest):
    """git 축은 실측되거나, **불가 사유가 기록**된다 (조용한 0 계상 금지)."""
    if "git_axis_unavailable" in live_manifest:
        assert live_manifest["git_axis_unavailable"], "사유가 빈 문자열이다"
        pytest.skip("git 축 미가용: %s" % live_manifest["git_axis_unavailable"])

    assert live_manifest["files_changed"] == len(live_manifest["file_changed_lines"])
    if live_manifest["files_changed"] == 0:
        # main 위 push 등 diff 가 비는 정의역 — 사실로 수용하되 조용히 넘기지 않는다
        assert live_manifest["insertions"] == 0 and live_manifest["deletions"] == 0
        return
    assert live_manifest["insertions"] > 0, "변경 파일이 있는데 삽입 0 (실측 아님 의심)"
    for path, n in live_manifest["file_changed_lines"].items():
        assert n is None or n >= 0, f"음수 변경 행수: {path}={n}"
    # 비공허 앵커: 본 Story 의 production SUT 가 diff 에 있다
    assert "scripts/lib/scheduled_task_reconcile.py" in live_manifest["file_changed_lines"], (
        "본 Story SUT 가 diff 에 없다 — base ref 가 엉뚱하거나 브랜치가 아니다"
    )


def test_impl_manifest_render_markdown_round_trips(live_manifest):
    """생성기 출력(§8.7 붙여넣기용 줄)을 **파서가 되읽어** 같은 값을 준다.

    ★ 라운드트립이 깨지면 "기계가 만든 줄을 붙였는데 검사기가 못 읽는" 상태가 되어
      기계화 자체가 무력화된다. 생성↔파싱 계약을 여기서 결박한다.
    """
    if "collect_axis_unavailable" in live_manifest or "git_axis_unavailable" in live_manifest:
        pytest.skip("축 미가용 — 라운드트립 정의역 밖")
    md = man.render_markdown(live_manifest)
    text = man.SECTION_HEADING + "\n\n" + md + "\n\n## 다음 절\n"
    back = man.parse_manifest_section(text)
    assert back is not None
    for key in ("files_changed", "insertions", "deletions",
                "ci_files", "collect_total", "collect_selected", "collect_deselected"):
        assert back.get(key) == live_manifest[key], (
            f"라운드트립 불일치 {key}: 생성 {live_manifest[key]!r} → 재파싱 {back.get(key)!r}"
        )
    # 표 축(`file_changed_lines`)은 markdown 선언 줄에 없다 — 라운드트립 정의역 밖이며
    # 그 사실을 여기 남긴다(없는 축을 검사한 척하지 않는다).
    assert "file_changed_lines" not in back or not back["file_changed_lines"], (
        "markdown 선언 줄에서 표 행이 파싱됐다 — 정의역 가정이 깨졌다"
    )


# ═══════════════ ③ live 대조 층 — 실 Story §8.7 (경로 주입 시) ═══════════════════
def test_impl_manifest_live_story_declaration_matches(live_manifest):
    """실 Story §8.7 ↔ 실측 대조. 경로 미주입이면 그 사실을 명시하고 skip.

    주입: `CFP2949_STORY_FILE=<path> pytest ...` (하드코딩 경로 없음 — Story 는
    별 repo 자산이다). CI 에서는 통상 미주입이며, 그때 이 층이 돌지 않는다는 사실은
    파일 헤더 정직 천장에 선언돼 있다.
    """
    story = man.resolve_story_path()
    if story is None:
        pytest.skip("Story 경로 미주입 (%s) — live 대조 미수행 (①② 는 무조건 실행)"
                    % man.ENV_STORY_FILE)
    assert os.path.isfile(story), f"주입된 Story 파일 부재: {story}"
    declared_live = man.parse_manifest_section(Path(story).read_text(encoding="utf-8"))
    viol = man.compare_manifest(live_manifest, declared_live)
    assert viol == [], (
        "§8.7 선언이 실측과 어긋난다 (%d건) — `bash scripts/gen-impl-manifest.sh "
        "generate --markdown` 산출로 갱신하라:\n%s" % (len(viol), "\n".join("  - " + v for v in viol))
    )


# ══════════ 헬퍼 자신의 직접 오라클 (구현리뷰 iter6 F-CR6-05) ═══════════════════
# ★ `man.extract_section` 은 형제 헬퍼(`test_scheduled_task_ac_matrix.py::
#   extract_adr_section`)와 **같은 종료조건**을 쓰는데, 그 종료조건을 구판
#   (`^#{N} ` = 정확히 같은 레벨만)으로 되돌려도 이 파일의 스위트가 전건 GREEN 이었다 —
#   §8.7 fixture 들이 절 뒤에 곧바로 같은 레벨 헤딩을 두는 **배치**라서 h2 흡수 형상이
#   만들어지지 않는다. 아래는 그 형상을 직접 만들어 종료 지점을 **값으로** 고정한다.
_SLICE_FIXTURE = """# 문서 제목

## 상위 절 A

### 8.7 Impl Manifest
- 총계: 1 파일
#### 하위 절
하위 본문
## 8.8 다음 절
다음 절 본문
"""

_SLICE_EXPECTED = """### 8.7 Impl Manifest
- 총계: 1 파일
#### 하위 절
하위 본문
"""


class TestExtractSectionTerminator:
    """`man.extract_section` 의 **종료 지점을 값으로** 고정한다.

    mutant kill: `end_re = re.compile(r"^#{1,%d} " % max(level, 1))` →
      `r"^#{%d} "` (정확히 같은 레벨만) 되돌리기 ⇒ 아래 첫 테스트 RED.
    """

    def test_stops_before_higher_level_heading(self):
        """`### X` 다음에 `## Y` 가 오면 **`## Y` 직전**에서 끝난다 (h2 흡수 0)."""
        got = man.extract_section(_SLICE_FIXTURE)
        assert got == _SLICE_EXPECTED, (
            "종료 지점이 어긋났다 — 상위 레벨 헤딩을 흡수했거나 하위 레벨에서 잘렸다.\n"
            f"기대:\n{_SLICE_EXPECTED!r}\n실제:\n{got!r}"
        )
        assert "## 8.8 다음 절" not in got, "상위 레벨 절을 삼켰다"
        assert "#### 하위 절" in got, "하위 레벨 절이 잘렸다 — 절의 일부여야 한다"

    def test_stops_before_h1(self):
        """상위 레벨은 h2 만이 아니다 — `# Z` 도 종료다."""
        text = "### 8.7 Impl Manifest\n본문\n# 최상위\n뒤\n"
        got = man.extract_section(text)
        assert got == "### 8.7 Impl Manifest\n본문\n", f"h1 에서 멈추지 않았다: {got!r}"

    def test_stops_at_same_level_sibling(self):
        """**회귀 가드**: 같은 레벨 형제에서 멈추는 기존 동작은 그대로다."""
        text = "### 8.7 Impl Manifest\n본문\n### 8.8 형제\n뒤\n"
        got = man.extract_section(text)
        assert got == "### 8.7 Impl Manifest\n본문\n", f"같은 레벨 종료가 깨졌다: {got!r}"

    def test_absent_heading_returns_none(self):
        """헤딩 부재 → None (형제 헬퍼는 AssertionError — 계약이 다르다는 사실을 고정)."""
        assert man.extract_section("## 다른 문서\n본문\n") is None


# ════════ 스위트 실패 삼킴 (FIX14) — 생성 축이 자기 실패를 기록하는가 ════════════
#
# ── 계기 (실물, 합성 아님) ────────────────────────────────────────────────────────
#   본 Story 의 9파일 스위트를 CI 인자 그대로 돌린 실행이 rc=1 로 끝나며
#       `1 failed, 163 passed, 1 skipped, 1 deselected in 471.16s (0:07:51)`
#   를 냈는데, 생성기의 §8.7 스위트 줄은 `163 passed, 1 skipped, 1 deselected` 였다.
#   원인 2개가 겹쳤다 — (a) `suite_axis` 가 `cp.returncode` 를 보지 않았다 (b) 요약 줄
#   정규식에 `failed` 슬롯이 없어 `search` 가 선두 `1 failed,` 를 건너뛰었다.
#   ⇒ **수기 사본을 없애려고 만든 장치가 자기 산출에서 실패를 삼켰다.**
#
# ── 그물 3겹 (한 겹이 뚫려도 다른 겹이 잡게) ──────────────────────────────────────
#   ⓪   실측 비-green(failed/error) → 선언 값이 맞아떨어져도 위반
#   ⓪-b 실행 outcome 합 ≠ 수집 선택 수 → 요약 줄을 일부만 읽었다는 신호
#   ⓪-c rc≠0 인데 실패 토큰 부재 → 설명되지 않은 비정상 종료(pytest rc 2/3/4/5)
#
# ── 이 절이 세우지 **않는** 것 ────────────────────────────────────────────────────
#   실패가 **기록**되는지까지다. 그 실패의 원인, 스위트가 옳은 것을 재는지는 판정하지
#   않는다 — 그 축은 리뷰·해당 오라클 소관이다.

FAILING_RUN_TAIL = REPO_ROOT / "tests" / "fixtures" / "cfp_2949" / "pytest-failing-run-tail.txt"

# 동결 자료가 담은 **실측 사실** (자료 헤더와 같은 값 — 여기 박은 건 기대치다)
REAL_FAILING_RC = 1
REAL_FAILING_LINE = "1 failed, 163 passed, 1 skipped, 1 deselected in 471.16s (0:07:51)"
REAL_COLLECT_SELECTED = 165          # 163 passed + 1 skipped + 1 failed (deselected 는 밖)


@pytest.fixture(scope="module")
def failing_stdout():
    assert FAILING_RUN_TAIL.is_file(), f"동결 자료 부재: {FAILING_RUN_TAIL}"
    return FAILING_RUN_TAIL.read_text(encoding="utf-8")


class TestSuiteAxisDoesNotSwallowFailure:
    """생성 축이 **자기 실패를 기록**하는가 (FIX14).

    mutant kill 3종:
      ① rc 판정 제거 (`summarize_suite_run` 의 `suite_rc_unexplained` 분기 삭제)
         ⇒ `test_nonzero_rc_without_failure_tokens_is_a_violation` RED
      ② `failed` 슬롯 제거 (`_SUITE_KNOWN_OUTCOMES` 에서 failed/error 제거)
         ⇒ `test_captured_real_failing_run_is_read_as_failing` RED
      ③ 미인식을 무결로 (`suite_axis_unavailable` 를 빈 dict 로 대체)
         ⇒ `test_unrecognized_summary_is_not_treated_as_clean` RED
    """

    # ── 반사실: **현재 실물** 입력이 위반으로 올라오는가 ──────────────────────────
    def test_captured_real_failing_run_is_read_as_failing(self, failing_stdout):
        """**M-② kill** — 실 실행 산출에서 실패 1건을 값으로 읽어낸다."""
        got = man.summarize_suite_run(failing_stdout, REAL_FAILING_RC)

        assert got.get("suite_failed") == 1, f"실패가 산출에서 사라졌다: {got!r}"
        assert got.get("suite_errors") == 0, got
        assert got.get("suite_passed") == 163, got
        assert got.get("suite_skipped") == 1, got
        assert got.get("suite_deselected") == 1, got
        assert got.get("suite_returncode") == REAL_FAILING_RC, got
        assert got.get("suite_summary_line") == REAL_FAILING_LINE, got
        assert "suite_axis_unavailable" not in got, got

    def test_legacy_regex_read_the_same_input_as_green(self, failing_stdout):
        """이 동결 자료가 **판별 자료**임을 귀속한다 — 구판은 여기서 초록이었다.

        ★ 이 테스트가 없으면 위 케이스가 "원래도 통과하던 입력" 을 시험하는 공허한
          단언일 수 있다. 구판 형상을 그 자리에서 재현해, 자료가 두 판본을 실제로
          **가른다**는 것을 값으로 고정한다.
        """
        legacy = re.compile(
            r"(\d+)\s+passed(?:,\s*(\d+)\s+skipped)?(?:,\s*(\d+)\s+deselected)?"
        )
        hit = None
        for ln in reversed([l.strip() for l in failing_stdout.splitlines() if l.strip()]):
            hit = legacy.search(ln)
            if hit:
                break

        assert hit is not None, "구판 정규식이 아무것도 못 읽었다 — 재현 형상이 아니다"
        assert (int(hit.group(1)), int(hit.group(2) or 0), int(hit.group(3) or 0)) \
            == (163, 1, 1), hit.groups()
        assert "failed" not in hit.group(0), (
            "구판 정규식이 실패를 포착했다면 이 자료는 판별 자료가 아니다: %r" % hit.group(0)
        )

    def test_summary_line_finder_anchors_on_line_shape(self, failing_stdout):
        """트레이스백 줄을 요약 줄로 오인하지 않는다.

        ★ 반례가 자료 안에 있다: `... timed out after 60 seconds` 는 `60 seconds` 라는
          `N word` 토큰을 갖는다. 줄 형상을 앵커하지 않고 토큰만 훑으면 이 줄이 잡힌다.
        """
        assert "timed out after 60 seconds" in failing_stdout, (
            "전제 붕괴: 반례 줄이 동결 자료에 없다 — 이 케이스가 공허해진다"
        )
        counts, line, unknown = man.parse_suite_summary(failing_stdout)

        assert line == REAL_FAILING_LINE, f"요약 줄 오인: {line!r}"
        assert unknown == [], f"화이트리스트 밖 토큰이 잡혔다: {unknown!r}"
        assert "seconds" not in counts, counts

    # ── ⓪ 실측 비-green 은 선언과 무관하게 위반 ─────────────────────────────────
    def test_generated_failure_is_a_violation_even_when_declaration_matches(
            self, failing_stdout):
        """**⓪ kill — FIX14 결함의 정확한 형상**.

        구판 생성기가 뱉은 초록 줄을 §8.7 에 그대로 붙이면 **값이 서로 맞는다**. 그래서
        값 대조 축은 조용하고, 이 케이스를 잡는 것은 비-green 판정 하나뿐이다.
        아래 두 번째 단언이 그 귀속을 고정한다(다른 축이 잡아 준 것이 아니다).
        """
        generated, declared = _suite_case("`163 passed, 1 skipped, 1 deselected`",
                                          collect_selected=REAL_COLLECT_SELECTED,
                                          collect_deselected=1)
        generated.update(man.summarize_suite_run(failing_stdout, REAL_FAILING_RC))

        viol = man.compare_manifest(generated, declared)
        joined = "\n".join(viol)

        assert any(v.startswith("suite_failed:") for v in viol), (
            "실패 1건이 있는 실행이 무결로 통과했다:\n" + joined
        )
        assert not any(v.startswith("suite_passed:") for v in viol), (
            "값 대조 축이 잡아 준 것이라면 ⓪ 의 판별력이 귀속되지 않는다:\n" + joined
        )

    def test_partially_read_summary_is_caught_by_run_total_invariant(self):
        """**⓪-b kill (독립 그물)** — 실행 outcome 합이 수집 선택 수에 못 미치면 위반.

        ★ 구판 파서가 돌려주던 dict 를 그대로 먹인다. 파싱을 고치지 않았더라도 이 그물
          하나로 FIX14 형상이 잡힌다(163 + 1 = 164 ≠ 165).
        """
        generated, declared = _suite_case("`163 passed, 1 skipped, 1 deselected`",
                                          collect_selected=REAL_COLLECT_SELECTED,
                                          collect_deselected=1)
        generated.update({"suite_passed": 163, "suite_skipped": 1, "suite_deselected": 1,
                          "suite_failed": 0, "suite_errors": 0, "suite_returncode": 0})

        viol = man.compare_manifest(generated, declared)
        assert any(v.startswith("suite_run_total:") for v in viol), (
            "요약 줄을 일부만 읽은 실행 축이 무결로 통과했다:\n" + "\n".join(viol)
        )

    def test_nonzero_rc_without_failure_tokens_is_a_violation(self):
        """**M-① kill** — rc≠0 인데 요약 줄이 초록이면 그 자체가 위반.

        pytest rc 2(중단)·3(내부 오류)·4(사용법)·5(수집 0)가 이 형상이다. 요약 줄만
        믿으면 중단된 실행이 완주한 실행으로 기록된다.
        """
        got = man.summarize_suite_run("163 passed, 1 skipped, 1 deselected in 10.00s\n", 2)
        assert "suite_rc_unexplained" in got, got

        generated, declared = _suite_case("`163 passed, 1 skipped, 1 deselected`",
                                          collect_selected=164, collect_deselected=1)
        generated.update(got)

        viol = man.compare_manifest(generated, declared)
        assert any(v.startswith("suite_returncode:") for v in viol), (
            "rc≠0 실행이 무결로 통과했다:\n" + "\n".join(viol)
        )

    def test_unrecognized_summary_is_not_treated_as_clean(self):
        """**M-③ kill** — 요약 줄을 못 읽으면 무결이 아니라 위반이다.

        (이 모듈이 선언 축에서 이미 지는 규율의 생성 축 확장 — 미인식 ≠ 무결.)
        """
        for stdout, rc in (("no tests ran in 0.01s\n", 5),
                           ("ERROR: file or directory not found: tests/nope.py\n", 4),
                           ("", 3)):
            got = man.summarize_suite_run(stdout, rc)
            assert "suite_axis_unavailable" in got, (stdout, got)
            assert "suite_passed" not in got, (
                "읽지 못한 실행에 passed 값이 생겼다: %r" % (got,)
            )

            viol = man.compare_manifest(dict(got), {"section_present": True})
            assert any(v.startswith("suite_axis_unavailable:") for v in viol), (
                "미인식 요약이 조용히 통과했다 (%r):\n%s" % (stdout, "\n".join(viol))
            )

    def test_unknown_outcome_token_is_reported(self):
        """화이트리스트 밖 outcome 토큰은 계상 정의역 밖임을 밝힌다.

        ★ 슬롯 열거식의 알려진 실패 양태: pytest 가 토큰을 하나 늘리면 조용히 눈이 먼다.
          모르는 토큰을 만나면 합계를 신뢰할 수 없다고 **말한다**.
        """
        got = man.summarize_suite_run("163 passed, 2 flaked, 1 deselected in 3.00s\n", 0)
        assert got.get("suite_unknown_tokens") == ["2 flaked"], got

        generated, declared = _suite_case("`163 passed, 1 deselected`",
                                          collect_selected=163, collect_deselected=1)
        generated.update(got)

        viol = man.compare_manifest(generated, declared)
        assert any(v.startswith("suite_unknown_tokens:") for v in viol), (
            "모르는 토큰이 섞인 요약이 조용히 통과했다:\n" + "\n".join(viol)
        )

    # ── 대조군 — 새 그물이 "무차별 위반" 이 아님 ────────────────────────────────
    def test_green_run_reports_zero_violations(self):
        """**대조군** — 실패 없는 실행 + 일치 선언 = 위반 없음.

        ★ 이 케이스가 위 판별 케이스들의 비공허성을 짊어진다. 없으면 비-green 판정을
          모든 입력에 대해 발화시켜도 판별 테스트가 전부 통과한다.
        """
        got = man.summarize_suite_run(
            "164 passed, 1 skipped, 1 deselected in 300.00s (0:05:00)\n", 0)
        assert got["suite_failed"] == 0 and got["suite_errors"] == 0, got
        assert "suite_rc_unexplained" not in got, got
        assert "suite_unknown_tokens" not in got, got

        generated, declared = _suite_case("`164 passed, 1 skipped, 1 deselected`",
                                          collect_selected=165, collect_deselected=1)
        generated.update(got)

        viol = man.compare_manifest(generated, declared)
        assert viol == [], "실패 없는 일치 자료인데 위반이 나왔다:\n" + "\n".join(viol)

    # ── 파생 불변식 재검토: 선언 축에는 failed 슬롯이 없다 ──────────────────────
    def test_declared_shortfall_from_a_failing_run_is_flagged(self):
        """**파생 불변식 (FIX14 재검토)** — 실행 축이 없는 대조에서 실패는 **부족분**이다.

        선언 축 canonical 형식(`N passed[, M skipped], K deselected`)에는 failed 슬롯이
        없다. 그래서 `check` 기본 경로(실행 축 미수집)에서는 `passed + skipped` 가 수집
        선택 수에 **못 미치는 것**으로 실패가 드러난다 — 164 ≠ 165 가 실물 수치다.
        선언 축 정규식을 넓히지 않은 이유이기도 하다(기존 §8.7 선언 하위호환 보존).
        """
        generated, declared = _suite_case("`163 passed, 1 skipped, 1 deselected`",
                                          collect_selected=REAL_COLLECT_SELECTED,
                                          collect_deselected=1)

        viol = man.compare_manifest(generated, declared)      # 실행 축 없음 → 파생 경로
        joined = "\n".join(viol)
        assert any(v.startswith("suite_passed:") for v in viol), joined
        assert any("failed/error" in v for v in viol), (
            "부족분의 원인 후보로 실패를 지목하지 않는다:\n" + joined
        )

    # ── 렌더 — 하위호환 ⊕ 거짓 초록 거부 ───────────────────────────────────────
    def test_render_markdown_green_line_is_byte_identical_to_legacy_form(self):
        """**하위호환** — 실패 없는 실행의 §8.7 줄은 FIX14 이전과 byte 동형이다.

        두 번째 자료는 `suite_returncode` 키가 **없는** 구 dict 다 — 새 키를 갖추지 않은
        호출자도 같은 줄을 얻는다는 것을 고정한다.
        """
        cases = (
            ({"suite_passed": 164, "suite_skipped": 1, "suite_deselected": 1,
              "suite_failed": 0, "suite_errors": 0, "suite_returncode": 0},
             "스위트 실행: `164 passed, 1 skipped, 1 deselected`"),
            ({"suite_passed": 98, "suite_skipped": 0, "suite_deselected": 1},
             "스위트 실행: `98 passed, 1 deselected`"),
        )
        for src, expected in cases:
            assert man.render_markdown(src) == expected, (
                "초록 렌더가 바뀌었다 — 기존 §8.7 선언과의 하위호환이 깨진다: %r"
                % man.render_markdown(src)
            )

    def test_render_markdown_refuses_to_render_failure_as_green(self, failing_stdout):
        """실패한 실행을 붙여넣을 수 있는 초록 줄로 렌더하지 않는다.

        ★ 구판은 그 줄을 뱉었고, 그 줄이 §8.7 에 들어갔다. 렌더가 거짓 초록을 만들지
          않는지까지 봐야 대조기 수정이 실효를 갖는다(생성기가 계속 거짓을 뱉으면
          사람이 그것을 붙이고 대조는 통과한다).
        """
        got = man.summarize_suite_run(failing_stdout, REAL_FAILING_RC)
        md = man.render_markdown(got)

        assert "`163 passed" not in md, f"실패 실행이 canonical 초록 줄로 렌더됐다: {md!r}"
        assert "비-green" in md and "failed 1" in md, md

        # 그대로 붙여넣어도 선언 파서가 초록으로 읽지 못한다
        back = man.parse_manifest_section(
            man.SECTION_HEADING + "\n\n" + md + "\n\n## 다음 절\n")
        assert back is not None and back.get("suite_passed") is None, (
            "비-green 렌더가 초록 선언으로 되읽혔다: %r" % (back,)
        )

    # ── 종단 (실 프로세스) ──────────────────────────────────────────────────────
    def test_suite_axis_end_to_end_on_a_real_failing_pytest_run(self, tmp_path):
        """**종단** — 실제로 실패하는 pytest 를 띄워 rc 경로까지 지난다.

        ★ 위 케이스들은 동결 산출을 먹인다. 이 케이스만이 `suite_axis` 가 프로세스를
          띄우고 그 **종료코드를 실제로 받아 오는** 경로를 지난다 — 파싱만 고치고 rc 를
          계속 버리는 구현을 배제한다.
        ★ 격리: repo 밖 tmp 에 자기 rootdir(`pytest.ini`)을 세운다.
        """
        (tmp_path / "pytest.ini").write_text(
            "[pytest]\nmarkers =\n    requires_golden: golden 의존\n",
            encoding="utf-8", newline="\n")
        (tmp_path / "test_e2e_suite_axis.py").write_text(
            "import pytest\n"
            "def test_ok_1(): pass\n"
            "def test_ok_2(): pass\n"
            "def test_boom(): assert 1 == 2\n"
            "def test_skipped(): pytest.skip('정의역 밖')\n"
            "@pytest.mark.requires_golden\n"
            "def test_deselected(): pass\n",
            encoding="utf-8", newline="\n")

        got = man.suite_axis(str(tmp_path), ["test_e2e_suite_axis.py"])

        assert got.get("suite_returncode") not in (None, 0), (
            f"실패하는 스위트인데 rc 가 0 이다 (rc 미수집 의심): {got!r}"
        )
        assert got.get("suite_failed") == 1, got
        assert got.get("suite_passed") == 2, got
        assert got.get("suite_skipped") == 1, got
        assert got.get("suite_deselected") == 1, got

        viol = man.compare_manifest(dict(got, collect_selected=4), {"section_present": True})
        assert any(v.startswith("suite_failed:") for v in viol), (
            "실 프로세스 실패가 대조에서 무결로 통과했다:\n" + "\n".join(viol)
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
