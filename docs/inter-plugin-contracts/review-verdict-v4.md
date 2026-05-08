---
kind: contract
contract_version: "4.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer of FIX routing data)
  - codeforge-review (lane plugin, producer + synthesizer; final gate write authority restored to PL per CFP-137)
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning — SemVer rule)
  - ADR-010 (Inter-plugin Contract Sibling Sync)
  - ADR-022 (superseded carrier — Sonnet review-verdict decider, removed by CFP-137)
authors:
  - CFP-137 — review-verdict v3 → v4 BREAKING (Sonnet decider field removal + agent teams pattern)
---

# review_verdict v4 — Inter-plugin Contract (CFP-137)

`codeforge-review` plugin → `codeforge` core (Orchestrator) 단방향 schema. v3와 BREAKING — **Sonnet decider 관련 모든 필드 제거** (ADR-022 supersede). PL 이 `pl_recommendation` 직접 final value 로 발화 + Story §9 / GitHub gate label / phase transition direct write 권한 복원. NEW: `team_context` (optional — agent teams 패턴 introspection).

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v4.md`: **canonical**
- 본 file (codeforge wrapper repo): sibling reference (ADR-010 sync 의무)

## 1. v3 → v4 BREAKING 변경 요약

| 영역 | v3.0 (CFP-61 ~ CFP-136) | v4.0 (CFP-137 부터) |
|---|---|---|
| `pl_recommendation` 의미 | PL advisory (Sonnet 가 final pick) | **PL final** (PASS / FIX / FIX_DISCRETIONARY / ESCALATE) |
| `sonnet_final_status` | Sonnet binary (PASS\|FIX) | **제거** |
| `decider_decision_ref` | Sonnet packet link (packet_id + model) | **제거** |
| `decision_state` | 8-value state machine (pending_sonnet 등) | **제거** |
| `write_errors` | partial write audit (Orchestrator self-write) | **제거** |
| `writes_completed` | Orchestrator self-write audit | **제거** |
| `review_lane_context` (decision-packet 영역) | populated for trigger 5 | **N/A** (Sonnet trigger 제거) |
| Story §9 / GitHub comment / gate label / phase transition write 주체 | **Orchestrator** (post-Sonnet) | **PL** (direct, CFP-137 회귀) |
| `team_context` | (없음) | NEW — optional agent teams metadata |

## 2. Schema

```yaml
review_verdict:
  contract_version: "4.0"            # BREAKING marker
  lane: design | code | security
  story_key: <STORY_KEY>
  iteration: <int>

  findings:                          # v3 그대로 (배열, severity/category/file/evidence/suggestion)
    - severity: P0 | P1 | P2
      category: <packet category_enum 중 하나>
      file: <path>
      line: <int>
      evidence: <markdown>
      suggestion: <markdown>

  pl_recommendation: PASS | FIX | FIX_DISCRETIONARY | ESCALATE  # PL final value (was advisory in v3)

  team_context:                      # NEW — optional, populated when PL spawns workers as agent team
    team_name: <e.g., TEAM-DESIGN-REVIEW | TEAM-CODE-REVIEW | TEAM-SECURITY-TEST>
    teammate_count: <int>            # PL + worker count (e.g., 3 = PL + Claude worker + Codex worker)
    sendmessage_rounds: <int>        # PL ↔ workers 합의 rounds (0 = single-shot, ≥1 = iterative dialog)
```

## 3. pl_recommendation 의미

| value | 의미 | PL 후속 행동 |
|---|---|---|
| `PASS` | 모든 finding < P0 또는 P0 부재 | Story §9 PASS row append + GitHub `[<lane>-리뷰]` PASS comment + `gate:*-pass` label + phase 다음 단계 transition |
| `FIX` | P0 finding ≥ 1 또는 P1 cluster 임계 초과 | Story §9 FIX row append + Story §10 FIX Ledger append + GitHub `[<lane>-리뷰]` FIX comment + DeveloperPL+ArchitectPL parallel diagnosis spawn 요청 (Orchestrator 경유) |
| `FIX_DISCRETIONARY` | P1 단발성 quality finding (필수 아님) | Story §9 row append (FIX_DISCRETIONARY 명시) + GitHub comment, 다음 단계 transition 가능 (Story author 재량) |
| `ESCALATE` | packet 자체 incomplete / runtime denial / 합의 불가 | Story §9 ESCALATE row + user escalation (lane block) |

PASS / FIX 시 PL 직접 write — Orchestrator self-write 단계 없음 (v3 와 BREAKING 차이).

## 4. team_context (agent teams 패턴, optional)

PL 이 worker 를 agent team 으로 spawn 할 경우 introspection 용. 단발성 single-shot worker spawn 시 `sendmessage_rounds: 0`. Iterative PL ↔ worker dialog (예: Codex finding ambiguity 재질의) 시 `sendmessage_rounds: ≥1`. 본 field 부재 시 = legacy single-shot 패턴 (CFP-137 이전 호환). enforcement 없음 — informational only.

## 5. ESCALATE 처리

`pl_recommendation=ESCALATE` 시:
- PL 이 Story §9 row append (`<escalated>` literal)
- GitHub `[<lane>-리뷰]` ESCALATE comment + user escalation request
- Story §10 / phase transition 차단
- Orchestrator = ESCALATE verdict 수신 시 user 알림 후 lane block

## 6. v4 ↔ canonical sync (ADR-010)

본 file = sibling. canonical = `mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v4.md`. canonical 변경 시 wrapper sibling sync PR 의무 (ADR-010). CI lint = `check-inter-plugin-contracts.sh` (wrapper repo MANIFEST.yaml 기반 completeness 검증).

## 7. v3 deprecate / archive

- v3 status: Active → Archived (CFP-137 머지 직후)
- v3 archive: 6 CFP 무사고 후 (= v4 안정화 확인) — 별도 cleanup CFP에서 file 삭제
- v1 / v2: 기존 archived state 유지

## 8. Decider 정책 변경 (CFP-137 / ADR-022 supersede)

v3 의 Sonnet review-verdict decider (trigger 5) 는 본 v4 에서 제거. ReviewPL 이 finding synthesis + final pick 자체 권한 보유. `pl_recommendation` 직접 final value 로 동작 — Sonnet packet round-trip 부재.

ADR-022 의 Sonnet decider trigger 5 (review-verdict) 는 본 contract bump 와 함께 supersede. 다른 trigger (a substantive 다중 선택지 / b FIX root-cause / c Codex ambiguity / d-constraint 제약 surfacing) 는 별도 ADR 흐름 (영향 받지 않음 — 본 contract 영역 밖).

## 9. SemVer 정당화 (ADR-008)

ADR-008 SemVer 룰 per: `pl_recommendation` 의미 shift (advisory → final), `sonnet_final_status` / `decider_decision_ref` / `decision_state` / `writes_completed` / `write_errors` 5 field 제거 = consumer (Orchestrator) parse 코드 BREAKING. major bump v3 → v4 의무. minor / patch 부족.
