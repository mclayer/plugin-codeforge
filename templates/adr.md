# ADR (Architecture Decision Record) 템플릿

설계 결정마다 `docs/adr/ADR-NNN-<slug>.md` 파일을 신규 생성. flat 디렉토리 + frontmatter `category:` 필드로 분류. CODEOWNERS가 `docs/adr/**` → architect team 자동 review 강제 → ADR 변경은 Phase 1 PR로 architect 결재 필수.

**사용 대상**: ArchitectAgent (DocsAgent 경유 의뢰), PMOAgent (ADR 후보 발의 — `status=Proposed` draft), DocsAgent (생성·갱신 단독 실행)

---

## 파일 메타

- **위치**: `docs/adr/ADR-NNN-<slug>.md` (flat). NNN = 기존 최대 + 1, slug = kebab-case 결정 요약
- **frontmatter**: `category:` 필수 (Architecture / Data & Storage / Infrastructure / Team & Process / UX / `<domain-category>`). status·date·related_files도 frontmatter
- **신규 ADR 없이 기존 ADR 결정 변경 금지** — 변경하려면 새 ADR에서 이전 ADR을 supersede

---

## 파일 frontmatter (필수)

```yaml
---
adr_number: NNN
title: <결정>
status: Proposed | Accepted | Deprecated | Superseded-by-ADR-MMM
category: Architecture | Data & Storage | Infrastructure | Team & Process | UX | <domain-category>
date: YYYY-MM-DD
related_files:
  - path/to/file.ext
  - path/to/other.ext
related_stories:
  - <STORY_KEY_PREFIX>-N
  - <STORY_KEY_PREFIX>-M
---
```

---

## 본문 섹션 (고정 순서)

```markdown
# ADR-NNN: <결정>

## 상태
`Proposed` / `Accepted` / `Deprecated` / `Superseded by ADR-MMM`
(하단 "Superseded by ..." 명시 시 새 ADR 파일 링크 추가)

## 컨텍스트
결정의 배경 · 문제 정의 · 제약 조건. Why this decision is needed now.

## 결정
구체 결정안. **동사·능동태**로 서술 ("X를 도입한다" / "Y를 금지한다"). 모호한 표현(고려·지향) 금지.

## 결과
결정의 긍정·부정·trade-off. 영향 받는 코드·레이어·운영 경계.

## 다이어그램 (선택)

\`\`\`mermaid
graph LR
    Client --> API
    API --> Service
    Service --> Port
    Port --> Adapter
\`\`\`

## 관련 파일
변경 또는 참조되는 파일 경로. Consumer project 기준 relative path.
```

---

## DocsAgent 작성 절차

```
1. 카테고리 판정 — 결정 성격에 따라 Architecture / Data & Storage / Infrastructure / Team & Process / UX / <domain> 중 선택
2. 기존 최대 ADR 번호 조회: `Glob(docs/adr/ADR-*.md)` 후 max + 1
3. slug 결정 (kebab-case, 결정 요약 짧게)
4. `Write(docs/adr/ADR-NNN-<slug>.md)` 호출, frontmatter + 본문 작성
5. Phase 1 PR에 commit (architect team CODEOWNERS auto-review)
6. 관련 Story file §3 "관련 ADR" 항목에 링크 추가 — `Edit(docs/stories/<KEY>.md)`
```

## PMOAgent ADR 후보 발의

패턴 분석에서 "설계 지침 부재" 반복 감지 시:

```markdown
---
type: adr-draft
category: Architecture | Data & Storage | ...
title: "ADR-NNN: <제안 결정>"
trigger: "최근 N Story에서 반복 발견된 {패턴}"
---

## 배경
{반복된 FIX 사례 인용 — Story 키·iteration·finding}

## 문제
{지침·패턴 부재로 인한 설계 재발명 비용}

## 제안 결정
{구체 결정안}

## 예상 결과
...
```

DocsAgent가 write queue 파일을 drain → `Write(docs/adr/ADR-NNN-<slug>.md)` 호출, frontmatter `status: Proposed`로 commit. 다음 Story 설계 진입 시 Architect가 검토해 `status: Accepted` 전이 또는 기각.
