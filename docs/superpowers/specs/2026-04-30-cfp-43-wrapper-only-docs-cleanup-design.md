---
spec_id: cfp-43
title: Wrapper-only docs cleanup + cross-repo backfill — DocsAgent ghost text 제거 + 6 lane plugin operational gap 해소
status: Draft
date: 2026-04-30
authors:
  - User (Codex 분석 후속 — Category A/B P0 잔여 cleanup 의뢰. Y2 권장안 (P0+P1) 채택)
  - Claude (Opus 4.7) — synthesis · design author · 21-gap audit
related_adrs:
  - ADR-009 (Wrapper-only Decomposition — ζ arc 결과. 본 CFP 가 추격하는 정합성 잔재)
  - ADR-010 (Inter-plugin Contract Sibling Sync — CFP-42 결과. 본 CFP 와 무관, but 같은 cleanup arc)
related_files:
  - CLAUDE.md (UPDATE — DocsAgent 참조 제거 + "문서 write 책임 분담" 재구성 + "19 core" → "0 core")
  - docs/orchestrator-playbook.md (UPDATE — DocsAgent.md 의존 제거 + §5 "DocsAgent 스폰 체크리스트" → "lane plugin self-write 체크리스트" 재구성 + §11 file-based write queue 절 cleanup)
  - templates/story-page-structure.md (UPDATE — DocsAgent 책임 칸 제거 + lane plugin 별 self-write 매핑)
  - templates/impl-manifest.md (UPDATE — DocsAgent §8.5 기록 책임 → DeveloperPL self-write)
  - README.md (UPDATE — Cross-cutting listing 에서 DocsAgent 제거)
  - docs/plugin-design.md (UPDATE — "19 core" → "0 core wrapper-only" + agent listing 갱신)
  - docs/consumer-guide.md (UPDATE — DocsAgent commit 책임자 표시 → lane plugin self-write)
  - docs/migration-guide.md (UPDATE — DocsAgent 권한 override 가이드 → 각 lane plugin 권한 가이드)
related_external_repos:
  - mclayer/plugin-codeforge-review (PR-1 — `templates/review-pl-base.md` §4·§7·§11)
  - mclayer/plugin-codeforge-pmo (PR-2 — `agents/PMOAgent.md` §1·§2·§4)
  - mclayer/plugin-codeforge-requirements (PR-3 — 4 agent md footer + §9.0 책임)
  - mclayer/plugin-codeforge-test (PR-4 — TestAgent.md footer + §9.3 ownership)
  - mclayer/plugin-codeforge-develop (PR-5 — DeveloperPLAgent.md §8.5 + footer)
  - mclayer/plugin-codeforge-design (PR-6 — ArchitectAgent.md step 5 + footer + cache invalidation)
---

## 0. 사용자 원문 (verbatim)

라운드별 핵심 발화 6건:

> 1. (CFP-42 후 후속 의뢰) "다음 할 일이 있나?" — 후속 candidates 검토 트리거
> 2. (CFP-A 채택) "그럼 이어서 해야한다." — 후속 docs cleanup CFP 진행 결정
> 3. (scope 결정) "1" — 단일 CFP-43 (전 8 file 일괄)
> 4. (작업 성격 확인) "지금 너가 수행할 내용이 DocsAgent 관련 내용을 각 plugin의 repo로 옮기는 작업이지?" — 작업 의도 명확화
> 5. (B 옵션 선택) "B로 해야지" — wrapper cleanup 만이 아니라 lane plugin 측 backfill 까지 포함하는 cross-repo 옵션
> 6. (Y2 채택) "Y2" — P0+P1 backfill (P2 제외)

추가 정렬:
- 사용자 발화 #4 가 핵심 분기점 — "이미 옮겨진 wrapper text 정리만" (option A) vs "lane plugin 측 누락 가능성 검증·backfill" (option B). 사용자가 후자를 선택해 작업 안전성 확보.
- 21-gap audit 으로 실제 누락 규모 정량화 (6 P0 / 12 P1 / 3 P2). P2 는 wrapper Orchestrator 행위라 backfill 불필요 — Y3 옵션은 노이즈로 제외.

## 1. 컨텍스트

### 1.1 ζ arc 잔재의 두 표면

