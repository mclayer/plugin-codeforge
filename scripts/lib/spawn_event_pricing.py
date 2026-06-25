#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# spawn_event_pricing.py — spawn-event-v1 per-token pricing 로컬 상수 table (0 API)
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — per-agent token_usage/cost_usd field 구조 차용. enforcement(COST_LIMIT
#       intervention)는 비-차용 (codeforge 는 측정·관측만 — ADR-042 §결정 10).
#
# 책임:
#   - model name → per-token USD pricing constant dict (로컬 상수, 0 API call — T-TAMP-1).
#   - cost_usd() 파생 함수 — token × local pricing constant.
#   - spawn-event-v1.md §2 cache tier 비율 verbatim: cache_creation = 1.25× input tier,
#     cache_read = 0.1× input tier.
#
# 불변식 (spawn-event-v1.md §3 / Change Plan §8.2):
#   - 0 API call: Anthropic/외부 pricing API 호출 절대 금지 — 로컬 상수 only.
#   - token 중 하나라도 None → cost None (unattributed token → unattributed cost).
#   - model 미등재 → None (unknown-model 안전 처리, 추정 금지 — ADR-119).
#
# pricing constant 갱신 = 별도 maintenance (Phase 2). 아래 per-1M-token USD 값은
# Anthropic 공식 pricing 기준 로컬 상수이며 stale 될 수 있음 (값 변동 시 본 table 갱신 필요).

# Windows cp949 인코딩 회피 (ADR-061 portability) — 본 모듈은 stdout 미사용이나 일관성 유지
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── pricing constant table (로컬, 0 API) ────────────────
#
# 단위 = per-1M-token USD (Anthropic 공식 pricing 기준 로컬 상수 — 갱신 필요 가능).
# 키 = model id substring (prefix) 매칭. cache 비율 = §2 verbatim (1.25× / 0.1× input tier).
#
# 주의(갱신 필요): 아래 base input/output 값은 알려진 Anthropic tier pricing 이며
# 가격 변동 시 stale 될 수 있다. 정확한 최신 값은 Anthropic 공식 pricing 페이지 기준으로
# 본 상수를 maintenance 갱신할 것 (0 API 원칙상 런타임 fetch 금지).

# tier 별 per-1M-token USD base (input / output). cache 비율은 input 에서 파생.
_TIER_INPUT_OUTPUT_PER_1M = {
    # claude-opus-4 tier
    "opus": (15.0, 75.0),
    # claude-sonnet tier
    "sonnet": (3.0, 15.0),
    # claude-haiku tier
    "haiku": (0.80, 4.0),
}

# §2 verbatim cache tier 비율 (input tier 기준)
_CACHE_CREATION_MULT = 1.25  # cache_creation = 1.25× input tier
_CACHE_READ_MULT = 0.10      # cache_read = 0.1× input tier

_PER_TOKEN_DIVISOR = 1_000_000.0


def _resolve_tier(model):
    """model id 문자열을 tier key 로 해석 (prefix substring 매칭).

    Returns tier key (str) | None (미등재 — unknown-model).
    """
    if not model:
        return None
    m = str(model).lower()
    # 우선순위 명시 — opus/sonnet/haiku substring 매칭
    for tier in ("opus", "sonnet", "haiku"):
        if tier in m:
            return tier
    return None


def per_token_rates(model):
    """model 의 per-token USD rate 4종 dict 반환 (input/output/cache_creation/cache_read).

    Returns dict {input, output, cache_creation, cache_read} (per-token USD) | None (미등재).
    """
    tier = _resolve_tier(model)
    if tier is None:
        return None
    input_1m, output_1m = _TIER_INPUT_OUTPUT_PER_1M[tier]
    input_per_token = input_1m / _PER_TOKEN_DIVISOR
    output_per_token = output_1m / _PER_TOKEN_DIVISOR
    return {
        "input": input_per_token,
        "output": output_per_token,
        "cache_creation": input_per_token * _CACHE_CREATION_MULT,
        "cache_read": input_per_token * _CACHE_READ_MULT,
    }


def cost_usd(model, input_tokens, output_tokens, cache_creation, cache_read):
    """token × local pricing constant 파생 cost (USD).

    spawn-event-v1.md §3 cost_usd rule:
      - 0 API call (로컬 상수 only).
      - token 중 하나라도 None → None (unattributed → unattributed cost).
      - model 미등재 → None (unknown-model 안전).

    Returns float | None.
    """
    # token 중 하나라도 None → None (unattributed)
    tokens = (input_tokens, output_tokens, cache_creation, cache_read)
    if any(t is None for t in tokens):
        return None

    rates = per_token_rates(model)
    if rates is None:
        return None  # 미등재 model → None (추정 금지)

    try:
        total = (
            int(input_tokens) * rates["input"]
            + int(output_tokens) * rates["output"]
            + int(cache_creation) * rates["cache_creation"]
            + int(cache_read) * rates["cache_read"]
        )
    except (TypeError, ValueError):
        return None

    # 소수 6자리 round (cost 표현 안정성 — accounting 용)
    return round(total, 6)


__all__ = ["cost_usd", "per_token_rates"]
