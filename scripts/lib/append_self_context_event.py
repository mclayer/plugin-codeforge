#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# append_self_context_event.py — self-context-v1 record append (L7 record-only 계측)
#
# Carrier: CFP-2572 Phase 2 (구현) / ADR-142 §결정 4 / ADR-043 Amendment 3.
#
# 책임:
#   - self-context-v1 record 6-field Allow-list 를 spawn-event.jsonl 공유 ledger 에 append.
#     (spawn-event-v1 과 SAME 파일 — record 는 schema_version="self-context-v1" 로 판별.)
#   - Orchestrator-self 장기 세션 context 누적을 record-only proxy telemetry 로 남긴다.
#
# Tier 정직 불변식 (ADR-142 tier-honesty / ADR-043 Amendment 3 (C) — 절대 위반 금지):
#   - L7 = [measurement] record-only. 게이트/블록/deny 언어 0건.
#   - delegation_ratio / pre_tokens = proxy, NOT lead-self ground-truth (platform surface 부재 — ADR-119). record-only, 게이트 아님.
#   - platform 은 live per-turn self-context surface 미제공(P1) — compact_boundary.preTokens(coarse)
#     + delegation-ratio proxy 만 존재. 따라서 live budget gate 불가, coarse proxy 기록만.
#
# 필수 불변식 (ADR-043 Amendment 3 (A)/(B) — 절대 위반 금지):
#   - 6-field Allow-list ONLY (7번째 field 금지):
#       schema_version(const "self-context-v1") / session_id(sha256) / turn_index(int) /
#       delegation_ratio(float 0.0–1.0 coarse-round | null) / pre_tokens(int bucketed | null) /
#       cause_category(CLOSED enum).
#   - FORBIDDEN (T-INFO-8 구조적 차단): file path / transcript 발췌 / tool_input body /
#     free-form reason string 절대 미저장. cause_category = domain-agnostic closed-set —
#     consumer file-path / BC 명 / prompt text 에서 파생 금지.
#   - opt-in default false (§결정 1 상속): telemetry.enabled AND channels.spawn_event 둘 다
#     true 일 때만 write. config 부재 = no-op (row 0, exit 0). silent always-on 금지.
#   - session_id = raw session id 의 sha256 (raw 저장 절대 금지 — T-INFO-7).
#   - pre_tokens = compact_boundary.preTokens 정수만 (transcript raw 미도달 — T-INFO-5 상속).
#   - O_APPEND per-row (H1 lost-update race 회피) — append_spawn_event._append_jsonl_row 재사용.
#   - never-block + fail-VISIBLE: 어떤 예외도 exit 0, 단 silent-success-on-error 금지 —
#     stderr 에 greppable "DROPPED" trace 출력 후 exit 0 (dropped-count 관측 채널).
#   - 0 API call: local I/O only.
#
# idempotency / dedup (7번째 field 미추가 — 6-field cap 고정):
#   - 같은 turn 의 결정론적 content → 같은 row (deterministic emission).
#   - read-side dedup key = (session_id, turn_index) 튜플. event_id field 미추가.
#     --compact-boundary-id 는 hook 이 monotonic turn_index 산출/tiebreak 에 쓸 수 있으나
#     6-field cap 때문에 row 에 미저장 (accepted 한계 — allow-list 고정).
#
# 재사용 (ADR-140 hygiene — 동일 로직 복붙 금지, 기존 함수 호출):
#   - _sha256 / _coerce_int_or_none / _coerce_float_or_none / _opt_in_enabled /
#     _resolve_storage_path / _append_jsonl_row 는 append_spawn_event 에서 import.
#     (gate / storage / append / hash 의 single source of truth 유지. 구조 재설계 아님 —
#      기존 module 무변경, self-context 고유 정규화만 본 파일에 신규 정의.)
#
# 사용:
#   python3 append_self_context_event.py \
#     --session-id <raw_session_id> --turn-index <int> \
#     [--delegation-ratio <0.0-1.0>] [--pre-tokens <int>] \
#     [--cause-category <enum>] [--compact-boundary-id <id>] \
#     --telemetry-enabled --spawn-event-enabled \
#     [--ledger-path <abs>] [--storage-path <parent-dir>]

