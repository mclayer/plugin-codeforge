---
spec_id: cfp-19
title: 오케스트레이션 병렬화 — Tier 1+2 (R1-R11) Story 처리시간 단축
status: Approved
date: 2026-04-28
authors:
  - Orchestrator (parallelization audit synthesizer)
  - CodexReviewAgent (P-1..P-8, GPT-5)
  - general-purpose self-audit (a..k)
related_adrs:
  - ADR-001 (review agent unification)
  - ADR-002 (consumer guide)
  - ADR-004 (ArchitectPL + SecurityArch)
  - ADR-006 (TestContractArch)
related_files:
  - docs/orchestrator-playbook.md
  - CLAUDE.md
  - agents/DocsAgent.md
  - agents/DesignReviewPLAgent.md
  - agents/CodeReviewPLAgent.md
  - agents/SecurityTestPLAgent.md
  - agents/ArchitectPLAgent.md
  - agents/DeveloperPLAgent.md
  - agents/TestAgent.md
  - templates/github-workflows/subissue-from-impl-manifest.yml
---

## 0. 사용자 원문 (Verbatim)

> 전체적으로 너무 느리다. 병렬로 수행할 수 있는 작업들이 있을텐데 너무 순차적으로 수행하는게 아닌지 codex와 함께 리뷰해서 계획된 CFP보다 우선해서 개정하자.

## 1. 컨텍스트 — 현재 직렬 병목

CFP-17·CFP-18 dogfooding 실증에서 **Story 1건 처리시간 60-90분 관찰**. PMO 권고 기존 CFP-19 (DataMigration) / CFP-20 (DesignReview checklist)보다 **사용자 critical feedback** 우선. Codex(GPT-5) + general-purpose 두 독립 감사로 11개 직렬 병목 식별, 두 감사가 강하게 수렴.

### 1.1 Top 병목 (감사 합의)

| # | 병목 지점 | 현 직렬 패턴 | 평균 추가 지연 |
|---|----------|-------------|--------------|
| B1 | DocsAgent write queue drain | "다음 lane 시작 전" 모든 의뢰 직렬 drain | 2-5분 |
| B2 | ReviewPL severity 종합 후 docs save | save 완료 → 다음 lane 통보 | 1-2분 |
| B3 | Claude/Codex review 워커 spawn | PL이 두 워커 한 packet으로 순차 trigger | 3-5분 |
| B4 | FIX 루프 single-track | DeveloperPL 진단 → ArchitectPL 판정 → 재실행 직렬 | 5-10분 |
| B5 | §8.5 Impl Manifest 수동 작성 | DeveloperPL이 git diff 매핑 직접 타이핑 | 2-4분 |
| B6 | lane packet 재구성 | 매 spawn마다 PL이 packet 재조립 | 1-2분 |
| B7 | Phase 1 merge ↔ Phase 2 prep | Phase 1 merge 대기 → 그 다음 Phase 2 prep 시작 | 3-5분 |
| B8 | ArchitectPL 검수 무차별 통합 | deputy 4-5인 산출물 모두 통합 후 검수 | 2-4분 |
| B9 | TestAgent 기능∥성능 직렬 | 기능 PASS → 성능 시작 | 3-5분 |
| B10 | 보안 1차 layer fetch 직렬 | SecurityTestPL spawn 후 gh api fetch | 1-2분 |
| B11 | FIX mechanical typo·link 처리 | 일반 FIX와 동일 full DeveloperPL 진단 루프 | 5-15분/건 |

**합계 예상 단축**: Tier 1 (B1-B8) 15-25분, Tier 2 (B9-B11) 5-7분. Story 1건당 **20-32분 단축** = 30-40% reduction.

## 2. 결정 — Tier 1+2 채택

R1-R11 11개 recommendation을 ADR 변경 없이(non-BREAKING) 적용. ArchitectPL N=5 deputy 운영 안정화 후 별도 ADR-007(§section ownership) 발의는 본 CFP 범위 외 (Tier 3 deferred).

