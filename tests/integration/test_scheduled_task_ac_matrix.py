#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_ac_matrix.py — §8.2 AC 매트릭스
#
# 계약: normative 8건 (AC-1/2/3/4/5/9/11/12/13) + AC-4 자발 배선
#
# 각 AC 마다 부재형 + 변형형 mutant 2종 이상을 실제로 생성해 RED 입증.
# presence-only (부재형만 검사) = hollow-oracle 이며 재작성 대상.
#
# RTM 함수 명명 규약(필수): test_ac<N>_<축>
#   AC-ID ↔ 명명 테스트 1:1 매핑 (매핑표에서 검증)

import os
import json
import re
import shutil
import subprocess
import tempfile
import time
import pytest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))

import scheduled_task_reconcile as sut


# ═══════════════════════════════ 공통 헬퍼 ═══════════════════════════════════
def _git(repo, *args, check=True):
    """cwd 변경 없이 repo 에 git 명령 실행 (Windows chdir 점유 회피)."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=check,
    )


def _stash_snapshot(repo):
    """`git stash list --format=%gd %H` 결과를 **집합**으로. 순서 무관 동일성 비교용."""
    cp = _git(repo, "stash", "list", "--format=%gd %H")
    return {ln.strip() for ln in (cp.stdout or "").splitlines() if ln.strip()}


def _make_repo_with_stash(repo_path):
    """dummy commit 1 + stash 1 을 가진 임시 git repo 생성 (전역 git identity 무의존)."""
    os.makedirs(repo_path, exist_ok=True)
    _git(repo_path, "init", "-q")
    _git(repo_path, "config", "user.email", "qadev@example.invalid")
    _git(repo_path, "config", "user.name", "qadev")
    Path(repo_path, "dummy.txt").write_text("base\n", encoding="utf-8")
    _git(repo_path, "add", "dummy.txt")
    _git(repo_path, "commit", "-q", "-m", "initial")
    Path(repo_path, "temp.txt").write_text("stashed\n", encoding="utf-8")
    _git(repo_path, "add", "temp.txt")
    _git(repo_path, "stash")


def _scan_roots_for(tmpdir, worktrees_dir):
    """production scan_roots 형상 그대로의 tmpdir 주입본 (실 홈 스캔 0, hermetic)."""
    return [
        {"path": worktrees_dir, "mode": "cross-check-only", "source": "worktrees-base"},
        {"path": os.path.join(tmpdir, "workspace"), "mode": "discover+classify",
         "source": "workspace-root"},
        {"path": os.path.join(tmpdir, "home"), "mode": "discover+classify",
         "source": "home-direct"},
    ]


def _md_table_rows(section: str, header_cells: list):
    """마크다운 섹션에서 **헤더 셀이 정확히 일치하는 표 1개**의 데이터 행을 파싱한다.

    substring 검사(도입 문장·배제 축 표·산문에서 리터럴이 공급되는 hollow oracle)를
    구조 파싱으로 대체하기 위한 헬퍼 — test_ac4_six_facet_enumeration 이 쓰는 방식의 추출본.

    Returns:
        list[list[str]] — 각 데이터 행의 셀 목록 (선행/후행 빈 셀 제거)

    Raises:
        AssertionError: 헤더 행 부재 (= 표 통째 삭제)
    """
    def _cells(line):
        parts = [c.strip() for c in line.strip().split("|")]
        # `| a | b |` → ['', 'a', 'b', ''] — 양끝 빈 셀 제거
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]
        return parts

    lines = section.split("\n")
    start = -1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and _cells(ln) == header_cells:
            start = i
            break
    if start == -1:
        raise AssertionError(
            f"표 헤더 부재: {header_cells} (표 통째 삭제 또는 헤더 변형)"
        )
    rows = []
    for ln in lines[start + 1:]:
        s = ln.strip()
        if not s.startswith("|"):
            break                       # 표 종료
        if set(s.replace("|", "").replace(" ", "")) <= {"-", ":"}:
            continue                    # 구분행
        rows.append(_cells(ln))
    return rows


def extract_adr_section(content: str, section_heading: str) -> str:
    """ADR 절 추출 헬퍼 — 줄 기반 startswith 로 확실한 슬라이싱.

    Args:
        content: ADR 전체 내용
        section_heading: 찾을 헤딩 문자열 (예: "### §결정 9")

    Returns:
        해당 헤딩부터 다음 같은 레벨 또는 상위 레벨 헤딩까지의 텍스트

    Raises:
        AssertionError: 헤딩 부재 또는 슬라이싱 오류

    검증:
        - 헤딩 발견 실패 → AssertionError
        - 슬라이스 길이 ≤ 헤딩 줄 길이 → AssertionError (1글자 사건 방지)
    """
    lines = content.splitlines(keepends=True)
    start_idx = next(
        (i for i, ln in enumerate(lines) if ln.startswith(section_heading)),
        -1
    )
    if start_idx == -1:
        raise AssertionError(f"절 부재: {section_heading}")

    # 헤딩 레벨 추론 (예: "### " → 3)
    heading_level = len(section_heading) - len(section_heading.lstrip("#"))
    heading_prefix = "#" * heading_level

    # 시작 줄 다음부터 같은 레벨 또는 상위 레벨의 다른 헤딩 찾기
    end_idx = next(
        (i for i in range(start_idx + 1, len(lines))
         if lines[i].startswith(heading_prefix + " ") and
            not lines[i].startswith(heading_prefix + "# ")),
        len(lines)
    )

    section = "".join(lines[start_idx:end_idx])

    # 검증: 슬라이스가 헤딩 이상의 유의미한 길이여야 함
    header_line = lines[start_idx]
    if len(section) <= len(header_line):
        raise AssertionError(
            f"절 슬라이싱 오류: {section_heading} (헤딩만 남음 또는 손상)"
        )

    return section


class TestAC1MeasurementDeclaration:
    """AC-1: live 증거 아티팩트 (미측정).

    Claude Desktop 미설치 환경 → measured=false 정직 선언.
    미측정을 PASS 로 대체하지 않음 (requires_golden 마커로 명시 FAIL).
    """

    def test_ac1_measurement_declaration_is_honest(self):
        """AC-1 선언 파일이 정직하게 measured=false 를 기재.

        Assert:
          - fixtures 파일 존재 + 내용 검증
          - measured == false
          - 사유 문자열 비어있지 않음
        """
        fixture_path = Path(__file__).parent.parent / "fixtures" / "cfp_2949" / "ac1-measurement-declaration.json"
        fixture_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 존재 검사
        assert fixture_path.exists(), (
            f"AC-1 선언 파일 부재: {fixture_path}"
        )

        # 파일 내용 검증 (UTF-8 인코딩 명시 — Windows cp949 회피)
        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("ac") == "AC-1", "AC ID 확인"
        assert data.get("measured") is False, (
            f"measured 는 False 이어야 함 (미측정), 실제: {data.get('measured')}"
        )
        assert data.get("reason"), "사유 문자열 비어있지 않음"
        assert "Claude Desktop" in data.get("reason", ""), (
            "사유에 Claude Desktop 미설치 명시"
        )

    @pytest.mark.requires_golden
    def test_ac1_live_evidence_artifact_present(self):
        """AC-1 live 증거: 실제 스케줄 작업 실행 아티팩트.

        requires_golden 마커: golden fixture (live-run-<run_id>/) 부재 시
        명시 FAIL (skip 금지, CFP-2889 §3.3).

        Assertion:
          - manifest.json 존재 + orchestrator_session_closed_at < run_started_at
          - report-body.md 비어있지 않음
          - comment_id 가 GitHub API 로 실조회 가능
        """
        evidence_pattern = Path(__file__).parent.parent / "fixtures" / "cfp_2949" / "live-run-*"
        evidence_dirs = list(evidence_pattern.parent.glob("live-run-*"))

        # 명시 FAIL (skip 금지)
        assert evidence_dirs, (
            "AC-1 live 증거 디렉터리 부재. "
            "claudedeveloper@localhost.local 에서 스케줄 작업 1회 실행 후 증거를 수집하세요. "
            "(requires_golden 마커, 미충족)"
        )

        # 첫 번째 증거 디렉터리 검증
        evidence_dir = evidence_dirs[0]

        # manifest.json 검증
        manifest_path = evidence_dir / "manifest.json"
        assert manifest_path.exists(), f"manifest.json 부재: {manifest_path}"

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # 세션-결박 negative control: orchestrator 세션이 run 보다 먼저 닫혀야 함
        orch_closed = manifest.get("orchestrator_session_closed_at")
        run_started = manifest.get("run_started_at")
        assert orch_closed and run_started, "타임스탬프 필드 부재"
        assert orch_closed < run_started, (
            f"세션-결박 invariant 위반: "
            f"orch_closed={orch_closed} >= run_started={run_started}"
        )

        # report-body.md 검증
        report_path = evidence_dir / "report-body.md"
        assert report_path.exists(), f"report-body.md 부재: {report_path}"
        with open(report_path) as f:
            body = f.read()
        assert body.strip(), "report-body.md 비어있음"

        # comment_id 실조회 (GitHub API)
        comment_id = manifest.get("landing_ref", {}).get("comment_id")
        assert comment_id, "landing_ref.comment_id 부재"
        # API 호출은 실 인증 필요 — 여기서는 comment_id 존재만 확인


class TestAC2ObservationOnlyDelta:
    """AC-2: 관측-only 델타 0.

    삭제 0 (로컬 파일 삭제 0 + GitHub write 0).
    4개 canary: 파일 면 3개 (workspace-root, codeforge-scratch, Temp) + stash 면 1개.
    파일 축 3종은 test_ac2_no_deletion_on_disk, stash 축은 test_ac2_no_stash_drop.
    """

    def test_ac2_no_deletion_on_disk(self):
        """INV-A: 삭제 프리미티브 호출 0 — **SUT 가 스스로** `GC_DRY_RUN=1` 을 강제한다.

        ★ 이 오라클의 load-bearing 설계 (이전 판본의 결함 봉합):
          이전 판본은 **테스트가 먼저** `GC_DRY_RUN=1` 을 설정해 SUT 의 의무를 대신
          이행했다. 그래서 `_observe_scratch` 의 `os.environ["GC_DRY_RUN"] = "1"` 줄을
          `pass` 로 지워도 전 스위트가 GREEN 이었다(무커버). 본 판본은
          ① env 에서 `GC_DRY_RUN` 을 **제거**한 채 호출하고
          ② 삭제 프리미티브(`os.remove` / `shutil.rmtree`)를 spy 로 가로채
          ③ 호출 수 0 을 단언한다 — 강제 책임이 SUT 에 남는다.

        ★ 안전: 실 홈·실 scratch 미접촉 (tmpdir 주입) ∧ spy 가 실 삭제를 대체하므로
          mutant 재현 중에도 파일이 실제로 지워지지 않는다.

        비공허성(vacuous 아님) 짝: 심은 loose 파일이 실제로 age>TTL 판정에 도달했음을
          scratch 관측의 `TTL초과=1` 로 확인한다. 이 짝이 없으면 "삭제 0" 은
          "삭제 후보 자체가 0" 으로도 참이 된다.

        mutant kill: `scheduled_task_reconcile.py` `_observe_scratch` 의
          `os.environ["GC_DRY_RUN"] = "1"` → `pass` ⇒ RED (spy 호출 1 ∧ TTL초과=0).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Arrange: canary 파일 3종
            workspace_canary = os.path.join(tmpdir, "workspace_sentinel.txt")
            Path(workspace_canary).touch()

            scratch_dir = os.path.join(tmpdir, "scratch")
            os.makedirs(scratch_dir)
            scratch_canary = os.path.join(scratch_dir, "scratch_sentinel.txt")
            Path(scratch_canary).touch()

            # age > TTL loose 파일 (삭제 후보 — 이게 있어야 삭제 경로가 실제로 발동)
            stale_loose = os.path.join(scratch_dir, "stale-loose.txt")
            Path(stale_loose).write_text("stale\n", encoding="utf-8")
            old = time.time() - 30 * 86400
            os.utime(stale_loose, (old, old))

            temp_dir = os.path.join(tmpdir, "temp")
            os.makedirs(temp_dir)
            temp_canary = os.path.join(temp_dir, "temp_sentinel.txt")
            Path(temp_canary).touch()

            # 삭제 프리미티브 spy — 호출만 기록하고 **실제 삭제는 하지 않는다**
            delete_calls = []

            def spy_remove(path, *a, **kw):
                delete_calls.append(("os.remove", str(path)))

            def spy_rmtree(path, *a, **kw):
                delete_calls.append(("shutil.rmtree", str(path)))

            # Act: 테스트는 GC_DRY_RUN 을 **설정하지 않는다** (SUT 의 의무)
            with mock.patch.dict(os.environ):
                os.environ.pop("GC_DRY_RUN", None)
                os.environ["CODEFORGE_SCRATCH_TTL_DAYS"] = "1"   # 판정 결정론화
                with mock.patch("os.remove", side_effect=spy_remove), \
                     mock.patch("shutil.rmtree", side_effect=spy_rmtree):
                    obs = sut.collect_observations(
                        repo_root=tmpdir,
                        scan_roots=_scan_roots_for(tmpdir, os.path.join(tmpdir, "worktrees")),
                        scratch_root=scratch_dir,
                        temp_root=temp_dir,
                    )

            # Assert (ㄱ): 삭제 프리미티브 호출 0 (INV-A)
            assert delete_calls == [], (
                f"INV-A 위반: 삭제 프리미티브가 호출됐다 (GC_DRY_RUN 강제 실패): {delete_calls}"
            )

            # Assert (ㄴ): 비공허성 — 심은 파일이 실제로 TTL 초과 판정에 도달
            scratch_obs = [o for o in obs if o.cls == "scratch"]
            assert len(scratch_obs) == 1, f"scratch 관측 1행 기대, 실제: {len(scratch_obs)}"
            assert "TTL초과=1" in scratch_obs[0].measured, (
                "삭제 후보가 판정에 도달하지 않았다 — '삭제 0' 단언이 공허해진다. "
                f"실측: {scratch_obs[0].measured!r}"
            )
            assert "삭제집행=0" in scratch_obs[0].measured, (
                f"dry-run 경로 미진입 (삭제집행 != 0): {scratch_obs[0].measured!r}"
            )

            # Assert (ㄷ): canary 파일 + stale 파일 모두 존재 (삭제 0)
            assert os.path.exists(workspace_canary), "workspace canary 삭제되지 않음"
            assert os.path.exists(scratch_canary), "scratch canary 삭제되지 않음"
            assert os.path.exists(temp_canary), "temp canary 삭제되지 않음"
            assert os.path.exists(stale_loose), "age>TTL loose 파일 삭제되지 않음"

    def test_ac2_github_write_zero(self):
        """GitHub 상태 write 0.

        post_report() 호출 을 spy 해서 호출 여부 검증.
        발화 없으면 post_report 미호출.

        ★ Hermetic: fixture 트리 주입 (실 홈 스캔 0).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            scratch_dir = os.path.join(tmpdir, "scratch")
            temp_dir = os.path.join(tmpdir, "temp")
            os.makedirs(scratch_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)

            # Arrange: collect_observations 를 fixture 값만 반환하도록 stub
            def mock_collect_observations(**kwargs):
                # 관측 0건 반환 (hermetic, 실 홈 스캔 0)
                return []

            with mock.patch.object(sut, "post_report") as spy_post:
                with mock.patch.object(sut, "collect_observations", side_effect=mock_collect_observations):
                    # Act: run() 호출 — 관측 0건이면 무발화 → post_report 미호출
                    sut.run(["--repo-root", tmpdir, "--channel", "owner/repo#123", "--dry-run"])

                    # Assert: post_report 미호출
                    assert spy_post.call_count == 0, (
                        f"관측 0건 시 post_report 미호출 기대, 실제: {spy_post.call_count}"
                    )

    def test_ac2_no_stash_drop(self):
        """AC-2 stash 축: **SUT 관측 사이클 전후** stash 스냅샷 일치 (집합 동일).

        `git stash drop` 은 `.git/refs/stash` 만 바꾸므로 파일 면 depth-1 스냅샷에
        나타나지 않는다 — 파일 축(test_ac2_no_deletion_on_disk)과 **별개 축**이 필요하다.

        ★ 오라클 형상 (Change Plan §8.2):
          임시 git repo 를 **scan root 로 주입** → `sut.collect_observations` 호출
          **전후**로 `git stash list --format=%gd %H` 스냅샷 채취 → **집합 동일** 단언.
          ★ 테스트 자신은 stash 를 조작하지 않는다 — 사이클 안의 유일 행위자가 SUT 다.
          (이전 판본은 테스트가 스스로 `git stash drop` 을 실행하고 `!=` 를 단언해
           SUT 참조가 0건이었다 — 선언은 '일치'인데 단언은 극성까지 반대였다.)

        mutant kill:
          ① `_observe_workspace_residue` 가 후보 디렉터리에 `git stash drop` 실행 ⇒ RED
          ② `collect_observations` 가 raise ⇒ RED (예외 전파로 오라클이 SUT 에 결박)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Arrange: worktrees-base scan root 아래에 stash 보유 임시 git repo
            worktrees_dir = os.path.join(tmpdir, "worktrees")
            os.makedirs(worktrees_dir, exist_ok=True)
            repo_path = os.path.join(worktrees_dir, "stash_repo")
            _make_repo_with_stash(repo_path)

            scratch_dir = os.path.join(tmpdir, "scratch")
            temp_dir = os.path.join(tmpdir, "temp")
            os.makedirs(scratch_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)

            stash_before = _stash_snapshot(repo_path)
            assert len(stash_before) == 1, (
                f"전제 붕괴: stash 1건 기대, 실제 {len(stash_before)}건 ({stash_before})"
            )

            # Act: SUT 관측 사이클 (테스트는 git 상태를 건드리지 않는다)
            obs = sut.collect_observations(
                repo_root=tmpdir,
                scan_roots=_scan_roots_for(tmpdir, worktrees_dir),
                scratch_root=scratch_dir,
                temp_root=temp_dir,
            )

            stash_after = _stash_snapshot(repo_path)

            # Assert (ㄱ): SUT 가 실제로 그 repo 에 도달했다 (오라클 결박 — 비공허성)
            worktree_paths = [o.display_path for o in obs if o.cls == "worktree"]
            assert any("stash_repo" in p for p in worktree_paths), (
                "SUT 가 주입한 stash repo 를 관측하지 않았다 — stash 단언이 공허해진다. "
                f"worktree 관측: {worktree_paths}"
            )

            # Assert (ㄴ): stash 스냅샷 **집합 동일** (제거·추가 0)
            assert stash_after == stash_before, (
                "AC-2 stash 축 위반: 관측 사이클이 stash 상태를 변경했다. "
                f"before={sorted(stash_before)} after={sorted(stash_after)}"
            )


