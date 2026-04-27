---
title: TestContractArchitectAgent 신설 — §8 Test Contract author input 분담
slug: cfp-18-test-contract-architect
status: draft
author: ArchitectAgent
inputs:
  - CodebaseMapperAgent
  - RefactorAgent
  - SecurityArchitectAgent
reviewers: [DesignReviewPLAgent]
related_adrs: [ADR-004, ADR-005, ADR-006]
created: 2026-04-27
story: CFP-18
---

# Change Plan: TestContractArchitectAgent 신설

## §1 목적

ADR-004 후속 — Codex audit #1 (Top-1, High severity) 해소. **§8 Test Contract author input을 chief author 단독에서 deputy로 분리**해 self-validation 위험 제거. SecurityArchitectAgent:§7 패턴과 isomorphic 적용.

수용 기준: AC-1~AC-10 + AC-INV-1~4 (Story §5.1 verbatim). 핵심: TestContractArchitectAgent 신설 / chief author 본문 작성권 유지(§8 author = ArchitectAgent) / deputy 4인 → 5인 SSOT 일괄 갱신 / ADR-006 발행 / §7-§8 cross-reference 규칙 명문화.

## §2 현재 구조 분석 (CodebaseMapper 입력)

- **§8 author**: `agents/ArchitectAgent.md`:56,76,80에서 chief author 단독 — Mapper/Refactor/SecurityArch deputy 입력 부재
- **ArchitectPL 검수 4 항목**: `agents/ArchitectPLAgent.md`:58-66 — §8 author input 통합 정합성 슬롯 부재
- **QADev 라인**: `agents/QADeveloperAgent.md`:25에 "계약 소유자 = ArchitectAgent", :71 "자체 추가 금지" — 시점 분리 invariant 보존
- **deputy 4명 hardcode 산재**: ArchitectAgent.md (7개소), ArchitectPLAgent.md (11개소), CLAUDE.md 다이어그램, playbook 다수, plugin.json `"22 core"` (실제 23 — CFP-17 drift 잔존)

## §3 도입할 설계 (Mapper / Refactor / SecurityArch 3-way 입력 + 충돌 결정)

### §3.1 핵심 결정

