---
adr_number: 39
title: Orchestrator subagent default for codeforge modification work
date: 2026-05-08
status: Accepted
category: orchestration-discipline
carrier_story: CFP-275
supersedes: null
amends: ADR-009
related_adrs:
  - ADR-009  # wrapper-only decomposition (amends)
  - ADR-025  # stop discipline + Epic-level continuity (motivation)
  - ADR-029  # phase execution visibility (narration interaction)
  - ADR-031  # lane-spawn evidence trail (§14 row append)
  - ADR-035  # codeforge agent teams Epic (subagent semantics)
related_stories:
  - CFP-275
related_cfps:
  - CFP-275
  - CFP-134
  - CFP-46
  - CFP-26
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/hotfix-playbook.md
  - docs/change-plans/cfp-275-orchestrator-subagent-default.md
  - docs/domain-knowledge/orchestrator-discipline/spawn-default.md
is_transitional: false
---

# ADR-039: Orchestrator subagent default for codeforge modification work

## 상태

**Accepted (2026-05-08)** — carrier_story = CFP-275. Phase 1 trust model (doc-only / no hook enforcement / no telemetry, ADR-025 + ADR-029 precedent 정합 — Phase 1 doc-only trust pattern). Effective = 본 ADR 가 포함된 Phase 1 PR merge timestamp (retroactive 미적용 — 신규 codeforge orchestration 행위부터).