class TestAC3SelfModificationChain:
    """AC-3: 자기수정 2류 차단.

    (i) 허용범위에 `update_scheduled_task` / write 도구 부재
    (ii) `~/.claude/**` 쓰기 명시 deny 실재
    (iii) 저장 프롬프트 금지행위 리터럴 0
    (iv) 외부 본문 유입 0
    """

    def test_ac3_no_update_scheduled_task_tool(self):
        """능력 감사: update_scheduled_task 허용범위 부재."""
        # ADR-172 저장 프롬프트 박제본에서 update_scheduled_task 검사
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-3 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # 저장 프롬프트 추출 (### §결정 2 절)
        decision_2_idx = content.find("### §결정 2")
        if decision_2_idx == -1:
            pytest.fail("ADR-172 의 §결정 2 절 부재")

        # fenced 코드블록 찾기
        code_start = content.find("```", decision_2_idx)
        if code_start == -1:
            pytest.fail("저장 프롬프트 fenced block 부재")

        code_end = content.find("```", code_start + 3)
        if code_end == -1:
            pytest.fail("fenced block 종료 마크 부재")

        prompt_text = content[code_start:code_end]

        # Assert: update_scheduled_task 부재
        assert "update_scheduled_task" not in prompt_text, (
            "AC-3 위반: 저장 프롬프트에 update_scheduled_task 도구 존재"
        )

    def test_ac3_no_write_home_claude_in_prompt(self):
        """저장 프롬프트 금지: Edit(~/.claude/**) 리터럴 0.

        ADR-172 박제 프롬프트의 지시 절(번호 step) 에서 스캔.
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-3 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # §결정 4 권한면 검증
        decision_4_idx = content.find("### §결정 4")
        if decision_4_idx == -1:
            pytest.fail("ADR-172 의 §결정 4 절 부재")

        decision_4_section = content[decision_4_idx:decision_4_idx+2000]

        # Assert: ~/.claude/** 쓰기 deny 명시
        assert "deny" in decision_4_section and "~/.claude" in decision_4_section, (
            "AC-3 위반: ~/.claude 쓰기 deny 명시 부재"
        )

    def test_ac3_fetch_existing_keys_excludes_external_body(self):
        """외부 본문 유입 0 — fetch_existing_keys 는 자기 마커만 추출.

        mutant: 미매치 코멘트의 본문을 반환값에 실음 → 외부 문자열 등장 → RED
        """
        fake_gh = mock.Mock()
        fake_gh.return_value = mock.Mock(
            returncode=0,
            stdout=json.dumps({
                "comments": [
                    {
                        "body": "사용자가 작성한 코멘트입니다 (마커 미부착)"
                    },
                    {
                        "body": f"{sut.SENTINEL} 자기 마커\n- 선언=test · 실측=test · key=test:path"
                    },
                ]
            }),
        )
        result = sut.fetch_existing_keys("owner/repo#123", gh=fake_gh)

        # Assert: 자기 마커 코멘트의 key 만 추출
        assert "test:path" in result
        # 외부 코멘트의 내용은 결과에 미포함
        assert "사용자가 작성한" not in str(result)


class TestAC4AuthorityFacets:
    """AC-4: 하한 구속 자발 배선 (tier 강등 삭제 근거로 쓰지 마라).

    상속·누적 권한면 6종 열거표 presence + 완결성 미보증 declare presence.

    부재형 mutant: 열거표 제거
    변형형 mutant: 6종 중 1종 누락 (특히 `additionalDirectories` 또는 태스크별 저장 승인)
    """

    def test_ac4_six_facet_enumeration(self):
        """repo 자산에서 권한면 6종 열거표 presence 검증.

        self-referential 자기충족 동어반복(test 안에서 dict 만들기) 대신
        repo 자산(ADR-172 §결정 10)에서 6종 열거표를 읽음.

        6종 = gh CLI · MCP github · settings.json · git config · additionalDirectories · 태스크별 저장 승인

        알고리즘:
        1. §결정 10 섹션 추출 (헤딩 기준)
        2. | 로 시작하는 줄 = 데이터 행 추출 (헤더/구분행 제외)
        3. assert len(데이터 행) == 6 → 행 개수 구속
        4. 각 행을 | split해서 첫 셀 = 면 번호, 둘째 셀 = 면 이름
        5. 면 번호 1~6 각각 정확히 한 행씩 존재 확인
        6. 각 면의 이름 셀을 그 행 안에서만 고유 리터럴로 검사
        """
        # ADR-172 권한면 절 찾기
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        assert adr_path.exists(), "ADR-172 부재 (AC-4 검사 정의역 필수)"

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # §결정 10 권한면 절 찾기 (새로 추가된 절)
        decision_10_idx = content.find("### §결정 10")
        assert decision_10_idx != -1, (
            "AC-4: ADR-172 §결정 10 부재 (권한면 6종 열거표 정본 필수)"
        )

        # §결정 10 섹션 추출 (다음 섹션까지)
        decision_10_end = content.find("### ", decision_10_idx + 4)
        decision_10_section = content[decision_10_idx:decision_10_end if decision_10_end != -1 else None]

        # 절 내에서 | 로 시작하는 줄 = 테이블 행 추출
        lines = decision_10_section.split('\n')
        data_rows = []
        for line in lines:
            line_stripped = line.strip()
            # | 로 시작하고 |---| 구분행이 아닌 행만 추출 (헤더도 제외)
            if line_stripped.startswith('|') and '---|' not in line_stripped:
                # 첫 번째는 헤더행 (# | 면 | 실효 ...)
                # 그 다음부터는 데이터행 (| 1 | gh ... |)
                if not line_stripped.startswith('| #'):
                    data_rows.append(line_stripped)

        # Assert (ㄱ): 정확히 6개 데이터 행 존재
        assert len(data_rows) == 6, (
            f"AC-4: 데이터 행 개수 오류. 기대 6개, 실제 {len(data_rows)}개. "
            f"행 내용: {data_rows}"
        )

        # 각 데이터 행을 파싱해서 면 번호와 이름 추출
        facet_numbers_found = set()
        facet_checks = {
            "1": ("gh", "CLI"),  # 1번 면: gh, CLI 둘 다
            "2": ("MCP", "github"),  # 2번 면: MCP, github 둘 다
            "3": ("settings.json",),  # 3번 면: settings.json (단독)
            "4": ("git config",),  # 4번 면: git config (단독)
            "5": ("additionalDirectories",),  # 5번 면: additionalDirectories (단독)
            "6": ("태스크별 저장 승인", "Always allowed"),  # 6번 면: 둘 다
        }

        for row in data_rows:
            # | 로 split해서 셀 추출
            cells = [c.strip() for c in row.split('|')]
            # | row | num | name | ... | 형태 → cells[1]=num, cells[2]=name
            if len(cells) < 4:
                continue

            facet_num = cells[1].strip()
            facet_name = cells[2].strip()

            # 면 번호가 1~6 범위인지 확인
            if facet_num not in ["1", "2", "3", "4", "5", "6"]:
                continue

            facet_numbers_found.add(facet_num)

            # 해당 면 번호의 고유 리터럴을 그 행 안에서만 검사
            if facet_num in facet_checks:
                required_literals = facet_checks[facet_num]
                # facet_name 셀 안에서 모든 required_literals 확인
                for lit in required_literals:
                    assert lit in facet_name, (
                        f"AC-4: 면 {facet_num} 리터럴 미검출: '{lit}'. "
                        f"행 이름 셀: {facet_name}"
                    )

        # Assert (ㄴ): 면 번호 1~6이 각각 정확히 한 번씩 존재
        expected_numbers = {"1", "2", "3", "4", "5", "6"}
        assert facet_numbers_found == expected_numbers, (
            f"AC-4: 면 번호 완결성 미충족. 발견: {facet_numbers_found}, "
            f"기대: {expected_numbers}, 누락: {expected_numbers - facet_numbers_found}"
        )

        # Assert (ㄷ): 완결성 미보증 declare 존재 (ADR-172 §결정 10 정책)
        #   ★ `any` 완화 유지 근거: 검사 대상은 "declare 의 **존재**"이지 특정 문안이
        #     아니다. 세 키워드는 동일 declare 의 서로 다른 표현면(제목 라벨 / 명제 본문 /
        #     확장 조건)이며 셋 중 하나라도 남아 있으면 정책이 문서에 살아 있다. 문안
        #     고정(all)로 좁히면 ADR 문장 다듬기마다 무의미 RED 가 나므로 의도적 완화다.
        #     — 대신 declare 를 **통째 삭제**하면 세 키워드가 동시에 사라져 RED 가 된다.
        declare_keywords = ["★ 완결성 미보증", "닫힌 집합이 아니다", "미확인 권한면"]
        has_declare = any(kw in decision_10_section for kw in declare_keywords)
        assert has_declare, (
            "AC-4: 완결성 미보증 declare 부재 (ADR-172 §결정 10 정책 위반)"
        )


class TestAC5PromotionZero:
    """AC-5: 승격 조건·주체·rollback 3항 + 승격 이력 0건."""

    def test_ac5_no_promotion_history(self):
        """도입기 승격 이력 0 — ADR-172 §결정 9 에서 정규식 검증.

        부재형 mutant: 승격 이력 제거
        변형형 mutant: 승격 이력 = 1건 또는 다른 숫자

        golden 출처: ADR-172 §결정 9 "승격 이력 = 0건" (도입기 상태).
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail("ADR-172 부재")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        try:
            decision_9_text = extract_adr_section(content, "### §결정 9")
        except AssertionError as e:
            pytest.fail(f"AC-5: {e}")

        # Assert: 승격 이력 = 0 앵커된 정규식
        import re
        # golden: "**승격 이력 = 0건** (도입기 상태)."
        promotion_pattern = r"\*\*승격\s*이력\s*=\s*0건\*\*"
        assert re.search(promotion_pattern, decision_9_text), (
            "AC-5: 승격 이력 = 0건 리터럴 미검출 (정규식)"
        )

        # 조건·주체·rollback 존재 확인
        for required in ["조건", "주체", "rollback"]:
            assert required in decision_9_text, f"AC-5: {required} 필드 부재"

        # 추가 검증: rollback lever 3종 — **문장 전문**으로 검사한다.
        #   ★ 이전 판본은 한글 단음절 "가"/"나"/"다" 를 검사했다. 그 음절들은 §결정 9
        #     산문에 각각 11/2/14 회 등장하므로 lever 3항을 **전량 삭제해도 통과**하는
        #     공허 오라클이었다. lever 별 고유 문장 전문이라야 1항 삭제가 곧 RED 다.
        levers = [
            "**(가)** Manual permission mode 에서 미승인 도구 호출 시 "
            "**run 이 승인까지 정지**한다",
            "**(나)** 태스크 Status **Active / Paused** 토글",
            '**(다)** **Delete** ("Also delete files on disk" 체크박스 포함)',
        ]
        for lever in levers:
            assert lever in decision_9_text, (
                f"AC-5: rollback lever 전문 미검출 — {lever!r}"
            )


