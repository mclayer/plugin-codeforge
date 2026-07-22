#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# append_spawn_event.py — spawn-event-v1 v1.0 ledger row append (SCHEMA SSOT)
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — per-agent registry(token_usage/cost_usd/tool_usage) + replay event 종류
#       + 경과초 keyed 패턴 차용. enforcement(COST_LIMIT intervention)는 비-차용
#       (codeforge 는 측정·관측만 — ADR-163 §결정 10).
#
# 책임:
#   - spawn-event-v1.md §2 19-field Allow-list + §3 append_rules 를 byte-faithful 구현.
#   - SubagentStop hook 단일 write 지점 (option i) 에서 호출되는 row append CLI.
#   - 본 파일의 _build_row() 가 생성하는 19-key dict = lint/dedup/replay 의 SSOT.
#
# 필수 불변식 (spawn-event-v1.md §3 / Change Plan §8.2 — 절대 위반 금지):
#   - opt-in default false: telemetry.enabled AND channels.spawn_event 둘 다 true 일 때만
#     write. config 부재 = 둘 다 false → no-op (row 0, exit 0). silent always-on 금지.
#   - attribution_confidence default = unattributed. != attributed 면 token/cost = null.
#     추정치 저장 절대 금지 (ADR-119) — naive transcript-sum 도 unattributed 분류.
#   - O_APPEND per-row (H1 lost-update race 회피): os.open(O_APPEND|O_CREAT|O_WRONLY)
#     1 row write. stop-event 의 read-modify-write(whole-file read + os.replace) 패턴
#     복사 금지 (append_stop_event.py _atomic_append = lost-update bug).
#   - actor = top-level session id 의 sha256 (raw session_id 저장 금지 — T-INFO-7).
#     stop-event runtime 의 raw session_id 패턴(append_stop_event.py line 73) 복사 금지.
#   - event_id = deterministic sha256(session_id_hash || agent_id_hash || spawn_seq)
#     (random UUID 금지 — InfraOpArch §11.6, at-least-once idempotent).
#   - timestamp = UTC Z strict (datetime.now(timezone.utc) + %Y-%m-%dT%H:%M:%SZ).
#     +00:00 / bare datetime 불허 (주의: stop-event 의 KST 와 다름 — spawn-event 는 UTC Z).
#   - transcript content / transcript_path 절대 미저장 (T-INFO-5 HARD) — numeric only.
#   - block 금지 graceful degradation: 어떤 예외도 exit 0 (stderr warning).
#   - 0 API call: Anthropic/GitHub/외부 API 호출 금지 — local I/O only.
#
# 사용:
#   python3 append_spawn_event.py \
#     --story-key CFP-2393 --lane-label 구현 --agent-type DeveloperAgent \
#     --session-id <raw_session_id> --agent-id <raw_agent_id> --spawn-seq <int> \
#     --telemetry-enabled --spawn-event-enabled \
#     [--ledger-path <abs>] [--event-type agent_stop] [--consumer-scope wrapper] ...

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows cp949 인코딩 회피: stdout/stderr UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# pricing 파생 (attributed 일 때만 사용). import 실패해도 graceful (cost=None fallback).
try:
    from spawn_event_pricing import cost_usd as _pricing_cost_usd
except Exception:  # pragma: no cover — import path fallback
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from spawn_event_pricing import cost_usd as _pricing_cost_usd
    except Exception:
        _pricing_cost_usd = None


# ─────────────────────── 닫힌집합 enum (contract §2/§3) ───────────────────────

# lane_label closed enum (9값 — label-registry-v2 정합: 8 lane + 없음)
_LANE_LABELS = {
    "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현", "구현-리뷰",
    "구현-테스트", "보안-테스트", "없음",
}
_LANE_FALLBACK = "없음"

# event_type closed enum (replay event 종류 — OMC 차용)
_EVENT_TYPES = {"agent_start", "agent_stop", "tool", "file_touch", "mode_change"}
_EVENT_TYPE_DEFAULT = "agent_stop"  # attribution primary

# attribution_confidence closed enum
_ATTRIBUTION_CONFIDENCE = {"attributed", "unattributed", "unsupported"}
_ATTRIBUTION_DEFAULT = "unattributed"  # default — 정확 source 미확보 시

