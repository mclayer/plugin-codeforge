"""보안 lane iter1 **S-2** — 원장 목적지는 정책 채널이지 실값 채널이 아니다.

두 갈래를 고정한다.

**(1) args-file 이 목적지를 결정할 수 없다.** `_ARGS_FILE_DENIED_KEYS` 는 gate flag 2종만
막고 있었다. 그래서 args-file 이 `{"ledger-path": "...\\pwned.jsonl"}` 를 실으면 CLI 가
목적지를 지정하지 않았는데도 원장이 **통째로 다른 파일로 바꿔치기**된다(`storage-path` 도 동일).
args-file 은 계약상 "측정 실값 채널" 이다 — 어디에 쓸지는 CLI flag 또는 project config 만
결정한다(F-CR-009 와 동일 논리, 대상만 목적지 축으로 확장).

**(2) 프로젝트 밖 목적지는 default 로 강등된다.** `_resolve_storage_path` 의 escape 검사는
"best-effort" 라는 주석만 있고 실제 검사는 없었다 — `--storage-path ..\\..\\elsewhere` 가
그대로 통과한다. realpath/commonpath 로 containment 를 확인하고, 벗어나면 default 경로로
강등하되 **WARN 으로 보이게** 한다.

불변: append 경로는 **exit-0 / never-block**(ADR-115) — 목적지 거부는 "실패" 가 아니라
정책 경로로의 강등이다. 따라서 비-0 exit 를 기대하지 않고, **row 는 여전히 기록**돼야 한다.

production 로직 재구현 금지 — 실제 `append_spawn_event.py` CLI(run_append) 호출로만 판정.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
APPEND_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_spawn_event.py"


def _default_ledger(proj):
    """`${CLAUDE_PROJECT_DIR}/.claude/ledger/spawn-event.jsonl` (정책 default 목적지)."""
    return proj / ".claude" / "ledger" / "spawn-event.jsonl"


def _write_args_file(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _setup_project(tmp_path, monkeypatch):
    proj = tmp_path / "proj"
    proj.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(proj))
    return proj


_BASE_PAYLOAD = {
    "story-key": "CFP-2850",
    "lane-label": "구현",
    "agent-type": "DeveloperAgent",
    "session-id": "sess-dest",
    "agent-id": "agent-dest",
    "spawn-seq": "1",
}


# ───────────── (1) args-file 은 목적지를 지정할 수 없다 ─────────────


def test_argsfile_cannot_redirect_ledger_path(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(disc) args-file 의 `ledger-path` 는 병합 거부 + WARN — 원장 바꿔치기 불가.

    discriminating: `ledger_path` 를 denied set 에서 빼면 escape 파일이 생성돼 RED.
    """
    proj = _setup_project(tmp_path, monkeypatch)
    escape = tmp_path / "escape" / "pwned.jsonl"
    args_file = _write_args_file(
        tmp_path / "args-ledger.json", dict(_BASE_PAYLOAD, **{"ledger-path": str(escape)})
    )

    res = run_append(None, opt_in=True, args_file=str(args_file))  # CLI 는 목적지 미지정

    # 측정 assertion (a): never-block (거부는 실패가 아님)
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # (b): args-file 이 지정한 목적지에 **아무것도 생기지 않는다** — 핵심 봉인
    assert not escape.exists(), (
        f"args-file 의 ledger-path 로 원장이 바꿔치기됨 — 목적지 정책이 실값 채널로 결정됨: {escape}"
    )
    # (c): 무음 무시 아님 — 거부가 stderr 로 식별 가능
    assert "WARN" in res.stderr and (
        "ledger_path" in res.stderr or "ledger-path" in res.stderr
    ), f"목적지 병합 거부가 stderr 로 표면화돼야 함 — stderr={res.stderr!r}"
    # (d): row 는 정책 default 경로에 정상 기록 (거부가 계측을 죽이지 않음)
    default_path = _default_ledger(proj)
    assert len(read_rows(default_path)) == 1, (
        f"거부 후에도 row 는 정책 default 경로에 기록돼야 함: {default_path}"
    )


