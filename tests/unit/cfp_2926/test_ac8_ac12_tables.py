"""test_ac8_ac12_tables.py — CFP-2926 RTM 명명 테스트 (AC-8 / AC-12).

Story §8.0.2 RTM:
  | AC-8  | test_doc_queue_five_ssot_consistency | T1 | 5 site 중 1건 역전 → RED |
  | AC-12 | test_slot_budget_table_sums_to_20    | T1 | 4+14+2 ≠ 20 → RED       |

대상 모듈:
  - `scripts/lib/check_doc_queue_ssot.py`     (GATE_ID = "NG-4")
  - `scripts/lib/check_slot_budget_table.py`  (GATE_ID = "NG-21")

★판별력 규율★ — 두 테스트 모두 **양성 baseline(GREEN) ↔ mutant(RED) 왕복**을 한
테스트 안에서 수행한다. mutant 만 있으면 "항상 RED" 와 구별 불가이고, baseline 만
있으면 "항상 GREEN" 과 구별 불가다.

★결정론(T1) 규율★ — 판정 입력은 전부 tmp_path 합성 fixture 다. 실 repo prose 상태에
verdict 를 결합시키지 않는다(다른 워커가 같은 파일을 편집 중이면 flaky 가 된다).
단 NG-4 는 ★경로 pin 이 실 repo 에서 5 site 로 resolve 되는지★ 만 별도 smoke 로
확인한다 — 경로 오타는 정확히 "4 site 만 읽고 통과" 라는 vacuous-pass 를 만드는
축이고, 이것만은 합성 fixture 로 잡을 수 없다.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import check_doc_queue_ssot
import check_slot_budget_table


# ──────────────────────────────────────────────────────────────────────────
# 공통 helper
# ──────────────────────────────────────────────────────────────────────────
def _run(module, *cli_args):
    """게이트 모듈을 in-process 실행 → (exit_code, verdict_dict).

    `emit()` 은 sys.exit 을 호출하지 않고 exit code 를 **반환**하므로(gate_verdict
    계약) 그대로 붙잡을 수 있다.
    """
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = module.main(["prog", *cli_args])
    payload = json.loads(buf.getvalue().strip().splitlines()[-1])
    return code, payload


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ──────────────────────────────────────────────────────────────────────────
# AC-8 / NG-4 — doc-queue 5-SSOT 교차
# ──────────────────────────────────────────────────────────────────────────
_PLAYBOOK_OK = """## 11. Cross-agent write coordination

**wrapper repo 자신은** `.claude-work/doc-queue/**` write queue 를 쓰지 않는다.

> **두 축 분리 (CFP-2926)**: "wrapper-self 미사용" != "doc-queue 폐기".
> **lane plugin agent 의 doc-queue 제출 규약은 live** — agent md 가 권한을 보유한다.
"""

_REQ_CLAUDE_OK = """## Self-write 책임

| Path | 책임 agent | Mechanism |
|---|---|---|
| `docs/stories/<KEY>.md §4.1` | ChangeImpactAgent (write queue drain) | `.claude-work/doc-queue/` |

> **doc-queue 규약 = live (CFP-2926)**: 위 mechanism 은 **정본**이다.
"""

_TEMPLATE_OK = """### §11. 참조

#### §11.A 데이터 마이그레이션 (ArchitectAgent — CFP-2926 번호 정합)

| 단계 | 갱신 섹션 | Owner agent |
|---|---|---|
| 요구사항 병렬 | §4.1·§4.2·§4.3 | ChangeImpactAgent (write queue drain) |
"""

_DESIGN_CLAUDE_OK = """## Self-write 책임

| Path | 책임 agent |
|---|---|
| `docs/stories/<KEY>.md §11.A 데이터 마이그레이션 mirror` (§11 자체 = pmo 소유) | ArchitectAgent |
"""

_AGENT_MD = """---
name: {name}
permissions:
  allow:
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
---

