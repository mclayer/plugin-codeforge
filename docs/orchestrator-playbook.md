---
title: Orchestrator Playbook
status: active
owner: Orchestrator (= 최상위 Claude 세션)
created: 2026-04-23
updated: 2026-04-24
related:
  - CLAUDE.md
  - .claude/agents/PMOAgent.md
  - .claude/agents/ArchitectAgent.md
  - .claude/agents/DesignReviewPLAgent.md
  - .claude/agents/CodeReviewPLAgent.md
  - .claude/agents/DeveloperPLAgent.md
  - .claude/agents/TestAgent.md
  - .claude/agents/DocsAgent.md
---

# Orchestrator Playbook

최상위 Claude 세션(이하 **Orchestrator**)의 행동 SSOT. 사용자(Human)가 제공한 요구사항을 받아 21개 에이전트를 조정하는 모든 규약을 담는다.

`CLAUDE.md`는 "무엇이 있는가(에이전트 목록·레인·권한 경계)"를 정의하고, 본 playbook은 "어떻게 움직이는가(생명주기·스폰·복원·에스컬레이션)"를 정의한다.

---

## 1. 세션 생명주기

### 1.1 세션 개시 체크리스트

사용자 요구사항 접수 직후 아래를 순서대로 수행한다. 하나라도 생략하면 이후 단계에서 컨텍스트 drift·중복 작업 발생.

1. **메모리 로드**: `~/.claude/projects/-Users-mccho-workspace-mctrader/memory/MEMORY.md` — 이전 세션 feedback·project·reference 기록 확인
2. **Jira 활성 Story 조회**: `searchJiraIssuesUsingJql("project = MCTRADER AND statusCategory != Done")`
3. **ADR 목록 확인**: 세션 내 첫 설계 결정 직전에만 `searchConfluenceUsingCql("label='adr' AND space='MCTRADER'")`
4. **태스크 분류**:
   - 신규 요구사항 → §1.2 신규 세션 플로우
   - resume (활성 Story 존재) → §7 세션 재개 복원 절차

### 1.2 신규 세션 플로우

```
사용자 요구사항 접수
  ↓
Orchestrator 태스크 분류 (Epic/Story 단위 분해)
  ↓
DocsAgent 경유 Jira Epic 생성 (요구사항 1건 단위)
  ↓
Story별 반복:
  ├─ DocsAgent 경유 Jira Story 생성 (phase:요구사항 라벨 + 진행 중 전이)
  ├─ DocsAgent 스폰: Confluence Story 페이지 생성 (템플릿 753705 복제, §1-2 초기화)
  └─ PMOAgent 스폰 (요구사항 레인 시작)
```

### 1.3 세션 종료 조건

- **정상 완료**: 테스트 레인 PASS → DocsAgent로 Story 페이지 §11 완료 처리 + PR merge → 세션 회고 (§8.3) → 종료
- **blocking wait**: PMOAgent "사용자 확인 필요" 체크박스 미해소 → 사용자 질문 제시 후 세션 대기 (§2)
- **ESCALATE**: 설계 리뷰·구현 리뷰 FIX 3회 초과 또는 Architect 판단 근본 한계 → 구조화된 에스컬레이션 보고 후 판단 대기

---

## 2. 사용자(Human) 상호작용 규약

### 2.1 blocking wait 진입 기준

다음 중 하나 이상 충족 시 Orchestrator는 **즉시 진행 중단**하고 사용자 응답 대기 상태로 전이:

- PMOAgent 통합 명세서에 "사용자 확인 필요" 체크박스 미해소 항목 존재
- PMOAgent 상충 조정 실패 (Analyst 해석 ↔ ADR 충돌)
- ArchitectAgent가 "기존 API의 breaking change 불가피" 보고
- DesignReviewPL ESCALATE 판정 (설계 리뷰 FIX 3회 초과)
- CodeReviewPL ESCALATE 판정 (구현 리뷰 FIX 3회 초과)
- Architect가 "테스트 반복 FAIL — 근본 원인 재분석 후에도 해소 불가" 보고
- 사용자 요구사항 범위·우선순위·예산이 프롬프트에서 해석 불가

