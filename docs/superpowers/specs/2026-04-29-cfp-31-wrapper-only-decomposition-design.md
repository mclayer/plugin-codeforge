---
spec_id: cfp-31
title: codeforge wrapper-only decomposition (ζ arc parent design — DocsAgent 제거 + Dev 분리 + 6 lane plugin)
status: Draft
date: 2026-04-29
authors:
  - User (radical pivot — wrapper-only · DocsAgent 제거 · Dev 분리)
  - Claude (Opus 4.7) — synthesis
  - Codex (GPT-5.4 via codex-rescue) — 2 round independent review
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker. 본 spec은 이 패턴을 7 lane으로 일반화)
  - ADR-008 (Inter-plugin Contract Versioning — 5 신규 contract 도입의 거버넌스 SSOT)
  - ADR-009-NEW (Wrapper-only core + writer-distributed lane plugins — 본 spec 결정의 ADR 후보)
related_files:
  - .claude-plugin/plugin.json (codeforge core — wrapper-only로 재정의 + description 갱신)
  - CLAUDE.md (전면 재작성 — 19 agent 매트릭스 → 6 lane plugin composition)
  - docs/orchestrator-playbook.md (writer-distributed model + §10 Orchestrator monopoly + lane plugin 스폰 규칙)
  - agents/DocsAgent.md (삭제 — 역할은 lane plugin + Orchestrator + CI Action에 분산)
  - agents/{Developer,DataEngineer,InfraEngineer,DeveloperPL,QADeveloper}Agent.md (codeforge-develop으로 이동)
  - agents/{RequirementsPL,Domain,RequirementsAnalyst,Researcher}Agent.md (codeforge-requirements로 이동)
  - agents/{ArchitectPL,Architect,CodebaseMapper,Refactor,SecurityArchitect,TestContractArchitect,DataMigrationArchitect}Agent.md (codeforge-design으로 이동)
  - agents/TestAgent.md (codeforge-test로 이동)
  - agents/PMOAgent.md (codeforge-pmo로 이동)
  - templates/{change-plan,adr,domain-knowledge}.md (codeforge-design 또는 codeforge-requirements로 이동)
  - templates/retro.md (codeforge-pmo로 이동)
  - templates/{story-page-structure,impl-manifest,CODEOWNERS,github-pr-template,github-issue-forms}/* (core 잔류 — cross-plugin schema)
  - templates/github-workflows/*.yml (core 잔류 — CI invariant enforcer)
  - docs/inter-plugin-contracts/{requirements-output,design-output,develop-output,test-verdict,pmo-output}-v1.md (NEW × 5)
  - docs/inter-plugin-contracts/review-verdict-v2.md (retrofit BREAKING — verdict 반환 → self-write)
  - scripts/check-inter-plugin-contracts.sh (NEW — 5 contract 일관성 lint)
  - scripts/check-marketplace-sync.sh (NEW — drift 감지 + auto-PR)
  - mclayer/plugin-codeforge-{requirements,design,develop,test,pmo}/* (NEW × 5 외부 repo)
  - mclayer/plugin-codeforge-review/* (existing, retrofit v2 BREAKING)
  - mclayer/marketplace/.claude-plugin/marketplace.json (5 신규 entry + codeforge wrapper version sync)
---

## 0. 사용자 원문 (verbatim)

라운드별 핵심 발화 4건:

> 1. "이전에 codeforge-review를 분리했지만 아직 codeforge가 너무 크다고 생각한다. 이 때문에 역할 분리가 명확하지 않고 변경 범위가 크고 결합이 자꾸 발생해 어려움이 있기 때문에 적극적으로 분리가 가능한 선에서 plugin을 분리하고자 한다. 너와 codex를 통해 기능이 모두 구현 가능한 범위 내에서 공격적으로 분리하기 위한 리뷰를 받아 제안하라."
>
> 2. (Q1 답) "A C" — A: Coupling 차단. 새 deputy/template 추가 시 core CLAUDE.md/playbook 무손상이 목표. C: 기능 응집도. 한 plugin이 한 lane responsibility 완결.
>
> 3. "분리가 될 때 DocsAgent의 역할은 모두 분리해서 가지고 나가야 한다."
>
> 4. "DocsAgent를 제거하고 DeveloperAgents까지 분리해서 codeforge는 이를 조합하는 래퍼 플러그인으로 작성하면 좋겠다는 생각인데."

추가 결정사항:
- **Q5** (해석 확인 + sequencing): "ㅇㅇ 너의 해석이 맞다. codex랑 리뷰 받아봐" — wrapper-only end-state 확정 + Codex 2차 리뷰 의뢰
- **Q6** (로드맵 채택): "a" — Codex 5 조건 + 9-CFP 로드맵 그대로 spec에 박음

## 1. 컨텍스트

### 1.1 ε arc 마무리와 ζ arc 동기

CFP-25(2026-04-28)가 staged ε arc parent design으로서 4 단계(Phase 0a/0b/0c + Phase 1)를 정의 — 모두 머지 완료(CFP-26/27/28/29). 후속 회고 CFP-30 머지(2026-04-29)로 ε arc 클로즈. 본 spec은 ζ arc parent design.

ε arc의 **결과 평가**(CFP-30 retro):
- review subsystem 1개 추출 — `codeforge-review v0.1.0` 분리 + `review_verdict v1` contract
- core agent 19개로 축소 (24 → 19, -21%)
- 그러나 user 측정상 "**core가 아직 너무 크다**, 변경 시 결합·역할 모호 발생"

ε arc의 **남은 통증** (사용자 원문 1번):
- 새 deputy 추가(CFP-18 TestContractArch, CFP-21 DataMigrationArch)가 매번 5+ 파일 수정 — `agents/<Name>.md` + `CLAUDE.md` + `docs/orchestrator-playbook.md` + `templates/change-plan.md` + DesignReviewPL 책임 매트릭스 + (해당되면) FIX decision table
- ε arc는 review만 분리해 이 통증을 부분 완화. arch-deputies / req-deputies / dev / test / pmo lane은 그대로 core 잔류

본 spec(ζ arc)는 **이 통증을 끝까지 추격해 wrapper-only 모델로 수렴**한다.

### 1.2 CFP-25와의 관계 — overrule 사항 명시

ζ arc는 ε arc의 두 가정을 명시적으로 폐기:

| CFP-25 결정 | ζ arc 처리 | 사유 |
|---|---|---|
| §10.1 "DocsAgent 영구 fixture로 남음" — Story §multi-writer 직렬화·GitHub lifecycle 단일 enforcement point 필요 | **폐기** — DocsAgent agent 삭제, 역할은 lane plugin + Orchestrator + CI Action 분산 | 사용자 원문 3·4. 통합 enforcement는 단일 agent가 아니라 `phase-label-invariant.yml` + machine-readable contract registry로 대체 가능 |
| §3.5 / Codex 라운드 2 "DeveloperAgents는 overlay/preset이 충분, 분리 안 함" | **폐기** — Developer/DataEng/InfraEng/DeveloperPL/QADev 모두 codeforge-develop으로 | 사용자 원문 4. wrapper-only 모델은 모든 lane이 plugin이어야 일관 |

다른 CFP-25 결정(`payload-only` doc-write, agent-cluster 보다 lane-coherence 선호)은 본 spec에서 **부분 수정 또는 확장**:
- `payload-only` → **lane-self-write로 변경** (lane plugin이 자기 lane § 직접 Edit + GitHub MCP 직접 호출)
- `lane-coherence` → **극한까지 적용** (모든 lane이 plugin)

### 1.3 Codex 2 라운드 검증 데이터

라운드 1 (agent-cluster vs lane-coherence): Codex가 lane-coherence 권고. 사용자 A+C 우선순위와 일치.

라운드 2 (wrapper-only 가정): Codex **GO with 5 conditions** 판정. 핵심 발견:
1. DocsAgent hidden coupling 7건 식별 (Q1) — 단순 agent 삭제로 자동 해결되지 않음
2. §10 FIX Ledger writer = Orchestrator 단독 권고
3. **Sequencing 역전**: design은 ROI 최대지만 **마지막**으로. split-brain mid-extraction = rollback 불가
4. Marketplace 4-plugin 임계점 — 자동화 없이 7-way 지속 불가
5. Contract harness가 두 번째 추출 전 필수

본 spec은 5 조건 모두 채택.

## 2. 합의된 strategy

### 2.1 End-state: wrapper-only codeforge + 6 lane plugin

```
codeforge (wrapper, 0 agents)
├── Orchestrator playbook (lane sequence + FIX router + spawn 규칙)
├── CLAUDE.md (composition spec — 6 lane plugin 의존 + Inter-plugin contract index)
├── templates/
│   ├── github-workflows/*.yml (CI invariant enforcer — story-init / phase-label-invariant /
│   │                           story-section-1-immutable / phase-gate-mergeable /
│   │                           fix-ledger-sync / subissue-from-impl-manifest)
│   ├── story-page-structure.md (cross-plugin schema)
│   ├── impl-manifest.md (cross-plugin schema)
│   ├── github-issue-forms/, github-pr-template.md, CODEOWNERS.template
├── docs/inter-plugin-contracts/ (6 contract SSOT — review-verdict-v2 retrofit + 5 신규)
├── docs/adr/ (plugin 아키텍처 결정 SSOT)
├── docs/project-config-schema.md (overlay schema)
├── scripts/ (CI helpers: check-inter-plugin-contracts, check-marketplace-sync, bootstrap-labels)
└── presets/ (project shape 별 dev roster preset)

codeforge-requirements (NEW)
codeforge-design       (NEW)
codeforge-develop      (NEW)
codeforge-test         (NEW)
codeforge-review       (existing, retrofit v2 BREAKING)
codeforge-pmo          (NEW)
```

각 lane plugin이 가진 self-write 능력 (DocsAgent 분산):
- 자기 lane Story file § 직접 Edit (직렬화 보증: `phase-label-invariant.yml` single-active)
- 자기 phase prefix comment 게시 (`mcp__github__add_issue_comment`)
- 자기 phase/gate label 부착·detach (`mcp__github__issue_write` add/remove labels)
- 자기 lane owner doc paths Write (예: codeforge-design은 docs/change-plans/** + docs/adr/**)

core 잔류 책임 (유일 enforcement):
- §10 FIX Ledger 직접 Edit (Orchestrator 단독, 후보 i)
- §1 생성 (story-init.yml CI Action)
- §1 immutability + phase label single-active + phase-gate mergeable + FIX Ledger label sync (CI Actions)
- bootstrap script · marketplace sync auto · contract lint harness

### 2.2 Codex 5 조건 — extraction 전제

| # | 조건 | 본 spec 처리 |
|---|---|---|
| 1 | §10 writer Orchestrator 독점 고정 — lane plugin은 FIX event 보고만, ledger 행 직접 append 금지 | F1 (CFP-32)에서 playbook 명시 + invariant SSOT에 박음 |
| 2 | Phase prefix·Story section 소유권·label명·gate명·FIX event 필드 machine-readable shared contract 완성 후 첫 non-review 추출 | F1 (CFP-32) deliverable: machine-readable invariant SSOT (yaml or json) + lint script |
| 3 | encoding 민감 workflow regex (`fix-ledger-sync.yml`, `subissue-from-impl-manifest.yml`) CI syntax test 검증 | F3 (CFP-34) deliverable |
| 4 | Marketplace sync 자동화 (CI drift 감지 + 자동 PR) 구축 후 추출 진행 | F3 (CFP-34) deliverable |
| 5 | 추출 순서 review v2 → PMO 순. design/develop이 먼저 시작되어서는 안 됨 | §9 sequencing 표 |

### 2.3 Writer-distributed model — invariant 재정의

DocsAgent 폐기 후 invariant 보장 메커니즘:

| Invariant | 현재 (ε arc) | ζ arc 후 |
|---|---|---|
| Story file 단일 writer 직렬화 | DocsAgent 단독 agent 정책 | `phase-label-invariant.yml` single-active phase 라벨 + lane plugin 자기 phase active 동안만 § write 권한 행사 + (NEW) `story-section-write-guard.yml` Action: § 변경 PR이 active phase plugin signature 일치하는지 검증 |
| Phase prefix comment 형식 | `agents/DocsAgent.md` SSOT | `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` (NEW machine-readable). `check-inter-plugin-contracts.sh`가 lane plugin 코멘트 dry-run 결과를 registry와 매칭 |
| Phase / gate label registry | `agents/DocsAgent.md` 본문 + `bootstrap-labels.sh` | `docs/inter-plugin-contracts/label-registry-v1.md` (NEW machine-readable) + bootstrap-labels.sh 가 registry를 source로 |
| FIX event schema | `agents/DocsAgent.md` §9 + Story §10 표 schema | `docs/inter-plugin-contracts/fix-event-v1.md` (NEW machine-readable) — Orchestrator 단독 append 시 사용 |
| §1 immutability | `story-section-1-immutable.yml` | (변화 없음) |
| Phase gate mergeable | `phase-gate-mergeable.yml` | (변화 없음) |
| §10 → label sync | `fix-ledger-sync.yml` 단방향 | (변화 없음 — Codex 권고로 양방향화 거부) |
| Sub-issue from impl-manifest | `subissue-from-impl-manifest.yml` 자동 + DocsAgent manual fallback | Action 자동 + (NEW) Orchestrator manual fallback 책임 (codeforge-develop 후보지만 CI 실패는 cross-plugin reconcile 필요 → core가 자연스러움) |
| `gh api` graphql/milestones/discussions fallback | DocsAgent 단독 | core utility actions로 추출 (`scripts/gh-graphql-fallback.sh` 등) — 어떤 plugin도 광범위 graphql 권한 부여 회피 |

## 3. 거부된 대안

### 3.1 Agent-cluster split (Codex 라운드 1 1차 권고)

내가 1차 추천했고 Codex가 일단 검토했으나 라운드 1 후반에 자기 판정으로 **lane-coherence 우위** 결론 내림. 본 spec도 같은 결론.

거부 사유: arch-deputies만 별도 plugin으로 빼고 ArchitectAgent(chief) + change-plan template + ArchitectPL이 core 잔류 시, 새 deputy 추가는 여전히 core SSOT (CLAUDE.md, playbook, change-plan 템플릿)을 흔든다. 명목상 decoupling이지 실질적 A 달성 못함.

### 3.2 Payload-only model (CFP-25 review 패턴 답습)

CFP-25 §10.1 + Codex 라운드 1 권고. lane plugin이 typed payload만 반환, core DocsAgent가 write.

거부 사유: 사용자 원문 3·4. 패턴 일관성을 위해 review v2 retrofit도 self-write로 통일.

부수 비용 인정: ArchitectAgent가 CFP-26 Phase 0a로 docs/change-plans/** + docs/adr/** direct write 권한 획득. ζ arc에서는 그 권한이 codeforge-design plugin 안으로 이동 — Phase 0a 결정이 plugin 경계 안에서 보존됨. 환원 아님.

### 3.3 Big-bang single CFP — 6 plugin 추출을 1 CFP에

거부 사유:
- review_verdict v1이 CFP-29 통째로 먹은 데이터 (1 contract = 1 CFP)
- 5 신규 contract 동시 도입 = 5 CFP 분량을 1에 압축 = ADR-008 manual versioning 한계 초과
- Codex 라운드 2 명시 거부

### 3.4 Foundation CFP 압축 (F1+F2+F3 → 1 CFP)

거부 사유: F1(invariant SSOT)·F2(contract harness)·F3(workflow tests + marketplace sync auto)는 각자 독립적 검증 필요. 1 CFP에 묶으면 검증 신호 분리 불가 → 어느 단계에서 break 났는지 추적 불가. F1 dogfood 결과가 F2 설계 input이 되는 의존성도 있음.

### 3.5 Design first ROI 우선

내가 라운드 1에서 추천. CFP-18/21 root cause 직격으로 ROI 최대.

거부 사유: Codex 라운드 2 TOP 위험 1번 — design은 가장 많은 결합 표면 동시 건드림 (change-plans + adr + §7/§8/§11 mirror + design review packet + phase/gate label + FIX 재진입). pattern 미검증 시점에 시작 → split-brain mid-extraction 발견 → rollback 불가능 (ArchitectAgent direct write는 이미 새 plugin, Orchestrator/core는 여전히 CI template과 §10 소유). split-brain 기간 실패가 design-plugin 버그인지 core-protocol 버그인지 구분 불가.

### 3.6 codeforge wrapper를 documentation repo + git submodule로 대체

Codex 라운드 2 Q6 검토 안. 순수 SW 아키텍처 관점에서는 더 깔끔.

거부 사유: `/plugins install codeforge@mclayer`로 워크플로우 substrate를 deliver하는 Claude Code 배포 관점에서 plugin이 우위. consumer는 1 install로 모든 의존 plugin SessionStart hook chain을 활성화. submodule 방식은 consumer가 manual setup 부담.

### 3.7 codeforge-test 영구 deferred (Codex 라운드 1 FIX_DISCRETIONARY)

거부 사유: 사용자가 wrapper-only를 채택한 이상 모든 lane이 plugin이 되어야 일관. test-lane만 core 잔류 시 wrapper-only 가정 깨짐. ROI 낮음은 sequencing 후순위로 처리 (CFP-37, develop 직전).

## 4. Architecture

### 4.1 7 plugin scope 분해 — 멤버 / owner doc paths / writer 능력

#### codeforge (wrapper, agent 0개)
- **멤버**: 없음 (Orchestrator는 top-level Claude 세션)
- **Owner doc paths**: 없음 (cross-plugin schema는 templates/이지만 read-only reference)
- **Writer 능력**: §10 FIX Ledger Edit (Orchestrator 단독), Story §1 (story-init.yml Action), 기타는 lane plugin에 위임
- **CI 책임**: `templates/github-workflows/*.yml` 6종 (변화 없음) + `scripts/check-inter-plugin-contracts.sh` + `scripts/check-marketplace-sync.sh`
- **plugin.json**: `description: "Composition wrapper for codeforge lane plugins — protocol, CI, schemas, bootstrap, Orchestrator instructions. Agent 0개. 6 lane plugin 의존."`

#### codeforge-requirements (NEW)
- **멤버**: RequirementsPLAgent · DomainAgent · RequirementsAnalystAgent · ResearcherAgent
- **Owner doc paths**: `docs/domain-knowledge/**` (DomainAgent 직접 write)
- **Owner Story sections**: §2 (요구사항 분석) · §5 (도메인 컨텍스트) · §6 (외부 리서치)
- **Writer 능력**: phase prefix `[요구사항]`, `phase:요구사항` label attach·detach, `gate:` 없음 (요구사항은 gate 없는 lane), Discussions Q&A category mutation (DomainAgent)
- **Inter-plugin contract**: `requirements-output-v1.md` (Orchestrator로 전달)

#### codeforge-design (NEW, 가장 마지막 추출)
- **멤버**: ArchitectPLAgent · ArchitectAgent (chief author) · CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent
- **Owner doc paths**: `docs/change-plans/**` (ArchitectAgent) · `docs/adr/**` (ArchitectAgent)
- **Owner templates**: `templates/change-plan.md` · `templates/adr.md` (lane plugin이 schema 자율 진화)
- **Owner Story sections**: §3 (관련 ADR) · §7 (보안 설계 요약 mirror) · §11 mirror에 데이터 마이그레이션 요약
- **Writer 능력**: phase prefix `[설계]`, `phase:설계` ↔ `phase:설계-리뷰` transition (gate label은 codeforge-review가 부착)
- **Inter-plugin contract**: `design-output-v1.md`

#### codeforge-develop (NEW)
- **멤버**: DeveloperPLAgent · QADeveloperAgent · DeveloperAgent · DataEngineerAgent · InfraEngineerAgent (+ overlay role:dev 동적 roster)
- **Owner doc paths**: 없음 (src/**, tests/** write는 consumer 코드 — plugin 자체는 아님)
- **Owner Story sections**: §8 (Test Contract 이행) · §8.5 (Impl Manifest)
- **Writer 능력**: phase prefix `[구현]`, `phase:구현` label, Phase 2 PR open (`mcp__github__create_pull_request`), §8.5 sub-issue 자동(Action) + manual fallback (Action 실패 시)
- **Inter-plugin contract**: `develop-output-v1.md`

#### codeforge-test (NEW)
- **멤버**: TestAgent (functional + performance subset 병렬 스폰)
- **Owner doc paths**: 없음
- **Owner Story sections**: §10 trigger (FAIL 보고 → Orchestrator §10 append)
- **Writer 능력**: phase prefix `[구현-테스트]`, `phase:구현-테스트` label, 결과 PR comment에 baseline 비교 표
- **Inter-plugin contract**: `test-verdict-v1.md`

#### codeforge-review (existing, retrofit v2 BREAKING)
- **멤버**: DesignReviewPLAgent · CodeReviewPLAgent · SecurityTestPLAgent · ClaudeReviewAgent · CodexReviewAgent
- **Owner doc paths**: 없음 (review는 doc owner 아님)
- **Owner Story sections**: §9 (리뷰·테스트 결과)
- **Writer 능력**: phase prefix `[설계리뷰\|구현리뷰\|보안테스트]`, `phase:*-리뷰\|보안-테스트` label, **gate:design-review-pass · gate:security-test-pass label 직접 부착** (v1에서는 core가 부착 — v2에서 self-attach로 전환)
- **Inter-plugin contract**: `review-verdict-v2.md` (v1과 wire compatibility 어려움 — BREAKING bump)

#### codeforge-pmo (NEW)
- **멤버**: PMOAgent
- **Owner doc paths**: `docs/retros/**`
- **Owner templates**: `templates/retro.md`
- **Owner Story sections**: §11 (회고 pointer)
- **Writer 능력**: Epic milestone 생성·진행률 갱신 (`mcp__github__milestone_*` — 권한 신설), Epic Issue body 갱신, PMO 보고서 PR comment, ADR 후보 발의 (codeforge-design에 hand-off)
- **Inter-plugin contract**: `pmo-output-v1.md`

### 4.2 Inter-plugin contract index (6개)

| Contract | 방향 | 상태 |
|---|---|---|
| `review-verdict-v2.md` | codeforge-review ↔ codeforge wrapper | retrofit BREAKING (v1 → v2 — verdict 반환만 → self-write 전환) |
| `requirements-output-v1.md` | codeforge-requirements → codeforge wrapper | NEW |
| `design-output-v1.md` | codeforge-design → codeforge wrapper | NEW |
| `develop-output-v1.md` | codeforge-develop → codeforge wrapper | NEW |
| `test-verdict-v1.md` | codeforge-test → codeforge wrapper | NEW |
| `pmo-output-v1.md` | codeforge-pmo → codeforge wrapper | NEW |

추가 cross-plugin invariant SSOT 3개 (contract는 아니지만 same harness lint):

| SSOT | 목적 |
|---|---|
| `comment-prefix-registry-v1.md` | 11종 phase prefix + `[FIX #N]` 시맨틱스 SSOT |
| `label-registry-v1.md` | type/phase/gate/fix label 분류·이름 SSOT (bootstrap-labels.sh source) |
| `fix-event-v1.md` | Orchestrator §10 append 시 row schema |

### 4.3 SessionStart dependency chain

consumer 측 `.claude/_overlay/` SessionStart hook이 6 plugin 의존을 검증:

```
codeforge SessionStart hook:
  - check installed: codeforge-requirements, codeforge-design, codeforge-develop,
                     codeforge-test, codeforge-review, codeforge-pmo
  - check installed: codex@openai-codex, superpowers@claude-plugins-official,
                     claude-md-management@claude-plugins-official, github@claude-plugins-official
  - check CLI: codex, gh + gh auth status
  - 미설치 시 fail-fast + install 안내
```

각 lane plugin SessionStart hook은 **자기 plugin만** 처리 (CFP-29 패턴 답습).

## 5. Components — 9 CFP 상세

### 5.1 CFP-31 (본 spec)

- 본 design doc commit (no code change)
- ADR-009 신규 (Wrapper-only core + writer-distributed lane plugins)
- v0.18.0 → v0.19.0 (minor — design doc commit)

### 5.2 CFP-32 (F1 — invariant SSOT + §10 Orchestrator monopoly)

**deliverable**:
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` (NEW machine-readable yaml + markdown narrative)
- `docs/inter-plugin-contracts/label-registry-v1.md` (NEW)
- `docs/inter-plugin-contracts/fix-event-v1.md` (NEW)
- `docs/orchestrator-playbook.md` 갱신 — §10 Orchestrator 직접 Edit 명시 + writer-distributed model 설명 (이 시점엔 lane plugin이 없지만 모델만 확정)
- `agents/DocsAgent.md` 갱신 — "본 agent는 ζ arc 진행 중 단계적 해체. CFP-35부터 lane-self-write 전환" 명시 (아직 삭제 안 함)
- `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 확장 — 신규 3 SSOT 검증
- 1-2 real Story로 §10 Orchestrator 직접 Edit dogfood (DocsAgent 우회)
- v0.19.0 → v0.20.0

**검증**:
- 1 dogfood Story에서 Orchestrator §10 Edit 정상 동작
- 3 SSOT lint pass
- DocsAgent §10 권한 회수 후 회기 가능

### 5.3 CFP-33 (F2 — contract lint harness)

**deliverable**:
- `scripts/check-inter-plugin-contracts.sh` (NEW) — 다음 검증:
  - frontmatter 필드: contract_version, status, related_plugins, related_adrs
  - 본문 §1-§3 schema (Schema · Wire · Errors)
  - 예시 (example payload) 유효성 검증 (jsonschema 또는 pyyaml 검증)
  - changelog 섹션 존재
  - compat matrix 존재 (이전 버전과의 호환성)
- `scripts/check-comment-prefix.sh` (NEW) — `comment-prefix-registry-v1.md` 항목 vs 실제 코드(이 시점에는 DocsAgent.md만)에서 사용된 prefix dry-run 매칭
- `scripts/check-label-registry.sh` (NEW) — `label-registry-v1.md` vs `bootstrap-labels.sh` 동기화
- `.github/workflows/contract-lint.yml` (NEW CI workflow)
- v0.20.0 → v0.21.0

**검증**:
- 의도적 frontmatter break 도입 → CI fail
- registry mismatch 도입 → CI fail
- 정상 상태 CI pass

### 5.4 CFP-34 (F3 — workflow yaml syntax tests + marketplace sync auto)

**deliverable**:
- `scripts/check-workflow-yaml.sh` (NEW) — `templates/github-workflows/*.yml` regex syntax test:
  - `fix-ledger-sync.yml`: §10 행 파싱 정규식 fixture 테스트
  - `subissue-from-impl-manifest.yml`: §8.5 매핑표 파싱 fixture 테스트
  - `phase-gate-mergeable.yml`: PR body `Closes #N` 패턴 테스트
- `scripts/check-marketplace-sync.sh` (NEW) — 다음 자동:
  - codeforge wrapper + 6 lane plugin (5 + review)의 `.claude-plugin/plugin.json` mirrored 필드 read
  - mclayer/marketplace의 `marketplace.json` plugins[] entry 비교
  - drift 발견 시 CI fail + automated marketplace PR draft (gh CLI)
- `.github/workflows/marketplace-sync.yml` (NEW CI workflow — codeforge PR merge 감지 → marketplace sync PR auto-open)
- v0.21.0 → v0.22.0

**검증**:
- 의도적 marketplace drift 도입 → CI fail + PR draft 생성 확인
- workflow yaml regex break 도입 → fixture 테스트 fail

### 5.5 CFP-35 (review v2 retrofit — 첫 lane self-write 검증)

**왜 첫째**:
- 이미 plugin이라 코드 이동 0 (mclayer/plugin-codeforge-review 외부 repo 그대로)
- contract revise만 필요 (v1 → v2 BREAKING)
- writer-distributed 패턴 첫 검증

**deliverable** (mclayer/plugin-codeforge-review 측):
- `agents/{Design,Code,Security}ReviewPLAgent.md` 권한 추가:
  - `mcp__github__add_issue_comment`
  - `mcp__github__issue_write` (add/remove labels — gate:* 직접 부착)
  - `Edit("docs/stories/<KEY>.md §9")` — 직접 Edit
- `templates/review-pl-base.md` §3 갱신 — write 단계 추가 (verdict 생성 후 self-write)
- `docs/inter-plugin-contracts/review-verdict-v2.md` 신규 — v1과 BREAKING (verdict.write_actions 필드 제거, 대신 plugin이 직접 수행)
- `.claude-plugin/plugin.json` v0.1.0 → v1.0.0 BREAKING

**deliverable** (codeforge wrapper 측):
- `CLAUDE.md` 갱신 — review v2 self-write 명시
- `docs/inter-plugin-contracts/review-verdict-v1.md` archived (Archived status — CFP-D 시점 전환)
- `docs/inter-plugin-contracts/review-verdict-v2.md` 사본 (SSOT는 codeforge-review)
- v0.22.0 → v0.23.0 (지금 시점엔 BREAKING bump 안 함 — codeforge wrapper는 review를 spawn할 뿐 직접 의존 코드 없음)
- mclayer/marketplace sync PR (auto from F3)

**검증**:
- 1-2 real Story가 review v2 self-write로 §9 + comment + gate label 정상
- core DocsAgent가 review verdict 처리 안 하는지 audit (회기 가능)
- review plugin 단독 bump가 codeforge wrapper bump 야기 안 함

### 5.6 CFP-36 (codeforge-pmo)

**왜 둘째**:
- 가장 작은 lane (PMOAgent 1개)
- 결합 약함 (Cross-cutting, lane gate에 무관)
- writer-distributed 패턴 두 번째 검증 — 코드 이동 첫 사례

**deliverable** (mclayer/plugin-codeforge-pmo 신규 외부 repo):
- `.claude-plugin/plugin.json` v0.1.0
- `agents/PMOAgent.md` (이동) + 권한 확장 (Issue/PR comment, milestone mutation `mcp__github__milestone_*` — 가능 여부 확인 필요. 불가 시 `gh api repos/*/milestones*` fallback)
- `templates/retro.md` (이동)
- `overlay/hooks/regen-agents.sh` + `session-start-deps-check.sh` (codeforge core 설치 verify)
- `docs/inter-plugin-contracts/pmo-output-v1.md` (NEW)
- `README.md`, `CHANGELOG.md`

**deliverable** (codeforge wrapper 측):
- `agents/PMOAgent.md` 삭제
- `templates/retro.md` 삭제
- `CLAUDE.md` "Cross-cutting PMOAgent" 섹션 → "codeforge-pmo plugin 의존" 으로 갱신
- SessionStart hook 의존 6 plugin 명시
- v0.23.0 → v1.0.0 (첫 BREAKING — 새 plugin install 의무)
- mclayer/marketplace sync PR (auto from F3)

**검증**:
- 1 Story 회고가 codeforge-pmo self-write로 정상 (retro.md + Story §11 + Epic milestone 갱신)
- codeforge wrapper bump 0건 (PMO 내부 변경 시)

### 5.7 CFP-37 (codeforge-requirements)

**deliverable** (mclayer/plugin-codeforge-requirements 신규):
- 4 agent 이동: RequirementsPL, Domain, Analyst, Researcher
- `templates/domain-knowledge.md` 이동
- `docs/domain-knowledge/**` direct write 권한 plugin 안에 보존
- Discussions Q&A category mutation 권한 (DomainAgent — `gh api repos/*/discussions*` fallback)
- `docs/inter-plugin-contracts/requirements-output-v1.md` (NEW)

**deliverable** (codeforge wrapper):
- 해당 agent + template 삭제
- v1.0.0 → v1.1.0 (minor — wrapper 자체는 BREAKING 없음, lane plugin 신규는 wrapper 입장 minor)

**검증**: 1 Story 요구사항 lane이 codeforge-requirements self-write로 정상.

### 5.8 CFP-38 (codeforge-test)

**deliverable**: TestAgent 이동 + `docs/inter-plugin-contracts/test-verdict-v1.md` (NEW). codeforge-test은 가장 단순 — TestAgent 1개, owner doc 없음, Story §10 trigger만 (Orchestrator append).

**검증**: 1 Story 구현테스트 lane이 codeforge-test self-report로 정상 (FAIL 시 Orchestrator §10 append 정상).

### 5.9 CFP-39 (codeforge-develop)

**deliverable**: 5 agent 이동 (Developer, DataEng, InfraEng, DeveloperPL, QADev) + role:dev roster discovery 메커니즘 plugin 안에 보존 + presets/* 이동 (preset도 lane 자체 진화) + `docs/inter-plugin-contracts/develop-output-v1.md` (NEW).

**검증**: 1 Story 구현 lane이 codeforge-develop self-write로 정상. role:dev roster overlay 확장이 codeforge-develop 내부에서 동작 (wrapper 무관).

### 5.10 CFP-40 (codeforge-design — 가장 마지막)

**왜 마지막**:
- 가장 큰 표면 (5 deputies + chief + PL + 2 templates + Story §3·§7·§11 mirror + design review packet + FIX 재진입)
- 패턴이 5 plugin (review v2 + pmo + requirements + test + develop)에서 검증된 후 진입 → split-brain 위험 최소

**deliverable**: 7 agent 이동 (ArchitectPL, Architect chief, 5 deputies) + `templates/change-plan.md` · `templates/adr.md` 이동 + `docs/inter-plugin-contracts/design-output-v1.md` (NEW).

**검증**: 1 Story 설계 lane이 codeforge-design self-write로 정상. 새 deputy 추가 (가상 시나리오) 시 codeforge wrapper bump 0건.

**최종 상태**:
- codeforge wrapper agent 0개
- DocsAgent 완전 삭제 (CFP-32 시점부터 단계적 권한 회수, CFP-40 시점에 agent file 최종 삭제)
- v??.??.?? → v2.0.0 (전체 ζ arc 완료 milestone)

## 6. Data flow

### 6.1 As-is (ε arc 후)

```
RequirementsPL → write queue → DocsAgent drain → docs/stories/<KEY>.md §2-§6
ArchitectAgent → docs/change-plans/*.md direct (CFP-26 Phase 0a)
ArchitectAgent → docs/adr/*.md direct
DomainAgent → docs/domain-knowledge/**/*.md direct
PMOAgent → docs/retros/*.md direct
DesignReviewPL (codeforge-review) → review_verdict v1 → core DocsAgent drain → §9 + comment + label
DeveloperPL → write queue → DocsAgent drain → §8/§8.5 + Phase 2 PR open
TestAgent → write queue → DocsAgent drain → §10 trigger
Orchestrator → DocsAgent 의뢰 → §10 FIX Ledger append
```

### 6.2 ζ arc 후 (CFP-40 완료)

```
codeforge-requirements → docs/stories/<KEY>.md §2-§6 direct + [요구사항] comment + phase:요구사항 label
                       → docs/domain-knowledge/**/*.md direct