# consumer_scope closed enum
_CONSUMER_SCOPES = {"wrapper", "consumer"}

# agent_type semi-open fallback (roster 미등재 흡수)
_AGENT_TYPE_FALLBACK = "unknown-agent"

# 19-field 정확 키 순서 (lint/dedup/replay 가 참조하는 SSOT)
_ROW_KEYS = (
    "event_id", "schema_version", "timestamp", "story_key", "lane_label",
    "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
    "duration_ms", "tool_call_count", "actor", "parent_event_id",
    "consumer_scope", "event_type", "elapsed_seconds",
)

_SCHEMA_VERSION = "spawn-event-v1"

# storage path basename 고정 (override 는 parent dir 만 대체 — contract §3 storage_path_override_rule)
_LEDGER_BASENAME = "spawn-event.jsonl"
_DEFAULT_PARENT_REL = os.path.join(".claude", "ledger")


# ─────────────────────── hash 유틸 (raw 저장 금지) ───────────────────────────

def _sha256(value):
    """문자열 sha256 hex digest. 빈 값/None → 빈 문자열 sha256 (안정 결정성)."""
    if value is None:
        value = ""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _compute_event_id(session_id_hash, agent_id_hash, spawn_seq):
    """deterministic event_id = sha256(session_id_hash || agent_id_hash || spawn_seq).

    random UUID 금지 (InfraOpArch §11.6) — 동일 입력 = 동일 id (at-least-once idempotent).
    """
    seq = "" if spawn_seq is None else str(spawn_seq)
    composite = "%s||%s||%s" % (session_id_hash, agent_id_hash, seq)
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


def _normalize_parent_event_id(raw_parent, already_hashed):
    """parent_event_id 정규화 — sha256 reference | null.

    already_hashed=True 면 raw 값이 이미 hash 라 그대로 사용 (단 64-hex sha256 형태 검증).
    already_hashed=False 면 raw 를 hash 처리. 빈 값 → None (raw 부재).
    """
    if raw_parent is None:
        return None
    s = str(raw_parent).strip()
    if not s:
        return None
    if already_hashed:
        # 이미 hash 라고 명시된 경우 — sha256 hex 형태면 그대로, 아니면 안전하게 재hash
        if len(s) == 64 and all(c in "0123456789abcdef" for c in s.lower()):
            return s.lower()
        return _sha256(s)
    return _sha256(s)


# ─────────────────────── enum 정규화 (graceful fallback) ─────────────────────

def _normalize_lane_label(raw):
    """lane_label closed enum — 미매칭 → '없음' fallback (reject 안 함, graceful)."""
    if raw is None:
        return _LANE_FALLBACK
    s = str(raw).strip()
    return s if s in _LANE_LABELS else _LANE_FALLBACK


def _normalize_agent_type(raw):
    """agent_type semi-open — 빈 값/None → unknown-agent fallback.

    roster 검증(membership)은 lint(check_spawn_event_schema.py) 책임 — append 시엔
    전달받은 값 + unknown-agent fallback 만 (semi-open semantics).
    """
    if raw is None:
        return _AGENT_TYPE_FALLBACK
    s = str(raw).strip()
    return s if s else _AGENT_TYPE_FALLBACK


def _normalize_event_type(raw):
    """event_type closed enum — 미매칭 → default agent_stop."""
    if raw is None:
        return _EVENT_TYPE_DEFAULT
    s = str(raw).strip()
    return s if s in _EVENT_TYPES else _EVENT_TYPE_DEFAULT


def _normalize_attribution_confidence(raw):
    """attribution_confidence closed enum — 미매칭 → default unattributed."""
    if raw is None:
        return _ATTRIBUTION_DEFAULT
    s = str(raw).strip()
    return s if s in _ATTRIBUTION_CONFIDENCE else _ATTRIBUTION_DEFAULT


def _normalize_consumer_scope(raw):
    """consumer_scope closed enum. 미지정/미매칭 → CLAUDE_PROJECT_DIR basename 휴리스틱 → wrapper."""
    if raw is not None:
        s = str(raw).strip()
        if s in _CONSUMER_SCOPES:
            return s
    # 미지정 → basename 휴리스틱: plugin-codeforge checkout = wrapper, 그 외 = consumer
    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if proj_dir:
        base = os.path.basename(os.path.normpath(proj_dir)).lower()
        if "plugin-codeforge" in base or base == "codeforge":
            return "wrapper"
        return "consumer"
    return "wrapper"


