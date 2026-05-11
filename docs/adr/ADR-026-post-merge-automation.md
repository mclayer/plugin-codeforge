---
adr_number: 26
title: Post-merge follow-up automation — wrapper Orchestrator workflow + cross-repo Story writer (telemetry only)
status: Accepted
category: Team & Process
date: 2026-05-04
carrier_story: CFP-74
related_files:
  - templates/github-workflows/post-merge-followup.yml
  - scripts/post-merge-story-writer.sh
  - scripts/post-merge-sibling-close.sh
  - scripts/post-merge-telemetry.sh
  - scripts/next-phase.sh
  - docs/orchestrator-playbook.md
  - docs/adr/ADR-022-sonnet-review-verdict-decider.md
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md
  - docs/adr/ADR-011-inter-plugin-contract-drift-detection.md
related_stories:
  - CFP-74
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-026: Post-merge follow-up automation

## 상태

Accepted (2026-05-04). carrier_story = CFP-74. codeforge productivity round 2.

## 컨텍스트

CFP-73 (round 1) Phase 1 (ADR-025 정책 명확화) land 후 사용자 동일 호소 verbatim 재발 (2026-05-04). ADR-025 §결정 1 invariant ("Sonnet decides → automatic proceed") 가 land 됐음에도 stop 빈도 감소 미실현.

Codex+Claude+Sonnet round 2 진단 = primary root cause = **(a) Post-merge manual actions**. 사용자 admin merge 후 Story §9 PASS write + phase label transition + Issue close + sibling PR close 4-5 manual stops per merge. CFP-73 4 PR × 4 actions ≈ 16+ stops 누적 직접 evidence.

Sonnet decider (CFP-74-001) pick=`alpha` (Candidate I single PR + Candidate III telemetry bundling).

## 결정 요약

### 결정 1 — Wrapper Orchestrator post-merge follow-up automation 의무

PR merge event 시 4 action 순차 자동 처리:
1. **Phase label transition** — carrier Issue 의 `phase:*` label 다음 phase 로 transition
2. **Story §9 writer** — internal-docs `wrapper/stories/<KEY>.md` §9 row append (decider:user_admin marker)
3. **Issue close** — `phase:완료` 도달 시 carrier Issue 자동 close
4. **Sibling PR auto-close** — archive marker (`Closed (deferral)` 등) sibling PR 자동 close

각 action 은 idempotent (workflow 재실행 시 중복 처리 안 함).

### 결정 2 — Cross-repo PAT (CFP-71 precedent + ADR-011 정합)

internal-docs 측 cross-repo write 는 organization secret `CODEFORGE_CROSS_REPO_PAT` 사용:
- scope = `contents:write` only on `mclayer/codeforge-internal-docs`
- 90 day expiration + 사용자 수동 갱신 (CFP-71 §7.3 정합)
- workflow log 자동 mask (gh CLI)

### 결정 3 — Telemetry only (no enforcement)

ADR-022 §결정 11 Phase 1 trust model 정합. workflow 는 follow-up 자동 처리만, **사용자 stop 발화 자체를 차단 / refuse 하지 않음**. 측정 채널 = `<internal-docs>/wrapper/post-merge-counters.jsonl` (JSONL append-only, contract_version 1.0). 30+ run 누적 후 PMOAgent retro 분석 → Phase 2 enforcement 도입 여부 별도 CFP.

stop-event-v1 (CFP-73 deferred) 와의 관계: 본 ADR 의 telemetry counter = lite version (post-merge specific). stop-event-v1 full schema 는 CFP-73 deferral 그대로 잔존. 30+ run 후 통합 평가.

### 결정 4 — Disable-by-flag safety + main 직접 push 금지 invariant

- `.codeforge/post-merge-automation.disabled` file 추가 시 workflow 즉시 정지 (운영 emergency 안전망)
- internal-docs 측 cross-repo write 는 **branch 생성 + PR open** 패턴 — main 직접 push 금지 (사용자 admin merge 패턴 유지)
- 본 invariant 위반 시 ADR-024 story-scoped branch policy 위반 = policy_violation defect