ADR-009 가 정의한 wrapper-only end-state 는 두 표면 모두에서 정합되어야 한다:
- **wrapper repo**: agent file 0개. CLAUDE.md / orchestrator-playbook / templates 가 wrapper-only 모델만 묘사
- **6 lane plugin repo**: 각자 자기 lane self-write 책임을 명확히 보유. agent md 에 "DocsAgent 경유" 같은 stale path 부재

CFP-29~CFP-40 추출 시점에 두 표면 모두 일부 갱신됐지만, ζ arc 종료 후 ([CFP-41 retro](../../retros/2026-04-29-zeta-arc-completion.md)) 에 stale 잔재가 다음 두 분류로 남음:

**Category A** (wrapper text 잔재):
- [CLAUDE.md](../../../CLAUDE.md): "agents/`<Name>`.md SSOT" (line 3) + "DocsAgent 경유" 인용 ~20건 + "DocsAgent + 3 owner agent 분담 모델" 절 (line 460-471)
- [docs/orchestrator-playbook.md](../../orchestrator-playbook.md): DocsAgent 참조 ~40건 + §5 "DocsAgent 스폰 체크리스트" 표 + §11 file-based write queue 절 (lines 809-866)
- [templates/{story-page-structure, impl-manifest}.md](../../../templates/): "DocsAgent 단독" + "DocsAgent 액션" 표
- [README.md](../../../README.md): Cross-cutting listing
- [docs/{plugin-design, consumer-guide, migration-guide}.md](../../): "19 core 에이전트" + DocsAgent commit 책임자 표시

**Category B** (lane plugin 측 operational gap):
21-gap audit (본 brainstorming 단계 산출) 가 식별:
- 6 P0 — operational logic 결함 (e.g., codeforge-review `review-pl-base.md §4` 가 deprecated `ledger-append` queue type 사용 → CFP-32 deny rule 에 silent skip)
- 12 P1 — 거의 모든 lane plugin agent md 의 "문서화 표준" footer 가 pre-ζ-arc copy-paste ("모든 문서화는 Orchestrator 경유 DocsAgent 가 기록") — self-write 표 (CLAUDE.md) 와 모순
- 3 P2 — Orchestrator 행위 (background security prefetch 등), backfill 불필요

### 1.2 Codex 분석과의 관계

Codex 1차 분석 (CFP-42 직전) 이 Category A/B 양쪽을 식별했지만 일률적으로 "wrapper cleanup" 으로 분류. 사용자 발화 #4 가 "lane plugin 측 누락 가능성" 을 짚어 Category B 의 정확한 처리 방향 (cross-repo backfill) 을 결정. 본 CFP 는 사용자 가설 검증 후 audit 으로 정량화한 결과를 기반.

### 1.3 21-gap audit 결과 요약

| Severity | Count | 처리 |
|---|---|---|
| P0 | 6 | backfill 의무 (operational bug) |
| P1 | 12 | backfill 권장 (Y2) — 동질적 stale text |
| P2 | 3 | backfill 불필요 (Orchestrator 행위) |

P0 분포:
- codeforge-review (1): `review-pl-base.md §4` ledger-append queue → CFP-32 deny
- codeforge-pmo (1): `PMOAgent.md §4` deprecated `adr-draft` queue type
- codeforge-develop (2): `DeveloperPLAgent.md` §"구현 완료 흐름" + kind:impl-manifest R5 ambiguity
- codeforge-design (2): `ArchitectAgent.md` step 5 + footer (Story §7/§3/§11 self-write 모순)

## 2. 결정 사항

### 2.1 D1. Cleanup 깊이 = X2 (Simplify + Replace)

wrapper repo 의 cleanup 은 **find/replace + DocsAgent-shaped 구조 simplify** 까지. 이유:
- 단순 find/replace 만 (X1) 은 §5 "DocsAgent 스폰 체크리스트" 표·"분담 모델" 절 등 DocsAgent 가 fixture 였던 시대에만 의미 있던 구조 잔존 → DocsAgent 없는 모델에서 어색
- 전면 rewrite (X3) 는 Development Agent Team 트리·lane 흐름도 등 wrapper-only 정합 이미 보유한 영역까지 건드림 → review·검증 부담 큼
- X2 는 균형: 텍스트 대체 + structurally-DocsAgent 섹션을 "lane plugin self-write boundary" 모델로 재구성, 그 외 매크로 구조 보존

