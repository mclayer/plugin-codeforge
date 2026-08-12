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
# append pattern (kernel-atomic single-row append — 공유 primitive 재사용):
#   [구 구현 = lost-update bug] 원장 전체 read → tmpfile 전체 재작성 → os.replace 의
#   read-modify-write 였다. 두 프로세스가 같은 시점에 read 하면 나중 replace 가 앞 writer 의
#   행을 통째로 덮어써 행이 소실됐다. os.replace 는 torn-write 는 막지만 lost-update 는
#   못 막는다. 이 소실은 예외 없이 exit 0 으로 완주하므로 에러 로그로 탐지 불가 —
#   검출 수단은 행 수 대조뿐이었다.
#   [현 구현] append_spawn_event._append_jsonl_row (공유 write primitive, ADR-155
#   Amendment 1) 에 위임 — 원장 read 0, row 당 단일 write:
#     - POSIX: os.open(O_APPEND|O_CREAT|O_WRONLY) + os.write 단일-write = kernel-atomic
#       (커널이 seek-to-EOF 와 write 를 분리 불가하게 직렬화 — POSIX.1-2017 write(), O_APPEND).
#     - Windows: CreateFileW(FILE_APPEND_DATA — FILE_WRITE_DATA 불포함) + WriteFile
#       (MSVCRT O_APPEND = lseek-then-write 비원자라 대체). open 불가 FS →
#       msvcrt.locking(LK_NBLCK) non-blocking fallback + bounded retry + VISIBLE degrade.
#   ★honest ceiling (primitive 의 2축 분리 천장 승계 — 무조건 보증 아님):
#     clobber(lost-update) 축 무손실 범위 = local NTFS/POSIX 정규파일 + row 당 단일-write
#     한정. network share(SMB/NFS)·redirected volume 제외. torn(multi-sector interleave)
#     축은 별개 축으로 아무것도 주장하지 않는다 (row < 4KB 로 bounded 될 뿐).
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
import os
import sys
from pathlib import Path

# ── 공유 write primitive 재사용 (ADR-140 hygiene: reuse-before-write) ──────────
# append_spawn_event._append_jsonl_row = cross-platform kernel-atomic single-row append
# (POSIX O_APPEND / Windows FILE_APPEND_DATA — ADR-155 Amendment 1). spawn-event-v1 ·
# self-context-v1 · dev-process-event-v1 3 consumer 가 이미 동일 import 로 상속 중이며
# stop-event-v1 이 4번째 consumer 다 — 코드 복제 금지(신규 중복 유입 0).
# import 실패도 graceful — _IMPORT_ERROR 로 지연시켜 _atomic_append 가 VISIBLE degrade,
# main() 이 WARN + exit 0 (ADR-115 §결정 5). read-modify-write 로의 silent fallback 절대 금지
# — 그 패턴 자체가 되살리면 안 되는 lost-update bug 다.
try:
    from append_spawn_event import _append_jsonl_row
    _IMPORT_ERROR = None
except Exception:  # pragma: no cover — import path fallback (scripts/lib 미등재 컨텍스트)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from append_spawn_event import _append_jsonl_row  # noqa: E402
        _IMPORT_ERROR = None
    except Exception as _exc2:
        _append_jsonl_row = None
        _IMPORT_ERROR = _exc2


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
    ledger file 에 JSON line 1행 kernel-atomic append (원장 read 0).

    공유 write primitive append_spawn_event._append_jsonl_row 에 위임한다 —
    POSIX os.O_APPEND 단일-write / Windows CreateFileW(FILE_APPEND_DATA) + WriteFile
    (open 불가 FS → msvcrt.locking(LK_NBLCK) non-blocking fallback + bounded retry).
    ledger dir mkdir -p 동등 처리와 file mode 0600 (Unix; Windows = ACL 영역 외 no-op) 도
    primitive 소관이다. 산출 bytes = json.dumps(row, ensure_ascii=False) + "\\n" (utf-8).

    구 구현은 read-modify-write (원장 전체 read → tmpfile 전체 재작성 → os.replace) 였고,
    이는 lost-update bug 였다 — 동시 append 시 나중 replace 가 앞 writer 의 행을 덮어써
    소실시키면서도 예외 없이 exit 0 으로 완주해(에러 로그 탐지 불가) 행 수 대조로만 검출됐다.

    honest ceiling (primitive 천장 승계 — 무조건 보증 아님):
      clobber(lost-update) 축 무손실 범위 = local NTFS/POSIX 정규파일 + row 당 단일-write
      한정. network share(SMB/NFS)·redirected volume 제외. torn(multi-sector interleave)
      축은 별개 축으로 무주장.

    primitive import 실패 시 RuntimeError raise (VISIBLE degrade) — caller 가 stderr WARN 후
    exit 0. read-modify-write 로의 silent fallback 은 하지 않는다 (bug 복원 금지).
    """
    if _IMPORT_ERROR is not None:
        raise RuntimeError(
            "append_spawn_event._append_jsonl_row import 실패 — kernel-atomic append 불가 "
            "(read-modify-write silent fallback 금지: lost-update bug). cause=%r"
            % (_IMPORT_ERROR,)
        )
    _append_jsonl_row(ledger_path, row)


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