1. **TestContractArchitectAgent 신설** — ArchitectPL 직속 5번째 deputy. SecurityArch 동형 (Mapper M1·M2 채택)
2. **§8 author = ArchitectAgent 유지** — TestContractArch는 author input contributor (사용자 결정 #2 verbatim, SecurityArch:§7 동형)
3. **TestContractArch 책임 정의 = "QA perspective contributor"** — Researcher Insight 3 경고 반영, "test contract author" 회피 (Architect 영역 중복 차단)

### §3.2 ArchitectPL 검수 — 메타-규칙 2 항목 압축 (충돌 1: Refactor STRONG ROI #1 채택)

**채택 근거**: Refactor 채택. SecurityArch (CFP-17) + TestContractArch (CFP-18) 두 번 적용 시점에 패턴 표면화 — deputy N+1 추가 시 sub-bullet 1행만 갱신, enumerate 폭증 회피 ROI 정당. Mapper M4 우려(readability 1행 차이)는 long-term drift 방지가 상회.

ArchitectPLAgent.md §3 검수 항목 4 → 2 (메타-규칙):

```
1. §섹션별 deputy author input 통합 정합성 (메타-규칙):
   - §2 → CodebaseMapperAgent
   - §3·§6 → RefactorAgent
   - §7 → SecurityArchitectAgent
   - §8 → TestContractArchitectAgent
   각 deputy 산출물의 chief author 채택/반박 정합성 검증
2. §섹션 누락 차단 (§7 / §8 / §10 ADR 판단)
```

### §3.3 §7 ↔ §8 cross-reference 규칙 (충돌: 사용자 결정 #4 + Refactor STRONG ROI #2 채택)

- §7 author 권한: 보안 테스트 항목은 SecurityArch가 §7.5 위협-완화 매핑에 작성
- §8 cross-reference 의무: TestContractArch가 §8.2 경계·invariant 작성 시 §7.5 항목 cross-ref ("→ §7.5 T-N 참조")
- 양 agent md (`SecurityArchitectAgent.md`, `TestContractArchitectAgent.md`)에 "§7 ↔ §8 cross-reference 규칙" 섹션 mutual reference

### §3.4 TestContractArch ↔ QADev mutual reference (Refactor STRONG ROI #3 채택)

- TestContractArchitectAgent.md "QADev 인터페이스" 섹션: 시점·산출물 type 분리 명시 (Story §2.3 invariant verbatim)
- QADeveloperAgent.md:25 갱신: `"계약 소유자 = ArchitectAgent (chief author, TestContractArch deputy input 통합 후 §8 확정)"`
- :71 "자체 추가 금지" + `role: qa` invariant 보존 (변경 금지)

### §3.5 도형 대립 비참여 cross-reference (충돌 3: Refactor 1줄 채택)

CodebaseMapperAgent.md / RefactorAgent.md / SecurityArchitectAgent.md "Mapper/Refactor와의 관계" 절 끝에 1줄 추가:
> TestContractArchitectAgent는 §8 author input contributor (도형 대립 비참여 — Mapper/Refactor/SecurityArch 3-way와 별개 영역).

본문 변경 금지 (사용자 결정 #4 정합).

### §3.6 ADR-005 status 전이

CFP-17 §7 N/A + CFP-18 §7 부분 N/A 두 번 dogfooding 검증으로 **결정 1·2·3 (N/A 표기 형식·면제 분류·N/A inheritance 차단)** 안정화 검증 완료 → ADR-005 status `Proposed` → `Accepted` 전이 (chief author + 사용자 승인). 본 Change Plan 채택 시 ADR-005 frontmatter 갱신 동시 commit.

**결정 4 분리**: ADR-005 결정 4 (invariant-check Step 신설)는 **본 Story 범위 외**. CFP-17/18 dogfooding은 결정 1·2·3에 한정 검증, 결정 4 invariant-check workflow Step 추가 implementation은 별도 Story (CFP-19+) 발의 의무. 본 status 전이가 결정 4 self-condition 충족을 함의하지 않음.

## §4 API 계약

### §4.1 TestContractArch ↔ ArchitectPL (input/output)

- **Input**: 공통 패키지 (코드 경로 + Story §1-7 + 관련 ADR + Change Plan 초안). 다른 deputy 산출물 미수신 (독립성)
- **Output**: §8.1 단위/통합/인프라 커버리지 후보 + §8.2 경계·invariant 후보 + §8.3 Perf Baseline 적용성 판정 + §8.6 N/A 권한 행사 시 사유

### §4.2 TestContractArch ↔ ArchitectAgent (chief author 통합)

chief author가 deputy output을 §8.1-§8.3 본문에 반영. 채택/반박 근거를 Change Plan §3에 명시. TestContractArch §8.6 N/A 권고 시 chief author 채택/반박 권한.

### §4.3 TestContractArch ↔ QADev (시점 분리)

설계 lane TestContractArch §8 본문 author input → 구현 lane QADev §8.5 Impl Manifest 매핑표 author. 산출물 type 분리 invariant (명세 텍스트 vs 테스트 함수 코드).

### §4.4 TestContractArch ↔ SecurityArch (§7-§8 cross-reference)

§7.5 위협-완화 매핑이 §8.2 경계·invariant에 cross-ref되도록 양 deputy가 양방향 reference. chief author 통합 시 두 섹션 일관성 검증 (ArchitectPL 메타-규칙 §3.2-1번 항목으로 감사).

## §5 변경 계획 (파일 단위)

| 파일 | 유형 | 담당 | 설명 |
|------|------|------|------|
| `agents/TestContractArchitectAgent.md` | 신규 | DocsAgent | SecurityArchitectAgent.md verbatim copy + 도메인 substitution (§7→§8, "공격자/위협"→"QA perspective contributor", **"trust boundary/auth/data"→"§8 author input (QA perspective contributor)"**). WebSearch/WebFetch 제거 (min-privilege, SecurityArch §7.7). "QADev 인터페이스" 섹션 + "§7-§8 cross-reference 규칙" 섹션 추가. **본문 구조 매핑** (SecurityArch §7.x → TestContractArch §8.x): §7.1 Trust boundary → §8.0 책임 범위(§8.1·§8.2·§8.3 author input scope) / §7.2 STRIDE-LITE → §8.1 단위·통합·인프라 covered cases / §7.3 Auth/Authz → §8.2 경계·invariant / §7.4 민감 데이터 → §8.3 Perf Baseline 타당성 / §7.5 위협-완화 매핑 → §8.4 N/A 권한(동형) / §7.6 N/A → §8.4 N/A 권한 |
| `agents/ArchitectAgent.md` | 수정 | DocsAgent | 7개소: description / :23, 27, 39, 48 "3 deputy" → "4 deputy", :56 §8 author 라인 "TestContractArch input 통합 후 확정" 보강 |
| `agents/ArchitectPLAgent.md` | 수정 | DocsAgent | 11개소: description / :23, 27 deputy 4 → 5 / :38-43 spawn diagram +TestContractArch / :45, 51 input 4 → 5 / :58-66 검수 4 항목 → 메타-규칙 2 항목 (§3.2 위 본문) / :70 clarification list / :103 4 deputy → 5 |
| `agents/QADeveloperAgent.md` | 수정 | DocsAgent | :25 1줄 보강 (§3.4 위 verbatim). :33, 53-56, 71 invariant 보존 |
| `agents/CodebaseMapperAgent.md` | 수정 | DocsAgent | "Mapper/Refactor와의 관계" 절 끝 1줄 cross-ref (§3.5) |
| `agents/RefactorAgent.md` | 수정 | DocsAgent | 동상 1줄 cross-ref |
| `agents/SecurityArchitectAgent.md` | 수정 | DocsAgent | 동상 1줄 cross-ref + "§7 ↔ §8 cross-reference 규칙" 섹션 신설 |
| `templates/change-plan.md` | 수정 | DocsAgent | frontmatter inputs +1 (TestContractArchitectAgent). §8 header에 "author input: TestContractArch (deputy) → chief author 통합" 1줄. §8.4 신설 (§8.6 N/A 권한 — `plugin-meta-na`/`runtime-inert` ADR-005 정합) |
| `templates/review-checklists/design.md` | 변경 0 | — | 기존 `test-contract` enum + 5축 충분 (Mapper M9). invariant Test 6 3-location parity 부담 회피 |
| `CLAUDE.md` | 수정 | DocsAgent | 다이어그램 (5 deputy) / **22 core → 23 core (v0.12.0)** / Never-skippable list / spawn list / 4 감사 → 메타 2 항목 / write queue list. "3-way 이념 대립" 본문 변경 금지, 절 끝 1줄 cross-ref |
| `docs/orchestrator-playbook.md` | 수정 | DocsAgent | deputy 수 일괄 (4→5) + 토큰 예산 표 + 작업 요약 표 + bonus drift 정정: **line 22 / 561 / 589 "20 core" → "23 core"** (CFP-17 drift 정정 + CFP-18 적용). **line 1001 v5 changelog "24 core" → "23 core"** (CFP-17 drift, §5 누락분 보강 — chief author 판정: changelog 항목이 "그 시점 정확값" 기록이라면 v5 시점 baseline 22 core ⊕ CFP-18 +1 = 23 core가 history fact, "24 core"는 drift로 분류). **line 1004 v9 changelog "25 → 20 core agents"는 정정 대상 아님** — ADR-001 직후 baseline 20 core 정확 history fact. "23 core" 표기는 playbook에 부재 (현 baseline 22 core가 doc에 22로 표기). |
| `docs/plugin-design.md` | 수정 | DocsAgent | 5개소 **22 → 23 core** + 라인업 prose +1 element |
| `.claude-plugin/plugin.json` | 수정 | DocsAgent | version 0.11.0 → 0.12.0 + **"22 core" → "23 core"** |
| `CHANGELOG.md` | 수정 | DocsAgent | v0.12.0 entry (BREAKING — invariant Test 7 의무, **22 → 23 core**) |
| `README.md` | 수정 | DocsAgent | 4개소 **22 → 23 core** |
| `docs/migration-guide.md` | 수정 | DocsAgent | "v0.11 → v0.12" 절 신설 (invariant Test 7 통과) |
| `docs/adr/ADR-006-testcontract-architect.md` | 신규 | DocsAgent | ADR-004 verbatim copy + substitution + 사용자 5 결정 verbatim 인용 |
| `docs/adr/ADR-005-plugin-self-application-na-standardization.md` | 수정 | DocsAgent | frontmatter status `Proposed` → `Accepted` (§3.6) |
| `docs/adr/ADR-004-architectpl-securityarch-restructure.md` | 수정 | DocsAgent | 라인 70-72 후속 #1 closure 라인: "#1 = CFP-18 + ADR-006으로 해소" cross-ref |

> **변경 통계**: 신규 2 + 수정 16 + 변경 0 1 = 총 19 파일. (기존 "수정 17" 표기는 review-checklists/design.md "변경 0" 행 합산 오류 — off-by-one 정정.)

> **Impl Manifest**: Phase 2 PR §8.5 매핑표 commit 후 자동 sub-issue 생성 (subissue-from-impl-manifest.yml)

## §6 리팩토링 선행 작업

§3.2 메타-규칙 압축은 본 Story 범위 내 (TestContractArch 추가 시 enumerate 폭증 회피가 직접 요구) — 별도 선행 PR 불필요. ArchitectPLAgent.md 갱신과 동일 commit에 포함.

기타 deferred (Refactor packet B): deputy yaml manifest (CFP-19+), frontmatter dict 전환 (REJECT), 책임 매트릭스 sub-division (REJECT), invariant-check workflow 자동화 (CFP-19+).

## §7 보안 설계 (SecurityArchitectAgent 입력)

### §7.5 위협 ↔ 완화 매핑

본 Story의 위협-완화 매핑은 §7.7 본문이 substitute 한다 — T1 (신규 agent permission model) ↔ min-privilege spec (WebSearch/WebFetch 제거, deny list). §7.7 yaml block이 mapping table의 implementation 형식. SecurityArch 통상 §7.5 STRIDE-LITE 표 형식 대신, plugin-meta Story 특성(§7.6 부분 N/A) 상 단일 위협 T1만 존재해 §7.7 1행 매핑으로 substitute 정합.

### §7.6 부분 N/A — `plugin-meta-na` (ADR-005 분류)

본 Story는 trust boundary 변경 없음 — STRIDE 분석 부분 N/A. 근거: agent md / template / docs / yaml 변경만, 외부 입력·인증·민감데이터 흐름 변경 0건.

- 검증 채널: ArchitectPL 메타-규칙 §3.2-1번 항목 (§7 SecurityArch input 통합 정합성)
- 면제 분류: `plugin-meta-na` (ADR-005 결정 2 verbatim)

### §7.7 T1 위협 + min-privilege 완화책 (§7.5 substitute implementation)

**T1 (P1)**: TestContractArchitectAgent frontmatter `permissions:` over-privileged allow list 부여 시 deputy 권한 model 위반 위험.

**완화책 (min-privilege spec)** — TestContractArchitectAgent.md 신규 작성 시 의무 적용:

```yaml
permissions:
  allow:
    - Read
    - Grep
    - Glob
    - Bash(find *)
    - Bash(ls *)
    - Bash(git log *)
    - Bash(git blame *)
    - Edit(.claude-work/doc-queue/**)
    - Write(.claude-work/doc-queue/**)
    - Bash(mkdir -p .claude-work/doc-queue*)
    - Bash(ls .claude-work/doc-queue*)
  deny:
    - Edit(src/**)
    - Write(src/**)
    - Edit(tests/**)
    - Write(tests/**)
    - Edit(docs/**)
    - Write(docs/**)
```

**SecurityArch 대비 차이**: WebSearch/WebFetch 제거 (TestContractArch는 외부 lookup 불필요, 내부 §8 author input만 produce — min-privilege 강화).

### §7.8 ADR-004 패턴 안정성

stateless 재스폰 + path-scoped permissions invariant 유지. T1 완화책 외 신규 보안 결정 없음.

## §8 Test Contract

### §8.6 N/A — `plugin-meta-na` (ADR-005 정합, §8.4 신설 절 verbatim 적용)

본 Story는 실행 가능 코드 0줄 — agent md / template / docs / yaml 변경만. 단위/통합/인프라/Perf 테스트 inert.

- 검증 채널: invariant-check workflow 자동 검증 — agent count 22→**23** parity / frontmatter contract / ADR-002 footer / write queue parity / category enum 3-location parity / severity_overrides count / BREAKING migration-guide presence (Test 7)
- 면제 분류: `plugin-meta-na`
- self-paradox 인지: TestContractArch가 신설 대상 자체이므로 본 Change Plan §8은 chief author 단독 author (TestContractArch input 0건) — Story §1 verbatim 인지된 paradox

## §9 분기 선택 (필요 Dev 조합)

- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰): docs/stories/CFP-18.md §1-§7 + docs/change-plans/cfp-18-test-contract-architect.md + docs/adr/ADR-006-testcontract-architect.md draft
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트): 19 SSOT 갱신 + agents/TestContractArchitectAgent.md 신규 + ADR-005/004 cross-ref 갱신
- 의존성: 없음. 모든 파일 독립 갱신 가능 → DocsAgent 단일 commit batch 가능

## §10 ADR 대상 여부

### §10.1 신규 ADR-006 발행 의무

새 deputy 도입 = "에이전트 추가·역할 재정의" (CLAUDE.md ADR 생성 기준 직접 해당). ADR-006 작성 의무.

### §10.2 ADR 정합성 점검

- ADR-001/002/003: 무관, 위반 0
- ADR-004: 후속 #1 closure로 정합. 본문 "후속 조치" 섹션에 cross-ref 추가 (ADR 본문 변경 = 신규 ADR 의무가 아닌 cross-ref 갱신만, supersede 아님)
- ADR-005: status `Proposed` → `Accepted` 전이 (CFP-17/18 두 번 dogfooding) — chief author + 사용자 승인 권한
- ADR-006: 신규 — `Accepted` 상태로 author (사용자 5 BLOCKING 결정 verbatim 인용)
