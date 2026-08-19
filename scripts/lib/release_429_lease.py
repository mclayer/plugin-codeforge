#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# release_429_lease.py — 429 subagent concurrency lease release
#
# Carrier: CFP-2967 Phase 2 (workerC — lease acquire/release + reconcile 4-status)
#
# 책임:
#   - SubagentStop 훅 진출 시 lease 파일 삭제 (유실 해도 무해 — 만료가 흡수)
#   - lease 파일명 패턴: `.claude/ledger/429-lease-<agent_id>.json`
#   - fail-open ALWAYS (exit 0) — 어떤 실패도 SubagentStop 훅 block 금지
#   - graceful degradation: 파일미존재 / 삭제실패 → stderr warning + exit 0
#   - 0 API call, stdlib only, 네트워크 0
#
# 사용:
#   python3 release_429_lease.py --agent-id <id> [--ledger-dir <path>]
#
# 기술 계약:
#   - agent_id: 필수. SubagentStop payload 의 agent_id 필드 (호출자가 유도 책임)
#   - ledger-dir: optional, default = CLAUDE_PROJECT_DIR/.claude/ledger
#   - exit 0 ALWAYS (fail-open 강제)

import argparse
import os
import sys
from pathlib import Path


def release_lease(agent_id: str, ledger_dir: Path) -> None:
    """lease 파일 삭제 (agent_id 단위).

    파일 미존재 = 무해 (release 유실은 reconcile::expire 이 흡수)
    삭제 실패 → stderr warning + return (exit 0 유지)
    """
    try:
        lease_file = ledger_dir / f"429-lease-{agent_id}.json"

        # 파일이 존재하면 삭제
        if lease_file.exists():
            lease_file.unlink()

    except FileNotFoundError:
        # 이미 없음 = 무해
        pass
    except Exception as e:
        # fail-open: stderr warning 만 출력하고 계속 진행
        print(
            f"[codeforge-wrapper-release-429-lease] WARN: lease release failed — {e}",
            file=sys.stderr
        )


def main():
    parser = argparse.ArgumentParser(
        description="429 subagent concurrency lease release"
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
            "[codeforge-wrapper-release-429-lease] WARN: CLAUDE_PROJECT_DIR unset — ledger release skipped",
            file=sys.stderr
        )
        sys.exit(0)

    # release
    release_lease(args.agent_id, ledger_dir)
    sys.exit(0)  # always exit 0


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code if e.code is not None else 0)
    except Exception:
        sys.exit(0)  # catch-all fail-open
