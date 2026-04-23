# GitLab → GitHub + Atlassian 이관 설계

**Date**: 2026-04-23
**Status**: Draft (spec 리뷰 대기)
**Scope**: 코드 호스팅·이슈·ADR·문서 전체 플랫폼 이관

## 1. 타깃 아키텍처

| 도구 | 용도 | 식별자 |
|---|---|---|
| GitHub (private org) | 코드 + PR 워크플로 | `mctrader/mctrader` |
| Jira Cloud | 운영 이슈 (bugs, 기능 요청) | project key `MCTR` |
| Confluence Cloud | ADR + 도메인 문서 | space key `MCTRADER` |
| GitLab (아카이브) | 이관 전 이력 참조 | `mctrader1/mctrader` (read-only archived) |

**레포 내 유지**: `docs/change-plans/` (PR·설계 계획과 1:1 매핑되므로 Git-versioned 유지)

## 2. 결정 요약

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| D1 | 플랫폼 분담 | GitHub=코드/PR · Jira=이슈 · Confluence=ADR+문서 | 각 도구의 본래 강점에 정합 |
| D2 | Atlassian 준비 | 기존 프로젝트·스페이스 사용 | 신규 생성 공수 불필요 |
| D3 | ADR 위치 | Confluence 페이지 (Jira 아님) | ADR은 불변 결정 문서 — 티켓 아님 |
| D4 | ADR 구조 | 도메인 카테고리 계층 | 탐색성·도메인 분리 |
| D5 | 카테고리 수 | 6개 | Team&Process / Architecture / Data&Storage / Infrastructure / Dashboard&UX / Trading Strategy |
| D6 | Cutover | 단계적 순차 (단일 세션) | 중간 상태 관찰·롤백 용이 |
| D7 | docs 분할 | change-plans=레포 · bugs=Jira · guides+api=Confluence | 각 콘텐츠 성격에 정합 |
| D8 | GitHub | Organization / private | 향후 협업 전제 |
| D9 | 실행 방식 | MCP 직접 호출 (Approach 3) | 대화형 검증 가능, 스크립트 유지 부담 없음 |
| D10 | GitLab 사후 | Read-only archive | 이력 보존 + dual-source 혼동 방지 |

## 3. Confluence 구조

### 3.1 ADR 페이지 계층
```
Space: MCTRADER
 └── ADR (루트 페이지, 인덱스 + Page Properties Report 매크로)
      ├── Team & Process
      │    ├── ADR-014b: 에이전트 팀 구조 재편 — Developer 계열 분리
      │    ├── ADR-016: TesterAgent 신설 및 자동 디버그 루프
      │    ├── ADR-020: TDD 병렬 구현 + 순차 품질 게이트
      │    └── ADR-021: 요건 단계 도입 — PMOAgent + RequirementsAnalyst
      ├── Architecture
      │    ├── ADR-001: Hexagonal Architecture
      │    └── ADR-009: QueuePositionModel lifecycle 포트 공식화
      ├── Data & Storage
      │    ├── ADR-002: OrderBook Diff-only 저장
      │    └── ADR-003: Parquet + DuckDB 채택
      ├── Infrastructure
      │    ├── ADR-008: Linux 단일 서버, systemd 프로세스 관리
      │    └── ADR-012: Collector 수명주기 — collectorctl + systemd/launchd
      ├── Dashboard & UX
      │    ├── ADR-010: Dashboard Web Interface (FastAPI + Jinja2)
      │    ├── ADR-011: 서버사이드 타임존 변환
      │    ├── ADR-014a: 시각화 뷰 레이어 — Ladder/Tape/Imbalance
      │    ├── ADR-017: Dashboard DuckDB Connection
      │    ├── ADR-018: Dashboard Cache Strategy
      │    └── ADR-019: Orderbook Snapshot Lookback
      └── Trading Strategy
           ├── ADR-004: 백테스트 우선 개발 전략
           ├── ADR-005: Queue Position Model
           ├── ADR-006: Bithumb 우선 연동, 멀티 거래소 추상화
           ├── ADR-007: 틱띠기 — OrderBook Imbalance 기반
           └── ADR-013: 백테스트 진행률 추적 패턴
```

**ADR-014 중복 처리**: 현재 GitLab에 "ADR-014" 두 건 존재. 이관 시 `ADR-014a` / `ADR-014b`로 분리 (번호 공백 ADR-015는 그대로 둠 — 이력 그대로 보존).

