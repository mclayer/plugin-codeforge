#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_hook_merge_registration.py — CFP-2926 NG-12 hook registration validation.

hooks.json 의 PreToolUse Bash matcher 등록면 검증 (H-2' 형상 — 4 차단 hook 공유 1개 등록 site).

규정:
  - 4 차단 hook(cross-repo-gh-safety, repo-confinement, git-branch-delete-merge-gate,
    worktree-location-guard) 가 hooks.json PreToolUse 의 **동일 matcher 블록** 에
    "matcher": "Bash" 로 등록돼 있어야 함 (단일 실패점 — 한 줄이 좁아지면 4개 동시 죽음).
  - 등록면(matcher) 보존 assert 상시 (§7.7.2 H-2′) — 수정은 본 Story 범위 밖.
  - mutant: matcher 에서 Bash 제거 → 각 회차 RED (M-F′).

불변식:
  - empty-target: PreToolUse 블록 자체 미존재 → INCONCLUSIVE
  - unknown-input: hooks.json unparseable → fail-closed RED (exit 1)
  - trace: 등록 hook 수 · 정합 상태

★★born-inert 정정 이력 (CFP-2926 Phase 2 — DeveloperPL firsthand 검출 · NG-16 동종 재발)★★
  종전 구현은 ★CI 배선에서 등록면에 영구 미도달★ 했다:
    (1) **경로 오류** — `os.path.join(repo_root, "hooks.json")` 을 봤으나 wrapper 의
        실 등록면은 ★`hooks/hooks.json`★ 이다. CI 배선(`--repo-root .`)에서
        `isfile` False → 즉시 `INCONCLUSIVE hooks_json_not_found`(exit 3) 로 반환되고
        파싱·matcher 판정에 ★도달조차 못 했다★.
        ⇒ `hooks.json` 을 어떻게 훼손해도 결과가 불변 = ★판별력 0★ (mutant 로 죽일 수도
        없다 — 이미 죽어 있었다). 항상-INCONCLUSIVE 는 항상-GREEN 과 똑같이 hollow 다.
    (2) **vacuous trace** — `trace.handler_ids = [h.get("id","unknown") …]` 였는데
        matcher entry dict 에는 `id` 키가 애초에 없다 ⇒ 실측 항상 `["unknown"]`
        = `[154-AC-5]` execution-trace 정보량 0.
  ⇒ 정정: 등록면 후보를 **우선순위대로 resolve**(`hooks/hooks.json` → `hooks.json` →
     `.claude/hooks.json`; `--hooks-json` 명시 지정이 최우선 override)하고,
     ★resolve 된 경로를 `identity_probe` 에 echo★([154-AC-13])하며, trace 의 hook 식별자는
     등록 command 문자열에서 **유도한 실 hook 이름**으로 교체했다.
     resolve 패턴은 sibling NG-16 `check_subagent_stop_auto_emit.py`
     (`_HOOKS_REGISTRATION_CANDIDATES` / `_resolve_registration_file`) 를 그대로 답습한다
     (신규 발명 0 — 동일 결함 class 의 동일 처방).

★정직 천장 — 본 게이트가 검출하지 못하는 축 (over-claim 금지)★
  - **검출 깊이**: 판정은 "Bash matcher 블록이 등록면에 존재하는가" 까지다.
    ★4 차단 hook 이 그 블록에 **개별로** 등록돼 있는지는 verdict 에 관여하지 않는다★
    ⇒ "블록은 남기고 hook 1종만 삭제" mutant 는 **본 모듈이 놓친다**.
    (관측치는 `trace.expected_blocking_hook_present_count` 로 **싣기만** 하고 판정에는
     쓰지 않는다 — 검사 범위 확대는 Change Plan 범위 밖 결정이라 미구현.)
    이 공백은 **test-tier** 로 보강돼 있다:
    `tests/unit/cfp_2926/test_ng12_hook_merge.py::test_hook_merge_matcher_registration_alive`
    (0') 및 `::test_hook_merge_each_gate_still_blocks`(실 도구 경유 e2e).
  - **matcher 판정 폭**: 정확 상등(`"Bash"`) ∨ list 포함만 해소한다. `"Bash|Write"` 같은
    ★파이프 병합형 matcher 는 미해소★ 라, H-2 병합으로 matcher 형상이 바뀌면 false RED 가
    될 수 있다(현행 `hooks/hooks.json` 은 정확 상등이라 오늘은 무해). 판정 semantic 확대
    역시 Change Plan 범위 밖 → 필요 시 escalate.
  - **등록 ≠ 발화**: 등록 **선언**만 본다. 하네스가 실제로 이 hook 을 호출하는지는
    본 모듈로 증명되지 않는다(플랫폼 소관, ADR-154 §결정 4 INV-5 detection sufficiency).
  - 등록면 후보가 **하나도 없을 때**는 종전대로 `INCONCLUSIVE`(exit 3, non-GREEN) 를
    유지한다 — sibling NG-16 은 같은 상황을 RED 로 사상하나, verdict 사상 변경은 본 정정
    범위 밖이라 손대지 않았다(양쪽 모두 non-GREEN 이라 조용한 통과는 없다).
  - "100% 기계강제 / 완전 봉인 / 전부 검출" 아님.

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import json
import os
import sys

from gate_verdict import (
    GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-12"

# 4 차단 hook 이름 (상수, 검증 대상 확인용 — 실 매처 항목 필드는 matcher 값 체크)
_EXPECTED_HOOK_IDS = {
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
}

# ★등록면 후보 — 우선순위대로 resolve 하고 resolved 경로를 probe 에 echo 한다★
# sibling NG-16(`check_subagent_stop_auto_emit.py`) 이 동일 born-inert 결함에 채택한
# 패턴을 그대로 답습(신규 발명 0). 1순위 = wrapper 실제 등록면(`hooks/hooks.json`),
# 2순위 = repo 루트(구 구현 가정), 3순위 = consumer overlay(`.claude/hooks.json`).
_HOOKS_REGISTRATION_CANDIDATES = (
    os.path.join("hooks", "hooks.json"),
    "hooks.json",
    os.path.join(".claude", "hooks.json"),
)


def _resolve_registration_file(repo_root):
    """등록면 파일을 우선순위대로 resolve. Returns: (abs_path or None, rel or None)."""
    for rel in _HOOKS_REGISTRATION_CANDIDATES:
        path = os.path.join(repo_root, rel)
        if os.path.isfile(path):
            return path, rel
    return None, None


def _hook_name_of(command):
    """등록 command 문자열에서 hook 식별자를 유도한다.

    `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" cross-repo-gh-safety`
        → `cross-repo-gh-safety`

    ★종전 `handler.get("id", "unknown")` 은 matcher entry dict 에 `id` 키가 없어
    실측 항상 `"unknown"` 이었다(trace 정보량 0)★. 인자 없는 command 형상이면 마지막
    토큰이 실행 파일 경로이므로 basename 으로 낮춘다(경로 전체 echo 회피).
    """
    if not isinstance(command, str):
        return None
    tokens = command.strip().split()
    if not tokens:
        return None
    token = tokens[-1].strip('"').strip("'")
    if "/" in token or "\\" in token:
        token = os.path.basename(token.replace("\\", "/"))
    return token or None


def _registered_hook_names(handlers):
    """Bash matcher 블록들에 등록된 hook 이름 목록(등록 순서 보존)."""
    names = []
    for handler in handlers:
        hooks = handler.get("hooks")
        if not isinstance(hooks, list):
            continue
        for hook in hooks:
            if not isinstance(hook, dict):
                continue
            name = _hook_name_of(hook.get("command"))
            if name:
                names.append(name)
    return names


def _find_bash_matcher_hook_blocks(pretooluse_list):
    """PreToolUse 에서 Bash matcher 를 포함하는 모든 블록 찾기.

    PreToolUse 는 hook handler dict 의 list (또는 단일 dict).
    각 handler 의 "matcher" field 가 "Bash" 를 포함하면 그 handler 반환.

    Returns: list of hook handler dicts that have matcher=Bash or matcher contains Bash
    """
    handlers = []
    if isinstance(pretooluse_list, list):
        handlers = pretooluse_list
    elif isinstance(pretooluse_list, dict):
        handlers = [pretooluse_list]
    else:
        return []

    bash_handlers = []
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        matcher = handler.get("matcher")
        if matcher is None:
            continue
        # matcher 가 "Bash" (string) 또는 "Bash" 포함 (list)
        if isinstance(matcher, str) and matcher == "Bash":
            bash_handlers.append(handler)
        elif isinstance(matcher, list) and "Bash" in matcher:
            bash_handlers.append(handler)
    return bash_handlers


def main(argv=None):
    """Main entry point.

    CLI:
      python check_hook_merge_registration.py --repo-root <path> [--hooks-json <path>]

    Exit codes:
      0 = PASS (Bash matcher registered with expected hooks)
      1 = RED (matcher validation failed)
      3 = INCONCLUSIVE (PreToolUse not configured)
    """
    parser = argparse.ArgumentParser(
        prog="check_hook_merge_registration.py",
        description="PreToolUse hook Bash matcher registration validation (H-2′).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--hooks-json", default="", help="hooks.json path (override default)"
    )

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)

    # ★경로 resolve★ — `--hooks-json` 명시 지정이 최우선 override, 그 다음 후보 우선순위.
    # (종전엔 repo 루트 `hooks.json` 단일 고정이라 실 등록면 `hooks/hooks.json` 에
    #  영구 미도달 = born-inert. 상단 docstring 정정 이력 참조.)
    if args.hooks_json:
        hooks_json_path = os.path.abspath(args.hooks_json)
        resolved_via = "--hooks-json"
        if not os.path.isfile(hooks_json_path):
            hooks_json_path = None
    else:
        hooks_json_path, resolved_via = _resolve_registration_file(repo_root)

    # ★[154-AC-13]★ 실제로 무엇을 봤는지 — 경로 미도달이 vacuous 판정으로 굳지 않도록
    # resolve 결과를 그대로 echo 한다(종전 born-inert 의 직접 원인 차단).
    probe = {
        "repo_root": repo_root,
        "registration_candidates": list(_HOOKS_REGISTRATION_CANDIDATES),
        "resolved_via": resolved_via,
        "resolved_hooks_json": hooks_json_path,
        "file": hooks_json_path,  # 하위호환 key (종전 probe 필드)
    }

    # hooks.json 존재 확인
    if hooks_json_path is None:
        result = empty_target(
            gate_id=GATE_ID,
            reason="hooks_json_not_found",
            trace={
                "candidate_count": len(_HOOKS_REGISTRATION_CANDIDATES),
                "resolved_file_count": 0,
            },
            identity_probe=probe,
        )
        return emit(result)

    # JSON 파싱
    try:
        with open(hooks_json_path, "r", encoding="utf-8") as f:
            hooks_data = json.load(f)
    except json.JSONDecodeError as e:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=f"hooks_json_parse_error: {str(e)[:80]}",
            identity_probe=probe,
        )
        return emit(result)
    except Exception as e:
        result = unknown_input(
            gate_id=GATE_ID,
            reason=f"hooks_json_read_error: {str(e)[:80]}",
            identity_probe=probe,
        )
        return emit(result)

    if not hooks_data:
        result = empty_target(
            gate_id=GATE_ID,
            reason="hooks_json_empty",
            identity_probe=probe,
        )
        return emit(result)

    # hooks 객체 추출 (형식: { "hooks": {...} } 또는 { "PreToolUse": [...] })
    hooks_obj = hooks_data.get("hooks", hooks_data)
    if not isinstance(hooks_obj, dict):
        result = unknown_input(
            gate_id=GATE_ID,
            reason="hooks_root_not_dict",
            identity_probe=probe,
        )
        return emit(result)

    # PreToolUse 블록 추출
    pretooluse = hooks_obj.get("PreToolUse")
    if pretooluse is None:
        result = empty_target(
            gate_id=GATE_ID,
            reason="pretooluse_not_found",
            identity_probe=probe,
        )
        return emit(result)

    # Bash matcher 블록 찾기
    bash_handlers = _find_bash_matcher_hook_blocks(pretooluse)
    if not bash_handlers:
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="bash_matcher_not_registered",
            trace={
                "bash_handler_count": 0,
                "registered_hook_count": 0,
                "registered_hook_names": [],
            },
            identity_probe=probe,
        )
        return emit(result)

    # Bash matcher 블록이 있으면 PASS
    # (★정직: 실제 4 차단 hook 이 그 matcher 블록에 등록돼 있는지는 본 gate 범위 밖
    #   — 등록면 축만 검증, 차단 판정 자체는 M-F 소관. 아래 expected_* 는 ★관측치 echo★
    #   일 뿐 verdict 에 관여하지 않는다 — 상단 docstring 정직 천장 참조.)
    registered_names = _registered_hook_names(bash_handlers)
    expected_present = sorted(_EXPECTED_HOOK_IDS & set(registered_names))
    trace = {
        "bash_handler_count": len(bash_handlers),
        "registered_hook_count": len(registered_names),
        "registered_hook_names": registered_names,
        "expected_blocking_hook_present_count": len(expected_present),
        "expected_blocking_hook_total": len(_EXPECTED_HOOK_IDS),
    }
    probe_pass = dict(probe)
    probe_pass["matcher_field"] = "Bash"
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="bash_matcher_registered",
        trace=trace,
        identity_probe=probe_pass,
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
