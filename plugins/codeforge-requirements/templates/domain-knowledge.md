# Domain Knowledge 페이지 템플릿

DomainAgent가 `docs/domain-knowledge/<area>/<topic>.md` 직접 write 시 따르는 schema SSOT (CFP-26 Phase 0a 이후 owner direct write).

**사용 대상**: DomainAgent (생성·갱신 단독), DocsAgent (Story §3·§5 ADR·도메인 인용 처리 — 직접 write 안 함)

---

## 파일 위치

- **위치**: `docs/domain-knowledge/domain/<area>/<topic>.md`. `<area>`는 consumer overlay가 정의 (예: `policies/`, `accounting/`, `auth/`) — ADR-056 domain/ 서브디렉터리
- **계층**: 디렉토리 1-2단계 권장 (area / topic)
- **CODEOWNERS**: `docs/domain-knowledge/domain/**` → `@org/domain-experts` 자동 review (consumer overlay가 매핑)

---

## Frontmatter (필수)

```yaml
---
kind: domain_fact
title: <한 줄 제목>
area: <영역 — overlay에서 정의된 area 중 하나>
topic_slug: <kebab-case-slug>
status: draft | active | deprecated
sources:
  - "<원천 — 사용자 원문 / ADR / 코드 / 외부 표준 / 사내 위키 등>"
  - "<원천 2>"
related_adrs: [ADR-NNN, ADR-MMM]   # 도메인 결정과 연결되는 ADR
related_stories: [<KEY-N>, <KEY-M>] # 본 KB가 도출된 Story
updated: YYYY-MM-DD                 # 마지막 수정일 (DomainAgent가 갱신 시 업데이트)
---
```

---

## 본문 섹션 (고정 순서)

```markdown
# <Area> · <Topic>

## 정의
용어·개념의 한 줄 정의 (사전식). 비즈니스 맥락 반영.

## 컨텍스트
이 지식이 왜 필요한가, 어디서 쓰이는가 — Story·ADR·코드·운영 사례 인용.

## 핵심 규칙 / 불변식 (invariant)
- 규칙 1 (예: "한 사용자는 동시에 1개 active 세션만 보유")
- 규칙 2

## 경계 / 예외
규칙이 적용되지 않는 케이스 — 명시적 carve-out.

## 관련 ADR / Story / 코드
- [ADR-NNN](../../adr/ADR-NNN-<slug>.md) — 결정 인용
- [Story <KEY>](../../stories/<KEY>.md) — 도출 Story
- 코드 경로 (consumer 기준 relative)

## 변경 이력
- YYYY-MM-DD: 초기 작성 (Story <KEY>)
- YYYY-MM-DD: 규칙 1 추가 (Story <KEY>)
```

---

## DomainAgent 작성 절차

```
1. consumer overlay에서 area 목록 확인 (`.claude/_overlay/project.yaml` 또는 docs/domain-knowledge 기존 디렉토리)
2. 적절한 area 선택, topic-slug 결정 (kebab-case)
3. `Write(docs/domain-knowledge/domain/<area>/<topic>.md)` 호출 (ADR-056 — domain/ 서브디렉터리), frontmatter `kind: domain_fact` + 본문 작성
4. Story file §3 "관련 ADR" 또는 별도 §5 "도메인 지식" 섹션에 링크 추가 — Orchestrator 경유 DocsAgent에 의뢰 (Story file은 multi-writer)
5. 기존 page 갱신 시 frontmatter `updated` 필드 + "변경 이력" 섹션 append
```

---

## lexicon 산출물 schema (`kind: lexicon_relation`) — CFP-2453 / ADR-091 Amendment 3

consumer **application-BC** 의 단어 사전(lexicon). 동음이의(homonym)·유의(synonym)·반의(antonym) **관계** 산출물 — 1-fact(`domain_fact`)와 disjoint 한 산출물 유형(여러 용어를 함께 비교해야 드러나는 관계). DomainAgent build+maintain owner.

