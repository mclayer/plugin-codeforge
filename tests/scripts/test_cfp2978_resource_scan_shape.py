#!/usr/bin/env python3
"""
CFP-2978 AC-4 resource-scan shape validation test — QADev P0-3

[결속 선언]
본 파일의 모든 leg 은 Python SSOT `scripts/lib/check_parallel_work_sentinel.py --mode=resource-scan`
을 **subprocess.run() 실행**해 그 stdout JSON 위에서만 판정한다. 리터럴 dict 자기assert 0.

[정의역 선언]
본 테스트는 Python 인터프리터 직접 호출 경로(셸 비의존)로 resource-scan shape 계약만 검증한다.
bash wrapper (.sh) 경로는 bash 하네스 29 leg 에서 이미 덮으므로 중복 불필요(ADR-061 thin wrapper).

[다중 invocation 설계]
mock seam _run_gh 가 args 무시로 모든 호출에 동일 fixture 제공 → 단일 invocation 으로 모든 leg 동시 양성 불가.
각 invocation 은 특정 gh 응답 형식 fixture 를 사용:
- invocation-1 (repo view 형식): leg①, leg③ 양성 가능 (branches 파싱 실패)
- invocation-2 (branches 형식): leg② 양성 가능 (repo view 파싱 실패)
- invocation-3 (degrade): leg① 음성 (rc=1)
- M-4b (branches 음성): leg② RED (JSON 원문)
- M-4c (repo 음성): leg③ RED (비-slug)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional


# Python SSOT 절대경로 (bash wrapper 비의존)
PYTHON_SSOT = Path(__file__).resolve().parents[2] / "scripts" / "lib" / "check_parallel_work_sentinel.py"

# AC-4 정규식 상수 (production 코드 값공간)
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/@+-]{1,255}$")
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100}$")


# ============================================================================
# F-0: Oracle 결속 메타 leg (결속이 깨지면 RED)
# ============================================================================
def test_f0_oracle_bound_to_resource_scan_cli():
    """
    F-0 (결속 메타): SUT 바이너리(Python SSOT) 존재 및 resource-scan 모드 지원 검증.

    결속 대상 = `python3 scripts/lib/check_parallel_work_sentinel.py --mode=resource-scan`
    결속이 깨지는 신호 = python file 부재 또는 불가읽음 또는 --help 불가.

    이 leg 이 RED 이면 나머지 모든 test 는 의미 없다.
    """
    assert PYTHON_SSOT.exists(), f"Python SSOT missing: {PYTHON_SSOT}"
    assert PYTHON_SSOT.is_file(), f"SSOT is not a file: {PYTHON_SSOT}"
    assert os.access(PYTHON_SSOT, os.R_OK), f"SSOT not readable: {PYTHON_SSOT}"

    # 헬스 체크: --help 호출
    try:
        proc = subprocess.run(
            [sys.executable, str(PYTHON_SSOT), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # --help 가 exit 0 이 아닐 수도 있으므로 rc 는 검증 안 함
    except subprocess.TimeoutExpired:
        raise AssertionError(f"SSOT --help timed out")
    except Exception as err:
        raise AssertionError(f"SSOT not executable: {err}")

    print(f"\n[F-0 Oracle Binding] SUT bound and accessible:")
    print(f"  Path: {PYTHON_SSOT}")
    print(f"  Exists: {PYTHON_SSOT.exists()}")


# ============================================================================
# AC-4 검사 술어 (모듈 단일 정의 — 전 테스트 재사용)
# ============================================================================
def _check_leg1_present_and_true(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    leg① 검사: `determined is True` 동일성 + `branches`, `open_prs` 존재.

    성공: (True, "")
    실패: (False, 원인 설명)
    """
    if "determined" not in payload:
        return False, "missing 'determined' key"
    if payload.get("determined") is not True:
        return False, f"determined != True (got {payload.get('determined')!r})"
    if "branches" not in payload:
        return False, "missing 'branches' key"
    if "open_prs" not in payload:
        return False, "missing 'open_prs' key"
    return True, ""


