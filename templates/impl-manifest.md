# Impl Manifest 템플릿

구현 레인 완료 시 DeveloperPL이 4 Dev 산출물을 수집해 **파일 단위 매핑표**를 구성. DocsAgent가 Story 페이지 §8.5에 테이블 기록 + 동시에 Jira sub-task 일괄 생성.

**사용 대상**: DeveloperPLAgent (초안 구성), DocsAgent (§8.5 기록 + Jira sub-task 생성), ArchitectAgent (매핑표 감사 입력), CodeReviewPL·SecurityTestPL (§8.5 대비 실제 파일 일치 확인)

---

## Story 페이지 §8.5 테이블 포맷

| 파일 경로 | 변경 유형 | 담당 Agent | Change Plan 매핑 | 라인 수(±) | 비고 |
|-----------|-----------|------------|------------------|------------|------|
| `src/<path>/server.py` | 수정 | BackendDev | §5 항목 2 | +42 -5 | 신규 라우트 2개 |
| `src/<path>/domain/entity.py` | 추가 | BackendDev | §3 도입할 설계 | +120 | 신규 Aggregate |
| `tests/unit/domain/test_entity.py` | 추가 | QADev | §8.1 커버리지 | +85 | Entity 단위 테스트 |
| `deploy/systemd/<service>.service` | 수정 | ServerEng | §5 항목 7 | +3 -1 | 의존성 체인 추가 |

### 컬럼 규격

| 컬럼 | 값 | 비고 |
|------|----|----|
| 파일 경로 | repo root 기준 relative path | backtick 감싸기 |
| 변경 유형 | `추가` / `수정` / `제거` | 단일 값 |
| 담당 Agent | `BackendDev` / `FrontendDev` / `DataEng` / `ServerEng` / `QADev` | 1개 |
| Change Plan 매핑 | `§N 항목 M` 또는 `§N` (섹션 전체) | Change Plan 섹션 번호 |
| 라인 수(±) | `+X` / `-Y` / `+X -Y` | git diff numstat 기준 |
| 비고 | 한 줄 설명 | 선택 |

### 필수 원칙

- **모든 변경 파일 포함** — PR의 git diff 파일 목록과 1:1 일치해야 함
- 누락 시 **CodeReview P0 차단** (§8.5 ↔ 실제 파일 불일치)
- **생성 파일만 있으면 안 됨** — 수정·제거 파일도 전부 기록

---

## Jira sub-task 생성 (DocsAgent 병행)

각 파일 단위로:

```
mcp__atlassian__createJiraIssue(
  issueTypeName="하위 작업",
  parentKey=<Story key>,
  summary="<file path>",
  labels=["impl-manifest", "component:<consumer overlay value>"],
  description=<Change Plan 매핑·담당 Agent·변경 유형·라인 수>
)
```

PR merge 시 GitHub for Jira가 sub-task 자동 완료 전이.

---

## DeveloperPL 초안 구성 절차

```
1. 4 Dev + QADev 완료 보고 수집 (각 Dev의 수정 파일 목록 취합)
2. 각 파일에 대해:
   - git diff --numstat로 라인 수 확인
   - Change Plan §5 변경 계획·§3 도입할 설계·§6 리팩토링 선행 중 해당 항목 매핑
3. 테이블 구성 (위 포맷)
4. Orchestrator에 전달 → DocsAgent가 §8.5 기록 + Jira sub-task 일괄 생성
```

---

## Architect 감사 입력

Impl Manifest는 CodeReview·Architect 감사의 **입력**:

| 감사 항목 | 체크 |
|-----------|------|
| **§8.5 ↔ git diff 일치** | 기록된 파일 = PR 변경 파일 목록 |
| **§8.5 ↔ Change Plan 매핑 타당성** | 각 파일의 "Change Plan 매핑" 컬럼이 §1-10 범위 내 |
| **4 Dev 담당 경로 준수** | Backend가 template/static 수정 없음, Frontend가 server.py 수정 없음 등 |
| **라인 수 합리성** | 계획 대비 과다 (+ 500줄 이상인데 "리팩토링 선행" 매핑 등) 경고 |

불일치 시 DevPL 재지시 → 해당 Dev/QADev 재스폰.
