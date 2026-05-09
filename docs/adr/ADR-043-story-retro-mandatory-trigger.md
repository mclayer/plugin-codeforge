---
adr_number: 43
title: Story 완료 회고 의무화 — Phase 2 PR merge 후 PMOAgent 자동 trigger + gate:retro-complete close-blocking
status: Proposed
category: Team & Process
date: 2026-05-09
carrier_story: CFP-138
parent_epic: CFP-134
related_files:
  - templates/github-workflows/retro-mandatory.yml
  - templates/github-workflows/post-merge-followup.yml
  - templates/github-workflows/phase-label-invariant.yml
  - templates/story-page-structure.md
  - docs/inter-plugin-contracts/label-registry-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - scripts/bootstrap-labels.sh
  - CLAUDE.md
related_stories:
  - CFP-134
  - CFP-135
  - CFP-138
related_adrs:
  - ADR-009
  - ADR-013
  - ADR-022
  - ADR-024
  - ADR-025
  - ADR-026
  - ADR-031
  - ADR-035
  - ADR-039
supersedes: null
superseded_by: null
amends:
  - ADR-035 (Wave 2 amendment_id 추가 — D5 Story 완료 회고 의무화 implementation level)
---

# ADR-043: Story 완료 회고 의무화 — Phase 2 PR merge 후 PMOAgent 자동 trigger

## 상태

**Proposed (2026-05-09)** — CFP-138 carrier. CFP-134 Epic 의 Wave 2 child Story (D5 Foundation 결정 implementation). Phase 1 PR merge 시 `Accepted` 전환.

본 ADR 의 spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md) §4.3 (CFP-138 부분).

## 컨텍스트

사용자 directive 2026-05-08 (CFP-134 brainstorming spec turn 9, verbatim):

> "story 완료 회고는 사용자 요청이 없어도 의무로 수행한다."

추가 framing (turn 7-8 정합):

> "codex review와 sonnet decider를 codeforge의 일환으로 보는 것 같은데 그건 아니다. 사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다."

### 현재 상태

- ADR-035 D5 (Foundation 결정) — "PMOAgent 가 Phase 2 PR merge 후 retro 자동 trigger (사용자 요청 불필요). `gate:retro-complete` label 신설 — 미작성 시 Story close 차단" 명시. Implementation = CFP-138 carrier (본 ADR).
- ADR-026 post-merge-followup.yml = 4-action workflow + telemetry-only mode + idempotent + disable-by-flag (`/.codeforge/post-merge-automation.disabled`). 본 ADR 가 5번째 action 추가 또는 **별도 workflow 분리** 결정.
- codeforge-pmo PMOAgent.md = `Edit(docs/retros/**)` + `Edit(docs/stories/**)` + `mcp__github__issue_write` 권한 보유. 새 권한 추가 불필요.
- Story file template `templates/story-page-structure.md` §11 = `- 회고 (PMOAgent 작성)` vague placeholder line 157. schema 갱신 필요.
- `templates/github-workflows/phase-label-invariant.yml` `enforce-terminal-on-close` job = closed event terminal phase 검증 + comment alert (auto-reopen 안 함). retro 의무 별도 workflow 분리 정합.

### Gap

1. **retro automation timing 미정의** — Story close 시점 vs Phase 2 PR merge 시점. ADR-026 post-merge-followup.yml Action 3 (Issue close) 와 race condition 우려.
2. **doc-only Story 의 retro 의무** — Phase 2 PR 부재 시 trigger window 미정의.
3. **partial-write protocol 부재** — PMOAgent retro write 일부 실패 (Epic milestone API fail / network) 시 처리.
4. **Story §11 schema vague** — 현재 `- 회고 (PMOAgent 작성)` = 비-structured. machine-readable 검증 불가.
5. **PMOAgent mandate amendment 부재** — codeforge-pmo CLAUDE.md "Story 완료 시 → 회고 감사" trigger 가 ad-hoc 또는 자동 명시 부재.

