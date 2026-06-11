---
adr_number: 56
title: Domain-Concept knowledge directory separation — domain/ vs concept/ 물리 분리
date: 2026-05-11
status: Accepted
category: agent-design
carrier_story: null
supersedes: []
amends: ADR-046
related_stories: []
related_adrs:
  - ADR-046
  - ADR-013
related_files:
  - mclayer/plugin-codeforge-requirements/agents/DomainAgent.md
  - mclayer/plugin-codeforge-requirements/agents/ResearcherAgent.md
  - mclayer/plugin-codeforge-requirements/agents/RequirementsPLAgent.md
  - mclayer/plugin-codeforge-requirements/CLAUDE.md
  - mclayer/plugin-codeforge-requirements/templates/domain-knowledge.md
  - mclayer/plugin-codeforge-requirements/templates/concept-knowledge.md
  - scripts/check-doc-frontmatter.sh
is_transitional: false
---

# ADR-056: Domain-Concept knowledge directory separation

## 상태

**Accepted (2026-05-11)** — ADR-013 dogfood-out waiver (ADR-046 패턴 inherit).

## 컨텍스트

ADR-046이 DomainAgent(사내 known knowns)와 ResearcherAgent(외부 concept)의 mandate를 분리했으나, 산출 파일 경로가 `docs/domain-knowledge/<area>/<topic>.md` 단일 경로로 공유되어 소유 경계가 파일명 접두어 규약에만 의존하고 있었다. 파일명 규약은 강제력이 약해 혼용 가능성이 있다.

브레인스토밍(Opus + Codex 독립 검토) 결과 두 검토가 동일한 분리 축을 도출했다:

| | DomainAgent | ResearcherAgent |
|---|---|---|
| 답하는 질문 | "우리 시스템에서 이 요구는 어디에 닿는가?" | "이 용어는 업계·학계에서 무엇을 의미하는가?" |
| 소스 | ADR + 코드 + domain/domain-*.md | WebSearch/WebFetch + concept/concept-*.md 누적본 |
| PLAgent에 주는 가치 | 위치성 — 기존 제약·충돌·gap 표면화 | 의미성 — 개념 정의 + 해석 옵션 (결정은 PLAgent) |

또한 PLAgent의 §6 합성 시 "ResearcherAgent 개념을 DomainAgent §2 내부 제약과 조화시키지 않은 채 요구사항에 직접 복사" 문제가 구조적으로 차단되지 않고 있었다. Codex 검토가 PLAgent 합성 순서 명문화를 제안했다.

## 결정

### 결정 1: 물리 디렉터리 분리

```
docs/domain-knowledge/
├── domain/          ← DomainAgent 단독 소유
│   └── <area>/<topic>.md  (frontmatter: kind: domain_fact)
└── concept/         ← ResearcherAgent 단독 소유
    └── <slug>.md    (frontmatter: kind: concept_definition)
```

- 기존 `docs/domain-knowledge/<area>/<topic>.md` 파일 전량을 `docs/domain-knowledge/domain/<area>/<topic>.md`로 이동
- ResearcherAgent는 신규 `docs/domain-knowledge/concept/<slug>.md` 경로에 write 권한 부여
- 파일명 규약이 아닌 **경로** 자체가 소유 신호

### 결정 2: frontmatter `kind` 필드 추가

| 파일 위치 | 필수 kind 값 | 추가 필수 필드 |
|---|---|---|
| `docs/domain-knowledge/domain/**` | `domain_fact` | title, area, topic_slug, status, updated (기존 유지) |
| `docs/domain-knowledge/concept/**` | `concept_definition` | title, slug, status, updated |

### 결정 3: PLAgent 합성 순서 명문화

PLAgent는 3 sub-agent 산출물을 아래 순서로 합성한다:

1. **§5 Analyst** — 모호성 목록 확정 (언어적 불확실성 먼저 해소)
2. **§2 Domain** — 내부 제약 적용 (시스템 경계 확인 후)
3. **§6 Researcher** — 외부 개념으로 용어 disambiguation (내부 제약 조화 후 적용)
4. **PLAgent 결정** — 최종 요구사항·AC·Non-goal 작성

**금지 규칙**: PLAgent는 ResearcherAgent §6의 개념·재편 요구사항을 DomainAgent §2 내부 제약과 조화시키지 않은 채 요구사항에 직접 복사하는 것을 금지한다. Researcher는 선택지·개념을 제공하고 PLAgent가 결정한다.

### 결정 4: §6 compact summary

ResearcherAgent는 §6 출력에 자신이 참조/생성한 concept 파일의 compact 요약을 포함한다. PLAgent가 `docs/domain-knowledge/concept/` 파일을 매번 직접 Glob+Read하는 부담을 제거.

형식: 각 concept 파일별 1-3줄 요약 + 파일 경로 링크.

### 결정 5: 4중 강제 레이어

1. **디렉터리**: `domain/` vs `concept/` 물리 경로
2. **frontmatter schema**: `kind` 필드 존재 + 유효값 검증
3. **lint**: `check-doc-frontmatter.sh` — `docs/domain-knowledge/domain/` / `docs/domain-knowledge/concept/` 별도 REQUIRED 필드 검증 (warning 모드 유지, CFP-28 strict 전환 후 fail)
4. **CODEOWNERS**: `docs/domain-knowledge/domain/**` → DomainAgent owner team, `docs/domain-knowledge/concept/**` → Researcher owner team (consumer overlay 매핑)

## 결과 (Consequences)

### 긍정

- 소유 경계가 파일시스템 수준으로 집행 — 파일명 규약 의존 제거
- PLAgent 합성 순서 명문화로 "개념 무단 복사" 패턴 구조적 차단
- §6 compact summary로 PLAgent의 concept 파일 직접 탐색 부담 제거
- ResearcherAgent의 concept 파일 누적 → 프로젝트 전반에 걸친 개념 사전 형성

### 부정 / 트레이드오프

- 기존 6개 domain-knowledge 파일 이동 마이그레이션 필요 (경로 참조 갱신)
- lint 스크립트 두 경로 분기 처리 (복잡도 소폭 증가)

## 대안 검토

| 대안 | 기각 사유 |
|------|----------|
| 파일명 접두어 규약 (`domain-*.md` / `concept-*.md`) | 강제력 약함 — 파일시스템 레벨 소유 신호 부재 |
| 단일 `kind` 필드만 (디렉터리 분리 없이) | 에디터·CODEOWNERS에서 경로 기반 필터 불가 |
| ResearcherAgent에 domain/ 접근 허용 | ADR-046 mandate boundary 위반 |

## ADR-013 dogfood-out waiver 사유

ADR-046 §waiver 3 사유(KEY collision / Action permission / cost asymmetry) 동일 유효. 본 ADR scope = ADR 2건 + agent 파일 3건 + template 2건 + lint 스크립트 + 마이그레이션. ADR-046 waiver pattern inherit.

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-046](ADR-046-researcher-role-redefinition.md) — ResearcherAgent role (본 ADR가 Amendment 1 적용)
- `mclayer/plugin-codeforge-requirements:agents/DomainAgent.md` (구 lane repo — 현 `plugins/codeforge-requirements/agents/`, repo 삭제됨 2026-06-12)
- `mclayer/plugin-codeforge-requirements:agents/ResearcherAgent.md`
- `mclayer/plugin-codeforge-requirements:agents/RequirementsPLAgent.md`

## 관련 ADR

- [ADR-046](ADR-046-researcher-role-redefinition.md) — ResearcherAgent role (Amendment 1 대상)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out waiver 근거
