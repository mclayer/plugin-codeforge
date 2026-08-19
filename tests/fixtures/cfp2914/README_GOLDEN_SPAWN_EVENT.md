# GOLD Fixture: spawn-event.jsonl (CFP-2914 Phase 2)

## Provenance

- **Source**: `C:/workspace/mclayer/plugin-codeforge/.claude/ledger/spawn-event.jsonl`
- **SHA256 (first 16 chars)**: `1A3964CF3600F319`
- **Captured**: 2026-08-13 07:34:41 KST
- **Physical line count**: 139
- **Parsed rows (dedup)**: 115
- **Dedup-collapsed rows**: 24

## Schema & Fields (23 fields)

`spawn-event-v1` (CFP-2914 §2.1):
- `actor` `agent_type` `attribution_confidence` `cache_creation_input_tokens` `cache_read_input_tokens`
- `consumer_scope` `cost_usd` `duration_ms` `elapsed_seconds` `event_id` `event_type`
- `input_tokens` `lane_label` `model` `outcome` `output_tokens` `parent_event_id`
- `schema_version` `story_key` `termination_cause` `timestamp` `tool_call_count` `total_tokens`

## Security Scan

**Sensitive values**: 0 rows
- No tokens/credentials found
- No absolute paths in `actor` / `story_key` fields
- Safe to publish as-is

## Form Shape (CP §8.7 原装)

### Real ledger (139 rows, current state) vs CP §8.7 reference (80-row snapshot)

| Form | CP §8.7 Expected | Real 139-row | Difference |
|---|---|---|---|
| `duration_ms: null` | 9 | 19 | +10 (measured growth) |
| `unattributed` (null story_key) | 10 | 0 | -10 (story_key evolution) |
| `(normal, success, tool_call_count: 0)` | 1 | 1 | 0 (unchanged, discriminator preserved) |
| `agent_type: "claude"` | 10 | 12 | +2 (model non-uniformity) |

**Note**: CP §8.7 가 명시한 "4개 형상" 은 **80행 스냅샷** 기준이며, 현재 139행 원장은 진화해 drift 했다. **이 대비는 CP §8.8.1 (규칙 3 도달 0행) 도 거짓**임을 증명한다 ↓

## Critical Finding: MUT-L3b Premise Violated

**CP §8.8.1 원문**: *"규칙 3 단독 도달 행이 원장에서 영원히 불가능하다"* ⇒ MUT-L3b = "GOLD 생존 EXPECTED"

**Real ledger 실측** (139행):
- `tool_call_count: null ∧ termination_cause: !zero_output ∧ outcome: !partial`
- **10건 실제 존재** (규칙 3 단독 도달)

| `(termination_cause, tool_call_count, outcome)` | 건수 | Rule |
|---|---|---|
| `(normal, null, failure)` | 5 | Rule 3 |
| `(error, null, failure)` | 2 | Rule 3 |
| `(timeout, null, partial)` | 2 | Rule 3 + Rule 4 (partial overrides) |
| `(error, null, partial)` | 1 | Rule 3 + Rule 4 |

**Implication**: MUT-L3b expected value **must be "KILL"** not "SURVIVE EXPECTED" (CP 문면은 stale).

## Test Fixture Contract

This file is **read-only diagnostic input** for `test_cfp2914_diagnostic.py`:
- `test_effective_three_state_ladder()`: MUT-L1/L3a/L3b/L4a/L4b/AC-1 실행
- `test_critical_path_mut_1_5()`: 합성 fixture 별도 사용 (GOLD 미포함)

**I-9 원장 read-only 준수**: 이 fixture 는 **복사본** (원본 `C:/workspace/mclayer/plugin-codeforge/.claude/ledger/spawn-event.jsonl` 무수정).

## File Format

**JSONL** (JSON Lines, 한 줄 한 JSON 객체):
- UTF-8 encoding
- LF line ending (`\n` only, CRLF 금지)
- 파싱 실패(malformed JSON) 줄 = 0행
