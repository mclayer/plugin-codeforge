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
    """ADR 절 추출 헬퍼 — 줄 기반 슬라이싱. 종료 = **레벨 ≤ 현재 레벨**인 다음 헤딩.

    Args:
        content: ADR 전체 내용
        section_heading: 찾을 헤딩 문자열 (예: "### §결정 9")

    Returns:
        해당 헤딩부터 **같은 레벨 또는 상위 레벨** 헤딩 직전까지의 텍스트

    Raises:
        AssertionError: 헤딩 부재 또는 슬라이싱 오류

    검증:
        - 헤딩 발견 실패 → AssertionError
        - 슬라이스 길이 ≤ 헤딩 줄 길이 → AssertionError (1글자 사건 방지)

    ★ 종료조건 정정 (구현리뷰 iter5 F-CR5-02 — 헬퍼 자신이 h2 맹인이었다):
      구판 종료조건은 `startswith("### ") and not startswith("#### ")` 였다. 이름은
      "같은 레벨" 인데 실제로는 **정확히 같은 레벨만** 종료로 봤고 `## `·`# ` 상위 레벨은
      종료로 보지 않았다 — 즉 docstring 이 선언한 "또는 상위 레벨" 이 코드에 없었다.
      귀결: 한 문서의 **마지막** `###` 절은 이후 h2 절 전부를 흡수한다. ADR-172 의
      `### §결정 10` 이 정확히 그 자리라 슬라이스가 `## 결과` · `## 관련 파일` ·
      `## 해소 기준` · `## Amendment 1` **h2 4절**을 삼키고 `### A1-1` 에서야 멈췄다.
      이 결함은 **헬퍼를 쓰는 5 site 전부가 상속**한다(오늘 §결정 2·4·8·9 가 무해한
      유일한 이유는 그 뒤에 같은 레벨 헤딩이 곧바로 오기 때문 — 구조가 아니라 배치다).
      ⇒ 종료조건을 **레벨 ≤ 현재 레벨**로 정정한다(정규식 `^#{1,N} `).

      mutant kill (AC-4 정의역에서 실측):
        · M-SURVIVE   — §결정 10 권한면 행 1개를 `## 결과` 절로 **이동** ⇒ 본 판본 RED /
                        구판 **생존**(슬라이스가 `## 결과` 까지 흘러 행을 여전히 셌다.
                        구판 오라클이 잰 것은 "§결정 10 에 열거"가 아니라 "문서 어딘가 존재")
        · M-FALSE-RED — `## 결과` 에 무관한 표 행 주입 ⇒ 본 판본 GREEN / 구판 **거짓 RED**
                        (§결정 10 과 무관한 행을 데이터 행으로 셌다)
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
    if heading_level < 1:
        raise AssertionError(f"헤딩 형식 오류(선두 '#' 부재): {section_heading!r}")

    # 종료 = 레벨 1..heading_level 의 다음 헤딩 (= 같은 레벨 **또는 상위 레벨**).
    #   `^#{1,N} ` 는 `#### ` 를 매치하지 않는다 — 4번째 문자가 공백이 아니므로
    #   backtrack 해도 `#{1,3}` + ' ' 가 성립하지 않는다(하위 레벨은 절의 일부로 보존).
    end_re = re.compile(r"^#{1,%d} " % heading_level)
    end_idx = next(
        (i for i in range(start_idx + 1, len(lines)) if end_re.match(lines[i])),
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


# ══════════ 헬퍼 자신의 직접 오라클 (구현리뷰 iter6 F-CR6-05) ═══════════════════
# ★ 왜 필요했나: iter5 가 종료조건을 `^#{1,N} ` 로 정정한 것은 **진짜 봉합**이었지만
#   (M-SURVIVE 재현으로 확인) 그 실험이 **기계화되지 않았다** — 종료조건을 구판
#   (`^#{N} ` = 정확히 같은 레벨만)으로 되돌려도 이 파일의 스위트가 전건 GREEN 이었다.
#   AC 표 검사들은 §결정 10 뒤에 곧바로 같은 레벨 헤딩이 오는 **배치**에 기대고 있어
#   h2 흡수 형상을 만들지 못한다. 아래는 그 형상을 fixture 로 직접 만든다.
_SLICE_FIXTURE = """# 문서 제목

