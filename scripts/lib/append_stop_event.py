#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# append_stop_event.py — stop-event-v1 v1.0 ledger row atomic append
#
# Carrier: CFP-1743 (Story-3 of Epic CFP-1740 — ADR-115 §결정 2·3·5)
#
# 책임:
#   - stop-event-v1 v1.0 JSON row 를 ledger file 에 atomic append
#   - ADR-115 §결정 5 graceful degradation 5층 보장
#   - ADR-061 Amendment 3 외부 .py 파일 의무 (> 5 lines → heredoc 금지)
#   - ADR-061 Amendment 3 CodeQL ReDoS guard (ledger row 작성 자체엔 regex 미사용)
#   - block 금지 (ADR-115 §결정 2) — stdout 출력 없음 (ledger 전용)
#
# 사용:
#   python3 append_stop_event.py \
#     --hook-source stop|subagent-stop \
#     --stop-reason <reason_str> \
#     --session-id <session_id> \
#     --ledger-path <abs_path_to_jsonl>
#
# Graceful degradation:
#   - ledger dir 부재 → mkdir -p 동등 (pathlib.mkdir parents=True exist_ok=True)
#   - ledger write 실패 → stderr warning + exit 0
#   - 어떤 예외도 → exit 0 (Stop hook block 금지)
#
# file mode:
#   - ledger file 생성 시 0600 (Unix) — os.chmod 호출
#   - Windows = ACL 영역 외, os.chmod no-op (declarative comment only)
#
# atomic append pattern (POSIX guarantee):
#   os.replace(tmp_file, target) — write-then-rename pattern.
#   단, POSIX 에서만 진정한 atomic. Windows 에서는 os.replace 가 rename semantics
#   (동일 filesystem 안에서 atomic, cross-filesystem 시 copy+delete).
#   multi-process concurrent append 는 이 패턴으로 보장.
#   단일 jsonl 파일에 두 hook 이 동시 접근할 가능성이 있으므로 tmpfile rename 사용.
#
# stop-event-v1 v1.0 row schema:
#   {
#     "timestamp_kst": "2026-05-27T15:00:00+09:00",
#     "hook_source": "stop" | "subagent-stop",
#     "hook_decision": "record-only",
#     "session_id": "<CLAUDE_SESSION_ID or derived>",
#     "stop_reason": "<from stdin JSON or arg>"
#   }
#
# Story-4 (#1744) = stop-event-v1 v1.0 → v1.1 MINOR bump 예정 (schema 확장).
# 본 파일은 v1.0 row schema SSOT.

import argparse
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path


def _kst_now() -> str:
    """KST ISO 8601 타임스탬프 반환 (ADR-079 §결정 1 display layer KST 강제)."""
    # Python 3.9+ zoneinfo 사용 가능하지만 stdlib 호환성 위해 UTC+9 수동 오프셋
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    kst_offset = datetime.timezone(datetime.timedelta(hours=9))
    kst_now = utc_now.astimezone(kst_offset)
    return kst_now.strftime("%Y-%m-%dT%H:%M:%S+09:00")


def _build_row(hook_source: str, stop_reason: str, session_id: str) -> dict:
    """stop-event-v1 v1.0 ledger row dict 구성."""
    return {
        "timestamp_kst": _kst_now(),
        "hook_source": hook_source,
        "hook_decision": "record-only",
        "session_id": session_id,
        "stop_reason": stop_reason,
    }


def _atomic_append(ledger_path: Path, row: dict) -> None:
    """
    ledger file 에 JSON line atomic append.

    POSIX atomic pattern: 기존 내용 읽기 + 새 row append → tmpfile write → os.replace.
    ledger dir 부재 시 mkdir -p 동등 처리.
    file mode: 0600 (Unix, Windows no-op).
    """
    # dir 보장
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    # 기존 내용 읽기 (파일 부재 시 빈 문자열)
    existing = ""
    if ledger_path.exists():
        existing = ledger_path.read_text(encoding="utf-8")

    # 새 row JSON line
    new_line = json.dumps(row, ensure_ascii=False)

    # 합산 (trailing newline 보장)
    if existing and not existing.endswith("\n"):
        new_content = existing + "\n" + new_line + "\n"
    else:
        new_content = existing + new_line + "\n"

    # tmpfile 에 write → os.replace (atomic rename)
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=str(ledger_path.parent),
        prefix=".stop-event-tmp-",
        suffix=".jsonl",
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_f:
            tmp_f.write(new_content)

        # file mode 0600 (Unix; Windows = no-op, ACL 영역 외)
        try:
            os.chmod(tmp_path, 0o600)
        except (OSError, AttributeError):
            pass  # Windows no-op

        # atomic replace
        os.replace(tmp_path, str(ledger_path))

    except Exception:
        # cleanup tmp on error
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="stop-event-v1 v1.0 ledger row atomic append (CFP-1743)"
    )
    parser.add_argument(
        "--hook-source",
        required=True,
        choices=["stop", "subagent-stop"],
        help="hook_source enum: stop | subagent-stop",
    )
    parser.add_argument(
        "--stop-reason",
        default="",
        help="stop_reason 문자열 (stdin JSON 에서 추출된 값)",
    )
    parser.add_argument(
        "--session-id",
        default="",
        help="CLAUDE_SESSION_ID 또는 CLAUDE_PROJECT_DIR 유래 세션 식별자",
    )
    parser.add_argument(
        "--ledger-path",
        required=True,
        help="ledger jsonl 파일 절대 경로",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger_path)
    row = _build_row(
        hook_source=args.hook_source,
        stop_reason=args.stop_reason,
        session_id=args.session_id,
    )

    try:
        _atomic_append(ledger_path, row)
    except Exception as exc:
        # graceful degradation — 어떤 실패도 exit 0 (ADR-115 §결정 5)
        print(
            f"[codeforge-wrapper-stop] WARN: ledger append failed — {exc}",
            file=sys.stderr,
        )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
