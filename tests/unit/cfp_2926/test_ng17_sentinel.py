"""test_ng17_sentinel.py — CFP-2926 NG-17 (`check_parallel_work_sentinel` fail-open 제거).

계약 SSOT: Story CFP-2926 §7.8 S-2 (처방) + §8.0.8 (1) NG-17 행 (4항목 규격).

★본 게이트의 판정 semantics 는 형제 게이트와 다르다 (divergence — 오판 주의)★
  다른 NG 게이트: unknown-input → fail-closed **RED (exit 1)** `[154-AC-4]`.
  NG-17        : unknown-input → `degraded=true` → **INCONCLUSIVE (exit 3)**.
  근거 = §7.8 S-2 가 fail-closed 전환을 **명시 금지** ("가드가 작업을 막으면 우회가
  규범이 된다"). ⇒ `[154-AC-4]` 의 "fail-closed" 를 **"조용한 통과 금지"로만** 이행하고
  **"차단"으로는 이행하지 않는다**. 따라서 NG-17 에는 ★RED 경로가 없다★ —
  `test_ng17_never_emits_red` 가 그 불변식을 상시 고정한다.

검사 축 (제거된 fail-open 2건):
  (F1) `_run_git_log` 가 선행 `git fetch origin` 의 rc 를 ★완전히 버리던★ 경로
       — §7.8 말미가 "병렬 충돌 가드가 정확히 병렬도 최대 순간에 fail-open" 이라 지목한 실물.
  (F2) `mode_head_compare` 의 git 실패 → `git_fetch_failed` payload + ★exit 0★ 경로.

fixture 철학 — ★mock seam 0★:
  실패는 mock env 가 아니라 **실물 git 상태**로 만든다(존재하지 않는 remote / 삭제된
  bare repo / worktree 부재). 그래야 "seam 이 참이라 통과" 가 아니라 "실제 rc 가 참이라
  통과" 가 된다. 판별력 근거 = 각 테스트가 ★exit 0 과 exit 3 을 왕복★ 으로 대조한다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SENTINEL = REPO_ROOT / "scripts" / "lib" / "check_parallel_work_sentinel.py"

EXIT_PASS = 0
EXIT_RED = 1
EXIT_INCONCLUSIVE = 3


# --------------------------------------------------------------------------- helpers
def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """git 실행 (서명·identity 를 커밋 단위로 고정 — 호스트 전역 설정 비의존)."""
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _make_repo(tmp_path: Path, *, extra_worktrees: int = 0) -> tuple[Path, Path]:
    """hermetic git repo 생성 → (work, remote_bare).

    remote 는 로컬 bare repo(file 경로) — 네트워크 0. `origin` fetch 가 실제로 성공한다.
    """
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    _git("config", "user.email", "ng17@test.local", cwd=work)
    _git("config", "user.name", "ng17", cwd=work)
    _git("config", "commit.gpgsign", "false", cwd=work)
    (work / "seed.txt").write_text("seed\n", encoding="utf-8", newline="\n")
    _git("add", "seed.txt", cwd=work)
    _git("commit", "-qm", "init", cwd=work)
    _git("remote", "add", "origin", str(remote), cwd=work)
    _git("push", "-q", "origin", "HEAD:refs/heads/main", cwd=work)
    for i in range(extra_worktrees):
        _git("worktree", "add", "-q", str(tmp_path / f"wt{i}"), "-b", f"wt{i}", cwd=work)
    return work, remote


def _break_origin(work: Path, tmp_path: Path) -> None:
    """origin 을 실재하지 않는 경로로 재지정 → `git fetch origin` rc != 0 (실물 실패).

    remote 디렉터리 삭제 대신 set-url 을 쓰는 이유 = Windows 의 git object 파일은
    read-only 라 `shutil.rmtree` 가 PermissionError 로 죽는다(플랫폼 잡음). set-url 은
    양 플랫폼 결정론이고, 만드는 실패도 동일하게 "원격 해소 불가" 다.
    """
    _git("remote", "set-url", "origin", str(tmp_path / "absent-remote.git"), cwd=work)


def _run_gate(*args: str, cwd: Path | None = None, env_extra: dict | None = None):
    """NG-17 게이트/모드를 ★subprocess 로★ 실행 → (rc, payload_dict, raw_stdout).

    함수 직접 호출이 아니라 실 CLI 경로로 도는 이유 = exit code 자체가 판정면이기 때문.
    """
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(SENTINEL), *args],
        cwd=str(cwd) if cwd else str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    payload = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
    return proc.returncode, payload, proc.stdout


# --------------------------------------------------------------------------- ⓐ fetch 실패
def test_ng17_fetch_failure_declares_inconclusive_not_pass(tmp_path):
    """ⓐ `git fetch` rc != 0 → degraded=true → ★exit 3★ (exit 0 아님).

    ★2-exit-differ 왕복★: 같은 repo·같은 명령에서 remote 만 바꿔 0 ↔ 3 을 대조한다.
    (항상-3 반환기와 구별 — negative control 이 같은 테스트 안에 있다.)
    """
    work, _remote = _make_repo(tmp_path, extra_worktrees=1)

    rc_bad, payload_bad, _ = _run_gate(
        "--repo-root", str(work), "--remote", "no-such-remote-xyz"
    )
    assert rc_bad == EXIT_INCONCLUSIVE, f"fetch 실패가 exit {rc_bad} 로 흡수됨 (fail-open 잔존)"
    assert payload_bad["verdict"] == "INCONCLUSIVE"
    assert payload_bad["trace"]["degraded"] is True
    assert payload_bad["trace"]["fetch_rc"] not in (0, None)
    assert payload_bad["reason"].startswith("fetch_rc_nonzero")

    # negative control — 정상 remote 면 같은 경로가 exit 0
    rc_ok, payload_ok, _ = _run_gate("--repo-root", str(work))
    assert rc_ok == EXIT_PASS, f"정상 remote 인데 exit {rc_ok} (항상-INCONCLUSIVE 반환기 의심)"
    assert payload_ok["verdict"] == "PASS"
    assert payload_ok["trace"]["degraded"] is False
    assert payload_ok["trace"]["fetch_rc"] == 0


def test_ng17_unknown_fetch_rc_declares_inconclusive(tmp_path):
    """ⓐ' fetch rc ★미지★(미실행) → degraded=true → exit 3. "미지 = 성공" 승격 금지."""
    work, _ = _make_repo(tmp_path, extra_worktrees=1)
    rc, payload, _ = _run_gate("--repo-root", str(work), "--skip-fetch")
    assert rc == EXIT_INCONCLUSIVE
    assert payload["reason"] == "fetch_rc_unknown"
    assert payload["trace"]["fetch_rc"] is None
    assert payload["trace"]["degraded"] is True


