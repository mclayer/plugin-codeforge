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
#   - spawn-event-v1.md §2 23-field Allow-list + §3 append_rules 를 byte-faithful 구현
#     (CFP-2850 Amendment 4 — 19 → 23, +total_tokens/model/outcome/termination_cause additive).
#   - Orchestrator task-notification 수신 시점 single-write CLI (Amendment 4 writer topology —
#     구 SubagentStop hook single-write option i supersede). 실값 = UTF-8 args-file 채널.
#   - 본 파일의 _build_row() 가 생성하는 23-key dict = lint/dedup/replay 의 SSOT.
#
# 필수 불변식 (spawn-event-v1.md §3 / Change Plan §8.2 — 절대 위반 금지):
#   - opt-in default false: telemetry.enabled AND channels.spawn_event 둘 다 true 일 때만
#     write. config 부재 = 둘 다 false → no-op (row 0, exit 0). silent always-on 금지.
#   - attribution_confidence default = unattributed. != attributed 면 token/cost = null.
#     추정치 저장 절대 금지 (ADR-119) — naive transcript-sum 도 unattributed 분류.
#   - cross-platform kernel-atomic single-row append (H1 완료행 clobber 봉인, ADR-155 Amd1):
#     POSIX = os.O_APPEND 단일-write(이미 kernel-atomic) / Windows = FILE_APPEND_DATA
#     (MSVCRT lseek-then-write 대체 — clobber-free) + open 불가 FS non-blocking lock fallback.
#     stop-event 의 read-modify-write(whole-file read + os.replace) 패턴 복사 금지
#     (append_stop_event.py _atomic_append = lost-update bug). 상세 = _append_jsonl_row.
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
# per_token_rates 는 model semi-open 정규화(roster 해석 가능 여부)에 REUSE — 별도 roster
# 상수 복제 금지 (ADR-140 reuse-before-write). import 실패 시 model 은 pass-through(검증 불가).
try:
    from spawn_event_pricing import cost_usd as _pricing_cost_usd
    from spawn_event_pricing import per_token_rates as _pricing_per_token_rates
except Exception:  # pragma: no cover — import path fallback
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from spawn_event_pricing import cost_usd as _pricing_cost_usd
        from spawn_event_pricing import per_token_rates as _pricing_per_token_rates
    except Exception:
        _pricing_cost_usd = None
        _pricing_per_token_rates = None


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

# model semi-open fallback (CFP-2850 Amendment 4 — pricing roster ∪ unknown-model).
# agent_type semi-open 패턴 REUSE. pricing roster 미해석 non-empty 값 → unknown-model
# 버킷(free-form leak 차단, T-INFO-8). empty/None → null (optional field).
_MODEL_FALLBACK = "unknown-model"

# outcome closed enum (CFP-2850 N9 — completion-quality 축, open_extension:false).
# stop-event-v1 outcome 3값 REUSE + inconclusive additive. SUCCESS-hardcode 금지(ADR-093):
# 미제공/미매칭 → None(null), success 로 default 하지 않는다. record-only.
_OUTCOMES = {"success", "inconclusive", "failure", "partial"}

# termination_cause closed enum (CFP-2850 N9 — mechanism 축).
# timeout = 시간·context·turn·budget/credit-exhaustion 통합 상위. zero_output = tool_uses=0
# silent failure. 미제공/미매칭 → None(null). record-only.
_TERMINATION_CAUSES = {"normal", "timeout", "zero_output", "error", "cancelled"}

# ★T-TAMP-2 (CFP-2850 §7.2) — args-file usage 정수 sanity 상한 (비음수 + overflow guard).
# interim cap (empirical-source: TBD Phase 2 payload dump — §13 dimensional). 위반 시
# attribution=unattributed + token null (추정 대체 금지). 1e12 = 임의 실측 초과 방어 bound.
_USAGE_SANITY_CAP = 1_000_000_000_000

# T-TAMP-2 적용 대상 usage 정수 field (args-file 병합값 검증 — argparse dest 명명).
_USAGE_INT_FIELDS = (
    "total_tokens", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens",
    "duration_ms", "tool_call_count",
)