# ─────────────────────── UTC Z strict timestamp ──────────────────────────────

def _utc_z_now():
    """UTC Z strict timestamp — 2026-06-24T14:22:33Z. +00:00 / bare datetime 불허.

    주의: stop-event 는 KST(+09:00) — spawn-event 는 UTC Z (contract §2 verbatim).
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────── token / cost 파생 (추정 금지) ───────────────────────

def _coerce_int_or_none(value):
    """int 변환 또는 None (실패/빈값 → None)."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _derive_token_cost(attribution_confidence, args):
    """token/cost 파생 — attribution_confidence == attributed 일 때만 numeric.

    그 외 (unattributed/unsupported) = token/cost 전부 null (추정치 저장 절대 금지, ADR-119).
    derivation fn 은 정확 source 미확보 시 unattributed 경로로 null 반환 (NOT 0, NOT 추정).

    Phase 2 본 구현은 SubagentStop payload 에서 정확 token source 를 직접 못 얻으므로
    default unattributed 가 정상 경로 — token flag 가 주어져도 attribution != attributed 면
    null 강제. attributed 는 호출자가 명시적으로 정확 source 를 보장할 때만.

    Returns dict {input_tokens, output_tokens, cache_creation_input_tokens,
                  cache_read_input_tokens, cost_usd}.
    """
    # attributed 가 아니면 전부 null 강제 (token flag 무시 — 추정 합산 금지)
    if attribution_confidence != "attributed":
        return {
            "input_tokens": None,
            "output_tokens": None,
            "cache_creation_input_tokens": None,
            "cache_read_input_tokens": None,
            "cost_usd": None,
        }

    # attributed — 호출자가 정확 source 보장. numeric coerce (실패 시 None).
    input_tokens = _coerce_int_or_none(args.input_tokens)
    output_tokens = _coerce_int_or_none(args.output_tokens)
    cache_creation = _coerce_int_or_none(args.cache_creation_input_tokens)
    cache_read = _coerce_int_or_none(args.cache_read_input_tokens)

    cost = None
    if _pricing_cost_usd is not None and args.model:
        cost = _pricing_cost_usd(
            args.model, input_tokens, output_tokens, cache_creation, cache_read
        )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "cost_usd": cost,
    }


# ─────────────────────── row 구성 (19-field SSOT) ────────────────────────────

def _build_row(args):
    """spawn-event-v1 v1.0 19-field row dict 구성 (Allow-list ONLY — SSOT).

    transcript content / transcript_path 절대 미저장 (T-INFO-5) — numeric/enum/hash only.
    """
    session_id_hash = _sha256(args.session_id)   # actor 원천 (raw 미저장)
    agent_id_hash = _sha256(args.agent_id)        # event_id 원천 (raw 미저장)

    event_id = _compute_event_id(session_id_hash, agent_id_hash, args.spawn_seq)
    attribution_confidence = _normalize_attribution_confidence(args.attribution_confidence)
    token_cost = _derive_token_cost(attribution_confidence, args)

    parent_event_id = _normalize_parent_event_id(
        args.parent_event_id, already_hashed=args.parent_event_id_is_hash
    )

    row = {
        "event_id": event_id,
        "schema_version": _SCHEMA_VERSION,
        "timestamp": _utc_z_now(),
        "story_key": str(args.story_key) if args.story_key else "",
        "lane_label": _normalize_lane_label(args.lane_label),
        "agent_type": _normalize_agent_type(args.agent_type),
        "attribution_confidence": attribution_confidence,
        "input_tokens": token_cost["input_tokens"],
        "output_tokens": token_cost["output_tokens"],
        "cache_creation_input_tokens": token_cost["cache_creation_input_tokens"],
        "cache_read_input_tokens": token_cost["cache_read_input_tokens"],
        "cost_usd": token_cost["cost_usd"],
        "duration_ms": _coerce_int_or_none(args.duration_ms),
        "tool_call_count": _coerce_int_or_none(args.tool_call_count),
        "actor": session_id_hash,  # sha256 (raw session_id 미저장 — T-INFO-7)
        "parent_event_id": parent_event_id,
        "consumer_scope": _normalize_consumer_scope(args.consumer_scope),
        "event_type": _normalize_event_type(args.event_type),
        "elapsed_seconds": _coerce_float_or_none(args.elapsed_seconds),
    }
    return row