codeforge-design → docs/change-plans/*.md direct + docs/adr/*.md direct + Story §3·§7·§11 mirror direct
                 → [설계] comment + phase:설계 ↔ phase:설계-리뷰 label transition
codeforge-review → §9 direct + [설계리뷰|구현리뷰|보안테스트] comment + phase:*-리뷰|보안-테스트 label
                 + gate:design-review-pass / gate:security-test-pass direct
codeforge-develop → §8/§8.5 direct + [구현] comment + phase:구현 label + Phase 2 PR open
                  + sub-issue manual fallback (Action 실패 시)
codeforge-test → [구현-테스트] comment + phase:구현-테스트 label + 결과 PR comment
               → FAIL 시 Orchestrator로 fix-event-v1 보고 (Story §10 직접 append 안 함)
codeforge-pmo → docs/retros/*.md direct + Story §11 mirror direct + Epic milestone 갱신
              + ADR 후보 발의 시 codeforge-design hand-off
Orchestrator → §10 FIX Ledger append (lane plugin fix-event-v1 보고 받아서)
             → Story §1 (story-init.yml CI Action 자동 — Orchestrator 무관)
```

직렬화 보증: `phase-label-invariant.yml`이 single-active phase 강제. lane plugin은 자기 phase active 동안만 § write 권한 행사. 추가로 (NEW) `story-section-write-guard.yml` Action: § 변경 PR이 active phase plugin signature 일치하는지 검증.

## 7. Error handling / Edge cases — Codex hidden coupling 7건

### 7.1 Story § multi-writer 직렬화 (HIGH)

**위험**: lane plugin 둘이 동시 active phase 진입 가능성 (예: 설계-리뷰 PASS와 구현 phase 전환 사이 race).

**완화**:
- `phase-label-invariant.yml` single-active 강제 — Action이 두 phase 라벨 동시 부착 시 reject
- (NEW) `story-section-write-guard.yml` Action — § 변경 PR signature(commit author + phase active 시점) 검증
- Stale branch 덮어쓰기는 git rebase + force-push protection으로 처리 (이미 존재)

### 7.2 Phase prefix comment SSOT (HIGH)

**위험**: `agents/DocsAgent.md` 본문에 있던 11종 prefix가 lane plugin에 흩어지면 fork.

**완화**: F1 (CFP-32) deliverable `comment-prefix-registry-v1.md` — machine-readable SSOT. F2 (CFP-33) `check-comment-prefix.sh`가 lane plugin 코드와 registry 매칭 검증.

### 7.3 Sub-issue manual fallback (HIGH)

**위험**: `subissue-from-impl-manifest.yml` Action 부분 성공 후 addSubIssue 실패 시 reconcile owner 부재.

**완화**: Orchestrator가 fallback 책임 — top-level Claude 세션이 Action 결과 read + 부족 시 `mcp__github__sub_issue_write` manual call. core utility script `scripts/sub-issue-reconcile.sh` (CFP-34에서 신설).

### 7.4 `gh api` graphql/milestones/discussions fallback (HIGH)

**위험**: 모든 plugin에 광범위 graphql 권한 부여 = DocsAgent anti-pattern 재현.

**완화**: core utility shell scripts (`scripts/gh-graphql-fallback.sh` 등)에 narrowed function 정의. 각 lane plugin은 자기 lane용 narrow API만 호출 (예: codeforge-pmo는 milestones만, codeforge-requirements는 discussions만).

### 7.5 Milestone tracking 권한 (MED)

**위험**: PMOAgent가 현재 milestone mutation 권한 없음.

**완화**: codeforge-pmo plugin frontmatter에 `mcp__github__milestone_*` 또는 `Bash(gh api repos/*/milestones*)` 권한 추가. CFP-36 deliverable.

### 7.6 Discussion routing 권한 (MED)

**위험**: DomainAgent가 현재 Discussion write 권한 없음.

**완화**: codeforge-requirements plugin frontmatter에 `Bash(gh api repos/*/discussions*)` 권한 추가. CFP-37 deliverable.

### 7.7 §10 race 방지 (HIGH)

**위험**: Orchestrator가 §10 Edit 도중 lane plugin이 §3 Edit 동시 시도 → git conflict.

**완화**:
- Orchestrator는 lane plugin spawn 사이 idle window에 §10 patch (playbook 명시)
- §10 Edit 전 Orchestrator가 stale-read 체크 (`git pull --rebase` 또는 file mtime 비교)
- 충돌 발생 시 fail-fast + 사용자 ESCALATE (자동 재시도 금지 — append-only ledger 손상 위험)

## 8. Testing / Validation

### 8.1 CFP-32 (F1) 검증

- 1-2 real Story로 §10 Orchestrator 직접 Edit 시도 — DocsAgent 우회 후 정상 동작
- 3 SSOT (comment-prefix / label-registry / fix-event) lint pass
- agents/DocsAgent.md "단계적 해체 진행 중" 메모가 audit trail 보존

### 8.2 CFP-33 (F2) 검증

- 의도적 frontmatter break 도입 → CI fail 확인
- registry mismatch 도입 → CI fail
- 정상 상태 CI pass + warning 없음

### 8.3 CFP-34 (F3) 검증

- 의도적 marketplace drift 도입 → CI fail + automated PR draft 생성 확인
- workflow regex fixture 테스트 100% pass
- `fix-ledger-sync.yml` regex가 §10 schema 변화에 robust한지 검증

### 8.4 각 추출 CFP (CFP-35~CFP-40) 검증

공통 합격 조건:
- 1-2 real Story가 해당 lane self-write로 정상 동작 (회고 포함)
- 해당 lane plugin 단독 bump 시 codeforge wrapper bump 0건
- contract lint pass (CFP-33 deliverable에 의해)
- marketplace sync 자동 (CFP-34 deliverable에 의해)
- 회고에 hidden coupling 발견 사례 기록

### 8.5 ζ arc 종합 검증 (CFP-40 완료 후)

- 가상 시나리오: "새 architect deputy 추가" — codeforge-design 안에서 끝, codeforge wrapper bump 0건 (사용자 A 우선순위 충족 검증)
- 가상 시나리오: "새 role:dev 추가 (예: ML Engineer)" — codeforge-develop preset 추가만, wrapper 무관 (overlay·preset 모델 보존 검증)
- core agent 수 19 → 0 (DocsAgent 포함 모두 분산)
- 6 contract 모두 lint pass + 2 CFP 연속 wrapper bump 없는 lane plugin internal 변경 사례

## 9. Migration / CFP sequencing — 9 CFP 로드맵

```
CFP-31 (본 spec) : design doc commit (no code change) + ADR-009 신설
                   v0.18.0 → v0.19.0

CFP-32 (F1)      : §10 Orchestrator monopoly + 3 invariant SSOT machine-readable
                   v0.19.0 → v0.20.0
                   [검증: 1-2 dogfood Story]

CFP-33 (F2)      : Contract lint harness (check-inter-plugin-contracts.sh + 2 보조)
                   v0.20.0 → v0.21.0
                   [검증: 의도적 break → CI fail]

CFP-34 (F3)      : Workflow yaml syntax tests + marketplace sync auto
                   v0.21.0 → v0.22.0
                   [검증: 의도적 drift → auto-PR 확인]

────────────────── 여기까지 foundation. 아래부터 lane 추출 ──────────────────

CFP-35           : codeforge-review v2 retrofit (BREAKING — review-side v0.1.0 → v1.0.0)
                   wrapper v0.22.0 → v0.23.0 (wrapper 자체는 BREAKING 없음)
                   [검증: review v2 self-write 1-2 Story]

CFP-36           : codeforge-pmo (NEW)
                   wrapper v0.23.0 → v1.0.0 (첫 wrapper BREAKING — install 의무 추가)
                   [검증: PMO self-write 1 Story]

CFP-37           : codeforge-requirements (NEW)
                   wrapper v1.0.0 → v2.0.0 BREAKING (consumer 신규 plugin install 의무)
                   [검증: 요구사항 lane self-write 1 Story]

CFP-38           : codeforge-test (NEW)
                   wrapper v2.0.0 → v3.0.0 BREAKING
                   [검증: 구현테스트 lane self-report → Orchestrator §10 append 정상]

CFP-39           : codeforge-develop (NEW)
                   wrapper v3.0.0 → v4.0.0 BREAKING
                   [검증: 구현 lane self-write + role:dev roster overlay 동작]

CFP-40           : codeforge-design (NEW — 가장 마지막)
                   wrapper v4.0.0 → v5.0.0 BREAKING
                   [추가 검증: 가상 새 deputy 추가 시 wrapper 무손상]
                   DocsAgent agent file 최종 삭제 (CFP-32부터 단계적 회수 끝)

CFP-41 (회고)    : ζ arc 회고 + ADR-009 status Accepted → Adopted (실 적용 결정으로 표시)
                   v5.0.0 → v5.0.1 (patch — retro만)
```

각 CFP 평균 2주 가정 시 약 18-22주 (4-5개월). 압축은 부분 가능하지만 Codex 5 조건 위반 시 split-brain 위험.

**버전 정책 노트**:
- CFP-32~34 (foundation) — 모두 minor (no BREAKING, additive) → v0.19→v0.20→v0.21→v0.22
- CFP-35 (review v2 retrofit) — codeforge-review 측 v0.1.0 → v1.0.0 BREAKING (verdict schema 변경). codeforge wrapper 측은 spawn만 하므로 BREAKING 없음 → v0.22→v0.23
- CFP-36~40 (lane plugin 신설) — consumer 측 plugin install 의무 추가가 BREAKING의 정의 (`/plugins install <plugin>` 필수 step 추가) → wrapper bump v0.23 → v1.0.0 → v2.0.0 → v3.0.0 → v4.0.0 → v5.0.0
- 누적 5 wrapper BREAKING은 ζ arc 비용의 일부로 수용. consumer는 매 단계 README install 안내를 따라 진행.

## 10. Risks / Open issues

### 10.1 9 CFP commitment 크기 — 4-5개월

ζ arc는 ε arc(CFP-25~30, 4 CFP 약 2개월)의 2배 이상. 중간 abandon 시 sunk cost 큼.

**완화**: 각 단계가 독립 검증 + dogfood. CFP-32 dogfood 실패 시 그 시점 abandon → DocsAgent 환원 가능 (회수 비용 작음). CFP-35 review v2 retrofit 실패 시도 회수 가능. CFP-36 이후 abandon은 wrapper plugin schema가 일관 유지된다면 부분 환원 가능 (lane plugin은 그대로 두고 wrapper만 다시 모놀리식 회기).

### 10.2 codeforge-design이 마지막 — 가장 큰 위험은 마지막에 노출

ROI 최대인 design을 마지막에 두는 sequencing은 split-brain 위험 회피 목적. 단점: 마지막 단계에서 break 발견 시 8 CFP 누적 sunk cost 후 abandon 결정 어려움.

**완화**: CFP-39(develop) 검증 완료 시점에 design 시뮬레이션 dry-run (실제 추출 안 하고 contract만 작성 + 1 Story 가상 흐름) → 실제 CFP-40 진입 전 위험 평가.

### 10.3 wrapper plugin schema 검증 — agent 0개 plugin이 valid한가?

Claude Code plugin schema가 `agents/` 기여를 강제하는지 unknown. plugin.json만 + templates만 + docs만 plugin이 install 가능한지 확인 필요.

**완화**: CFP-32 시점에 Claude Code plugin schema spec 확인 (현재 documentation 미참조). agent 0개 plugin이 reject되면 codeforge wrapper에 dummy/utility agent 1개 (예: bootstrap-helper) 유지 — 이는 wrapper 가치 제안 손상 안 함.

### 10.4 Contract harness가 semantic intent 검증 못함

Codex 라운드 2 명시: 구조 lint(필드/enum/version/예시/changelog/compat)는 가능. semantic intent (예: "FIX cause 분류 정확성", "ADR이 prior ADR을 올바르게 supersede하는가")는 lint 불가능 → prose drift 잔여.

**완화**: 회고 단계에서 semantic drift 사례 수집 → 점진적 contract 정밀화 (예: enum 추가, validation 추가). contract harness 완벽주의 추구 안 함 — 80% 보호로 만족.

### 10.5 ADR-008 manual versioning 한계 — 6 contract 동시 진화

ε arc는 1 contract만 있어서 manual versioning 견딤. 6 contract는 cross-contract 의존성 (예: review-verdict-v2가 fix-event-v1 reference) 발생 가능. 일관 진화 어려움.

**완화**: CFP-33 contract harness가 cross-contract dependency 매트릭스 검증. v-bump 시 의존 contract도 강제 점검. 자동화 미흡 부분은 review CFP에서 manual catch.

### 10.6 Marketplace 7-way sync — Codex 임계점 초과

CFP-34 deliverable이 sync 자동화. 그러나 마켓플레이스 측 PR review는 여전히 manual. 7 PR 동시 발생 시 reviewer 부담.

**완화**: marketplace sync PR은 autoMerge 라벨로 mergeable (codeforge plugin 측 main merge가 source-of-truth — marketplace는 mirror). 사용자 (1인 maintainer 환경)가 자동 머지 정책 채택 시 부담 거의 없음.

### 10.7 Story §10 Orchestrator 단독 — sequential bottleneck

§10 append가 Orchestrator 직렬. 병렬 lane FIX 동시 발생 시 직렬 처리 → 약간 느림.

**완화**: 실제 시나리오에서 동시 lane FIX는 드묾 (lane sequence가 직렬). idle window에 patch로 충분. 측정해 문제되면 후속 spec.

### 10.8 사용자가 모를 가능성 (Codex Q7) — 재명시

**TOP 위험**: codeforge-design을 contract harness 미완성 상태에서 시작 시 split-brain mid-extraction = rollback 불가능.

**완화**: 본 spec 시퀀싱이 명시적으로 design을 마지막에. CFP-32~34 foundation을 못 끝내면 CFP-40 진입 자체가 차단된다고 playbook에 박음.

## 11. Codex 라운드 1·2 학습 데이터 (transparency)

### 11.1 라운드 1 (agent-cluster vs lane-coherence)

- **내 1차 추천**: agent-cluster (4 plugin: arch-deputies / req-deputies / test-lane / pmo)
- **Codex 라운드 1 verdict**: lane-coherence > agent-cluster. 이유: agent-cluster는 PL/chief/template을 core 잔류시켜 실질 decoupling 못함 — 명목상 A 충족이지 실질적 A 못함
- **본 spec 채택**: lane-coherence (사용자 wrapper-only 채택으로 극한까지)

### 11.2 라운드 1 → 라운드 2 사용자 pivot

라운드 1 후 사용자가 두 번 pivot:
1. "DocsAgent의 역할은 모두 분리해서 가지고 나가야 한다" — DocsAgent 영구 fixture 폐기 (CFP-25 §10.1 overrule)
2. "DeveloperAgents까지 분리해서 codeforge는 이를 조합하는 래퍼 플러그인" — Dev 분리 + wrapper-only (CFP-25 §3.5 overrule)

라운드 2는 새 가정에서 검증.

### 11.3 라운드 2 (wrapper-only 모델 위험 평가)

- **Codex 판정**: GO with 5 conditions
- **핵심 발견**: hidden coupling 7건 (Q1 표) — 단순 agent 삭제로 자동 해결 안 됨
- **sequencing 역전**: design 첫째 → design 마지막. split-brain 위험 회피
- **marketplace 4-plugin 임계점**: 자동화 없이 7-way 지속 불가
- **Top 위험 1개**: Story section serialization + comment prefix contract machine-enforced 전 design 추출 = split-brain unrecoverable

### 11.4 본 spec의 양보

- Codex의 "payload-only model" → 폐기 (사용자 lane-self-write 채택)
- Codex의 "DocsAgent 영구 fixture" → 폐기 (사용자 overrule)
- Codex의 "design 마지막" → **수용**
- Codex의 "5 조건 모두 충족 후 추출" → **수용**

본 spec은 사용자 방향성과 Codex의 리스크 분석을 합쳐 9 CFP 로드맵으로 구체화.

---

## 부록 A. plugin.json description 갱신 예시 (codeforge wrapper)

```json
{
  "name": "codeforge",
  "version": "0.19.0",
  "description": "Composition wrapper for codeforge lane plugins — protocol, CI, schemas, bootstrap, Orchestrator instructions. Agent 0개 (ζ arc CFP-40 완료 시점). 6 lane plugin 의존: codeforge-{requirements,design,develop,test,review,pmo}. 7 plugin 생태계 + Inter-plugin Contract v1/v2 (ADR-008).",
  "author": { "name": "Josh" },
  "keywords": [
    "orchestration",
    "composition",
    "lane-plugins",
    "writer-distributed",
    "wrapper-only"
  ]
}
```

## 부록 B. CFP-25 결정 vs ζ arc 결정 매트릭스

| 영역 | CFP-25 (ε arc) | CFP-31 (ζ arc) |
|---|---|---|
| DocsAgent 처리 | 영구 fixture (§10.1) | 단계적 해체 → 최종 삭제 |
| DeveloperAgents 처리 | overlay 충분 (§3.5) | codeforge-develop 분리 |
| 추출 단위 | review subsystem 1개 | 6 lane plugin (5 신규 + review v2 retrofit) |
| 추출 패턴 | payload-only (verdict 반환, core write) | lane-self-write |
| 추출 모델 | agent-cluster (review만 확인) | lane-coherence 극한 |
| 추출 순서 | review 1회 | review v2 → pmo → req → test → develop → design |
| Foundation 사전 작업 | none (직접 추출) | 3 CFP (F1/F2/F3) 사전 |
| Contract 도입 비용 | 1 contract 1 CFP | 6 contract over 6 CFP + harness |
| Marketplace sync | manual | 자동화 (CFP-34) |
| BREAKING bump 누적 | 1 (codeforge v0.16 → v0.17) | 5+ (wrapper v1 → v2 → ... → v5; review v0.1 → v1) |
| arc 길이 | 4 CFP, 약 2개월 | 9 CFP, 약 4-5개월 |

## 부록 C. ADR-009 신설 골자

- **제목**: Wrapper-only core + writer-distributed lane plugins
- **상태**: Proposed (CFP-31 머지 시 Accepted)
- **컨텍스트**: ε arc 후 사용자 진단 — core 19 agent가 여전히 결합 진원지. CFP-18·CFP-21 deputy 추가가 5+ 파일 흔든 통증 반복
- **결정**: codeforge core를 wrapper-only로 (agent 0개) + 6 lane plugin이 self-write 권한 보유
- **결과**: A(coupling 차단) 실질 달성 + C(기능 응집도) 극한. 비용: 9 CFP + Marketplace 7-way + Contract harness + BREAKING bump 누적
- **대안**: payload-only (CFP-25 review 패턴) — 거부 (사용자 wrapper-only 채택). agent-cluster — 거부 (실질 decoupling 못함)
- **다이어그램**: §4.1 ASCII
- **관련 파일**: 본 spec related_files

## 부록 D. ζ arc 진입 직전 체크리스트

CFP-32 진입 전:
- [ ] 본 spec(CFP-31) 머지
- [ ] ADR-009 status Accepted
- [ ] PMOAgent 회고 — ε arc 평가 + ζ arc 진입 의향 confirm
- [ ] 사용자 9 CFP commitment 명시 합의
- [ ] Claude Code plugin schema spec 확인 (agent 0개 plugin valid 검증) — Risk 10.3