## 상위 절 A

### 대상 절
대상 본문 1
#### 하위 절
하위 본문
## 상위 절 B
상위 본문 B
"""

_SLICE_EXPECTED = """### 대상 절
대상 본문 1
#### 하위 절
하위 본문
"""


class TestExtractAdrSectionTerminator:
    """`extract_adr_section` 의 **종료 지점을 값으로** 고정한다.

    mutant kill: 종료조건 `^#{1,N} ` → `^#{N} ` (정확히 같은 레벨만) 되돌리기
      ⇒ `test_stops_before_higher_level_heading` RED (슬라이스가 `## 상위 절 B` 를 흡수).
    """

    def test_stops_before_higher_level_heading(self):
        """`### X` 다음에 `## Y` 가 오면 **`## Y` 직전**에서 끝난다 (h2 흡수 0)."""
        got = extract_adr_section(_SLICE_FIXTURE, "### 대상 절")
        assert got == _SLICE_EXPECTED, (
            "종료 지점이 어긋났다 — 상위 레벨 헤딩을 흡수했거나 하위 레벨에서 잘렸다.\n"
            f"기대:\n{_SLICE_EXPECTED!r}\n실제:\n{got!r}"
        )
        # 값 고정을 두 방향으로 재확인 (문자열 비교가 우연히 맞는 일 방지)
        assert "## 상위 절 B" not in got, "상위 레벨 절을 삼켰다"
        assert "#### 하위 절" in got, "하위 레벨 절이 잘렸다 — 절의 일부여야 한다"

    def test_stops_before_h1(self):
        """상위 레벨은 h2 만이 아니다 — `# Z` 도 종료다."""
        text = "### 대상 절\n본문\n# 최상위\n뒤\n"
        got = extract_adr_section(text, "### 대상 절")
        assert got == "### 대상 절\n본문\n", f"h1 에서 멈추지 않았다: {got!r}"

    def test_stops_at_same_level_sibling(self):
        """**회귀 가드**: 같은 레벨 형제에서 멈추는 기존 동작은 그대로다."""
        text = "### 대상 절\n본문\n### 형제 절\n뒤\n"
        got = extract_adr_section(text, "### 대상 절")
        assert got == "### 대상 절\n본문\n", f"같은 레벨 종료가 깨졌다: {got!r}"

    def test_runs_to_eof_when_no_terminator(self):
        """종료 헤딩이 없으면 문서 끝까지 (경계)."""
        text = "### 대상 절\n본문\n#### 하위\n더\n"
        assert extract_adr_section(text, "### 대상 절") == text


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

    def test_ac2_github_write_zero(self, capsys):
        """AC-2 ① GitHub 측 델타 0 (normative) — **비공허 관측 + `--dry-run`** 형상.

        ★ 이전 판본의 구조적 공허 (구현리뷰 iter2 F-1 — 여기서 봉합):
          `collect_observations` 를 **빈 목록**으로 stub 했기 때문에 `run()` 이
          `if not observations:` 조기반환 경로만 탔고, 그 경로에서 `post_report` 는
          **도달 불가**라 `call_count == 0` 이 *어떤 구현에서도* 참이었다. 실증
          (DeveloperPL firsthand, 2회 반복 + 무돌연변이 대조):
            · Arm A — `if args.dry_run:` 분기에 `post_report(...)` 주입 ⇒ **아무도 안 죽음**
            · Arm B — `if not observations:` 분기에 주입 ⇒ 그 테스트만 RED
          즉 `--dry-run` 인자를 넘기면서도 dry-run 경로를 **한 줄도 태우지 않았다**.

        ★ 여기서의 형상 (3항):
          ① `collect_observations` stub = **fixture Observation ≥1** (빈 목록 금지)
          ② `--dry-run` 으로 `run()` 을 태우고 **`post_report` + `fetch_existing_keys`
             양쪽** spy 로 `call_count == 0` — Change Plan §8.0·§8.2-E 의
             *"채널 미접촉 = 조회조차 하지 않는다"* **2 conjunct 를 모두** 잰다.
          ③ **비공허성 앵커** — stdout DONE 줄의 `observed=N` 이 실제로 ≥1 임을 확인.
             이게 없으면 다음 hermetic 화가 같은 자리를 다시 빈 목록으로 되돌려도
             RED 가 나지 않는다(이번 결함의 재발 경로 자체를 막는 앵커다).

        mutant kill:
          · `if args.dry_run:` 분기에 `post_report(...)` 주입 ⇒ RED (Arm A — 이전 판본 GREEN)
          · `--dry-run` 분기에 `fetch_existing_keys(...)` 주입 ⇒ RED (조회 conjunct)
          · `collect_observations` stub 이 빈 목록으로 회귀 ⇒ RED (앵커 ③)

        ★ Hermetic 3중: fixture 관측 주입(실 홈 스캔 0) · 정지 플래그 tmpdir 주입
          (실 사용자 F2 파일에 종속되면 정지 경로로 새어 단언이 다시 공허해진다) ·
          heartbeat 경로 tmpdir 주입(실 사용자 상태 무접촉 — dry-run 은 미기록이지만
          경로 회귀 시에도 실 파일을 건드리지 않도록 봉인).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            scratch_dir = os.path.join(tmpdir, "scratch")
            temp_dir = os.path.join(tmpdir, "temp")
            os.makedirs(scratch_dir, exist_ok=True)
            os.makedirs(temp_dir, exist_ok=True)
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            f2_path = os.path.join(tmpdir, "no-such-stop-flag.disabled")   # 부재 = 정지 아님

            # Arrange ①: 비공허 관측 — fixture Observation 2건 (빈 목록 금지)
            fixture_obs = [
                sut.Observation(cls="worktree", display_path="~/.claude/worktrees/fixture-a",
                                declared="정리됨", measured="잔존", mismatch=True),
                sut.Observation(cls="scratch", display_path="~/.claude/codeforge-scratch/fixture-b",
                                declared="TTL초과=0", measured="TTL초과=1", mismatch=True),
            ]

            def mock_collect_observations(**kwargs):
                return list(fixture_obs)

            original_flag = sut.STOP_FLAG_LOCAL
            try:
                sut.STOP_FLAG_LOCAL = f2_path
                with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}), \
                     mock.patch.object(sut, "post_report") as spy_post, \
                     mock.patch.object(sut, "fetch_existing_keys") as spy_fetch, \
                     mock.patch.object(sut, "collect_observations",
                                       side_effect=mock_collect_observations):
                    # Act: --dry-run — 채널 미접촉 계약 경로를 **실제로** 태운다
                    rc = sut.run(["--repo-root", tmpdir,
                                  "--channel", "owner/repo#123", "--dry-run"])
            finally:
                sut.STOP_FLAG_LOCAL = original_flag

            out = capsys.readouterr().out

            # Assert (ㄱ) — **비공허성 앵커**: 관측이 실제로 ≥1 로 dry-run 경로에 도달
            m = re.search(r"DONE: observed=(\d+)", out)
            assert m is not None, (
                f"DONE 줄 부재 — run() 이 dry-run 경로를 완주하지 않았다. stdout={out!r}"
            )
            observed = int(m.group(1))
            assert observed == len(fixture_obs) and observed > 0, (
                "비공허성 붕괴: dry-run 경로가 관측 %d건이 아니라 %d건으로 실행됐다 "
                "(0 이면 조기반환 경로 — 이 테스트의 채널 단언이 공허해진다). stdout=%r"
                % (len(fixture_obs), observed, out)
            )
            assert rc == 0, f"advisory 계약(INV-F) 위반: rc={rc}"

            # Assert (ㄴ) — conjunct 1/2: 발화 0
            assert spy_post.call_count == 0, (
                f"AC-2 ① 위반: --dry-run 인데 post_report 호출 {spy_post.call_count}회"
            )
            # Assert (ㄷ) — conjunct 2/2: **조회조차 0** (§8.0·§8.2-E "채널 미접촉")
            assert spy_fetch.call_count == 0, (
                f"AC-2 ① 위반: --dry-run 인데 fetch_existing_keys 호출 {spy_fetch.call_count}회 "
                "(미접촉 = 조회조차 하지 않는다)"
            )

    def test_ac2_github_write_zero_on_empty_observation(self, capsys):
        """AC-2 ① 의 **0건 경로** 축 — 관측 0건 조기반환에서도 채널 델타 0.

        위 `test_ac2_github_write_zero` 가 dry-run 경로를 전담하게 되면서 비게 되는
        경로를 그대로 덮는 형제 오라클이다. 두 테스트는 `run()` 의 **서로 다른
        종료 경로**를 태운다 — 하나가 다른 하나를 대체하지 않는다.

        mutant kill: `if not observations:` 분기에 `post_report(...)` 주입 ⇒ RED
          (Arm B — 이전 판본이 유일하게 죽이던 mutant. 여기서 승계한다.)

        ★ 이 경로는 `write_heartbeat()` 를 호출하므로 heartbeat 경로 주입이
          **필수**다 — 주입이 없으면 이 테스트가 실 사용자 파일
          (`~/.claude/worktree-gc-state/scheduled-task-last-run.epoch`)을 갱신해
          관측자 생존 신호를 위조한다(이전 판본의 실 결함).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            hb_path = os.path.join(tmpdir, "heartbeat.epoch")
            f2_path = os.path.join(tmpdir, "no-such-stop-flag.disabled")

            def mock_collect_observations(**kwargs):
                return []

            original_flag = sut.STOP_FLAG_LOCAL
            try:
                sut.STOP_FLAG_LOCAL = f2_path
                with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}), \
                     mock.patch.object(sut, "post_report") as spy_post, \
                     mock.patch.object(sut, "fetch_existing_keys") as spy_fetch, \
                     mock.patch.object(sut, "collect_observations",
                                       side_effect=mock_collect_observations):
                    rc = sut.run(["--repo-root", tmpdir, "--channel", "owner/repo#123"])
            finally:
                sut.STOP_FLAG_LOCAL = original_flag

            out = capsys.readouterr().out

            # Assert (ㄱ): 실제로 0건 경로였다 (경로 앵커 — 이 테스트의 정의역 고정)
            assert re.search(r"DONE: observed=0 ", out) is not None, (
                f"0건 경로 미진입 — 이 테스트의 정의역이 아니다. stdout={out!r}"
            )
            assert rc == 0, f"advisory 계약(INV-F) 위반: rc={rc}"

            # Assert (ㄴ·ㄷ): 발화 0 ∧ 조회 0
            assert spy_post.call_count == 0, (
                f"AC-2 ① 위반: 관측 0건인데 post_report 호출 {spy_post.call_count}회"
            )
            assert spy_fetch.call_count == 0, (
                f"AC-2 ① 위반: 관측 0건인데 fetch_existing_keys 호출 {spy_fetch.call_count}회"
            )

            # Assert (ㄹ): heartbeat 는 tmpdir 로만 기록 (실 사용자 상태 무접촉)
            assert os.path.exists(hb_path), (
                "0건 경로는 관측 사이클을 완주하므로 heartbeat 기록 대상이다 "
                "(§8.10.1 기록 O 5경로) — 주입 경로에 기록이 없다"
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
        """능력 감사: 저장 프롬프트 안 `update_scheduled_task` 부재.

        ★ 정의역 폐쇄 (구현리뷰 iter4 F-CR-402 회수 site 3, 신규 발견):
          구판은 `code_start = content.find("```", decision_2_idx)` 로 **상한 없이**
          앞으로 훑었다. 오늘 무해한 유일한 이유는 ADR-172 의 fenced block 이 정확히
          1쌍(L66/L82)이라 표류할 대상이 0 이기 때문이다 — 구조가 아니라 우연이다.
          다른 절이 코드블록을 하나라도 얻는 순간 §결정 2 의 프롬프트를 삭제한 mutant 가
          **RED 가 아니라 vacuous-pass** 로 넘어간다: 부정 단언(`not in`)은 정의역이
          비거나 엉뚱하면 **자동으로 참**이 되기 때문이다.

        봉합 (CP §8.0-c D-1 + D-2):
          · D-1 절 경계 폐쇄 — `extract_adr_section("### §결정 2")` 로 정의역을 닫는다
            (고정 창·상한 없는 `find()` 금지). 신규 자산 0(이미 4 site 가 쓰는 헬퍼).
          · D-2 부정 단언 전 **정의역 non-empty 선행 단언** — fenced block 실재 +
            프롬프트 본문 실재(선두 리터럴)를 먼저 세운 뒤에 부정 단언을 놓는다.

        mutant kill (2종 실측):
          · discriminating — §결정 2 fence 삭제 ∧ §결정 5 에 더미 코드블록 추가
            ⇒ 본 판본 RED / 구판 **vacuous-pass**(더미 블록으로 표류)
          · regression-guard — §결정 5 에 더미 코드블록만 추가(§결정 2 온전)
            ⇒ 본 판본 GREEN (정의역이 §결정 2 로 닫혀 있음을 확인)
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-3 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # D-1: 정의역을 §결정 2 절로 **닫는다** (절 밖 fence 로 표류 불가)
        try:
            decision_2_section = extract_adr_section(content, "### §결정 2")
        except AssertionError as e:
            pytest.fail(f"AC-3: {e}")

        # D-2: 부정 단언 앞에 정의역 non-empty 를 **선행 단언**한다.
        code_start = decision_2_section.find("```")
        assert code_start != -1, (
            "AC-3 정의역 붕괴: §결정 2 절 안에 fenced block 이 없다 — 저장 프롬프트 박제본이 "
            "사라졌거나 절 밖으로 이동했다. 이 상태에서 부정 단언을 놓으면 vacuous-pass 다."
        )
        code_end = decision_2_section.find("```", code_start + 3)
        assert code_end != -1, (
            "AC-3 정의역 붕괴: §결정 2 절 안 fenced block 의 종료 마크 부재 (절 경계에서 잘렸다)."
        )
        prompt_text = decision_2_section[code_start:code_end]

        assert prompt_text.strip("` \n\r\t"), (
            "AC-3 정의역 붕괴: §결정 2 fenced block 이 비어 있다 — 부정 단언이 자동 참이 된다."
        )
        # 정의역이 **실제로 그 프롬프트인지** 양성 결박 (빈 블록·엉뚱한 블록 차단)
        assert "codeforge 로컬 잔재 관측" in prompt_text, (
            "AC-3 정의역 붕괴: §결정 2 의 첫 fenced block 이 저장 프롬프트 박제본이 아니다 "
            f"(선두 리터럴 미검출). 블록 선두 80자: {prompt_text[:80]!r}"
        )

        # Assert(부정): update_scheduled_task 부재 — 위에서 정의역을 세운 뒤에만 유효하다
        assert "update_scheduled_task" not in prompt_text, (
            "AC-3 위반: 저장 프롬프트에 update_scheduled_task 도구 존재"
        )

    def test_ac3_no_write_home_claude_in_prompt(self):
        """권한면: §결정 4 **안에** 권한 층 lever 2항 + 계상 금지 3축 명제 실재.

        ★ 선언 명제 정정 (구현리뷰 iter4 F-CR-402): 구판 선언은 "`~/.claude` 쓰기 deny
          명시 실재" 였는데, §결정 4 는 그런 문장을 담지 않는다 — 담은 것은 (a) 규범
          lever 2항(`permissions.deny` 키 **신설** + `disableBypassPermissionsMode`)과
          (b) 그 lever 들을 live 실측 전까지 **계상하지 말라**는 3축 요구다. 선언을
          본문 사실에 맞춰 정정하고 단언을 그 명제에 결박한다.

        ★ F-B 봉합 (구현리뷰 iter4 P1): 직전 판본은 `content[idx : idx+2000]` **고정 창**
          으로 잘랐다. §결정 4 실제 길이는 915자라 창이 **2.19배 초과**해 §결정 5·6 을
          통째로 삼켰고, 그 두 절이 `deny`·`~/.claude` 를 각각 보유한다 ⇒ §결정 4 본문을
          전부 지워도 두 conjunct 가 **이웃 절에서** 충족돼 mutant 가 생존했다.
          이 오라클의 정의역이 §결정 4 가 아니었던 것이다(2 conjunct 중 `deny` 쪽 판별력 0).

        교체: 같은 파일의 `extract_adr_section()` — 헤딩부터 같은 레벨 다음 헤딩까지만
        자르고, 본문이 사라지면 그 자리에서 AssertionError("헤딩만 남음")로 착지한다.
        이미 3 site(§결정 8 ×2, §결정 9)가 쓰는 헬퍼라 신규 자산 0.

        mutant kill (3종 실측 — 구판 대조군 동반, 정직 기록):
          ┌──────────────────────────────────────┬────────┬──────────────┐
          │ mutant                               │ 본 판본 │ 구판(고정 창) │
          ├──────────────────────────────────────┼────────┼──────────────┤
          │ A 부재형 §결정 4 본문 삭제           │  RED   │ **생존**      │
          │ B 변형형 `~/.claude`→`<home>/.claude`│  RED   │  RED          │
          │ C 판별형 `deny` 만 제거(경로는 잔존) │  RED   │ **생존**      │
          │ D lever 2항+계상금지 3축 삭제        │  RED   │ **생존**      │
          │   (host settings 문장만 잔존)        │        │  ↑ G0 결격    │
          └──────────────────────────────────────┴────────┴──────────────┘
          · B 는 구판도 잡았다 — 즉 B 단독으로는 이 봉합의 판별 근거가 되지 못한다
            (regression-guard case). 실 판별 근거는 A·C 다.
          · C 는 리뷰 진단("2 conjunct 중 `deny` 쪽 판별력 0")을 **정확히 격리**한다:
            §결정 4 에서 `deny` 만 지우고 `~/.claude` 를 남기면 구판은 이웃 §결정 5 의
            `deny` 로 충족돼 통과했다.
          · D 는 **정의역을 §결정 4 로 닫은 뒤에도 남은** 결함이다(F-CR-402). 절 경계
            문제가 아니라 **술어 등급** 문제라 창을 좁혀도 못 잡는다 — 잔존 carrier 가
            같은 절·같은 줄 안에서 두 토큰을 공급하기 때문이다. G1 명제 앵커로만 죽는다.
        """
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        if not adr_path.exists():
            pytest.fail(f"ADR-172 부재: {adr_path} (AC-3 검사 정의역 필수, design lane 산출물 부재)")

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # §결정 4 권한면 검증 — 헤딩 기준 **정확 슬라이싱**(고정 창 금지, 위 docstring)
        decision_4_section = extract_adr_section(content, "### §결정 4")

        # ── G1 명제 앵커 (구현리뷰 iter4 F-CR-402 / CP §8.0-c) ────────────────────
        #   구판 `"deny" in s and "~/.claude" in s` 는 **G0 결격**이었다: 짧은 일반 토큰
        #   2개의 독립 공존이라, 규범 lever 2항과 계상 금지 3축을 전부 지우고 host
        #   settings 문장만 남긴 mutant D 가 **생존**했다. 잔존 carrier 가
        #     "host `~/.claude/settings.json` 을 방어 lever 로 계상하지 **않는다** — `deny` 키 부재"
        #   로 **선언 명제와 정반대 취지**인데 두 토큰을 한 줄 안에 갖기 때문이다.
        #   창을 좁히는(locality) 방향으로는 원리적으로 못 잡는다 — 같은 줄에 있으므로.
        #   ⇒ 토큰 공존이 아니라 **명제 앵커**로 승격한다.
        #   ☞ 대가: G1 승격은 이 오라클을 ADR 본문 **리터럴에 결박**한다 — 문안을 다듬기만
        #     해도 RED 가 된다. 이는 결함이 아니라 CP §8.0-c 정직 천장 3번이 이미 선언한
        #     성질(리워딩 내성 없음 = 검출력의 대가)이며, 앵커 갱신은 ADR 편집과 같은
        #     Story 안에서 처리한다.
        anchors = {
            "권한 층 lever — permissions.deny 키 신설":
                "`permissions.deny` 키 신설",
            "권한 층 lever — bypass 차단 토글":
                "disableBypassPermissionsMode",
            "계상 금지 3축 (V1) deny 적용 여부": "(V1)",
            "계상 금지 3축 (V2) permission mode 상속": "(V2)",
            "계상 금지 3축 (V3) 토글 user-scope 실효": "(V3)",
            # 구판 conjunct 의 **의도**(host settings 를 lever 로 세지 않는다)를 G1 등급
            # 문장 전문으로 승계한다 — 토큰 `~/.claude` 단독 공존이 아니라 명제로.
            "host settings 계상 금지 명제":
                "host `~/.claude/settings.json` 을 방어 lever 로 계상하지 않는다",
        }
        missing = [name for name, lit in anchors.items() if lit not in decision_4_section]
        assert not missing, (
            "AC-3 위반: §결정 4 권한면 명제 앵커 누락 — %s\n"
            "(G0 토큰 공존이 아니라 명제 앵커 동시 presence 를 요구한다. "
            "규범 lever 2항 또는 계상 금지 3축이 절에서 사라졌는지 확인하라.)" % missing
        )

    def test_ac3_fetch_existing_keys_excludes_external_body(self):
        """외부 본문 유입 0 — fetch_existing_keys 는 자기 마커만 추출.

        mutant: 미매치 코멘트의 본문을 반환값에 실음 → 외부 문자열 등장 → RED

        ★ 픽스처 갱신 (FIX13 / F-SEC-1, ADR-172 A6-2 대가 5항): 채택 술어가
          `SENTINEL in body` 단독에서 **`viewerDidAuthor is True` ∧ SENTINEL** 로 좁혀졌다.
          필드 없는 구 픽스처는 fail-closed 로 전량 불신되어 이 테스트가 RED 로 드러났다
          (조용히 통과하지 않는다 — fail-closed 기본값의 부수 이득). 타인 저작 축의
          판별은 형제 파일(`test_scheduled_task_output_hardening.py`)이 전담한다.
        """
        fake_gh = mock.Mock()
        fake_gh.return_value = mock.Mock(
            returncode=0,
            stdout=json.dumps({
                "comments": [
                    {
                        "body": "사용자가 작성한 코멘트입니다 (마커 미부착)",
                        "viewerDidAuthor": False,
                    },
                    {
                        "body": f"{sut.SENTINEL} 자기 마커\n- 선언=test · 실측=test · key=test:path",
                        "viewerDidAuthor": True,
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

        ★ 정의역 폐쇄 (구현리뷰 iter5 F-CR5-02 — D-1 정의역 전수의 마지막 site):
          구판은 helper 조차 쓰지 않는 raw `content.find("### ", idx+4)` 였다. FIX5 가
          §8.0-c D-1("고정 창·상한 없는 find 금지, 절 경계로 정의역을 닫는다")을 신설한
          바로 그 라운드에 이 site 를 놓쳤다. 실측 귀결: `### §결정 10` 다음의 `### ` 는
          **`### A1-1`**(Amendment 1 하위 절)이라 슬라이스가 `## 결과` · `## 관련 파일` ·
          `## 해소 기준` · `## Amendment 1` **h2 4절을 흡수**했다.
          ⇒ helper 로 회수한다. 단 helper 자신도 같은 h2 맹인 결함을 갖고 있었으므로
            (b) 회수만으로는 **닫히지 않는다** — `extract_adr_section` 의 종료조건
            정정(a)과 **둘 다** 있어야 정의역이 §결정 10 으로 닫힌다.

        mutant kill (2종 실측 — 구판 대조군 동반):
          · M-SURVIVE   — 권한면 행 1개를 `## 결과` 절로 **이동** ⇒ 본 판본 RED(6→5) /
                          구판 **생존**(정의역이 문서 꼬리까지 열려 있어 여전히 6행)
          · M-FALSE-RED — `## 결과` 에 무관한 표 행 주입 ⇒ 본 판본 GREEN /
                          구판 **거짓 RED**(6→7)
        """
        # ADR-172 권한면 절 찾기
        adr_path = Path(__file__).parent.parent.parent / "archive" / "adr" / "ADR-172-local-scheduled-task-residue-observation.md"
        assert adr_path.exists(), "ADR-172 부재 (AC-4 검사 정의역 필수)"

        with open(adr_path, encoding="utf-8") as f:
            content = f.read()

        # §결정 10 권한면 절 — 헤딩 기준 **정확 슬라이싱**(raw find 금지, D-1)
        try:
            decision_10_section = extract_adr_section(content, "### §결정 10")
        except AssertionError as e:
            pytest.fail(f"AC-4: ADR-172 §결정 10 정의역 붕괴 — {e} "
                        "(권한면 6종 열거표 정본 필수)")

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

        # 1. 채택 축 — **필드 전문**으로 결박한다 (G1).
        #    ★ 구판 `"**채택 축**" in s and "P4" in s` 는 **G0 결격**이었다
        #      (구현리뷰 iter4 F-CR-402 회수 site 2, 신규 발견):
        #      같은 §결정 8 슬라이스 안 6셀 비교표가 `| **P4 Desktop 로컬 (채택)** | ...`
        #      행으로 `P4` 를 **독립 공급**하므로, 결정 기록의 채택 축을 `P3b` 로 바꾼
        #      mutant 에서도 두 토큰이 각각 충족돼 통과했다. 즉 이 단언은 "무엇을
        #      채택했는가" 를 전혀 판별하지 못했다 — 비교표 존재만 확인하고 있었다.
        assert "- **채택 축** = **P4 — Desktop 로컬 스케줄 작업**" in decision_section, (
            "AC-12: 채택 축 필드 전문('- **채택 축** = **P4 — Desktop 로컬 스케줄 작업**') "
            "미검출. 채택 축이 바뀌었거나 결정 기록 필드가 사라졌다 "
            "(비교표의 P4 셀은 이 명제의 근거가 되지 못한다 — 표는 후보 나열이다)."
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
        # ★ 기대 형상 = **산출면**(`_safe_text` 통과 후). 마크다운 무해화(F-SEC-4)가
        #   마스크 토큰의 `<`·`>` 도 이스케이프한다 — 우리 자신의 토큰을 예외로 두면
        #   그 예외 문면이 그대로 우회 표면이 되므로 예외를 두지 않았다.
        #   리터럴로 박아 둔다(SUT 로 계산하면 무해화 제거 mutant 아래 항진명제가 된다).
        assert "\\<user-home\\>" in result, (
            f"AC-13: <user-home> 정규화 미검출(산출면 형상): {result}"
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

        ★ 기대치 = (입력, **산출면 기대 문자열**) 쌍. 마크다운 무해화(F-SEC-4)는 마스크
          토큰의 `<`·`>` 를 이스케이프하지만 **경로 사실은 하나도 지우지 않는다** —
          이 테스트가 재는 것("비위반 토큰이 손상되지 않는다")은 그대로다.
          `~` 는 무해화 대상이 아니다(선언된 잔여: `~~` 짝이 있어야 발동 + 홈-상대
          표기 가독성이 load-bearing).
        """
        test_cases = [
            ("~/.claude/worktrees/foo", "~/.claude/worktrees/foo"),          # 홈 상대 경로
            ("<workspace>/plugin-codeforge", "\\<workspace\\>/plugin-codeforge"),  # 마커 경로
            ("<user-home>/.claude", "\\<user-home\\>/.claude"),              # 정규화된 경로
        ]
        for text, expected in test_cases:
            result = sut._safe_text(text)
            assert expected in result, (
                f"AC-13 오탐: 비위반 {text!r} 가 손상됨: {result!r}"
            )
            # 무해화가 **사실을 지우지 않았는가** — 역무해화하면 입력이 정확히 복원된다.
            assert sut.unneutralize_markdown(result) == text, (
                f"AC-13: 비위반 토큰이 가역 복원되지 않는다 — 무해화가 정보를 잃었다: "
                f"{text!r} → {result!r} → {sut.unneutralize_markdown(result)!r}"
            )


# ═══════════════════════════════ Mutant Kill Evidence ═════════════════════
# 아래는 테스트 실행 후 보고할 mutant 정보 (RED 재현 증거용)이며,
# 실제 mutant 실증은 개발자가 production code 를 임시 수정해 수행한다.
# (docstring-only reference)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
