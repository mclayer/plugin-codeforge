"""test_ng12_hook_merge.py — CFP-2926 NG-12 hook 병합 게이트 명명 테스트 3종.

계약 SSOT: Story CFP-2926 §7.7.1 (H-1 분할선) · §7.7.2 (H-2 병합 + H-2′ 등록면) ·
           §8.0.1 tier 표 (T1 / ★migration★) · §8.0.2 RTM (hook 병합 3행) ·
           §8.0.8 (1) NG-12 행.

RTM 명명 테스트 (이름 변경 금지 — `ac-traceability` Hop3 가 symbol 실재를 대조):
  ① `test_hook_merge_each_gate_still_blocks`        tier=T1        mutant=M-F
  ② `test_hook_merge_matcher_registration_alive`    tier=T1        mutant=M-F′
  ③ `test_hook_merge_matcher_union_preserved`       tier=★migration★ (병합 PR 1회 한정)

★왜 "실 도구 호출 경유 end-to-end" 인가 (§7.7.2 규정 ①)★
  차단 4종은 개별 matcher 가 아니라 `hooks.json` PreToolUse 의 ★단일 `"matcher": "Bash"`
  블록 하나★ 를 공유한다 ⇒ 그 한 줄이 좁아지면 4 가드가 **동시에** 죽는다. 그런데 검사
  함수를 직접 import 해 호출하는 테스트는 등록면을 **정의상 관측하지 못하므로** 4개 모두
  GREEN 을 낸다(= ADR-154 §결정 2 `silent-green`). ⇒ 본 파일은 함수 직접 호출을 금하고,
  `hooks.json` 의 matcher 를 **해석**해 나온 command 문자열을 **그대로 실행**한다.

★관측 상한 (over-claim 금지)★
  본 테스트는 harness 자체를 구동하지 못한다. 관측 가능한 것은
  ⓐ `hooks.json` 등록면 해석 결과 ⓑ 해석돼 나온 command 의 실제 실행 결과(exit 2 = block)
  까지다. "하네스가 실제로 이 hook 을 호출한다"는 여기서 증명되지 않는다(플랫폼 소관).
  또한 §7.7.2 정직 조항대로 "차단 판정 자체가 옳은가"의 **완전성**은 보증 밖이다
  (ADR-154 §결정 4 INV-5 — detection sufficiency undecidable).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS_JSON = REPO_ROOT / "hooks" / "hooks.json"
NG12_MODULE = REPO_ROOT / "scripts" / "lib" / "check_hook_merge_registration.py"

# §7.7.1 H-1 분할선 — ★차단 4종★ (임계경로 유지 의무, 비동기화 = 차단 아님)
BLOCKING_HOOKS = (
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
)

EXIT_PASS, EXIT_RED, EXIT_INCONCLUSIVE = 0, 1, 3
PRETOOLUSE_BLOCK_RC = 2  # Claude Code PreToolUse 계약: exit 2 + stderr = block

# ★실행 제외 (해석 대상에서는 제외하지 않음)★
#   `pretooluse-dev-process-capture` 는 matcher `Agent|Bash|Write|Edit|MultiEdit` 라
#   Bash 해석 집합에 들어오지만, 발화하면 `dev_process_hook_capture.record_hook_event`
#   가 원장에 행을 append 한다 — 그 원장이 곧 본 Story 의 AC-14·AC-15 관측면이므로
#   테스트가 실행하면 ★증거 평면을 오염★ 시킨다(§7.7.1 이 H-2 최적화 대상에서도 명시
#   제외한 바로 그 hook). ⇒ 등록면 해석에는 남기고 **실행만** 건너뛴다.
_EXCLUDE_FROM_EXECUTION = {"pretooluse-dev-process-capture"}

_BASH = shutil.which("bash")

# Windows Python 의 subprocess(['gh',...]) 는 CreateProcess 라 `.exe` 만 해소한다 —
# extensionless sh 스텁도 `.cmd` 도 잡히지 않고 **실 gh** 가 PATH 뒤에서 선택된다
# (본 워커 firsthand 실측: 스텁 dir 를 PATH 선두에 둬도 `gh version 2.91.0` 응답).
# 선례 = hooks/tests/test_git_branch_delete_merge_gate.py 의 `_requires_posix_gh_stub`.
_requires_posix_gh_stub = pytest.mark.skipif(
    os.name == "nt",
    reason="gh sh-stub 은 POSIX shebang 의존 — Windows CreateProcess 미해소 (CI=POSIX 에서 실행)",
)
_requires_bash = pytest.mark.skipif(
    _BASH is None, reason="hooks.json command 실행에 bash 필요 (polyglot run-hook.cmd)"
)


# ═══════════════════════════════════════════════ 등록면 해석 (dispatch-faithful resolver)
def load_hooks_json(path: Path | None = None) -> dict:
    return json.loads((path or HOOKS_JSON).read_text(encoding="utf-8"))


def _matcher_matches(matcher, tool_name: str) -> bool:
    """하네스 matcher 의미론 근사 — ★정규식 매칭★ (문자열 상등 아님).

    기존 prior art `hooks/tests/test_hooks_json_topology.py::_matcher_hook_names` 는
    `entry.get("matcher") == matcher` 상등 비교라 `"Agent|Bash|Write"` 같은 **병합형**
    matcher 를 놓친다. H-2 병합 후에는 matcher 형상이 바뀔 수 있으므로 여기서는
    상등이 아니라 **해석**해야 판별력이 유지된다(그래서 cross-import 대신 재도출).
    """
    if matcher is None or matcher == "" or matcher == "*":
        return True
    if isinstance(matcher, list):
        return any(_matcher_matches(m, tool_name) for m in matcher)
    if not isinstance(matcher, str):
        return False
    try:
        return re.fullmatch(matcher, tool_name) is not None
    except re.error:
        return matcher == tool_name


def resolve_commands(hooks_data: dict, tool_name: str) -> list[str]:
    """PreToolUse 에서 `tool_name` 에 대해 ★실제로 발화될★ command 문자열 목록."""
    hooks_obj = hooks_data.get("hooks", hooks_data)
    entries = hooks_obj.get("PreToolUse") or []
    if isinstance(entries, dict):
        entries = [entries]
    out: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if not _matcher_matches(entry.get("matcher"), tool_name):
            continue
        for hook in entry.get("hooks") or []:
            cmd = hook.get("command") if isinstance(hook, dict) else None
            if isinstance(cmd, str) and cmd.strip():
                out.append(cmd)
    return out


def hook_name_of(command: str) -> str:
    """`"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" <name>` → `<name>`."""
    return command.split()[-1].strip('"').strip("'")


def matcher_tokens_for(hooks_data: dict, hook_names: set) -> set:
    """`hook_names` 중 하나라도 등록된 PreToolUse 블록의 matcher 토큰 합집합."""
    hooks_obj = hooks_data.get("hooks", hooks_data)
    entries = hooks_obj.get("PreToolUse") or []
    if isinstance(entries, dict):
        entries = [entries]
    tokens: set = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        registered = {
            hook_name_of(h["command"])
            for h in (entry.get("hooks") or [])
            if isinstance(h, dict) and isinstance(h.get("command"), str)
        }
        if not (registered & hook_names):
            continue
        matcher = entry.get("matcher")
        if isinstance(matcher, str):
            tokens |= {t for t in matcher.split("|") if t}
        elif isinstance(matcher, list):
            tokens |= {str(t) for t in matcher}
    return tokens


# ═══════════════════════════════════════════════ 실행 (registered command → subprocess)
def _run_registered_command(command: str, payload: dict, env_extra: dict | None = None):
    """등록된 command 문자열을 실행 → (rc, stderr). rc 2 = PreToolUse block.

    `${CLAUDE_PLUGIN_ROOT}` 만 확장하고 경로·인자는 등록된 문자열 그대로 쓴다.

    ★polyglot 진입점은 bash 쪽을 쓴다 (Windows 실측 근거)★
      `hooks/run-hook.cmd` 는 polyglot 이다 — 1행 `:; exec bash "$(dirname "$0")/$f"`
      (Unix) / 그 아래 batch 본문(Windows). 본 워커 firsthand 실측에서 **Windows 의 두
      dispatch 경로(cmd.exe `/c`, Git Bash 의 `.cmd` 직접 실행)는 hook 의 `exit 2` 를
      ★0 으로 붕괴★** 시킨다(차단 메시지는 stderr 에 나오는데 rc=0). 통제 실험으로
      원인 확정: batch 의 `exit /b %ERRORLEVEL%` 가 `if exist (...)` **괄호 블록 안**에
      있어 parse-time 확장된다 (flat 배치 = rc 2 / 괄호 블록 = rc 0 실측 대조).
      ⇒ 테스트가 관측 가능한 결정론 경로 = polyglot 의 bash 진입. POSIX(CI)에서는 이것이
      곧 프로덕션 경로다. Windows cmd 분기는 **본 테스트 미커버** 이며 별도 보고 대상이다.
    """
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(REPO_ROOT).replace("\\", "/")
    if env_extra:
        env.update(env_extra)
    expanded = command.replace("${CLAUDE_PLUGIN_ROOT}", env["CLAUDE_PLUGIN_ROOT"])
    tokens = shlex.split(expanded)
    if tokens and tokens[0].endswith(".cmd"):
        argv = [_BASH, *tokens]          # polyglot Unix 진입 (1행 exec bash)
    else:
        argv = [_BASH, "-c", expanded]   # 병합 후 형상 변경 대비 (일반 셸 명령)
    proc = subprocess.run(
        argv,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(REPO_ROOT),
    )
    return proc.returncode, proc.stderr


def executable_commands(hooks_data: dict, tool_name: str) -> list[str]:
    """해석된 chain 중 ★실행해도 되는★ 것 (_EXCLUDE_FROM_EXECUTION 제외)."""
    return [
        c for c in resolve_commands(hooks_data, tool_name)
        if hook_name_of(c) not in _EXCLUDE_FROM_EXECUTION
    ]


def _dispatch(payload: dict, env_extra: dict | None = None):
    """tool_name 으로 등록면을 해석해 나온 chain 을 순차 실행. 첫 block 에서 멈춘다.

    반환 (blocked_rc_or_None, blocking_stderr, executed_command_count).
    """
    commands = executable_commands(load_hooks_json(), payload["tool_name"])
    for command in commands:
        rc, stderr = _run_registered_command(command, payload, env_extra)
        if rc == PRETOOLUSE_BLOCK_RC:
            return rc, stderr, len(commands)
    return None, "", len(commands)


def _gh_stub_dir(tmp_path: Path, stdout: str) -> Path:
    """POSIX fake `gh` — 열린 PR 1건을 결정론으로 반환 (네트워크 0)."""
    bindir = tmp_path / "fakebin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text(f"#!/bin/sh\ncat <<'GHEOF'\n{stdout}\nGHEOF\nexit 0\n",
                  encoding="utf-8", newline="\n")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return bindir


# ── 차단 4종 개별 양성 fixture (M-F) + ★동형 음성 대조★ ────────────────────────────
#    음성 대조가 없으면 "무조건 차단하는 구현" 과 구별되지 않는다.
def _scenario(hook: str, tmp_path: Path) -> dict:
    root_posix = str(REPO_ROOT).replace("\\", "/")
    if hook == "cross-repo-gh-safety":
        return {
            "marker": "[cross-repo-gh-safety] BLOCKED",
            "block": {"tool_name": "Bash",
                      "tool_input": {"command": "gh pr edit 94 --body leak"}},
            "allow": {"tool_name": "Bash",
                      "tool_input": {"command":
                                     "gh pr edit 94 --repo mclayer/plugin-codeforge --body ok"}},
            "env": {},
        }
    if hook == "repo-confinement":
        return {
            "marker": "[check_repo_confinement] BLOCKED",
            "block": {"tool_name": "Bash", "cwd": root_posix,
                      "tool_input": {"command": "echo leak > ~/cfp2926-probe.txt"}},
            "allow": {"tool_name": "Bash", "cwd": root_posix,
                      "tool_input": {"command": "echo ok > ./cfp2926-probe.txt"}},
            "env": {},
        }
    if hook == "git-branch-delete-merge-gate":
        bindir = _gh_stub_dir(tmp_path, '[{"number": 2741, "title": "probe PR"}]')
        return {
            "marker": "[branch-delete-merge-gate] BLOCKED",
            "block": {"tool_name": "Bash",
                      "tool_input": {"command": "git push origin --delete cfp-probe"}},
            "allow": {"tool_name": "Bash",
                      "tool_input": {"command": "git push origin main"}},
            "env": {"PATH": f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}"},
        }
    if hook == "worktree-location-guard":
        return {
            "marker": "[check_worktree_location_guard] BLOCKED",
            "block": {"tool_name": "Bash",
                      "tool_input": {"command":
                                     "git worktree add /tmp/cfp2926-outside -b probe"}},
            "allow": {"tool_name": "Bash",
                      "tool_input": {"command":
                                     "git worktree add ~/.claude/worktrees/cfp2926-inside -b probe"}},
            # tier 승격 env — default(warn) 대비 2-state 판별을 같은 테스트가 함께 편다.
            "env": {"WORKTREE_LOCATION_GUARD_TIER": "block"},
        }
    raise AssertionError(f"unknown scenario: {hook}")


# ═══════════════════════════════════════════════ ① T1 — M-F (검사 축, 실 도구 경유 e2e)
@_requires_bash
@pytest.mark.parametrize(
    "hook",
    [
        "cross-repo-gh-safety",
        "repo-confinement",
        pytest.param("git-branch-delete-merge-gate", marks=_requires_posix_gh_stub),
        "worktree-location-guard",
    ],
)
def test_hook_merge_each_gate_still_blocks(hook, tmp_path):
    """M-F — 병합 후 차단 4종 ★개별★ 양성 대조 (§7.7.2 규정 ①).

    각 회차는 (ⓐ 등록면 해석 → ⓑ 해석된 command 실행 → ⓒ 그 가드의 BLOCKED 마커 확인)
    을 통과해야 한다. matcher 가 좁아지면 ⓐ 에서 0 개가 나와 즉시 RED — 함수 직접
    호출로는 관측 불가능한 실패 모드다.
    병합(H-2) 전후 무관하게 성립한다: chain 전체를 돌려 "누가" 아니라 "차단되는가 +
    그 검사가 보존됐는가(마커)" 를 본다 ⇒ 단일 진입점으로 병합돼도 계약 그대로.
    """
    sc = _scenario(hook, tmp_path)

    commands = resolve_commands(load_hooks_json(), "Bash")
    assert commands, "matcher 해석 결과 0 → RED (§7.7.2 H-2′ — 등록면이 죽었다)"

    rc, stderr, resolved = _dispatch(sc["block"], sc["env"])
    assert rc == PRETOOLUSE_BLOCK_RC, (
        f"{hook}: 차단 fixture 가 통과됐다 (resolved={resolved}, rc={rc})"
    )
    assert sc["marker"] in stderr, (
        f"{hook}: 차단은 됐으나 그 가드의 검사가 아니다 — 보존 위반 (stderr={stderr[:160]!r})"
    )

    # ★음성 대조★ — 같은 가드가 정상 입력을 막지 않는다 ("무조건 차단" 구현 kill)
    rc_ok, stderr_ok, _ = _dispatch(sc["allow"], sc["env"])
    assert rc_ok is None, (
        f"{hook}: 정상 입력이 차단됐다 — 판별력 0 인 over-block (stderr={stderr_ok[:160]!r})"
    )


@_requires_bash
def test_hook_merge_worktree_guard_tier_env_is_load_bearing():
    """`WORKTREE_LOCATION_GUARD_TIER=block` 동반 assertion (env 주입 = 무근거 금지).

    위 시나리오가 env 를 export 하므로, 그 env 가 실제로 판정을 뒤집는지(warn=통과 /
    block=차단) 를 별도로 고정한다 — env 없이도 우연히 차단됐다면 위 양성 대조는
    가짜였을 것이다.
    """
    payload = {"tool_name": "Bash",
               "tool_input": {"command": "git worktree add /tmp/cfp2926-outside -b probe"}}
    rc_warn, _, _ = _dispatch(payload, {"WORKTREE_LOCATION_GUARD_TIER": "warn"})
    rc_block, stderr_block, _ = _dispatch(payload, {"WORKTREE_LOCATION_GUARD_TIER": "block"})
    assert rc_warn is None, "warn tier 인데 차단됐다 — tier env 가 판정을 지배하지 않는다"
    assert rc_block == PRETOOLUSE_BLOCK_RC
    assert "[check_worktree_location_guard] BLOCKED" in stderr_block


# ═══════════════════════════════════════════════ ② T1 — M-F′ (등록면 축, 상시)
def _invoke_ng12(*extra_args: str):
    """NG-12 모듈 1회 실행 → (rc, 단일라인 JSON payload). 인자 조합은 호출자가 정한다."""
    proc = subprocess.run(
        [sys.executable, str(NG12_MODULE), *extra_args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    payload = {}
    for line in proc.stdout.splitlines():
        if line.strip().startswith("{"):
            payload = json.loads(line.strip())
    return proc.returncode, payload


def _run_ng12(hooks_json: Path):
    """★명시 지정(override) 경로★ — 사본/mutant 를 직접 겨눌 때."""
    return _invoke_ng12("--repo-root", str(REPO_ROOT), "--hooks-json", str(hooks_json))


def _run_ng12_by_repo_root(repo_root: Path):
    """★resolve 경로★ — `--hooks-json` 없이 CI 배선(`--repo-root .`)과 동일 형상."""
    return _invoke_ng12("--repo-root", str(repo_root))


def test_hook_merge_matcher_registration_alive(tmp_path):
    """M-F′ — `hooks.json` matcher 에서 도구 1종 제거/블록 삭제 → ★각 회차 RED★.

    ★mutant 를 테스트 안에서 직접 주입★한다(수동 1회 실증이 아니라 상시 실행) —
    작업 트리는 건드리지 않고 tmp 사본에만 주입하므로 오염 0.
    """
    live = load_hooks_json()

    # (0) 기준선 — 실 hooks.json 은 Bash 를 해소하고 NG-12 가 PASS
    assert resolve_commands(live, "Bash"), "Bash matcher 해석 결과 0 (§7.7.2 H-2′ RED)"
    rc_live, payload_live = _run_ng12(HOOKS_JSON)
    assert rc_live == EXIT_PASS, f"기준선 RED: {payload_live}"
    assert payload_live["gate_id"] == "NG-12"

    # (0') 차단 4종이 그 matcher 를 통해 실제로 도달 가능한가
    #   ★정직★: 이 assert 는 **테스트 tier** 다 — NG-12 모듈 자신은 "Bash matcher 블록
    #   존재" 까지만 보고 4 hook 등록 여부는 검사하지 않는다(모듈 docstring 자인).
    resolved_names = {hook_name_of(c) for c in resolve_commands(live, "Bash")}
    missing = set(BLOCKING_HOOKS) - resolved_names
    assert not missing, f"차단 hook 이 Bash 등록면에서 도달 불가: {sorted(missing)}"

    # (1) mutant M-F′-a — matcher 에서 도구 1종("Bash") 제거 → 차단 4종 도달 불가 + NG-12 RED
    mutant_a = json.loads(json.dumps(live))
    for entry in mutant_a["hooks"]["PreToolUse"]:
        if entry.get("matcher") == "Bash":
            entry["matcher"] = "Write"          # Bash 를 matcher 에서 제거
    path_a = tmp_path / "mutant_a.json"
    path_a.write_text(json.dumps(mutant_a, ensure_ascii=False, indent=2),
                      encoding="utf-8", newline="\n")
    # ★해석 결과가 "빈 리스트" 는 아니다★ — `pretooluse-dev-process-capture` 의 matcher
    #   (`Agent|Bash|Write|Edit|MultiEdit`)가 여전히 Bash 를 덮기 때문. 그래서 판정 기준은
    #   "총 0건" 이 아니라 ★차단 4종의 도달 가능성★ 이어야 한다(총건수 기준은 오라클 결함).
    mutated_names = {hook_name_of(c) for c in resolve_commands(mutant_a, "Bash")}
    assert not (set(BLOCKING_HOOKS) & mutated_names), "matcher 축소가 해석에 반영되지 않음"
    rc_a, payload_a = _run_ng12(path_a)
    assert rc_a == EXIT_RED, f"M-F′-a 미검출 (rc={rc_a}, {payload_a})"
    assert payload_a["verdict"] == "RED"

    # (2) mutant M-F′-b — 등록 블록 자체 삭제 → NG-12 RED
    mutant_b = json.loads(json.dumps(live))
    mutant_b["hooks"]["PreToolUse"] = [
        e for e in mutant_b["hooks"]["PreToolUse"] if e.get("matcher") != "Bash"
    ]
    path_b = tmp_path / "mutant_b.json"
    path_b.write_text(json.dumps(mutant_b, ensure_ascii=False, indent=2),
                      encoding="utf-8", newline="\n")
    assert not (set(BLOCKING_HOOKS)
                & {hook_name_of(c) for c in resolve_commands(mutant_b, "Bash")})
    rc_b, payload_b = _run_ng12(path_b)
    assert rc_b == EXIT_RED, f"M-F′-b 미검출 (rc={rc_b}, {payload_b})"

    # (3) negative control — 사본을 그대로 두면 PASS (항상-RED 와 구별)
    path_c = tmp_path / "control.json"
    path_c.write_text(json.dumps(live, ensure_ascii=False, indent=2),
                      encoding="utf-8", newline="\n")
    rc_c, _ = _run_ng12(path_c)
    assert rc_c == EXIT_PASS, "무변경 사본이 RED — 항상-RED 게이트(판별력 0)"

    # (4) unknown-input fail-closed [154-AC-4] — NG-12 는 형제 게이트 규격대로 RED
    path_d = tmp_path / "broken.json"
    path_d.write_text("{ not json", encoding="utf-8", newline="\n")
    rc_d, payload_d = _run_ng12(path_d)
    assert rc_d == EXIT_RED and payload_d["verdict"] == "RED"


# ═══════════════════════════════════ ②′ born-inert 회귀 가드 (경로 되돌림 고정)
def test_ng12_real_repo_registration_channel_reaches_actual_surface(tmp_path):
    """★born-inert 회귀 가드★ — `--hooks-json` **없이** 실 repo 등록면에 도달하는지 고정.

    ★왜 위의 ② 로는 못 잡았나★: `_run_ng12` 는 항상 `--hooks-json <사본>` 을 명시 지정해
    override 분기만 탄다 ⇒ 모듈의 **기본 경로 resolve** 는 테스트 정의상 미관측이었다.
    그 사이 종전 구현은 `<repo_root>/hooks.json` (실제는 `hooks/hooks.json`) 을 봐서
    CI 배선(`--repo-root .`)에서 ★영구 `INCONCLUSIVE hooks_json_not_found`(exit 3)★ —
    `hooks.json` 을 어떻게 훼손해도 결과가 불변인 ★판별력 0★ 상태였다
    (sibling NG-16 `test_real_repo_registration_channel_reaches_actual_surface` 와 동종).

    고정 대상 3:
      ⓐ 기본 resolve 가 실 등록면(`hooks/hooks.json`)에 **도달**한다
      ⓑ resolved 경로가 `identity_probe` 에 **echo** 된다 ([154-AC-13])
      ⓒ trace 의 hook 식별자가 **실값**이다 (종전 `["unknown"]` = 정보량 0 회귀 차단)
    + 음성 대조: 후보가 하나도 없는 repo-root 는 not-found 로 갈린다 ⇒ resolve 가 실
      파일에 하드코딩된 것이 아님을 같은 테스트가 함께 편다(항상-PASS 와 구별).
    """
    rc, payload = _run_ng12_by_repo_root(REPO_ROOT)

    # ⓐ 등록면 도달 — born-inert 였다면 여기서 exit 3 / not_found 로 실패한다
    assert payload.get("reason") != "hooks_json_not_found", (
        "기본 resolve 가 실 등록면에 미도달 (born-inert 회귀): %s" % payload
    )
    assert rc == EXIT_PASS, f"실 repo 기준선이 PASS 가 아니다: rc={rc}, {payload}"
    assert payload["gate_id"] == "NG-12"
    assert payload["reason"] == "bash_matcher_registered", payload

    # ⓑ resolved 경로 echo
    probe = payload["identity_probe"]
    resolved = (probe.get("resolved_hooks_json") or "").replace("\\", "/")
    assert resolved.endswith("hooks/hooks.json"), probe
    assert (probe.get("resolved_via") or "").replace("\\", "/") == "hooks/hooks.json", probe
    assert Path(resolved) == HOOKS_JSON.resolve(), probe

    # ⓒ trace 실값 — `unknown` placeholder 가 아니고 차단 4종이 실제로 보인다
    names = payload["trace"]["registered_hook_names"]
    assert "unknown" not in names, f"vacuous trace 회귀: {names}"
    assert set(BLOCKING_HOOKS) <= set(names), f"차단 4종 미관측: {names}"
    assert payload["trace"]["registered_hook_count"] == len(names)

    # 음성 대조 — 후보 전무 repo-root 는 not-found 로 갈린다(하드코딩 아님)
    rc_empty, payload_empty = _run_ng12_by_repo_root(tmp_path)
    assert rc_empty == EXIT_INCONCLUSIVE, payload_empty
    assert payload_empty["reason"] == "hooks_json_not_found", payload_empty
    assert payload_empty["identity_probe"]["resolved_hooks_json"] is None, payload_empty


# ═══════════════════════════════════════════════ ③ ★migration★ — matcher union (1회성)
_MIGRATION_ENV = "CFP2926_HOOK_MERGE_MIGRATION"
_MERGED_HOOK_ENV = "CFP2926_MERGED_HOOK_NAME"
_MERGE_BASE_ENV = "CFP2926_HOOK_MERGE_BASE"

_migration_only = pytest.mark.skipif(
    os.environ.get(_MIGRATION_ENV) != "1",
    reason=(
        "tier=migration — H-2 병합 PR ★1회 한정★ 실행이며 착지 후 T1 은퇴 "
        "(§8.0.1 tier 표 / §8.0.2 RTM / 설계리뷰 iter2 P2-E). 상시 회귀로 두면 좌변"
        "(병합 전 matcher) 관측면이 소멸해 tautological 또는 하드코딩 중 하나가 된다. "
        f"병합 PR 안에서만 {_MIGRATION_ENV}=1 로 켠다."
    ),
)


@_migration_only
def test_hook_merge_matcher_union_preserved():
    """§7.7.2 규정 ② — 병합 ★전★ 4 hook matcher 합집합 ⊆ 병합 ★후★ 진입점 matcher 합집합.

    ★1회성인 이유★: 좌변은 그 PR 의 merge-base blob 에서만 관측 가능하다
    (`git show <merge-base>:hooks/hooks.json`). 착지 후에는 좌변 관측면이 사라지므로
    상시 회귀로 두면 ⒜ 양변이 같은 파일을 읽는 tautology(판별력 0) 또는 ⒝ 금지된
    하드코딩 중 하나가 된다 — 둘 다 자기 규정 위반(P2-E).
    상시 등록면 보호는 ①(실 도구 경유 e2e) + ②(M-F′) 가 전담한다.

    ★강등의 수용된 대가 (은폐 금지)★: 착지 이후 "원래 4 hook 이 덮던 도구 집합"이라는
    역사적 기준선은 상시 검증되지 않는다.
    """
    merge_base = os.environ.get(_MERGE_BASE_ENV) or subprocess.run(
        ["git", "merge-base", "HEAD", "origin/main"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    assert merge_base, f"merge-base 미해소 — {_MERGE_BASE_ENV} 로 명시 주입하라"

    blob = subprocess.run(
        ["git", "show", f"{merge_base}:hooks/hooks.json"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8",
    )
    assert blob.returncode == 0, f"merge-base blob 판독 실패: {blob.stderr[:200]}"
    before = json.loads(blob.stdout)
    after = load_hooks_json()

    left = matcher_tokens_for(before, set(BLOCKING_HOOKS))
    assert left, "좌변(병합 전) matcher 합집합이 비었다 — merge-base 오지정 = vacuous 참"

    # 우변 = 차단 4종 잔존분 ∪ 병합 진입점. 진입점 이름은 명시 주입하며,
    # 미주입 + 4종 전멸이면 ★조용히 통과시키지 않고 실패★ 한다(fail-closed).
    right_names = set(BLOCKING_HOOKS)
    merged_name = os.environ.get(_MERGED_HOOK_ENV, "").strip()
    if merged_name:
        right_names.add(merged_name)
    right = matcher_tokens_for(after, right_names)
    assert right, (
        "우변 matcher 합집합이 비었다 — 병합 진입점을 "
        f"{_MERGED_HOOK_ENV} 로 지정하라 (미지정 통과 금지)"
    )

    assert left <= right, (
        f"matcher union 축소 — 병합으로 도구 커버리지가 소실됐다: 손실={sorted(left - right)}"
    )
