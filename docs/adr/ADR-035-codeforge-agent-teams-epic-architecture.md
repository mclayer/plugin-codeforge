---
adr_number: 35
title: codeforge agent teams + GitOps + retro 의무화 + ADR-022 deprecate Epic architecture (CFP-134)
date: 2026-05-08
status: Accepted
category: architecture
carrier_story: CFP-134
parent_epic: CFP-134
supersedes: null
amends: null
related_stories:
  - CFP-134
  - CFP-135
  - CFP-136
  - CFP-137
  - CFP-138
  - CFP-139
  - CFP-140
related_adrs:
  - ADR-009
  - ADR-022
  - ADR-024
  - ADR-025
  - ADR-029
  - ADR-044  # CFP-137 carrier — D2 implementation level SSOT (amendment_log[1] applied)
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
amendment_log:
  - amendment_id: 1
    date: 2026-05-08
    scope: "CFP-140 추가 — GitHub Enterprise Cloud (GHEC) governance 4 영역 (rulesets-as-code / required workflows enterprise sync / audit log streaming + decision packet SIEM trail / Issue Types + sub-issues migration) 을 GitOpsAgent mandate 로 확장. 본 ADR Initial draft 는 D1-D5 (Foundation 결정) 만, CFP-137 가 phase-scoped agent teams 내용 amendment, CFP-140 가 GHEC governance 내용 amendment 추가 예정."
    status: planned
  - amendment_id: 2
    date: 2026-05-09
    scope: "CFP-137 (Wave 2) carrier — D2 (Agent teams 적극 도입) 의 implementation level 결정 본 ADR 외 별도 ADR-044 (Phase-scoped sequential team SSOT) 으로 carrier 분리. ADR-044 가 lifecycle / team-spec yaml 7종 / hook 3종 / review-verdict v3 → v4 cutover / 5 권장 패턴 measurable verification 통합. 본 ADR D2 본문 변경 0 — D2 §결정 정합 invariant 무손상 + ADR-044 carrier 명시 cross-ref 만 추가."
    status: applied
    applied_pr: "wrapper Phase 1 PR (CFP-137)"
  - amendment_id: 3
    date: 2026-05-09
    scope: "CFP-138 (Wave 2) — D5 Story 완료 회고 의무화 implementation level. Phase 2 PR merge 후 4 attempts (1 initial + 3 retries) cumulative offset (PR merge +5/+10/+20/+35min) + close-blocking forcing function (gate:retro-complete). retro-mandatory.yml workflow + label-registry v1.5 (gate:retro-complete) + Story §11 schema migration + codeforge-pmo PMOAgent mandate amendment. ADR-045 = D5 Foundation 결정 implementation carrier. amendment_id shift from 2 → 3 due to CFP-137 first-merge precedence (R3 정합)."
    status: applied
    ref: ADR-045
    cfp: CFP-138
    applied_pr: "wrapper Phase 1 PR (CFP-138)"
---

# ADR-035: codeforge agent teams + GitOps + retro 의무화 + ADR-022 deprecate Epic architecture

## 상태

**Accepted (2026-05-08)** — CFP-134 Epic carrier ADR. Foundation 결정 (D1-D5) 본 ADR Initial draft 에 명시. Phase-scoped agent teams + worktree 상세 (D2 의 implementation level) 는 CFP-137 (Wave 2) 가 amendment 추가 예정 — 본 ADR Amendment 1 marker 보유. GHEC governance 4 영역 (D6) 은 CFP-140 (Wave 4, Amendment 1 추가됨) 이 별도 ADR (ADR-038/039 분할 예정) carrier — 본 ADR 외부.

본 Epic 의 spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md). 본 ADR = doc 화된 Epic-level decision SSOT (frontmatter `category: architecture` 분류 — 다중 child Story 결정 통합).

## 컨텍스트

사용자 directive 2026-05-08 (`claude-opus-4-7` wrapper session, 12-turn conversation):