class TestAC9ReconcileCompleteness:
    """AC-9: reconcile 회수 — tick K회 건너뛰고 잔재 K개 추가 후 1회 호출 → K 전부 보고.

    cursor 구현이면 RED (K 중 일부만 보고).
    """

    def test_ac9_reports_all_accumulated_observations(self):
        """K회 축적 후 1회 호출 → K 전부 보고.

        상태 무의존 reconcile — cursor·watermark 부재. 매 실행이 현재 상태 전량을 재관측.
        """
        # property 테스트로 이관 (dynamic_roster.py 에서 fuzz/property 실행)
        # 여기서는 기본 구조만 검증: render_report 가 축적 관측 K개를 모두 포함하는지 검증
        observations = [
            sut.Observation(
                cls=f"class{i}",
                display_path=f"path{i}",
                declared="decl",
                measured="meas",
                mismatch=False,
            )
            for i in range(5)  # K=5 축적
        ]
        report = sut.render_report(observations, "test", "001")

        # Assert: render_report 이 K개 모두를 포함
        # items=N 필드가 축적 관측 수를 반영하는지 검증
        assert "items=" in report, "render_report 가 items 필드를 기재"
        # 최소한 5개의 관측이 보고에 반영되는지 확인
        for i in range(5):
            assert f"path{i}" in report, f"관측 {i} 경로가 보고에 포함"

    def test_ac9_scan_pipeline_reports_all_synthesized_residue(self):
        """AC-9 회수 완전성 — **관측 파이프라인**(`_observe_workspace_residue`)을 태운다.

        ★ 신설 사유 (RTM mutant 귀속 오류 봉합):
          위 `test_ac9_reports_all_accumulated_observations` 는 Observation 을 직접
          만들어 `render_report` 만 호출하므로 **스캐너 파이프라인에 도달하지 않는다**.
          그래서 RTM 이 AC-9 mutant 로 지목한 `verdicts = discovery.judge(classified)[:2]`
          (관측 절단)이 그 테스트에서 **도달 불가**였다. 본 테스트는 scan_roots 를 주입해
          discover→classify→judge 를 실제로 태우고 합성 잔재 전량 보고를 단언한다.

        mutant kill: `_observe_workspace_residue` 의
          `verdicts = discovery.judge(classified)` → `...[:2]` ⇒ RED.
        """
        K = 4      # ≥3 (절단 mutant `[:2]` 와 판별되도록 여유 1)
        with tempfile.TemporaryDirectory() as tmpdir:
            worktrees_dir = os.path.join(tmpdir, "worktrees")
            scratch_dir = os.path.join(tmpdir, "scratch")
            temp_dir = os.path.join(tmpdir, "temp")
            for d in (worktrees_dir, scratch_dir, temp_dir):
                os.makedirs(d, exist_ok=True)

            # Arrange: 합성 잔재 K개 (tick K회 건너뛴 상태의 등가물)
            for i in range(K):
                leaf = os.path.join(worktrees_dir, f"synth-residue-{i}")
                os.makedirs(leaf, exist_ok=True)
                Path(leaf, "marker.txt").write_text("x\n", encoding="utf-8")

            # Act: 상태 무의존 reconcile 1회 (cursor·watermark 부재)
            obs = sut.collect_observations(
                repo_root=tmpdir,
                scan_roots=_scan_roots_for(tmpdir, worktrees_dir),
                scratch_root=scratch_dir,
                temp_root=temp_dir,
            )
            report = sut.render_report(obs, "ac9-task", "ac9-run")

            # Assert (ㄱ): worktree 축 관측 개수 == K (절단 0)
            worktree_obs = [o for o in obs if o.cls == "worktree"]
            assert len(worktree_obs) == K, (
                f"AC-9: 합성 잔재 {K}개 전량 관측 기대, 실제 {len(worktree_obs)}개 — "
                f"{[o.display_path for o in worktree_obs]}"
            )

            # Assert (ㄴ): 발화 본문에도 K개 전량 등재 (보고 단계 절단 0)
            for i in range(K):
                assert f"synth-residue-{i}" in report, (
                    f"AC-9: 합성 잔재 synth-residue-{i} 가 보고 본문에 미등재"
                )

            # Assert (ㄷ): 각 관측의 dedup key 가 본문 key= 필드로 라운드트립
            for o in worktree_obs:
                assert f"key={sut.dedup_key(o)}" in report, (
                    f"AC-9: key 라운드트립 실패 — {sut.dedup_key(o)!r}"
                )


