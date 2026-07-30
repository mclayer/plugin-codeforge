# SPDX-License-Identifier: MIT
# task_notification_usage_golden.py — CFP-2850 §8.7 captured-golden fixture (SSOT)
#
# Change Plan §8.7 (CONDITIONAL-ACTIVE): task-notification `<usage>` 블록은
# UNDOCUMENTED harness surface(harness-internal, spec 미공개)이므로 합성-only 박제
# 금지 — **실 capture fixture 의무**. 아래 값은 전부 실세션 Orchestrator-vantage
# 실측이며 합성치가 아니다. 관측된 실 형상 = 전건 "단일 subagent_tokens aggregate"
# (계약 4-way input/output/cache_creation/cache_read 분해가 아님) → degrade tier-2
# 가 default 경로임을 봉인한다(Change Plan §3.1 degrade ladder tier-2).
#
# ── 진위 (합성-only 아님) ─────────────────────────────────────────────────────
#   본 fixture 의 모든 정수는 실 task-notification 수신 실측이다. 합성/추정 0.
#   Phase 2 payload dump 로 정확 field명·granularity 확정 시 golden 갱신
#   (hollow-gate 방지, OQ-1 실행 의무 — Change Plan §8.7 말미).

# ── 실 capture 3건 (본 세션 Orchestrator-vantage) ────────────────────────────
# [empirical-source: 2026-07-27 실세션 task-notification]
#   각 dict = 단일 task-notification 의 usage block 삼중항 verbatim.
#   subagent_tokens 는 단일 aggregate(4-way 분해 부재 — tier-2 관측 형상).
#   출처 vantage: Orchestrator-vantage relay (원 payload = Orchestrator 세션 수신분, Story §9.4-note 등재).
SESSION_CAPTURES = [
    {"subagent_tokens": 139284, "tool_uses": 25, "duration_ms": 524995},
    {"subagent_tokens": 216489, "tool_uses": 3,  "duration_ms": 531031},
    {"subagent_tokens": 82983,  "tool_uses": 23, "duration_ms": 577422},
]

# ── 설계세션 7 통지 실측 (subagent_tokens 단일 aggregate) ─────────────────────
# [empirical-source: 본 설계세션 task-notification 2026-07-27]
#   Change Plan §2.5 / §8.7 verbatim — 7 deputy task-notification 수신 실측.
#   전부 단일 aggregate → tier-2 default 경로 확증 (4-way 분해 부재).
DESIGN_SESSION_SUBAGENT_TOKENS = [89132, 175559, 153652, 139110, 143361, 139201, 141178]

# ── G2 블록-부재 crash 형상 (tier-3 degrade) ─────────────────────────────────
# [empirical-source: Change Plan §8.7 G2 degrade tier-3 형상]
#   프로세스 crash → usage block 부재 → token=null(unattributed) ∧
#   termination_cause ∈ {zero_output, error}. fail-VISIBLE. 추정 저장 절대 금지.
CRASH_SHAPE = {
    "usage_block_present": False,
    "expected_attribution": "unattributed",
    "expected_total_tokens": None,
    "expected_input_output_cache_null": True,
    "expected_termination_causes": ("zero_output", "error"),
    "degrade_tier": 3,
}

# ── 파생 편의 상수 ────────────────────────────────────────────────────────────
# 전 aggregate 실측 (capture 3 + 설계세션 7 = 10건) — 전건 tier-2 단일 aggregate.
ALL_AGGREGATE_TOKENS = (
    [c["subagent_tokens"] for c in SESSION_CAPTURES] + DESIGN_SESSION_SUBAGENT_TOKENS
)

# 관측된 실 형상 = 전건 단일 aggregate (4-way 분해 0건) — degrade tier-2 default.
OBSERVED_DEGRADE_TIER = 2

# empirical-source 태그 (fixture 진위 self-declare — 매핑표 검증용)
EMPIRICAL_SOURCES = (
    "2026-07-27 실세션 task-notification",
    "본 설계세션 task-notification 2026-07-27",
)

__all__ = [
    "SESSION_CAPTURES",
    "DESIGN_SESSION_SUBAGENT_TOKENS",
    "CRASH_SHAPE",
    "ALL_AGGREGATE_TOKENS",
    "OBSERVED_DEGRADE_TIER",
    "EMPIRICAL_SOURCES",
]
