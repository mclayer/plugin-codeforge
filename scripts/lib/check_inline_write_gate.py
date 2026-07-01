r"""
scripts/lib/check_inline_write_gate.py
CFP-2544 — Orchestrator inline-write gate (Wave1 warning) verifier SSOT

기능:
  PreToolUse(Write|Edit|MultiEdit) 훅에서 호출 — 최상위 세션(Orchestrator)이
  repo/worktree 파일을 직접 편집하는 규율 이탈을 검출한다. 실측 근거: 83 세션
  파싱 → repo 소스 직접 Edit/Write 127건(worktree 95 + 직접 32). CLAUDE.md
  "수정 작업 = agent spawn, inline 직접편집 4종만" 규칙 이탈.

  discriminator = PreToolUse payload 의 `agent_id` 필드 (code.claude.com/docs/en/hooks):
    - non-empty 문자열 = subagent 내부 호출 = ALLOW (정당 편집 97.5% 보존)
    - 부재/null/"" = 최상위(Orchestrator) main-thread = block-candidate (F2 fail-safe)
  `agent_type`/`subagent_type` 은 판정에 사용 금지 — `--agent` 플래그로도 present
  가능해 top-level 오판(bypass) 위험 (§7.2 SecurityArch).

  path 판정 (block-candidate 확정 후):
    worktree(`~/.claude/worktrees/`) 체크가 memory(`~/.claude/`) carve-out 보다
    반드시 먼저 — worktree 는 memory 의 prefix-subset 이라 순서가 결정적이다
    (뒤집으면 worktree 95건이 memory 로 오분류돼 가드 전체 무력화, §7.1).

  Wave1 = warning-tier: block-candidate 도 stderr block 마커 + exit 0.
    NEVER exit 2 (ADR-115 §결정 5 fail-open + escalate 금지). Wave2 deny 승격 =
    ADR-060 evidence-gate 후 별 CFP.

책임 경계:
  - 책임: agent_id 부재(Orchestrator) AND file_path repo/worktree AND whitelist 외
    → stderr block 마커(exit 0, Wave1 warning).
  - 비책임: subagent 편집(agent_id 존재) / memory·scratch·repo-밖 경로 / bump·parity
    등은 위임강제(default) 또는 BYPASS env. Bash redirect(U2)·mcp__github__*(U3) =
    후속 CFP (scope 밖).

Bypass:
  BYPASS_INLINE_WRITE_GATE=1 — stderr audit 한 줄(UTC ISO) + exit 0.
  audit 마커는 block 마커와 distinct sentinel (case 9 판별).

Fail-open (인프라 오류 → 통과, session brick 회피):
  stdin 비거나 JSON 파싱 실패 / 비-Write·Edit·MultiEdit tool / file_path 부재 → exit 0.
  (guard 는 best-effort 1차 안전망 — false-negative 가 false-positive 보다 안전).

PreToolUse block contract (Claude Code):
  Wave1 = exit 0 항상 (deny 비활성). Wave2(후속) = exit 2 + stderr = block.
"""

import json
import os
import sys
import time

# Windows cp949 stdout/stderr encoding 차단 (ADR-061 standardize).
# errors="replace" — cp949 환경에서 인코딩 불가 문자 방어 (lib/ 다수 파일 관용).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_NAME = "check_inline_write_gate"
BYPASS_ENV = "BYPASS_INLINE_WRITE_GATE"

# distinct sentinel 2종 (§8.3 design-confirm #2) — block ≠ audit.
#   block 마커 = block-candidate 검출 시 stderr 발화.
#   audit 마커 = BYPASS env 로 gate 억제 시 stderr 발화.
BLOCK_MARKER = "[codeforge-wrapper-inline-write-gate] BLOCK"
AUDIT_MARKER = "[codeforge-wrapper-inline-write-gate] BYPASS-AUDIT"