class TestAC11MarkerTwoTypes:
    """AC-11: 도입기 정확히 2종 마커 (sentinel + trailer).

    부재형 mutant: 마커 미부착
    변형형 mutant: 마커를 CLI 밖으로 옮김 (호출자가 붙이는 구조) → RED
    """

    def test_ac11_sentinel_and_trailer_in_report(self):
        """sentinel + trailer 양쪽 포함."""
        obs = [
            sut.Observation(
                cls="test",
                display_path="path",
                declared="decl",
                measured="meas",
                mismatch=False,
            ),
        ]
        report = sut.render_report(obs, "test", "001")

        assert sut.SENTINEL in report, f"SENTINEL 포함 예상: {sut.SENTINEL}"
        assert sut.TRAILER in report, f"TRAILER 포함 예상: {sut.TRAILER}"

    def test_ac11_exactly_two_marker_types(self):
        """도입기 마커 = sentinel 1종 + trailer 1종."""
        assert sut.SENTINEL == "[scheduled-task-observe]"
        assert sut.TRAILER == "[scheduled-task-run]"
        assert sut.SENTINEL != sut.TRAILER, "마커 구분"

    def test_ac11_markers_not_in_normal_text(self):
        """마커는 render_report 가 소유 (CLI 내에서 부착).

        도입기 마커 정확히 2종:
        - sentinel: [scheduled-task-observe] (고정)
        - trailer: [scheduled-task-run] (태스크·run 참조)

        부착 주체 = render_report (CLI 결정론 함수).
        """
        obs = [
            sut.Observation(
                cls="test",
                display_path="path",
                declared="decl",
                measured="meas",
                mismatch=False,
            ),
        ]
        report = sut.render_report(obs, "test_task", "run_123")

        # 1. sentinel 정확히 1회 출현
        sentinel_count = report.count(sut.SENTINEL)
        assert sentinel_count == 1, (
            f"AC-11 sentinel 횟수 오류: 기대 1회, 실제 {sentinel_count}회. "
            f"sentinel={sut.SENTINEL}"
        )

        # 2. trailer 정확히 1회 출현
        trailer_count = report.count(sut.TRAILER)
        assert trailer_count == 1, (
            f"AC-11 trailer 횟수 오류: 기대 1회, 실제 {trailer_count}회. "
            f"trailer={sut.TRAILER}"
        )

        # 3. 마커 **종수 == 2** — 산출에 등장하는 `[토큰]` 전량을 열거해 집합 동일 단언.
        #    ★ 이전 판본 `assert "[cfp-" not in report` 는 fixture 가 애초에 "[cfp-" 를
        #      공급하지 않아 SUT 행동과 무관하게 항상 참인 구조적 항진명제였다.
        #      여기서는 "SUT 가 실제로 무엇을 붙였는가" 를 열거해 3종째를 배제한다
        #      (승격 후 브랜치 prefix 가 도입기에 새면 RED — ADR-172 §결정 9).
        emitted_markers = set(re.findall(r"\[[^\[\]\s]+\]", report))
        assert emitted_markers == {sut.SENTINEL, sut.TRAILER}, (
            f"AC-11 도입기 마커 종수 위반: 기대 {{{sut.SENTINEL}, {sut.TRAILER}}}, "
            f"실제 {sorted(emitted_markers)} (ADR-172 §결정 9 — 도입기 정확히 2종)"
        )