## 결정 (D-1 ~ D-8)

### D-1 — Trigger timing = Phase 2 PR merge 직후 + 5분 grace

**결정**: retro-mandatory.yml workflow trigger = `pull_request closed event` (merged=true) + Phase 2 marker (PR title regex `Phase 2` OR `phase:보안-테스트` PR label). 5분 grace period 내 PMOAgent retro write 시간 부여.

5분 grace 후 `gate:retro-complete` label 부재 검출 시 close-blocking 동작 (Issue close 시도 시 자동 reopen + `[PMO]` prefix comment).

**거절된 대안**:
- (b) Story Issue close 시점 trigger — race condition (post-merge-followup.yml Action 3 도 Issue close 시점에 trigger, 동시 발화 시 sequence 불명확)
- (c) `gate:security-test-pass` label 부착 시점 trigger — Phase 1 PR merge 후 phase:설계-리뷰 → phase:구현 transition 영역과 분리 안 됨

**근거**: Issue body §1.3 verbatim "Phase 2 PR merge 완료 → 자동으로 TEAM-RETRO spawn" 정합. 5분 grace = workflow 단일 실행 안 sleep step 또는 scheduled cron retry 영역 (D-4 partial-write protocol 정합).

**Implementation**: retro-mandatory.yml workflow `on: pull_request: types: [closed]` + `if: github.event.pull_request.merged == true` + Phase 2 marker check + `sleep 300` step 또는 별도 scheduled trigger.

### D-2 — Workflow 분리 = 별도 retro-mandatory.yml 신설 (post-merge-followup.yml 미터치)

**결정**: ADR-026 의 post-merge-followup.yml Action 5 추가 안 함. **별도 `templates/github-workflows/retro-mandatory.yml` 신설**.

**거절된 대안**:
- (b) post-merge-followup.yml 안 Action 5 추가 — single-responsibility 위반. 4 action 모두 PR merge 시점 즉시 발화 (continue-on-error + outcome aggregation), retro 는 5분 grace + 2 retry max — trigger window 다름.
- (c) post-merge-followup.yml 안 별도 job 추가 — workflow 안 multi-job 시 disable-by-flag check + telemetry 정합 복잡화.

**근거**:
- single-responsibility — post-merge-followup = 4 즉시 action, retro-mandatory = 5분 grace + retry + close-blocking
- ADR-026 §결정 4 disable-by-flag invariant 보존 — 두 workflow 모두 같은 flag (`.codeforge/post-merge-automation.disabled`) 검사 가능 (D-7 정합)
- retry 시 4 action 동시 재실행 = idempotent invariant 위반 risk (post-merge-followup 의 phase label transition + Issue close 등은 1-shot 의도)
- ADR-026 patterns mirror 가능 (workflow concurrency / continue-on-error / cross-repo PAT / outcome aggregation) — 재발명 회피

**Implementation**: 신규 `templates/github-workflows/retro-mandatory.yml` 작성 + self-app `.github/workflows/retro-mandatory.yml` parity (`scripts/check-workflow-parity.sh` 정합).

### D-3 — Doc-only Story retro 의무 = 모든 Story 적용

**결정**: Phase 1 PR + Phase 2 PR 일반 패턴 + ADR-027 Amendment 1 doc-only Story (Phase 1 단독) 모두 retro 의무. 단 doc-only Story 의 trigger window 는 **Phase 1 PR merge 시점** (Phase 2 부재 시).

**거절된 대안**:
- (b) doc-only Story 면제 — Story-level 일관성 약화. 미래 doc 변경 retroactive audit 시 retro 부재로 학습 누적 부족.

**근거**: Story-level 일관성 우선. doc-only Story 도 retro write 의무 (간단 retro 라도). retro file = `<sprint>-cfp-NNN-<slug>.md` naming — Phase 1 PR merge 시점에 작성 가능.