> "codeforge가 작업하는 내용은 절대로 main branch에 직접 commit할 수 없다. PR Merge를 해야만 한다... branch를 통해 병행 작업을 수행할 수 있지 않을까? Epic > Story > sub... 이렇게 있는 경우 branch를 하위 생성하여 agent 내에서 적극적으로 병렬 작업할 수 있도록 해야한다."

> "PMOAgent가 Epic과 Story 단위 등 하위 구조를 나누면 GitRepoAgent가 해당하는 브랜치를 생성하고 작업하는 agent에 넘겨주는 것이다. 또 충돌이 일어났을 경우 PMOAgent 또는 다른 PL Agent와 통신하여 충돌을 해결하는 역할도 수행할 수 있다."

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다."

> "codex review와 sonnet decider를 codeforge의 일환으로 보는 것 같은데 그건 아니다. 사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다."

> "story 완료 회고는 사용자 요청이 없어도 의무로 수행한다."

> "진짜 GitOpsAgent 안필요해? 이정도면 있는게 나을텐데"

> "서로 의존적이지 않은 작업은 병렬 실행하고 worktree해서 작업해도 되겠지?"

### 현재 상태

- ADR-009 (wrapper-only decomposition, Adopted) — wrapper agent 0개 invariant
- ADR-024 (Story-scoped branch policy, Accepted) — flat `cfp-NNN[-slug]` naming
- ADR-022 (Sonnet decider 5-trigger 자동 발동, Accepted) — Codex review + Sonnet decider 가 codeforge 1st-class 로 자동 invoke
- 6 lane plugin (requirements / design / review / develop / test / pmo) + PMOAgent in codeforge-pmo
- `superpowers:using-git-worktrees` skill 가 worktree 옵션 제공 — Stage 0 worktree 가능
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 활성 시 SendMessage / TaskList / TeamCreate 사용 가능

### Gap

1. Hierarchical branch convention 미정의 — 1 Story 안에서 N teammate 가 자기 sub-branch 위에서 병렬 작업 시 lane / sub-task 분기 표현 불가
2. Worktree lifecycle 자동화 부재 — Orchestrator inline 처리, 책임 분산 부족
3. Agent teams 활용 정책 부재 — 모든 lane spawn 이 one-shot subagent (continuous dialog 불가, 토큰 비효율)
4. Sonnet decider 가 codeforge 1st-class component 로 잘못 통합 — 사용자 의도 (ad-hoc 도구) 와 충돌
5. Story 완료 회고가 ad-hoc (사용자 요청 시) — 의무화 부재
6. GitOps 책임자 부재 — Orchestrator inline 처리, 충돌 해소 / sequential merge / GC 분담 부족

## 결정 (D1-D5 Foundation, D6 = Amendment 1 별도)

### D1 — ADR-022 + Sonnet decider 처리 = deprecate

**결정**: ADR-022 status `Accepted` → `Deprecated` (Superseded chain 미사용 — 후속 ADR 가 명시적 'Supersedes' 안 함, 'codeforge family 결정 deprecate' 가 정확한 framing). 사용자 personal memory 3 항목 (`feedback_codex_review_auto_proceed.md` / `feedback_no_clarification_default.md` / `feedback_decider_protocol.md`) 도 동시 삭제 (사용자 환경에서 사전 처리, evidence-only).

**거절된 대안**:
- (B) ADR-022 active 유지 — 사용자 directive 정면 위배
- (C) ADR-022 amendment — magnitude 가 amendment 수준 초과 (5 trigger 자동 발동 전체 무효)

**근거**: 사용자 turn 7-8 명시. Codex review / Sonnet decider 는 사용자 explicit request 시에만 ad-hoc invoke — codeforge 자동 invoke 금지. Phase 1 trust model = doc-only deprecate (Plugin CLAUDE.md doc 만으로 정책 정의).

