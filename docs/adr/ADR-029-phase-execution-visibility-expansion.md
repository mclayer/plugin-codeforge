---
adr_number: 29
title: Phase execution visibility expansion — sub-step terminal narration
date: 2026-05-05
status: Accepted
category: orchestration
carrier_story: CFP-114
supersedes: null
amendment_log:
  - date: 2026-05-09
    carrier: CFP-283
    section: "§결정 2"
    summary: "Sanitize policy 적용 범위 확장 — narration (stderr) → narration + telemetry ledger unified SSOT (ADR-043 §결정 4 SSOT 분담 narrative + §결정 3 Deny-list regex specifics 정합)"
related_adrs:
  - ADR-042  # measurement channel architecture (sibling — sanitize scope expansion trigger)
  - ADR-043  # telemetry privacy policy (unified sanitize SSOT — §결정 4 SSOT 분담 narrative + §결정 3 Deny-list regex specifics)
is_transitional: false
---

# ADR-029: Phase execution visibility expansion — sub-step terminal narration

## 상태

Accepted (2026-05-05). carrier_story = CFP-114.

## 컨텍스트

CFP-20 (`docs/orchestrator-playbook.md` §14) 가 §0 Live Progress mechanism 도입 — Orchestrator 가 `.claude-work/progress/<KEY>.md` file 에 7-lane × phase 진행을 hierarchical 형식으로 기록. Trigger SSOT 표 (§14.5) 에서 **lane-level event 만 `terminal narration ✅`** (사용자 가시), sub-step event (deputy spawn / return / 병렬 dispatch / R9 subset) 는 `❌ (file only)`.

사용자 directive (2026-05-05) — "phase 와 내부 진행단계를 완료 시마다 출력해주어야 한다". 즉 file-write 외 사용자 가시 출력도 sub-step 수준까지 확장 의무.

Stop discipline 측면 = ADR-022 + ADR-025 + Amendment 1 (CFP-73 / CFP-80) 가 이미 정립 — 5 whitelist 외 stop = `policy_violation` defect. 본 ADR 는 **visibility expansion 만 다룸 (stop 측면 재정립 X)**.

> **(2026-05-08, CFP-135 inline note)**: ADR-022 가 Deprecated 처리 (CFP-134 / ADR-035) — 본 ADR 의 ADR-022 reference 는 history record (Stop discipline 정책 자체는 ADR-025 + Amendment 1 + Amendment 2 SSOT 로 무손상). visibility expansion 정책 무영향.

## 결정 요약

5 결정 freeze. carrier Story = CFP-114.

### 결정 1 — sub-step event narration 의무

`docs/orchestrator-playbook.md` §14.5 Trigger SSOT 표 의 `terminal narration` 컬럼:
- Deputy spawn / Deputy return / 병렬 dispatch (R3·R4·R7·R9) / R9 subset 완료 = `❌ (file only)` → `✅ (narrate)` 로 전환
- Lane-level event (Lane 진입 / PASS / FIX 등 8개) = 변경 없음 (기존 `✅` 유지)
- R10 prefetch (security 1차 layer cache) = **의도적 skip 유지** (사용자 무관 메타)

### 결정 2 — Narration format 표준

```
[<lane-한국어>] <event>: <detail>
```

- 1 sentence (멀티라인 금지)
- stderr only (stdout 미사용 — file-write 와 격리)
- 한국어 lane 이름 (요구사항 / 설계 / 설계 리뷰 / 구현 / 구현 리뷰 / 구현 테스트 / 보안 테스트)
- `<detail>` 은 step 명칭·상태·타임스탬프 등 진행 메타데이터만 포함한다.
- Credential, secret, token, 개인식별정보(PII), 원문 deputy 산출물의 민감 payload 는 narration 에 포함 금지.

