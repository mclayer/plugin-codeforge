"""_expect.py — CFP-2850 테스트 공유 기대 상수 (23-field parity + outcome enum SSOT).

Change Plan §3.7 / §10.A verbatim. sibling test 파일이 `import _expect` 로 사용.
(pytest prepend import mode 가 test dir 를 sys.path 에 주입 → sibling import 가능.)
"""

# 기존 19-field (contract §2 Allow-list — 순서·의미 불변).
CONTRACT_19_FIELDS = (
    "event_id", "schema_version", "timestamp", "story_key", "lane_label",
    "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
    "duration_ms", "tool_call_count", "actor", "parent_event_id",
    "consumer_scope", "event_type", "elapsed_seconds",
)

# 4 신규 additive optional field (19→23, Change Plan §3.7).
NEW_4_FIELDS = ("total_tokens", "model", "outcome", "termination_cause")

CONTRACT_23_FIELDS = CONTRACT_19_FIELDS + NEW_4_FIELDS

# outcome closed-set (completion-quality 축 — stop-event outcome 3값 REUSE + inconclusive additive).
OUTCOME_ENUM = {"success", "inconclusive", "failure", "partial"}

# termination_cause closed-set (mechanism 축). credit-exhaustion = timeout sub-case (독립 top-level 아님).
TERMINATION_CAUSE_ENUM = {"normal", "timeout", "zero_output", "error", "cancelled"}

# stop-event-v1 outcome vocab (harmonize REUSE 원천 — AC-13).
STOP_EVENT_OUTCOME = {"success", "failure", "partial"}