본 ADR 의 implementation plan SSOT = [`wrapper/change-plans/cfp-275-orchestrator-subagent-default.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-275-orchestrator-subagent-default.md) (internal-docs SSOT, ADR-013 dogfood-out). 본 ADR = 정책 결정 SSOT.

## 컨텍스트

### 사용자 directive 3 발화 (2026-05-08, verbatim — Story §1 source)

> "무조건 subagent만 하도록 하자. 그것 때문에 user stop이 자꾸 발생한다."

> "codeforge를 이용한 수정 작업에서는 무조건 subagent이다."

> "그러니까 story 발의해서 적용해"

### 추가 사용자 directive (ADR-035 §컨텍스트 verbatim — 토큰 trade-off)

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다."

본 directive 가 본 ADR 의 §결정 4 운영 risk surfacing (rate limit / token cost) 의 trade-off 수용 근거.

### 현재 상태

- ADR-009 (wrapper-only decomposition, Adopted) — wrapper agent 0개 invariant. Orchestrator (top-level Claude 세션) 가 모든 work 을 6 lane plugin 의 agent 로 spawn.
- ADR-025 (stop discipline + Epic-level continuity, Accepted) — user-stop = `policy_violation`, whitelist 5종 strict. §결정 7 의 `policy_violation_subdecision` 패턴 — "후보 A/B/C/D 중 어떤거?" / "큰 작업이라 확인 받겠습니다" / "Phase 1 완료, Phase 2 시작할까요?" 류 sub-decision stop = defect.
- ADR-029 (phase execution visibility, Accepted) — Orchestrator stderr 1-line narration 의무.
- ADR-031 (lane-spawn evidence trail, Accepted) — Story §14 row append (Orchestrator self-write monopoly).
- ADR-035 (codeforge agent teams Epic, Accepted) — D2 agent teams 활성 분기. ADR-022 deprecate.

### Gap

1. **ADR-009 의 "Orchestrator 가 모든 work spawn" 원칙이 explicit policy 로 codified 되지 않음** — 결과적으로 wrapper Orchestrator 가 매 codeforge 수정 작업마다 "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 발생. 해당 분기가 ADR-025 §결정 7 의 sub-decision stop 발화 채널.
2. **Inline whitelist 미정의** — 사용자 dialog (AskUserQuestion 등) / TodoWrite scratchpad / read-only Q&A 답변 / status report 4 카테고리가 mechanism level 분기되지만 normative table 부재.
3. **Anthropic 공식 권장 (selective spawn) 와 codeforge 정책 (always-spawn) 사이 진영 위치 미정의** — Researcher §6.B 4 framework 비교 결과 wrapper-specific binary 정책의 학계/산업 case study 부재 (Researcher §6.A fact 5).
4. **SSOT 분산점 6 곳** — CLAUDE.md L103 단락 / playbook §3 / playbook §14 / consumer-guide §"Stop discipline" / hotfix-playbook / Wrapper 위임 패턴 — collapse 필요 (RefactorAgent B1 HIGH).

## 결정 (13)

### 결정 1 — codeforge 수정 작업 = Orchestrator default subagent spawn

codeforge 를 이용한 **수정 작업** 진행 중, Orchestrator (top-level Claude 세션, ADR-009) 는 모든 work 을 `Agent` tool spawn (subagent) 으로 수행한다. inline 수행 (Orchestrator turn 안에서 Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 직접 호출) 은 §결정 2 의 4 entry whitelist 외 영역에서 금지.

**수정 작업 정의** (closed enumeration):

- file edit / write (`docs/**`, `src/**`, `templates/**` 포함)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue / branch / merge)
- Story file write (§1-§14 어느 섹션이든)
- FIX Ledger §10 row append (fix-event-v1 contract — ownership 무변, mechanism 만 spawn)
- Lane-spawn evidence §14 row append (ADR-031 — ownership 무변, mechanism 만 spawn)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- **trivial Read 1건 도 spawn 의무** (사용자 verbatim 명시 — Story §2 AC-3 trivial-threshold-zero)

"이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 자체 금지 — branch logic 제거가 본 ADR 의 핵심.

### 결정 2 — Inline whitelist (closed 4-entry enumeration)

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 (Yes/No / 옵션 선택) | Subagent one-shot 이라 continuous dialog 자체 mechanism 불가능 (ADR-009 §결정 + CLAUDE.md "플랫폼 제약"). DialogFidelityAgent verifier subagent spawn 은 본 entry scope 안 cognitive 보강 — 사용자 dialog 본 발화 inline 유지 + 직전/직후 verifier spawn = §결정 1 default subagent spawn 정합 (5번째 entry 신설 아님, closed enumeration 보존 — ADR-071 §결정 13 / CFP-818). |
| 2 | TodoWrite scratchpad | progress visualization marker write | TodoWrite = file write 아님, Orchestrator scratchpad / meta progress channel — 수정 작업 enumeration 미포함. (참고: ADR-038 = TodoWrite progress visualization 도입 informational reference, 본 entry 정당화에 normative dependency 아님 — TodoWrite tool surface 자체가 file system / GitHub state mutation 미발화이므로 본 ADR 내 standalone 정당화) |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청에 대한 응답 (state report / option enumeration / 도메인 설명) | 수정 작업 아님 — codeforge orchestration scope 외 |
| 4 | Status report | Phase 완료 / Story close / final report | 수정 작업 아님 (read-only synthesis) — ADR-025 Amendment 1 §결정 11 의 "1번 final report" |

4 entry **외** 의 모든 codeforge orchestration 행위 = subagent spawn 의무. **모호 시 = 수정 작업 측 분류** (안전 방향 — ADR-013 cutoff precedent 정합).

5번째 카테고리 추가 = ADR-039 amendment 의무. 본 closed enumeration 가 future "Skill 호출 / Glob / Grep / Read tool 분류 enum 확장" 압박을 차단 — 모두 4 entry 의 어느 하나로 routing 또는 수정 작업 측 분류.

### 결정 3 — Ownership ≠ Mechanism 분리

본 정책은 **mechanism (어떻게 수행)** 변경. **ownership (누가 작성권)** 무변.

- Orchestrator monopoly ownership (유지 — invariant 무손상):
  - Story §10 FIX Ledger row append (CFP-32 / fix-event-v1 contract)
  - Story §14 Lane Evidence row append (ADR-031 / CFP-126)
  - review-verdict v3 final write (Story §9 / GitHub comment / gate label / phase transition — ADR-022 deprecate 후에도 Orchestrator domain 유지)
  - branch protection / CI workflow / cross-plugin schema templates
- Mechanism (변경): 위 ownership 영역의 file write / GitHub state change 도 **subagent spawn 으로 수행**. Orchestrator 가 "§10 row append 전용 subagent" / "§14 row append 전용 subagent" / "label transition 전용 subagent" 를 spawn 해 Edit / mcp__github__\* tool 호출.

본 분리는 ADR-031 §결과 invariant 무손상 입증 + lane plugin agent 변경 부재 입증의 핵심 근거.

### 결정 4 — Scope = codeforge orchestration 한정

본 정책 적용 범위 = **codeforge orchestration**. 즉 wrapper Orchestrator 가 codeforge family (wrapper + 6 lane plugin) 의 spawn / docs/** / GitHub state / Story file / FIX Ledger / lane-spawn evidence 영역에서 수행하는 행위. 일반 Q&A / conversational 응답 / non-codeforge 작업 (예: 단순 정보 답변 / 사용자 dialog) 은 비적용 — §결정 2 Inline whitelist 가 boundary clarification.

### 결정 5 — Lane plugin / 6 SubAgent / inter-plugin contract = 0 변경

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) agent 변경 0건.
- design lane 6 SubAgent (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch) + 2 CONDITIONAL SubAgent (LiveOps / LiveOrdering) 변경 0건.
- Inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건.
- ADR-009 §결과 invariant 무손상 (Writer 단독 invariant precedent — ADR-029 / ADR-031 와 동일 패턴).

### 결정 6 — Hotfix path 동일 적용 (no exception)

`docs/hotfix-playbook.md` 의 Hotfix 경로 (운영 장애 대응 / 사후 감사 의무) 도 본 정책 적용. 사용자 verbatim "무조건" — emergency 시에도 spawn 의무. Hotfix 의 fast-path 본질 (Phase skip / lane skip) 은 무변, **mechanism 만 spawn 의무**.

### 결정 7 — Consumer scope (wrapper + consumer Orchestrator 동일 적용)

본 정책 = wrapper Orchestrator + consumer Orchestrator (예: mctrader Orchestrator / 추후 다른 consumer) 모두 적용. consumer Orchestrator 가 codeforge family plugin 을 사용하는 시점부터 본 정책 inheritance — `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" 신규 subsection 가 SSOT cross-ref.

ADR-025 §결정 9 (consumer scope) 와 동일 enforcement 패턴 — Phase 1 = trust model (사용자 directive 의 directive 발화 의무 + enforcement hook 없음).

### 결정 8 — Phase 1 = doc-only trust model

본 ADR 의 effective enforcement 강도 = doc-only. 매 Orchestrator 행위 시 (1) 본 ADR-039 / (2) playbook §3.0 / (3) CLAUDE.md "Default subagent context" / (4) consumer-guide § "Subagent default" / (5) hotfix-playbook 1줄 reading 시 자체 인지. 자동 enforcement 부재.

ADR-025 / ADR-029 precedent 정합 (Phase 1 doc-only trust pattern) — Phase 2 enforcement = 별도 follow-up CFP.

### 결정 9 — Phase 2 enforcement / measurement = deferred follow-up CFP

후속 CFP (현재 미할당) 가 다음 영역 처리:

- **stop-event-v1 ledger** 도입 (ADR-025 §결정 10 deferred). Orchestrator user-stop 발화 시 ledger row append → `reason_class: policy_violation_subdecision` 발생률 측정 → 본 정책 효과 검증.
- **Orchestrator inline write detect hook** (PreToolUse on Write / Edit / mcp__github__\*). Orchestrator 직접 호출 detect → warning surface (또는 strict mode 시 차단).
- **spawn cost telemetry** (token / latency 정량 측정). Researcher §6.F fact gap (spawn latency 정량 데이터 부재) 충당.
- **rate-limited error → unwanted user-stop** second-order risk 측정 (OpRiskArch §7.4.4 운영 risk surfacing).

ROI 평가 후 enforcement 강도 결정. 본 Story scope = Phase 1 doc-only.

### 결정 10 — ADR-009 amends 관계

본 ADR = ADR-009 (wrapper-only decomposition) 의 **자연 확장** / **explicit 격상**. 새 invariant 가 아닌 기존 invariant 의 codification. frontmatter `amends: ADR-009` 명시.

ADR-009 의 "wrapper agent 0개 → Orchestrator 가 모든 work 을 spawn" 원칙은 이미 wrapper-only decomposition 의 결과로 존재. 본 ADR 가 그 원칙을 **explicit policy 로 stamping** + branch logic 제거 + Inline whitelist 4-entry codification.

### 결정 11 — ADR-022 (Deprecated) 와의 충돌 자동 해소

ADR-022 (Sonnet decider 5-trigger 자동 발동) = Deprecated by ADR-035 (CFP-134 / ADR-035, 2026-05-08). 본 ADR 시행 후에도 Sonnet 자동 dispatch 부재 — 사용자 ad-hoc 호출 전용 도구.

사용자 ad-hoc Sonnet 호출 시에도 본 정책 적용 — Sonnet 호출 자체가 subagent spawn (Agent tool with `model:sonnet`) 이므로 자연 정합. CFP-137 / CFP-134 follow-up 의무 (ADR-022 본문 잔재 cleanup) 는 본 ADR scope 외.

### 결정 12 — Cross-ADR amendment 의무 (Ownership ≠ Mechanism normative anchoring)

§결정 3 의 Ownership ≠ Mechanism 분리 (Orchestrator-spawned subagent = Orchestrator-owned delegate) 가 normative 정합을 갖추려면 ADR-031 (lane-spawn evidence) + fix-event-v1 contract (Story §10 FIX Ledger) 의 "Orchestrator self-write" / "Writer monopoly v1: Orchestrator 단독" invariant 가 **Orchestrator-owned delegate subagent 의 self-write 행위를 explicitly cover** 해야 한다.

**Amendment 의무** (본 ADR carrier Story 안 commit 동반, ADR-010 sibling sync 패턴):

- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` — **Amendment 1** 신설:
  > Orchestrator-owned delegate subagent (Orchestrator 가 §14 row append 전용으로 spawn 한 subagent) 의 §14 lane evidence write = §결정 1 의 "Wrapper Orchestrator self-write" 정의에 포함됨. mechanism level subagent 경유여도 ownership identity = Orchestrator 유지 (ADR-039 §결정 3 cross-ref).
- `docs/inter-plugin-contracts/fix-event-v1.md` — **Amendment** 신설 (`append_rules.writer` 절):
  > "Orchestrator 단독" 의 **Orchestrator 정의** = top-level Claude 세션 + Orchestrator 가 §10 row append 전용으로 spawn 한 delegate subagent 모두 포함. lane plugin agent 가 자체 임의 §10 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn). Cross-ref: ADR-039 §결정 3 + §결정 12.

본 amendment 가 본 carrier Story 안 commit 되지 않으면 §결정 3 가 ADR-031 line 49 + fix-event-v1 line 21 / line 135 invariant 와 normative 충돌 — DesignReview P0 차단 사유.

**ADR-010 sibling sync** (fix-event-v1 amendment 시): wrapper repo 만 fix-event-v1 보유 (canonical). codeforge-pmo / 기타 lane plugin sibling 부재 — sibling sync overhead 0건.

### 결정 13 — Phase 1 scope expansion (4 SSOT doc edits effective date alignment)

§결정 8 의 Phase 1 doc-only trust model 효과 = 4 SSOT doc reading 시 자체 인지. 이 효과는 4 SSOT doc 가 **본 ADR 와 동일 PR 안에서 갱신** 되어야 발효 — 별도 follow-up PR 분리 시 본 ADR Accepted 시점부터 4 SSOT doc 미반영 PR merge 시점까지 normative gap 발생 ("Accepted but not effective" — DesignReview P1 finding).

**Phase 1 PR scope 확정** (Phase 2 PR scope 에서 이동 — Story §4 정정):

- `docs/adr/ADR-039-...md` (본 file)
- `docs/adr/ADR-031-...md` (Amendment 1 — §결정 12 carrier)
- `docs/inter-plugin-contracts/fix-event-v1.md` (Amendment — §결정 12 carrier)
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md` (internal-docs SSOT, ADR-013)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md`
- **`CLAUDE.md`** — "오케스트레이션 규칙" / "플랫폼 제약" / "Wrapper 위임 패턴" 갱신 (Phase 1 이동, B1 + B2)
- **`docs/orchestrator-playbook.md`** — §3.0 normative section 신설 (Phase 1 이동, B1 HIGH)
- **`docs/consumer-guide.md`** — § "Subagent default (codeforge orchestration)" 신규 subsection (Phase 1 이동, B5 HIGH)
- **`docs/hotfix-playbook.md`** — 1줄 ADR-039 cross-ref (Phase 1 이동)

**Effective date** = 본 ADR 가 포함된 Phase 1 PR merge 시점 = 4 SSOT doc 모두 갱신된 시점 (동일 PR commit batch 보장). retroactive 미적용.

DeveloperPL Phase 2 lane 경유 안 함 — ArchitectPL 직접 4 doc edit (chief author 통과 방향 유지, 편차 제거).

## 회피된 대안

### 대안 A — Selective inline (Anthropic 공식 권장)

Anthropic 공식 (`https://www.anthropic.com/engineering/claude-code-best-practices`) 의 "side task that would flood main conversation" criterion 기반 selective spawn.

**거부 이유**:
- 사용자 verbatim "무조건" directive 와 정면 충돌 (Story §1)
- "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 = 본 ADR motivation 의 user-stop 발화 채널 (ADR-025 §결정 7 sub-decision stop). selective spawn 정책 = 분기 자체 보존 → user-stop 회피 motivation 미충족
- selective criterion 의 정량 boundary 부재 ("flood" 정의 모호) → 매번 분기 발화

채택 = §결정 1 binary always-spawn.

### 대안 B — 즉시 hook enforcement (Phase 1 부터)

PreToolUse hook 으로 Orchestrator 직접 Write / Edit / mcp__github__\* 호출 detect → 즉시 차단.

**거부 이유**:
- ADR-025 / ADR-029 의 Phase 1 trust model precedent 위반 (doc-only / enforcement 후속 CFP)
- spawn latency 정량 데이터 부재 (Researcher §6.F fact gap) → false-positive 위험 (legitimate Read 행위 차단)
- §결정 2 Inline whitelist 4-entry 의 mechanism level boundary 가 hook code level 에서 정확 detect 불가능 (예: Read 가 Q&A 답변용인지 수정 작업의 일부인지 mechanism level 모호)

채택 = §결정 8 Phase 1 doc-only + §결정 9 Phase 2 deferred.

### 대안 C — Lane plugin 측 적용

6 lane plugin agent 자체에 spawn 의무 stamping (lane plugin 내부 행위도 spawn 으로 강제).

**거부 이유**:
- ADR-009 wrapper-only decomposition scope 위반 — wrapper Orchestrator 만 spawn 권한 invariant. Lane plugin agent 는 self-write boundary 안에서 자체 Edit / Read 호출 — 재귀 spawn limit 와 직접 충돌 (subagent → Agent tool 호출 금지, CLAUDE.md "플랫폼 제약")
- 본 ADR motivation = Orchestrator user-stop 회피. Lane plugin agent 는 user-stop 발화 채널 아님 (subagent one-shot return)

채택 = §결정 5 lane plugin 0 변경.

## 외부 fact (Researcher §6 reference)

본 ADR 의 §결정 정당화 + 회피된 대안 reject 근거의 외부 데이터:

1. **Anthropic multi-agent research system** — https://www.anthropic.com/engineering/multi-agent-research-system
   - Multi-agent ≈ 15× 토큰 vs single-agent chat (Anthropic 자체 측정)
   - 90.2% performance lift on multi-step research benchmark (vs single-agent baseline)
2. **Anthropic Claude Code best practices** — https://www.anthropic.com/engineering/claude-code-best-practices
   - "Side task that would flood main conversation" criterion (selective spawn 권장)
   - 본 ADR = stricter binary policy (always-spawn) — 진영 위치 codify 필요
3. **Anthropic Claude Code subagent docs** — https://docs.claude.com/en/docs/claude-code/sub-agents
   - one-shot semantics / continuous dialog 불가능 → §결정 2 Inline whitelist entry 1 의 mechanism rationale source
4. **Anthropic Claude Code metrics blog** — https://www.anthropic.com/news/claude-code (auto-mode 정당화 근거)
   - 93% approve rate / 17% false-negative — Orchestrator user-stop 회피 motivation 정합

**Fact gap (Researcher §6.F 명시)**:
- spawn latency 정량 데이터 부재 (Anthropic 정성 언급만) — Phase 2 측정 의무
- "always-spawn" binary 정책 학계/산업 case study 검색 0건 — wrapper-specific design choice (debut audit measurable signal)

## 검증 채널

Phase 1 trust model 의 검증 채널 = doc lint (TestContractArchitect §8.4 산출물 verbatim — Change Plan §8.4):

1. **Spawn-default presence lint** — 4 SSOT doc (playbook §3.0 / CLAUDE.md "Default subagent context" / consumer-guide § "Subagent default" / hotfix-playbook 1줄) 의 ADR-039 cross-ref 존재 검증 (`scripts/check-doc-section-schema.sh` 확장 또는 신규 lint script).
2. **Branch-logic absence lint** — playbook / CLAUDE.md / consumer-guide 안 "inline 으로 충분" / "trivial 이면 inline" / "subagent 가 나은가" 류 결정 분기 prompt 부재 검증 (grep deny-list).
3. **ADR-039 frontmatter schema 정합** — `amends: ADR-009` / `category: orchestration-discipline` / `status: Accepted` / `carrier_story: CFP-275` 필드 존재 검증.
4. **Cross-reference lint** — ADR-039 본문 + Change Plan §5 / §3 의 ADR-009 / ADR-025 / ADR-029 / ADR-031 cross-ref 존재 검증.
5. **Story §11 retro append schema 정합** — Phase 2 PR merge 후 PMOAgent retro append 시 schema 검증.

**현재 Phase 1 PR scope 안 lint 도입** = 후보 1 + 후보 2 만 (가능하면). 후보 3-5 = follow-up CFP.

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` (본 file)
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md` (implementation plan)
- `docs/orchestrator-playbook.md` §3.0 신설 (B1 HIGH)
- `CLAUDE.md` "오케스트레이션 규칙" § "Default subagent context (수정 작업)" 1 paragraph (B2 HIGH)
- `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" 신규 subsection (B5 HIGH)
- `docs/hotfix-playbook.md` 1줄 추가 (AC-13)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md` (DomainAgent draft commit)

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) 변경 없음 (§결정 5 lane plugin 0 변경 invariant)
- Inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건
- design lane 6 SubAgent + 2 CONDITIONAL SubAgent 변경 0건
- Stop discipline (ADR-025) 5 종 whitelist 무변 — 본 ADR 는 stop 발생 가능성을 줄이는 mechanism 이지 whitelist 자체를 변경 X
- ADR-031 §14 lane evidence write monopoly 무변 (ownership 무변, §결정 3 mechanism 분리)
- Story §10 FIX Ledger Orchestrator monopoly 무변 (ownership 무변)
- TodoWrite 흐름 무변 (§결정 2 Inline whitelist entry 2 — TodoWrite tool surface 자체 standalone 정당화, ADR-038 informational reference 만, normative dep 아님)

### Reversibility

- Yes — 본 ADR `status: Deprecated` 전환 + 영향 file revert 시 ADR-009 + ADR-025 기존 enforcement 강도 복원
- ADR-022 → ADR-035 precedent 패턴 (status flip + Deprecated marker + 회피 doc edit)

## Out-of-scope

- Phase 2 enforcement (hook / telemetry / stop-event-v1 ledger) — §결정 9 deferred
- 6 lane plugin agent 의 spawn 의무 stamping — §결정 5 lane plugin 0 변경 invariant 위반
- ADR-022 본문 잔재 cleanup — CFP-137 / CFP-134 follow-up
- Skill 호출 / Glob / Grep / Read tool 분류 enum 확장 — §결정 2 closed 4-entry 위반 (Refactor B3 over-engineering 회피)
- spawn cost ROI 분석 / 정량 boundary 도입 — Phase 2 deferred
- Multi-Story / Epic-level continuity 흐름 변경 — ADR-025 Amendment 1 무손상

## 관련 ADR

- **ADR-009** (wrapper-only decomposition) — **amends** 관계. 본 ADR = ADR-009 의 자연 확장 / explicit 격상.
- **ADR-025** (stop discipline + Epic-level continuity) — motivation. §결정 7 의 `policy_violation_subdecision` sub-class "이거 inline 으로 충분한가" stop 을 mechanism level 에서 제거. 5 종 whitelist 무변.
- **ADR-029** (phase execution visibility) — narration interaction. 매 subagent spawn / return 가 narrate 대상. Orchestrator stderr narration 의무 보존.
- **ADR-031** (lane-spawn evidence trail) — §14 row append ownership 무변, mechanism 만 spawn (§결정 3). **Amendment 1** 본 ADR carrier Story 안 commit 동반 (§결정 12) — Orchestrator-owned delegate subagent 가 self-write 정의에 포함됨 명시.
- **ADR-035** (codeforge agent teams Epic) — subagent semantics 분기. 본 ADR 의 "subagent" = default subagent context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`) 의 one-shot subagent. Agent teams enabled context (CFP-137 deferred) 는 본 ADR 의 default 분기 외 — agent teams 활성 시에도 본 정책의 spawn 의무 유지, dialog 가능성만 확장.
- **ADR-038** (progress visualization TodoWrite) — informational reference. 본 ADR 의 §결정 2 Inline whitelist entry 2 (TodoWrite scratchpad) 의 normative 정당화는 TodoWrite tool surface 자체 (file system / GitHub state mutation 미발화) 에서 standalone 도출 — ADR-038 normative dependency 아님 (PR merge order 무관, P0-1 fix).
- **ADR-022** (Sonnet decider 5-trigger 자동 발동) — **Deprecated by ADR-035** (CFP-134 / ADR-035, 2026-05-08). 본 ADR 시행 후 Sonnet 자동 dispatch 부재 — 사용자 ad-hoc 호출 시에도 Sonnet 호출 자체가 subagent spawn (Agent tool with `model:sonnet`) 이므로 자연 정합 (§결정 11).
- **ADR-013** (codeforge family dogfood-out policy) — spec / plan 위치 internal-docs override. 본 ADR Story spec / plan 도 internal-docs SSOT.
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명 (`cfp-275-orchestrator-subagent-default`).
- **ADR-005** (plugin meta exempt) — N/A lane 사유 reference (Change Plan §7 / §11 / §8.5 N/A).

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/orchestrator-playbook.md` §3.0 (신설 — Phase 1 scope, §결정 13)
- `CLAUDE.md` "오케스트레이션 규칙" § "Default subagent context (수정 작업)" (Phase 1 scope, §결정 13)
- `docs/consumer-guide.md` § "Subagent default (codeforge orchestration)" (Phase 1 scope, §결정 13)
- `docs/hotfix-playbook.md` (1줄 ADR-039 cross-ref, Phase 1 scope, §결정 13)
- `docs/domain-knowledge/orchestrator-discipline/spawn-default.md`
- `docs/change-plans/cfp-275-orchestrator-subagent-default.md`
- `docs/adr/ADR-031-lane-spawn-evidence-trail.md` (Amendment 1, §결정 12)
- `docs/inter-plugin-contracts/fix-event-v1.md` (Amendment, §결정 12)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-275.md`
- `mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-275-*.md` (Researcher / DomainAgent / Analyst output SSOT)