대안 X1·X3 반려 (사용자 X2 선택, round 3 후 명시).

### 2.2 D2. Backfill 깊이 = Y2 (P0 + P1)

cross-repo backfill 은 **P0 운영 결함 + P1 동질적 stale text 까지**. 이유:
- P0 만 (Y1) 은 6 fix 단위로 충분하지만 P1 의 "문서화 표준 footer" stale 이 거의 모든 plugin agent md 에 동일 패턴으로 존재 — 별도 CFP 미루기 비효율
- P0+P1 (Y2) 는 18 fix 단위. 동질적 footer cleanup 이 5 PR 모두에 자연스럽게 분산 → 추가 PR 비용 0
- P2 (Y3) 는 backfill 대상 아님 (Orchestrator 행위)

대안 Y1·Y3 반려 (사용자 Y2 선택, round 6).

### 2.3 D3. PR 분할 = 7 PR (6 cross-repo + 1 wrapper)

각 lane plugin 은 자기 repo 단위로 1 PR. wrapper 는 마지막 1 PR. 이유:
- cross-repo 는 PR 단위 분할 강제 (1 PR 이 2 repo 를 동시에 touch 불가)
- 6 lane plugin × 1 fix-bundle PR = 6 PR (각자 독립 머지 가능)
- wrapper 는 모든 lane plugin 변경 완료 후 reference 가 정합한 상태에서 cleanup → 7번째 PR

각 lane plugin PR 의 scope 는 §3.1 의 표 참조.

### 2.4 D4. Ordering = cross-repo 우선 → wrapper 후속

PR-1~PR-6 (cross-repo) 머지 → PR-7 (wrapper) 머지 순. 이유:
- P0 들이 operational bug. 머지 빠를수록 안전
- wrapper PR-7 가 lane plugin self-write 표를 reference 하므로 lane plugin 정합 후 wrapper 갱신
- PR-1~PR-6 끼리는 의존 없음 — 사용자가 병렬 머지 가능

### 2.5 D5. Verification = file-level lint + grep test

각 PR 머지 후 자기 repo 의 lint chain PASS + 신규 grep test:
- wrapper PR-7 후: `grep -rn "DocsAgent" CLAUDE.md docs/ templates/ README.md --exclude-dir=superpowers --exclude-dir=.git` 출력 0 (history reference 제외)
- lane plugin PR-1~PR-6 후: 자기 plugin 의 agent md 에 "DocsAgent" 또는 deprecated queue type (`adr-draft`, `change-plan`, `ledger-append`) 0건

P2 (wrapper Orchestrator 행위) 는 wrapper docs 자체에 명시적 owner 표시 — backfill 안 함.

## 3. 산출물

### 3.1 7 PR 매트릭스

| PR | Repo | Branch (예상) | File targets | Gap items |
|---|---|---|---|---|
| PR-1 | mclayer/plugin-codeforge-review | `cfp-43-pl-base-cleanup` | `templates/review-pl-base.md` §4·§7·§11 | P0×1 (§4 ledger-append) + P1×2 (§7/§11 stale "DocsAgent SSOT") |
| PR-2 | mclayer/plugin-codeforge-pmo | `cfp-43-pmo-self-write-cleanup` | `agents/PMOAgent.md` §1·§2·§4 | P0×1 (§4 adr-draft queue) + P1×2 (§2 self-contradiction + §1 W14 Epic milestone) |
| PR-3 | mclayer/plugin-codeforge-requirements | `cfp-43-req-footer-cleanup` | `agents/{RequirementsPL,Domain,RequirementsAnalyst,Researcher}Agent.md` 4 file footer + RequirementsPL §9.0 책임 | P1×3 (footer × 4 + §9.0 + cross-repo schema reference) |
| PR-4 | mclayer/plugin-codeforge-test | `cfp-43-test-footer-cleanup` | `agents/TestAgent.md` footer + §9.3 ownership | P1×2 (footer + §9.3 write boundary) |
| PR-5 | mclayer/plugin-codeforge-develop | `cfp-43-dev-section-self-write` | `agents/DeveloperPLAgent.md` §"구현 완료 흐름" + impl-manifest R5 + footer | P0×2 (§8.5 + R5 ambiguity) + P1×1 (footer) |
| PR-6 | mclayer/plugin-codeforge-design | `cfp-43-arch-section-self-write` | `agents/ArchitectAgent.md` step 5 + footer + PMO ADR draft hand-off + cache invalidation | P0×2 (§7/§3/§11 self-write) + P1×2 (PMO hand-off + cache invalidation) |
| PR-7 | mclayer/plugin-codeforge **(wrapper)** | `cfp-43-wrapper-cleanup` | 8 wrapper files (§3.2 표) | wrapper Category A 일괄 (X2 depth) |

