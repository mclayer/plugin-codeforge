#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Bypass env gate disjoint invariant INV-B1.

목적:
  게이트 4종 × bypass env 4종 = 16-cell matrix
  각 cell: deny payload 에서 "exit==0 iff env==own(gate)" 검증

정의역:
  게이트 4종:
    1. cross-repo-gh-safety (BYPASS_CROSS_REPO_GH_SAFETY)
    2. repo-confinement (BYPASS_REPO_CONFINEMENT)
    3. git-branch-delete-merge-gate (BYPASS_BRANCH_DELETE_MERGE_GATE)
    4. worktree-location-guard (BYPASS_WORKTREE_LOCATION_GUARD)

  각 게이트마다 고유 deny payload (deny-triggering test case)

INV-B1: exit==0 iff env==own(gate)
  - 예: cross-repo-gh-safety 게이트 + BYPASS_CROSS_REPO_GH_SAFETY=1 → exit 0
  - 예: cross-repo-gh-safety 게이트 + BYPASS_REPO_CONFINEMENT=1 → exit 2 (deny)

테스트:
  - 각 게이트별 deny payload 이용
  - 4개 bypass env 조합 (본 env + 타 env 3개 + 미설정)
  - 16 cell 모두 검증 — 대각 4 (test_bypass_env_own_gate_exits_zero)
                      + 비대각 12 (test_bypass_env_other_gate_denies)

branch-gate 축 (CFP-2965 AC-20 완결):
  git-branch-delete-merge-gate 는 열린 PR 조회에 `gh` 를 쓴다. 과거 이 축 3 cell
  (비대각) 과 사전조건은 "gh mock 필요"로 제외돼 13/16 이었다. gh mock-seam 을
  배선해 16/16 로 완결한다 (seam 설계·PATH shim 불가 사유 = 아래 seam 주석).

  모든 branch-gate cell 은 **마커 assert** 를 동반한다 (ADR-171 mock-seam):
    - gh 를 무는 cell (비대각 12 중 3 + 사전조건) → 마커 **존재** 필수.
      부재 = shim 미사용 = 실 gh 폴백 → 관측 무효이므로 FAIL.
    - 대각 cell (자기 bypass=1) → bypass 가 gh 조회보다 앞에서 단락하므로
      마커 **부재** 가 정상. 여기선 stderr 의 bypass audit 줄로 경로를 확정한다.
  실 gh 네트워크 호출 0.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import pytest
from pathlib import Path

from hook_runner_cfp2965 import BYPASS_ENVS, parametrize_argvalues, requires_bash, run_hook_bash

# 훅 실행은 bash 직접 호출로 통일 (구 `cmd.exe /c run-hook.cmd` 하드코딩은 Linux CI 에서
# FileNotFoundError → 전건 FAIL). bypass disjoint 판정 축은 OS 무관 — conftest SSOT.
pytestmark = requires_bash


# Deny payloads per gate (S0/corpus 검증분 재사용)
DENY_PAYLOADS = {
    "cross-repo-gh-safety": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "gh pr edit 94"  # bare space trigger (sed truncation)
        }
    },
    "repo-confinement": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "echo secret > ~/payload.txt"  # home-root write (redirect)
        }
    },
    "git-branch-delete-merge-gate": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git push origin --delete develop"  # delete branch
        }
    },
    "worktree-location-guard": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git worktree add /tmp/test-wd"  # non-standard path
        }
    },
}

# Bypass env names (1:1 map to gates) — 정의는 hook_runner_cfp2965 (공용 정의역).
#   timeout rationale 표의 AC-16 #1 정의역과 **같은 게이트 4종**을 가리켜야 하므로
#   두 테스트가 서로를 import 하지 않고 고유명 모듈을 공통 출처로 삼는다
#   (테스트-간 import 는 수집 구성에 따라 이름 해석이 흔들리는 표면 — CR-201).

# Hook names (from hooks.json)
HOOK_NAMES = {
    "cross-repo-gh-safety": "cross-repo-gh-safety",
    "repo-confinement": "repo-confinement",
    "git-branch-delete-merge-gate": "git-branch-delete-merge-gate",
    "worktree-location-guard": "worktree-location-guard",
}