# 판정 대상 tool 3종 (Write/Edit/MultiEdit). 그 외 tool → scope 밖 (fail-open).
_TARGET_TOOLS = ("Write", "Edit", "MultiEdit")

# 경로 carve-out 접두사 (정규화 후 비교).
#   worktree = `~/.claude/worktrees/` — repo 편집으로 분류(block-candidate).
#   scratch  = `~/.claude/codeforge-scratch/` — allow.
#   memory   = `~/.claude/` — allow (generic carve-out, worktree/scratch 이후 검사).
_WORKTREE_SUBPATH = os.path.join(".claude", "worktrees")
_SCRATCH_SUBPATH = os.path.join(".claude", "codeforge-scratch")
_MEMORY_SUBPATH = ".claude"


def _norm(p):
    """경로 정규화 — realpath + normcase + normpath (예외 시 realpath 생략).

    check_repo_confinement.py `_norm()` 재사용 — MSYS2 `/c/Users/…` ↔ Windows
    `C:\\Users\\…` 오분류 방어 (§7.1 InfraOp).
    """
    try:
        return os.path.normcase(os.path.normpath(os.path.realpath(p)))
    except OSError:
        return os.path.normcase(os.path.normpath(p))


def _home():
    """홈 디렉터리 — `HOME` env 우선, 부재 시 `os.path.expanduser("~")`.

    본 훅은 run-hook.cmd → Git Bash 로 실행되어 MSYS `$HOME` 를 상속한다. 그런데
    Windows Python 의 `os.path.expanduser("~")` 는 `HOME` 을 무시하고 `USERPROFILE`
    을 쓴다 — bash 가 보는 `~/.claude/worktrees/` 와 Python 이 보는 홈이 어긋날 수
    있다. `HOME` 이 설정돼 있으면 그것을 정본으로 삼아 bash↔Python parity 를 맞춘다
    (§7.1 InfraOp — Windows/Unix home 오분류 방어).
    """
    return os.environ.get("HOME") or os.path.expanduser("~")


def _read_payload():
    """stdin = PreToolUse JSON payload. 비거나 파싱 실패 시 None (fail-open)."""
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return None
    if not raw or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


def _check_bypass():
    """BYPASS_INLINE_WRITE_GATE=1 → stderr audit(UTC ISO) 후 True (allow short-circuit)."""
    if os.environ.get(BYPASS_ENV) == "1":
        audit_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(
            f"{AUDIT_MARKER} {BYPASS_ENV}=1 — inline-write gate suppressed at {audit_ts}",
            file=sys.stderr,
        )
        return True
    return False


def _classify_agent(payload):
    """caller 판정 (F2 fail-safe).

    agent_id 가 non-empty 문자열일 때만 subagent → "subagent" 반환(ALLOW 경로).
    부재(키 누락) / null(None) / "" 3종 전부 "orchestrator" 반환(block-candidate 경로).
    `hooks/subagent-stop` 이 `data.get('agent_id','')` 로 top-level 읽기 실증 —
    payload 구조 firsthand corroborate (§7.2).
    """
    agent_id = payload.get("agent_id")
    if isinstance(agent_id, str) and agent_id != "":
        return "subagent"
    return "orchestrator"