**Total**: 6 P0 + 12 P1 = 18 gap fixes. P2 3건 처리 안 함.

### 3.2 PR-7 wrapper 변경 file 표

| File | 변경 |
|---|---|
| [CLAUDE.md](../../../CLAUDE.md) | line 3 "agents/<Name>.md SSOT" 갱신 (lane plugin 별 SSOT pointer) + "DocsAgent" 인용 ~20건 제거/대체 + line 460-471 "DocsAgent + 3 owner agent 분담 모델" 절 → "Lane plugin self-write boundary" 절 재구성 + line 84·125 Cross-cutting listing 에서 DocsAgent 제거 |
| [docs/orchestrator-playbook.md](../../orchestrator-playbook.md) | DocsAgent 인용 ~40건 제거/대체 + line 15 agents/DocsAgent.md 의존 제거 + §5 "DocsAgent 스폰 체크리스트" 표 → "lane plugin self-write 체크리스트" 표로 재구성 + §11 file-based write queue 절 → "Orchestrator 직접 path" 절로 단순화 (deprecated queue types 명시) |
| [templates/story-page-structure.md](../../../templates/story-page-structure.md) | "DocsAgent 액션" column → "Owner agent" column 으로 변경 (각 row 의 owner 가 self-write) + "DocsAgent 독점" 표현 제거 |
| [templates/impl-manifest.md](../../../templates/impl-manifest.md) | DeveloperPL self-write §8.5 명시 (DocsAgent 의뢰 path 제거) + Action 자동 sub-issue 부분만 보존 |
| [README.md](../../../README.md) | line 15 "단독 문서 writer (DocsAgent)" → "각 lane plugin self-write" + line 23 "[Cross-cutting] PMOAgent, DocsAgent" → "[Cross-cutting] PMOAgent" |
| [docs/plugin-design.md](../../plugin-design.md) | "19 core 에이전트" → "0 core wrapper-only + 6 lane plugin (codeforge-{review,pmo,requirements,test,develop,design})" + agent listing 분포 표 갱신 |
| [docs/consumer-guide.md](../../consumer-guide.md) | docs/{adr,change-plans,domain-knowledge}/ 옆 "DocsAgent commit" → "각 owner agent self-write (lane plugin)" + Phase-gate-mergeable troubleshooting 의 "DocsAgent 라벨 부착" → "lane plugin self-write" |
| [docs/migration-guide.md](../../migration-guide.md) | "DocsAgent 권한 override" 가이드 → "각 lane plugin 권한" 가이드. line 110 "codeforge core (DocsAgent): verdict 받아 ..." → "각 lane plugin self-write" |

## 4. 의존 + Ordering

PR-1~PR-6 (cross-repo) 우선 머지 → PR-7 (wrapper) 마지막. PR-1~PR-6 끼리 병렬 머지 가능.

**근거**:
- PR-1·PR-2·PR-5·PR-6 의 P0 fix 들이 lane plugin 의 잘못된 path (deprecated queue type usage 등) 차단 → 빠를수록 안전
- PR-7 의 "DocsAgent 제거" 는 lane plugin self-write 표를 reference 하는 형태 — lane plugin 측 정합 후 wrapper 갱신해야 cross-link 가 정합

**예외**: PR-3·PR-4 는 P1 만 (footer cleanup 위주). PR-7 와의 의존 무관 — 시점 자유.

## 5. Test contract

### 5.1 기능 테스트 (PR 별)