**Implementation**: CFP-135 (Wave 1 첫 작업 — 본 Story carrier).

### D2 — Agent teams 적극 도입

**결정**: Phase-scoped sequential team 패턴 적극 도입. 1 Story = N team (요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → 보안테스트 → retro). 각 team 은 lane 진입 시 TeamCreate, 완료 시 TeamDelete (single-Story-long team 회피). Orchestrator = 영구 lead (Story 전 기간 fixed).

**거절된 대안**:
- (B) 보수적 부분 도입 — 현 one-shot subagent 패턴의 토큰 비효율 / continuous dialog 불가 문제 미해결
- (C) 도입 보류 — 사용자 directive 정면 위배

**근거**: 사용자 turn 5+8 명시 ("적극 도입" + "토큰 비용 무관"). ROI source = (a) Lane PL ↔ Lane PL coordination, (b) Lane PL ↔ Worker continuous dialog, (c) Parallel diagnosis (CFP-19 R4), (d) Worktree isolation (D3).

**Risk + Mitigation**:
- Phase-scoped team — `/resume` no-resumption risk 회피 (single-Story-long team 미사용)
- 권장 3-5 명 초과 (Design 8명, Develop 5-7명) — 25 thread 한도 내 + Specialization 패턴 정합으로 허용
- Experimental status — Hotfix path 유지 + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` SessionStart hook 검증 의무

**Implementation**: CFP-137 (Wave 2). D2 의 implementation level 결정은 본 ADR 외 별도 [ADR-044 (Phase-scoped sequential team SSOT)](ADR-044-phase-scoped-sequential-team.md) carrier — `templates/team-spec-<lane>.yaml` 7종 + hook 3종 (TeammateIdle / TaskCreated / TaskCompleted) + review-verdict v3 → v4 contract bump + 5 권장 패턴 measurable verification 통합. 본 ADR amendment_log[1] = `applied` (CFP-137 wrapper Phase 1 PR carrier). lane plugin agent prompt 갱신 = sibling sync follow-up PR (ADR-010 wrapper-first 절차).

### D3 — GitOpsAgent 신설 + 위치 = codeforge-pmo plugin

**결정**: GitOpsAgent 를 codeforge-pmo plugin 안에 신설 (long-running teammate, Story 전 기간). PMOAgent (cross-cutting) 와 같은 plugin 안에서 sibling teammate — turn 3 "PMOAgent ↔ GitRepoAgent 협업" 자연.

**거절된 대안**:
- (B) wrapper agent 신설 — ADR-009 invariant (wrapper agent 0개) 위반
- (C) 신규 plugin (codeforge-gitops) — overhead, ROI 낮음
- (D) Orchestrator inline — 책임 비대화

**책임**: hierarchical branch tree 생성 + worktree N 개 동시 생성 + 각 teammate 의 worktree path 결정 + sequential merge orchestration + 충돌 감지 시 lane PL teammate / PMOAgent 와 SendMessage + stale worktree GC + cross-platform path 일관 처리.

**Write paths**: `.claude-work/worktree-manifest.yaml` + Story §10.5 "Git Ops Log" (신규 section, CFP-139 carrier).

**Implementation**: CFP-139 (Wave 3, depends on CFP-136 + CFP-137).

### D4 — Hierarchical branch convention (ADR-024 amendment)

**결정**: ADR-024 amendment — `cfp-NNN[/<lane>[/<sub>]]` 계층 추가. flat naming `cfp-NNN[-slug]` 그대로 유효 (story root branch). hierarchical 은 sub-branch 영역 추가만 — backward compat 유지.

```yaml
naming_convention:
  story_root: cfp-NNN[-slug]
  lane: cfp-NNN/<lane-name>
  sub_task: cfp-NNN/<lane-name>/<sub-name>
  fix_iter: cfp-NNN/fix-iter-<N>
  retro: cfp-NNN/retro