## 대안 검토

### 대안 A — 4 sub-decomposition (β)
- I.a / I.b / I.c / I.d 각각 별 PR 분리
- 거부 사유: delivery 시간 4배 증가 (각 sub × Phase 1+2 dogfood). root cause 명확하니 incremental 의미 marginal. Sonnet pick reasoning 정합 (CFP-74-001).

### 대안 B — Enforcement 즉시 도입 (γ)
- workflow 가 사용자 stop 발화 자체 차단 / refuse
- 거부 사유: ADR-022 §결정 8 Phase 2 ROI 평가 SSOT 위반. measurement 없이 enforcement 도입 시 over-correction 위험. 사용자 통제 상실 가능성.

### 대안 C — Story file 단순화 (δ)
- §1-12 sections 축소
- 거부 사유: SSOT 파급 범위 부적합. root cause = post-merge manual actions 와 무관.

## 결과

긍정:
- 사용자 admin merge 후 manual 4-5 stops 자동 처리 → 직접 stop 빈도 감소
- ADR-022 §결정 11 Phase 1 trust model 정합 (telemetry only)
- CFP-73 deferral 의도 보존 (stop-event-v1 full schema 미land)
- disable-by-flag + main 직접 push 금지 invariant 로 운영 위험 mitigation

부정:
- workflow 잘못 처리 시 conflict (사용자 manual write 와 동시 발생) — 단 idempotent dedup + branch 명 unique 로 mitigation
- Cross-repo PAT expiration 의무 (90d) — CFP-71 §3.3 runbook 적용

### Reversibility

Yes. `.codeforge/post-merge-automation.disabled` flag 또는 workflow yaml 삭제 시 즉시 기존 manual 동작 복원.

## Out-of-scope

- Enforcement (whitelist 외 stop refusal) — Phase 2 ROI 평가 후 별도 CFP
- stop-event-v1 full schema (CFP-73 deferral 잔존)
- Consumer overlay path support (PMOAgent retro 후)
- Lane plugin self-emit (S3, 후속 CFP)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `templates/github-workflows/post-merge-followup.yml` (workflow)
- `scripts/post-merge-{story-writer,sibling-close,telemetry,next-phase}.sh` (4 scripts)
- `docs/orchestrator-playbook.md` §16 (narrative SSOT)
- `CLAUDE.md` (workflow list 6 → 7)
- `<internal-docs>/wrapper/post-merge-counters.jsonl` (telemetry, first run 후 신설)

## 관련 ADR

- **ADR-022** §결정 1 User Override hierarchy: workflow 가 merge 결정 안 함, follow-up 만 (사용자 admin merge 결정 보존)
- **ADR-022** §결정 11 Phase 1 trust model: telemetry only, no enforcement hook
- **ADR-024** story-scoped branch policy: cfp-74 branch + Phase 1 PR 분리 정합. internal-docs 측 cross-repo write 도 branch + PR (1 PR 통합 거부 정합)
- **ADR-025** §결정 1: Sonnet pick=alpha 자동 진행 정합
- **ADR-001** review-agent-unification: review separation 변경 없음
- **ADR-008** SemVer: post-merge-counters.jsonl v1.0 = additive minor 가능
- **ADR-011** cross-repo PAT: CFP-71 precedent 정합
- **ADR-045 / CFP-138 Phase 1 follow-up** (2026-05-09): post-merge-telemetry.sh 의 Contents API SHA-based optimistic concurrency pattern 이 [`docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md`](../domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md) Pattern A 로 SSOT 화. retro-attempts.jsonl (ADR-045) 도 동일 Pattern A 의무. 본 ADR-026 implementation (post-merge-telemetry.sh) 는 이미 Pattern A 정합 — 본문 변경 0 (cross-ref only).
