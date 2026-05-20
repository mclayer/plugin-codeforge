# ArchitectLane DDD 재편 CFP — 새 세션 escalation 프롬프트

> ⚠️ **STALE / ON HOLD (2026-05-20 KST 정정 prepend)** — 본 worktree 작업은 **Sequential 결정**에 의해 보류. 사유 = CFP-1086 BackendArchEpic (ADR-86 active, 7+3+1 roster: AggregateArchitectAgent / APIContractArchitectAgent / ModuleArchitectAgent 신설 + DataArchitectAgent 축소, ADR-042 Amendment 8) 가 ArchitectLane deputy roster 재편 진행 중이고, 본 CFP 의 DDD 어휘 재편 (특히 "Aggregate metaphor" / Subdomain Specialist mapping) 과 영역 충돌 가능. **재진입 조건**: (a) CFP-1086 Epic close 확인 (모든 Wave Story LAND, 11 deputy file 안정) + (b) `Explore-verify-output.md` / `PMOAgent-2nd-pass-output.yaml` 재read + (c) 본 ESCALATION-PROMPT 본문 fact 재합의 후 CFP-1107 (재번호) 신규 issue create 또는 CFP-1086 의 Phase N+1 통합 등 사용자 결정 영역.
>
> **stale fact 정정 (verify-via: Explore + gh issue list 2026-05-20 KST)**:
> - 본문 §10 `다음 CFP 번호 = 1104` = stale (#1106 점유, title `[CFP-1104]` misnomer; **다음 reservable = CFP-1107**)
> - 본문 §2 `현재 ArchitectLane 구조 = 10 agent` = transient (CFP-1086 Wave 2/3 LAND 후 **11 agent 7+3+1 roster** 로 재편 예정)
> - 본문 §8 `ADR amendment 대상 = ADR-004/006/007/014/064/068/080` = 일부 정정 의무 (Explore Task D = **ADR-014 Amendment 2 critical, ADR-004/006/007 기초 확정 re-amend 불필요**, ADR-080 terminology 표준 의무, ADR-064/068 MEDIUM, ADR-042/008/010 추가 — PMO 2nd pass 10 ADR 산출)
>
> **현 worktree 산출 (preserve for future reference)**:
> - `PMOAgent-2nd-pass-output.yaml` — Story 분해 6건 + scope_manifest + INV-5 (vocabulary theater forcing function) + Risk Top 5 — CFP-1086 LAND 후 fact 재합의 후 재사용 가능
> - `Explore-verify-output.md` — 10 agent vocabulary verify (DDD hit 0) + ADR-031 5/5 적합도 + CFP 번호 fact + ADR amendment 7건 사전 검사 — fact reference 로 영구 보존
>
> **사용자 confirm 3건 (보존)**: (Q1) Golden-path = ADR-031 / (Q2) Mega-CFP 단일 + 6 Story 내부 분해 + Phase 1 docs PR + Phase 2 PR1~PR5 sequential / (Q3) downstream = upstream Phase 2 PR5 LAND + worked example 시연 PASS 후
>
> 본 문서 = 신규 Claude Code 세션에 그대로 붙여넣어 작업을 이어받기 위한 self-contained handoff. **단, 위 STALE 영역 정정 후 사용 의무 (verify-before-trust, ADR-073 Amendment 2 정합).** 이전 세션의 brainstorm Phase 0/1 산출물 + Codex 합성 결과 + 다음 단계 액션 전부 포함.

---

## SESSION OPEN — 이 메시지로 새 세션 시작

```
당신은 codeforge ArchitectLane DDD 재편 CFP + ADR 작성을 이어받는다.

이전 세션에서 plugin-codeforge 의 codeforge-brainstorm Phase 0 + Phase 1 (Codex 일괄 dispatch) 까지 완료. 이번 세션은 Phase 2 (spec 작성 + scope_manifest + PMO 2nd pass) → CFP issue 예약 → ADR 작성 + Phase 1 docs PR 까지 진행.

## 환경 컨텍스트

- Primary working dir: c:/workspace/mclayer/plugin-codeforge
- 기존 worktree 재사용: c:/workspace/mclayer/plugin-codeforge/.claude/worktrees/architectlane-ddd-brainstorm
  - branch: worktree-architectlane-ddd-brainstorm (origin/main fresh)
  - CFP issue 예약 후 branch 명 정렬 (cfp-1104-architectlane-ddd 등)
- 다음 CFP 번호 = 1104 (현 최신 #1103). gh issue create 시점 atomically reserve
- 한국어로 응답
- Korean preference, plugin-codeforge wrapper-only convention (ADR-009 wrapper-only-decomposition)

세션 진입 첫 액션:
1. `EnterWorktree path="c:/workspace/mclayer/plugin-codeforge/.claude/worktrees/architectlane-ddd-brainstorm"` 호출해서 기존 worktree 진입
2. 본 ESCALATION-PROMPT.md 읽고 컨텍스트 흡수
3. TodoWrite 로 진행 상태 초기화 (Phase 2 시작 시점)
4. 아래 §10 다음 액션 순서대로 실행

---

## 1. WHY (실제 동기) — 이미 사용자 확인된 영역

> **mctrader/codeforge 가 성장하면서 암묵적 BC/Aggregate 결정이 ADR 에 명시 안 됨 → cross-repo Story 진행 중 차등 해석·FIX 루프 누적 (MCT-170 / MCT-177 / MCT-179 / MCT-180 / MCT-184 / MCT-185 Phase 0 verify lesson 6회 재현). 산업 표준 어휘(DDD) 로 명시화하면 신규 agent/member 합류 시 일관 discipline 강제 가능.**

핵심 신호: **vocabulary theater 위험** (Codex BIG concern) — 단순 "agent description 에 DDD 단어 박는" 작업은 실패. **forcing function 이 spawn decision · review findings · ADR acceptance criteria 까지 침투해야** lesson 6회 누적이 실제로 끊어진다.

---

## 2. 현재 ArchitectLane 구조 (Phase 0 verified)

위치: `c:/workspace/mclayer/plugin-codeforge-design/agents/` (10 file)

| Agent | 역할 (현 어휘) |
|---|---|
| ArchitectPLAgent | PL/supervisor — 6 deputy + chief author 산출물 통합, FIX 원인 판정 |
| ArchitectAgent | Chief Author — Change Plan §1-§11 + ADR draft + §8 Test Contract + §11 데이터 마이그레이션 |
| CodebaseMapperAgent | fact source 변호자 — file structure / API surface / dependency graph 만 인용 (no synthesis) |
| RefactorAgent | refactoring 옹호자 — decoupling / pattern / interface 분리 3 카테고리 |
| SecurityArchitectAgent | 보안 설계 변호자 — 위협 모델 / trust boundary / auth+data 모델 |
| TestContractArchitectAgent | §8 Test Contract QA — coverage / boundary / invariant / Perf Baseline |
| DataMigrationArchitectAgent | 데이터 무결성 / migration 안전성 변호자 |
| OperationalRiskArchitectAgent | 운영 리스크 변호자 |
| LiveOpsDeputyAgent | CONDITIONAL — live ops 관련 시만 spawn |
| LiveOrderingDeputyAgent | CONDITIONAL — live ordering 관련 시만 spawn |

**현 어휘 패턴**: artifact-centric (Change Plan/ADR/Test Contract) + perspective-contributor (보수/혁신/위협). **DDD 어휘 0건** (verified-via: grep + read frontmatter).

---

## 3. Phase 0 — 4 agent 병렬 결과 (이전 세션 박제)

### DomainAgent (5 facts)

1. codeforge `docs/domain-knowledge/` (concept/ 4 + domain/ 11 dir) grep "DDD|bounded.context|aggregate.root|ubiquitous" = **0 hit**
2. 10 agent frontmatter = artifact-centric + perspective-contributor, DDD 어휘 0
3. **Lane Self-Write Ownership Matrix SSOT 존재** (`domain/governance-principle/lane-self-write-ownership-matrix.md`) — 본 CFP 가 docs/stories §10/§14 monopoly + Change Plan §·ADR § monopoly 와 충돌 없이 통합 필수
4. **agent-teams Wave 2 row 갱신 의무** (ADR-044 phase-scoped sequential team) — agent 숫자·이름 변경 시 row 갱신
5. **decision-style.md (ADR-064 carrier)** 의 forbid-list / derived-default / parallel-default / top-down-ratchet 4 패턴 중 본 ADR 표현 형식 결정 의무

### Researcher (Unknown unknowns)

1. **양 BC 어휘 충돌**: governance BC (codeforge "Aggregate" = supervised authority cluster) ↔ application BC (mctrader "Aggregate" = DDD Aggregate) — 동음이의 → **Published Language 분리 의무**
2. **self-reference paradox 우려**: ADR-013 dogfood-out + ADR-005 plugin-self-application N/A 와 충돌. **Claude 정정 판단**: DDD = 외부 design discipline. codeforge 가 DDD 채택 ≠ codeforge 가 codeforge 자신 사용. ADR-013/005 위반 0. **non-blocker.**

### Analyst (why 기반 확장)

- 명시 = "CFP+ADR + 상속" / 실제 = **+ retroactive annotation + template field 의무 + glossary SSOT**
- AC-3 핵심: retroactive annotation 후 interpretation drift = 0 (Phase 0 verify 시점 모순 0)

### PMO (예비 분해)

- **codeforge upstream Epic = 5 Story**:
  1. ADR-DDD-governance 신규 + `docs/glossary.md` 신규
  2. 10 agent frontmatter `bounded_context` field + role-by-role DDD term mapping
  3. Story template `§ubiquitous_language` + Change Plan template `§bounded_context_boundary`
  4. review-verdict-v4 contract `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` enum 추가
  5. deputy mandate matrix (6+2) Subdomain Specialist 재배치
- **mctrader downstream Epic = 3 Story**:
  1. 6 repo BC charter 박제 (hub=Governance / data=Storage / engine=Trading / market=SharedKernel / signal-collector=Acquisition / web=Presentation)
  2. **Top 10 ADR DDD annotation** (ADR-029~033 + 5 추가, Codex Q3=C 정합)
  3. mctrader ubiquitous-language SSOT `docs/glossary.md` + 어휘 검증 cron
- **Top 위험**: Subdomain 분류 합의의 정치적 어려움 → 완화 = upstream Story 1 = 분류 기준만, 실 분류는 downstream Story 1 repo-by-repo

---

## 4. Derived Default 선언 (사용자 정정 의무)

ADR-064 §결정 3 룰 1 (derived-default declare + 진행) 적용. **사용자가 다음 5개 default 에 정정 신호 없음** = 채택.

| # | 결정점 | Default |
|---|--------|---------|
| **D-language** | governance BC ↔ application BC 어휘 분리 | **Published Language 분리** (codeforge 단독 SSOT + mctrader 단독 SSOT 2개) |
| **D-classify** | Subdomain 분류 결정 시점 | **upstream = 분류 기준만 / downstream = repo-by-repo 실 분류** |
| **D-template** | Story/Change Plan template field 의무화 | **의무 + lint enforcement** (ADR-082 self-write verification 정합) |
| **D-selfref** | self-reference paradox | **non-blocker** (외부 discipline 채택 ≠ plugin self-application) |
| **Q1 — CFP Scope** | codeforge ArchitectLane DDD 책임 범위 | **(C) 양측** — agent rename + consumer 검증 책임 추가. **사용자 implicit confirm = "mctrader-hub 에서 적절치 않다, codeforge 로 옮겨서 수행하자"** signal |

---

## 5. Codex 합성 결과 (Q2-Q6, verbatim)

> Codex 는 독립 expert 관점 (Sonnet decider 금지 — feedback_brainstorm_codex_review_pattern). Claude 가 일괄 dispatch 후 verbatim 박제.

### Q2 — agent ↔ DDD pattern mapping principle = **(D) Hybrid**

> Rationale: 단일 DDD 패턴을 모든 agent 에 강제 = 너무 rigid + false precision. **PL/Architect = authority pair** (plan consistency), **대부분 deputy = Domain Service** (specialized judgment contributor), **conditional deputy = Subdomain Specialist** (live operational subdomain 활성 시만 spawn).
> Pushback: "Plugin = BC, PL = Aggregate Root, SubAgent = Entity" 강한 매핑 거부. Agent = process participant ≠ domain object.

### Q3 — mctrader retroactive ADR annotation 범위 = **(C) Top 10**

> Rationale: 33 ADR 전수 annotation = high ceremony + low immediate payoff. annotation 0 = migration benefit 손실. Top 10 = consequential historical decision 에 vocabulary 검증. **ADR-029~033 + 추가 5** = architectural coupling 가장 visible 한 영역.

### Q4 — deputy spawn DDD remap = **(B) Subdomain Specialist + "which subdomain under threat"**

> Rationale: "perspective under threat" 를 DDD 어휘로 sharpen — "which subdomain decision is at risk". Deputy = contributor 유지, BC Owner 아님 (Story 가 multiple BC 가로지를 수 있음 → advisory expertise ≠ contextual authority).
> Pushback: option (C) deputy = BC Owner = overreach. BC ownership 은 repo/domain governance 영역 (mctrader 6 repo charter), transient agent spawn logic 아님.

### Q5 — Aggregate metaphor strength = **(C) 양쪽 다**

> Rationale: PL = Aggregate Root 는 supervised authority 의 metaphor only. **Change Plan + ADR draft 산출물 자체는 real consistency boundary**. 핵심 invariant: §1-§11 + BC classification + aggregate impacts + language choices + risks + ADR rationale 가 handoff 전 cohere 해야 함.
> Pushback: **CFP 가 "agent control metaphor" vs "artifact consistency boundary" 를 explicit separate 해야 함**.

### Q6 — DDD enforcement layer 위치 = **(C) Prompt + Template lint + review-verdict-v4 enum**

> Rationale: prompt 만으로는 drift + agent compliance inconsistent. Template lint = mechanical structure / reviewer finding type = semantic accountability. Consumer CI gate (option D) = premature — vocabulary 가 적어도 1 CFP cycle stabilize 후 진입.

### Codex BIG CONCERN

> **Vocabulary theater 위험**: agent 가 DDD 단어 emit 하면서 기존 implicit decision flow 유지. "BC", "Aggregate", "Published Language" 가 **spawn decision · review findings · ADR acceptance criteria 를 실제로 바꾸지 않으면** restructure = document 만 향상, runtime 6× lesson 해소 = 0.

### Codex 실용 제안

> **하나의 golden-path worked example** — 실 mctrader ADR (preferably ADR-029~033) 1건 으로 before/after Story field + deputy spawn rationale + Change Plan DDD field + review-verdict finding 전수 시연. **모든 agent prompt + lint rule 이 수렴할 concrete behavioral target.**

---

## 6. 확정 채택 사항 종합 (이 세션에서 spec 작성 기준)

| 영역 | 채택 |
|------|------|
| CFP scope | 2-Epic (codeforge upstream 5 Story + mctrader downstream 3 Story) |
| agent ↔ DDD 매핑 | Hybrid — PL/Architect = authority pair, 6 SubAgent = Domain Service, 2 conditional deputy = Subdomain Specialist |
| Subdomain 분류 결정 시점 | upstream 기준만 / downstream repo-by-repo |
| 양 BC 어휘 | Published Language 분리 (codeforge `docs/glossary.md` + mctrader `docs/glossary.md` 2개 SSOT) |
| mctrader retroactive ADR annotation | Top 10 (ADR-029~033 + 영향도 기준 5 추가) |
| deputy spawn 결정 | "which subdomain under threat" matrix (perspective-contributor 어휘 → subdomain specialist 어휘 transition) |
| Aggregate metaphor strength | 양쪽 다 — PL = metaphor, ArchitectLane 산출물 = real Aggregate (consistency boundary). **CFP 본문이 두 의미 explicit separate 의무** |
| DDD enforcement layer | (1) agent frontmatter DDD role + (2) Story/Change Plan template lint mandatory + (3) review-verdict-v4 contract enum. **Consumer CI gate = phase out (별 CFP)** |
| template field 의무화 | Mandatory + lint enforcement |
| self-reference paradox | non-blocker |
| **Golden-path worked example** | **mctrader ADR-029 또는 ADR-031 1건 으로 full before/after 시연** (Codex pragmatic suggestion) |

---

## 7. Open Questions — 본 세션 진입 후 결정 필요

이전 세션에서 미확인. 새 세션 진입 직후 사용자 confirm 필요:

1. **Golden-path 예시 대상 ADR 선택** — Codex 권고 ADR-029~033 중 어느 것? (추정 best fit = ADR-031 data-domain-decoupling — 4-Layer 모델이 이미 layered architecture 사례 + Open Host Service 사례 + ACL 사례 동시 보유. ADR-029 tier-promotion = aggregate consistency boundary 사례. **권고 = ADR-031**)
2. **upstream Epic = Mega-CFP-1104 단일 vs 5-CFP 분리** — PMO 가 5 Story 권고. Codex 가 "1 CFP cycle stabilize 후 다음 진입" 권고 = mega-CFP 단일 + Phase 1+Phase 2 PR 분리 가능. **권고 = mega-CFP-1104 단일 + Phase 1 docs PR + Phase 2 PR1~PR5 sequential**
3. **downstream Epic 진입 시점** — upstream LAND 직후 vs 1 Story 통합 검증 후 (vocabulary theater 차단 gate). **권고 = upstream Phase 2 PR5 LAND + golden-path worked example 시연 PASS 후 downstream 진입**

---

## 8. ADR 후보 (예약 필요)

본 CFP-1104 가 발의할 신규 ADR:

| ADR # (예측) | 제목 후보 | 영역 |
|---|---|---|
| **ADR-NNN** (다음 번호 — 카운터 atomic reserve 의무 ADR-036) | architectlane-ddd-governance | ArchitectLane 10 agent DDD 재편 헌장 (Q2 Hybrid + Q4 Subdomain Specialist + Q5 양쪽 분리) |

amendment 대상 ADR:
- **ADR-004 architectpl-securityarch-restructure** — Q4 deputy spawn 매트릭스 재정의 amendment
- **ADR-006 testcontract-architect** + **ADR-007 datamigration-architect** + **ADR-014 operational-risk-ssot-distribution** — Q2 deputy = Domain Service 어휘 정렬 amendment
- **ADR-080 agent-role-terminology-deputy-subagent** — DDD 어휘 extension amendment (deputy/subagent terminology 의 DDD pattern 매핑 박제)
- **ADR-064 decision-principle-mandate** + **ADR-068 boundary-completeness-invariants** — DDD enforcement layer (Q6) integration amendment

---

## 9. Phase 2 산출물 의무 목록

PMO 2nd pass 가 확정 분해해야 할 산출물:

### codeforge upstream Epic (Mega-CFP-1104)

| Story | 산출물 | LAND order |
|---|---|---|
| 1 | ADR-NNN architectlane-ddd-governance 신규 + `plugin-codeforge/docs/glossary.md` 신규 (50+ DDD term SSOT) + concept/ 신규 4 entry (bounded-context, ubiquitous-language, aggregate, 4-layer-architecture) | Phase 1 docs PR |
| 2 | 10 agent frontmatter `bounded_context` + `ddd_pattern` field + role-by-role description DDD term injection | Phase 2 PR1 |
| 3 | Story template (`templates/story.md`) `§ubiquitous_language` + Change Plan template (`templates/change-plan.md`) `§bounded_context_boundary` + `§affected_aggregates` block + lint script | Phase 2 PR2 |
| 4 | `templates/inter-plugin-contracts/review-verdict-v4.md` `bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` enum 추가 + version bump v4→v5 | Phase 2 PR3 |
| 5 | `skills/deputy-mandate/` matrix (6+2) Subdomain Specialist 재배치 + 2 conditional deputy 의 spawn trigger = "live operational subdomain 활성" 명시 | Phase 2 PR4 |
| 6 (golden-path) | mctrader ADR-031 (또는 사용자 선택) before/after worked example — Story field + deputy spawn rationale + Change Plan DDD field + review-verdict finding 전수 박제 → `examples/ddd-golden-path-mct031.md` | Phase 2 PR5 |

### mctrader downstream Epic (별 CFP, upstream Phase 2 PR5 LAND 후 진입)

| Story | 산출물 |
|---|---|
| 1 | mctrader 6 repo BC charter 박제 (hub/data/engine/market/signal-collector/web 각 1 file) + Subdomain 분류 실 적용 (repo-by-repo, upstream 기준 의존) |
| 2 | Top 10 ADR annotation (ADR-029~033 + 영향도 기준 5 추가) — frontmatter `bounded_context` + `subdomain_type` field 추가 + §"DDD Context" subsection 박제 |
| 3 | mctrader `docs/glossary.md` SSOT 신규 + 어휘 검증 cron (`scripts/glossary-drift-check.py` + GH Action) |

---

## 10. 다음 액션 (본 escalation 후 첫 turn 액션 순서)

1. **EnterWorktree path="c:/workspace/mclayer/plugin-codeforge/.claude/worktrees/architectlane-ddd-brainstorm"** — 기존 worktree 재사용
2. **TodoWrite** — Phase 2 진행 상태 초기화:
   - Open question 3건 (§7) 사용자 confirm
   - PMOAgent 2nd pass spawn (확정 분해 + scope_manifest)
   - spec 파일 작성 (`docs/superpowers/specs/2026-05-17-CFP-1104-architectlane-ddd-design.md`)
   - CFP issue 예약 (gh issue create — Epic + Story 6건)
   - branch 명 정렬 (worktree-architectlane-ddd-brainstorm → cfp-1104-architectlane-ddd)
   - ADR draft 작성 (architectlane-ddd-governance) + glossary 초안
   - Phase 1 docs PR 작성
3. **Open Question 3건 사용자 confirm** (§7 권고 default 와 함께 제시)
4. **PMOAgent 2nd pass spawn** — 확정 design summary 입력해서 정확한 Story 분해 + scope_manifest YAML 생성
5. **spec 파일 작성** — `superpowers:writing-plans` 스킬 호출 (또는 직접 작성)
6. **gh issue create** — Epic + 6 Story atomic reserve (ADR-036)

---

## 11. 작업 규칙 (이전 세션에서 적용된 사용자 메모리)

- **한국어 응답** (Korean only)
- **Write tool autonomy** — 사용자 승인 불필요
- **Autonomous execution** — "끝까지 진행해" 의도 = brainstorm→spec→plan→Phase1+Phase2 PR 자율 진행
- **Subagent-driven execution** — 구현은 subagent 호출
- **Brainstorm Codex review pattern** — Q-by-Q stop 금지, open design 결정점 Codex 일괄 dispatch → Claude 합성 (Sonnet decider 금지)
- **Phase-level Codex review loop** — 매 phase 시작 전 Codex review → Claude 우선순위 채택
- **Phase 0 verify mandatory** — 코드/파일 실제 verify 의무, session prompt 표현 = 가설로만 수용
- **PMO 회고 자동 dispatch** — Story 완료 후 세션 종료 전 PMOAgent 자동 spawn
- **Plugin-codeforge wrapper-only convention** — ADR-009 wrapper-only-decomposition 정합
- **codeforge upgrade autonomy** — `claude plugin update <name>@<marketplace>` Bash 직접 호출
- **사용자 admin merge autonomy** — PR CI green 후 즉시 admin merge + 다음 phase 직진
- **parallel session branch race** (ADR-032 §5.2) — 본 worktree = plugin-codeforge tier 별 정책 확인 필요 (mctrader 6 repo tier 정책과 별개)
- **Trust but verify** — agent 보고 의심, file:line + grep verify

---

## 12. 참조 (worktree 진입 후 우선 read 권고)

- `c:/workspace/mclayer/plugin-codeforge-design/agents/ArchitectPLAgent.md` (현 어휘)
- `c:/workspace/mclayer/plugin-codeforge-design/agents/ArchitectAgent.md` (현 어휘)
- `c:/workspace/mclayer/plugin-codeforge/docs/adr/ADR-004-architectpl-securityarch-restructure.md` (deputy mandate amendment 대상)
- `c:/workspace/mclayer/plugin-codeforge/docs/adr/ADR-080-agent-role-terminology-deputy-subagent.md` (terminology amendment 대상)
- `c:/workspace/mclayer/plugin-codeforge/docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.md` (충돌 없이 통합 의무)
- `c:/workspace/mclayer/plugin-codeforge/docs/domain-knowledge/domain/governance-principle/decision-style.md` (ADR-064 carrier — 본 ADR 표현 형식 결정)
- `c:/workspace/mclayer/plugin-codeforge/templates/inter-plugin-contracts/review-verdict-v4.md` (enum 추가 대상)
- `c:/workspace/mclayer/plugin-codeforge/.codeforge/counters.json` (CFP 번호 reserve)
- mctrader-hub: `c:/workspace/mclayer/mctrader-hub/docs/adr/ADR-031-data-domain-decoupling.md` (golden-path 후보 1번 — 4-Layer 모델 + OHS + ACL 동시 보유)

---

## 13. 본 escalation 파일 위치

`c:/workspace/mclayer/plugin-codeforge/.claude/worktrees/architectlane-ddd-brainstorm/ESCALATION-PROMPT.md`

새 세션 진입 시 위 SESSION OPEN 메시지 그대로 붙여넣기 → Claude 가 본 파일을 자동으로 read 해서 context 흡수.
```

---

## 사용 방법

1. **현 세션 종료** (또는 그대로 둬도 됨)
2. **plugin-codeforge 디렉토리에서 새 Claude Code 세션 시작**
3. **위 ```SESSION OPEN``` 블록 내용 그대로 첫 메시지로 붙여넣기**
4. **Claude 가 본 ESCALATION-PROMPT.md 를 read 하고 컨텍스트 흡수 후 §10 다음 액션 순서대로 진행**
