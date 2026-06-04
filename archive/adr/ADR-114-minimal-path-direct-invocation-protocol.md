---
adr_number: 114
title: Minimal path direct invocation protocol — full-lane process escalation fallback
status: Accepted
category: governance
date: 2026-05-26
carrier_story: CFP-1685
is_transitional: false
amends: null
supersedes: null
related_adrs:
  - ADR-039  # inline whitelist closed 4-entry + inline exception per user directive
  - ADR-064  # §결정 5 CFP scope unitary (minimal path direct = single carrier 보존 패턴)
  - ADR-067  # Max FIX 3/3 + implementability reassessment (ESCALATE trigger)
  - ADR-082  # Amendment 29 §결정 1-R mid-Story FIX-loop re-verification (slot collision 차단)
  - ADR-085  # multi-session collaboration protocol (parallel race 영역)
related_stories:
  - CFP-1685  # carrier (escalation_action escalate_user — Option A 사용자 결정)
  - CFP-1110  # 1st applied case (ADR-082 Amd 5 + ADR-071 Amd 6 §결정 17 paired)
  - CFP-1646  # 2nd applied case (ADR-024 Amendment 17 + 1st attempt PRs closed audit trail)
related_files:
  - CLAUDE.md
  - docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md
  - docs/adr/ADR-067-max-fix-implementability-reassessment.md
mechanical_enforcement_actions: []   # declaration-only Wave 1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern). pattern_count ≥ 3 재발 시 follow-up CFP MUST promote.
---

# ADR-114: Minimal path direct invocation protocol — full-lane process escalation fallback

## 상태

Accepted (2026-05-26 KST — CFP-1685 carrier, CFP-1646 PMOAgent retro §6 F4 escalation_action `escalate_user` Option A 사용자 결정)

## 컨텍스트

codeforge full-lane process (요구사항 → 설계 → 설계리뷰 → 구현 → ...) 진행 중 다음 조건 누적 시 inline FIX scope 초과 → ESCALATE_PACKET_INCOMPLETE:
- FIX iteration ≥ 3 (ADR-067 Max FIX 3/3 implementability reassessment trigger)
- N+ ambiguity blocker (parallel race slot collision + branch state ambiguity + origin advance)
- 사용자 directive (minimal path 선택)

기존 ADR-039 inline whitelist 4-entry closed-set (사용자 dialog / TodoWrite scratchpad / Read-only Q&A / Status report) + inline exception per user directive 영역이 **exception path 정형화 부재** — when / how / boundary mechanical wire 미codify.

### 적용 사례 (pattern_count ≥ 2 reach)

