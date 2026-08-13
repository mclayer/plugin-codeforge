#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""test_ac16_lane_overlap.py — CFP-2926 AC-16 / NG-8 lane overlap predicate RTM 테스트.

RTM (Story §8.0.2): `AC-16 | — | test_lane_overlap_predicate_c1_c2_c3 | T1 |
write_set 교집합 1건 주입 → 불허`

Story §8.0.8 (1) NG-8 규격:
  - empty-target : `read_set`/`write_set` **미선언** → non-GREEN
                   ∧ `write_set` 추출 결과 0행 → `EXTRACTION_EMPTY` fail-closed
                   (선언은 됐고 **추출만 0** 인 경우가 종전 미분류 — 설계리뷰 iter2 P1-B)
  - unknown-input: 미지 glob → fail-closed ∧ lane `CLAUDE.md` self-write 표
                   unparseable → exit 1
  - trace        : 대조 lane 쌍 수 · 추출 lane 수 · `write_set` 원소 수
  - identity_bearing: **true** — 채널 = 각 lane `CLAUDE.md` self-write 표(기계 추출, §7.10)

★★P2-b (설계리뷰 iter3 blocking 승계) — 본 테스트가 검증하는 핵심★★
  종전 fail-closed 는 "추출 0 → EXTRACTION_EMPTY" **관측치 단독**이었다.
  ⇒ 추출 lane 이 **6 → 5** 로 조용히 줄어드는 형상은 EXTRACTION_EMPTY 미발화 →
     ★permissive★ 였다. 본 개정은 **선언 SSOT 에서 유도한 기대 roster 연접**을 추가한다.
  `TestNG8P2bExpectedLaneCount` 가 그 연접을 mutant 로 falsify 한다.

★본 테스트가 **검증하지 않는** 축 (정직 declare)★
  - self-write 표 **행 내용**의 정합(경로 실재·glob 의미론) — 미검증.
  - 선언 SSOT 2곳 + 디렉토리를 **한꺼번에 일관되게** 바꾼 경우 — 검출 불가(정당 변경과
    기계적 구별 불가). 이는 결함이 아니라 설계상 상한이다.
  - 실 repo 판정은 **본 파일의 검증 대상이 아니다** — mutant 왕복은 실 repo 상태에
    의존하지 않도록 전부 **합성 fixture**(tmp_path) 위에서 수행한다.
    (실측 2026-08-13: `plugins/codeforge-review/CLAUDE.md` 가 self-write 표 + sentinel
     을 보유해 실 repo 는 `PASS(declared_empty=codeforge-review)` 다. 종전 이 자리에
     적혀 있던 "표 부재 → INCONCLUSIVE" 서술은 실측과 불일치해 정정했다.)

★sentinel 승격 자격 (구현리뷰 iter2 F-CR2-002)★
  `EMPTY-WRITE-SET(synthesis-only)` 토큰은 피검사자 lane doc(**untrusted body**)의
  "∅ 를 주장한다" 는 **표식**일 뿐이고, GREEN 승격 권한은 검사자 측
  `_DECLARED_EMPTY_ALLOWLIST` 에 있다. `TestNG8SentinelAllowlist` 가 그 분리를
  falsify 한다 (allowlist 밖 lane 의 토큰 → RED `sentinel_not_allowlisted`).