def test_argsfile_cannot_redirect_storage_path(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(disc) args-file 의 `storage-path` 도 병합 거부 + WARN (parent-dir override 축).

    discriminating: `storage_path` 를 denied set 에서 빼면 escape 디렉터리에 원장이 생겨 RED.
    """
    proj = _setup_project(tmp_path, monkeypatch)
    escape_dir = tmp_path / "escape2"
    args_file = _write_args_file(
        tmp_path / "args-storage.json", dict(_BASE_PAYLOAD, **{"storage-path": str(escape_dir)})
    )

    res = run_append(None, opt_in=True, args_file=str(args_file))

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion: escape 디렉터리에 원장 미생성
    assert not (escape_dir / "spawn-event.jsonl").exists(), (
        f"args-file 의 storage-path 로 원장 부모 디렉터리가 바꿔치기됨: {escape_dir}"
    )
    assert "WARN" in res.stderr and (
        "storage_path" in res.stderr or "storage-path" in res.stderr
    ), f"storage-path 병합 거부가 stderr 로 표면화돼야 함 — stderr={res.stderr!r}"
    assert len(read_rows(_default_ledger(proj))) == 1, "거부 후에도 row 는 default 경로에 기록"


# ───────────── (2) 프로젝트 밖 목적지 → default 강등 ─────────────


def test_storage_path_outside_allowed_roots_downgrades_to_default(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(disc) 허용 root 밖을 가리키는 `--storage-path` → default 강등 + WARN.

    args-file 을 막아도 CLI 축이 열려 있으면 containment 는 여전히 없다. realpath/commonpath
    검사가 없으면 escape 디렉터리에 원장이 생겨 RED.

    ★허용 root 는 `CLAUDE_PROJECT_DIR | repo root | OS 임시 디렉터리` 3종이다. pytest 의
    `tmp_path` 는 **OS 임시 디렉터리 안**이라 그대로 쓰면 carve-out 에 걸려 이 테스트가
    통째로 vacuous 해진다(무엇을 막아도 통과). 그래서 자식 프로세스의 임시 디렉터리를
    `tmp_path/fake-temp` 로 좁혀 escape 후보를 **세 root 모두의 밖**으로 밀어낸다 —
    실제 사용자 홈/시스템 경로를 건드리지 않고 결함 형상을 재현하는 유일한 hermetic 방법.
    (carve-out 자체가 살아있는지는 `test_os_temp_carveout_preserved` 가 별도로 고정.)
    """
    proj = _setup_project(tmp_path, monkeypatch)
    fake_tmp = tmp_path / "fake-temp"
    fake_tmp.mkdir()
    for var in ("TMPDIR", "TEMP", "TMP"):
        monkeypatch.setenv(var, str(fake_tmp))
    outside = tmp_path / "outside-ledger"

    res = run_append(
        None, opt_in=True, storage_path=str(outside),
        story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-esc", agent_id="agent-esc", spawn_seq="1",
    )

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion (a): 프로젝트 밖에 원장 미생성
    assert not (outside / "spawn-event.jsonl").exists(), (
        f"허용 root 밖 storage_path 가 그대로 사용됨(containment 부재): {outside}"
    )
    # (b): default 로 강등되어 row 는 살아있음 (강등이지 drop 아님)
    default_path = _default_ledger(proj)
    assert len(read_rows(default_path)) == 1, (
        f"escape 차단 후 default 경로 강등이 아니라 계측이 소실됨: {default_path}"
    )
    # (c): 강등이 무음이면 운영자가 자기 설정이 무시된 걸 모른다
    assert "WARN" in res.stderr and (
        "storage_path" in res.stderr or "storage-path" in res.stderr
    ), f"default 강등이 stderr 로 표면화돼야 함 — stderr={res.stderr!r}"


def test_storage_path_inside_project_is_honored(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(reg) 프로젝트 **안** 의 `--storage-path` 는 그대로 존중 — 과잉 차단 회귀 방어.

    containment 검사가 정상 override 까지 막으면 consumer 의 합법적 배치가 깨진다.
    이 대조군이 없으면 위 escape 테스트는 "storage_path 를 아예 무시" 하는 구현으로도
    통과해버린다(vacuous).
    """
    proj = _setup_project(tmp_path, monkeypatch)
    inside = proj / "custom" / "ledger"

    res = run_append(
        None, opt_in=True, storage_path=str(inside),
        story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-inside", agent_id="agent-inside", spawn_seq="1",
    )

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion: 프로젝트 안 override 는 요청한 자리에 그대로 착지
    rows = read_rows(inside / "spawn-event.jsonl")
    assert len(rows) == 1, (
        f"프로젝트 안 storage_path override 가 무시됨(과잉 차단) — 기대 {inside}, "
        f"stderr={res.stderr!r}"
    )
    assert rows[0]["story_key"] == "CFP-2850"


def _run_cli_in_cwd(cwd, **flags):
    """실제 append CLI 를 **지정 cwd** 에서 fork (공유 fixture 는 cwd=repo root 고정이라 별도).

    CLAUDE_PROJECT_DIR 미선언 regime 을 재현할 때 default 목적지가 `./.claude/ledger/...`
    (=cwd 상대)가 되므로, cwd 를 격리하지 않으면 **작업 트리에 원장이 생긴다**(오염 금지).
    production 재구현이 아니라 실 CLI 의 fork 지점만 바꾼다.
    """
    cmd = [sys.executable, str(APPEND_SCRIPT), "--telemetry-enabled", "--spawn-event-enabled"]
    for key, val in flags.items():
        cmd += ["--" + key.replace("_", "-"), str(val)]
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8"
    )


def test_os_temp_carveout_only_in_undeclared_regime(tmp_path, monkeypatch, read_rows):
    """(reg — honest ceiling) 경계 **미선언** regime 에서는 OS 임시 디렉터리 write 가 열려 있다.

    허용 root 정책은 두 갈래다:
      ① `CLAUDE_PROJECT_DIR` 선언 → **그것만**이 권위(임시 디렉터리 carve-out 없음).
      ② 미선언 → degraded: repo root ∪ OS 임시 디렉터리 (판정 권위가 없으니 "명백한 밖"만 차단).
    ②가 열려 있다는 사실을 테스트로 명문화하지 않으면 (a) carve-out 이 조용히 사라져
    CI/도구의 ephemeral 원장 용법이 깨지거나, (b) 반대로 "containment 가 있으니 임의 경로
    write 는 불가" 라는 **과대 주장**이 자란다. containment 는 authz 경계가 아니다 —
    호출자는 이미 임의 실행 권한을 가지며, 봉인 대상은 "설정 축 override 가 선언된 경계
    밖으로 원장을 내보내는" 경로 하나뿐이다(bounded degradation).
    """
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)  # ② 미선언 regime
    workdir = tmp_path / "cwd"  # default 목적지 격리 (작업 트리 오염 0)
    workdir.mkdir()
    scratch = tmp_path / "ci-scratch"  # OS 임시 디렉터리 안

    res = _run_cli_in_cwd(
        workdir, storage_path=str(scratch),
        story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-temp", agent_id="agent-temp", spawn_seq="1",
    )

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion: 미선언 regime 의 OS temp carve-out 은 열려 있다 (요청한 자리에 착지)
    assert len(read_rows(scratch / "spawn-event.jsonl")) == 1, (
        f"미선언 regime 의 OS 임시 디렉터리 carve-out 이 사라짐 — CI/도구의 ephemeral 원장 "
        f"용법이 깨진다. 기대 {scratch}, stderr={res.stderr!r}"
    )
    # 격리 확인: default 강등이 일어났더라도 그 목적지는 격리 cwd 안이다(작업 트리 오염 0)
    assert not (REPO_ROOT / ".claude" / "ledger" / "spawn-event.jsonl").exists(), (
        "테스트가 작업 트리에 원장을 생성함 — cwd 격리 실패(트리 오염 금지)"
    )