def _coerce_float_or_none(value):
    """float 변환 또는 None."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ─────────────────────── storage path 결정 (override = parent dir 대체) ──────

def _resolve_storage_path(args):
    """ledger path 결정 — basename 고정(spawn-event.jsonl), override 는 parent dir 만 대체.

    우선순위:
      1. --ledger-path (명시 override, full path) — test/직접 지정.
      2. telemetry.storage_path override (parent dir 대체) + 고정 basename.
      3. default = ${CLAUDE_PROJECT_DIR}/.claude/ledger/spawn-event.jsonl.

    escape 검사 = best-effort (단순 path join — InfraOpArch §7.4.5 escape 금지는 best-effort).
    """
    # 1. 명시 full path override
    if args.ledger_path:
        return Path(args.ledger_path)

    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "") or "."

    # 2. telemetry.storage_path override (parent dir 대체)
    storage_path = args.storage_path
    if storage_path:
        parent = Path(storage_path)
        if not parent.is_absolute():
            parent = Path(proj_dir) / parent
        return parent / _LEDGER_BASENAME

    # 3. default
    return Path(proj_dir) / _DEFAULT_PARENT_REL / _LEDGER_BASENAME


# ─────────────────────── opt-in gate (default false) ────────────────────────

def _read_config_telemetry(proj_dir):
    """project.yaml / project.json 의 telemetry 블록 읽기. 부재 → 빈 dict (둘 다 false 간주).

    config source = ${CLAUDE_PROJECT_DIR}/project.yaml 또는 project.json.
    어떤 read/parse 실패도 graceful — 빈 dict 반환 (default false 유지).
    """
    if not proj_dir:
        return {}
    candidates = [
        (os.path.join(proj_dir, "project.yaml"), "yaml"),
        (os.path.join(proj_dir, "project.yml"), "yaml"),
        (os.path.join(proj_dir, "project.json"), "json"),
    ]
    for path, kind in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                if kind == "json":
                    data = json.load(f)
                else:
                    import yaml  # lazy — config 존재 시에만 의존
                    data = yaml.safe_load(f)
            if isinstance(data, dict):
                tel = data.get("telemetry")
                return tel if isinstance(tel, dict) else {}
        except Exception:
            # parse 실패 → graceful (default false)
            return {}
    return {}


def _opt_in_enabled(args):
    """opt-in gate — telemetry.enabled AND channels.spawn_event 둘 다 true 일 때만 True.

    gate source 우선:
      - CLI flag --telemetry-enabled / --spawn-event-enabled (명시 opt-in).
      - 아니면 project.yaml/project.json telemetry 블록 (CLAUDE_PROJECT_DIR 기준).
    config 부재 / 둘 중 하나라도 false → False (no-op). silent always-on 금지.

    Returns bool.
    """
    # CLI flag 가 명시되면 그것이 1차 source (둘 다 명시돼야 enable)
    flag_telemetry = args.telemetry_enabled
    flag_channel = args.spawn_event_enabled

    if flag_telemetry or flag_channel:
        # 명시 flag 경로 — 둘 다 true 여야 enable
        return bool(flag_telemetry and flag_channel)

    # flag 미지정 → config 읽기 (default false)
    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    tel = _read_config_telemetry(proj_dir)
    enabled = bool(tel.get("enabled", False))
    channels = tel.get("channels")
    spawn_event = bool(channels.get("spawn_event", False)) if isinstance(channels, dict) else False
    return enabled and spawn_event


# ─────────────────────── O_APPEND per-row write (H1) ─────────────────────────

def _append_jsonl_row(ledger_path, row):
    """O_APPEND per-row write — 1 JSON line + "\\n". lost-update race 회피 (H1).

    os.open(path, O_APPEND | O_CREAT | O_WRONLY, 0o600) → 1 row write → close.
    stop-event 의 read-modify-write(whole-file read + os.replace) 패턴 절대 복사 금지.
    """
    # parent dir 보장
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    # 1 JSON line (ensure_ascii=False — 한글 lane_label 보존)
    line = json.dumps(row, ensure_ascii=False) + "\n"

    # O_APPEND per-row — kernel-atomic append (cross-process lost-update 회피)
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    fd = os.open(str(ledger_path), flags, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)

    # file mode 0600 (Unix; Windows = ACL 영역 외 no-op)
    try:
        os.chmod(str(ledger_path), 0o600)
    except (OSError, AttributeError):
        pass  # Windows no-op


# ─────────────────────── argparse / main ────────────────────────────────────

def _build_parser():
    p = argparse.ArgumentParser(
        description="spawn-event-v1 v1.0 ledger row append (CFP-2393 Phase 2 / Epic CFP-2391 S3)"
    )
    # 식별 / 분류
    p.add_argument("--story-key", default="", help="story_key — e.g. CFP-2393")
    p.add_argument("--lane-label", default="", help="lane_label closed enum (미매칭 → 없음)")
    p.add_argument("--agent-type", default="", help="agent_type semi-open (빈 값 → unknown-agent)")
    p.add_argument("--event-type", default=_EVENT_TYPE_DEFAULT,
                   help="event_type closed enum (default agent_stop)")
    p.add_argument("--consumer-scope", default=None,
                   help="consumer_scope enum {wrapper, consumer} (미지정 → basename 휴리스틱)")

    # event_id / actor 원천 (raw — hash 처리됨)
    p.add_argument("--session-id", default="", help="top-level session id (actor sha256 원천 — raw 미저장)")
    p.add_argument("--agent-id", default="", help="spawn 된 subagent id (event_id sha256 원천 — raw 미저장)")
    p.add_argument("--spawn-seq", default="", help="spawn sequence (event_id 결정성 원천)")
    p.add_argument("--parent-event-id", default=None,
                   help="parent_event_id (nested spawn chain). 기본 = raw 받아 hash")
    p.add_argument("--parent-event-id-is-hash", action="store_true",
                   help="--parent-event-id 가 이미 sha256 hash 면 지정 (그대로 사용)")

    # numeric measurement
    p.add_argument("--duration-ms", default=None, help="duration_ms (int|null)")
    p.add_argument("--tool-call-count", default=None, help="tool_call_count (int|null)")
    p.add_argument("--elapsed-seconds", default=None, help="elapsed_seconds (number|null)")

    # attribution / token (attributed 일 때만 numeric — 그 외 null 강제)
    p.add_argument("--attribution-confidence", default=_ATTRIBUTION_DEFAULT,
                   help="enum {attributed, unattributed, unsupported} (default unattributed)")
    p.add_argument("--input-tokens", default=None, help="input_tokens (attributed 시에만 사용)")
    p.add_argument("--output-tokens", default=None, help="output_tokens (attributed 시에만 사용)")
    p.add_argument("--cache-creation-input-tokens", default=None,
                   help="cache_creation_input_tokens (attributed 시에만)")
    p.add_argument("--cache-read-input-tokens", default=None,
                   help="cache_read_input_tokens (attributed 시에만)")
    p.add_argument("--model", default="", help="cost_usd 파생용 model id (attributed 시 pricing 입력)")

    # storage
    p.add_argument("--ledger-path", default="", help="ledger jsonl full path override (test/직접 지정)")
    p.add_argument("--storage-path", default="",
                   help="telemetry.storage_path override (parent dir 대체, basename 고정)")

    # opt-in gate (default false — silent always-on 금지)
    p.add_argument("--telemetry-enabled", action="store_true",
                   help="telemetry.enabled opt-in flag (channels flag 와 둘 다 필요)")
    p.add_argument("--spawn-event-enabled", action="store_true",
                   help="channels.spawn_event opt-in flag (telemetry flag 와 둘 다 필요)")
    return p


def main():
    parser = _build_parser()
    args = parser.parse_args()

    # graceful degradation: 어떤 예외도 exit 0 (block 금지 — ADR-115 §결정 5 inherit)
    try:
        # opt-in gate — off 면 no-op (row 0, exit 0)
        if not _opt_in_enabled(args):
            # silent no-op (opt-in default false — silent always-on 금지의 역: off 시 write 0)
            sys.exit(0)

        row = _build_row(args)
        ledger_path = _resolve_storage_path(args)
        _append_jsonl_row(ledger_path, row)
    except Exception as exc:
        print(
            "[codeforge-spawn-event] WARN: append failed — %s" % exc,
            file=sys.stderr,
        )
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