# --------------------------------------------------------------------------- ⓑ empty-target
def test_ng17_zero_comparison_worktree_declares_inconclusive(tmp_path):
    """ⓑ 대조 worktree 0개 → ★exit 3★. `0 == 0` 을 "충돌 없음"으로 읽지 않는다 [154-AC-3].

    ★왕복★: 동일 repo 에 worktree 를 1개 붙이면 같은 명령이 exit 0 으로 뒤집힌다
    ⇒ "worktree 수" 가 실제 load-bearing 임을 대조로 증명(선언 아님).
    """
    work, _ = _make_repo(tmp_path, extra_worktrees=0)
    rc0, payload0, _ = _run_gate("--repo-root", str(work))
    assert rc0 == EXIT_INCONCLUSIVE, "대조 worktree 0 이 통과로 흡수됨 (vacuous pass)"
    assert payload0["reason"] == "no_comparison_worktree"
    assert payload0["trace"]["comparison_worktree_count"] == 0
    assert payload0["trace"]["fetch_rc"] == 0, "fetch 는 성공했어야 empty-target 축이 분리 검증됨"

    _git("worktree", "add", "-q", str(tmp_path / "wt-late"), "-b", "wt-late", cwd=work)
    rc1, payload1, _ = _run_gate("--repo-root", str(work))
    assert rc1 == EXIT_PASS
    assert payload1["trace"]["comparison_worktree_count"] == 1