import argparse
import os
import sys

# Windows cp949 인코딩 회피: stdout/stderr UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────── 재사용 import (ADR-140 — 복붙 금지) ─────────────────
# gate / storage / append / hash = append_spawn_event single source of truth.
# import 실패도 graceful — _IMPORT_ERROR 로 지연 후 main() 의 fail-VISIBLE 경로가 처리.
try:
    from append_spawn_event import (  # noqa: E402
        _sha256,
        _coerce_int_or_none,
        _coerce_float_or_none,
        _opt_in_enabled,
        _resolve_storage_path,
        _append_jsonl_row,
    )
    _IMPORT_ERROR = None
except Exception:  # pragma: no cover — import path fallback (scripts/lib 미등재 컨텍스트)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from append_spawn_event import (  # noqa: E402
            _sha256,
            _coerce_int_or_none,
            _coerce_float_or_none,
            _opt_in_enabled,
            _resolve_storage_path,
            _append_jsonl_row,
        )
        _IMPORT_ERROR = None
    except Exception as _exc2:
        _IMPORT_ERROR = _exc2


# ─────────────────────── self-context-v1 스키마 상수 ─────────────────────────

_SCHEMA_VERSION = "self-context-v1"

# cause_category CLOSED enum (domain-agnostic — path/prompt 파생 금지, SecurityArch 확정)
_CAUSE_CATEGORIES = {
    "read-heavy",
    "synthesis-inline",
    "fix-diagnosis",
    "spawn-dispatch",
    "skill-load",
    "env0-mediation",
    "other",
}
_CAUSE_FALLBACK = "other"

# 6-field 정확 키 순서 (Allow-list ONLY — 7번째 field 금지)
_ROW_KEYS = (
    "schema_version",
    "session_id",
    "turn_index",
    "delegation_ratio",
    "pre_tokens",
    "cause_category",
)

# pre_tokens bucket 폭 (coarse — compact_boundary.preTokens 반올림, raw 정밀도 미저장)
_PRE_TOKENS_BUCKET = 1000


# ─────────────────────── self-context 고유 정규화 ────────────────────────────

def _coerce_turn_index(value):
    """turn_index — int coerce 또는 0 (monotonic, non-nullable). 실패/빈값 → 0."""
    coerced = _coerce_int_or_none(value)
    return coerced if coerced is not None else 0


def _normalize_delegation_ratio(value):
    """delegation_ratio proxy — clamp [0.0, 1.0] + 2-decimal coarse-round. None → None.

    proxy, NOT ground-truth (platform surface 부재 — ADR-119). 추정 정밀도 저장 금지.
    """
    coerced = _coerce_float_or_none(value)
    if coerced is None:
        return None
    clamped = max(0.0, min(1.0, coerced))
    return round(clamped, 2)


def _bucket_pre_tokens(value):
    """pre_tokens — compact_boundary.preTokens 를 최근접 1000 으로 bucket. None → None.

    coarse only (transcript raw 미도달 — T-INFO-5 상속). proxy, ground-truth 아님.
    """
    coerced = _coerce_int_or_none(value)
    if coerced is None:
        return None
    return int(round(coerced / _PRE_TOKENS_BUCKET)) * _PRE_TOKENS_BUCKET


def _normalize_cause_category(raw):
    """cause_category CLOSED enum — 미매칭 → 'other' fallback (reject 안 함, never-reject).

    domain-agnostic 고정 closed-set — path/prompt/BC 명 파생 금지 (ADR-043 Amd3 (A)).
    """
    if raw is None:
        return _CAUSE_FALLBACK
    s = str(raw).strip()
    return s if s in _CAUSE_CATEGORIES else _CAUSE_FALLBACK


# ─────────────────────── row 구성 (6-field SSOT) ─────────────────────────────