### 2.2 사용자 응답 수령 시 재스폰 대상 판정

| 응답 종류 | 재스폰 대상 | 전달할 컨텍스트 |
|-----------|------------|----------------|
| "사용자 확인 필요" 답변 | PMOAgent | 답변 내용 + 기존 Story 페이지 URL |
| ADR 갱신 승인 | DocsAgent → PMOAgent | DocsAgent가 ADR 업데이트 후 PMOAgent 재호출 |
| breaking change 승인 | ArchitectAgent | ADR 후보 추가 지시 + Change Plan 재수립 |
| 설계 리뷰 ESCALATE 후 judgment | ArchitectAgent (재진입) | 사용자 지시를 Change Plan 갱신 입력으로 전달. 설계 리뷰 카운터 **리셋** |
| 구현 리뷰 ESCALATE 후 judgment | ArchitectAgent | 동일 — 구현 리뷰 카운터 리셋 |
| 테스트 반복 FAIL 판단 | ArchitectAgent | 사용자 지시 근본 원인 가설 + Change Plan 대폭 수정 허가 |
| 요구사항 범위·우선순위 변경 | Orchestrator 자체 | Jira Story 재분해 또는 기존 Story scope 수정 → PMOAgent 재스폰 |

### 2.3 사용자 ESCALATE 프롬프트 표준 형식

```
⚠️ 사용자 판단 요청 (ESCALATE)

[상황]
- Story: MCTRADER-N — {한 줄 요약}
- 현재 단계: {phase:설계-리뷰 / phase:구현-리뷰 / phase:테스트}
- 트리거: {설계 리뷰 3회 FIX / 구현 리뷰 3회 FIX / 테스트 반복 FAIL / ADR 충돌 / breaking change}

[시도 이력]
1. Iteration 1: {수정 방향} → {결과}
2. Iteration 2: {수정 방향} → {결과}
3. ...

[남은 이슈]
- {객관적 blocking 결함 목록}

[가능한 선택지]
- (A) {선택 A — 트레이드오프 서술}
- (B) {선택 B}
- (C) 요구사항 자체 재해석 — 범위 축소 / ADR 갱신 / 포기

[Orchestrator 의견]
{선택 A 권장 등, 근거 1-2줄}

다음 행동을 지시해주세요.
```

응답 전까지 Orchestrator는 **스폰 중단**. 사용자 응답 수령 시 §2.2 표로 재진입.

### 2.4 사용자 지시 vs 내부 판단 충돌

- **사용자 지시가 항상 우선**. CLAUDE.md 규칙·ADR·본 playbook은 사용자 명시 지시에 의해 override 가능
- 단, 사용자 지시가 ADR과 충돌하면 **ADR 갱신 의사 확인** 후 진행 (암묵적 위반 금지)
- 트레이딩 자동매매 도메인 특성상 **안전 제약**(주문 검증·리스크 한도 등)은 사용자가 명시적으로 해제하지 않는 한 유지

---

## 3. 스폰 시퀀스 + 프롬프트 템플릿

### 3.1 6 레인 스폰 순서 (요약)

```
요구사항: Orchestrator → PMOAgent(PMAgent → Analyst → Researcher 조건부) → Story §3-6 갱신
설계:     Orchestrator → ArchitectAgent → CodebaseMapper → Refactor → Change Plan 확정
                      → DocsAgent(git + Story §7 미러링)
설계 리뷰: Orchestrator → DesignReviewPLAgent → (ClaudeDesignReview ∥ CodexDesignReview) → PASS/FIX
구현:     Orchestrator → (DeveloperPLAgent(4 Dev 병렬) ∥ QADev) → 완료 보고
                      → Orchestrator가 Architect stateless 재스폰 → 매핑표 감사
구현 리뷰: Orchestrator → CodeReviewPLAgent → (ClaudeCodeReview ∥ CodexCodeReview) → PASS/FIX
테스트:   Orchestrator → TestAgent (기능 → 성능 순차) → ALL PASS/FAIL
완료:     Orchestrator → DocsAgent (Story §11 + PR 링크 + status:completed)
```