| PR | Test |
|---|---|
| PR-1 | `mclayer/plugin-codeforge-review` repo 의 lint chain (자기 repo 의 `scripts/check-*.sh`) PASS + `grep -c "ledger-append" templates/review-pl-base.md` = 0 |
| PR-2 | `mclayer/plugin-codeforge-pmo` lint PASS + `grep -c "adr-draft" agents/PMOAgent.md` = 0 |
| PR-3 | `mclayer/plugin-codeforge-requirements` lint PASS + 4 agent md 의 "DocsAgent" footer line 부재 |
| PR-4 | `mclayer/plugin-codeforge-test` lint PASS + TestAgent.md footer "DocsAgent" 부재 |
| PR-5 | `mclayer/plugin-codeforge-develop` lint PASS + DeveloperPLAgent.md "DocsAgent 경유" 부재 |
| PR-6 | `mclayer/plugin-codeforge-design` lint PASS + ArchitectAgent.md "DocsAgent 의뢰" 부재 |
| PR-7 | wrapper lint chain (frontmatter + section-schema + inter-plugin-contracts + test-harness + check-doc-links) PASS + grep test |

### 5.2 wrapper grep test

```bash
# Negative — DocsAgent 잔재 0 in non-history sections
test "$(grep -rn 'DocsAgent' CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | grep -v 'history\|legacy' \
  | wc -l)" = "0"

# Negative — "19 core" 주장 0
test "$(grep -rn '19 core' CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | wc -l)" = "0"

# Positive — "0 core" 또는 "wrapper-only" 명시 존재
test "$(grep -rn 'wrapper-only\|0 core' CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | wc -l)" -gt "0"
```

수동 spot-check (PR-7 reviewer):
- CLAUDE.md "Lane plugin self-write boundary" 절이 6 lane plugin 별 owner path 명시
- orchestrator-playbook §5 표가 lane plugin self-write 흐름으로 일관되게 재구성됨
- README.md 의 Cross-cutting listing 에 DocsAgent 부재

### 5.3 성능 테스트

N/A — 순수 docs 변경. baseline 무관.

### 5.4 통합 테스트

PR-1~PR-7 머지 후, wrapper 의 `docs/orchestrator-playbook.md` 의 cross-repo 인용 (예: "lane plugin self-write 책임은 각 plugin CLAUDE.md 참조") 이 실제 lane plugin 의 갱신된 self-write 표를 정확히 가리키는지 spot-check.

## 6. Phase 1 / Phase 2 PR split (per PR)

**중요**: 본 CFP-43 은 codeforge dogfooded workflow 와 다소 다르게 처리됨 — **7 PR 각자 단일 PR** (Phase 1+2 분리 안 함). 이유:
- 각 PR 이 작은 fix 단위 (footer 갱신·deprecated queue 제거·1 섹션 재구성)
- 7-lane workflow 의 Phase 1 (요구사항·설계·설계리뷰) + Phase 2 (구현·구현리뷰·구현테스트·보안테스트) 가 docs cleanup 에는 과도
- CFP-42 와 동일 패턴 — wrapper 자체 dogfooding meta-CFP 는 admin merge 로 처리 가능

각 PR body 에 다음 명시:
- 본 CFP-43 spec link
- gap audit 결과의 해당 plugin section
- before/after diff 의 핵심 1-2 line

## 7. Out of scope

| 항목 | 분리 사유 | 후속 CFP |
|---|---|---|
| review-verdict-v1 archive | retro:75 후속 (Codex CFP-D) | 별도 CFP |
| canonical↔sibling drift detection | CFP-42 §10 deferred (A3 영역) | 별도 CFP |
| migration-guide v0.22→v5 BREAKING parity | retro:77 follow-up (Codex CFP-E) | 별도 CFP. 본 CFP 의 PR-7 은 DocsAgent 인용 cleanup 만 — breaking parity 자체는 별도 |
| 새 lane plugin 추가·기능 변경 | scope 무관 | 별도 CFP |
| P2 backfill (3 항목 — Orchestrator 행위) | wrapper docs 에 owner 명시만으로 충분 | N/A |

## 8. Open questions / risks

### 8.1 Question — PR ordering 강제 메커니즘

**Q**: PR-1~PR-6 머지 전 PR-7 (wrapper cleanup) 가 머지되는 것을 어떻게 방지?

**현재 결정**: 작업 sequence 로 통제. PR-1~PR-6 머지 완료 후 PR-7 open. 자동 강제 메커니즘 (예: GitHub Action) 도입 안 함 (overhead).