**Implementation**: retro-mandatory.yml workflow 가 Phase 2 marker 부재 시 fallback = Phase 1 PR merge + Story Issue close 시점 trigger. 또는 doc-only Story = `phase:보안-테스트` 도달 시점 (Phase 1 PR merge 후 phase progression 가능). 본 ADR 결정 = doc-only Story 도 retro 의무.

### D-4 — Partial-write protocol = 4 attempts (1 initial + 3 retries) + ESCALATE + close-blocking 유지

**결정**: PMOAgent retro write 시 partial failure (예: retro file write 성공 + Story §11 update 성공 — Epic milestone API 호출 fail) 발생 시 retry policy.

**Cumulative offset spec from PR merge timestamp** (verbatim — 6 source sync SSOT, FIX iter 1 F-1 fix):

| Attempt | Wait from previous | Cumulative offset from PR merge | Action |
|---|---|---|---|
| **First attempt** (initial) | — (5min grace) | **+5min** | PMOAgent retro write 시도 |
| **Retry 1** | +5min wait | **+10min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn |
| **Retry 2** | +10min wait | **+20min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn |
| **Retry 3** | +15min wait | **+35min** | gate:retro-complete 부재 검출 시 PMOAgent re-spawn (final attempt) |
| **ESCALATE** | — | **+35min** 후 | retry 3 fail 시 `[PMO] Retro automation failed after 3 retries — 사용자 ESCALATE` comment + `gate:retro-complete` 미부착 (Story close 차단 유지) |

**Total attempts = 4** (1 initial + 3 retries).
**Total max latency from PR merge to ESCALATE = 35min** (5min grace + 5+10+15 retry waits).

35min 후 Story close 차단 유지 + 사용자 manual 복구 후 PMOAgent re-spawn → 정상 경로 복귀.

**거절된 대안**:
- (b) retry 1회 + ESCALATE — transient failure (network blip / GitHub API 5xx) 자동 복구 부족
- (c) infinite retry — DoS risk (PR 다수 merge 시 worker thread 누적)
- (d) close-blocking 해제 — silent failure 차단 무력화 (mandate forcing function 의미 상실)

**근거**: 5min grace = first attempt budget. 5/10/15 wait = 점진 증가 (exponential backoff lite). 35min max latency 후 사용자 ESCALATE = silent failure 차단 정합.

**Idempotency invariant** (§11.6 cross-ref): 매 attempt 가 idempotent — retro file 존재 검사 (PMOAgent re-spawn 시 existing file 검출 + abort 또는 append) + `gh label add` no-op (이미 부착 시) + Issue close-blocking auto-reopen idempotent comment (EXISTING_ALERT check, retro-mandatory.yml workflow 안).

**Phase 2 implementation spec** (F-5 fix — DesignReview iter 1 P1, Phase 2 PR scope):
- **State management mechanism**: `<internal-docs>/wrapper/retro-attempts.jsonl` (Phase 2 신설, ADR-026 post-merge-counters.jsonl 와 별도 channel). per-Story attempt counter 누적 — schema = `{story_key, pr_ref, attempt_n: 1|2|3|4, last_attempted_at: ISO8601, status: in_flight|success|failed|escalated}`.
- **Re-trigger mechanism**: GitHub Actions `workflow_run` event (workflow self re-trigger) 또는 scheduled cron `*/5 * * * *` (every 5min, jsonl state 검사 후 due retry execute). Phase 1 PR scope 에서는 first attempt (5min grace) 만 implement — retry 영역 = Phase 2 PR scope.
- **Max attempts state machine**: 4번째 attempt fail 시 `escalated` state 진입 + ESCALATE comment + close-blocking 유지.

Phase 1 PR scope (본 ADR carrier) = first attempt 5min grace + close-blocking action 만. retry state machine = Phase 2 PR scope deferred.

### D-5 — Story §11 schema migration = 신규 Story 부터 적용 (backward compat)

**결정**: `templates/story-page-structure.md` §11 schema 갱신 — 현재 `- 회고 (PMOAgent 작성)` line 157 vague placeholder → 4 field structured:

```markdown
- 회고 (PMOAgent 작성):
    retro_file: <relative-path-or-cross-repo-url>
    retro_summary: <one-paragraph-summary, max 500자>
    learnings_count: <integer >= 0>
    feedback_back_to_codeforge: <Issue link list or empty []>
```

**Migration**: 신규 Story (CFP-138 merge 이후 close) 부터 신규 schema 적용. 기존 close Story file 100+ 의 §11 영역 = `- 회고 (...)` 불완전 string 유지 (retroactive 미처리).

**Backward compat 검증**: `scripts/check-doc-section-schema.sh` 가 PMOAgent owner section 검증 — Story frontmatter `created_at >= CFP-138 merge date` 또는 status:open at CFP-138 merge time 검출 시 strict mode. 그 외 lenient mode (vague placeholder OK).

**거절된 대안**:
- (b) 모든 close Story retroactive backfill — 100+ Story 변조 risk + Story §1 verbatim invariant 위반 risk
- (c) schema 미터치 (vague placeholder 유지) — machine-readable 검증 불가

**근거**: Issue body §1.3 verbatim "retroactive 미처리" 정합 + ADR-013 dogfood-out / append-only invariant 정합.

### D-6 — label-registry MINOR bump = v1.4 → v1.5 (gate:retro-complete entry)

**결정**: `docs/inter-plugin-contracts/label-registry-v1.md` v1.4 → v1.5 (additive minor, ADR-008 SemVer 정합). `gate:retro-complete` entry 추가:

```yaml
- name: gate:retro-complete
  category: gate
  color: "0e8a16"
  description: "Story 완료 회고 작성됨 (PMOAgent self-write — CFP-138 / ADR-043 mandate)"
  single_active: false
  attach_owner_plugin: "codeforge-pmo (PMOAgent self-write)"
```

`scripts/bootstrap-labels.sh` 에 `create_label "gate:retro-complete" "0e8a16" "..."` 1줄 append + line 51 echo "29종" → "30종" 갱신.

**Idempotency invariant**: `gh label create ... 2>/dev/null || gh label edit ... 2>/dev/null` 패턴 유지 — 기존 30+ label 무수정.

**MANIFEST.yaml** entry version update (label-registry-v1: "1.4" → "1.5").

**거절된 대안**:
- (b) MAJOR bump v2.0 — 기존 label 삭제 / rename 없음 (additive minor 충분)

**근거**: ADR-008 SemVer (additive minor). consumer breaking 없음 — 기존 label 유지.

### D-7 — Disable-by-flag safety = `.codeforge/post-merge-automation.disabled` 단일 flag 공유

**결정**: retro-mandatory.yml workflow 도 ADR-026 와 동일한 `.codeforge/post-merge-automation.disabled` flag 검사. 두 workflow 모두 같은 flag 단일 disable.

**거절된 대안**:
- (b) 별도 flag `.codeforge/retro-mandatory.disabled` — 운영 복잡성 증가, ADR-026 §결정 4 invariant 의 simplicity 정합 약화

**근거**: ADR-026 §결정 4 invariant (운영 emergency 안전망) 정합. 단일 flag = post-merge automation 전체 disable (4 action + retro mandate 양쪽). 부분 disable 필요 시 workflow yaml 직접 수정 (별도 PR).

### D-8 — Sibling sync 의무 = codeforge-pmo plugin Phase 1 PR pair

**결정**: ADR-010 sibling sync — wrapper Phase 1 PR 와 codeforge-pmo plugin Phase 1 PR 같은 Story 안 같이 merge 의무.

**Sibling 영역**:
- codeforge-pmo `CLAUDE.md` "Self-write 책임" 표 — `docs/retros/<sprint>.md` row trigger 컬럼 amendment (`story_completion (Phase 2 PR merge 자동, CFP-138) / cross_story_audit_request`)
- codeforge-pmo `agents/PMOAgent.md` 호출 시점 표 amendment (line 56-60 — `Story 완료 시 (Phase 2 PR merge 후 5분 grace, CFP-138 자동 trigger)`)
- codeforge-pmo `agents/PMOAgent.md` 책임 상세 §2 Story 완료 회고 감사 영역 → mandate 자동 trigger 명시