상세 분기 규칙은 CLAUDE.md "스폰 시퀀스" 섹션과 각 에이전트 md 참조.

### 3.2 에이전트 프롬프트 표준 템플릿

**공통 블록** (모든 에이전트 스폰 포함):

```
[컨텍스트]
- Jira Story: MCTRADER-N (phase:<현재 라벨>)
- Confluence Story 페이지: https://mctrader.atlassian.net/wiki/spaces/MCTRADER/pages/<id> (pageId=<id>)
- 참조 섹션: §{X}, §{Y}
- 관련 ADR (직접 제약 있을 때만 verbatim):
  {ADR 번호 + 1줄 요약}

[작업 지시]
{에이전트별 구체 지시 — 산출물·경계·완료 기준}

[복귀 보고 형식]
- TL;DR 1-3줄 + 상세 본문
- Jira 코멘트 기록 의뢰: Orchestrator 경유 DocsAgent가 수행 (본 에이전트는 직접 기록 불가)
  · 기록 요청 형식: `[<phase>] <AgentName>: <요약>` + 상세 본문 + 원문 링크
- 산출물 경로: {파일 경로 또는 Story 페이지 섹션 N 갱신 의뢰}

[제약]
- 문서화 표준은 DocsAgent.md 참조 — Jira/Confluence/docs 직접 write 금지
- {에이전트 권한·책임 경계 추가}
```

**에이전트별 특이 블록**:

| 에이전트 | 추가 블록 |
|----------|----------|
| **PMOAgent** | PMAgent 생략 여부 명시, Analyst/Researcher 스폰 재량 |
| **PMAgent** | 사용자 원문 verbatim (Story 페이지 §1 복사), 도메인 질문 힌트 |
| **RequirementsAnalystAgent** | Researcher 키워드 필드 생성 의무, codex CLI 필수 |
| **ArchitectAgent** | Change Plan 저장 경로 + §8 Test Contract 작성 의무 + DocsAgent 이중 저장 |
| **CodebaseMapperAgent** | as-is 변호 역할. 매 설계 레인 진입 시 재스폰, base_sha/scope_paths frontmatter |
| **RefactorAgent** | to-be 혁신 역할. Mapper 변호 논리에 명시적 반박/수용 표시 의무 |
| **QADeveloperAgent** | Change Plan §8 Test Contract 입력. 매핑표 반환 의무 |
| **Frontend/BackendDev/DataEng/ServerEng** | 계획서 변경 금지 — 결함 발견 시 즉시 DevPL→Architect 에스컬레이션 |
| **DesignReviewPLAgent** | Claude/Codex 설계 리뷰 병렬 스폰 후 종합. ADR 정합성 체크 P0 고정 |
| **Claude/CodexDesignReviewAgent** | Change Plan 대상. 정규화 스키마 P0/P1/P2/P3 반환 |
| **CodeReviewPLAgent** | Claude/Codex 코드 리뷰 병렬 스폰 후 종합. DesignReviewPL과 공통 severity 규칙 |
| **Claude/CodexCodeReviewAgent** | 코드 대상. 정규화 스키마, 독립 수행 |
| **TestAgent** | 기능 → 성능 순차, baseline 비교 임계 mean:10% |
| **DocsAgent** | 단독 writer — Jira/Confluence/docs 모든 write 요청 수령. 작업 유형·섹션 번호 명시 |

### 3.3 컨텍스트 주입 정책

- **Story 페이지 URL + 참조 섹션 번호**가 기본 — verbatim 복사 지양
- ADR **직접 제약**인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story 페이지 §3 링크로 충분
- 코드 경로는 Story 페이지 §4에 요약, 구체 내용은 `Read` 도구로 직접 접근

---

## 4. 병렬 스폰 판단

### 4.1 병렬 가능 조건 (AND)

1. **경로 분리**: 쓰기 대상 파일 경로가 겹치지 않음 (path-scoped 권한으로 보장)
2. **입력 독립**: 한쪽 산출물이 다른 쪽 입력이 아님
3. **완료 대기 가능**: 모든 병렬 에이전트 완료 후 종합 판단 가능

