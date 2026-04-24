# Confluence Story 페이지 구조 템플릿

Jira Story 1건당 Confluence 페이지 1개. 요구사항 접수부터 PR merge까지 모든 컨텍스트·설계·개발 서사가 이 페이지로 누적.

**사용 대상**: DocsAgent (생성·섹션 갱신 단독), 모든 에이전트 (URL + 섹션 번호 참조해 read-only fetch)

**위치**: Consumer overlay가 지정한 Confluence space · `Stories` parent pageId. 제목 `<PROJECT_KEY>-N: <한 줄 요약>`.

**템플릿 복제**: Consumer overlay가 지정한 Story Page 템플릿(pageId)을 복제해 신규 생성.

---

## 라벨 (Confluence page labels)

- `story` 필수
- `<PROJECT_KEY>-N` (Jira key 동기화)
- `status:active` (진행 중) → `status:completed` (PR merged 후)
- 관련 `adr:NNN` (Story 결정이 참조·갱신하는 ADR)

---

## 섹션 구조 (번호 고정 · 누락 섹션 진입 차단)

### §1. 사용자 원문
- Orchestrator가 Jira Story 생성 + Confluence 페이지 초기화 시 verbatim 삽입
- 재작성·요약 금지 (변조 방지)

### §2. 도메인 해석 (DomainAgent)
- 도메인 제약 / 암묵 가정 / 범위 경계 / 우선순위 힌트
- 지식 공백 섹션
- 기존 Domain Knowledge 페이지 참조 목록

**타이밍**: 페이지 생성 시점엔 placeholder (요구사항 레인 진입 전 비어있음). DomainAgent가 Analyst·Researcher와 **병렬 실행** 후 결과 반환하면 RequirementsPL이 DocsAgent 경유로 §2 채움 — 따라서 **Analyst·Researcher는 §2를 입력으로 참조하지 않음** (독립 관점 보장). §5·§6과 같은 사이클에 동시 기록.

### §3. 관련 ADR
- 직접 제약 ADR (verbatim 또는 full 요약)
- 배경 참조 ADR (번호 + 1줄 요약)
- 기존 ADR 갱신·신설 필요 여부

### §4. 관련 코드 경로 + 책임
- 변경 대상 파일·클래스·레이어
- 현재 책임 요약

### §5. 요구사항 확장 해석 (RequirementsAnalyst)
- 유스케이스 / AC / 엣지 케이스 / 제외 범위 / 암묵 가정
- §5.5 "사용자 확인 필요" (blocking wait 항목)

### §6. 외부 지식 배경 (Researcher)
- Researcher 자체 도출 키워드 커버리지 + 출처 URL
- ADR 정합성 점검 결과
- "외부 지식 보강 불필요" 판정 시에도 사유를 명시 (섹션 생략 금지 — 독립 관점 결과 보존)

### §7. 설계 서사 (Architect)
- Change Plan 링크 (`docs/change-plans/<slug>.md`)
- §1 목적 / §3 도입할 설계 / §4 API 계약 / §9 분기 선택 요약 미러링 (5-10줄)
- CodebaseMapper ↔ RefactorAgent 대립 결론

### §8. 개발 서사 (DeveloperPL + 4 Dev)

#### §8.1 Backend 산출물
#### §8.2 Frontend 산출물
#### §8.3 DataEng 산출물
#### §8.4 ServerEng 산출물

#### §8.5 Impl Manifest (파일 단위 매핑표)
[`impl-manifest.md`](impl-manifest.md) 스키마 따름. DocsAgent가 Story 페이지 §8.5에 테이블 기록 + 동시에 Jira sub-task 일괄 생성.

### §9. 품질 게이트 이력

#### §9.0 Clarification 재스폰 이력 (FIX 아님)

PL(RequirementsPL / Architect)이 병렬 서브 에이전트 결과 통합 중 추가 질의를 위해 Orchestrator 경유 재스폰 요청한 이력. FIX 루프(§10)와 구분 — 재스폰은 아직 게이트 실패가 아님.