# ============================================================================
# branch-gate gh mock-seam (ADR-171 mock-seam — 마커로 shim 사용 실증)
# ============================================================================
#
# git-branch-delete-merge-gate.py 는 열린 PR 을 subprocess.run(["gh", ...],
# shell=False) 로 조회한다. deny cell 을 만들려면 "열린 PR 있음" 응답이 필요하다.
#
# ★ PATH shim 이 성립하지 않는다 (firsthand 실측 2026-08-14, Windows/py3.14):
#   Windows CreateProcess 는 확장자 없는 argv0 에 `.exe` 만 덧붙인다 — PATHEXT 는
#   cmd.exe 의 탐색 규칙이지 CreateProcess 의 규칙이 아니다. 그래서 PATH 앞에 둔
#   `gh.bat` / `gh.cmd` / extensionless `gh` 는 **선택되지 않고** 뒤쪽 PATH 의
#   실제 `gh.exe` 가 호출된다.
#     실측: gh.bat 를 PATH 앞에 두고 훅 실행 → rc=0 (기대 2), 마커 미생성.
#           즉 shim 이 조용히 무시되고 실 gh 가 네트워크로 응답([] = 열린 PR 없음)
#           → fail-open exit 0 = **거짓 PASS**. (동일 관측이
#           test_git_branch_delete_merge_gate.py 의 POSIX-only skip 근거이기도 하다)
#
# → seam 을 프로세스 경계 **안쪽**으로 옮긴다. PYTHONPATH 에 sitecustomize.py 를
#   두면 훅의 python 이 기동 시 자동 import 하고, 거기서 subprocess.run 을 감싼다.
#   argv0=="gh" 일 때만 canned JSON 반환 + 마커 파일 기록, 그 외는 원본에 위임.
#   실 gh 프로세스 기동 0 · 네트워크 호출 0.
#
# 마커 의무: shim 이 실제로 사용됐음을 파일 존재로 증명한다. seam 이 깨지면
#   (PYTHONPATH 미전달 / import 실패) 마커가 없고 실 gh 가 [] 를 돌려 rc=0 이 되어
#   테스트가 **FAIL** 한다 (조용한 거짓 PASS 불가 — fail-closed).

_GH_SITECUSTOMIZE = '''\
"""테스트 전용 gh mock-seam. PYTHONPATH 주입 시 python 기동과 함께 자동 import."""
import os
import subprocess

_orig_run = subprocess.run


def _run(args, *a, **kw):
    argv0 = args[0] if isinstance(args, (list, tuple)) and args else None
    if argv0 == "gh":
        marker = os.environ.get("GH_SHIM_MARKER")
        if marker:
            with open(marker, "w", encoding="ascii") as fh:
                fh.write("shim-used")
        stdout = os.environ.get("GH_SHIM_STDOUT", "[]")
        return subprocess.CompletedProcess(args, 0, stdout, "")
    return _orig_run(args, *a, **kw)


subprocess.run = _run
'''

# canned 응답 — 열린(미머지) PR 1건 = deny 를 만드는 shape
# (.py 실물 기준: _open_prs_for_branch 는 `--json number,title` 결과를 list 로 받고,
#  비어 있지 않으면 _build_block_message 후 exit 2)
GH_SHIM_OPEN_PR = json.dumps([{"number": 42, "title": "WIP feature"}])


def _make_gh_seam(tmp_path: Path) -> tuple[dict, Path]:
    """gh mock-seam env dict + 마커 경로 생성.

    Returns: (env_extra, marker_path) — marker_path 는 아직 미존재.
    """
    shim_dir = tmp_path / "ghseam"
    shim_dir.mkdir(parents=True, exist_ok=True)
    (shim_dir / "sitecustomize.py").write_text(_GH_SITECUSTOMIZE, encoding="utf-8")
    marker = tmp_path / "gh-shim-marker.txt"
    env_extra = {
        # Windows 형식 절대경로 (소비자 = python 기동 경로 해석)
        "PYTHONPATH": str(shim_dir),
        "GH_SHIM_MARKER": str(marker),
        "GH_SHIM_STDOUT": GH_SHIM_OPEN_PR,
    }
    return env_extra, marker


