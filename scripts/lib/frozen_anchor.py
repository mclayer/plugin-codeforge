#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""frozen_anchor.py — frozen ADR 앵커 내용-기반 resolve (줄번호 앵커 금지).

CFP-2926 / Story §8.0.9 — frozen ADR 에 Amendment 가 append 되면 뒤 줄번호가
밀린다. 줄번호로 assert 하면 자기 PR 이 자기 게이트를 RED 로 만든다(born-broken).
그래서 앵커는 verbatim 문자열 내용으로 grep -n -F -x -e 재해석하고, 줄번호는
산출값(trace emit 입력)일 뿐 입력으로 쓰지 않는다.

외부 의존 0 — 표준 라이브러리(hashlib, pathlib, subprocess, typing)만 사용.
"""

import hashlib
import subprocess
from pathlib import Path
from typing import List, Optional

ANCHOR_OK = "ANCHOR_OK"
ANCHOR_NOT_FOUND = "ANCHOR_NOT_FOUND"
ANCHOR_AMBIGUOUS = "ANCHOR_AMBIGUOUS"
ANCHOR_RESOLVE_FAILED = "ANCHOR_RESOLVE_FAILED"
ANCHOR_CONTENT_MISMATCH = "ANCHOR_CONTENT_MISMATCH"


class AnchorResolution:
    """grep 재해석 1회 결과 값 객체."""

    def __init__(
        self,
        status: str,
        line_numbers: Optional[List[int]] = None,
        match_count: int = 0,
        grep_exit: int = -1,
        sha256: str = "",
    ) -> None:
        self.status = status
        self.line_numbers = line_numbers if line_numbers is not None else []
        self.match_count = match_count
        self.grep_exit = grep_exit
        self.sha256 = sha256


REGISTERED_ANCHORS = {
    "A-1": {
        "path": "archive/adr/ADR-044-phase-scoped-sequential-team.md",
        "verbatim": (
            "- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) "
            "§결정 1 — default subagent context 의 재귀 spawn "
            "금지 (Lead·teammate 공통, platform inherent)"
        ),
        "sha256": "4d1767f73b5a318432ff288f36b48bf6cce0dc35a5f308e7b1545bc674b642b3",
        "line_hint": 624,  # ★hint 전용 — assert 입력 금지★
    },
    "A-2": {
        "path": "archive/adr/ADR-064-decision-principle-mandate.md",
        "verbatim": (
            "| `env=0` (default subagent context, ADR-039) | Orchestrator round-trip polyfill "
            "— PL 이 batch N task multi-instance subagent dispatch 를 1 round trip "
            "안에 spawn | 재귀 spawn (platform inherent) / worker-to-worker "
            "SendMessage (codeforge policy) |"
        ),
        "sha256": "653a054d3ea84a09f1bf506de2178b177b24b53f735b6c76daf733f5519043b4",
        "line_hint": 691,
    },
}


def line_sha256(line: str) -> str:
    """줄 바이트열(trailing newline 제외, UTF-8)의 sha256 hexdigest."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def resolve_anchor(repo_root, verbatim: str, rel_path: str) -> AnchorResolution:
    """grep -n -F -x -e <verbatim> -- <file> 로 매 실행 시 재해석.

    5-state 판정 (§8.0.9):
      exit 0 ∧ match=1  → ANCHOR_OK
      exit 0 ∧ match>=2 → ANCHOR_AMBIGUOUS
      exit 1            → ANCHOR_NOT_FOUND (0 매치)
      exit >= 2         → ANCHOR_RESOLVE_FAILED (grep 호출 실패)
      grep 미설치/실행 불가 → ANCHOR_RESOLVE_FAILED (예외 삼키고 GREEN 금지)
    """
    target = str(Path(repo_root) / rel_path)

    try:
        proc = subprocess.run(
            ["grep", "-n", "-F", "-x", "-e", verbatim, "--", target],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        # grep 이 PATH 에 없거나 실행 불가 — 예외를 삼키고 GREEN 금지, RESOLVE_FAILED 로 사상.
        return AnchorResolution(status=ANCHOR_RESOLVE_FAILED, grep_exit=-1)

    returncode = proc.returncode

    if returncode >= 2:
        return AnchorResolution(status=ANCHOR_RESOLVE_FAILED, grep_exit=returncode)

    matched_lines = [entry for entry in proc.stdout.splitlines() if entry]
    line_numbers: List[int] = []
    for entry in matched_lines:
        num_str, sep, _content = entry.partition(":")
        if not sep:
            # grep -n 출력 형식(N:content) 위반 — 파싱 불가 → RESOLVE_FAILED.
            return AnchorResolution(status=ANCHOR_RESOLVE_FAILED, grep_exit=returncode)
        try:
            line_numbers.append(int(num_str))
        except ValueError:
            return AnchorResolution(status=ANCHOR_RESOLVE_FAILED, grep_exit=returncode)

    match_count = len(line_numbers)

    if returncode == 1:
        # exit 1 = 0 매치 (grep 규약)
        return AnchorResolution(status=ANCHOR_NOT_FOUND, grep_exit=returncode)

    # returncode == 0
    if match_count == 1:
        return AnchorResolution(
            status=ANCHOR_OK,
            line_numbers=line_numbers,
            match_count=match_count,
            grep_exit=returncode,
            sha256=line_sha256(verbatim),
        )

    if match_count >= 2:
        return AnchorResolution(
            status=ANCHOR_AMBIGUOUS,
            line_numbers=line_numbers,
            match_count=match_count,
            grep_exit=returncode,
        )

    # exit 0 인데 매치 0 — grep 규약 위반(비정상 조합), fail-closed.
    return AnchorResolution(status=ANCHOR_RESOLVE_FAILED, grep_exit=returncode)


def verify_anchor(repo_root, anchor_id: str) -> AnchorResolution:
    """REGISTERED_ANCHORS[anchor_id] 를 resolve 하고 sha256 대조까지 수행."""
    entry = REGISTERED_ANCHORS[anchor_id]
    resolution = resolve_anchor(repo_root, entry["verbatim"], entry["path"])

    if resolution.status == ANCHOR_OK and resolution.sha256 != entry["sha256"]:
        return AnchorResolution(
            status=ANCHOR_CONTENT_MISMATCH,
            line_numbers=resolution.line_numbers,
            match_count=resolution.match_count,
            grep_exit=resolution.grep_exit,
            sha256=resolution.sha256,
        )

    return resolution