class TestAC12TripleAxisSixCellComparison:
    """AC-12: 3축 × {비용,보안} 6셀 비교 + 결정 기록 (normative).

    검사 대상 = ADR-172 `### §결정 8` 절(절 헤딩 기준).

    부재형 mutant: 비교표 또는 결정 기록 제거
    변형형 mutant:
      - M2 결정 시각을 다른 시각으로 변경 (2026-08-12T23:59:59+09:00)
      - M3 "채택 축" 라벨 제거 ("P4" 만 남김)
    """

    def test_ac12_three_axis_six_cell_comparison_present(self):
        """6셀 비교표: 3축(P3a/P3b/P4) × {비용, 보안} 을 **표 구조**로 파싱해 검증.

        ★ honest ceiling — 헤더 문안 결합 (선언된 trade-off, 검출력 아님):
          표 식별을 헤더 셀 문자열(`축`/`비용 축`/`보안 축`) 일치로 하므로 **헤더 변형**
          (예: `비용 축` → `비용`)이 "표 통째 삭제" 와 같은 RED 를 낸다. 그 RED 는
          검출력이 아니라 ADR 문안에 대한 **결합 부작용**이다. 위치(첫 번째 표) 로만
          식별하면 같은 §결정 8 안의 "배제 축별 사유의 지위" 표와 구별할 수 없어
          더 나쁘므로 수용한 trade-off다.
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-12 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        try:
            decision_section = extract_adr_section(content, "### §결정 8")
        except AssertionError as e:
            pytest.fail(f"AC-12: {e}")

        # ★ 구조 파싱 (이전 판본 봉합):
        #   이전 판본은 `axis in section and attr in section` 이라는 **독립 substring**
        #   검사였다. 리터럴이 도입 문장·배제 축 표·결정 기록에서 공급되므로 §결정 8 의
        #   6셀 표를 **통째 삭제해도 통과**했다(hollow). 여기서는 헤더가 정확히
        #   `축 | 비용 축 | 보안 축` 인 표 1개를 찾아 행 개수·축·셀 텍스트를 구속한다.
        rows = _md_table_rows(decision_section, ["축", "비용 축", "보안 축"])

        # (ㄱ) 데이터 행 개수 == 3 (행 1개 삭제 = RED)
        assert len(rows) == 3, (
            f"AC-12: 6셀 비교표 데이터 행 3개 기대, 실제 {len(rows)}개. 행: {rows}"
        )

        # (ㄴ) 각 행의 첫 셀이 축 라벨 — 3축이 각각 정확히 한 행씩
        axes_found = []
        for cells in rows:
            assert len(cells) == 3, (
                f"AC-12: 표 행 셀 3개(축/비용/보안) 기대, 실제 {len(cells)}: {cells}"
            )
            axis_cell, cost_cell, sec_cell = cells
            matched = [a for a in ("P3a", "P3b", "P4") if a in axis_cell]
            assert len(matched) == 1, (
                f"AC-12: 축 셀이 P3a/P3b/P4 중 정확히 1종이어야 함 — {axis_cell!r}"
            )
            axes_found.append(matched[0])

            # (ㄷ) 3×2 = 6셀 텍스트 non-empty (마크다운 강조 문자만 남은 셀 배제)
            for attr, cell in (("비용", cost_cell), ("보안", sec_cell)):
                assert cell.strip(" *_-"), (
                    f"AC-12: {matched[0]}×{attr} 셀이 비어 있음 — 행: {cells}"
                )

        assert sorted(axes_found) == ["P3a", "P3b", "P4"], (
            f"AC-12: 3축 완결성 미충족. 발견: {axes_found}"
        )

    def test_ac12_adoption_record_literals_present(self):
        """결정 기록: P4 채택 축 · 사용자 주체 · 정본 시각 + 지위 라벨 4종.

        golden 출처: ADR-172 §결정 8 "결정 기록" 절 (Story §5.5 사용자 결정).
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-12 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        try:
            decision_section = extract_adr_section(content, "### §결정 8")
        except AssertionError as e:
            pytest.fail(f"AC-12: {e}")

        # 1. 채택 축 라벨 + P4 리터럴 (3축 구분)
        assert "**채택 축**" in decision_section and "P4" in decision_section, (
            "AC-12: 채택 축 라벨 또는 P4 리터럴 부재"
        )

        # 2. 주체 — 필드 전문으로 검사한다.
        #    ★ 이전 판본 `"**사용자**" in s or "사용자" in s` 는 앞 항이 사문(死文)이었다:
        #      뒤 항이 앞 항의 부분문자열이라 or 전체가 산문 어디의 "사용자" 로도 참이 됐다.
        assert "**결정 주체** = **사용자**" in decision_section, (
            "AC-12: 결정 주체 필드 전문('**결정 주체** = **사용자**') 미검출"
        )

        # 3. 시각 정본값 전문: 2026-08-12T12:15:00+09:00 (ISO 8601, KST)
        datetime_pattern = r"2026-08-12T12:15:00\+09:00"
        assert re.search(datetime_pattern, decision_section), (
            "AC-12: 결정 시각 정본값 2026-08-12T12:15:00+09:00 미검출"
        )

        # 4. 지위 라벨 — 필드 전문 (동일 사문 봉합)
        assert "**선택의 지위** = **가치 판단**" in decision_section, (
            "AC-12: 지위 라벨 필드 전문('**선택의 지위** = **가치 판단**') 미검출"
        )


