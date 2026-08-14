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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