### 3.2 Page Properties 스키마
각 ADR 페이지 상단에 Confluence `{page-properties}` 매크로:

| Key | 예시 값 |
|---|---|
| 번호 | `ADR-017` |
| 상태 | `Accepted` / `Superseded by ADR-NNN` |
| 카테고리 | `Dashboard & UX` |
| 결정일 | `2025-01-15` |
| 관련 파일 | `src/mctrader/dashboard/duckdb_layer.py` (Wiki 링크) |
| Supersedes | `ADR-005` (해당 시) |

루트 "ADR" 페이지에 `{page-properties-report}` 매크로로 자동 테이블 생성.

### 3.3 Mermaid 변환
GitLab 이슈 본문의 ` ```mermaid ` 코드블록 → Confluence `{mermaid}` 매크로. 본문 구조(`## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램 / ## 관련 파일`) 유지.

### 3.4 guides + api 페이지
```
Space: MCTRADER
 ├── Guides
 │    ├── Config Reference
 │    ├── Dashboard Collector Data
 │    ├── Known Issues
 │    ├── Orderbook/Trade Visualization Spec
 │    └── Running Services
 └── API Reference
      └── Bithumb WebSocket API
```

## 4. Jira 구조 (bugs)

### 4.1 이슈 표현
- Project key: `MCTR`
- Issue Type: `Bug`
- Label: `migrated-from-repo`
- 필드 매핑 (`docs/bugs/*.md` → Jira):

| `.md` 요소 | Jira 필드 |
|---|---|
| 파일명 (예: `bug-collector-sighup-nohup.md`) | Summary (prefix 제거) |
| `## 증상` | Description (섹션 유지) |
| `## 원인` | Description |
| `## 해결` | Description + Resolution note |
| 관련 PR/커밋 | Link to GitHub |

### 4.2 이관 대상 (3건, 2026-04-23 기준)
- `bug-collector-sighup-nohup.md`
- `bug-parquet-sink-dict-mutation.md`
- `bug-test-tsfmt-wrong-timestamp.md`

상태는 이관 시점에 Resolved/Closed로 설정 (모두 과거 해결된 이력).

## 5. GitHub 이관

### 5.1 레포 생성
- Org `mctrader` (사전 생성 — 미존재 시 수동 생성 필요)
- Repo `mctrader` (private)
- Default branch: `main`
- Branch protection: `main`에 PR 필수 (옵션)

### 5.2 이관 절차
```bash
# 1) GitLab에서 bare clone
git clone --mirror https://gitlab.com/mctrader1/mctrader.git mctrader-mirror.git

# 2) GitHub에 push
cd mctrader-mirror.git
git remote set-url --push origin https://github.com/mctrader/mctrader.git
git push --mirror

# 3) 로컬 작업 레포의 origin 변경
cd /Users/1111971/workspace/mctrader
git remote set-url origin https://github.com/mctrader/mctrader.git
git remote -v  # 검증
git fetch origin
```

### 5.3 검증
- `git ls-remote origin | wc -l`이 GitLab과 일치
- 최근 브랜치 `feat/dashboard-perf` fetch 성공
- 태그 개수 일치

## 6. MCP / 에이전트 설정 재편

### 6.1 settings(.local).json
**제거**:
- `.claude/settings.json` L12: `mcp__GitLab__list_issues`
- `.claude/settings.local.json` L65–78: GitLab issue/label 관련 권한 전체

**추가** (Atlassian MCP는 인증 후 자동 노출되지만 allowlist 명시로 권한 프롬프트 감소):
- `mcp__atlassian__createPage`, `updatePage`, `getPage`, `searchPages`
- `mcp__atlassian__createJiraIssue`, `updateJiraIssue`, `searchJiraIssues`
- (정확한 tool 이름은 인증 후 `discover_tools` 결과 기준으로 확정 — spec에서는 카테고리로 표기)

### 6.2 CLAUDE.md 수정 범위
- L47 "ADR ID + 1줄 요약 → mcp__GitLab__get_issue fetch" → `mcp__atlassian__*`로 교체
- L101 "문서 쓰기: DocsAgent(.md + GitLab MCP)" → "DocsAgent(.md + Atlassian MCP)"
- L113–118 "ADR (GitLab Issues SSOT)" 섹션 전체 재작성 (Confluence SSOT로)
  - 프로젝트 ID → Confluence space key
  - `list_issues(labels=["ADR"])` → Confluence Labels 쿼리 또는 Page Properties Report
  - 이슈 포맷 → 페이지 템플릿 (Page Properties + 본문 섹션)