- **CFP-1110** (1st applied case, 2026-05-20 KST) — paradox-break minimal path, ADR-082 Amendment 5 + ADR-071 Amendment 6 §결정 17 paired. 사용자 직권 closed-loop break.
- **CFP-1646** (2nd applied case, 2026-05-26 KST) — ADR-024 Amendment 17. full-lane 1st attempt 3 parallel race events + 3 FIX iterations + ESCALATE_PACKET_INCOMPLETE → 사용자 minimal path 선택 → 1st attempt PRs (#1664 + #941) closed + 새 branch + Orchestrator inline write.

## 결정

### 결정 1: Trigger condition (When)

minimal path direct invocation = 다음 3 조건 중 사용자 directive 필수 + 1+ 추가 조건:
- **(필수) 사용자 directive** — 사용자가 minimal path 명시 선택 (AskUserQuestion 응답 또는 직접 directive). ADR-039 inline exception per user directive 영역.
- **(추가 1+) FIX iteration ≥ 3** — ADR-067 Max FIX 3/3 implementability reassessment trigger 도달
- **(추가 1+) N+ ambiguity blocker** — parallel race slot collision (amendment_id / label-registry version / bypass family count) + branch state ambiguity + origin advance 등 inline FIX scope 초과
- **(추가 1+) ESCALATE_PACKET_INCOMPLETE** — lane PL 이 implementability reassessment 후 ESCALATE verdict 반환

사용자 directive 단독으로는 minimal path 발동 불가 (full-lane default 우선) — 1+ 추가 조건 동반 의무. exception path = norm 아님 (full-lane 이 default, minimal path 는 escalation fallback).

### 결정 2: Procedure (How)

minimal path direct 발동 시 Orchestrator 절차:
1. **1st attempt PRs close** — full-lane attempt 의 모든 PR (wrapper + internal-docs) `state:closed` (not_merged), audit trail comment 의무 (closed PRs = 1st attempt audit trail 보존)
2. **새 branch 신설** — `cfp-NNN-v2` (1st attempt branch `cfp-NNN` 와 disjoint, origin/main latest base)
3. **Orchestrator inline write scope** — ADR-039 inline exception per user directive 영역. lane spawn skip. Orchestrator 가 Edit/Write/Bash 직접 산출물 작성.
4. **commit + PR + admin merge** — 1 clean commit, force-push 회피 (새 branch). admin merge (CI fail = pre-existing main drift 시 hotfix-bypass label).

### 결정 3: Boundary (scope limit)

minimal path direct scope 제한:
- **single carrier 보존** — ADR-064 §결정 5 CFP scope unitary 정합. 1 Story = 1 carrier (minimal path 도 CFP scope unitary 유지).
- **ADR amendment stacking 회피** — minimal path 자체가 ADR amendment stacking 발생 안 함 (별 carrier 분리).
- **lane evidence preservation** — Story §10 FIX Ledger + §14 Lane Evidence 에 full-lane attempt audit trail 보존 의무 (FIX iter + ESCALATE + minimal path pivot 기록).
- **mid-Story FIX-loop re-verification** — ADR-082 Amendment 29 §결정 1-R 정합 (FIX iter ≥ 2 시점 amendment slot + version + bypass count 3-tuple 재verify) — minimal path direct re-author 시 slot collision 재발 차단.

### 결정 4: Exception path = norm 아님 (ratchet 강화 invariant)

minimal path direct = exception channel (full-lane default 우선). exception path 가 norm 으로 mutation 되지 않도록:
- minimal path 발동 = 사용자 directive 필수 (Orchestrator self-decide 불가)
- 매 발동 = Story §14 Lane Evidence 에 `[minimal-path-direct: <trigger-condition>]` marker 의무 (audit trail)
- pattern_count ≥ 3 재발 시 mechanical enforcement promotion (when condition lint) — 별 follow-up CFP carrier

## 결과

- full-lane process escalation fallback 정형화 — ESCALATE_PACKET_INCOMPLETE 시 사용자 directive 기반 minimal path 발동 protocol 명확
- exception path = norm 아님 invariant 보존 (full-lane default 우선)
- CFP-1110 + CFP-1646 2 applied case codify (pattern_count ≥ 2 reach)
- lane evidence preservation 의무 (audit trail 보존)

## 해소 기준

N/A — `is_transitional: false` (permanent governance protocol). minimal path direct = full-lane process 의 영구 escalation fallback channel. ADR-058 §결정 7 governance carrier default presumption 정합.

## Wave 2 (Phase 2 PR scope — future carrier)

- mechanical wire — `scripts/lib/check_minimal_path_direct_marker.py` (Story §14 `[minimal-path-direct: ...]` marker presence-grep + trigger condition verify)
- evidence-checks-registry `minimal-path-direct-marker` warning-tier entry
- `hotfix-bypass:minimal-path-direct-marker` family member

## 관련 파일

- CFP-1685 carrier Story
- CFP-1646 PMOAgent retro §6 F4 (escalation_action escalate_user — Option A 사용자 결정)
- `docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` — inline whitelist closed 4-entry + inline exception per user directive
- `docs/adr/ADR-064-decision-principle-mandate.md` — §결정 5 CFP scope unitary
- `docs/adr/ADR-067-max-fix-implementability-reassessment.md` — Max FIX 3/3 + implementability reassessment (ESCALATE trigger)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 29 §결정 1-R mid-Story FIX-loop re-verification (slot collision 차단)
- `docs/adr/ADR-085-multi-session-collaboration-protocol.md` — multi-session collaboration protocol (parallel race 영역)
- CFP-1110 1st applied case + CFP-1646 2nd applied case
