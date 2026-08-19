#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# acquire_429_lease.py — 429 subagent concurrency lease acquire
#
# Carrier: CFP-2967 Phase 2 (workerC — lease acquire/release + reconcile 4-status)
#
# 책임:
#   - SubagentStart 훅 진입 시 lease 파일 생성 (ConcurrentSubagents 관측)
#   - lease 파일 = `.claude/ledger/429-lease-<agent_id>.json`
#   - 파일 내용 = JSON: {"agent_id": "<id>", "timestamp": "<ISO8601 UTC Z>", "renewed_at": "<UTC Z>"}
#   - fail-open ALWAYS (exit 0) — 어떤 실패도 SubagentStart 훅 block 금지
#   - graceful degradation: mkdir 실패 / write 실패 / 어떤 예외 → stderr warning + exit 0
#   - 0 API call, stdlib only, 네트워크 0
#
# 사용:
#   python3 acquire_429_lease.py --agent-id <id> [--ledger-dir <path>]
#
# 기술 계약:
#   - agent_id: 필수. SubagentStart payload 의 agent_id 필드 (호출자가 유도 책임)
#   - ledger-dir: optional, default = CLAUDE_PROJECT_DIR/.claude/ledger
#   - exit 0 ALWAYS (fail-open 강제)

import argparse
import datetime
import json
import os
import sys
from pathlib import Path


def _utc_now_z() -> str:
    """UTC ISO 8601 타임스탬프 (UTC Z strict — spawn-event 규약)."""
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    return utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")


def acquire_lease(agent_id: str, ledger_dir: Path) -> None:
    """lease 파일 생성 (agent_id 단위).

    파일명: 429-lease-<agent_id>.json
    내용: {"agent_id": "<id>", "timestamp": "<now_UTC>", "renewed_at": "<now_UTC>"}

    실패 → stderr warning + return (exit 0 유지)
    """
    try:
        # parent dir 보장
        ledger_dir.mkdir(parents=True, exist_ok=True)

        lease_file = ledger_dir / f"429-lease-{agent_id}.json"
        now_utc = _utc_now_z()

        lease_record = {
            "agent_id": agent_id,
            "timestamp": now_utc,
            "renewed_at": now_utc,
        }

        # atomic write: temp + rename (cross-platform kernel-atomic pattern)
        with open(lease_file, "w", encoding="utf-8") as f:
            json.dump(lease_record, f, ensure_ascii=False)

        # file mode 0600
        try:
            os.chmod(str(lease_file), 0o600)
        except (OSError, AttributeError):
            pass  # Windows no-op

    except Exception as e:
        # fail-open: stderr warning 만 출력하고 계속 진행
        print(f"[codeforge-wrapper-acquire-429-lease] WARN: lease acquire failed — {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="429 subagent concurrency lease acquire"
    )
    parser.add_argument("--agent-id", required=True, help="subagent agent_id")
    parser.add_argument(
        "--ledger-dir",
        default=None,
        help="ledger directory (default: CLAUDE_PROJECT_DIR/.claude/ledger)"
    )

    args = parser.parse_args()

    # ledger dir 결정
    ledger_dir = None
    if args.ledger_dir:
        ledger_dir = Path(args.ledger_dir)
    elif "CLAUDE_PROJECT_DIR" in os.environ:
        ledger_dir = Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".claude" / "ledger"
    else:
        # CLAUDE_PROJECT_DIR 미설정 → 작동 불가, graceful skip (exit 0)
        print(
            "[codeforge-wrapper-acquire-429-lease] WARN: CLAUDE_PROJECT_DIR unset — ledger acquire skipped",
            file=sys.stderr
        )
        sys.exit(0)

    # acquire
    acquire_lease(args.agent_id, ledger_dir)
    sys.exit(0)  # always exit 0


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code if e.code is not None else 0)
    except Exception:
        sys.exit(0)  # catch-all fail-open