- **위치**: `docs/domain-knowledge/domain/<area>/lexicon.md` (DomainAgent `domain/**` 권한 내 — glob 변경 0). consumer overlay 가 `<area>` 정의 (예: `domain/vocabulary/lexicon.md`).
- **owner write**: DomainAgent 직접. ResearcherAgent `concept/**` 와 disjoint — lexicon 은 `concept/**` 미침범(포인터 cross-ref 만).
- **기계 검증**: `scripts/check-lexicon-drift.sh` (warning-tier) + doc-frontmatter `kind: lexicon_relation` allowlist (`scripts/lib/check_doc_frontmatter.py` KIND_VALID).
- **prior-art (inspiration 인용만, conformance claim 아님)**: ANSI/NISO Z39.19 controlled vocabulary 관계어휘(USE/UF·RT) + ISO 704 concept-oriented terminology. 조항 번호는 추정 — conformance 주장 금지 (ADR-119 hedge).

### lexicon frontmatter (필수)

```yaml
---
kind: lexicon_relation
title: <한 줄 제목 — 예: "<프로젝트> application-BC lexicon">
area: <영역 — overlay에서 정의된 area 중 하나>
topic_slug: lexicon
status: draft | active | deprecated
updated: YYYY-MM-DD
relations:
  - term: <표기>                              # mechanical
    relation: homonym | synonym | antonym     # mechanical (enum)
    conflict_with: <충돌 대상 term>           # relation=homonym/antonym 시 (mechanical)
    usage_citations:                          # 1급 필드 — D5 forcing function (mechanical: presence)
      - "<file:line 또는 동등 — 실 사용처>"   # homonym entry 는 1+ 의무 (semantic 적합성=DomainAgent)
    definition: <의미 정의>                   # semantic
  - <다음 entry ...>
---
```

### lexicon 작성 규칙 (보존 의무)

- **동음이의 2-entry explicit-separate (ADR-091 §결정3)**: 한 entry 에 두 의미를 함께 기술 금지. `relation: homonym` 충돌쌍은 **각각 별 entry** + 상호 `conflict_with` 참조. governance BC glossary 의 Aggregate 2-entry pair 가 살아있는 선례. drift-check collision-candidate 도 이 2-entry 구조를 전제로 surface.
- **D5 forcing function (ADR-091 §결정7 답습)**: 동음이의어(homonym) entry 는 사용처 인용(`usage_citations`, file:line 1+) 의무 — 나열만 금지. drift-check 가 presence 검사 (인용 의미 적합성은 DomainAgent semantic, ADR-119 abstain).
- **BC 분리 (INV-R6, ADR-091 §결정4)**: application-BC lexicon ↔ governance-BC glossary 는 **분리된 controlled vocabulary**. 한쪽이 다른 쪽을 정의하지 않고 cross-ref(link)만 — content 복제 금지.
- **자동 action 0 (I-LEX-2)**: qualifier(예: `data-provenance`/`run-provenance`)는 *권고*. drift-check WARN 해도 자동 rename/리네이밍 강제 0 — 실 리팩터는 설계 lane 결정.

---

## concept-dictionary 산출물 schema (`kind: concept_definition` 재사용) — CFP-2453

개념별 깊이(정의/불변식/위치) 산출물. lexicon(용어 간 관계)과 **다른 추상 레벨** — ISO 704 concept-oriented 정합(개념이 일차 단위, 용어는 표시). **신규 kind 신설 0** — 기존 `kind: concept_definition`(`templates/concept-knowledge.md`) 재사용.

- **위치**: `docs/domain-knowledge/domain/<area>/concept-dictionary.md` (DomainAgent `domain/**` 권한 내).
- **owner = 경로 기반**: `domain/<area>/concept-dictionary.md` (DomainAgent 소유) ↔ `concept/**` 의 동일 kind 파일(ResearcherAgent 소유) = 경로가 owner 결정. kind 재사용은 충돌 0 (kind = frontmatter schema 식별자이지 ownership 선언 아님). DomainAgent 는 `concept/**` narrative content 미침범 (포인터 cross-ref 만).

### concept-dictionary frontmatter (필수 — concept_definition schema)

```yaml
---
kind: concept_definition
title: <한 줄 제목>
slug: concept-dictionary
status: draft | active | deprecated
updated: YYYY-MM-DD
---
```

### concept-dictionary 본문 entry 필드 (개념별)

- `concept` — 개념명 (mechanical)
- `definition` — 의미 정의 (semantic)
- `invariants[]` — 개념 불변식 목록
- `location` — 코드 경로 / bounded context / `concept/**` 심층문서 링크 (셋 다 허용 — ISO 704 concept 속성 관점)
- `lexicon_refs[]` — 개념→용어 방향 참조 (R2 concept-우선 — concept-dictionary 가 lexicon entry 를 참조)