def _classify_path(file_path, cwd):
    """file_path 경로 분류 → "block" (repo/worktree) | "allow" (memory/scratch/outside).

    ordering invariant (load-bearing, §7.1):
      1. worktree (`~/.claude/worktrees/`)   → block   ← 반드시 memory 보다 먼저
      2. scratch  (`~/.claude/codeforge-scratch/`) → allow
      3. memory   (`~/.claude/`)             → allow (generic carve-out)
      4. repo root (cwd 기준) 접두사          → block
      5. else (repo 밖)                      → allow

    step 1 이 step 3 보다 뒤면 모든 worktree 경로가 memory 로 오분류돼 잘못 allow
    → 가드 전체 무력화 (worktree 편집 = 실측 127건 중 95건).
    relative file_path 는 cwd 기준 resolve (§8.7 design-confirm #3).
    """
    if not file_path:
        return "allow"  # file_path 부재 → scope 밖 (fail-open)

    # relative → cwd 기준 절대화 (design-confirm #3). cwd 부재 시 os.getcwd().
    base_cwd = cwd or os.getcwd()
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_cwd, file_path)

    norm_path = _norm(file_path)
    home = _norm(_home())

    worktree_prefix = _norm(os.path.join(home, _WORKTREE_SUBPATH)) + os.sep
    scratch_prefix = _norm(os.path.join(home, _SCRATCH_SUBPATH)) + os.sep
    memory_prefix = _norm(os.path.join(home, _MEMORY_SUBPATH)) + os.sep

    # 1. worktree — memory carve-out 보다 먼저 (subset ordering invariant)
    if norm_path.startswith(worktree_prefix):
        return "block"
    # 2. scratch — allow
    if norm_path.startswith(scratch_prefix):
        return "allow"
    # 3. memory — allow (generic carve-out, 1·2 이후)
    if norm_path.startswith(memory_prefix):
        return "allow"

    # 4. repo root (cwd 기준) 접두사 → block-candidate
    norm_cwd = _norm(base_cwd)
    if norm_path == norm_cwd or norm_path.startswith(norm_cwd + os.sep):
        return "block"

    # 5. else (repo 밖) → allow
    return "allow"


def _emit_block():
    """block-candidate 검출 시 stderr block 마커 발화 (Wave1 warning)."""
    print(
        f"{BLOCK_MARKER} — Orchestrator 직접 repo/worktree 편집 검출 (CFP-2544).\n"
        f"\n"
        f"사유: 최상위 세션(Orchestrator)의 Write/Edit/MultiEdit 가 repo 또는\n"
        f"  worktree 경로를 향합니다. codeforge 규율상 repo 파일 수정은 예외 없이\n"
        f"  lane agent 에 위임해야 합니다 (ADR-039 §결정 1 / §결정 9).\n"
        f"\n"
        f"해소:\n"
        f"  - 소유 lane agent 를 spawn 해 편집을 위임하세요 (trivial 편집도 위임).\n"
        f"  - FIX 루프 실패 산출물은 소유 lane 으로 반송 (Orchestrator self-patch 금지).\n"
        f"\n"
        f"Wave1 = warning-only (편집 허용, 실 차단 없음). Wave2 deny 승격 = ADR-060\n"
        f"  evidence-gate(PR≥20 + bypass 외 failure=0 + sibling merged) 후 별 CFP.\n"
        f"bypass (의도된 직접 편집 확신 시): {BYPASS_ENV}=1 환경변수 설정 (audit trail).\n"
        f"참조: CFP-2544 inline-write gate.",
        file=sys.stderr,
    )


def main():
    # 1. Bypass — audit trail 의무 (경로 로직 이전 short-circuit)
    if _check_bypass():
        sys.exit(0)

    payload = _read_payload()
    if payload is None:
        sys.exit(0)  # fail-open (빈/malformed stdin)

    # 2. 비-Write/Edit/MultiEdit tool → 통과 (guard scope 외)
    if payload.get("tool_name") not in _TARGET_TOOLS:
        sys.exit(0)

    # 3. caller 판정 — subagent 는 무조건 통과 (97.5% 정당 편집 보존, path 축 short-circuit)
    if _classify_agent(payload) == "subagent":
        sys.exit(0)

    # 4. Orchestrator (agent_id 부재/null/"") — path 판정
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    cwd = payload.get("cwd")

    if _classify_path(file_path, cwd) == "block":
        _emit_block()

    # Wave1: 항상 exit 0 (block-candidate 도 warning-only, NEVER exit 2)
    sys.exit(0)


if __name__ == "__main__":
    main()