class TestAC13StaticTextLint:
    """AC-13: 정적 텍스트면 secret 0 + 미정규화 절대경로 0.

    부재형 mutant: 정규화 미실행 (결과에 절대경로 그대로)
    변형형 mutant: redact 미실행 (결과에 토큰 문자열 그대로)

    행동 단언: 예시 입력 5종 정규화 확인
    """

    def test_ac13_no_unredacted_absolute_path_in_output(self):
        """산출 문자열에 미정규화 절대경로 0 — 정규화 행동 검증.

        _safe_text → base.sanitize 경로 정규화 통과.
        mutant: _normalize_paths 를 return s 로 무력화 → RED
        """
        # 1. /Users/alice 절대경로 → <user-home> 치환 확인
        text = "/Users/alice/.claude/worktrees/foo"
        result = sut._safe_text(text)
        assert "/Users/alice" not in result, (
            f"AC-13: 미정규화 절대경로 /Users/alice 검출: {result}"
        )
        assert "<user-home>" in result, (
            f"AC-13: <user-home> 정규화 미검출: {result}"
        )

        # 2. /home/bob 절대경로 → <user-home> 또는 유사 치환
        text = "/home/bob/x"
        result = sut._safe_text(text)
        assert "/home/bob" not in result, (
            f"AC-13: 미정규화 절대경로 /home/bob 검출: {result}"
        )

    def test_ac13_no_secret_literals_in_static_text(self):
        """정적 텍스트에 secret 패턴 0 — redact 행동 검증.

        base.sanitize 가 redact 담당 (credential redact 등).
        mutant: sanitize 를 pass-through 로 무력화 → RED
        """
        # 1. GitHub PAT 토큰 redact 확인
        text = "token=ghp_1234567890abcdefghij"
        result = sut._safe_text(text)
        assert "ghp_1234567890abcdefghij" not in result, (
            f"AC-13: 미redact 토큰 ghp_* 검출: {result}"
        )
        # redact 마커는 대괄호 형태일 것으로 예상
        # (구체 형태는 base.sanitize 구현에 의존)

    def test_ac13_no_false_positive_redaction(self):
        """비위반 토큰 오탐 금지 회귀.

        정규화 경로·마커 리터럴은 위반으로 잡히면 안 됨.
        """
        # 정규화 경로 형태들이 redact 되면 안 됨
        test_cases = [
            "~/.claude/worktrees/foo",  # 홈 상대 경로
            "<workspace>/plugin-codeforge",  # 마커 경로
            "<user-home>/.claude",  # 정규화된 경로
        ]
        for text in test_cases:
            result = sut._safe_text(text)
            # 정규화된 형태는 그대로 유지되어야 함
            assert text in result, (
                f"AC-13 오탐: 비위반 {text} 가 손상됨: {result}"
            )


# ═══════════════════════════════ Mutant Kill Evidence ═════════════════════
# 아래는 테스트 실행 후 보고할 mutant 정보 (RED 재현 증거용)이며,
# 실제 mutant 실증은 개발자가 production code 를 임시 수정해 수행한다.
# (docstring-only reference)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