- L119 이슈 포맷 블록 → 페이지 템플릿 블록

### 6.3 .claude/agents/*.md 수정 범위
- `DocsAgent.md` L11–22: GitLab tool 목록 → Atlassian tool 목록
- `DocsAgent.md` L33–37: "ADR은 GitLab Issues 전용" → "ADR은 Confluence 페이지 전용"
- `DocsAgent.md` L67–70: "GitLab Wiki 마이그레이션" 섹션 삭제 (이미 Confluence로 이동)
- `PMOAgent.md` L61: `mcp__GitLab__get_issue` → `mcp__atlassian__getPage`

## 7. 실행 순서 (단일 세션)

| Step | 작업 | 검증 |
|---|---|---|
| 1 | Atlassian MCP 인증 확인, GitHub org `mctrader` 존재 확인 | `mcp__atlassian__authenticate` 성공 / `gh api orgs/mctrader` |
| 2 | Confluence: "ADR" 루트 + 6개 카테고리 parent 페이지 생성 | 웹 UI에서 계층 확인 |
| 3 | ADR 21건 이관 (GitLab → Confluence, MCP 반복 호출) | 루트 페이지 Page Properties Report 테이블 자동 생성 |
| 4 | guides 5건 + api 1건 이관 | Confluence 페이지 렌더 확인 |
| 5 | bugs 4건 이관 (→ Jira MCTR) | Jira 이슈 목록 확인 |
| 6 | GitHub repo 생성 + `git push --mirror` | brancheѕ/tags 카운트 일치 |
| 7 | 로컬 `origin` URL 교체 + fetch 검증 | `git remote -v` |
| 8 | `CLAUDE.md` / `.claude/agents/*.md` / `settings(.local).json` 일괄 갱신 | grep으로 `GitLab` 잔여 참조 0건 확인 |
| 9 | `docs/guides/`, `docs/api/`, `docs/bugs/` 디렉토리 제거 + 커밋 | `ls` 확인 |
| 10 | GitLab 프로젝트 archived 설정 (웹 UI 또는 API) | GitLab UI 상단에 "Archived" 표시 |

## 8. 에러 처리 / 롤백

- **각 step 실패 시 GitLab이 여전히 SSOT** (step 10 전까지). 부분 이관 상태 허용 — 재시도 기반.
- **Confluence 페이지 중복 생성**: title+parent로 유일성 확인 → 존재 시 update, 없으면 create (멱등).
- **Jira 이슈 재생성 방지**: label `migrated-from-repo` + 파일명 기반 summary로 기존 이슈 존재 여부 search 후 skip.
- **GitHub 미러 오류**: repo 삭제 후 재시도 (이력 GitLab에 보존).
- **롤백 게이트**: Step 10 실행 전 사용자 최종 확인 필수.

## 9. 검증 체크리스트

- [ ] Confluence 루트 "ADR" 페이지 Page Properties Report에 21건 표시
- [ ] 샘플 ADR (ADR-001, ADR-017) Mermaid 다이어그램 렌더
- [ ] Jira MCTR 프로젝트 Bug 4건 조회 가능
- [ ] `git ls-remote origin` (GitHub) vs GitLab 레퍼런스 수 일치
- [ ] `grep -rn "GitLab\|mcp__GitLab" CLAUDE.md .claude/`  결과 0건
- [ ] `docs/` 하위에 `change-plans/`만 존재
- [ ] GitLab 프로젝트 아카이브 상태

## 10. 범위 외 (Out of Scope)

- CI/CD 이관 (GitLab CI → GitHub Actions): 현재 `.gitlab-ci.yml` 부재. 필요 시 별도 스펙.
- GitLab MRs → GitHub PRs 이관: 과거 MR이 없거나 무의미 (단독 작업자). 필요 시 별도.
- Issue Tracker 통합 (GitHub Issues + Jira 양방향): Q7(B) 결정으로 bugs만 Jira — 양방향 불필요.
- GitLab Wiki 마이그레이션: 사용 이력 없음.