예시:
```
[설계] Deputy spawn 6/6 병렬 (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch)
[설계] DataMigrationArchitectAgent return — §11 Migration 전략 + Rollback 경로 author 완료
[설계] ArchitectAgent (chief author) — Change Plan §3 author 시작
[설계 리뷰] R7 병렬 dispatch — DesignReviewPL ∥ DeveloperPL Phase 2 PR 준비
[구현 테스트] R9 functional subset 완료 — 18 test pass, 다음 performance subset 진입
```

> **Amendment 1 (2026-05-09, CFP-283 carrier)** — sanitize policy 적용 범위 확장: 본 §결정 2 sanitize policy = narration (stderr) **+ telemetry ledger (ADR-043 정합) 양쪽 적용**. ADR-043 §결정 4 (SSOT 분담 narrative) + §결정 3 (Deny-list regex specifics) 양쪽 cross-ref. CFP-283 measurement channel (stop-event-v1) 신설로 ledger sanitize 도 동일 정책 inherit — privacy = cross-cutting concern (narration + ledger 동일 정책). future ledger (spawn-event-v1 land 시) 도 동일 적용 의무. ADR-043 §결정 3 = sanitize Deny-list regex 6 pattern SSOT, ADR-043 §결정 4 = ADR-029 ↔ ADR-043 SSOT 분담 narrative (본 §결정 2 = format / 한국어 lane / stderr-only invariant SSOT, ADR-043 §결정 3 = Deny-list specifics). 양쪽 SSOT 변경 시 sync 의무.

### 결정 3 — Stop discipline cross-reference (재정립 X)

본 ADR scope = visibility expansion 만. Stop policy SSOT = **ADR-025 + Amendment 1 + Amendment 2 (CFP-73 / CFP-80 / CFP-135) 그대로 유지** (이전 ~~"ADR-022 + ADR-025 + Amendment 1"~~, ADR-022 Deprecated 후 actor reference remap):

- 5 whitelist (ADR-025 §결정 1 + Amendment 2 정정 후): (1) user environment 변경 의무, (2) destructive action 직전, (3) 진정 unprecedented, (4) decider escalation_required=true (PL pl_recommendation=ESCALATE 또는 사용자 ad-hoc Sonnet escalation), (5) 작업 단위 완료 후 final report
- 위 외 = `policy_violation` defect (ADR-025 §결정)
- Phase boundary stop = `policy_violation_phase_split` (ADR-025 Amendment 1)
- Sub-decision stop = `policy_violation_subdecision` (ADR-025 Amendment 1)

본 ADR 는 사용자 가시성 강화로 stop discipline enforcement 를 **간접 보강** (사용자가 sub-step 진행을 보면 silent stop detect 용이). 직접 정책 변경 X.

### 결정 4 — Verbosity opt-out (consumer overlay flag)

`.claude/_overlay/project.yaml` 의 신규 field:

```yaml
progress_narration_verbosity: full  # 기본값
# 또는 lane_only (CFP-20 기존 동작 — sub-step narrate 안 함, file 만 update)
```

- `full` (default): 모든 sub-step narrate (본 ADR §결정 1 적용)
- `lane_only`: lane-level event 만 narrate (CFP-20 기존 동작)
- 다른 값 = validate_config.py FAIL (unknown 값 reject)

backward-compat: 신규 field 부재 시 = default `full` (행동 변경 — opt-in 이 아닌 opt-out). consumer 가 verbose 출력 원치 않을 시 명시적 `lane_only` 설정 의무.

### 결정 5 — Lane plugin 변경 불요

`docs/orchestrator-playbook.md` §14.1 명시: "**Writer: Orchestrator 단독**". Sub-step event 는 lane plugin agent 가 발생시키나 narration 은 Orchestrator (top-level Claude session) 가 수행. 따라서 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) CLAUDE.md 변경 **불요**.

본 ADR 의 scope = **wrapper repo only**. Cross-repo Epic 패턴 (ADR-020) 미발화.

## 대안 검토

### 대안 A — Lane plugin agent 측 narration 위임

각 lane plugin 의 PL agent prompt 에 "sub-step 완료 시 stderr 1-line narration 의무" 정책 추가.