본문.
"""


def _build_ssot_repo(root, agent_md_count=None):
    """NG-4 가 기대하는 5 site 를 모두 갖춘 합성 repo 를 만든다."""
    if agent_md_count is None:
        agent_md_count = check_doc_queue_ssot.MIN_AGENT_MD_WITH_QUEUE_PERMISSION + 5

    _write(root / "docs" / "orchestrator-playbook.md", _PLAYBOOK_OK)
    _write(root / "plugins" / "codeforge-requirements" / "CLAUDE.md", _REQ_CLAUDE_OK)
    _write(root / "templates" / "story-page-structure.md", _TEMPLATE_OK)
    _write(root / "plugins" / "codeforge-design" / "CLAUDE.md", _DESIGN_CLAUDE_OK)
    for i in range(agent_md_count):
        _write(
            root / "plugins" / "codeforge-design" / "agents" / f"Agent{i:02d}.md",
            _AGENT_MD.format(name=f"Agent{i:02d}"),
        )
    return root


def test_doc_queue_five_ssot_consistency(tmp_path, repo_root):
    """AC-8 — 쓰기 소유권 5-SSOT 가 단일 방향인지 교차 대조한다.

    RTM mutant 계약: ★5 site 중 1건 역전 → RED★.
    추가로 ★4 site 만 읽고 통과 금지★(경로 1개 소실 → non-GREEN)를 함께 고정한다.
    """
    # ── baseline (negative control) : 5 site 전건 resolved → PASS ──────────
    base = _build_ssot_repo(tmp_path / "base")
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(base))
    assert code == 0, out
    assert out["verdict"] == "PASS"
    assert out["reason"] == "five_ssot_single_direction"
    assert out["trace"]["sites_compared"] == check_doc_queue_ssot.EXPECTED_SITE_COUNT == 5
    assert set(out["identity_probe"]["resolved_site_paths"]) == {
        "S1", "S2", "S3", "S4", "S5"
    }

    # ── M-1 ★RTM 계약★ : site 1건(S2) 역전 → RED ─────────────────────────
    m1 = _build_ssot_repo(tmp_path / "m1")
    _write(
        m1 / "plugins" / "codeforge-requirements" / "CLAUDE.md",
        _REQ_CLAUDE_OK + "\n`.claude-work/doc-queue/**` write queue 는 폐기한다.\n",
    )
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m1))
    assert code == 1, out
    assert out["verdict"] == "RED"
    assert out["reason"] == "ssot_direction_conflict"
    hits = out["identity_probe"]["reverse_hits"]
    assert [h["site_id"] for h in hits] == ["S2"], hits
    # 나머지 4 site 는 여전히 resolved — "1건만 역전" 이 판정을 뒤집었음을 고정
    assert out["trace"]["sites_compared"] == 5
    assert out["trace"]["conflicting_sites"] == 1

    # ── M-2 ★4 site 통과 금지★ : site 경로 1개 제거 → non-GREEN ──────────
    m2 = _build_ssot_repo(tmp_path / "m2")
    (m2 / "plugins" / "codeforge-design" / "CLAUDE.md").unlink()
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m2))
    assert code != 0, out
    assert code == 3, out  # INCONCLUSIVE — GREEN 으로 흡수되지 않는다
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["reason"] == "site_count_shortfall"
    assert out["trace"]["sites_compared"] == 4
    assert [
        s["site_id"] for s in out["identity_probe"]["unresolved_sites"]
    ] == ["S5"]

    # ── M-3 : S5 두-주인 부활(§11.A → bare §11) → RED ─────────────────────
    m3 = _build_ssot_repo(tmp_path / "m3")
    _write(
        m3 / "plugins" / "codeforge-design" / "CLAUDE.md",
        _DESIGN_CLAUDE_OK.replace("§11.A 데이터 마이그레이션", "§11 데이터 마이그레이션"),
    )
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m3))
    assert code == 1, out
    assert out["reason"] == "ssot_direction_conflict"
    assert out["identity_probe"]["reverse_hits"][0]["site_id"] == "S5"

    # ── M-4 : 방향 선언 자체 삭제 → undetermined RED (역전과 다른 분기) ───
    m4 = _build_ssot_repo(tmp_path / "m4")
    _write(
        m4 / "docs" / "orchestrator-playbook.md",
        _PLAYBOOK_OK.replace("제출 규약은 live", "제출 규약"),
    )
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m4))
    assert code == 1, out
    assert out["reason"] == "ssot_direction_undetermined"
    assert out["identity_probe"]["missing_require"]["S1"] == [
        "submission_convention_live"
    ]

    # ── M-5 : agent md 군 대량 소거 → site 미성립 → non-GREEN ─────────────
    m5 = _build_ssot_repo(
        tmp_path / "m5",
        agent_md_count=check_doc_queue_ssot.MIN_AGENT_MD_WITH_QUEUE_PERMISSION - 1,
    )
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m5))
    assert code == 3, out
    assert out["reason"] == "site_count_shortfall"
    assert [
        s["site_id"] for s in out["identity_probe"]["unresolved_sites"]
    ] == ["S4"]

    # ── M-6 ★[154-AC-4]★ : unparseable doc → 조용한 제외 아니라 fail-closed ─
    m6 = _build_ssot_repo(tmp_path / "m6")
    with open(m6 / "templates" / "story-page-structure.md", "wb") as fh:
        fh.write(b"\xff\xfe invalid utf-8 \x80\x81")
    code, out = _run(check_doc_queue_ssot, "--repo-root", str(m6))
    assert code == 1, out
    assert out["verdict"] == "RED"
    assert out["reason"] == "unparseable_doc"

    # ── live smoke : 경로 pin 이 실 repo 에서 5 site 로 resolve 되는가 ─────
    # ★verdict 는 단정하지 않는다★ — prose 상태는 다른 워커 소유라 결정론 밖.
    # 여기서 고정하는 것은 "경로 오타로 site 가 조용히 4개가 되지 않는다" 뿐이다.
    _, live = _run(check_doc_queue_ssot, "--repo-root", str(repo_root))
    assert live["trace"]["sites_compared"] == 5, live["identity_probe"]
    assert live["reason"] != "site_count_shortfall"


# ──────────────────────────────────────────────────────────────────────────
# AC-12 / NG-21 — 슬롯 예산 표 합
# ──────────────────────────────────────────────────────────────────────────
_SLOT_DOC_OK = """# 절차서