**Open**: 사용자가 momentum 우선해 PR-7 먼저 작업하고 PR-1~PR-6 동시 진행 가능. 그 경우 PR-7 의 wrapper docs 가 "lane plugin self-write 표 reference" 형태이므로 lane plugin 측 갱신 전 머지되면 일시적 broken reference. 단 모든 PR 머지 후 정합 회복.

### 8.2 Risk — cross-repo PR 의 dogfooded workflow 정합

**Risk**: 6 lane plugin 의 자체 dogfooded workflow (Issue Form + story-init.yml 등) 가 본 cleanup PR 들에 적용되어야 하는지 불명확.

**Mitigation**: 각 plugin repo 의 정책 follow. 자체 dogfooded workflow 미존재 시 직접 PR + admin merge. 존재 시 Issue Form 제출 후 진행. 본 CFP-43 spec 은 wrapper meta-CFP 이므로 lane plugin 측 process 를 강제하지 않음.

### 8.3 Risk — DocsAgent 참조 false positive

**Risk**: §5.2 grep test 가 history mention 까지 잡아 false fail.

**Mitigation**: `--exclude-dir=superpowers` (specs/plans 의 history 영역 제외) + `grep -v 'history\|legacy'` (본문 내 history block 제외). docs/superpowers/specs/2026-04-29-cfp-31-... 같은 spec history 는 보존 — 본 CFP scope 밖.

### 8.4 Risk — agent md 갱신과 lane plugin CLAUDE.md self-write 표 자체 contradict 잔재

**Risk**: 21-gap audit 이 모든 모순을 잡았다는 보장 없음. 추가 발견 시 별도 follow-up CFP 필요.

**Mitigation**: PR review 시 (특히 PR-1·2·5·6) reviewer 가 자기 plugin 의 CLAUDE.md self-write 표와 갱신된 agent md 를 스폿-비교. follow-up gap 발견 시 본 CFP 의 §10 FIX Ledger 에 추가 또는 별도 CFP open.

## 9. 참조

### 9.1 ADR

- [ADR-009 Wrapper-only Decomposition](../../adr/ADR-009-wrapper-only-decomposition.md) — ζ arc 결과. 본 CFP 가 추격하는 정합성 잔재의 출처
- [ADR-010 Inter-plugin Contract Sibling Sync](../../adr/ADR-010-inter-plugin-contract-sibling-sync.md) — CFP-42 결과. 같은 cleanup arc

### 9.2 관련 CFP

- [CFP-31 ζ arc parent design](2026-04-29-cfp-31-wrapper-only-decomposition-design.md) — 본 CFP 가 backfill 하는 ζ arc 의 parent
- [CFP-42 sibling backfill](2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md) — 직전 cleanup 단계. 본 CFP 와 같은 자세
- CFP-29 (codeforge-review extraction) — review-pl-base.md 의 출처
- CFP-36~CFP-40 — 각 lane plugin 추출 (5 plugin)
- CFP-41 ζ arc retro — Migration-guide BREAKING parity follow-up 명시

### 9.3 Audit 산출물

본 spec 작성 직전 dispatched audit subagent 산출:
- 21 gap items (W1-W16 wrapper inventory + per-plugin gap analysis)
- 6 P0 / 12 P1 / 3 P2 categorization
- "stale 문서화 표준 footer" 가 거의 모든 lane plugin agent md 의 공통 P1 패턴

### 9.4 Wrapper 측 gap inventory (W1-W16) 인용 source

위치 source:
- W1·W6·W12·W13: `docs/orchestrator-playbook.md` §5 + DocsAgent agent description
- W2·W3·W5·W11: `docs/orchestrator-playbook.md` §11 + §12
- W4: `docs/inter-plugin-contracts/fix-event-v1.md` (CFP-32 monopoly)
- W7: `docs/orchestrator-playbook.md` §3-§4 lane PASS gate
- W8: `docs/orchestrator-playbook.md` §4.2 Clarification respawn
- W9·W10: `docs/orchestrator-playbook.md` §5.1 + §11 prefetch
- W14: `agents/PMOAgent.md` (Pre-CFP-36 — 본 audit 시점 plugin repo 의 stale)
- W15: `templates/story-page-structure.md` §11
- W16: `docs/orchestrator-playbook.md` §10 hotfix audit

각 P0/P1 fix 의 정확한 line 위치는 implementation plan 단계에서 task-level 로 구체화.