def _build_row(args):
    """self-context-v1 6-field row dict 구성 (Allow-list ONLY — SSOT).

    numeric/enum/hash only. file path / transcript / tool_input / free-form string 절대 미저장.
    dedup = deterministic content → 같은 (session_id, turn_index) 튜플 (read-side dedup key).
    """
    row = {
        "schema_version": _SCHEMA_VERSION,
        "session_id": _sha256(args.session_id),  # sha256 (raw 미저장 — T-INFO-7)
        "turn_index": _coerce_turn_index(args.turn_index),
        "delegation_ratio": _normalize_delegation_ratio(args.delegation_ratio),  # proxy
        "pre_tokens": _bucket_pre_tokens(args.pre_tokens),  # proxy (bucketed)
        "cause_category": _normalize_cause_category(args.cause_category),
    }
    return row


# ─────────────────────── argparse / main ────────────────────────────────────

def _build_parser():
    p = argparse.ArgumentParser(
        description="self-context-v1 record append — L7 record-only 계측 "
        "(CFP-2572 Phase 2 / ADR-142 §결정 4 / ADR-043 Amendment 3)"
    )
    # 식별 (raw — sha256 처리됨)
    p.add_argument("--session-id", default="",
                   help="top-level session id (session_id sha256 원천 — raw 미저장)")
    p.add_argument("--turn-index", default="0",
                   help="turn_index (int, monotonic — 실패/빈값 → 0)")

    # proxy 계측 (ground-truth 아님 — record-only)
    p.add_argument("--delegation-ratio", default=None,
                   help="delegation_ratio proxy (float 0.0-1.0, coarse-round | null)")
    p.add_argument("--pre-tokens", default=None,
                   help="pre_tokens (int, compact_boundary.preTokens 출처, bucketed | null)")
    p.add_argument("--cause-category", default=_CAUSE_FALLBACK,
                   help="cause_category CLOSED enum (미매칭 → other)")

    # dedup tiebreak (row 미저장 — 6-field cap. hook 이 turn_index 산출에 사용 가능)
    p.add_argument("--compact-boundary-id", default=None,
                   help="compact_boundary event id (dedup tiebreak, row 미저장 — 6-field cap)")

    # storage (append_spawn_event._resolve_storage_path 재사용 — basename spawn-event.jsonl 고정)
    p.add_argument("--ledger-path", default="",
                   help="ledger jsonl full path override (test/직접 지정)")
    p.add_argument("--storage-path", default="",
                   help="telemetry.storage_path override (parent dir 대체, basename 고정)")

    # opt-in gate (default false — silent always-on 금지. append_spawn_event._opt_in_enabled 재사용)
    p.add_argument("--telemetry-enabled", action="store_true",
                   help="telemetry.enabled opt-in flag (channels flag 와 둘 다 필요)")
    p.add_argument("--spawn-event-enabled", action="store_true",
                   help="channels.spawn_event opt-in flag (telemetry flag 와 둘 다 필요)")
    return p


def main():
    parser = _build_parser()
    args = parser.parse_args()

    # DROPPED trace 용 turn (raw best-effort — 예외가 정규화 전에 나도 표기 가능)
    turn_for_trace = args.turn_index

    # never-block + fail-VISIBLE: 어떤 예외도 exit 0, 단 greppable DROPPED trace 출력.
    # (SystemExit 은 Exception 비-subclass — opt-in no-op 의 sys.exit(0) 는 여기 미포획.)
    try:
        # import 실패 지연 처리 → fail-VISIBLE 경로로 흡수
        if _IMPORT_ERROR is not None:
            raise _IMPORT_ERROR

        # opt-in gate — off 면 no-op (row 0, exit 0). silent always-on 금지의 역.
        if not _opt_in_enabled(args):
            sys.exit(0)

        row = _build_row(args)
        ledger_path = _resolve_storage_path(args)
        _append_jsonl_row(ledger_path, row)
    except Exception as exc:
        # fail-VISIBLE (silent-success-on-error 금지) — greppable DROPPED marker.
        print(
            "[codeforge-self-context] DROPPED turn=%s — %s" % (turn_for_trace, exc),
            file=sys.stderr,
        )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