**거절된 대안**:
- (b) wrapper-only PR — codeforge-pmo plugin 정합 부재 시 PMOAgent agent file invalid (mandate amendment 미반영, agent 가 자기 역할 trigger 모름)

**근거**: ADR-010 cross-plugin sibling sync 정합. Phase 1 PR pair = same Story 안 ATOMIC merge.

## 대안 검토

### 대안 A — Workflow 통합 (post-merge-followup Action 5 추가, β)

- post-merge-followup.yml 의 4 action 후 Action 5 (gate:retro-complete check + close-blocking) 추가
- 거부 사유:
  - single-responsibility 위반
  - retry 시 4 action 동시 재실행 = idempotent 위반 risk
  - 5분 grace + 2 retry max trigger window 가 즉시-실행 4 action 와 다름
  - D-2 결정 정합

### 대안 B — Story Issue close 시점 trigger (γ)

- post-merge-followup.yml Action 3 가 Issue close 후 retro 검증
- 거부 사유: race condition (Action 3 와 retro 검증 동시 발화 시 sequence 불명확). D-1 결정 정합.

### 대안 C — Retroactive backfill (δ)

- 본 ADR merge 후 기존 close Story 100+ 에 retro 작성
- 거부 사유:
  - Story §1 verbatim invariant 위반 risk (PMOAgent edit 시 §1 line range 변조 우려)
  - 100+ Story 변조 risk
  - Issue body §1.3 verbatim "retroactive 미처리" 정합
  - 별도 backfill CFP 가능 (선택 — out-of-scope)

### 대안 D — Doc-only Story 면제 (ε)

- doc-only Story (Phase 2 부재) retro 의무 면제
- 거부 사유: Story-level 일관성 약화. D-3 결정 정합.

## 결과

긍정:
- ADR-035 D5 Foundation 결정 implementation 충족
- 사용자 directive (turn 9) verbatim 정합
- ADR-022 Deprecated (Sonnet decider 자동 발동 무효) framing 와 같은 Wave 2 진행
- ADR-026 post-merge-followup.yml 미터치 (single-responsibility 보존)
- bootstrap-labels.sh idempotency 보존 (기존 30+ label 무수정)
- backward compat (기존 Story file retroactive 미처리)
- forcing function 동작 (close-blocking + 4 attempts (1 initial + 3 retries) + 35min max latency + ESCALATE)

부정:
- 5min grace + 4 attempts (1 initial + 3 retries) cumulative = 35min max latency — 정상 경로에서 retro write 첫 attempt 성공 시 0-5min (acceptable)
- Story close 시점 다소 지연 (5분 grace + PMOAgent spawn time)
- Cross-repo PAT (CODEFORGE_CROSS_REPO_PAT) expiration 의존 — ADR-026 §결정 2 90d runbook 정합
- Doc-only Story trigger window 정의 복잡 (Phase 2 marker fallback) — D-3 implementation 정밀화 의무

### Reversibility

Yes. Rollback 경로:

1. **즉시 disable**: `.codeforge/post-merge-automation.disabled` flag 활성 → 양 workflow no-op
2. **단계적 revert**:
   - retro-mandatory.yml 삭제 (workflow disable)
   - label-registry-v1 v1.5 → v1.4 revert (gate:retro-complete entry 삭제)
   - bootstrap-labels.sh `gate:retro-complete` 1줄 revert
   - story-page-structure.md §11 schema revert (`- 회고 (PMOAgent 작성)` line 복구)
   - codeforge-pmo CLAUDE.md + agents/PMOAgent.md amendment revert
   - ADR-043 status: Accepted → Deprecated