def _run_hook_with_env(hook_name: str, payload: dict, env_override: dict) -> tuple[int, str]:
    """훅 실행 (env 오버라이드).

    특별 처리: worktree-location-guard 는 TIER=block 동반 필수 (deny 판정 경로).
    """
    # 환경 변수 설정
    env = os.environ.copy()
    # 모든 bypass env 초기화
    for bypass_env in BYPASS_ENVS.values():
        env.pop(bypass_env, None)
    # seam env 잔재 초기화 (앞 cell 의 마커/PYTHONPATH 누수 방지)
    for seam_env in ("PYTHONPATH", "GH_SHIM_MARKER", "GH_SHIM_STDOUT"):
        env.pop(seam_env, None)
    # 특정 env 만 설정
    env.update(env_override)
    # worktree-location-guard 는 TIER=block 동반 (deny path 진입 조건)
    if hook_name == "worktree-location-guard":
        env["WORKTREE_LOCATION_GUARD_TIER"] = "block"

    rc, _stdout, stderr = run_hook_bash(
        hook_name, json.dumps(payload).encode("utf-8"), env=env
    )
    return rc, stderr


def test_gh_shim_seam_standalone(tmp_path):
    """사다리 ①: seam 자체 실증 (훅과 무관하게 gh 호출이 가로채지는가).

    hook 을 거치지 않고 python 자식 프로세스에서 직접 `gh pr list` 를 호출해
    (a) canned JSON 이 돌아오고 (b) 마커가 생성되는지 확인한다.
    이 테스트가 실패하면 아래 branch-gate cell 들의 관측은 의미가 없다.
    """
    env_extra, marker = _make_gh_seam(tmp_path)
    env = os.environ.copy()
    env.update(env_extra)

    probe = (
        "import json, subprocess\n"
        "r = subprocess.run(['gh','pr','list','--head','develop','--state','open',"
        "'--json','number,title'], capture_output=True, text=True)\n"
        "print(r.returncode); print(r.stdout.strip())\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=60,
    )
    out_lines = result.stdout.strip().splitlines()

    assert marker.exists(), (
        "seam 무효 — gh 호출이 가로채지지 않았다 (마커 미생성). "
        f"PATH 상 실 gh 가 응답했을 수 있음.\nstdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert out_lines and out_lines[0] == "0", f"shim rc 비정상: {result.stdout!r}"
    assert json.loads(out_lines[1]) == json.loads(GH_SHIM_OPEN_PR), (
        f"shim stdout 이 canned JSON 과 불일치: {out_lines[1]!r}"
    )


@pytest.mark.parametrize(
    "gate_key,bypass_env_name",
    [
        (gate, BYPASS_ENVS[gate])
        for gate in BYPASS_ENVS.keys()
    ]
)
def test_bypass_env_own_gate_exits_zero(gate_key: str, bypass_env_name: str, tmp_path):
    """INV-B1 대각 cell (4): 자기 게이트의 bypass env=1 → exit 0.

    branch-gate 는 gh seam 을 동반한다. seam 없이도 exit 0 이 나오지만(실 gh 가
    'develop 에 열린 PR 없음'을 돌려줘 fail-open) 그건 **판별력 0 의 공허한 통과**다
    — bypass 가 고장나도 통과하기 때문. seam 으로 "열린 PR 있음"을 고정해야
    exit 0 이 오직 bypass 때문임이 확정된다 (대조군 = 사전조건 cell 의 exit 2).
    """
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    env_override = {bypass_env_name: "1"}
    marker = None
    if gate_key == "git-branch-delete-merge-gate":
        seam_env, marker = _make_gh_seam(tmp_path)
        env_override.update(seam_env)

    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    assert rc == 0, (
        f"Gate {gate_key} with {bypass_env_name}=1 should exit 0, got {rc}\n"
        f"stderr: {stderr}"
    )

    if marker is not None:
        # 대각 cell 에서는 bypass 가 gh 조회 **이전에** 단락시키므로 마커가 없는 것이
        # 정상이다 (.py main(): BYPASS 검사 → return 0 이 _open_prs_for_branch 보다 앞).
        # 마커 부재 + bypass audit 줄 = "gh 를 아예 안 물었다" 는 더 강한 관측.
        assert not marker.exists(), (
            "대각 cell 인데 gh 가 조회됐다 — bypass 가 gh 호출보다 뒤에서 처리됨"
        )
        assert "BYPASS_BRANCH_DELETE_MERGE_GATE=1" in stderr, (
            f"bypass audit 줄 부재 — 실제로 bypass 경로를 탔는지 불명. stderr: {stderr}"
        )


@pytest.mark.parametrize(
    "gate_key",
    list(BYPASS_ENVS.keys())  # 4 게이트 전부 (branch-gate 는 gh seam 동반 — 제외 해제)
)
@pytest.mark.parametrize(
    "other_bypass_idx",
    [0, 1, 2]  # 타 3개 bypass env
)
def test_bypass_env_other_gate_denies(gate_key: str, other_bypass_idx: int, tmp_path):
    """INV-B1 비대각 cell (12): 타 게이트의 bypass env=1 → 자기 게이트 deny (exit 2).

    git-branch-delete-merge-gate 는 gh mock-seam 동반 (위 seam 주석 참조).
    마커 assert 로 "실 gh 폴백이 아니라 shim 응답으로 deny 했음"을 고정한다.
    """
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    gate_keys = list(BYPASS_ENVS.keys())
    other_gates = [k for k in gate_keys if k != gate_key]

    # 구 코드는 여기서 pytest.skip 했다 — 게이트 4종 ⇒ other_gates 는 항상 3, idx 는
    # 항상 {0,1,2} 이므로 **도달 불가** 분기였고, 만에 하나 축이 줄면 cell 을 조용히
    # 삼켜 12 cell 이 소리 없이 축소된다. fail-closed assert 로 전환한다.
    assert other_bypass_idx < len(other_gates), (
        f"타 게이트 {len(other_gates)}종 < idx {other_bypass_idx} — 비대각 축 정의 오류 "
        f"(cell 을 skip 으로 삼키지 않고 실패시킨다)"
    )

    other_gate = other_gates[other_bypass_idx]
    other_bypass_env = BYPASS_ENVS[other_gate]

    env_override = {other_bypass_env: "1"}
    marker = None
    if gate_key == "git-branch-delete-merge-gate":
        seam_env, marker = _make_gh_seam(tmp_path)
        env_override.update(seam_env)

    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    # Deny payload: 타 env는 무시, 본 게이트는 여전히 차단
    assert rc == 2, (
        f"Gate {gate_key} with {other_bypass_env}=1 (wrong env) should exit 2, got {rc}\n"
        f"stderr: {stderr}"
    )

    if marker is not None:
        assert marker.exists(), (
            "gh mock-seam 미사용 — 마커 부재. deny 가 shim 응답이 아니라 실 gh "
            f"응답/폴백에서 나왔을 수 있어 관측이 무효다.\nstderr: {stderr}"
        )


def test_bypass_env_unset_denies():
    """INV-B1: bypass env 미설정 → deny (exit 2)."""
    gate_key = "cross-repo-gh-safety"
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    env_override = {}  # 모두 미설정
    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    assert rc == 2, (
        f"Gate {gate_key} without bypass env should exit 2, got {rc}\n"
        f"stderr: {stderr}"
    )


def test_precondition_deny_without_bypass_env(tmp_path):
    """사전 조건 (4 게이트 전부): deny payload + bypass env 0 → exit 2.

    대각 cell 의 exit 0 이 "bypass 때문"임을 말하려면, 같은 payload 가 bypass 없이는
    실제로 차단된다는 대조군이 있어야 한다. 이게 없으면 대각 cell 은 공허하다.

    git-branch-delete-merge-gate 도 gh mock-seam 동반으로 포함한다 (제외 해제).
    """
    for gate_key in DENY_PAYLOADS.keys():
        payload = DENY_PAYLOADS[gate_key]
        hook_name = HOOK_NAMES[gate_key]

        env_override = {}
        marker = None
        if gate_key == "git-branch-delete-merge-gate":
            seam_env, marker = _make_gh_seam(tmp_path / gate_key)
            env_override.update(seam_env)

        # env 0개 (worktree-guard 는 TIER=block 동반)
        rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

        assert rc == 2, (
            f"Precondition failed: Gate {gate_key} with deny payload (no bypass env) "
            f"should exit 2, got {rc}. stderr: {stderr}"
        )

        if marker is not None:
            assert marker.exists(), (
                "gh mock-seam 미사용 — 마커 부재. 실 gh 폴백 의심 (관측 무효).\n"
                f"stderr: {stderr}"
            )


#   parametrize introspect 헬퍼는 hook_runner_cfp2965.parametrize_argvalues (공용).
#   구 커버리지 assert 는 기대값을 BYPASS_ENVS 에서 재유도한 뒤 BYPASS_ENVS 와
#   비교했다 — 자기 자신을 비교하는 항진명제라, parametrize 목록에서 게이트를
#   빼도(과거 branch-gate 제외 회귀 그대로) 늘 통과한다. 실 파라미터 소스를
#   데코레이터에서 직접 읽어야 축소가 검출된다.
_parametrize_argvalues = parametrize_argvalues


def test_16cell_matrix_coverage_complete():
    """16-cell 커버리지 완결 assert (제외 0 — AC-20).

    판정 소스 = 두 테스트 함수에 붙은 parametrize 데코레이터 **실물**.
    어느 축에서든 게이트를 빼면 여기서 깨진다 (조용한 cell 축소 불가).
    """
    gates = set(BYPASS_ENVS.keys())
    assert len(gates) == 4, f"게이트 4종 기대, 실제 {len(gates)}"

    # --- 대각 4 cell: (gate, own_env) 쌍을 실 파라미터에서 회수
    diagonal = _parametrize_argvalues(
        test_bypass_env_own_gate_exits_zero, "gate_key,bypass_env_name"
    )
    assert len(diagonal) == 4, f"대각 4 cell 기대, 실제 {len(diagonal)}"
    diagonal_gates = {g for g, _ in diagonal}
    assert diagonal_gates == gates, (
        f"대각 cell 에서 빠진 게이트 존재: {sorted(gates - diagonal_gates)}"
    )
    for gate_key, env_name in diagonal:
        assert env_name == BYPASS_ENVS[gate_key], (
            f"대각 cell env 오배선: {gate_key} → {env_name} "
            f"(기대 {BYPASS_ENVS[gate_key]})"
        )

    # --- 비대각 12 cell: gate 축 × other_bypass_idx 축 (둘 다 실 파라미터)
    off_gates = _parametrize_argvalues(test_bypass_env_other_gate_denies, "gate_key")
    off_idx = _parametrize_argvalues(
        test_bypass_env_other_gate_denies, "other_bypass_idx"
    )
    assert set(off_gates) == gates, (
        f"비대각 축에서 빠진 게이트 존재: {sorted(gates - set(off_gates))}"
    )
    assert sorted(off_idx) == [0, 1, 2], f"타 env 3종 축이 아님: {off_idx}"
    off_diagonal_count = len(off_gates) * len(off_idx)
    assert off_diagonal_count == 12, f"비대각 12 기대, 실제 {off_diagonal_count}"

    assert len(diagonal) + off_diagonal_count == 16, "16-cell 미완결"

    # branch-gate 가 어느 축에서도 제외되지 않았는지 명시 확인 (AC-20 회귀 방지)
    assert "git-branch-delete-merge-gate" in diagonal_gates
    assert "git-branch-delete-merge-gate" in set(off_gates), (
        "branch-gate 가 비대각 축에서 제외됨 — AC-20 회귀 (gh seam 배선 확인)"
    )


def test_coverage_assert_is_not_tautological():
    """위 커버리지 assert 가 **실 파라미터**를 읽는다는 것의 실증 (판별력 self-test).

    parametrize 가 축소된 가짜 함수를 넣으면 반드시 깨져야 한다. 구현이 다시
    BYPASS_ENVS 재유도(항진)로 퇴행하면 이 테스트가 잡는다.
    """

    @pytest.mark.parametrize(
        "gate_key,bypass_env_name",
        [(g, BYPASS_ENVS[g]) for g in BYPASS_ENVS if g != "git-branch-delete-merge-gate"],
    )
    def _shrunk(gate_key, bypass_env_name):  # pragma: no cover - 실행 대상 아님
        pass

    recovered = _parametrize_argvalues(_shrunk, "gate_key,bypass_env_name")
    assert len(recovered) == 3, "introspect 가 실 파라미터를 읽지 못함"
    assert "git-branch-delete-merge-gate" not in {g for g, _ in recovered}, (
        "축소된 파라미터인데 게이트가 살아있다 — introspect 아닌 재유도 의심"
    )