def test_ng17_unparseable_worktree_enumeration_declares_inconclusive(tmp_path):
    """ⓑ' worktree 열거 불가(비-git 디렉터리) → degraded → exit 3 (exit 0/1 아님)."""
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    rc, payload, _ = _run_gate("--repo-root", str(plain), "--skip-fetch")
    assert rc == EXIT_INCONCLUSIVE
    assert payload["trace"]["degraded"] is True
    assert payload["trace"]["comparison_worktree_count"] is None


# --------------------------------------------------------------------------- ⓒ divergence 불변식
def test_ng17_never_emits_red(tmp_path):
    """★divergence 불변식★ — NG-17 은 어떤 입력에서도 RED(exit 1)/차단을 내지 않는다.

    §7.8 S-2 "fail-closed 전환은 금지". 이 테스트가 없으면 후속 회전이 형제 게이트와의
    '일관성' 을 명분으로 RED 로 승격시켜 **가드가 작업을 막고 → 우회가 규범이 되는**
    회귀를 만든다. 관측된 exit 는 {0, 3} 뿐이어야 한다.
    """
    work, _remote = _make_repo(tmp_path, extra_worktrees=1)
    plain = tmp_path / "plain"
    plain.mkdir()
    _break_origin(work, tmp_path)  # 원격 해소 불가 — fetch rc != 0

    observed = set()
    for args in (
        ("--repo-root", str(work)),                                   # fetch 실패
        ("--repo-root", str(work), "--skip-fetch"),                   # rc 미지
        ("--repo-root", str(plain), "--skip-fetch"),                  # 열거 불가
        ("--repo-root", str(work), "--remote", "bogus-remote"),       # remote 부재
    ):
        rc, _payload, _ = _run_gate(*args)
        observed.add(rc)
    assert observed <= {EXIT_PASS, EXIT_INCONCLUSIVE}, (
        f"NG-17 이 {observed} 를 냈다 — exit 1(RED)/차단은 §7.8 S-2 명시 금지"
    )
    assert EXIT_RED not in observed


def test_ng17_divergence_is_declared_in_module_docstring():
    """docstring 에 divergence declare 존재 — ★presence 검사이지 참임의 증명이 아니다★.

    실 판정 semantics 의 teeth 는 위 행위 테스트들이 쥔다. 본 테스트는 "다음 리뷰어가
    NG-17 을 일관성 위반으로 오판" 하는 것을 막는 문면 앵커만 고정한다(§8.0.8 인용 +
    §7.8 S-2 사유). 문면과 행위가 갈라지면 위 행위 테스트가 먼저 깨진다.
    """
    src = SENTINEL.read_text(encoding="utf-8")
    assert 'GATE_ID = "NG-17"' in src
    for anchor in ("§7.8 S-2", "§8.0.8", "divergence declare", "fail-closed"):
        assert anchor in src, f"divergence declare 앵커 누락: {anchor}"


# --------------------------------------------------------------------------- ⓓ 4항목 번들
def test_ng17_emits_trace_and_identity_probe(tmp_path):
    """[154-AC-5] trace numeric 3종 + [154-AC-13] identity_probe resolved-target echo.

    §8.0.8 NG-17 행: trace = 대조 worktree 수 · fetch rc · `degraded` 플래그 /
    probe = true — 채널 = 공유 `.git/shallow` · 원격 fetch 결과.
    """
    work, _ = _make_repo(tmp_path, extra_worktrees=2)
    rc, payload, _ = _run_gate("--repo-root", str(work))
    assert rc == EXIT_PASS
    assert payload["gate_id"] == "NG-17"

    trace = payload["trace"]
    assert trace["comparison_worktree_count"] == 2      # 검사량 (numeric)
    assert trace["fetch_rc"] == 0                        # fetch rc
    assert trace["degraded"] is False                    # degraded 플래그

    probe = payload["identity_probe"]
    # 채널 echo — 공유 .git/shallow 실경로가 실제로 해소돼 나와야 한다 (경로 오타 = vacuous)
    assert probe["shallow_file"].endswith("/shallow")
    assert probe["git_common_dir"] != "unresolved"
    assert "shallow_exists" in probe
    assert Path(probe["git_common_dir"]).name == ".git"