```

Worktree base = `${HOME}/.claude/worktrees/<repo-name>/` (cross-platform).

**거절된 대안**:
- (B) flat naming 유지 — agent teams + worktree integration 시 lane / sub-task 분기 표현 불가

**Implementation**: CFP-135 (본 Story 의 ADR-024 Amendment 1 carrier). enforcement (branch naming auto enforcement) 는 별도 CFP — solo-dev 환경 deferred (현재 ADR-024 결정 4 Phase 2 한계 정합).

### D5 — Story 완료 회고 의무화

**결정**: PMOAgent 가 Phase 2 PR merge 후 retro 자동 trigger (사용자 요청 불필요). `gate:retro-complete` label 신설 — 미작성 시 Story close 차단.

**거절된 대안**:
- (B) ad-hoc 유지 (현 상태) — 사용자 turn 9 directive 위배

**근거**: 사용자 turn 9 명시 ("story 완료 회고는 사용자 요청이 없어도 의무로 수행한다.").

**Implementation**: CFP-138 (Wave 2, depends on CFP-135 ADR-022 deprecate 후 — decider 비-개입 전제 위에 retro mandate 작성). **Implementation level SSOT = [ADR-045](ADR-045-story-retro-mandatory-trigger.md)** (Wave 2 amendment_id=3 / shift from 2→3 due to CFP-137 first-merge precedence, R3 정합). Phase 2 PR merge 후 4 attempts (1 initial + 3 retries) cumulative offset (PR merge +5/+10/+20/+35min) + close-blocking forcing function (gate:retro-complete) — 상세 D-1 ~ D-8.

## D6 (Amendment 1 — CFP-140 Wave 4 추가, 별도 ADR carrier)

GHEC governance 4 영역 (rulesets-as-code / required workflows enterprise sync / audit log streaming + decision packet SIEM trail / Issue Types + sub-issues migration) 을 GitOpsAgent mandate 로 확장. 본 ADR 외부 — CFP-140 carrier 가 별도 ADR (ADR-038/039 분할 예정) author. 본 §= Epic-level cross-ref only.

상세: Stage 0 spec §3.6 + §4.3 (CFP-140) verbatim.

## 결과

긍정:
- 사용자 directive (12-turn) 정합 — branch governance + agent teams + GitOps 책임 분담 + decider 정정 + retro 의무화 5 영역 통합
- ADR-009 wrapper-only invariant 무손상 (D3 = lane plugin 영역)
- ADR-024 backward compat 유지 (D4 = additive sub-branch 영역만)
- Phase-scoped sequential team — `/resume` no-resumption + Story-long team risk 회피
- 6 child Story 분할 + Wave 별 병렬 (Amendment 1: 5 → 6) — drift 위험 낮음

부정:
- 5 CFP 분할 → CI / merge 순서 복잡 — Wave 별 병렬 + Epic Issue 의 dependency graph 명시 + PMOAgent topological enforce (ADR-020 §결정 5) 로 mitigation
- review-verdict v3 → v4 contract bump (CFP-137 scope) — consumer breaking, MAJOR bump + migration guide. mctrader debut audit 까지 0건 (consumer 영향 0)
- Experimental agent teams API 의존 — Hotfix path 유지 + SessionStart hook 검증 의무

## ADR 정합성

- ADR-009 (wrapper-only) — D3 GitOpsAgent in codeforge-pmo plugin 으로 invariant 무손상
- ADR-022 — D1 deprecate (본 ADR 가 architecture decision SSOT 으로 ADR-022 의 Sonnet decider 정책 무효화)
- ADR-024 — D4 Amendment 1 (hierarchical branch convention) carrier — CFP-135 이 별도 amendment 작성 의무
- ADR-025 (Stop discipline) — D1 deprecate 와 정합 (ADR-022 reference 만 정리, ADR-025 정책 자체는 carrier 로 유지)
- ADR-029 (Phase execution visibility) — D1 deprecate 와 정합 (Sonnet decider auto-proceed 정책 무효 → visibility 정책 자체는 무영향)

## CFP-135 Foundation Story — change-plan + 6 deputy 면제 근거

본 ADR-035 가 CFP-134 Epic 의 **architecture decision SSOT** 역할 — D1 (ADR-022 deprecate) / D2 (Agent teams 적극 도입) / D3 (GitOpsAgent 신설) / D4 (Hierarchical branch convention) / D5 (Story 완료 회고 의무화) 의 Foundation 결정 5종 모두 본 ADR 본문 명시. 따라서 **CFP-135 Foundation Story 는 별도 change-plan 작성 면제** (ADR-013 dogfood-out policy 정합 — internal-docs SSOT 의 architecture decision 이 본 ADR 이므로 §3 도입할 설계 SSOT 역할 충족).

또한 CFP-135 = **doc-only Story** (Phase 2 implementation 부재, ADR-027 Amendment 1 정합) — §7 (보안 설계) / §11 (데이터 마이그레이션) / §13 (Live Operational Discipline) 모두 N/A. 따라서 **6 deputy gathering skip 정합** (deputy mandate 매트릭스 의 active row 0). CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch 6 deputy 모두 mandate 영역 (코드 경로 매핑 / refactor 영역 / trust boundary / DR / Test Contract / migration) 본 Story 에서 비활성. ArchitectAgent (chief author) 가 직접 본 ADR 작성 + Stage 0 spec verbatim 보존 invariant 우선 — Wave 2 (CFP-137 worktree 인프라) / Wave 3 (CFP-139 GitOpsAgent) 진입 시 deputy gathering 재개 trigger (§7 / §11 / §13 sub 활성).

## 관련 파일

- `CLAUDE.md` — 4 영역 SSOT 정정 (CFP-135 carrier)
- `docs/orchestrator-playbook.md` — agent teams + worktree dispatch 절차 (CFP-137 carrier)
- `docs/consumer-guide.md` — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 안내 (CFP-137 carrier)
- `docs/adr/ADR-009-wrapper-only-decomposition.md` — wrapper agent 0개 invariant
- `docs/adr/ADR-022-sonnet-review-verdict-decider.md` — D1 deprecate target
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — D4 amendment carrier
- `docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md` — Stop discipline 정책 (ADR-022 reference 만 정리)
- `docs/adr/ADR-029-phase-execution-visibility-expansion.md` — Visibility 정책 (D1 무영향)

## 6 child Story Wave map (Amendment 1: 5 → 6)

```
                    Epic CFP-134 (본 ADR carrier)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   CFP-135 (A)       CFP-136 (B)       CFP-138 (D)
   foundation        worktree-infra    retro 의무화
   (Wave 1)          (Wave 1)          (Wave 1, A 부분 의존)
                          │                 │
                          │                 │
                          ▼                 │
                     CFP-137 (C)            │
                     agent teams 도입        │
                     (Wave 2, A+B 의존)      │
                          │
                          ▼
                     CFP-139 (E)
                     GitOpsAgent base
                     (Wave 3, B+C 의존)
                          │
                          ▼
                     CFP-140 (F, Amendment 1)
                     GitOpsAgent GHEC governance
                     (Wave 4, E 의존)
```

| Wave | CFPs | 의존성 | 병렬 가능? |
|---|---|---|:-:|
| Wave 1 | CFP-135 (A) ∥ CFP-136 (B) ∥ CFP-138 (D) | independent (D 는 A 부분 의존) | A, B 병렬 / D 는 A 부분 완료 후 |
| Wave 2 | CFP-137 (C) | A + B 완료 | sequential after Wave 1 |
| Wave 3 | CFP-139 (E) | B + C 완료 | sequential after Wave 2 |
| Wave 4 (Amendment 1) | CFP-140 (F) | E 완료 | sequential after Wave 3 |