- **장점**: agent 가 자신의 sub-step 도메인을 가장 잘 앎 → context-rich narration
- **단점**: 6 repo cross-repo Epic, agent prompt 일관성 유지 부담, narration format drift risk
- **거부 이유**: §14.1 의 Writer 단독 invariant 위배. Orchestrator 가 lane plugin return event 받을 때 narrate 하면 충분 — agent 측 추가 책임 불요.

### 대안 B — 파일 출력만 강화 (terminal 변경 X)

`.claude-work/progress/<KEY>.md` 갱신 frequency / detail 만 향상, terminal narration 변경 X.

- **장점**: 변경 minimal
- **단점**: 사용자 directive 미충족 — "출력해주어야" = 가시 출력 의무
- **거부 이유**: 요구사항 미충족.

### 대안 C — UserPromptSubmit hook 확장 (CFP-104) 으로 progress inject

CFP-104 의 UserPromptSubmit hook 이 매 prompt submit 시 §0 progress 일부 inject.

- **장점**: 기존 mechanism 재사용
- **단점**: 사용자 prompt submit 시점만 출력 — sub-step 완료 즉시 출력 안 됨. 요구사항 ("완료 시마다 출력") 미충족
- **거부 이유**: 즉시성 부족.

**채택 = 본 ADR §결정 1-5** (Orchestrator stderr narration 직접 확장).

## 결과

### 영향 file (wrapper repo)

- `docs/orchestrator-playbook.md` §14.5 — Trigger SSOT 표 갱신 (4 sub-step event narration ✅)
- `docs/project-config-schema.md` — `progress_narration_verbosity` field 명세
- `overlay/_overlay/project.yaml.example` — 신규 field 예시 (commented)
- `overlay/hooks/validate_config.py` SCHEMA_RULES — 신규 field 인식
- `CLAUDE.md` — 본 ADR reference (Orchestration 규칙 §)
- `docs/adr/ADR-029-phase-execution-visibility-expansion.md` (본 file)

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) 변경 없음
- §0 Live Progress file (CFP-20) 동작 무변화 — terminal output 만 확장
- Stop discipline (ADR-022 + ADR-025) 정책 무변화 — cross-reference 만

### Reversibility

- Yes — `progress_narration_verbosity: lane_only` 설정으로 CFP-20 기존 동작 복원
- ADR revert 시 sub-step narration 제거 → file-only 동작 복원

## Out-of-scope

- Stop discipline 정책 변경 (ADR-022 + ADR-025 + Amendment 1 SSOT 그대로 — §결정 3 cross-reference 만)
- 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) CLAUDE.md 변경 (§결정 5 — Writer 단독 invariant)
- §0 Live Progress file 동작 (CFP-20 무변화 — terminal output 만 확장)
- Per-deputy narration content 표준 (deputy 별 작성자 책임 — 본 ADR §결정 2 sanitize policy 만 강제)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/orchestrator-playbook.md` §14.5 — Trigger SSOT 표 갱신
- `docs/project-config-schema.md` §2 — `progress_narration_verbosity` field 명세
- `overlay/_overlay/project.yaml.example` — 신규 field 예시
- `overlay/hooks/validate_config.py` SCHEMA_RULES — `_is_progress_narration_verbosity` enum validator
- `docs/consumer-guide.md` — verbosity 사용법
- `CLAUDE.md` — 본 ADR reference

## 관련 ADR

- ADR-013 (codeforge-family dogfood-out policy) — 본 ADR carrier Story = `mclayer/codeforge-internal-docs/wrapper/stories/CFP-114.md`
- ADR-020 (Cross-repo Epic 패턴) — 본 ADR scope = wrapper-only (Epic 미발화)
- ADR-022 (Sonnet decider) — 5 stop whitelist SSOT
- ADR-025 + Amendment 1 (Stop discipline) — `policy_violation` 분류 SSOT
- ADR-027 (Consumer adoption protocol) — consumer 측 SessionStart hook 정책 (independent)