# --------------------------------------------------------------------------- ⓔ F1/F2 head-compare
def test_ng17_head_compare_fetch_rc_no_longer_discarded(tmp_path):
    """(F1) ★본 개정의 실물★ — git log 는 성공하는데 `git fetch` 만 실패하는 상황.

    종전 구현은 fetch rc 를 버렸으므로 이 입력에서 ★exit 0★ 을 냈다(= 병렬도 최대 순간의
    fail-open). 개정 후 exit 3 + degraded=true.
    ★왕복★: 원격 살아있음 → exit 0 / 원격 소멸 → exit 3 (같은 명령·같은 repo).
    """
    work, _remote = _make_repo(tmp_path)
    prior = _git("rev-parse", "HEAD", cwd=work).stdout.strip()

    rc_ok, payload_ok, _ = _run_gate(
        "--mode", "head-compare-sibling-commits", "--branch", "HEAD",
        cwd=work, env_extra={"CFP_PRIOR_SHA": prior},
    )
    assert rc_ok == EXIT_PASS
    assert payload_ok["fetch_rc"] == 0
    assert payload_ok["degraded"] is False

    _break_origin(work, tmp_path)  # 원격만 해소 불가 — git log 는 여전히 rc 0
    rc_bad, payload_bad, _ = _run_gate(
        "--mode", "head-compare-sibling-commits", "--branch", "HEAD",
        cwd=work, env_extra={"CFP_PRIOR_SHA": prior},
    )
    assert rc_bad == EXIT_INCONCLUSIVE, (
        f"fetch 실패인데 exit {rc_bad} — `git fetch` rc 를 버리는 fail-open 이 잔존한다"
    )
    assert payload_bad["degraded"] is True
    assert payload_bad["fetch_rc"] not in (0, None)


def test_ng17_head_compare_git_failure_declares_inconclusive(tmp_path):
    """(F2) git log 실패 → 종전 `git_fetch_failed` payload + ★exit 0★ → 개정 exit 3.

    payload 키(delta_commits/parallel_detected/degradation/marker)는 ★전건 보존★ —
    하위 parser 무손상. 바뀐 것은 exit code 와 승격 필드(degraded/verdict)뿐이다.
    """
    work, _ = _make_repo(tmp_path)
    rc, payload, _ = _run_gate(
        "--mode", "head-compare-sibling-commits", "--branch", "HEAD",
        cwd=work, env_extra={"CFP_PRIOR_SHA": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"},
    )
    assert rc == EXIT_INCONCLUSIVE, f"git log 실패가 exit {rc} 로 흡수됨"
    assert payload["degradation"] == "git_fetch_failed"       # 기존 키 보존
    assert payload["marker"] == "[parallel-work-sentinel-api-failed]"
    assert payload["delta_commits"] == []
    assert payload["parallel_detected"] is False
    assert payload["degraded"] is True                        # 승격 필드
    assert payload["verdict"] == "INCONCLUSIVE"


# --------------------------------------------------------------------------- ⓕ 비회귀 경계
@pytest.mark.parametrize("mode", ["title-search", "epic-state-poll"])
def test_ng17_does_not_touch_gh_channel_modes(mode, tmp_path):
    """★NG-17 이 손대지 않는 축의 명시 고정★ — gh 채널 degrade 는 exit 0 유지.

    NG-17 의 선언 채널은 공유 `.git/shallow` · 원격 fetch 결과다. gh API 채널의
    honest-degrade(CFP-2723 설계, 기존 회귀 스위트가 exit 0 을 고정)는 본 개정 대상이
    아니며, 여기서 **의도된 비대상**임을 코드로 못박는다(조용한 scope 확대 방지).
    """
    fixture = tmp_path / "payload.json"
    fixture.write_text("not-json-at-all", encoding="utf-8", newline="\n")
    args = ["--mode", mode]
    if mode == "epic-state-poll":
        args += ["--epic-id", "100"]
    rc, payload, _ = _run_gate(
        *args, env_extra={"CFP967_GH_MOCK_RESPONSE": str(fixture)}
    )
    assert rc == EXIT_PASS, f"{mode} gh degrade 가 exit {rc} 로 바뀜 — NG-17 scope 이탈"
    assert payload["degradation"] == "gh_payload_invalid"