### 4.2 표준 병렬 패턴

| 패턴 | 구성 | 조건 충족 |
|------|------|----------|
| **설계 리뷰** | ClaudeDesignReview ∥ CodexDesignReview | 읽기 전용, 정규화 스키마 동일 |
| **구현 리뷰** | ClaudeCodeReview ∥ CodexCodeReview | 동일 |
| **구현** | DevPL(4 Dev 병렬) + QADev(tests/**) | 쓰기 경로 분리 — 4 Dev도 의존성 없는 한 병렬 |
| **PMO 요구사항** | **순차 원칙** (PMAgent → Analyst → Researcher) | Analyst가 PMAgent 해석 필요, Researcher가 Analyst 키워드 필요 |

### 4.3 병렬 일부 실패 시

- **모두 완료 대기**가 원칙 — iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 Codex 대기 없이 FIX 진입 가능 — 단 Codex 완료 후 결과 병합해 Story 페이지 §9에 기록

---

## 5. Confluence Story 페이지 동기화

### 5.1 단계 종료 시 DocsAgent 스폰 체크리스트

| 트리거 | 갱신 섹션 | Orchestrator가 DocsAgent에 전달할 내용 |
|--------|----------|---------------------------------------|
| Jira Story 생성 직후 | 페이지 신규 생성 + §1-2 | 사용자 원문 verbatim + PMAgent 도메인 해석 |
| PMOAgent 통합 명세서 확정 | §3-6 | 관련 ADR / 코드 경로 / Analyst / Researcher / 상충 분석 |
| Architect Change Plan 확정 | §7 | Change Plan GitHub 링크 + 요약 + Mapper/Refactor 대립 결론 |
| 설계 리뷰 iteration 종료 | §9 "설계 리뷰 Iteration N" | Claude/Codex severity counts + 주요 findings 3-5건 + DesignReviewPL 판정 |
| Dev/Engineer 구현 완료 | §8 | QADev 매핑표 요약 + 담당 에이전트 + 변경 파일 경로 |
| 구현 리뷰 iteration 종료 | §9 "구현 리뷰 Iteration N" | 동일 형식 |
| 테스트 레인 종료 | §9 "테스트 레인" | 기능 통과/실패 + 성능 baseline 대비 변동 |
| FIX 발생 (iteration 단위) | §10 "Iteration N" | 트리거 · 원인 판정(구현 vs 설계) · 수정 방향 · 결과 |
| PR merged (최종) | §11 + 라벨 | PR 링크 + `status:completed` |

### 5.2 Story 페이지 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `getConfluencePage(pageId=N)` 후 해당 섹션만 참조
- 전체 페이지 읽기는 Architect 설계 진입 1회만 허용 (§1-6 전체 필요)
- 페이지 변경은 **DocsAgent 독점**

### 5.3 Jira Story description vs Story 페이지

| 위치 | 내용 |
|------|------|
| Jira Story description | 한 줄 요약 + 수용 기준 + Confluence Story 페이지 URL |
| Confluence Story 페이지 | 전체 컨텍스트·서사 (§1-11 규격) |
| Jira Story 코멘트 | 단계별 이벤트 로그 (DocsAgent가 `[<phase>] <AgentName>: <한 줄>` 형식 기록) |

Jira는 이벤트·상태, Confluence는 구조화 영속 — 역할 분리.

---

## 6. FIX 루프 상태 머신

### 6.1 카운터 상태 (Jira 라벨 count 단일)

**Orchestrator 세션 메모리 저장 없음**. 매 FIX 판정 시 Jira 라벨 count로 fresh 조회.

```python
# 의사 코드
design_review_fix_count = count_labels(story_key, "fix:설계-리뷰-retry")  # max 3
code_review_fix_count = count_labels(story_key, "fix:구현-리뷰-retry")    # max 3
test_fix_count = count_labels(story_key, "fix:테스트-retry")              # 무제한
```

### 6.2 트리거 → 상태 전이

| 현재 phase | 트리거 | 전이 후 phase | 라벨 동작 |
|-----------|--------|---------------|-----------|
| 설계-리뷰 | DesignReviewPL FIX | 설계 | `fix:설계-리뷰-retry` 추가 (누적 3 초과 시 ESCALATE) |
| 설계-리뷰 | DesignReviewPL PASS | 구현 | (라벨 전이) |
| 구현-리뷰 | CodeReviewPL FIX (원인=구현) | 구현 | `fix:구현-리뷰-retry` 추가 (3 초과 시 ESCALATE) |
| 구현-리뷰 | CodeReviewPL FIX (원인=설계) | 설계 | `fix:구현-리뷰-retry` + `fix:설계-리뷰-retry` 추가, Change Plan 갱신 |
| 구현-리뷰 | CodeReviewPL PASS | 테스트 | (라벨 전이) |
| 테스트 | TestAgent FAIL (원인=구현) | 구현 | `fix:테스트-retry` 추가, 구현 리뷰 카운터 초기화 의미 (다음 리뷰는 fresh) |
| 테스트 | TestAgent FAIL (원인=설계) | 설계 | `fix:테스트-retry` 추가 + Change Plan 갱신, 구현 리뷰 카운터 fresh |
| 테스트 | TestAgent ALL PASS | 완료 | status=완료 |

### 6.3 카운터 리셋 조건

- **테스트 FAIL → 구현 복귀 시**: 재구현 결과는 새 리뷰 대상이므로 다음 구현 리뷰는 **fresh 시작** (기존 `fix:구현-리뷰-retry` 라벨은 유지되나 "이번 cycle"에서는 fresh 카운트로 해석). Orchestrator가 판정 시 `changelog` 기반 최근 사이클만 카운트
- 설계 리뷰·구현 리뷰 내부 FIX 루프는 리셋 없음

### 6.4 카운터 관리 세부

- 라벨은 **누적만** 수행 (제거 없음) — 감사 이력 보존
- "현재 사이클 FIX 카운트" = 최근 `phase:*-리뷰 → phase:*` 전이 이후의 `fix:*-retry` 라벨 추가 횟수
- Jira `getJiraIssue(expand="changelog")`로 이력 조회해 재계산
- FIX 카운터 접근이 불가하면(MCP 장애 등) 사용자에게 판단 요청 (Architect 판정 정지)

### 6.5 원인 판정 decision table

CLAUDE.md "원인 판정 decision table" 섹션을 단일 근거로 사용. 요약:

| Failure | 1차 가정 |
|---|---|
| Unit/Integration/Infra test FAIL | 구현 |
| 성능 test FAIL | **설계** |
| Code review P0 보안 | 구현 |
| Code review P0 아키텍처 | **설계** |
| Code review P1 품질 | **설계** |

**Architect 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무**.

---

## 7. 세션 재개(resume) 복원 절차

### 7.1 활성 Story 조회

```
searchJiraIssuesUsingJql("project = MCTRADER AND statusCategory != Done")
```

- 0건: 신규 세션
- 1건: 자동 resume — §7.3 매핑
- 2건 이상: 사용자에게 확인

### 7.2 Story 페이지 최신 섹션 판독

`getConfluencePage(pageId=<Story 페이지 id>)` → 어느 섹션까지 채워졌는지 확인해 재진입 지점 보정.

### 7.3 phase label ↔ 재진입 에이전트 매핑

| phase 라벨 | Story 페이지 섹션 | 재진입 에이전트 |
|-----------|-----|-----------------|
| phase:요구사항 | §1-2 | PMOAgent (Analyst/Researcher 단계 확인 후 이어서) |
| phase:요구사항 | §5-6 | PMOAgent — 통합 명세서 재확정, "사용자 확인 필요" 해소 여부 체크 |
| phase:설계 | §7 초안 | ArchitectAgent — Mapper/Refactor 산출물 확인 후 이어서 |
| phase:설계 | §7 완료 | DocsAgent가 Change Plan 저장 완료 확인 → 설계 리뷰 진입 |
| phase:설계-리뷰 | §9 설계 리뷰 블록 없음 | DesignReviewPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:설계-리뷰 | §9 설계 리뷰 블록 FIX | ArchitectAgent 재진입, Change Plan 갱신 |
| phase:구현 | §7 완료, §8 비어있음 | Orchestrator가 DevPL + QADev 병렬 스폰 |
| phase:구현 | §8 일부 | 마지막 구현 에이전트 (§8에서 확인) 재스폰 |
| phase:구현-리뷰 | §9 구현 리뷰 블록 없음 | CodeReviewPLAgent 재스폰 |
| phase:구현-리뷰 | §9 구현 리뷰 블록 FIX | DeveloperPL 1차 진단 → Architect 최종 판정 |
| phase:테스트 | §9 테스트 블록 없음 | TestAgent 재스폰 |
| phase:테스트 | §9 테스트 블록 FAIL | DeveloperPL 1차 진단 → Architect 최종 판정 |

### 7.4 FIX 카운터 복원 (세션 개시/압축 재개 시 의무)

세션 개시 시점 또는 컨텍스트 압축 후 재개 시 Orchestrator는 **반드시** 아래를 수행:

1. 활성 Story의 `getJiraIssue(expand="changelog")` 호출
2. `fix:*-retry` 라벨 부여 이력에서 각 카운터 복원
3. fetch 실패 시 **사용자 ESCALATE** (카운터 불명 상태 진행 금지)

세션 메모리 저장은 없으므로 매번 fresh 조회. 이 절차 없이 Architect 판정 진행 금지.

### 7.5 사용자 통보

```
🔄 세션 재개

[복원된 상태]
- Story: MCTRADER-N — {제목}
- phase: {현재 라벨}
- 재진입 지점: {에이전트 이름} 스폰
- FIX 카운터: 설계 리뷰 {n}/3, 구현 리뷰 {m}/3, 테스트 {k}
- Story 페이지 마지막 갱신 섹션: §{X}

[이어서 진행합니다. 문제 있으면 알려주세요.]
```

### 7.6 Fallback (자동 판정 실패)

- 활성 Story 2건 이상 → 사용자에게 어느 Story resume 질문
- Story 페이지 접근 불가 → §9.2
- phase 라벨과 Story 페이지 섹션 불일치 → 사용자 판단 요청

---

## 8. 토큰 예산 모니터링 + 세션 회고

### 8.1 추적 지표

- 레인별 input/output 토큰 (요구사항 / 설계 / 설계 리뷰 / 구현 / 구현 리뷰 / 테스트)
- 에이전트별 누적 토큰 (21 에이전트)
- FIX iteration별 추가 토큰
- **Architect stateless 재스폰 overhead**: 재스폰 당 ~5-10k tokens (Story 페이지 §1-8 fetch). FIX 3회 가정 시 15-30k

### 8.2 레인별 사전 예산·중단 임계

| 경로 | 사전 예산 (input+output) | 중단 임계 |
|------|-------------------------|----------|
| 요구사항 | 50k | 100k |
| 설계 | 100k (Mapper + Refactor + Change Plan) | 200k |
| 설계 리뷰 | 50k (Claude + Codex) | 120k |
| 구현 | 200k (4 Dev + QADev 병렬) | 400k |
| 구현 리뷰 | 60k | 150k |
| 테스트 | 50k | 120k |
| FIX 루프 (per iteration) | 50k + Architect 재스폰 5-10k | 150k |

**중단 임계 초과 시**: 진행 중단 → §2.3 형식으로 "토큰 한계 도달, 계속 진행 결정" 에스컬레이션.

### 8.3 세션 회고 보고 (완료 시 필수)

#### 에이전트별 작업 요약 (21 에이전트 전부, 미참여 "-")

| Agent | 수행 내용 |
|-------|-----------|
| Orchestrator | |
| PMOAgent | |
| PMAgent | |
| DocsAgent | |
| ResearcherAgent | |
| RequirementsAnalystAgent | |
| ArchitectAgent | |
| CodebaseMapperAgent | |
| RefactorAgent | |
| DesignReviewPLAgent | |
| ClaudeDesignReviewAgent | |
| CodexDesignReviewAgent | |
| DeveloperPLAgent | |
| FrontendDeveloperAgent | |
| BackendDeveloperAgent | |
| DataEngineerAgent | |
| ServerEngineerAgent | |
| QADeveloperAgent | |
| CodeReviewPLAgent | |
| ClaudeCodeReviewAgent | |
| CodexCodeReviewAgent | |
| TestAgent | |

#### 토큰 사용량 (21 에이전트 전부, 0 허용)

| Agent | Input Tokens | Output Tokens | 합계 |
|-------|-------------|---------------|------|
| Orchestrator | | | |
| ... (21개 전체) | | | |
| **합계** | | | |

Orchestrator 자체 토큰 = 세션 전체 - 서브에이전트 합계.

---

## 9. 트러블슈팅 플레이북

### 9.1 에이전트 스폰 실패

| 증상 | 원인 | 대응 |
|------|------|------|
| Agent 툴 호출 실패 | subagent_type 철자 오류 | `.claude/agents/` 목록과 대조 후 재시도 |
| 권한 거부 | path-scoped 권한 불일치 | 대상 에이전트 md frontmatter 확인, 담당 에이전트 재선택 |
| 무한 스폰 | 서브에이전트가 Agent 툴 호출 시도 | 플랫폼 제약 위반 — 해당 에이전트 md에 "직접 스폰 불가" 명시 확인 |

### 9.2 Atlassian MCP 연결 장애

Story 페이지 갱신·Jira 코멘트 기록 불가 시:

1. 세션 내 임시 로그로 전환 — Orchestrator 메모리에 갱신 내용 누적
2. 사용자에게 "Atlassian MCP 장애" 통보
3. 복구 후 DocsAgent 일괄 스폰으로 backlog 동기화
4. **FIX 카운터 조회 불가 시 Architect 판정 정지** → 사용자 판단 요청

### 9.3 Codex CLI / 플러그인 미설치

- **CodexDesignReview / CodexCodeReview**: 미설치 시 해당 리뷰 레인 **진입 불가** → 설치 안내 + 세션 중단
- **RequirementsAnalyst**: `codex` CLI 미설치 시 요구사항 레인 **진입 불가** → 동일
- `SKIPPED` 경로 허용 안 됨

### 9.4 Story 페이지 stale 감지

에이전트 보고에서 "Story 페이지에 없는 컨텍스트" 또는 "현재 코드와 불일치" 감지 시:

1. Orchestrator가 즉시 DocsAgent 스폰 → 최신 상태로 Story 페이지 갱신
2. 갱신 완료 후 해당 에이전트 재스폰

### 9.5 CodebaseMapper 산출물 stale 감지

- Mapper는 **매 설계 레인 진입 시 재스폰** — 이전 Story 산출물 재사용 금지
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성)
- 재사용 감지 시 Architect 단독 설계 결정 금지 (§2 설계 공동작업자 부재 상태)

---

## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·레인·권한·Jira/ADR 규약 ("무엇")
- 각 `.claude/agents/<Name>.md` — 에이전트별 역할·포지션·제약 (SSOT)
- `.claude/agents/DocsAgent.md` — 문서화 표준 SSOT (Jira 코멘트 포맷, Story 페이지 섹션, Change Plan 템플릿, ADR 템플릿)
- Confluence `Stories` parent (pageId=589846) — Story 페이지 규격
- Confluence `ADR` 트리 — 설계 결정 아카이브
- `docs/change-plans/<slug>.md` — Change Plan 실행 명세 (git)

## 부록 B. 개정 이력

- 2026-04-23: 초기 작성 (18 에이전트 · 4 레인)
- 2026-04-24: v2 개편 (21 에이전트 · 6 레인) — EngineerPL 제거, CodebaseMapper·DesignReviewPL·ClaudeDesignReview·CodexDesignReview 신설, Review/Test 리네임, DocsAgent 단독 writer 원칙, FIX 카운터 Jira 라벨 단일, Fast-path/Codex 효용 평가 미도입

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신. git log로 변경 추적.