def _check_leg1_degrade_omits_lists(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    leg① 음성 (degrade 경로): `determined is False` + `branches`, `open_prs` 부재.

    성공: (True, "")
    실패: (False, 원인 설명)
    """
    if payload.get("determined") is not False:
        return False, f"determined != False (got {payload.get('determined')!r})"
    if "branches" in payload:
        return False, "'branches' key should be absent in degrade payload"
    if "open_prs" in payload:
        return False, "'open_prs' key should be absent in degrade payload"
    return True, ""


def _check_leg2_branch_names_regex(branches: List[str]) -> Tuple[bool, str]:
    """
    leg② 검사: `branches` 원소 정규식.

    정규식: `^[A-Za-z0-9._/@+-]{1,255}$` ∧ `..` 미포함 ∧ 선두 `-` 아님

    ★ FIX Iter 4 (CR-2) — **개수 floor 를 본 술어에서 제거**했다.
      구 판은 여기에 `if len(branches) < 2: return False, …` 를 두었는데, 그것이
      **판별 축보다 먼저 종결**해 음성 대조군이 정규식에 **닿지도 못했다**.
      firsthand: M-4b 의 실 종결 문면 =
        `[M-4b] PASS: JSON text rejected. reason=branches should have >= 2 elements, got 1`
      ⇒ 아래 3검사(정규식 · `..` · 선두 `-`)를 **통째로 삭제해도 `7 passed`** 였다.
         실 판별자는 magic floor `2` 하나였고 3검사는 장식이었다.

      ★ 가드 약화가 아니라 **중복 제거**다: 같은 floor 가 **호출부**
        (`test_ac4_leg2_branch_names_match_corpus_regex` 의 `len(branches) >= 2`
        양성 비공허성 앵커)에 이미 있고 거기 존치한다. 양성 leg 에선 잉여였고,
        음성 leg 에선 유해했다 — 술어 내부에서만 걷어낸다.
      ⇒ **본 술어의 정의역 = 원소별 형태 판정뿐**. 카디널리티는 호출부 책임.

    성공: (True, "")
    실패: (False, 원인 설명)
    """
    if not isinstance(branches, list):
        return False, f"branches is not a list: {type(branches)}"

    for branch in branches:
        if not isinstance(branch, str):
            return False, f"branch element is not str: {type(branch)}"
        if not BRANCH_RE.match(branch):
            return False, f"branch '{branch}' doesn't match regex"
        if ".." in branch:
            return False, f"branch '{branch}' contains '..' (invalid)"
        if branch.startswith("-"):
            return False, f"branch '{branch}' starts with '-' (invalid)"

    return True, ""


def _check_leg3_excluded_self_repo_slug(excluded_self: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    leg③ 검사: `excluded_self.repo` slug 정규식.

    정규식: `^[A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100}$`

    성공: (True, "")
    실패: (False, 원인 설명)
    """
    if not isinstance(excluded_self, dict):
        return False, f"excluded_self is not a dict: {type(excluded_self)}"

    repo = excluded_self.get("repo")
    if not isinstance(repo, str):
        return False, f"excluded_self.repo is not str: {type(repo)}"

    if not SLUG_RE.match(repo):
        return False, f"excluded_self.repo '{repo}' doesn't match slug regex"

    return True, ""


def _invoke_resource_scan(
    repo: Optional[str] = None,
    path: Optional[str] = None,
    mock_response: Optional[Path] = None,
    mock_rc: Optional[int] = None,
    mock_stderr: Optional[str] = None,
    mock_auth_fail: bool = False,
) -> Tuple[int, Dict[str, Any], str]:
    """
    resource-scan 모드 실호출 및 JSON 파싱 (Python SSOT 직접 호출, 셸 비의존).

    반환: (rc, payload_dict, stderr_excerpt)
      rc: 프로세스 exit code
      payload_dict: stdout JSON 파싱 결과 (실패 시 {})
      stderr_excerpt: stderr 발췌
    """
    cmd = [sys.executable, str(PYTHON_SSOT), "--mode=resource-scan"]
    if repo:
        cmd.extend(["--repo", repo])
    if path:
        cmd.extend(["--path", path])

    # env 는 os.environ 사본에 mock seam 얹기 (PATH 등 상실 방지)
    env = os.environ.copy()

    # mock seam 설정
    if mock_response:
        env["CFP967_GH_MOCK_RESPONSE"] = str(mock_response)
    if mock_rc is not None:
        env["CFP967_GH_MOCK_RC"] = str(mock_rc)
    if mock_stderr:
        env["CFP967_GH_MOCK_STDERR"] = mock_stderr
    if mock_auth_fail:
        env["CFP967_GH_AUTH_MOCK"] = "fail"

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return 1, {}, "timeout"
    except Exception as err:
        return 1, {}, str(err)

    # stdout JSON 파싱
    payload = {}
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as err:
            print(f"JSON decode error: {err}", file=sys.stderr)
            print(f"stdout: {proc.stdout}", file=sys.stderr)

    stderr_excerpt = proc.stderr[:500] if proc.stderr else ""

    return proc.returncode, payload, stderr_excerpt


# ============================================================================
# AC-4 leg① + leg③ 양성 테스트 (invocation-1: empty/valid fixture)
# ============================================================================
def test_ac4_leg1_determined_is_true_and_lists_present():
    """
    AC-4 leg①: `determined is True` + `branches`, `open_prs` 존재.

    invocation-1 (empty fixture로 모든 gh 호출 성공, 빈 lists):
    - mock 이 모든 gh 호출에 동일 fixture 제공 → 각 호출이 다른 형식 기대
    - 아무 fixture나 써도 resource-scan 이 try-except 로 처리
    - determined=true + branches/open_prs 는 빈 list 도 가능
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        fixture_path = tmpdir_path / "empty.txt"

        # fixture: 비어있거나 각 gh 호출과 호환 가능한 형식
        # resource-scan 이 파싱 실패 시에도 default 값 사용 (prs = [], commits = [])
        fixture_path.write_text("")

        rc, payload, stderr = _invoke_resource_scan(
            repo="mclayer/mctrader",
            mock_response=fixture_path,
        )

        assert rc == 0, f"Expected rc=0, got {rc}. stderr: {stderr}"

        # leg① 검사: determined is True + keys 존재
        # ★무조건 assert — 조건부 통과 경로를 두지 않는다 (공허 통과 차단).
        ok, reason = _check_leg1_present_and_true(payload)
        assert ok, f"leg① failed: {reason}. payload keys={sorted(payload)}"
        # F-2 결격 차단: "키 존재" 가 아니라 `is True` 동일성이어야 한다.
        assert payload.get("determined") is True, (
            f"leg① 은 키 존재가 아니라 `is True` 동일성이다 (got {payload.get('determined')!r})"
        )
        print("[AC-4 leg①] PASS: determined is True + branches/open_prs 존재")


# ============================================================================
# AC-4 leg② 양성 테스트 (invocation-2: branches 줄 단위 fixture)
# ============================================================================
def test_ac4_leg2_branch_names_match_corpus_regex():
    """
    AC-4 leg②: `branches` 원소 정규식 검증.

    invocation-2 (branches 줄 단위 fixture):
    - gh api repos/.../branches -q .[].name 응답 형식 (줄 단위, JSON 아님)
    - resource-scan 이 파싱해서 줄 단위로 branches list 생성
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        fixture_path = tmpdir_path / "branches.txt"

        # fixture: gh api branches -q .[].name 응답 형식 (줄 단위)
        branches_text = "main\nfeat/BKT-94-phase2-impl"
        fixture_path.write_text(branches_text)

        rc, payload, stderr = _invoke_resource_scan(
            repo="example/repo",
            mock_response=fixture_path,
        )

        assert rc == 0, f"Expected rc=0, got {rc}. stderr: {stderr}"

        # payload 에 branches 가 있는지 확인
        branches = payload.get("branches", [])
        # ★무조건 assert — 조건부 통과 경로를 두지 않는다 (공허 통과 차단).
        # ★비-공허성: 빈 list 는 leg② 를 공허 만족시키므로 2건 이상을 강제한다
        #   (§8.C "양성 fixture 의무" — 실 코퍼스 실명 2건 채택).
        assert len(branches) >= 2, (
            f"leg② 양성 fixture 의무 위반 — 2건 이상이어야 공허 만족이 아니다: {branches!r}"
        )
        ok, reason = _check_leg2_branch_names_regex(branches)
        assert ok, f"leg② failed: {reason}. branches={branches!r}"
        print(f"[AC-4 leg②] PASS: {len(branches)} branches match regex")


# ============================================================================
# AC-4 leg③ 양성 테스트 (invocation-3: git 에서 가져온 repo)
# ============================================================================
def test_ac4_leg3_excluded_self_repo_is_slug():
    """
    AC-4 leg③: `excluded_self.repo` slug 정규식 검증 (양성).

    ★정의역 사실 (firsthand): `excluded_self.repo` 는 git remote 가 아니라
      `gh repo view --json nameWithOwner` 산출이며 **mock seam 이 지배한다**
      (`_run_gh` 가 `args` 를 참조하지 않고 fixture 바이트를 그대로 반환).
      따라서 fixture 를 정확한 slug 1줄로 두면 leg③ 양성이 결정적으로 재현된다.
      (M-4c 가 같은 채널로 비-slug 를 주입해 RED 를 내는 것이 그 반증이다.)

    invocation-3 정의역: leg③ **양성만**. 이 fixture 는 branches 를 1원소로
      만들므로 leg② 는 본 invocation 의 **정의역 밖**이다 (leg② 양성은
      invocation-2 가 담당). 단일 fixture 가 전 leg 을 덮는 척하지 않는다.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "self-repo.txt"
        # mock 은 전 gh 호출에 같은 바이트를 준다 → 이 1줄이 self_repo 가 된다.
        fixture_path.write_text("mclayer/plugin-codeforge\n", encoding="utf-8")

        rc, payload, stderr = _invoke_resource_scan(
            repo="mclayer/plugin-codeforge",
            mock_response=fixture_path,
        )

        assert rc == 0, f"Expected rc=0, got {rc}. stderr: {stderr}"

        excluded_self = payload.get("excluded_self")
        # ★무조건 assert — 조건부 통과 경로를 두지 않는다 (공허 통과 차단).
        ok, reason = _check_leg3_excluded_self_repo_slug(excluded_self)
        assert ok, f"leg③ failed: {reason}. excluded_self={excluded_self!r}"
        assert excluded_self["repo"] == "mclayer/plugin-codeforge", (
            f"leg③ 채널 결속 실패 — mock 이 지배하지 않았다: {excluded_self!r}"
        )
        print(f"[AC-4 leg③] PASS: excluded_self.repo='{excluded_self['repo']}'")


# ============================================================================
# M-4a 대조군: degrade payload (determined=False)
# ============================================================================
def test_ac4_m4a_degraded_payload_omits_lists():
    """
    M-4a 대조군: leg① 음성 — degrade 경로에서 `branches`, `open_prs` 부재.

    fixture: CFP967_GH_MOCK_RC=1 (gh 실패) → degrade payload 생성 기대

    leg① 선택문: "키 존재" 형 술어라면 여기서 GREEN 이 되므로 discriminating.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        fixture_path = tmpdir_path / "empty.json"
        fixture_path.write_text("")

        rc, payload, stderr = _invoke_resource_scan(
            repo="mclayer/mctrader",
            mock_response=fixture_path,
            mock_rc=1,  # gh 실패 시뮬레이션
        )

        # rc 는 0 이어야 함 (graceful degradation)
        assert rc == 0, f"Expected graceful degrade (rc=0), got rc={rc}"

        # leg① 음성 검사
        ok, reason = _check_leg1_degrade_omits_lists(payload)
        assert ok, f"M-4a failed: {reason}. payload: {payload}"
        print(f"[M-4a] PASS: degrade payload omits branches/open_prs")


# ============================================================================
# leg② 음성 대조군 공용 하네스 (M-4b · M-4d · M-4e — 축 격리)
# ============================================================================
# ★ 대조군 설계 규칙 (CR-2 가 준 교훈): 대조군은 **판별 축 이외의 모든 선행 가드를
#   충족**해야 한다. 그렇지 않으면 축에 닿기 전에 다른 가드가 먼저 답을 내버리고,
#   그 통과를 "축이 작동했다" 로 오독하게 된다 (구 판 M-4b 가 정확히 그랬다).
#   ⇒ 세 대조군 모두 (i) 원소 **2건** (호출부 floor 충족) (ii) 전부 `str`
#      (iii) 첫 원소 `main` 은 3검사 전건 통과 — 위반은 **둘째 원소 1건, 축 1개뿐**.
#   ⇒ 그리고 종결 **사유 문면을 축별로 assert** 한다. "RED 였다" 로는 부족하다 —
#      어느 assert 에서 종결됐는지가 판별력의 실체다.
def _run_leg2_negative_control(
    ctl: str,
    fixture_text: str,
    expected_branches: List[str],
    expected_reason: str,
) -> str:
    """leg② 음성 대조군 1건 실행. 종결 사유 문면 반환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "branches.txt"
        fixture_path.write_text(fixture_text, encoding="utf-8")

        rc, payload, stderr = _invoke_resource_scan(
            repo="example/repo",
            mock_response=fixture_path,
        )

        # ★무조건 assert — print 만 하는 경로를 두지 않는다 (unfailable 차단).
        assert rc == 0, f"{ctl}: 대조군은 rc=0 경로여야 한다 (got {rc}). stderr: {stderr}"

        branches = payload.get("branches", [])

        # ── 선행 가드 충족 앵커 (축 격리의 전제) ──────────────────────────────
        assert branches == expected_branches, (
            f"{ctl} 하네스 결격 — SSOT 가 기대 branches 를 내지 않았다. "
            f"실측={branches!r}, 기대={expected_branches!r}. "
            "대조군이 의도한 축에 닿지 못한다."
        )
        assert len(branches) >= 2, (
            f"{ctl} 하네스 결격 — 호출부 floor(>=2)를 대조군이 충족해야 "
            f"개수 축이 아닌 형태 축을 시험한다. branches={branches!r}"
        )

        # ── 판별 축 ────────────────────────────────────────────────────────
        ok, reason = _check_leg2_branch_names_regex(branches)
        assert not ok, (
            f"{ctl} 결격 — 위반 원소가 leg② 를 통과했다. "
            f"branches={branches!r} (검사기가 이 입력을 잡지 못하면 판별력 0)"
        )
        # ★ 종결 지점 고정 — 다른 가드가 먼저 답을 내면 여기서 잡힌다.
        assert reason == expected_reason, (
            f"{ctl} 축 어긋남 — 기대한 축이 아닌 곳에서 종결됐다.\n"
            f"  실측 사유: {reason!r}\n"
            f"  기대 사유: {expected_reason!r}"
        )
        print(f"[{ctl}] PASS: rejected at expected axis. reason={reason}")
        return reason


# ============================================================================
# M-4b 대조군: 음성 fixture (JSON 원문) — 축 = 정규식
# ============================================================================
def test_ac4_m4b_json_text_branches_rejected():
    """
    M-4b 대조군: leg② 음성 — JSON 원문이 branch 로 해석되는 경우 (축 = **정규식**).

    ★ FIX Iter 4 (CR-2): fixture 를 1줄 → **2줄**로 교체했다. 구 판 fixture
      (`{"error": "invalid"}` 1줄)는 branches 를 **1원소**로 만들었고, 술어 내부
      floor(`>= 2`)가 정규식보다 **먼저** 종결해 정규식은 실행조차 되지 않았다
      (firsthand: `reason=branches should have >= 2 elements, got 1`).
      ⇒ 첫 원소를 유효 branch(`main`)로 두어 개수·형(型) 가드를 통과시키고,
        **둘째 원소만** 정규식을 위반하게 한다.
    """
    _run_leg2_negative_control(
        ctl="M-4b",
        fixture_text='main\n{"error": "invalid"}',
        expected_branches=["main", '{"error": "invalid"}'],
        expected_reason="branch '{\"error\": \"invalid\"}' doesn't match regex",
    )


# ============================================================================
# M-4d 대조군: `..` 포함 branch — 축 = dotdot (신설, CR-2)
# ============================================================================
def test_ac4_m4d_dotdot_branch_rejected():
    """
    M-4d 대조군 (신설): leg② 음성 — `..` 포함 (축 = **dotdot**).

    ★ 축 격리 근거: `feat/a..b` 는 정규식 `^[A-Za-z0-9._/@+-]{1,255}$` 를
      **통과**한다(`.` 와 `/` 가 값공간 안). 선두 `-` 도 아니다. 따라서 이 입력을
      잡는 검사는 `".." in branch` **하나뿐**이며, 그 검사를 지우면 이 대조군만
      단독으로 RED 가 된다. (git refname 규칙상 `..` 는 실 금칙이다.)
    """
    _run_leg2_negative_control(
        ctl="M-4d",
        fixture_text="main\nfeat/a..b",
        expected_branches=["main", "feat/a..b"],
        expected_reason="branch 'feat/a..b' contains '..' (invalid)",
    )


# ============================================================================
# M-4e 대조군: 선두 `-` branch — 축 = leading-dash (신설, CR-2)
# ============================================================================
def test_ac4_m4e_leading_dash_branch_rejected():
    """
    M-4e 대조군 (신설): leg② 음성 — 선두 `-` (축 = **leading-dash**).

    ★ 축 격리 근거: `-rf` 는 정규식을 **통과**한다(`-` 가 값공간 안). `..` 도 없다.
      따라서 이 입력을 잡는 검사는 `branch.startswith("-")` **하나뿐**이다.
      (선두 `-` 는 하류에서 옵션으로 오해석되는 argv injection 표면이라 실 금칙이다.)
    """
    _run_leg2_negative_control(
        ctl="M-4e",
        fixture_text="main\n-rf",
        expected_branches=["main", "-rf"],
        expected_reason="branch '-rf' starts with '-' (invalid)",
    )


# ============================================================================
# M-4c 대조군: 음성 fixture (non-slug excluded_self.repo)
# ============================================================================
def test_ac4_m4c_non_slug_excluded_self_rejected():
    """
    M-4c 대조군: leg③ 음성 — non-slug excluded_self.repo.

    fixture: gh repo view 응답이 비-slug (예: error dict, invalid format)
    - resource-scan 파싱 실패 또는 repo 가 slug 형식 아님
    - leg③ 정규식 미충족 → RED 기대
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        fixture_path = tmpdir_path / "bad-slug.json"

        # fixture: non-slug (nameWithOwner 없거나 형식 잘못됨)
        fixture_path.write_text('{"error": "not found"}')

        rc, payload, stderr = _invoke_resource_scan(
            repo="example",  # incomplete slug
            mock_response=fixture_path,
        )

        # ★무조건 assert — print 만 하는 경로를 두지 않는다 (unfailable 차단).
        assert rc == 0, f"M-4c: 대조군은 rc=0 경로여야 한다 (got {rc}). stderr: {stderr}"

        excluded_self = payload.get("excluded_self", {})
        ok, reason = _check_leg3_excluded_self_repo_slug(excluded_self)
        assert not ok, (
            "M-4c 결격 — 비-slug 가 leg③ 을 통과했다. "
            f"excluded_self={excluded_self!r} (leg③ 양성과 짝을 이뤄야 판별력이 선다)"
        )
        print(f"[M-4c] PASS: non-slug rejected. reason={reason}")
