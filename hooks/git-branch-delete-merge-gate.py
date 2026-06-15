#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT (file structure adapted from superpowers v5.1.0 hook pattern)
"""git-branch-delete-merge-gate.py — PreToolUse hook: 미머지 PR branch 삭제 하드차단.

목적:
  remote branch 삭제 명령(`git push <remote> --delete|-d <b>` / `git push <remote> :<b>`)
  을 가로채, 해당 branch 에 열린(미머지) PR 이 있으면 PreToolUse 단계에서 물리 차단한다.

사고 박제: 2026-06-15 INCIDENT #2280 — 미머지 PR 의 branch 를 선삭제(merge 확인 없이
  cleanup 스크립트가 무조건 실행) 하자 PR 이 auto-close 되고, phase-gate-mergeable
  status check 가 그 branch 의 head SHA 에 "expected" 상태로 stuck. reopen·fresh PR·
  admin merge 까지 BLOCKED 되어 복구에 비용 발생. branch delete 는 비가역 — merge 호출
  실패 시에도 파이프(`A; B` / `A && B` 의 exit code 가림)로 삭제가 실행되는 구조 결함.

책임 경계:
  - 책임: `git push <remote> {--delete|-d} <branch...>` / `git push <remote> :<branch>`
          (colon refspec deletion) 형태의 remote branch 삭제에 대해, 대상 branch 에
          열린 PR 존재 시 차단 (exit 2). 미머지 PR branch 선삭제 방지.
  - 비책임: tag 삭제(`--delete tag` / `:refs/tags/...`) = scope 외 (fail-open 통과).
          local branch 삭제(`git branch -d/-D`) = remote PR 영향 0 → scope 외.
          worktree-lifecycle skill (merge 확인 후 삭제 순서 불변) 이 가이드 차원 보완.

정적 properties:
  (a) 표준 라이브러리만 사용 (외부 의존 0).
  (b) filesystem touch 0 (stdin/stderr/stdout 만).
  (c) network call 1 — `gh pr list` subprocess (delete 패턴 매칭 시에만, fail-open).
      cross-repo-gh-safety 의 "network 0" 와 다른 점. 사유: PR merge 상태는 로컬 git
      으로 알 수 없다(squash merge 는 branch commit 을 origin/main ancestry 에 안 올림).
      gh 조회가 필수다. 어떤 gh 오류(부재/non-zero/timeout/JSON 파싱 실패)든 fail-open.

PreToolUse block contract (Claude Code): exit 2 + stderr = block (Claude 재시도 판단).
  exit 0 = allow. 미매칭 / 비-Bash tool / 모든 예외·파싱실패·gh실패 = exit 0 (fail-open).
  P0 fail-safe: 자기 결함으로 정상 작업 차단 금지 — "열린 PR 확인" 만 유일한 차단 경로.

Bypass:
  BYPASS_BRANCH_DELETE_MERGE_GATE=1 — stderr audit echo + exit 0
  (의도된 abandon 삭제 확신 시. launcher 에서 1차 + 본 core 에서 재확인).
"""

from __future__ import annotations

import datetime
import json
import os
import shlex
import subprocess
import sys

_GH_TIMEOUT_SEC = 10


def _read_input() -> dict:
    """stdin = PreToolUse JSON payload. dict 반환 (실패 시 빈 dict — fail-open)."""
    try:
        if sys.stdin.isatty():
            return {}
    except Exception:
        pass
    try:
        raw = sys.stdin.read(1 << 20)  # bounded ≤1 MiB
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw.strip())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def _extract_command(payload: dict) -> str:
    """payload.tool_input.command 추출 (비-Bash / 부재 시 빈 문자열)."""
    if payload.get("tool_name") != "Bash":
        return ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    cmd = tool_input.get("command")
    return cmd if isinstance(cmd, str) else ""


def _strip_ref_prefix(name: str) -> str:
    """refs/heads/ prefix 제거 (branch 이름 정규화). 빈 결과는 호출자가 거른다."""
    if name.startswith("refs/heads/"):
        return name[len("refs/heads/") :]
    return name


def _is_tag_ref(name: str) -> bool:
    """tag 삭제 토큰 판별 — scope 외 (fail-open 통과)."""
    return name == "tag" or name.startswith("refs/tags/")