### 2.1 R1 — DocsAgent dual-mode drain (B1 해소)

**현재**: Orchestrator가 "lane 종료 직전 DocsAgent 1회 spawn → 모든 queue 의뢰 drain → 완료 대기" 직렬.

**변경**: write queue 의뢰를 2종으로 라벨링.
- `mode: blocking` — 다음 lane이 의존하는 산출물 (예: §1-7 Phase 1 PR open 직전, §8.5 Impl Manifest, gate 라벨 전후, ADR draft commit)
- `mode: background` — 누적 보고·코멘트·monitoring (예: agent 산출물 요약 코멘트, 회고 §11 append, FIX Ledger Iter mirror)

Orchestrator는 `mode: blocking` 의뢰만 다음 lane 진입 게이트로 사용. `mode: background`는 다음 lane spawn 후 별도 DocsAgent run으로 처리. Lane 진입 시 background queue 잔존 시 다음 spawn에 합류.

**파일**: [agents/DocsAgent.md](../../agents/DocsAgent.md) §write queue 형식 + [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §11 + DocsAgent 의뢰자 18종 md (mode 라벨 명시 의무).

### 2.2 R2 — ReviewPL pre-save handoff (B2 해소)

**현재**: ReviewPL이 severity 종합 → DocsAgent로 결과 save → save 완료 후 Orchestrator가 다음 lane spawn.

**변경**: ReviewPL이 severity 결정(PASS/FIX) 즉시 Orchestrator에 verdict return → Orchestrator가 다음 lane spawn 트리거 + 동시에 DocsAgent에 결과 save 의뢰 (`mode: background`). Save는 lane 진행과 병렬.

**파일**: [templates/review-pl-base.md](../../templates/review-pl-base.md) §3 (verdict-first protocol) + 3 ReviewPL md (DesignReview/CodeReview/SecurityTest).

### 2.3 R3 — Orchestrator-direct dual review worker spawn (B3 해소)

**현재**: ReviewPL이 ClaudeReviewAgent → CodexReviewAgent 워커를 spawn한다고 documented 되어 있으나 실제로는 PL이 lane packet 작성 후 두 워커를 한 메시지에 dispatch.

**변경 (현실 정합)**: PL은 lane packet만 작성해 Orchestrator에 return. **Orchestrator가 두 워커를 한 message에서 병렬 spawn**. PL은 결과 수령 → severity 종합. PL의 spawn 책임 explicit하게 Orchestrator로 이관 (서브에이전트 재귀 spawn 금지 platform 제약 정합).

**파일**: 3 ReviewPL md, [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §스폰 시퀀스, [CLAUDE.md](../../../CLAUDE.md) 스폰 시퀀스 다이어그램.

### 2.4 R4 — FIX speculative pipelining (B4 해소)

**현재**: review FIX → DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → "구현 원인" 시 DeveloperPL 재spawn → 재구현 → 재리뷰. 진단·판정 직렬.

**변경**: review FIX 트리거 시 Orchestrator가 DeveloperPL 1차 진단 + ArchitectPL 최종 판정을 **병렬 spawn**. ArchitectPL 판정 packet에 "DeveloperPL 진단 docs/stories/<KEY>.md §10 Iter N row append 후 차후 fetch" 명시 → ArchitectPL이 스스로 review findings + Change Plan + ADR 정합성 평가. 결과 충돌 시 Orchestrator가 ArchitectPL verdict 우선 (chief judge 역할 보존).

**낙관적 가속 가정**: 80% 케이스에서 두 진단 일치 (구현 원인 vs 설계 원인). 충돌 20% 케이스만 ArchitectPL 우선으로 retry → 평균 5분 단축.

**파일**: [agents/DeveloperPLAgent.md](../../agents/DeveloperPLAgent.md), [agents/ArchitectPLAgent.md](../../agents/ArchitectPLAgent.md), [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §FIX state machine.

### 2.5 R5 — §8.5 Impl Manifest auto-gen (B5 해소)

**현재**: DeveloperPL이 commit append 후 git diff 직접 읽고 §8.5 표를 타이핑. 수동 매핑 + sub-issue title 작성.

**변경**: DocsAgent에 신규 helper 추가 — `mode: blocking, kind: impl-manifest, args: {commit_range, change_plan_path}`. DocsAgent가 `git diff --name-status <range>` + Change Plan §5 변경 계획 cross-ref → §8.5 표 자동 생성 (path/agent_role/related_change_plan_section). DeveloperPL은 review·승인만 (line-edit).

**보조**: Add/Modify/Delete 레이블 자동 (A/M/D), agent_role inferer (`tests/**`→QADev, `src/**`→DeveloperAgent role:dev, `docs/**`→DocsAgent, etc.).

**파일**: [agents/DocsAgent.md](../../agents/DocsAgent.md) §9 Impl Manifest helper, [agents/DeveloperPLAgent.md](../../agents/DeveloperPLAgent.md) (수동 작성 deprecated).

### 2.6 R6 — Lane Context Packet warm cache (B6 해소)

**현재**: Orchestrator가 매 spawn마다 Story file을 Read → 필요 섹션 추출 → packet 재구성. 같은 Story 내 여러 lane 진입 시 중복.

**변경**: Orchestrator session-local cache (`.claude-work/cache/<KEY>.json`)에 섹션별 hash 저장. spawn 시 packet 조립을 cache hit → 변경 없으면 reuse. Story file 변경(commit hash) 시 invalidate. 하나의 Story 내 평균 6 lane × 4 spawn = 24회 spawn에서 14-18회 cache hit 기대.

**파일**: [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §12 Context Packet 갱신.

### 2.7 R7 — Phase 1 merge ↔ Phase 2 prep parallel (B7 해소)

**현재**: 설계 리뷰 PASS → Phase 1 PR mergeable → merge → 그 다음 Phase 2 PR open + 첫 commit 준비.

**변경**: 설계 리뷰 PASS 즉시 Orchestrator가 두 작업 병렬 트리거.
- Track A: DocsAgent가 `gate:design-review-pass` 라벨 부착 + Phase 1 PR merge
- Track B: DeveloperPL spawn → Change Plan §5·§8 fetch → 첫 commit draft 준비 (PR open은 main merge 완료 후)

Track B는 Track A 완료 시점에 PR open 준비 완료 → 즉시 `mcp__github__create_pull_request`. 평균 3-5분 단축.

**파일**: [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §스폰 시퀀스 §[설계 리뷰] 분기.

### 2.8 R8 — ArchitectPL fail-fast pre-synthesis check (B8 해소)

**현재**: ArchitectPL이 deputy 4-5인 산출물을 모두 수령 → 통합 검수 → 메타-규칙 1·2 위반 발견 시 chief author retry.

**변경**: ArchitectPL이 deputy 산출물 수령 즉시 빠른 sanity check (각 deputy의 §섹션 author input 표면 형식 검증 + Story §1 cross-ref 존재 여부) → 결격 detected 시 즉시 해당 deputy clarification 재spawn. 통합 단계 도달 전 cycle 단축.

**파일**: [agents/ArchitectPLAgent.md](../../agents/ArchitectPLAgent.md) §메타-규칙 (pre-synthesis fast path 추가).

### 2.9 R9 — TestAgent 기능∥성능 병렬 (B9 해소, Tier 2)

**현재**: TestAgent 기능 모드 ALL PASS → 성능 모드 spawn → ALL PASS → 보안 lane 진입.

**변경**: TestAgent를 `subset` 인자로 분리 spawn 가능하게 변경. Orchestrator가 두 subset 동시 spawn (`subset: functional` / `subset: performance`). 두 subset 모두 PASS 시 보안 lane 진입. 한쪽 FAIL 시 즉시 FIX 루프 (다른 한쪽도 fail-safe 보존).

**제약**: 성능 baseline 측정이 기능 테스트 부산물 사용 시 의존성 확인 필요 (consumer overlay에서 정의). 의존 시 sequential fallback.

**파일**: [agents/TestAgent.md](../../agents/TestAgent.md) (subset arg), [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §스폰 시퀀스 §[구현 테스트].

### 2.10 R10 — SecurityTestPL 1차 layer pre-fetch (B10 해소, Tier 2)

**현재**: 구현 테스트 PASS → SecurityTestPL spawn → PL이 1차 layer (`gh api repos/*` Dependabot/CodeQL/Secret Scanning) fetch → packet 작성 → 2차 layer 워커 spawn.

**변경**: 구현 lane Phase 2 PR open 직후 Orchestrator가 background DocsAgent에 1차 layer fetch 의뢰 (`mode: background, kind: security-prefetch`) → JSON dump를 `.claude-work/cache/<KEY>-sec1.json`에 저장. SecurityTestPL spawn 시 packet에 cache 첨부 → fetch 단계 skip. 평균 1-2분 단축.

**파일**: [agents/SecurityTestPLAgent.md](../../agents/SecurityTestPLAgent.md), [agents/DocsAgent.md](../../agents/DocsAgent.md) §Bash 권한 (security prefetch helper).

### 2.11 R11 — FIX mechanical fast-path (B11 해소, Tier 2)

**현재**: 모든 review FIX는 동일 cycle (DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → 재구현). typo / broken link / minor naming 같은 명확 mechanical fix도 풀 cycle.

**변경**: ReviewPL severity verdict packet에 `category` 필드 추가. category가 `typo | broken-link | minor-naming | comment-only` 중 하나이고 severity가 P2이거나 single-file P1인 경우 → Orchestrator가 fast-path 적용:
- DeveloperPL이 직접 fix commit 후 ArchitectPL 판정 skip
- 재리뷰는 same-iteration internal verify (다음 Iter row 안 매김)

**제약**: P0 또는 multi-file P1는 fast-path 자격 없음. 분류 잘못이면 다음 Iter row append (정상 cycle 회복).

**파일**: [templates/review-pl-base.md](../../templates/review-pl-base.md) §3, [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) §FIX state machine, [agents/DeveloperPLAgent.md](../../agents/DeveloperPLAgent.md).

## 3. 비결정 (Tier 3 deferred)

다음 항목은 **본 CFP 범위 외**, ADR-007 별도 발의:
- §section ownership model (deputy를 §section author로, chief author를 cross-ref integrator로) — N=5 deputy 안정화 필요
- 2-PR draft pipeline (Phase 1 design 진행 중 Phase 2 PR draft pre-create) — invariant guard 부담

## 4. 영향 범위

### 4.1 BREAKING / Non-BREAKING
- **Non-BREAKING (전체)**: ADR 변경 없음. consumer가 SessionStart hook으로 자동 적용. R5 §8.5 helper만 신규 가용 (수동 작성 fallback 유지).

### 4.2 변경 파일 (예상)
- [CLAUDE.md](../../../CLAUDE.md) — 스폰 시퀀스 다이어그램 (R3·R7·R9 반영)
- [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) — §11 (R1) §12 (R6) §스폰 시퀀스 (R3·R7·R9·R10) §FIX state machine (R4·R11)
- [templates/review-pl-base.md](../../templates/review-pl-base.md) — verdict-first protocol (R2·R11)
- [agents/DocsAgent.md](../../agents/DocsAgent.md) — dual-mode queue (R1) + impl-manifest helper (R5) + security-prefetch helper (R10)
- [agents/DesignReviewPLAgent.md](../../agents/DesignReviewPLAgent.md) — Orchestrator-direct spawn (R3) + verdict-first (R2)
- [agents/CodeReviewPLAgent.md](../../agents/CodeReviewPLAgent.md) — same as above
- [agents/SecurityTestPLAgent.md](../../agents/SecurityTestPLAgent.md) — same + R10 cache 첨부
- [agents/ArchitectPLAgent.md](../../agents/ArchitectPLAgent.md) — fail-fast pre-synthesis (R8) + parallel diagnosis (R4)
- [agents/DeveloperPLAgent.md](../../agents/DeveloperPLAgent.md) — parallel diagnosis (R4) + manifest review (R5) + fast-path (R11)
- [agents/TestAgent.md](../../agents/TestAgent.md) — subset arg (R9)

총 11개 파일. ADR 변경 0건 (Non-BREAKING).

### 4.3 invariant-check 영향
- Step 6 3 lane category enum parity — ReviewPL packet schema 변경 시 (`category` 필드 추가) 영향. `templates/review-checklists/*.md`의 category enum에 mechanical fast-path 자격 카테고리 추가 가능 검토.
- Step 8 severity overrides count parity — 영향 없음 (severity 룰 추가 없음).
- 워크플로우 parity (CFP-13) — 영향 없음 (워크플로우 파일 변경 없음).

## 5. Test Contract (§8 후보)

R1-R11 각각 검증 가능 단위:

| R | 검증 방법 | 측정 지표 |
|---|----------|----------|
| R1 | Mock Story 1건 실행, blocking/background drain log 분석 | drain 직렬 시간 측정 |
| R2 | ReviewPL verdict-return → 다음 lane spawn 사이 시간 측정 | <5초 expected |
| R3 | Orchestrator-direct dual spawn unit (실제 PL이 spawn 시도 시 platform error) | platform error fail-fast |
| R4 | parallel diagnosis 일치률 (5건 mock fix evidence) | 일치 4건+ expected |
| R5 | DocsAgent helper unit (3 mock commit range) | git diff parse 정합 100% |
| R6 | cache hit rate 측정 (1 Story spawn log 분석) | hit rate 60%+ expected |
| R7 | Track A·B parallel start log 검증 | gap <30초 |
| R8 | deputy 산출물 결격 case 3건 mock → fast-fail trigger 검증 | trigger 100% |
| R9 | functional+performance subset parallel run, 결과 정합 | 결과 차이 0건 |
| R10 | security-prefetch cache hit case 검증 | cache hit 시 fetch skip |
| R11 | mechanical fix classification 정확률 (10 mock review verdict) | 정확률 90%+ expected |

각 R마다 unit/integration test 1-2건. QADev이 §8 Test Contract 작성 시 TestContractArchitectAgent input.

## 6. 보안 영향 (§7 후보)

**Trust boundary**: 변화 없음. 모든 외부 호출은 기존 boundary 유지 (gh CLI, MCP github, codex CLI).

**Threat model (STRIDE-LITE)**:
- Spoofing: cache hash 없음, R6 cache invalidation을 commit hash로 → tamper 시 hash 불일치 → cache miss
- Tampering: `.claude-work/cache/**` 파일이 외부 노출 안 됨, gitignore 추가 권장
- Information disclosure: security-prefetch cache (R10)에 Dependabot CVE 정보 포함 가능 → `.claude-work/cache/` 전체 gitignore 의무

**민감 데이터**: 없음 (gitignore 추가만)

**Auth/Authz**: 변화 없음

**위협↔완화**:
- T1 cache poisoning → commit hash invalidation
- T2 cache leak → `.claude-work/cache/` gitignore (R6·R10 동시)

## 7. ADR 영향

신규 ADR 없음. ADR-001/004/006 모두 변경 없음 (deputy 모델·리뷰 unification·§8 author input 그대로).

## 8. 후속 (deferred)

- ADR-007 §section ownership model — N=5 deputy 안정화 후 별도 brainstorming
- CFP-20 (DesignReview checklist 확장) — PMO 권고, 본 CFP 후 처리
- CFP-21 (DataMigrationArchitectAgent) — Codex 감사 #2, deputy N=6 안정화 후

## 9. 참고

- Codex 감사 결과 (P-1..P-8): `/private/tmp/claude-1021874023/.../tasks/a4e94bd8ebe141221.output`
- general-purpose self-audit (a..k): 본 세션 conversation
- 기준 측정: CFP-17 (60-90분), CFP-18 (75-90분, chief author timeout 1회 포함)
