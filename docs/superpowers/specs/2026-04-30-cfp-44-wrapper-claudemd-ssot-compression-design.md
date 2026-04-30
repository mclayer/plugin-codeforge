---
spec_id: cfp-44
title: Wrapper CLAUDE.md SSOT Compression — post-CFP-43 follow-up + ADR-012 boundary
status: Draft
date: 2026-04-30
authors:
  - User (CFP-43 후 잔존 부속 진단 의뢰 + Q1 옵션 (B) + Q2 옵션 (A) + Codex 권고 채택)
  - Claude (Opus 4.7) — synthesis · audit dispatch · design author
  - Codex (gpt-5.4) — second opinion (A1 정당화 + boundary statement 보강 권고)
related_adrs:
  - ADR-009 (Wrapper-only Decomposition — ζ arc parent)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sibling cleanup arc)
  - ADR-012 (NEW — Wrapper CLAUDE.md SSOT Boundary; PR-4 에서 신설)
related_files:
  - CLAUDE.md (UPDATE — 705 → ~330줄. lane internal · 중복 · stale 잔재 압축. SSOT Boundary 절 신설)
  - docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md (NEW)
related_external_repos:
  - mclayer/plugin-codeforge-test (PR-1 — TestAgent CLAUDE.md gap MISSING 해소)
  - mclayer/plugin-codeforge-design (PR-2 — 4-way ideology body + ArchitectPL lifecycle + Deputy Freshness)
  - mclayer/plugin-codeforge-requirements (PR-3 — Clarification 재스폰 pattern + Domain Knowledge schema)
related_cfps:
  - CFP-31 (ζ arc parent design)
  - CFP-43 (X2 cleanup predecessor — DocsAgent ghost text 제거)
---

## 0. 사용자 원문 (verbatim)

라운드별 핵심 발화 4건:

> 1. "이 codeforge 플러그인에 대해 보자. 이 플러그인에서 분리를 수행했지만 그 부속 사항이 너무 많이 남아있는 것 같다. 그 결과 CLAUDE.md가 너무 길어진 것 같은데 상황을 확인해보고 평가해라." — 진단 트리거
> 2. "2" — 옵션 (2') 채택: SSOT 분업 재설계 (ADR 급 결정)
> 3. "b" — Q1 옵션 (B): Wrapper CLAUDE.md = composition + cross-cutting policy. Target ~250-300줄
> 4. "a" — Q2 옵션 (A): audit 먼저, lane plugin SSOT coverage 검증 후 압축
> 5. "뭐가 좋냐 codex한테 물어봐" → 6. "ㅇㅋ codex가 이야가한대로" — A1' 채택 (A1 + Codex boundary statement 보강)
> 7. "ㅇㅋ" — 본 design 승인

추가 정렬:
- 발화 #1 의 "분리를 수행했지만 부속 사항이 너무 많이 남아있는 것 같다" 는 CFP-43 X2 depth 가 충분치 않았다는 사용자 진단. CFP-43 §2.1 가 X3 (전면 rewrite) 를 "review·검증 부담 큼" 이유로 reject 했지만, 본 CFP-44 가 "audit-driven minimum" 형태로 X3 의 위험을 제어하며 재시도.
- 발화 #5-#6 은 Codex 두 번째 의견 받기. Codex 가 A1 정당화 + 보강안 (explicit boundary statement) 제시 → 채택.

## 1. 컨텍스트

### 1.1 CFP-43 후 잔재

CFP-43 (PR #83/#84 머지, 2026-04-30) 가 wrapper repo 의 DocsAgent ghost text 제거 + 6 lane plugin operational gap backfill 완료. 그러나 wrapper CLAUDE.md 는 여전히 705줄 / ~16k tokens. 사용자 진단:

> "분리를 수행했지만 부속 사항이 너무 많이 남아있는 것 같다."

증상 분류:
- **Stale (CFP-43 처리 완료)**: DocsAgent 인용 · "19 core" 잘못된 numbering · deprecated queue type 등
- **Surplus (CFP-44 대상)**: 분리된 lane plugin 의 internal detail (agent 역할 · spawn sequence · ideology · lifecycle 등) 이 wrapper 에 잔존. 의도된 SSOT 분업이 아니라 "ζ arc 추출 시 미처 옮기지 못한" 부속

### 1.2 SSOT 검증

본 brainstorming 단계에서 dispatched audit subagent 가 6 lane plugin CLAUDE.md 를 조사:

| Lane plugin | Status | Gap |
|---|---|---|
| codeforge-test | **MISSING** | functional/performance subset · 10% baseline · sequential fallback 전무 — 가장 critical |
| codeforge-design | PARTIAL critical | "4-way 이념 대립" 헤더만 있고 본문 미작성 + ArchitectPL stateless lifecycle 누락 + Deputy Freshness rule 누락 |
| codeforge-requirements | PARTIAL critical | Clarification 재스폰 패턴 · Domain Knowledge page schema 누락 |
| codeforge-review | PARTIAL safe | severity SSOT 정상 (templates/review-pl-base.md §3) — wrapper compression 무손실 |
| codeforge-pmo | PARTIAL safe | trigger taxonomy 함축적, agent md 영역 |
| codeforge-develop | PARTIAL safe | QADev role · Impl Manifest schema 는 agent md 영역 |

추가 발견 — **wrapper-must-keep 3 항목** (cross-lane disambiguation, single-plugin home 없음):
1. Design / Code / Security 책임 매트릭스 (cross-lane scope)
2. 원인 판정 decision table — codeforge-review CLAUDE.md 가 명시적으로 wrapper 를 SSOT 로 지정
3. FIX Ledger §10 schema + Orchestrator monopoly + RESET 룰 (CFP-32 monopoly · `fix-event-v1` contract)

### 1.3 Codex 두 번째 의견

Codex (gpt-5.4) 권고 요약:
- A1 (audit-driven minimum) 정당화 — A2 (symmetric refresh, 6 cross-repo PR) 는 "process symmetry 만 사고 risk reduction 은 못 사는 거래"
- A1 잠재 약점 = "lane plugin 별 self-contained 깊이 차이" *documentation-quality asymmetry* — architectural blocker 아님
- **보강안**: A1 wrapper PR 에 *explicit compression boundary statement* 를 박는다. PR 추가 없이 maintainability 우려 해소
- **최종 권고**: A1' (= A1 + boundary statement → ADR-012 신설)

## 2. 결정 사항

### 2.1 D1. Wrapper CLAUDE.md 역할 = composition + cross-cutting policy only

압축 후 wrapper CLAUDE.md 가 보유하는 카테고리:
1. **Plugin identity** — 1단 인트로, marketplace sync 의무, 세션 개시 dependency check
2. **Cross-cutting policy** — dogfood Story 작성 의무, write boundary table, inter-plugin contract index, ADR list
3. **3 SSOT 예외** — 책임 매트릭스 + 원인 판정 decision table + FIX Ledger schema/RESET (위 §1.2)

**제외**: per-lane spawn sequence detail, agent role description, lane-internal ideology/lifecycle/Freshness, severity rule detail, 병렬 스폰 권장 (spawn sequence 중복), GitHub workflow subsection 9개 (consumer-guide.md + label-registry-v1.md SSOT 로 위임)

목표 line count: 705 → **~330줄** (53% 절감, ~9k tokens 매 세션 절약). 320 buffer 까지 허용 (§8.1 bottom-up 분석 결과 — SSOT 예외 3개 합계 + cross-cutting policy KEEP 항목 합계 만으로 ~193줄 잔류 의무. 280줄 첫 추정은 cross-cutting policy 잔류량 underestimate).

### 2.2 D2. Approach = A1' (Codex 보강안)

3 대안 비교:

| Approach | PR 수 | 위험 | 효과 |
|---|---|---|---|
| A1 (audit-driven minimum) | 4 (3 cross-repo + 1 wrapper) | safe partial 의 미발견 gap | ~330줄 달성 |
| A2 (symmetric refresh, CFP-43 패턴) | 7 (6 cross-repo + 1 wrapper) | over-engineering | ~330줄 달성, PR 비용 2배 |
| A3 (wrapper-only quick-win) | 1 | 5 PARTIAL gap deferral | ~500줄 (target 미달) |
| **A1' (= A1 + boundary statement)** | 4 + ADR-012 | 동일 | 동일 + maintainability anchor |

A1' 채택 (사용자 + Codex 합의). A2·A3 reject.

### 2.3 D3. PR 분할 = 4 PR (3 cross-repo + 1 wrapper)

| PR | Repo | 처리 |
|---|---|---|
| **PR-1** | mclayer/plugin-codeforge-test | TestAgent CLAUDE.md 에 functional/performance subset · 10% baseline · sequential fallback · runner overlay 추가 |
| **PR-2** | mclayer/plugin-codeforge-design | CLAUDE.md 의 "4-way 이념 대립" body 채움 + ArchitectPL stateless lifecycle + Deputy Freshness rule |
| **PR-3** | mclayer/plugin-codeforge-requirements | Clarification 재스폰 패턴 + Domain Knowledge page schema reference |
| **PR-4** | mclayer/plugin-codeforge (wrapper) | CLAUDE.md 압축 (705 → ~330줄) + ADR-012 신설 + "SSOT Boundary" 절 신설 |

### 2.4 D4. Ordering = cross-repo 우선 → wrapper 후속

PR-1 / PR-2 / PR-3 머지 → PR-4 머지 순. PR-1~PR-3 간 의존 없음 (병렬 머지 가능).

근거 (CFP-43 precedent §2.4):
- PR-4 의 wrapper CLAUDE.md 가 "lane plugin self-write 표 / lane plugin CLAUDE.md 참조" 형태 — lane plugin 측 정합 후 wrapper reference 가 정확
- PR-1 (test MISSING) 은 wrapper 압축 후 정보 손실 직접 막는 PR — 가장 빠르게

### 2.5 D5. ADR-012 신설

ADR-012 = "Wrapper CLAUDE.md SSOT Boundary" (Adopted upon PR-4 merge).

**Decision**: Wrapper plugin CLAUDE.md 의 content scope 는 다음으로 strictly limited:
1. Plugin identity (composition · marketplace sync · dependency check)
2. Cross-cutting policy (dogfood Story 작성 의무 · write boundary table · inter-plugin contract index · ADR list)
3. 3 named SSOT exceptions (cross-lane scope, no single-plugin home):
   - Design / Code / Security 책임 매트릭스
   - 원인 판정 decision table
   - FIX Ledger §10 schema + Orchestrator monopoly + RESET 룰

**Excluded** (lane plugin SSOT 또는 playbook 으로 위임):
- per-lane spawn detail · agent role description
- lane-internal ideology · lifecycle · Freshness rule
- severity rule detail (codeforge-review templates SSOT)
- 병렬 스폰 권장 (spawn sequence 중복)
- GitHub workflow subsection 상세 (consumer-guide.md + label-registry-v1.md SSOT)

**Future ratchet**: linter (`scripts/check-claude-md-scope.sh` 가칭) 가 boundary 강제 — 본 CFP scope 밖, 후속 CFP 처리.

CLAUDE.md 본문에는 ADR-012 의 5-line summary + ADR link 만 inline 명시 (top of file).

## 3. 산출물

### 3.1 PR-1 (codeforge-test) scope

**Branch**: `cfp-44-test-claude-md-backfill`
**File**: `CLAUDE.md`

**추가 내용** (TestAgent self-write 표 옆 또는 별도 절):
- functional / performance subset 병렬 spawn 규약
- baseline 10% mean threshold (consumer overlay 가 baseline 위치 지정)
- sequential fallback (`tests.performance.depends_on_functional: true`)
- consumer overlay runner config delegation

**ADR-012 reference**: PR-4 머지 후 cross-link 갱신 (또는 PR-1 본문에 PR-4 머지 후 1-line update follow-up 명시).

### 3.2 PR-2 (codeforge-design) scope

**Branch**: `cfp-44-design-claude-md-backfill`
**File**: `CLAUDE.md`

**추가 내용**:
- "4-way 이념 대립" 절 body 채움 (Mapper conservative ↔ Refactor innovator ↔ SecurityArch threat ↔ DataMigrationArch integrity. ArchitectAgent chief author 가 충돌 시 Change Plan §2/§3/§7/§11 에 결정 근거 명시)
- ArchitectPL stateless re-spawn lifecycle (token cost ~5-10k per spawn, FIX 3× = 15-30k overhead)
- Deputy Freshness rule (매 design lane 진입 시 5 deputy 재 spawn, 이전 Story 산출물 재사용 금지)

### 3.3 PR-3 (codeforge-requirements) scope

**Branch**: `cfp-44-req-claude-md-backfill`
**File**: `CLAUDE.md`

**추가 내용**:
- Clarification 재스폰 패턴 (one-shot subagent — PL 통합 중 추가 질의 필요 시 Orchestrator 에 "<에이전트> 재스폰 요청 + clarification context" 전달)
- Domain Knowledge page schema reference (frontmatter: title / area / topic_slug / status / sources / related_adrs / related_stories / updated; sections: ## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력. CFP-27 신설 — `templates/domain-knowledge.md` SSOT)

### 3.4 PR-4 (wrapper codeforge) scope

**Branch**: `cfp-44-wrapper-claude-md-compression`
**Files**:
- `CLAUDE.md` (UPDATE)
- `docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md` (NEW)

**CLAUDE.md 압축 표** (현재 line ref ~ §5.1 정확 grep 으로 plan 단계에서 매핑):

| 섹션 | 현재 | 후 | 처리 |
|---|---|---|---|
| Plugin intro (1-9) | 9 | 9 | KEEP (identity) |
| Marketplace cross-repo 동기화 의무 (11-22) | 12 | 12 | **KEEP** (wrapper-only cross-repo CI 의무) |
| 세션 개시 의무 (23-72) | 50 | ~25 | checklist 압축 + playbook §1.1 link. 6 의존성 SSOT 표는 잔류 |
| Development Agent Team tree (73-124) | 52 | ~10 | "lane → plugin → agent count" 6행 표로 |
| 레인 7개 · 단계 정의 (125-146) | 22 | ~12 | 레인 sequence 다이어그램 + 1 Story = 2 PRs invariant 만. 각 lane bullet 제거 |
| 오케스트레이션 규칙 intro (147-153) | 7 | 7 | KEEP (playbook SSOT pointer) |
| 컨텍스트 전달 (154-170) | 17 | ~5 | "Story file SSOT + lane plugin self-write" 만, packet detail 은 playbook §12 |
| Never-skippable 에이전트 (172-183) | 12 | ~3 | "lane plugin 별 self-write 표 SSOT 참조" 1줄 + PMO Cross-cutting 1줄 |
| 스폰 시퀀스 (185-275) | 91 | ~10 | high-level lane sequence + playbook §3 link |
| FIX 루프 detail (277-311) | 35 | ~18 | trigger / counter / §10 schema (KEEP — SSOT 예외 #3) |
| 원인 판정 decision table (313-341) | 29 | 29 | **KEEP (SSOT 예외 #2)** |
| Review severity 종합 규칙 (343-345) | 3 | 3 | already 1-paragraph pointer (KEEP) |
| 책임 매트릭스 (347-398) | 52 | 52 | **KEEP (SSOT 예외 #1)** |
| PMOAgent 프로젝트 관리 (400-414) | 15 | 3 | trigger 요약 + codeforge-pmo agent md link |
| 4-way 이념 대립 (416-426) | 11 | 0 | codeforge-design SSOT (PR-2 후) |
| 설계 deputy Freshness (428-432) | 5 | 0 | codeforge-design SSOT (PR-2 후) |
| ArchitectPL 라이프사이클 (434-440) | 7 | 0 | codeforge-design SSOT (PR-2 후) |
| Write 권한 (441-451) | 11 | 0 | post-CFP-40 redundant ("wrapper agent 0개" 자인) |
| Lane plugin self-write boundary 표 (453-477) | 25 | 25 | **KEEP** (cross-cutting policy) |
| Codex CLI / 플러그인 필수 (479-482) | 4 | 0 | §필수 의존성 SSOT 중복 |
| 병렬 스폰 권장 (484-490) | 7 | 0 | spawn sequence 중복 |
| Inter-plugin Contract (492-528) | 37 | 37 | **KEEP** (cross-cutting policy) |
| ADR (530-555) | 26 | ~12 | 위치/생성 기준 KEEP. DesignReview ADR check 는 codeforge-design SSOT |
| 버그 기록 (556-559) | 4 | 4 | KEEP |
| GitHub Workflow subsections (561-649) | 89 | ~25 | wrapper-owned `templates/github-workflows/` listing + 계층 절만. 상세는 consumer-guide.md + label-registry-v1.md SSOT |
| Story 작성 의무 (651-688) | 38 | 38 | **KEEP** (dogfood policy, cross-cutting) |
| docs/stories markdown 규약 요약 (690-697) | 8 | 8 | KEEP (cross-cutting) |
| Domain Knowledge (699-705) | 7 | 0 | codeforge-requirements SSOT (PR-3 후) |
| **ADD: SSOT Boundary 절** (top, after intro) | — | ~10 | ADR-012 5-line summary + link |

추정 합계: 705 → **~330줄** (정확 카운트는 plan 단계 + PR review 시 확정. 320 미만 달성 시 더 좋음)

**ADR-012 본문 구조** (CFP-43 ADR-009 schema follow):
- frontmatter (adr_number: 12 / title / status: Adopted / category: Team & Process / date: 2026-04-30 / related_files)
- ## 상태
- ## 컨텍스트 (CFP-43 후 잔재 + audit 결과)
- ## 결정 (D5 본문 verbatim)
- ## 결과 (cost · benefit · 검증)
- ## 거부된 대안 (A2 symmetric refresh / A3 wrapper-only quick-win / linter-first ratchet — boundary 정의 없이 자동 강제만 도입하는 안)
- ## 다이어그램 (생략 가능 — schema 변경 없음)
- ## 관련 파일

## 4. 의존 + Ordering

**Sequence**:
- T0: PR-1 / PR-2 / PR-3 cross-repo 작업 시작 (병렬 가능)
- T1: PR-1 머지 (admin 또는 자체 dogfood workflow)
- T2: PR-2 머지
- T3: PR-3 머지
- T4: PR-4 wrapper 작업 시작 (PR-1~PR-3 머지 완료 확인 후)
- T5: PR-4 머지 → ADR-012 Adopted

PR-1~PR-3 간 의존 없음. PR-4 는 PR-1~PR-3 모두 머지 후 시작 권장 (cross-link 정합).

**예외**: 사용자 momentum 우선 시 PR-4 를 PR-1~PR-3 와 병렬 작업 가능. 그 경우 PR-4 의 cross-link 가 일시적으로 broken (lane plugin 측 갱신 전 머지). 모든 PR 머지 후 정합 회복 — CFP-43 §8.1 와 동일 위험 모델.

## 5. Test contract

### 5.1 PR 별 기능 테스트

| PR | Test |
|---|---|
| PR-1 | `mclayer/plugin-codeforge-test` repo lint chain PASS + `grep -c '10% baseline\|functional.*subset\|performance.*subset' CLAUDE.md` ≥ 3 |
| PR-2 | `mclayer/plugin-codeforge-design` lint PASS + `grep -c '4-way\|stateless 재스폰\|Deputy Freshness' CLAUDE.md` ≥ 3 |
| PR-3 | `mclayer/plugin-codeforge-requirements` lint PASS + `grep -c 'Clarification 재스폰\|domain-knowledge.md' CLAUDE.md` ≥ 2 |
| PR-4 | wrapper lint chain (frontmatter + section-schema + inter-plugin-contracts + check-doc-links + check-doc-frontmatter) PASS + §5.2 wrapper grep 통과 |

### 5.2 Wrapper grep test (PR-4)

```bash
# Negative — 압축 대상 헤더 잔존 0 (본문 mention 은 별개)
grep -c '^### .*4-way 이념\|^### .*Deputy Freshness\|^### .*ArchitectPL 라이프사이클' CLAUDE.md  # = 0
grep -c '^### .*병렬 스폰 권장\|^### .*Codex CLI / 플러그인 필수' CLAUDE.md  # = 0
grep -c '^## Domain Knowledge' CLAUDE.md  # = 0 (## 헤더 부재 = codeforge-requirements 위임 완료)
grep -c '^### Write 권한' CLAUDE.md  # = 0

# Positive — boundary 절 존재
grep -c 'SSOT Boundary\|ADR-012' CLAUDE.md  # ≥ 2

# Line count
test "$(wc -l < CLAUDE.md)" -le "330"  # ~330 target. buffer 까지 허용
```

### 5.3 ADR-012 schema 검증

`scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` PASS (CFP-27 schema warning mode 적용).

### 5.4 Cross-link 정합 (PR-4 후)

수동 spot-check (reviewer):
- CLAUDE.md "lane plugin 참조" pointer 가 실제 lane plugin CLAUDE.md 의 갱신된 절을 가리킴
- ADR-012 의 "3 SSOT 예외" 가 CLAUDE.md 본문의 책임 매트릭스 + 원인 판정 table + FIX Ledger schema 와 일치

### 5.5 성능 테스트

N/A — 순수 docs 변경.

## 6. Phase 1 / Phase 2 PR split

CFP-43 precedent 답습 — 4 PR 모두 single-PR (Phase 1+2 분리 안 함). 이유:
- 각 PR 이 작은 fix 단위 (cross-repo CLAUDE.md 추가 ~30줄, wrapper CLAUDE.md 압축 표 적용)
- 7-lane workflow 가 docs cleanup 에 과도
- wrapper meta-CFP 는 admin merge 패턴 (CFP-42·CFP-43 수립)

각 PR body 명시:
- 본 CFP-44 spec link
- audit gap 의 해당 plugin section
- before/after diff 핵심 1-2 line
- (PR-4 한정) ADR-012 신설 안내

## 7. Out of scope

| 항목 | 분리 사유 | 후속 |
|---|---|---|
| Linter `check-claude-md-scope.sh` | ADR-012 ratchet — 본 CFP 는 boundary 정의만, 강제는 별도 | 후속 CFP |
| Playbook 재구조화 | 현재 CLAUDE.md ↔ playbook bidirectional SSOT 의 wrapper 측만 처리 — playbook 측 압축은 drift 위험 | 별도 검토 |
| Lane plugin agent md 변경 | 본 CFP 는 lane plugin CLAUDE.md 만 (SSOT pointer) — agent md 갱신은 audit 시 PARTIAL safe 분류 | 자연 follow-up 발생 시 별도 |
| migration-guide v0.22→v5 BREAKING parity | CFP-41 retro 후속 (CFP-43 §7) | 별도 |
| Symmetric backfill (review/pmo/develop CLAUDE.md refresh) | Codex 명시 reject — process symmetry 만 사고 risk reduction 못 사는 거래 | 미실시 |
| Wrapper plugin.json 변경 | 본 CFP 는 docs only — version bump 불필요 | N/A (PR-4 도 minor 또는 patch 후속) |

## 8. Open questions / risks

### 8.1 Question — PR-4 line count 정확도

**Q**: 표의 ~330줄 추정이 실제 압축 후 line count 와 일치할까?

**현재 결정**: plan 단계에서 line-by-line 매핑 + PR-4 작업 시 실제 line count 측정. 330 (target) 초과 시 추가 압축 시도. 380 초과 시 design 재검토.

**Bottom-up 분석**:
- KEEP no-compression (SSOT 예외 + cross-cutting policy): 책임 매트릭스 52 + 원인 판정 table 29 + Lane plugin self-write boundary 25 + Inter-plugin Contract 37 + Story 작성 의무 38 + 버그 기록 4 + docs/stories markdown 규약 8 + Marketplace sync 12 + Plugin intro 9 = **214줄** (의무 잔류)
- Compressed 합계 추정 (§3.4 표): 세션 개시 25 + Agent Team tree 10 + 레인 정의 12 + 오케스트레이션 intro 7 + 컨텍스트 전달 5 + Never-skippable 3 + 스폰 시퀀스 10 + FIX 루프 18 + Review severity 3 + PMOAgent 3 + ADR 12 + GitHub Workflow 25 + SSOT Boundary 신설 10 = **143줄**
- 총 추정: 214 + 143 = **357줄**

330 미만 달성하려면 cross-cutting policy 영역 (책임 매트릭스 / Story 작성 의무 등) 의 추가 압축이 필요. PR-4 작업 시 결정.

**Open**: 280줄 첫 추정은 cross-cutting policy 잔류량 underestimate. 본 self-review 에서 330줄 로 수정. 절감률은 53% (705→330) — 사용자 의도 (60% 절감) 보단 보수적이지만 정보 손실 0 우선.

### 8.2 Risk — playbook reference drift

**Risk**: Wrapper CLAUDE.md 가 `docs/orchestrator-playbook.md §3 (스폰 시퀀스) · §6.5 (decision table reference back)` 에 의존. playbook 구조 변경 시 link 깨짐.

**Mitigation**: `scripts/check-doc-links.sh` (existing) cover. PR-4 본문에 link 정합 spot-check 의무 명시.

### 8.3 Risk — PARTIAL safe 의 미발견 gap

**Risk**: review/pmo/develop 가 "PARTIAL safe" 로 분류됐지만 wrapper 압축 후 미발견 gap 이 surface 가능.

**Mitigation**: 발견 시 별도 follow-up CFP 로 처리. Codex 가 명시적으로 "이 risk 는 architectural blocker 아님" 판정 — A1' 의 trade-off 수용.

### 8.4 Risk — ADR-012 boundary 강제 수단 부재

**Risk**: ADR-012 가 boundary 정의만 두고 자동 강제 수단 (linter) 부재. 향후 wrapper CLAUDE.md drift 가능.

**Mitigation**: 본 CFP scope 밖 — 후속 CFP 에서 `check-claude-md-scope.sh` 도입. 단기 mitigation: PR review 시 ADR-012 boundary 준수 spot-check 의무.

### 8.5 Question — line count 목표 절대값

**Q**: 330줄이 target 이지만, 추가 잔류 필요 시 어디까지 허용?

**현재 결정**: 330 target → 380 까지 허용 (audit-uncovered gap surface 포함). 380 초과 시 design 재검토 (cross-cutting policy 영역의 SSOT 재배치 또는 본 CFP scope 축소).

## 9. 참조

### 9.1 ADR

- [ADR-009 Wrapper-only Decomposition](../../adr/ADR-009-wrapper-only-decomposition.md) — ζ arc parent. 본 CFP 가 추격하는 정합성 잔재의 출처
- [ADR-010 Inter-plugin Contract Sibling Sync](../../adr/ADR-010-inter-plugin-contract-sibling-sync.md) — 같은 cleanup arc
- ADR-012 (NEW, this CFP PR-4) — Wrapper CLAUDE.md SSOT Boundary

### 9.2 관련 CFP

- [CFP-31 ζ arc parent design](2026-04-29-cfp-31-wrapper-only-decomposition-design.md)
- [CFP-43 X2 cleanup predecessor](2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md) — DocsAgent ghost text + 21-gap audit. 본 CFP 의 직전 단계
- CFP-32 (FIX Ledger Orchestrator monopoly · `fix-event-v1` contract) — 본 CFP 의 SSOT 예외 #3 출처

### 9.3 Audit 산출물

본 brainstorming 단계에서 dispatched audit subagent 산출:
- 6 lane plugin CLAUDE.md SSOT coverage 매트릭스 (1 MISSING + 5 PARTIAL = 2 critical + 3 safe)
- 3 wrapper-must-keep 항목 식별 (책임 매트릭스, decision table, FIX Ledger schema)
- A1 vs A2 vs A3 trade-off 분석 input

### 9.4 Codex second opinion

(`Agent` codex:codex-rescue 호출 결과)
- A1 정당화 (audit-driven minimum)
- A2 reject (process symmetry 만 사고 risk reduction 못 사는 거래)
- A3 reject (ADR 급 결정 의도 미달성)
- 보강안 채택: explicit boundary statement → ADR-012 신설
