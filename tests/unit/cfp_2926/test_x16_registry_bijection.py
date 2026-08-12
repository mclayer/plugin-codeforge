"""X-16 — evidence-checks-registry NG 행 ↔ Story §8.0.8 (1) NG 표 bijection assert.

Story §9.8 (5) 승계 blocking #1 (설계리뷰 iter3 Codex peer (A) 지목) / §8.0.8 정직 천장 ④ 완화 ⒝.
대상 = ``scripts/lib/check_ng_registry_bijection.py``.

★검사기준 규율★ — 각 테스트는 "게이트가 무엇을 검출한다"를 선언하는 대신 ★그 결함을 실제로
주입해 non-GREEN 을 확인★ 하고, 원본에서 GREEN 을 확인하는 ★왕복(negative control)★ 을 갖는다.
왕복이 없는 단정("항상 RED" 와 구별 불가)은 이 파일에 두지 않는다.

★exit-masking 금지★ (ADR-171 §결정 5) — 모든 판정은 exit code 를 직접 비교한다.
★INCONCLUSIVE 는 exit 0 이 아니다★ 를 별도 계약 테스트로 못 박는다.

Carrier: CFP-2926 Phase 2 (구현) / X-16
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import check_ng_registry_bijection as gate
import gate_verdict as gv

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_REGISTRY = REPO_ROOT / "docs" / "evidence-checks-registry.yaml"
#: Story SSOT 는 별 repo(codeforge-internal-docs). wrapper 체크아웃에는 없을 수 있다 —
#: 있으면 live 대조하고, 없으면 ★그 사실을 명시하고 skip★ 한다(거짓 GREEN 금지).
LIVE_STORY_CANDIDATES = (
    Path.home() / ".claude" / "worktrees" / "codeforge-internal-docs" / "cfp-2926-phase2"
    / "wrapper" / "stories" / "CFP-2926.md",
)


# ── 합성 fixture 빌더 (CI 결정론 — live 파일 의존 0) ──────────────────────────

_REG_ENTRY = """  - name: cfp2926-ng-{n}-synthetic-gate
    description: |
      synthetic NG-{n}
    detect_command: python3 scripts/lib/check_synthetic_{n}.py --repo-root .
    workflow: templates/github-workflows/cfp-2926-phase2-gates.yml
    current_tier: warning
    introduced_by: CFP-2926
    owner_adr: ADR-154
    carrier_adr: ADR-171
    status: Active