def _parse_delete_branches(command: str) -> list[str]:
    """command 에서 remote branch 삭제 대상 branch 이름 list 추출.

    트리거 패턴 (둘 중 하나):
      - `git push <remote> --delete <b...>` / `git push <remote> -d <b...>`
      - `git push <remote> :<b>` (colon refspec deletion)

    git push 가 아니거나 삭제 패턴 미매치면 [] 반환. tag 삭제는 제외.
    shlex 파싱 실패 / 모든 예외 → [] (fail-open).
    """
    try:
        tokens = shlex.split(command)
    except Exception:
        return []
    if not tokens:
        return []

    # `git push` subcommand 위치 탐색 (env prefix VAR=val / 경로형 git 허용).
    push_idx = -1
    for i in range(len(tokens) - 1):
        tok = tokens[i]
        if (tok == "git" or tok.endswith("/git") or tok.endswith("\\git")) and tokens[
            i + 1
        ] == "push":
            push_idx = i + 1
            break
    if push_idx == -1:
        return []

    args = tokens[push_idx + 1 :]  # push 이후 토큰
    branches: list[str] = []
    delete_flag = False
    remote_seen = False  # 첫 비-flag 비-colon 토큰 = remote 이름 (1회 consume)

    for tok in args:
        if tok in ("--delete", "-d"):
            delete_flag = True
            continue
        if tok.startswith("-"):
            # 그 외 flag (--force, --tags, -u 등) 는 무시 — 대상 추출에 무관.
            continue
        if tok.startswith(":") and len(tok) > 1:
            # colon refspec deletion: `:<dst>` (src 빈 = 삭제). `src:` 는 삭제 아님.
            dst = tok[1:]
            if _is_tag_ref(dst):
                continue  # tag 삭제 — scope 외
            name = _strip_ref_prefix(dst)
            if name:
                branches.append(name)
            continue
        # 비-flag, 비-colon 일반 토큰.
        if not remote_seen:
            # 첫 일반 토큰 = remote (예: origin) — 삭제 대상 아님.
            remote_seen = True
            continue
        if delete_flag:
            # --delete/-d 모드: remote 이후 일반 토큰 = 삭제 대상 branch.
            if _is_tag_ref(tok):
                # `git push origin --delete tag <name>` → tag 삭제, scope 외.
                return []
            name = _strip_ref_prefix(tok)
            if name:
                branches.append(name)
        # delete_flag 아니고 colon 도 아닌 일반 refspec (예: `git push origin main`,
        # `git push origin src:dst`) = 삭제 아님 → 무시.

    # 중복 제거 (순서 보존)
    seen = set()
    uniq = []
    for b in branches:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def _open_prs_for_branch(branch: str) -> list[dict]:
    """`gh pr list --head <branch> --state open` → 열린 PR list.

    어떤 오류(gh 부재 FileNotFoundError / non-zero returncode / timeout /
    JSON 파싱 실패)든 [] 반환 (그 branch 는 fail-open — 차단 안 함).
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                "number,title",
            ],
            capture_output=True,
            text=True,
            timeout=_GH_TIMEOUT_SEC,
            shell=False,
        )
    except Exception:
        sys.stderr.write(
            f"[branch-delete-merge-gate] gh 확인 실패 — fail-open ('{branch}')\n"
        )
        return []
    if result.returncode != 0:
        sys.stderr.write(
            f"[branch-delete-merge-gate] gh 확인 실패 (rc={result.returncode}) — fail-open ('{branch}')\n"
        )
        return []
    try:
        data = json.loads(result.stdout or "[]")
    except (json.JSONDecodeError, ValueError):
        sys.stderr.write(
            f"[branch-delete-merge-gate] gh JSON 파싱 실패 — fail-open ('{branch}')\n"
        )
        return []
    return data if isinstance(data, list) else []


def _build_block_message(branch: str, prs: list[dict]) -> str:
    """exit 2 차단 메시지 (열린 PR 1개 이상)."""
    pr = prs[0]
    number = pr.get("number", "?")
    title = pr.get("title", "")
    return "\n".join(
        [
            f"[branch-delete-merge-gate] BLOCKED — '{branch}' 에 열린(미머지) PR #{number} ({title}) 존재.",
            "사유: 미머지 PR 의 branch 를 삭제하면 PR auto-close + phase-gate-mergeable status 가 "
            'SHA 에 stuck("expected") 되어 reopen·fresh PR·admin merge 까지 BLOCKED 됩니다 '
            "(INCIDENT 2026-06-15 #2280 박제).",
            f"해소: 먼저 merge 를 확인(`gh pr view {number} --json mergedAt` 비-null)한 뒤 branch 를 삭제하세요.",
            "bypass (의도된 abandon 삭제 확신 시): BYPASS_BRANCH_DELETE_MERGE_GATE=1",
        ]
    )


def main() -> int:
    """PreToolUse 진입점. 모든 경로 fail-open(exit 0) except 열린-PR-확인(exit 2)."""
    try:
        # bypass — launcher 에서 1차, 본 core 에서 재확인 (직접 .py 실행 대비).
        if os.environ.get("BYPASS_BRANCH_DELETE_MERGE_GATE", "0") == "1":
            try:
                ts = datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            except Exception:
                ts = "unknown"
            sys.stderr.write(
                f"[branch-delete-merge-gate] BYPASS_BRANCH_DELETE_MERGE_GATE=1 — gate suppressed at {ts}\n"
            )
            return 0

        payload = _read_input()
        command = _extract_command(payload)
        if not command:
            return 0  # 비-Bash / command 부재 → 통과

        branches = _parse_delete_branches(command)
        if not branches:
            return 0  # 삭제 패턴 아님 → 통과

        for branch in branches:
            prs = _open_prs_for_branch(branch)
            if prs:
                sys.stderr.write(_build_block_message(branch, prs) + "\n")
                return 2  # 유일한 차단 경로

        return 0  # 모든 branch 에 열린 PR 없음 → 통과
    except Exception:
        # P0 fail-open — 어떤 예외도 exit 0 (자기 결함으로 정상 작업 차단 금지).
        return 0


if __name__ == "__main__":
    sys.exit(main())