3. **이미 운영 중인 retro file 보존** (audit trail 유지) — append-only invariant 정합
4. **이미 부착된 `gate:retro-complete` label** = leave as-is (label 자체 GitHub 측 잔존, registry revert 후 무영향)

## Out-of-scope

- retro file schema 강화 / quality lint (현재 `templates/retro.md` schema 그대로 사용) — 별도 follow-up CFP
- Consumer-side retro mandate 도입 가이드 — `docs/consumer-guide.md` 후속 안내 (별도 CFP, debut audit 후)
- Retroactive backfill — 본 ADR 도입 이전 close 된 Story 100+ 의 retro 작성 (D-5 정합)
- Hotfix 경로 retro 의무 — `docs/hotfix-playbook.md` amendment 별도 CFP
- TEAM-RETRO 의 agent teams 활성 (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) 의존성 — 본 ADR 는 default subagent context 에서도 동작 (Orchestrator → PMOAgent subagent spawn one-shot 패턴)
- EC-5 사용자 manual edit policy (retro file append-only / immutable) — KB 신설 후보 (`docs/domain-knowledge/retro-flow/manual-override-policy.md`), 별도 CFP

## 관련 파일

- `templates/github-workflows/retro-mandatory.yml` (신규)
- `templates/github-workflows/post-merge-followup.yml` (미터치, ADR-026 보존)
- `templates/github-workflows/phase-label-invariant.yml` (`enforce-terminal-on-close` job 동시 동작)
- `templates/story-page-structure.md` §11 schema 갱신
- `docs/inter-plugin-contracts/label-registry-v1.md` v1.4 → v1.5
- `docs/inter-plugin-contracts/MANIFEST.yaml` label-registry-v1 entry update
- `scripts/bootstrap-labels.sh` 1줄 추가 + echo string 갱신
- `CLAUDE.md` "Story 작성 의무" + "Lane plugin self-write boundary" cross-ref minimal 추가
- `<internal-docs>/wrapper/change-plans/2026-05-09-cfp-138-retro-mandatory.md` (Change Plan)
- `<internal-docs>/wrapper/stories/CFP-138.md` §3·§7·§11 채움

## 관련 ADR

- **ADR-009** wrapper-only decomposition: 본 ADR 는 PMOAgent (codeforge-pmo lane plugin) mandate amendment + workflow 추가. wrapper agent 0개 invariant 무손상.
- **ADR-013** codeforge family dogfood-out policy: retro file write target = `<internal-docs>/<plugin-folder>/retros/`. wrapper repo `docs/retros/` 부재 정합.
- **ADR-022** Sonnet decider Comprehensive Policy (**Deprecated 2026-05-08**, CFP-134): 본 ADR 의 retro 자동 trigger 의무화 = ADR-022 deprecate framing (사용자 turn 9 directive) 의 일부.
- **ADR-024 + Amendment 1** Story-scoped branch policy: retro-mandatory.yml = PR merge event trigger only. main 직접 push 차단 invariant 무손상.
- **ADR-025 Amendment 1** Stop discipline + Epic-level continuity: 본 ADR 의 retro 자동 trigger = stop discipline 의무화 (사용자 매번 stop 발화 불필요). §결정 7 `policy_violation_subdecision` 차단 정합.
- **ADR-026** Post-merge follow-up automation: retro-mandatory.yml = 별도 workflow 분리 (D-2). disable-by-flag invariant 공유 (D-7). PAT scope 정합 (D-1).
- **ADR-031** Lane evidence: retro = lane 외 phase. §14 lane enum 미수정 (영향 없음).
- **ADR-035** codeforge agent teams Epic SSOT: 본 ADR = D5 Foundation 결정 implementation. amendment_log[] 에 `amendment_id: 2 (CFP-138)` 추가 의무 (CFP-137 first merge 시 본 lane rebase + amendment_id 다음 값으로 갱신).
- **ADR-039** Orchestrator subagent default: retro 자동 trigger 동작 = Orchestrator → PMOAgent subagent spawn (inline write 금지). 본 ADR 정합.