"""


def write_registry(tmp_path: Path, ng_ids, extra_blocks=()) -> Path:
    body = [
        'schema_version: "1.6"',
        "introduced_by: CFP-TEST",
        "entries:",
        "  - name: unrelated-pre-existing-check",
        "    description: |",
        "      CFP-2926 과 무관한 기존 entry — 선택 정의역 밖임을 확인하는 대조군.",
        "    detect_command: bash scripts/check-unrelated.sh",
        "    workflow: templates/github-workflows/unrelated.yml",
        "    current_tier: warning",
        "    introduced_by: CFP-0001",
        "    owner_adr: ADR-001",
        "    carrier_adr: ADR-171",
        "    status: Active",
    ]
    text = "\n".join(body) + "\n"
    for n in ng_ids:
        text += _REG_ENTRY.format(n=n)
    for blk in extra_blocks:
        text += blk
    path = tmp_path / "registry.yaml"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def write_story(
    tmp_path: Path,
    ng_ids,
    section_heading: str = "#### 8.0.8 ADR-154 self-verification 번들 매핑",
    table_anchor: str = "**(1) 신규 게이트 인벤토리 × 번들 매핑** — 4 항목 전건.",
    cell_fmt: str = "**NG-{n}**",
    name: str = "CFP-2926.md",
) -> Path:
    lines = [
        "# Story CFP-2926",
        "",
        "### 8.0.2 RTM",
        "",
        "| AC | test | tier |",
        "|---|---|---|",
        "| AC-1 | `test_x` | T1 |",
        "",
        section_heading,
        "",
        "> 왜 이 절이 신설되는가 — 규칙 R 도출.",
        "",
        "| §7.14 P | G2 | 귀속 |",
        "|---|---|---|",
        "| P-3 | ✔ | NG-2 · NG-3 |",   # ★첫 셀이 NG 가 아닌 감사표 — 오검출 대조군★
        "",
        table_anchor,
        "",
        "| NG | 신규 게이트 | 대응 |",
        "|---|---|---|",
    ]
    for n in ng_ids:
        lines.append("| %s | synthetic gate %s | AC-%s |" % (cell_fmt.format(n=n), n, n))
    lines += [
        "",
        "> 정직 천장 — presence 까지.",
        "",
        "#### 8.0.9 frozen 앵커 규격",
        "",
        "| NG | 밖 표 |",   # ★섹션 밖 표 — 범위 누출 대조군★
        "|---|---|",
        "| **NG-77** | 섹션 밖이라 잡히면 안 된다 |",
        "",
    ]
    path = tmp_path / name
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def run_gate(tmp_path: Path, registry: Path, story):
    """evaluate() 직접 호출 → (exit_code, GateResult)."""
    result = gate.evaluate(tmp_path, registry, story)
    return result.exit_code, result


# ── 0. negative control — 원본은 GREEN ────────────────────────────────────────

def test_matching_sets_pass_negative_control(tmp_path):
    """registry 21 ↔ Story 21 일치 → PASS(exit 0). ★왕복의 GREEN 쪽★."""
    ids = list(range(1, 22))
    rc, res = run_gate(tmp_path, write_registry(tmp_path, ids), write_story(tmp_path, ids))
    assert rc == 0, res.to_json()
    assert res.verdict == gv.PASS
    assert res.trace["registry_ng_count"] == 21
    assert res.trace["story_ng_count"] == 21
    assert res.trace["missing_in_registry"] == 0
    assert res.trace["extra_in_registry"] == 0


def test_decorated_and_out_of_section_cells_do_not_break_extraction(tmp_path):
    """★ 로 장식된 셀은 인정하고, §8.0.8 밖 표(NG-77)·감사표(첫 셀 비-NG)는 잡지 않는다."""
    ids = list(range(1, 22))
    story = write_story(tmp_path, ids, cell_fmt="★**NG-{n}**★")
    rc, res = run_gate(tmp_path, write_registry(tmp_path, ids), story)
    assert rc == 0, res.to_json()
    assert res.identity_probe["story_ng_ids"] == ["NG-%d" % n for n in ids]
    assert "NG-77" not in res.identity_probe["story_ng_ids"]


# ── 1. bijection 위반 (M-A / M-B) ────────────────────────────────────────────

def test_row_missing_from_registry_is_red(tmp_path):
    """Story 에 있으나 registry 미등록 → RED. (mutant M-A)"""
    story_ids = list(range(1, 22))
    reg_ids = [n for n in story_ids if n != 7]
    rc, res = run_gate(
        tmp_path, write_registry(tmp_path, reg_ids), write_story(tmp_path, story_ids)
    )
    assert rc == 1, res.to_json()
    assert res.verdict == gv.RED
    assert "BIJECTION_MISMATCH" in res.reason
    assert "NG-7" in res.reason
    assert res.trace["missing_in_registry"] == 1

    # ★왕복★ — 행 복원 시 GREEN
    rc2, res2 = run_gate(
        tmp_path, write_registry(tmp_path, story_ids), write_story(tmp_path, story_ids)
    )
    assert rc2 == 0, res2.to_json()


def test_phantom_row_in_registry_is_red(tmp_path):
    """registry 에 있으나 Story 표 밖 → RED. ★두 SSOT 밖에서 태어난 검사★ 검출 축. (mutant M-B)"""
    story_ids = list(range(1, 22))
    reg_ids = story_ids + [99]
    rc, res = run_gate(
        tmp_path, write_registry(tmp_path, reg_ids), write_story(tmp_path, story_ids)
    )
    assert rc == 1, res.to_json()
    assert "BIJECTION_MISMATCH" in res.reason
    assert "NG-99" in res.reason
    assert res.trace["extra_in_registry"] == 1

    rc2, _ = run_gate(
        tmp_path, write_registry(tmp_path, story_ids), write_story(tmp_path, story_ids)
    )
    assert rc2 == 0


# ── 2. Story 입력 축 (M-C 계열) — ★부재를 exit 0 으로 흡수하지 않는다★ ────────

def test_story_omitted_is_inconclusive_not_green(tmp_path):
    """--story 미지정 → INCONCLUSIVE(exit 3). ★exit 0 절대 금지★."""
    rc, res = run_gate(tmp_path, write_registry(tmp_path, [1, 2]), None)
    assert rc == 3, res.to_json()
    assert rc != 0
    assert res.verdict == gv.INCONCLUSIVE
    assert "STORY_SOURCE_UNRESOLVED" in res.reason
    # registry 측은 판독했음을 trace 로 증명 (판정 유보 ≠ 아무것도 안 함)
    assert res.trace["registry_ng_count"] == 2


def test_story_path_misspecified_is_red(tmp_path):
    """명시한 --story 경로가 파일이 아님 → RED(exit 1). (mutant M-C)"""
    rc, res = run_gate(
        tmp_path, write_registry(tmp_path, [1]), tmp_path / "no-such-story.md"
    )
    assert rc == 1, res.to_json()
    assert "STORY_PATH_UNRESOLVED" in res.reason


def test_story_directory_path_is_red(tmp_path):
    """--story 가 디렉터리 → RED (파일 아님을 조용히 넘기지 않는다)."""
    rc, res = run_gate(tmp_path, write_registry(tmp_path, [1]), tmp_path)
    assert rc == 1, res.to_json()
    assert "STORY_PATH_UNRESOLVED" in res.reason


def test_section_anchor_missing_is_red(tmp_path):
    """§8.0.8 섹션 heading 부재 → RED (엉뚱한 문서를 통과시키지 않는다)."""
    other = tmp_path / "other.md"
    with io.open(other, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# 무관 문서\n\n본문.\n")
    rc, res = run_gate(tmp_path, write_registry(tmp_path, [1]), other)
    assert rc == 1, res.to_json()
    assert "SECTION_ANCHOR_NOT_FOUND" in res.reason


def test_table_anchor_rename_is_red(tmp_path):
    """표 앵커 문면 rename → RED. ★heading/문면 rename → 0행 vacuous pass★ 봉인. (mutant M-C3)"""
    ids = list(range(1, 22))
    story = write_story(tmp_path, ids, table_anchor="**(1) 게이트 목록 표**")
    rc, res = run_gate(tmp_path, write_registry(tmp_path, ids), story)
    assert rc == 1, res.to_json()
    assert "TABLE_ANCHOR_NOT_FOUND" in res.reason

    rc2, _ = run_gate(tmp_path, write_registry(tmp_path, ids), write_story(tmp_path, ids))
    assert rc2 == 0


def test_ng_cell_format_change_is_extraction_empty_red(tmp_path):
    """첫 셀 형식 변경으로 추출 0 → EXTRACTION_EMPTY RED. ★0행을 '일치'로 읽지 않는다★. (M-C4)"""
    ids = list(range(1, 22))
    story = write_story(tmp_path, ids, cell_fmt="**Gate {n}**")
    rc, res = run_gate(tmp_path, write_registry(tmp_path, ids), story)
    assert rc == 1, res.to_json()
    assert "EXTRACTION_EMPTY" in res.reason
    assert res.trace["story_ng_count"] == 0


def test_duplicate_story_ng_id_is_red(tmp_path):
    """Story 표 안 NG id 중복 → RED (집합 비교가 중복을 흡수하는 지점)."""
    ids = [1, 2, 3, 3]
    rc, res = run_gate(tmp_path, write_registry(tmp_path, [1, 2, 3]), write_story(tmp_path, ids))
    assert rc == 1, res.to_json()
    assert "STORY_DUPLICATE_NG" in res.reason


# ── 3. registry 입력 축 (M-E / M-F / M-G / M-H) ──────────────────────────────

def test_unclassified_cfp2926_row_is_red(tmp_path):
    """introduced_by=CFP-2926 인데 NG 이름 규약 밖 → RED. ★조용한 행 제외 금지★. (mutant M-E)"""
    ids = list(range(1, 22))
    rogue = (
        "  - name: cfp2926-some-other-gate\n"
        "    description: |\n"
        "      NG 이름 규약 밖 CFP-2926 행.\n"
        "    detect_command: python3 scripts/lib/check_other.py\n"
        "    workflow: templates/github-workflows/cfp-2926-phase2-gates.yml\n"
        "    current_tier: warning\n"
        "    introduced_by: CFP-2926\n"
        "    owner_adr: ADR-154\n"
        "    carrier_adr: ADR-171\n"
        "    status: Active\n"
    )
    registry = write_registry(tmp_path, ids, extra_blocks=(rogue,))
    rc, res = run_gate(tmp_path, registry, write_story(tmp_path, ids))
    assert rc == 1, res.to_json()
    assert "UNCLASSIFIED_REGISTRY_ROW" in res.reason
    assert "cfp2926-some-other-gate" in res.reason
    assert res.trace["registry_unclassified_count"] == 1

    # ★왕복★ — rogue 행 제거 시 GREEN
    rc2, _ = run_gate(tmp_path, write_registry(tmp_path, ids), write_story(tmp_path, ids))
    assert rc2 == 0


def test_unclassified_row_is_not_silently_dropped_into_pass(tmp_path):
    """★판별력 핵심★ — rogue 행을 '조용히 무시' 하는 구현이었다면 이 케이스가 PASS 였을 것이다.

    rogue 행을 뺀 나머지가 완전한 bijection(1..21 ↔ 1..21)을 이루도록 구성한다.
    즉 ★bijection 자체는 성립★ 하므로, RED 의 유일한 원인은 unclassified 검출이다.
    """
    ids = list(range(1, 22))
    rogue = (
        "  - name: cfp2926-meta-gate-x\n"
        "    description: |\n"
        "      bijection 은 성립하는데 이 행만 규약 밖.\n"
        "    detect_command: python3 scripts/lib/check_meta.py\n"
        "    workflow: templates/github-workflows/cfp-2926-phase2-gates.yml\n"
        "    current_tier: warning\n"
        "    introduced_by: CFP-2926\n"
        "    owner_adr: ADR-154\n"
        "    carrier_adr: ADR-171\n"
        "    status: Active\n"
    )
    rc, res = run_gate(
        tmp_path,
        write_registry(tmp_path, ids, extra_blocks=(rogue,)),
        write_story(tmp_path, ids),
    )
    assert rc == 1, "조용한 제외 구현이면 여기서 exit 0 이 났을 것: %s" % res.to_json()
    assert "UNCLASSIFIED_REGISTRY_ROW" in res.reason


def test_duplicate_registry_ng_id_is_red(tmp_path):
    """registry NG id 중복 → RED. (mutant M-F)"""
    ids = [1, 2, 3]
    dup = _REG_ENTRY.format(n=3).replace(
        "cfp2926-ng-3-synthetic-gate", "cfp2926-ng-3-duplicate-gate"
    )
    rc, res = run_gate(
        tmp_path, write_registry(tmp_path, ids, extra_blocks=(dup,)), write_story(tmp_path, ids)
    )
    assert rc == 1, res.to_json()
    assert "REGISTRY_DUPLICATE_NG" in res.reason


def test_empty_registry_ng_is_explicit_red_not_vacuous_pass(tmp_path):
    """registry NG 0행 → ★명시 분기 RED★. ∅ ↔ ∅ 를 bijection 성립으로 읽지 않는다. (mutant M-G)

    ★"0 != 21 이라 우연히 RED" 에 의존하지 않음을 보인다★ — Story 측도 동시에 0 이 되도록
    만들 수 없으므로(EXTRACTION_EMPTY 가 먼저 발화), registry 0 자체가 독립 RED 사유임을
    reason code 로 확인한다.
    """
    rc, res = run_gate(tmp_path, write_registry(tmp_path, []), write_story(tmp_path, [1, 2]))
    assert rc == 1, res.to_json()
    assert "REGISTRY_NG_EMPTY" in res.reason
    assert res.trace["registry_ng_count"] == 0


def test_unparseable_registry_is_red(tmp_path):
    """registry 문법 파손 → RED (fail-closed, 조용한 skip 금지). (mutant M-H)"""
    broken = tmp_path / "broken.yaml"
    with io.open(broken, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("entries:\n  - name: x\n\tbad: tab\n")
    rc, res = run_gate(tmp_path, broken, write_story(tmp_path, [1]))
    assert rc == 1, res.to_json()
    assert "REGISTRY_UNPARSEABLE" in res.reason


def test_registry_missing_file_is_red(tmp_path):
    """registry 파일 부재 → RED."""
    rc, res = run_gate(tmp_path, tmp_path / "nope.yaml", write_story(tmp_path, [1]))
    assert rc == 1, res.to_json()
    assert "REGISTRY_UNPARSEABLE" in res.reason


# ── 4. ADR-154 번들 계약 ([154-AC-3/4/5/13]) ─────────────────────────────────

def test_inconclusive_never_maps_to_exit_zero():
    """[154-AC-3] 계약 — INCONCLUSIVE 는 어떤 경우에도 exit 0 이 아니다."""
    assert gv.EXIT_BY_VERDICT[gv.INCONCLUSIVE] == 3
    assert gv.EXIT_BY_VERDICT[gv.INCONCLUSIVE] != 0
    assert gv.EXIT_BY_VERDICT[gv.RED] == 1


def test_trace_emits_numeric_counts(tmp_path):
    """[154-AC-5] execution-trace — 검사량이 numeric 으로 emit 된다."""
    ids = list(range(1, 22))
    _, res = run_gate(tmp_path, write_registry(tmp_path, ids), write_story(tmp_path, ids))
    for key in (
        "registry_entries_total",
        "registry_cfp2926_rows",
        "registry_ng_count",
        "story_lines_scanned",
        "story_table_rows",
        "story_ng_count",
        "missing_in_registry",
        "extra_in_registry",
    ):
        assert key in res.trace, "trace 누락: %s" % key
        assert isinstance(res.trace[key], int), "%s 가 numeric 아님" % key
    assert res.trace["story_lines_scanned"] > 0
    assert res.trace["story_table_rows"] > 0


def test_identity_probe_echoes_resolved_targets(tmp_path):
    """[154-AC-13] identity probe — 실제로 판독한 대상(경로·앵커 줄·원문)을 echo 한다."""
    ids = list(range(1, 22))
    story = write_story(tmp_path, ids)
    _, res = run_gate(tmp_path, write_registry(tmp_path, ids), story)
    probe = res.identity_probe
    assert probe["story_path_abs"] == str(story)
    assert probe["story_section_anchor_line"] > 0
    assert "8.0.8" in probe["story_section_anchor_text"]
    assert "신규 게이트 인벤토리" in probe["story_table_anchor_text"]
    assert probe["registry_ng_ids"] == ["NG-%d" % n for n in ids]


def test_self_exclusion_declared_in_every_verdict(tmp_path):
    """★self-exclusion 은 조용한 제외가 아니다★ — PASS·RED·INCONCLUSIVE 전 verdict 에서 echo."""
    ids = list(range(1, 22))
    cases = [
        run_gate(tmp_path, write_registry(tmp_path, ids), write_story(tmp_path, ids)),      # PASS
        run_gate(tmp_path, write_registry(tmp_path, ids[:-1]), write_story(tmp_path, ids)),  # RED
        run_gate(tmp_path, write_registry(tmp_path, ids), None),                             # INCONCLUSIVE
    ]
    seen = set()
    for rc, res in cases:
        seen.add(rc)
        declare = res.identity_probe["self_exclusion"]
        assert "NG 행이 아니다" in declare
        assert "메타-게이트" in declare
        assert res.identity_probe["non_ng_registry_names_allowed"] == []
    assert seen == {0, 1, 3}, "3-state 전건이 실증되지 않음: %s" % (seen,)


def test_self_exclusion_constant_is_empty_by_design():
    """제외 확장은 ★코드 diff★ 로만 가능하다 — 현재 의도적 공집합."""
    assert gate.NON_NG_REGISTRY_NAMES == frozenset()


def test_gate_id_is_not_an_ng_id():
    """본 게이트 id 는 NG-n 이 아니다 (인벤토리 밖 메타-게이트임을 id 로 표시)."""
    assert gate.GATE_ID.startswith("X-16")
    assert not gate.REGISTRY_NG_NAME_RE.match(gate.GATE_ID)


# ── 5. live 대조 (실 registry / 실 Story) ────────────────────────────────────

def test_live_registry_has_expected_ng_rows():
    """실 registry 에 CFP-2926 NG 행이 실재하고 미분류 0 (§11.A.9 (h) 이행 실측)."""
    from check_deferred_followup_reconcile import load_registry_entries

    entries = load_registry_entries(str(LIVE_REGISTRY))
    ng, unclassified, dups = gate.extract_registry_ng(entries)
    assert unclassified == [], "미분류 CFP-2926 행: %s" % (unclassified,)
    assert dups == [], "중복 NG id: %s" % (dups,)
    assert sorted(ng) == list(range(1, 22)), "NG id 집합 불일치: %s" % (sorted(ng),)


def test_bijection_gate_itself_is_not_registered_as_ng_row():
    """★self-exclusion 의 기계 확인★ — 본 모듈을 가리키는 registry 행이 존재하지 않는다.

    등록되어 있으면 bijection 이 자기 자신 때문에 깨지므로, 그 상태를 테스트가 잡는다.
    """
    text = LIVE_REGISTRY.read_text(encoding="utf-8")
    assert "check_ng_registry_bijection.py" not in text.replace(
        "check_ng_registry_bijection.py 가 assert", ""
    ), "본 메타-게이트가 registry 행으로 등록됨 — bijection 자기파괴"


def _live_story():
    for cand in LIVE_STORY_CANDIDATES:
        if cand.is_file():
            return cand
    return None


def test_live_registry_matches_live_story_when_reachable():
    """실 registry ↔ 실 Story bijection. ★Story 미도달 시 skip 하되 그 사실을 명시★.

    (거짓 GREEN 금지 — skip 은 "검증했다"가 아니라 "검증하지 못했다"의 기록이다.)
    """
    story = _live_story()
    if story is None:
        pytest.skip(
            "Story SSOT(codeforge-internal-docs CFP-2926.md) 로컬 미도달 — live bijection "
            "미검증(검증 성공 아님). 합성 fixture 축 테스트는 그대로 유효."
        )
    rc, res = run_gate(REPO_ROOT, LIVE_REGISTRY, story)
    assert rc == 0, res.to_json()
    assert res.trace["registry_ng_count"] == res.trace["story_ng_count"] == 21


# ── 6. CLI 경계 (main / argparse / emit) ─────────────────────────────────────

def test_main_returns_exit_code_and_emits_single_json_line(tmp_path, capsys):
    """main() 은 exit code 를 ★반환★ 하고 단일 라인 JSON 을 emit 한다 (sys.exit 미호출)."""
    ids = list(range(1, 22))
    registry = write_registry(tmp_path, ids)
    story = write_story(tmp_path, ids)
    rc = gate.main(
        ["--repo-root", str(tmp_path), "--registry", str(registry), "--story", str(story)]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1, "단일 라인 JSON 계약 위반: %s" % (out,)
    payload = json.loads(out[0])
    assert payload["gate_id"] == gate.GATE_ID
    assert payload["verdict"] == "PASS"
    assert payload["identity_probe"]["self_exclusion"]


def test_main_without_story_returns_three(tmp_path, capsys):
    """CLI 경로에서도 --story 부재 = exit 3 (0 흡수 경로 부재)."""
    registry = write_registry(tmp_path, [1, 2, 3])
    rc = gate.main(["--repo-root", str(tmp_path), "--registry", str(registry)])
    assert rc == 3
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["verdict"] == "INCONCLUSIVE"