"""

from __future__ import annotations

import io
import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

# sys.path 는 상위 conftest 에서 이미 scripts/lib 를 주입했으므로 직접 import 가능
from check_lane_overlap_predicate import (
    GATE_ID,
    evaluate_overlap_predicate,
    main,
)
from gate_verdict import EXIT_INCONCLUSIVE, EXIT_PASS, EXIT_RED

LANES = ("requirements", "design", "review", "develop", "test", "pmo")


# ---------------------------------------------------------------------------
# fixture helper — 합성 lane repo (작업 트리 무오염)
# ---------------------------------------------------------------------------

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


#: ★sentinel 리터럴은 모듈에서 import 하지 않는다★ — import 하면 토큰 값이 바뀔 때
#: fixture 가 따라 움직여 그 축이 tautology 가 된다. 기대 문자열은 테스트가 직접 든다
#: (`test_expected_roster_echoes_declared_ssot_paths` 가 SSOT 경로를 직접 드는 것과 동형).
SENTINEL_TOKEN = "EMPTY-WRITE-SET(synthesis-only)"
SENTINEL_ROW = "| `%s` | 없음 — 직접 write 공집합 |\n" % SENTINEL_TOKEN


def default_write_rows(lane: str) -> str:
    """baseline lane 의 self-write 표 데이터 행 2개."""
    return "| `docs/%s/a.md` | Agent1 |\n| `docs/%s/b.md` | Agent2 |\n" % (lane, lane)


def lane_doc(lane: str, rows: str) -> str:
    """lane `CLAUDE.md` 본문 형판 — baseline 과 mutant 가 **같은 형판**을 쓴다.

    (표 heading·헤더·구분선은 고정하고 데이터 행만 갈아끼운다 — mutant 마다 새 문서
    형판을 발명하면 "형판이 달라서 RED" 인지 "행 내용 때문에 RED" 인지 분리되지 않는다.)
    """
    return ("# CLAUDE.md (codeforge-%s)\n\n## Self-write 책임\n\n"
            "| Path | 책임 agent |\n|---|---|\n"
            "%s\n"
            "## 다음 섹션\n\n본문.\n" % (lane, rows))


def build_lane_repo(root: Path, lanes=None, roster_skill=None, roster_claude=None) -> Path:
    """6 lane 전건이 self-write 표를 보유한 baseline repo 를 만든다 (기본 = PASS)."""
    lanes = list(LANES if lanes is None else lanes)
    roster_skill = list(LANES if roster_skill is None else roster_skill)
    roster_claude = list(roster_skill if roster_claude is None else roster_claude)

    _write(root / "CLAUDE.md",
           "# fixture\n\n6 lane plugin: `codeforge-{%s}@mclayer`.\n"
           % ", ".join(roster_claude))
    _write(root / "skills" / "lane-self-write-boundary" / "SKILL.md",
           "# fixture skill\n\n... `Self-write 책임` 표 (codeforge-{%s}) 참조.\n"
           % ",".join(roster_skill))
    for lane in lanes:
        _write(root / "plugins" / ("codeforge-" + lane) / "CLAUDE.md",
               lane_doc(lane, default_write_rows(lane)))
    return root


def run_gate(root: Path):
    """게이트 CLI 를 in-process 로 호출해 (exit_code, payload) 를 돌려준다."""
    stdout = io.StringIO()
    with patch("sys.stdout", stdout):
        exit_code = main(["check_lane_overlap_predicate.py", "--repo-root", str(root)])
    payload = json.loads(stdout.getvalue().strip().splitlines()[-1])
    assert payload["gate_id"] == GATE_ID
    return exit_code, payload


@pytest.fixture
def lane_repo(tmp_path):
    """baseline lane repo — 이 fixture 위에서 mutant 를 주입하고 revert 한다."""
    return build_lane_repo(tmp_path / "repo")


# ===========================================================================
# ★RTM 명명 테스트★ — Story §8.0.2 문자열과 정확히 일치해야 한다
# ===========================================================================

def test_lane_overlap_predicate_c1_c2_c3(lane_repo):
    """AC-16 / NG-8 — §7.10 C1·C2·C3 술어 + RTM mutant(write_set 교집합 1건 → 불허).

    §7.10 정의:
      C1  read_set(W)  ∩ write_set(lane N, 미완료)            == ∅
      C2  read_set(W)  ⊆ snapshot(lane N 진입 시점 고정 SHA)
      C3  write_set(W) ∩ (하류 게이트가 이미 판정한 산출물)     == ∅

    3 절이 **각각 독립으로 load-bearing** 임을 절마다 mutant 1건으로 falsify 한다
    (한 절만 죽여도 `allowed` 가 False 로 뒤집혀야 한다 — 나머지 2절은 참으로 고정).
    이어서 RTM 이 지정한 mutant("write_set 교집합 1건 주입 → 불허")를 **게이트 실행면**
    에서도 왕복 실증한다(RED → revert → GREEN).
    """
    base = dict(
        w_read_set=["plugins/**", "scripts/**"],
        w_write_set=["docs/change-plans/new.md"],
        lane_write_set=["docs/stories/K.md §2", "docs/domain-knowledge/**"],
        snapshot_paths=["plugins/**", "scripts/**"],
        downstream_artifacts=["docs/stories/K.md §9"],
    )

    # --- 기준선: 3절 전부 참 → 착수 허용 (negative control) ------------------
    ok = evaluate_overlap_predicate(**base)
    assert ok["allowed"] is True, ok
    assert (ok["c1"], ok["c2"], ok["c3"]) == (True, True, True), ok

    # --- C1 mutant: read_set 이 lane 의 write_set 1건과 겹침 → 불허 ----------
    m_c1 = dict(base, lane_write_set=base["lane_write_set"] + ["plugins/**"])
    r1 = evaluate_overlap_predicate(**m_c1)
    assert r1["c1"] is False and r1["allowed"] is False, r1
    assert r1["c1_violations"] == ["plugins/**"], r1
    assert (r1["c2"], r1["c3"]) == (True, True), "C1 만 죽어야 한다 (절 독립성)"

    # --- C2 mutant: read_set 이 snapshot 고정점 밖 1건 포함 → 불허 -----------
    m_c2 = dict(base, w_read_set=base["w_read_set"] + ["archive/adr/**"])
    r2 = evaluate_overlap_predicate(**m_c2)
    assert r2["c2"] is False and r2["allowed"] is False, r2
    assert r2["c2_violations"] == ["archive/adr/**"], r2
    assert (r2["c1"], r2["c3"]) == (True, True), "C2 만 죽어야 한다 (절 독립성)"

    # --- C3 mutant: W 의 write_set 이 하류 판정 산출물 1건과 겹침 → 불허 -----
    m_c3 = dict(base, w_write_set=base["w_write_set"] + ["docs/stories/K.md §9"])
    r3 = evaluate_overlap_predicate(**m_c3)
    assert r3["c3"] is False and r3["allowed"] is False, r3
    assert r3["c3_violations"] == ["docs/stories/K.md §9"], r3
    assert (r3["c1"], r3["c2"]) == (True, True), "C3 만 죽어야 한다 (절 독립성)"

    # --- ★RTM mutant★ 게이트 실행면: write_set 교집합 1건 주입 → 불허 -------
    exit_green, payload_green = run_gate(lane_repo)
    assert exit_green == EXIT_PASS, payload_green
    assert payload_green["trace"]["lane_pairs_compared"] == 15  # C(6,2)

    victim = lane_repo / "plugins" / "codeforge-develop" / "CLAUDE.md"
    original = victim.read_text(encoding="utf-8")
    _write(victim, original.replace("docs/develop/a.md", "docs/design/a.md"))

    exit_red, payload_red = run_gate(lane_repo)
    assert exit_red == EXIT_RED, payload_red
    assert payload_red["reason"] == "lane_write_set_overlap", payload_red
    assert payload_red["trace"]["overlap_pair_count"] == 1, payload_red
    assert payload_red["identity_probe"]["overlapped_paths"] == ["docs/design/a.md"]

    # --- revert 왕복 (negative control — "항상 RED" 와 구별) ----------------
    _write(victim, original)
    exit_back, payload_back = run_gate(lane_repo)
    assert exit_back == EXIT_PASS, payload_back
    assert payload_back["trace"]["overlap_pair_count"] == 0, payload_back


# ===========================================================================
# ★P2-b★ — 기대 lane 수 연접 (설계리뷰 iter3 blocking 승계)
# ===========================================================================

class TestNG8P2bExpectedLaneCount:
    """추출 lane 이 **조용히 줄어드는** 형상을 기대 roster 연접으로 잡는다."""

    @pytest.mark.parametrize("victim", ["test", "design", "pmo"])
    def test_lane_silently_dropped_is_red(self, lane_repo, victim):
        """★P2-b 핵심★ 6 → 5 (1 lane 조용히 누락) → RED `lane_count_mismatch`.

        종전(관측치 단독) 형상에서는 남은 5 lane 이 각자 표를 갖고 있으므로
        `EXTRACTION_EMPTY` 가 **미발화**했다 = permissive silent-green.
        """
        assert run_gate(lane_repo)[0] == EXIT_PASS  # negative control

        lane_dir = lane_repo / "plugins" / ("codeforge-" + victim)
        shutil.rmtree(lane_dir)

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "lane_count_mismatch", payload
        assert payload["trace"]["expected_lane_count"] == 6, payload
        assert payload["trace"]["discovered_lane_count"] == 5, payload
        assert payload["identity_probe"]["missing_lanes"] == ["codeforge-" + victim]

        # revert 왕복
        build_lane_repo(lane_repo)
        assert run_gate(lane_repo)[0] == EXIT_PASS

    def test_equal_count_different_set_is_separately_red(self, lane_repo):
        """개수는 같고 **집합만 다른** swap → `lane_roster_mismatch` (명시 분기).

        "합이 우연히 안 맞아서 RED" 에 의존하지 않는다 — 개수 동일(6==6) 이어도
        집합이 다르면 별 reason 으로 RED 여야 한다.
        """
        (lane_repo / "plugins" / "codeforge-test").rename(
            lane_repo / "plugins" / "codeforge-bogus")

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "lane_roster_mismatch", payload
        assert payload["trace"]["expected_lane_count"] == 6
        assert payload["trace"]["discovered_lane_count"] == 6  # ★개수는 같다★
        assert payload["identity_probe"]["missing_lanes"] == ["codeforge-test"]
        assert payload["identity_probe"]["undeclared_lane_dirs"] == ["codeforge-bogus"]

    def test_expected_roster_is_not_derived_from_observation(self, lane_repo):
        """★tautology 회피★ — 기대치가 관측면(디렉토리 glob)에서 오지 않음을 증명.

        lane 디렉토리를 지웠는데 `expected_lane_count` 가 **따라 줄면** 기대치가
        관측면 파생(자기참조)이라는 뜻이고 P2-b 는 무효다.
        """
        shutil.rmtree(lane_repo / "plugins" / "codeforge-pmo")
        shutil.rmtree(lane_repo / "plugins" / "codeforge-test")
        _, payload = run_gate(lane_repo)
        assert payload["trace"]["expected_lane_count"] == 6, "기대치가 관측면 파생이면 안 된다"
        assert payload["trace"]["discovered_lane_count"] == 4, payload

    def test_expected_roster_echoes_declared_ssot_paths(self, lane_repo):
        """`identity_probe` 가 기대치를 **어디서** 읽었는지 echo 한다 ([154-AC-13])."""
        _, payload = run_gate(lane_repo)
        probe = payload["identity_probe"]
        assert probe["roster_ssot_paths"] == [
            "skills/lane-self-write-boundary/SKILL.md",
            "CLAUDE.md",
        ], probe
        assert probe["declared_roster"] == sorted("codeforge-" + n for n in LANES)


# ===========================================================================
# 추출 채널 생존 — 미선언 vs 추출만 0 (ADR-154:149 경계)
# ===========================================================================

class TestNG8ExtractionChannel:
    """`EXTRACTION_EMPTY`(fail-closed RED) 와 미선언(non-GREEN) 을 **분리** 한다."""

    def test_declared_but_zero_rows_is_extraction_empty_red(self, lane_repo):
        """표 heading 은 있는데 행이 0 → RED `extraction_empty` (설계리뷰 iter2 P1-B).

        ★틀린 동작★: write_set = ∅ 이므로 (C1)·(C3) 자동 참 → PASS (silent-green).
        ★올바른 동작★: 추출 채널 사망으로 분류 → exit 1.
        """
        victim = lane_repo / "plugins" / "codeforge-pmo" / "CLAUDE.md"
        _write(victim, "# CLAUDE.md\n\n## Self-write 책임\n\n(표 삭제됨)\n\n## 다음\n\n본문.\n")

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "extraction_empty", payload
        assert payload["identity_probe"]["extraction_empty_lanes"] == ["codeforge-pmo"]
        assert payload["trace"]["extraction_empty_lane_count"] == 1
        assert payload["trace"]["extracted_lane_count"] == 5

        build_lane_repo(lane_repo)
        assert run_gate(lane_repo)[0] == EXIT_PASS

    def test_heading_rename_is_undeclared_not_pass(self, lane_repo):
        """heading rename → 미선언 → non-GREEN `INCONCLUSIVE`(별 상태, PASS 아님).

        `extraction_empty`(RED) 와 **다른 reason** 이어야 한다 — 두 상태를 한 통에
        섞으면 `ADR-154:149` 가 가르라 한 경계가 사라진다.
        """
        victim = lane_repo / "plugins" / "codeforge-review" / "CLAUDE.md"
        original = victim.read_text(encoding="utf-8")
        _write(victim, original.replace("## Self-write 책임", "## 소유 경계 (rename)"))

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_INCONCLUSIVE, payload
        assert payload["reason"] == "write_set_undeclared", payload
        assert payload["reason"] != "extraction_empty"
        assert payload["identity_probe"]["undeclared_lanes"] == ["codeforge-review"]

        _write(victim, original)
        assert run_gate(lane_repo)[0] == EXIT_PASS

    def test_overlap_outranks_undeclared(self, lane_repo):
        """미선언 lane 이 있어도 **겹침이 있으면 RED** 가 우선한다 (판정 순서 고정)."""
        rev = lane_repo / "plugins" / "codeforge-review" / "CLAUDE.md"
        _write(rev, rev.read_text(encoding="utf-8").replace(
            "## Self-write 책임", "## 소유 경계 (rename)"))
        dev = lane_repo / "plugins" / "codeforge-develop" / "CLAUDE.md"
        _write(dev, dev.read_text(encoding="utf-8").replace(
            "docs/develop/a.md", "docs/design/a.md"))

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "lane_write_set_overlap", payload


# ===========================================================================
# ★sentinel 승격 자격★ — 토큰(피검사자 주장) ↔ allowlist(검사자 승격권) 분리
# ===========================================================================

class TestNG8SentinelAllowlist:
    """`EMPTY-WRITE-SET(synthesis-only)` 토큰의 **승격 권한 소재**를 falsify 한다.

    ★결함의 정체★ (구현리뷰 iter2 F-CR2-002): 문제는 "공집합에 GREEN 을 준 것" 이
    아니다 — `ADR-154` §결정 6 은 "target 0건 = 정당 honest no-op" 을 승인한다.
    위반된 것은 같은 절 **§7.3-crit**: "repo-local 파일 body = **untrusted**".
    즉 ★피검사자 본문(lane `CLAUDE.md`)의 토큰이 자기 verdict 를 GREEN 으로 승격★
    시킨 것이 결함이며, 수리는 토큰 폐기가 아니라 **marker(피검사자) ↔ grant(검사자)
    분리** 다. 토큰은 "∅ 를 주장한다" 는 표식으로 남고, 승격은 검사자 측
    `_DECLARED_EMPTY_ALLOWLIST` 등재 lane 에만 부여된다.

    ★본 클래스가 보증하지 **않는** 것★: allowlist 는 "봉인" 이 아니다 — 코드 diff
    권한자는 명단을 늘릴 수 있다. 보증 범위는 ★자기선언 승격 경로 제거(승격을 코드
    리뷰 표면으로 강제)★ 까지다.
    """

    def test_allowlisted_lane_declared_empty_is_pass(self, lane_repo):
        """allowlist 등재 lane 이 토큰으로 ∅ 를 선언 → PASS `declared_empty`.

        ADR-154 §결정 6 이 승인한 "정당 honest no-op" 방향이 살아 있어야 한다
        (봉합이 이 방향까지 죽이면 과교정이다).
        """
        assert run_gate(lane_repo)[0] == EXIT_PASS  # negative control

        victim = lane_repo / "plugins" / "codeforge-review" / "CLAUDE.md"
        _write(victim, lane_doc("review", SENTINEL_ROW))

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_PASS, payload
        assert payload["reason"] == "roster_matched_and_no_overlap", payload
        assert payload["identity_probe"]["declared_empty_lanes"] == ["codeforge-review"]
        assert payload["trace"]["declared_empty_lane_count"] == 1, payload
        # ∅ 도 겹침 판정에 **참여**한다 (trivially disjoint) — 추출 lane 에서 빠지지 않는다
        assert payload["trace"]["extracted_lane_count"] == 6, payload
        assert payload["trace"]["write_set_element_total"] == 10, payload  # 12 - 2

    def test_non_allowlisted_lane_sentinel_is_red(self, lane_repo):
        """★본 봉합의 판별력 증거★ — allowlist **밖** lane 의 토큰 → RED.

        형상 = "실 write 행을 전부 지우고 토큰을 넣는" 우회. 이것이 GREEN 이면
        어떤 lane 이든 자기 문서 한 줄로 겹침 검사에서 스스로를 제외할 수 있다.

        ★`codeforge-design` 은 하드코딩이다★ — 모듈의 allowlist 를 import 해서
        "밖에 있는 lane 을 골라 쓰면" allowlist 를 넓혀도 테스트가 따라 움직여
        이 축이 tautology 가 된다.
        """
        assert run_gate(lane_repo)[0] == EXIT_PASS  # negative control

        victim = lane_repo / "plugins" / "codeforge-design" / "CLAUDE.md"
        _write(victim, lane_doc("design", SENTINEL_ROW))

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "sentinel_not_allowlisted", payload
        assert payload["identity_probe"]["sentinel_not_allowlisted_lanes"] == \
            ["codeforge-design"], payload
        assert payload["trace"]["sentinel_not_allowlisted_lane_count"] == 1, payload
        # ★승격되지 않았음★ — declared_empty 로 새지 않는다
        assert "codeforge-design" not in \
            payload["identity_probe"].get("declared_empty_lanes", []), payload

        # revert 왕복 (negative control — "항상 RED" 와 구별)
        build_lane_repo(lane_repo)
        assert run_gate(lane_repo)[0] == EXIT_PASS

    def test_allowlisted_lane_sentinel_removed_is_extraction_empty(self, lane_repo):
        """allowlist 등재 lane 이라도 **토큰이 없으면** 0행은 RED `extraction_empty`.

        allowlist 등재가 "이 lane 은 무조건 GREEN" 이 되면 표 파손이 조용히 통과한다
        — 등재는 *토큰의 승격 자격*이지 *검사 면제*가 아니다.
        """
        victim = lane_repo / "plugins" / "codeforge-review" / "CLAUDE.md"
        _write(victim, lane_doc("review", SENTINEL_ROW))
        assert run_gate(lane_repo)[0] == EXIT_PASS  # negative control (승격 상태)

        _write(victim, lane_doc("review", ""))  # ★sentinel 행 삭제★ → 표는 있고 0행

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "extraction_empty", payload
        assert payload["reason"] != "sentinel_not_allowlisted"
        assert payload["identity_probe"]["extraction_empty_lanes"] == ["codeforge-review"]
        assert payload["trace"]["declared_empty_lane_count"] == 0, payload

    def test_sentinel_with_nonempty_write_set_is_contradiction(self, lane_repo):
        """실경로 + 토큰 동시 → RED `empty_sentinel_contradiction` (★분기 순서 oracle★).

        `codeforge-develop` 은 allowlist **밖**이므로, 4c(allowlist)를 4b(모순)보다
        앞에 두면 이 형상이 `sentinel_not_allowlisted` 로 새어 모순 분기가 **관측
        불가**가 된다. 판정 순서 4b → 4c → `extraction_empty` 를 고정한다.
        """
        victim = lane_repo / "plugins" / "codeforge-develop" / "CLAUDE.md"
        _write(victim, lane_doc("develop",
                                default_write_rows("develop") + SENTINEL_ROW))

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "empty_sentinel_contradiction", payload
        assert payload["reason"] != "sentinel_not_allowlisted", "4b 가 4c 보다 앞이어야 한다"
        assert payload["identity_probe"]["sentinel_contradiction_lanes"] == \
            ["codeforge-develop"], payload
        assert payload["trace"]["sentinel_contradiction_lane_count"] == 1, payload

        build_lane_repo(lane_repo)
        assert run_gate(lane_repo)[0] == EXIT_PASS


# ===========================================================================
# 선언 SSOT 축 — unknown-input fail-closed ([154-AC-4])
# ===========================================================================

class TestNG8RosterSsotFailClosed:
    """기대 roster 를 못 읽으면 **조용히 통과하지 않는다**."""

    def test_roster_sentence_renamed_is_red(self, lane_repo):
        """선언 문장 rename(브레이스 열거 소멸) → RED `roster_ssot_unparseable`."""
        skill = lane_repo / "skills" / "lane-self-write-boundary" / "SKILL.md"
        _write(skill, "# fixture skill\n\n각 lane CLAUDE.md 참조.\n")

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"].startswith("roster_ssot_unparseable:"), payload
        assert "SKILL.md" in payload["reason"]

        build_lane_repo(lane_repo)
        assert run_gate(lane_repo)[0] == EXIT_PASS

    def test_roster_source_missing_is_red(self, lane_repo):
        """선언 SSOT 파일 자체 부재 → RED `roster_ssot_unreadable`."""
        (lane_repo / "skills" / "lane-self-write-boundary" / "SKILL.md").unlink()
        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"].startswith("roster_ssot_unreadable:"), payload

    def test_roster_ambiguous_two_matches_is_red(self, lane_repo):
        """브레이스 열거가 2건 이상 → RED `roster_ssot_ambiguous` (정본 선택 불가).

        §8.0.9 frozen 앵커 `ANCHOR_AMBIGUOUS` 와 동형 — "첫 매치를 조용히 채택"
        하면 나중에 추가된 열거가 정본을 가려도 침묵한다.
        """
        skill = lane_repo / "skills" / "lane-self-write-boundary" / "SKILL.md"
        _write(skill, skill.read_text(encoding="utf-8")
               + "\n또 다른 언급: codeforge-{design,develop}.\n")

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"].startswith("roster_ssot_ambiguous:"), payload
        assert "matches=2" in payload["reason"], payload

    def test_two_declared_sources_must_agree(self, tmp_path):
        """SSOT 2곳 중 **한쪽에서만** lane 을 빼면 → RED `roster_ssot_divergence`."""
        root = build_lane_repo(
            tmp_path / "diverge",
            roster_skill=[n for n in LANES if n != "pmo"],
            roster_claude=list(LANES),
        )
        exit_code, payload = run_gate(root)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "roster_ssot_divergence", payload

        build_lane_repo(root)  # 양쪽 6 lane 으로 복원
        assert run_gate(root)[0] == EXIT_PASS

    def test_bad_lane_name_is_red(self, lane_repo):
        """lane 이름이 허용 문자 밖(경로 조각 등) → RED (조용한 무시 금지)."""
        _write(lane_repo / "CLAUDE.md",
               "# fixture\n\n6 lane plugin: `codeforge-{requirements, ../../etc}@mclayer`.\n")
        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"].startswith("roster_ssot_bad_lane_name:"), payload

    def test_unreadable_lane_doc_is_red(self, lane_repo):
        """lane `CLAUDE.md` 가 UTF-8 로 안 읽히면 → RED (행 조용히 제외 금지)."""
        victim = lane_repo / "plugins" / "codeforge-test" / "CLAUDE.md"
        victim.write_bytes(b"## Self-write \xff\xfe\x00 invalid utf-8")

        exit_code, payload = run_gate(lane_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "lane_claude_md_unreadable", payload
        assert payload["identity_probe"]["unreadable_lanes"] == ["codeforge-test"]


# ===========================================================================
# ADR-154 번들 4항목 — trace / probe 형상
# ===========================================================================

class TestNG8Adr154Bundle:
    def test_trace_emits_required_numerics(self, lane_repo):
        """[154-AC-5] trace = 대조 lane 쌍 수 · 추출 lane 수 · write_set 원소 수."""
        _, payload = run_gate(lane_repo)
        trace = payload["trace"]
        assert trace["lane_pairs_compared"] == 15
        assert trace["extracted_lane_count"] == 6
        assert trace["write_set_element_total"] == 12
        for key in ("lane_pairs_compared", "extracted_lane_count",
                    "write_set_element_total", "expected_lane_count",
                    "discovered_lane_count"):
            assert isinstance(trace[key], int), (key, trace)

    def test_identity_probe_echoes_resolved_targets(self, lane_repo):
        """[154-AC-13] probe = 실제로 무엇을 봤는지 (resolved-target echo)."""
        _, payload = run_gate(lane_repo)
        probe = payload["identity_probe"]
        assert len(probe["resolved_lane_docs"]) == 6
        assert all(p.endswith("CLAUDE.md") for p in probe["resolved_lane_docs"])
        assert probe["write_set_size_by_lane"] == {
            "codeforge-" + n: 2 for n in LANES
        }

    def test_inconclusive_is_never_exit_zero(self, lane_repo):
        """INCONCLUSIVE 는 절대 GREEN 이 아니다 ([154-AC-3])."""
        victim = lane_repo / "plugins" / "codeforge-review" / "CLAUDE.md"
        _write(victim, "# CLAUDE.md (codeforge-review)\n\n## 다른 섹션\n\n본문.\n")
        exit_code, payload = run_gate(lane_repo)
        assert payload["verdict"] == "INCONCLUSIVE"
        assert exit_code == EXIT_INCONCLUSIVE
        assert exit_code != EXIT_PASS


class TestNG8Hygiene:
    def test_uses_gate_verdict_helpers(self):
        """공유 헬퍼 재사용 (신규 verdict 체계 발명 금지)."""
        import check_lane_overlap_predicate as mod

        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "from gate_verdict import" in source
        assert "empty_target(" in source
        assert "unknown_input(" in source

    def test_expected_roster_is_not_hardcoded_in_module(self):
        """★모듈에 lane 이름 roster 가 박혀 있으면 안 된다★ (option A 이행 확인).

        `_ROSTER_SSOT_SOURCES` 는 **파일 경로** 목록이어야 하고, lane 이름 목록
        (`codeforge-design` 등)을 상수로 들고 있으면 자기참조 stale 이 된다.
        """
        import check_lane_overlap_predicate as mod

        assert all(s.endswith(".md") for s in mod._ROSTER_SSOT_SOURCES), \
            "roster SSOT 는 파일 경로여야 한다"
        for name in LANES:
            token = "codeforge-" + name
            for const_name in ("_ROSTER_SSOT_SOURCES",):
                assert not any(token in s for s in getattr(mod, const_name)), \
                    "%s 에 lane 이름이 하드코딩됐다: %s" % (const_name, token)


# ===========================================================================
# 실 repo 관측 — 판정에 의존하지 않고 **채널 해석 결과만** 확인
# ===========================================================================

def test_real_repo_channel_resolves_all_declared_lanes(repo_root):
    """실 repo 에서 선언 roster ↔ 디렉토리가 일치함을 실측한다 (verdict 무관).

    ★실 repo verdict 를 단정하지 않는다★ — 실 repo 판정은 lane doc 편집에 따라
    움직이는 값이라 여기에 박아두면 곧 stale 이 된다(종전 이 자리의
    "`codeforge-review` 표 부재 → INCONCLUSIVE" 서술이 실제로 stale 이 됐다 —
    실측 2026-08-13 은 `PASS(declared_empty=codeforge-review)`). 따라서 본 테스트는
    **verdict 가 아니라 trace 로** 채널 해석 결과만 확인한다.
    """
    _, payload = run_gate(Path(repo_root))
    trace = payload["trace"]
    assert trace["expected_lane_count"] == trace["discovered_lane_count"], payload
    assert trace["expected_lane_count"] >= 1
    assert payload["verdict"] != "PASS" or trace["extracted_lane_count"] == \
        trace["expected_lane_count"]