| # | 시각 | 레인 | 재스폰 대상 | Clarification 사유 | 이전 출력 ref | 결과 |
|---|------|------|-------------|-------------------|---------------|------|
| 1 | ISO8601 | 요구사항 | ResearcherAgent | {PL이 추가 조사 요청한 주제} | §6 initial | §6 보강 |
| 2 | ISO8601 | 설계 | RefactorAgent | {Architect가 특정 제안 재해석 요청} | §7 Change Plan draft v1 | §7 갱신 |

- 같은 에이전트 **2회 한도** — 3회째 필요성 발생 시 사용자 ESCALATE로 전환
- DocsAgent append-only 관리 (행 삭제·수정 금지)

#### §9.1 설계 리뷰 Iteration N
- Claude · Codex severity counts + 주요 findings + DesignReviewPL 판정
- Iteration N마다 append

#### §9.2 구현 리뷰 Iteration N
- 동일 형식

#### §9.3 구현 테스트 레인
- 기능 통과/실패 + 성능 baseline 대비 변동

#### §9.4 보안 테스트 레인
- Claude · Codex severity counts + 주요 findings + SecurityTestPL 판정
- Iteration N마다 append

### §10. FIX Ledger (FIX 카운터 SSOT)

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰 | ... | 설계 | ... | — |
| ... |

DocsAgent가 append-only 관리 (행 삭제·수정 금지). "현재 사이클" count는 RESET 마커 이후 iteration만 합산.

### §11. 참조
- Jira Story URL
- PR URL (merge 후)
- Change Plan 링크
- 관련 ADR 링크

---

## 단계별 갱신 책임

| 단계 | 갱신 섹션 | DocsAgent 액션 |
|------|----------|----------------|
| 요구사항 접수 (Orchestrator) | §1 verbatim 삽입, §2·§5·§6 placeholder | `createConfluencePage(parentId=<STORIES_PARENT_ID>)` 템플릿 복제 |
| 요구사항 병렬 에이전트 개별 완료 (각 에이전트) | 본인 담당 섹션만 독립 기록 — Domain→§2 / Analyst→§5 / Researcher→§6 | 에이전트별 write queue 제출 → DocsAgent drain 시 **섹션별 atomic 갱신** (배치 금지, resume 시 부분 완료 감지를 위해) |
| 요구사항 확정 (RequirementsPLAgent) | §3-4 (공통 입력 미리 fetch된 ADR/코드 경로 반영) + 통합/상충 분석 블록 | `updateConfluencePage` |
| 설계 확정 (ArchitectAgent) | §7 | `updateConfluencePage` |
| 설계 리뷰 iteration (DesignReviewPL) | §9.1 | `updateConfluencePage` |
| 구현 완료 (DeveloperPL) | §8.1-8.4 + §8.5 | `updateConfluencePage` + `createJiraIssue` (sub-task 일괄) |
| 구현 리뷰 iteration (CodeReviewPL) | §9.2 | `updateConfluencePage` |
| 구현 테스트 (Orchestrator) | §9.3 | `updateConfluencePage` |
| 보안 테스트 iteration (SecurityTestPL) | §9.4 | `updateConfluencePage` |
| Clarification 재스폰 (RequirementsPL · Architect) | §9.0 append | `updateConfluencePage` (FIX 라벨 미추가) |
| FIX 루프 | §10 append | `updateConfluencePage` + Jira 라벨 추가 |
| Story 완료 회고 (PMOAgent) | §11 회고 블록 | `updateConfluencePage` |
| 최종 완료 (PR merged) | §11 PR 링크 + 라벨 `status:completed` | `updateConfluencePage` |

---

## 섹션 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `getConfluencePage(pageId=N)` 후 해당 섹션만 참조
- 전체 페이지 읽기는 Architect 설계 진입 1회만 허용 (§1-6 전체 필요)
- 페이지 변경은 **DocsAgent 독점**