# 23-field 정확 키 순서 (lint/dedup/replay 가 참조하는 SSOT).
# 기존 19-field 순서·의미 불변(additive) — CFP-2850 Amendment 4 로 하단 4 field append
# (total_tokens·model·outcome·termination_cause). 전부 optional(v1.0 reader skip, ADR-008).
_ROW_KEYS = (
    "event_id", "schema_version", "timestamp", "story_key", "lane_label",
    "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
    "duration_ms", "tool_call_count", "actor", "parent_event_id",
    "consumer_scope", "event_type", "elapsed_seconds",
    # ── CFP-2850 Amendment 4 additive (19 → 23) ──
    "total_tokens", "model", "outcome", "termination_cause",
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

# ★F-CR-014 (구현리뷰 FIX Iter 2) — 미매칭 enum 값 stderr WARN (무음 강등 정직 가시화).
# 구 구현은 closed-set 밖 값을 **조용히** null/fallback 으로 강등해, 호출자 오타(예:
# outcome="succeeded")와 "값 미제공"이 ledger 상 구분 불가했다(둘 다 null). 강등 자체는
# graceful 유지(reject 안 함 — record-only never-block)하되 **강등 사실을 stderr 로 표면화**
# 한다 (silent-success-on-error 금지, ADR-119 정직 표기).
# 경계: **미제공(None/빈 문자열) 은 WARN 대상 아님** — 미제공은 정상 honest-null 이지
# 미매칭이 아니다. stderr 전용 (ledger row 에는 어떤 free-form 도 유입되지 않음 — T-INFO-8).
_WARN_VALUE_MAXLEN = 64


def _warn_enum_fallback(field, raw, fallback_desc):
    """미매칭 enum 값 1건을 stderr 로 표면화 (record 는 계속 — graceful)."""
    s = str(raw)
    if len(s) > _WARN_VALUE_MAXLEN:
        s = s[:_WARN_VALUE_MAXLEN] + "…(truncated)"
    print(
        "[codeforge-spawn-event] WARN: '%s' 미매칭 enum 값 %r → %s (closed-set 밖 — "
        "record 계속, 무음 강등 아님)" % (field, s, fallback_desc),
        file=sys.stderr,
    )


def _normalize_lane_label(raw):
    """lane_label closed enum — 미매칭 → '없음' fallback (reject 안 함, graceful)."""
    if raw is None:
        return _LANE_FALLBACK
    s = str(raw).strip()
    if s in _LANE_LABELS:
        return s
    if s:  # 미제공(빈 값) 은 WARN 대상 아님 — 미매칭만
        _warn_enum_fallback("lane_label", s, "'%s' fallback" % _LANE_FALLBACK)
    return _LANE_FALLBACK


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
    if s in _EVENT_TYPES:
        return s
    if s:
        _warn_enum_fallback("event_type", s, "default '%s'" % _EVENT_TYPE_DEFAULT)
    return _EVENT_TYPE_DEFAULT


def _normalize_model(raw):
    """model semi-open (CFP-2850 Amendment 4) — pricing roster ∪ unknown-model fallback.

    agent_type semi-open 패턴 REUSE. empty/None → None (optional field, null — model 미제공).
    non-empty:
      - pricing roster 해석 가능(_pricing_per_token_rates 有) → 원 model id pass-through
        (AC-9 role·model grouping key 보존).
      - non-empty 이나 pricing roster 미해석 → `unknown-model` fallback bucket
        (free-form string leak 차단 — T-INFO-8, Deny-list 불요).
      - pricing 모듈 import 실패(_pricing_per_token_rates None) → 검증 불가 → pass-through
        (semi-open — membership reject 은 lint 책임, append 는 fallback 만).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None  # 미제공 → null (optional)
    if _pricing_per_token_rates is not None:
        try:
            if _pricing_per_token_rates(s) is None:
                # roster 미해석 → unknown-model bucket (F-CR-014 — 무음 버킷화 가시화)
                _warn_enum_fallback("model", s, "'%s' bucket (pricing roster 미해석)" % _MODEL_FALLBACK)
                return _MODEL_FALLBACK
        except Exception:
            return s  # 검증 불가 → pass-through (semi-open)
    return s


def _normalize_outcome(raw):
    """outcome closed enum (N9) — 미제공/미매칭 → None (null).

    SUCCESS-hardcode 금지 (ADR-093 open_extension:false, SUCCESS 로 default 하지 않음) —
    실측 machine-observable 근거 없이 success 를 날조하지 않는다 (honest-null). record-only.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if s in _OUTCOMES:
        return s
    if s:
        _warn_enum_fallback("outcome", s, "null (미분류)")
    return None


def _normalize_termination_cause(raw):
    """termination_cause closed enum (N9) — 미제공/미매칭 → None (null). record-only."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s in _TERMINATION_CAUSES:
        return s
    if s:
        _warn_enum_fallback("termination_cause", s, "null (미분류)")
    return None


def _normalize_attribution_confidence(raw):
    """attribution_confidence closed enum — 미매칭 → default unattributed."""
    if raw is None:
        return _ATTRIBUTION_DEFAULT
    s = str(raw).strip()
    if s in _ATTRIBUTION_CONFIDENCE:
        return s
    if s:
        _warn_enum_fallback("attribution_confidence", s, "default '%s'" % _ATTRIBUTION_DEFAULT)
    return _ATTRIBUTION_DEFAULT


def _normalize_consumer_scope(raw):
    """consumer_scope closed enum. 미지정/미매칭 → CLAUDE_PROJECT_DIR basename 휴리스틱 → wrapper."""
    if raw is not None:
        s = str(raw).strip()
        if s in _CONSUMER_SCOPES:
            return s
        if s:
            _warn_enum_fallback("consumer_scope", s, "basename 휴리스틱 fallback")
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


# ★F-CR-004 ③ (구현리뷰 FIX Iter 2) — hollow attributed 강등 대상 측정 field.
# attribution_confidence 는 계약 §2 상 **token 측정 source 확보 여부**를 뜻한다
# (contract §2: "attributed = 측정 실측 source 확보 — 4-way 분해 OR aggregate-only",
# §2.2 degrade ladder tier-1/tier-2). 따라서 판정 대상 = total_tokens + 4-way 뿐이다.
# **duration_ms / tool_call_count 는 의도적으로 제외** — 계약 §2.2 tier-3 이
# "전 token null / unattributed / duration_ms=wall-clock 가능" 을 명시하므로,
# duration 존재를 attribution 근거로 세면 tier-3 형상을 attributed 로 오분류하게 된다.
_TOKEN_MEASUREMENT_FIELDS = (
    "total_tokens", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens",
)


def _effective_attribution(attribution_confidence, args):
    """hollow attributed 강등 — attributed 인데 token 측정 field 가 전무하면 unattributed.

    ★F-CR-004 ③: 구 구현은 호출자가 `--attribution-confidence attributed` 만 주고 token 을
    하나도 안 주면 **attributed + 전 token null** 인 hollow row 를 그대로 기록했다. 이는
    "측정 source 를 확보했다" 는 1급 상태 표기와 "측정치가 하나도 없다" 는 실체가 모순인
    row 로, 하류 AC-15(attributed row ≥1 = landing bar) 를 **bare 배선만으로 통과**시키는
    activation≠landing 위장 경로였다. 측정 field 전무 = source 미확보이므로 unattributed 로
    강등한다 (honest-null 정합 — 없는 측정을 있는 것처럼 표기하지 않는다, ADR-119).

    강등 판정 = `_coerce_int_or_none` 재사용 (별 coerce 규칙 복제 금지 — ADR-140):
    비정수 쓰레기값도 coerce 후 None 이므로 hollow 로 동일 취급된다.
    tier-2(aggregate-only, total_tokens 만) 는 **강등 대상 아님** — 측정 1개라도 있으면 attributed.
    """
    if attribution_confidence != "attributed":
        return attribution_confidence
    for field in _TOKEN_MEASUREMENT_FIELDS:
        if _coerce_int_or_none(getattr(args, field, None)) is not None:
            return "attributed"  # 측정 1개 이상 확보 (tier-1 또는 tier-2)
    print(
        "[codeforge-spawn-event] WARN: attributed 선언이나 token 측정 field 전무 "
        "(%s 전부 null) → attribution_confidence=unattributed 강등 "
        "(hollow attributed 금지 — 측정 없는 attributed 는 honest-null 위반)"
        % ", ".join(_TOKEN_MEASUREMENT_FIELDS),
        file=sys.stderr,
    )
    return _ATTRIBUTION_DEFAULT


def _derive_token_cost(attribution_confidence, args):
    """token/cost 파생 — attribution_confidence == attributed 일 때만 numeric.

    그 외 (unattributed/unsupported) = token/cost 전부 null (추정치 저장 절대 금지, ADR-119).
    derivation fn 은 정확 source 미확보 시 unattributed 경로로 null 반환 (NOT 0, NOT 추정).

    Phase 2 본 구현은 SubagentStop payload 에서 정확 token source 를 직접 못 얻으므로
    default unattributed 가 정상 경로 — token flag 가 주어져도 attribution != attributed 면
    null 강제. attributed 는 호출자가 명시적으로 정확 source 를 보장할 때만.

    Returns dict {total_tokens, input_tokens, output_tokens,
                  cache_creation_input_tokens, cache_read_input_tokens, cost_usd}.

    ★CFP-2850 degrade ladder (3-tier, honest-null 불변식 보존):
      - tier-1 (4-way 분해 제공): 4 field populate + cost 파생(model 有) + total_tokens.
      - tier-2 (aggregate-only = 관측된 실 형상, subagent_tokens 단일): total_tokens
        populate + 4-way null + cost null. **model 有여도 cost=null** — cost 파생은
        pricing 이 4-way 부재 시 None 반환(spawn_event_pricing.cost_usd `any(t is None)→None`)
        → 회귀 금지(AC-1 P3 pin). 아래 로직은 4-way 미제공(None)이면 cost None 을 자연 산출.
      - tier-3 (블록 부재/unattributed): 전 token 및 total_tokens null 강제.
    """
    # attributed 가 아니면 전부 null 강제 (token flag 무시 — 추정 합산 금지, tier-3)
    if attribution_confidence != "attributed":
        return {
            "total_tokens": None,
            "input_tokens": None,
            "output_tokens": None,
            "cache_creation_input_tokens": None,
            "cache_read_input_tokens": None,
            "cost_usd": None,
        }

    # attributed — 호출자가 정확 source 보장. numeric coerce (실패 시 None).
    total_tokens = _coerce_int_or_none(args.total_tokens)   # tier-2 aggregate honest 저장
    input_tokens = _coerce_int_or_none(args.input_tokens)
    output_tokens = _coerce_int_or_none(args.output_tokens)
    cache_creation = _coerce_int_or_none(args.cache_creation_input_tokens)
    cache_read = _coerce_int_or_none(args.cache_read_input_tokens)

    # cost 파생 = pricing(model, 4-way). 4-way 中 하나라도 None(tier-2 aggregate-only) →
    # pricing 이 None 반환 → cost null (blended-rate 추정 금지, granularity caveat honest-null).
    cost = None
    if _pricing_cost_usd is not None and args.model:
        cost = _pricing_cost_usd(
            args.model, input_tokens, output_tokens, cache_creation, cache_read
        )

    return {
        "total_tokens": total_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "cost_usd": cost,
    }


# ─────────────────────── row 구성 (19-field SSOT) ────────────────────────────

def _build_row(args):
    """spawn-event-v1 v1.2 23-field row dict 구성 (Allow-list ONLY — SSOT).

    기존 19-field 순서·의미 불변 + CFP-2850 Amendment 4 additive 4 field
    (total_tokens·model·outcome·termination_cause, 전부 numeric/enum — T-INFO-8 free-form 0).
    transcript content / transcript_path 절대 미저장 (T-INFO-5) — numeric/enum/hash only.
    """
    session_id_hash = _sha256(args.session_id)   # actor 원천 (raw 미저장)
    agent_id_hash = _sha256(args.agent_id)        # event_id 원천 (raw 미저장)

    event_id = _compute_event_id(session_id_hash, agent_id_hash, args.spawn_seq)
    attribution_confidence = _normalize_attribution_confidence(args.attribution_confidence)
    # hollow attributed 강등 (F-CR-004 ③) — row 의 attribution_confidence field 도 강등 반영
    attribution_confidence = _effective_attribution(attribution_confidence, args)
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
        # ── CFP-2850 Amendment 4 additive (total_tokens honest-null gated in token_cost) ──
        "total_tokens": token_cost["total_tokens"],
        "model": _normalize_model(args.model),
        "outcome": _normalize_outcome(args.outcome),
        "termination_cause": _normalize_termination_cause(args.termination_cause),
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


# ───────── cross-platform kernel-atomic single-row append (H1 / ADR-155 Amendment 1) ─────────
#   공유 write primitive — spawn-event-v1 · self-context-v1 · dev-process-event-v1 3 consumer 상속.
#   봉인 축 = 완료행 lost-update(clobber): 2-writer 경합에서 한 writer 가 다른 writer 의 완료행을
#   유효 JSON 으로 통째 overwrite 하는 silent 소실(CFP-2817 FIX Iter 3, T-CLOBBER-SILENT).
#     - POSIX(os.name != 'nt'): os.O_APPEND 단일-write 는 이미 kernel-atomic — 커널이 seek-to-EOF 와
#       write 를 분리 불가하게 직렬화(POSIX.1-2017 write(), O_APPEND). 무변경.
#     - Windows(os.name == 'nt'): MSVCRT os.O_APPEND = lseek-then-write(비원자) → 경합 시 clobber.
#       FILE_APPEND_DATA(ctypes CreateFileW, FILE_WRITE_DATA 불포함) 로 대체 → 커널이 append 를
#       단일 atomic 으로 직렬화(lock-free → MCT-51 keepalive-stall 무위험, 원장 read 0 →
#       O_APPEND-pure no-read 불변식 보존). open 불가 FS → msvcrt.locking(LK_NBLCK) non-blocking
#       뮤텍스 fallback + bounded retry + VISIBLE degrade. racy 무잠금 O_APPEND silent fallback 및
#       10초 blocking LK_LOCK 절대 금지(ADR-155 Amendment 1).
#   Honest-ceiling(2축 분리): clobber 축 보장 = local NTFS/POSIX 정규파일 + row당 단일-write 한정.
#     network share(SMB/NFS)·redirected volume 제외. torn(multi-sector interleave) 축 = 별개 무주장
#     (Win32 single-sector atomic·multi-sector 무보장 unless transaction; index row <4KB bounded).

_WIN_APPEND_LOCK_OFFSET = 0xFFFFFF00   # fallback 뮤텍스 sentinel offset(실 데이터 미도달·64/32-bit 안전)
_WIN_LOCK_RETRIES = 8                   # non-blocking lock bounded retry (총 backoff ~0.18s << MCT-51 10s)
_WIN_LOCK_BACKOFF_S = 0.005            # 재시도 backoff base (bounded — LK_LOCK blocking 회피)

_win_fileapi = None  # lazy ctypes 바인딩 캐시 (Windows only — POSIX 미도달, import-cost 0)


class _AppendFallback(Exception):
    """FILE_APPEND_DATA open 불가(예: 일부 network FS) → msvcrt-lock fallback 신호 (내부 전용)."""


def _win_fileapi_bindings():
    """Windows FILE_APPEND_DATA 용 ctypes 바인딩 lazy 초기화 (POSIX 미도달)."""
    global _win_fileapi
    if _win_fileapi is not None:
        return _win_fileapi
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create = k32.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                       wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    write = k32.WriteFile
    write.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD,
                      ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]
    write.restype = wintypes.BOOL
    close = k32.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    _win_fileapi = {
        "ctypes": ctypes, "wintypes": wintypes,
        "CreateFileW": create, "WriteFile": write, "CloseHandle": close,
        "INVALID_HANDLE_VALUE": ctypes.c_void_p(-1).value,
        "FILE_APPEND_DATA": 0x0004,          # FILE_WRITE_DATA(0x0002) 불포함 — append-only access
        "FILE_SHARE_READ": 0x00000001, "FILE_SHARE_WRITE": 0x00000002,
        "OPEN_ALWAYS": 4, "FILE_ATTRIBUTE_NORMAL": 0x00000080,
    }
    return _win_fileapi


def _win_append_file_append_data(path_str, data):
    """Windows kernel-atomic append — CreateFileW(FILE_APPEND_DATA) → WriteFile → CloseHandle.

    dwDesiredAccess=FILE_APPEND_DATA(0x0004, FILE_WRITE_DATA 불포함) → 모든 WriteFile 이 커널
    seek-to-EOF+write 단일 atomic(clobber-free, lock-free). open 불가(INVALID_HANDLE_VALUE) →
    _AppendFallback(→ msvcrt fallback). WriteFile 실패/부분write → OSError raise(VISIBLE —
    절대 silent drop 안 함).
    """
    b = _win_fileapi_bindings()
    ct = b["ctypes"]
    wt = b["wintypes"]
    h = b["CreateFileW"](
        path_str, b["FILE_APPEND_DATA"],
        b["FILE_SHARE_READ"] | b["FILE_SHARE_WRITE"],
        None, b["OPEN_ALWAYS"], b["FILE_ATTRIBUTE_NORMAL"], None,
    )
    if not h or h == b["INVALID_HANDLE_VALUE"]:
        # open 실패 = network FS 등 FILE_APPEND_DATA 미지원 가능 → fallback (racy O_APPEND 아님)
        raise _AppendFallback("CreateFileW(FILE_APPEND_DATA) failed err=%d" % ct.get_last_error())
    try:
        written = wt.DWORD(0)
        ok = b["WriteFile"](h, data, len(data), ct.byref(written), None)
        if not ok:
            raise OSError("WriteFile failed err=%d" % ct.get_last_error())
        if written.value != len(data):
            raise OSError("WriteFile short write %d/%d" % (written.value, len(data)))
    finally:
        b["CloseHandle"](h)


def _win_append_locked_fallback(path_str, data):
    """FILE_APPEND_DATA 불가 FS fallback — msvcrt.locking(LK_NBLCK) non-blocking 뮤텍스 + bounded retry.

    sentinel offset(실 데이터 미도달·write 미발생 — 순수 lock 좌표)에 non-blocking 잠금으로 O_APPEND
    write 를 직렬화 → clobber 방지. LK_NBLCK 만 사용(10초 blocking LK_LOCK 금지 — MCT-51 keepalive
    stall). bounded retry 소진 시 VISIBLE degrade(raise → caller WARN 표면화). racy 무잠금 O_APPEND
    silent fallback 절대 금지.
    """
    import msvcrt
    import time
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    last_exc = None
    for attempt in range(_WIN_LOCK_RETRIES):
        fd = os.open(path_str, flags, 0o600)
        try:
            os.lseek(fd, _WIN_APPEND_LOCK_OFFSET, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)  # non-blocking 뮤텍스 획득 (실패 → OSError)
            except OSError as exc:
                last_exc = exc  # 다른 writer 보유 → bounded backoff 후 재시도
            else:
                try:
                    written = os.write(fd, data)  # O_APPEND seek-to-EOF+write, 뮤텍스가 직렬화
                    if written != len(data):
                        raise OSError("short write %d/%d" % (written, len(data)))
                    return
                finally:
                    os.lseek(fd, _WIN_APPEND_LOCK_OFFSET, os.SEEK_SET)
                    try:
                        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
        finally:
            os.close(fd)
        time.sleep(_WIN_LOCK_BACKOFF_S * (attempt + 1))
    raise OSError(
        "append_spawn_event: FILE_APPEND_DATA 불가 + msvcrt non-blocking lock %d회 재시도 실패 "
        "→ VISIBLE degrade (racy silent O_APPEND fallback·10초 blocking LK_LOCK 금지 — MCT-51). "
        "last=%r" % (_WIN_LOCK_RETRIES, last_exc)
    )


def _append_jsonl_row(ledger_path, row):
    """cross-platform kernel-atomic single-row append — 1 JSON line + "\\n" (H1 / ADR-155 Amd1).

    공유 write primitive(spawn-event-v1 · self-context-v1 · dev-process-event-v1 3 consumer 상속).
    산출 bytes = json.dumps(row, ensure_ascii=False) + "\\n" (utf-8) — 계약/스키마/데이터 byte-compat.
    원장 read 0(O_APPEND-pure). (ledger_path, row) 시그니처 무변경. stop-event 의 read-modify-write
    (whole-file read + os.replace) 패턴 절대 복사 금지.

    완료행 clobber(lost-update) 축 봉인 (CFP-2817 FIX Iter 3):
      - POSIX: os.O_APPEND 단일-write = 이미 kernel-atomic (무변경, no-op).
      - Windows: FILE_APPEND_DATA kernel-atomic append(MSVCRT lseek-then-write 대체) — open 불가
        FS → msvcrt.locking(LK_NBLCK) non-blocking fallback + bounded retry + VISIBLE degrade.
    Honest-ceiling: clobber 축 = local NTFS/POSIX 정규파일 + row당 단일-write. network share
      (SMB/NFS) 제외 · torn(multi-sector) 축 별개 무주장.
    """
    # parent dir 보장
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    # 1 JSON line (ensure_ascii=False — 한글 lane_label 보존). 산출 bytes 불변(byte-compat).
    line = json.dumps(row, ensure_ascii=False) + "\n"
    data = line.encode("utf-8")
    path_str = str(ledger_path)

    if os.name != "nt":
        # POSIX — os.O_APPEND 단일-write 이미 kernel-atomic (POSIX.1-2017 write()). 무변경.
        fd = os.open(path_str, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
    else:
        # Windows — FILE_APPEND_DATA kernel-atomic append; open 불가 FS → non-blocking lock fallback.
        try:
            _win_append_file_append_data(path_str, data)
        except _AppendFallback:
            _win_append_locked_fallback(path_str, data)

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
    p.add_argument("--total-tokens", default=None,
                   help="total_tokens — task-notification subagent_tokens aggregate 실측 "
                        "(CFP-2850, attributed 시에만; tier-2 aggregate-only honest 저장)")
    p.add_argument("--input-tokens", default=None, help="input_tokens (attributed 시에만 사용)")
    p.add_argument("--output-tokens", default=None, help="output_tokens (attributed 시에만 사용)")
    p.add_argument("--cache-creation-input-tokens", default=None,
                   help="cache_creation_input_tokens (attributed 시에만)")
    p.add_argument("--cache-read-input-tokens", default=None,
                   help="cache_read_input_tokens (attributed 시에만)")
    p.add_argument("--model", default="",
                   help="model id — cost_usd 파생 입력 + row model field (CFP-2850, semi-open "
                        "roster ∪ unknown-model). row 에 persist (현행 pricing arg gap 봉합, AC-9)")

    # N9 outcome 분류 (record-only, closed enum — gate 아님)
    p.add_argument("--outcome", default="",
                   help="outcome closed enum {success, inconclusive, failure, partial} "
                        "(CFP-2850 N9 — 미제공/미매칭 → null, SUCCESS-hardcode 금지)")
    p.add_argument("--termination-cause", default="",
                   help="termination_cause closed enum {normal, timeout, zero_output, error, "
                        "cancelled} (CFP-2850 N9 — 미제공/미매칭 → null)")

    # storage
    p.add_argument("--ledger-path", default="", help="ledger jsonl full path override (test/직접 지정)")
    p.add_argument("--storage-path", default="",
                   help="telemetry.storage_path override (parent dir 대체, basename 고정)")

    # ★UTF-8 args-file 채널 (CFP-2850 OQ-3 / T-ELEV-1) — argv=ASCII path 만, 실값·한국어
    #   lane_label content 는 파일 내부 UTF-8 JSON (argv string-interp injection + cp949 mangle 회피).
    p.add_argument("--args-file", default="",
                   help="UTF-8 JSON args-file (ASCII path, BOM 허용) — key=CLI dest"
                        "(dash|underscore) 실값 병합. opt-in gate flag 는 병합 거부(F-CR-009), "
                        "미지의 키는 drop+stderr WARN(F-CR-004). usage 정수는 argv 병합 후 "
                        "T-TAMP-2 validation(비음수+상한, 위반→unattributed)")

    # opt-in gate (default false — silent always-on 금지)
    p.add_argument("--telemetry-enabled", action="store_true",
                   help="telemetry.enabled opt-in flag (channels flag 와 둘 다 필요)")
    p.add_argument("--spawn-event-enabled", action="store_true",
                   help="channels.spawn_event opt-in flag (telemetry flag 와 둘 다 필요)")
    return p


# ─────────────────────── UTF-8 args-file 채널 + T-TAMP-2 (CFP-2850) ──────────

def _usage_within_bounds(value):
    """T-TAMP-2 — usage 정수 비음수 + 상한 sanity cap. None/미제공 = valid(무제약).

    정수 변환 불가 = validation 위반 아님(별도 coerce 단계서 None 처리 — 여기선 통과).
    비음수 위반(음수) / cap 초과 = 위반(False).
    """
    if value is None:
        return True
    try:
        iv = int(value)
    except (TypeError, ValueError):
        return True  # 정수 아님 → coerce None (별개 경로), T-TAMP-2 위반 아님
    return 0 <= iv <= _USAGE_SANITY_CAP


# ★F-CR-009 (구현리뷰 FIX Iter 2) — args-file 이 실을 수 **없는** gate-flag closed-set.
# 구 구현은 args-file 을 opt-in gate **앞**에서 무제한 병합해, args-file 이
# {"telemetry-enabled": true, "spawn-event-enabled": true} 를 실으면 project.yaml 의
# opt-in 설정(ADR-043 §결정 1 default false)을 **파일 하나로 우회**할 수 있었다. gate 결정은
# 오직 (a) 명시 CLI flag 또는 (b) project config 에서만 온다 — args-file 은 **측정 실값 채널**
# 이지 정책 채널이 아니다. 병합 시도는 drop + stderr WARN (silent bypass 금지).
_ARGS_FILE_DENIED_KEYS = frozenset({"telemetry_enabled", "spawn_event_enabled"})


def _validate_usage_bounds(args):
    """T-TAMP-2 — usage 정수 sanity validation (비음수 + 상한 cap). 위반 → unattributed 강제.

    ★F-CR-008 (구현리뷰 FIX Iter 2) — **argv 경로까지 확장**:
    구 구현은 이 validation 을 `_load_args_file` **안**에서만 돌려, args-file 경로로 들어온
    값은 검증하고 argv 로 직접 전달된 동일 값(`--total-tokens -5`)은 무검증 통과하는 비대칭
    구멍이 있었다(같은 field, 다른 전달 매체로 가드 우회). 이제 argv/args-file 병합 **최종값**
    을 단일 지점에서 검증한다 — 검증 로직 복제 0 (ADR-140), 호출 지점 = main() 1곳.

    위반 시 attribution=unattributed 강제 → token/cost null (추정 대체 금지, §7.2 / ADR-119).
    record-only 이므로 reject/비-0 exit 하지 않는다 (ADR-115 never-block).
    """
    for field in _USAGE_INT_FIELDS:
        if not _usage_within_bounds(getattr(args, field, None)):
            print(
                "[codeforge-spawn-event] WARN: usage 정수 '%s' T-TAMP-2 위반 "
                "(음수 또는 상한 %d 초과 — argv/args-file 병합 최종값) → "
                "attribution=unattributed 강제 (token null, 추정 금지)"
                % (field, _USAGE_SANITY_CAP),
                file=sys.stderr,
            )
            args.attribution_confidence = "unattributed"
            return False
    return True


def _load_args_file(args):
    """--args-file UTF-8 JSON 병합 (CFP-2850 OQ-3 / T-ELEV-1).

    argv 는 ASCII path 만; 실값·한국어 lane_label content 는 파일 내부 UTF-8 JSON
    (argv string-interp injection·Windows cp949 mangle 회피 — CFP-2817 D6 선례).
    파일 키 = CLI dest 명 (dash 또는 underscore 허용 — dash→underscore 정규화).

    병합 규율 (구현리뷰 FIX Iter 2):
      - **F-CR-010**: `utf-8-sig` 로 read — BOM 있는 UTF-8(Windows 편집기/PowerShell
        `Out-File -Encoding utf8` 기본 산출)도 수용. BOM 없는 UTF-8 은 동작 불변
        (utf-8-sig 는 BOM 부재 시 utf-8 과 동일 — byte-compat).
      - **F-CR-009**: gate-flag(`_ARGS_FILE_DENIED_KEYS`) 는 병합 거부 + WARN (opt-in 우회 차단).
      - **F-CR-004 ①**: allow-list(argparse dest) 밖 키는 여전히 drop 하되 **stderr WARN 으로
        가시화**. 구 구현은 무음 drop 이라 오타 키(`total-token`)나 계약 drift(신규 field 를
        writer 가 보내는데 append 가 모름)가 조용히 사라지고 row 는 정상처럼 보였다 —
        drop 은 반드시 trace 를 남긴다(silent-success-on-error 금지).
    파싱 실패 = graceful(argv 값 유지 + fail-VISIBLE stderr). exit-0 무손상.
    T-TAMP-2 validation 은 본 함수가 아니라 `_validate_usage_bounds` (argv 경로 공통, F-CR-008).
    """
    path = getattr(args, "args_file", "") or ""
    if not path:
        return
    try:
        # utf-8-sig: BOM 허용 (BOM 부재 시 utf-8 과 동일 — F-CR-010)
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as exc:  # 읽기/파싱 실패 → graceful (fail-VISIBLE)
        print(
            "[codeforge-spawn-event] WARN: args-file 읽기 실패 — %s (argv 값 유지)" % exc,
            file=sys.stderr,
        )
        return
    if not isinstance(data, dict):
        print(
            "[codeforge-spawn-event] WARN: args-file JSON 이 object 아님 — 병합 skip",
            file=sys.stderr,
        )
        return

    # 병합: file 키 → args attr (dash→underscore). allow-list = argparse dest.
    dropped = []   # allow-list 밖 (오타/계약 drift 후보) — F-CR-004 ①
    denied = []    # gate-flag 우회 시도 — F-CR-009
    for key, value in data.items():
        dest = str(key).replace("-", "_")
        if dest == "args_file":
            continue  # 재귀 방지 (args-file 이 또 args-file 지정 무의미)
        if dest in _ARGS_FILE_DENIED_KEYS:
            denied.append(dest)
            continue
        if hasattr(args, dest):
            setattr(args, dest, value)
        else:
            dropped.append(dest)

    if denied:
        print(
            "[codeforge-spawn-event] WARN: args-file 의 opt-in gate flag 병합 거부 — %s "
            "(gate 는 명시 CLI flag 또는 project config 에서만 결정 — args-file 우회 불가, "
            "ADR-043 §결정 1 opt-in default false)" % ", ".join(sorted(set(denied))),
            file=sys.stderr,
        )
    if dropped:
        # 키 이름만 표면화 (값 미출력 — content 유입 0). 과다 시 bound.
        names = sorted(set(dropped))
        shown = names[:20]
        suffix = " …(+%d)" % (len(names) - len(shown)) if len(names) > len(shown) else ""
        print(
            "[codeforge-spawn-event] WARN: args-file 미지의 키 %d개 drop — %s%s "
            "(argparse dest allow-list 밖: 오타 또는 계약 drift 의심 — 무음 drop 아님)"
            % (len(names), ", ".join(shown), suffix),
            file=sys.stderr,
        )


def main():
    parser = _build_parser()
    args = parser.parse_args()

    # graceful degradation: 어떤 예외도 exit 0 (block 금지 — ADR-115 §결정 5 inherit)
    try:
        # UTF-8 args-file 실값 병합. gate-flag 는 병합 대상 아님 (F-CR-009) —
        # 따라서 이 호출은 opt-in 판정에 영향을 주지 못한다 (측정 실값 채널 전용).
        _load_args_file(args)

        # T-TAMP-2 — argv/args-file 병합 최종값 sanity (F-CR-008: argv 경로 포함 단일 지점)
        _validate_usage_bounds(args)

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