## 7.7.4 슬롯 — static budget 예산

| 몫 | 슬롯 | 근거 |
|---|---:|---|
| **Reserved (lead 전용, 대여 금지)** | **4** | dual-peer 2 + research 1 + FIX 진단 1 |
| lane PL pool | **14** | per-PL cap 6 (동시 lane <= 2) |
| Headroom (미할당 고정) | **2** | depth-2 불가시분 흡수 |

- 초과 = spawn 하지 말고 lead 에 요청.

## 다음 절
"""


def _slot_doc(root, body, name="docs/slot.md"):
    path = root / name
    _write(path, body)
    return ["--repo-root", str(root), "--doc", name]


def test_slot_budget_table_sums_to_20(tmp_path):
    """AC-12 — 슬롯 예산 표가 실재하고 그 합이 20 인지 검사한다.

    RTM mutant 계약: ★4+14+2 != 20 → RED★.
    ★핵심★ — "표가 없어서 합이 0 이라 우연히 != 20" 경로에 의존하지 않음을
    ★reason 문자열이 서로 다르다★ 는 것으로 실증한다(§8.0.8 NG-21 명시 분기 요구).
    """
    reasons = {}

    # ── baseline (negative control) : 4+14+2 = 20 → PASS ──────────────────
    ok = tmp_path / "ok"
    code, out = _run(check_slot_budget_table, *_slot_doc(ok, _SLOT_DOC_OK))
    assert code == 0, out
    assert out["verdict"] == "PASS"
    assert out["reason"] == "slot_budget_sum_ok"
    assert out["trace"]["parsed_rows"] == 3
    assert out["trace"]["row_values"] == [4, 14, 2]
    assert out["trace"]["sum"] == 20 == check_slot_budget_table.EXPECTED_TOTAL
    assert out["identity_probe"]["budget_column_header"] == "슬롯"

    # ── M-a ★RTM 계약★ : 4 → 5 (합 21) → RED ─────────────────────────────
    bad_sum = tmp_path / "bad_sum"
    code, out = _run(
        check_slot_budget_table,
        *_slot_doc(bad_sum, _SLOT_DOC_OK.replace("| **4** |", "| **5** |")),
    )
    assert code == 1, out
    assert out["verdict"] == "RED"
    assert out["reason"] == "slot_budget_sum_mismatch"
    # ★합계 분기에 도달했음을 실증★ — 추출은 성공했고 값만 틀렸다
    assert out["trace"]["parsed_rows"] == 3
    assert out["trace"]["sum"] == 21
    reasons["sum_mismatch"] = out["reason"]

    # ── M-b ★heading rename → anchor 소멸★ : sum 분기와 다른 이름으로 RED ─
    renamed = tmp_path / "renamed"
    code, out = _run(
        check_slot_budget_table,
        *_slot_doc(
            renamed,
            _SLOT_DOC_OK.replace(
                "## 7.7.4 슬롯 — static budget 예산", "## 7.7.4 동시성 몫 배분"
            ),
        ),
    )
    assert code == 1, out
    assert out["reason"] == "table_heading_not_found"
    # ★"우연히 RED" 아님의 증거★ — 합계 산술에 애초에 도달하지 않았다
    assert out["trace"]["sum"] is None
    assert out["trace"]["parsed_rows"] == 0
    reasons["heading_gone"] = out["reason"]

    # ── M-c : heading 유지 + 데이터 행 0 (header+separator 만) → RED ──────
    zero_rows = tmp_path / "zero_rows"
    stripped = "\n".join(
        ln
        for ln in _SLOT_DOC_OK.splitlines()
        if not (ln.startswith("| ") and ("**" in ln or "Headroom" in ln or "lane PL" in ln))
    )
    code, out = _run(check_slot_budget_table, *_slot_doc(zero_rows, stripped + "\n"))
    assert code == 1, out
    assert out["reason"] == "table_rows_zero"
    assert out["trace"]["sum"] is None
    reasons["rows_zero"] = out["reason"]

    # ── M-d : heading 유지 + 표 블록 통째 삭제 → RED ─────────────────────
    no_table = tmp_path / "no_table"
    code, out = _run(
        check_slot_budget_table,
        *_slot_doc(
            no_table,
            "# 절차서\n\n## 7.7.4 슬롯 — static budget 예산\n\n산문만 있고 표가 없다.\n\n## 다음 절\n",
        ),
    )
    assert code == 1, out
    assert out["reason"] == "table_not_found"
    reasons["no_table"] = out["reason"]

    # ── M-e ★[154-AC-4]★ : 표 셀 비수치 → exit 1 (조용한 행 제외 금지) ────
    non_numeric = tmp_path / "non_numeric"
    code, out = _run(
        check_slot_budget_table,
        *_slot_doc(non_numeric, _SLOT_DOC_OK.replace("| **14** |", "| **TBD** |")),
    )
    assert code == 1, out
    assert out["verdict"] == "RED"
    assert out["reason"] == "non_numeric_cell"
    assert out["trace"]["failure_kind"] == "not_an_integer"
    # 앞선 1행만 파싱된 채 끊겼음 = 남은 행을 조용히 버리고 합산하지 않았다
    assert out["trace"]["parsed_rows"] == 1
    reasons["non_numeric"] = out["reason"]

    # ── M-f : 대상 문서 자체 부재 → RED ───────────────────────────────────
    missing = tmp_path / "missing"
    missing.mkdir(parents=True, exist_ok=True)
    code, out = _run(
        check_slot_budget_table, "--repo-root", str(missing), "--doc", "docs/slot.md"
    )
    assert code == 1, out
    assert out["reason"] == "target_doc_not_found"
    reasons["doc_missing"] = out["reason"]

    # ── ★명시 분기 실증★ : 6 실패 경로의 reason 이 전부 서로 다르다 ──────
    assert len(set(reasons.values())) == len(reasons) == 6, reasons
