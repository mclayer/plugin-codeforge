---
title: Migration Guide — 플러그인 버전업 시 consumer overlay 변경 절차
status: active
created: 2026-04-24
updated: 2026-04-24
---

# Migration Guide

`codeforge` 플러그인 버전업 시 consumer 프로젝트의 overlay를 마이그레이션하는 절차.

각 섹션은 **한 major/minor 버전 bump 당 1건**. breaking change가 있는 버전만 다룬다. Core는 플러그인 업데이트 시 자동 반영되지만, `.claude/_overlay/` 내용은 consumer가 직접 업데이트.

## 목차

- [v0.17 → v0.18](#v017--v018-cfp-28-phase-0c--lint-strict-전환--retro-frontmatter-backfill-non-breaking) — Lint strict 전환 + retro frontmatter backfill (Non-BREAKING)
- [v0.16 → v0.17](#v016--v017-cfp-29-phase-1--codeforge-review-plugin-추출-breaking) — codeforge-review plugin 추출 (BREAKING)
- [v0.15 → v0.16](#v015--v016-cfp-27-phase-0b--lint-강화--ci-integration-non-breaking) — Lint 강화 + CI Integration (Non-BREAKING)
- [v0.14 → v0.15](#v014--v015-cfp-26-phase-0a--single-owner-write-권한-재분배) — Single-owner write 권한 재분배 (BREAKING)
- [v0.13 → v0.14](#v013--v014) — 설계 lane 6-deputy: DataMigrationArchitectAgent 신설 (BREAKING)
- [v0.11.0 → v0.12.0](#v0110--v0120) — 설계 lane 5-deputy: TestContractArchitectAgent 신설 (BREAKING)
- [v0.10.0 → v0.11.0](#v0100--v0110) — 설계 lane 재구조화: ArchitectPLAgent + SecurityArchitectAgent 신설
- [v0.8 → v0.9](#v08--v09-reviewtest-워커-통합) — **3 lane × 2 vendor = 6 워커 → 2 워커 (BREAKING)**
- [v0.7 → v0.8](#v07--v08-atlassian-제거--github-전환) — **Atlassian 제거 + GitHub 전환 (BREAKING)**
- [v0.6 → v0.7](#v06--v07-요구사항설계-레인-병렬화) — 요구사항·설계 레인 병렬 모델
- [v0.5 → v0.6](#v05--v06-plugin-name-rename-dev-orchestrator--codeforge) — Plugin name rename + Atlassian 이관
- [v0.3 → v0.4](#v03--v04-stage-2-projectyaml-구조화) — `project.yaml` 도입
- [v0.2 → v0.3](#v02--v03-generic-dev-roster--preset) — Generic Dev roster + preset
- [v0.1 → v0.2](#v01--v02-보안-테스트-레인--templates) — 보안 테스트 레인 + templates (non-breaking)

---

## v0.17 → v0.18 (CFP-28 Phase 0c) — Lint strict 전환 + retro frontmatter backfill (Non-BREAKING)

**범위**: CFP-27 Phase 0b 도입된 4 owner doc path schema lint(`scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh`) 을 warning 모드 → strict 모드 전환. 이미 존재하는 retro 3 file frontmatter backfill + 회고 §1 regex 완화 + legacy change-plan allowlist.

**Plugin runtime 영향**: 없음 (Non-BREAKING). 에이전트 동작·overlay 메커니즘·workflow 자동화 모두 무변경.

**CI 영향 (consumer 영향 가능)**:

### 1. 신규 doc 작성 시 schema 강제

이제 다음 path 신규/갱신 시 `lint.yml` CI에서 PR 차단:

| Path | Schema source | 필수 frontmatter | 필수 본문 섹션 |
|---|---|---|---|
| `docs/change-plans/**` | `templates/change-plan.md` | title, slug, status, author, created, story | §1 목적 / §2 현재 구조 / §3 도입할 설계 / §4 API 계약 / §7 보안 / §8 Test Contract / §10 ADR 정합성 / §11 데이터 마이그레이션 |
| `docs/adr/**` | `templates/adr.md` | adr_number, title, status, category, date | ## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 관련 파일 |
| `docs/domain-knowledge/**` | `templates/domain-knowledge.md` | title, area, topic_slug, status, updated | ## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력 |
| `docs/retros/**` | `templates/retro.md` | title, date, sprint_period, cfp_keys, authors | ## §1 ... / ## §2 ... / ## §3 ... / ## §4 ... (제목 자유) |

### 2. Legacy change-plan 자동 면제

- `docs/change-plans/cfp-1` ~ `docs/change-plans/cfp-18`(현재 디렉토리에 존재하는 16건, CFP-3·CFP-17 제외)은 schema 도입 이전 산출물로 자동 면제 (allowlist hardcode)
- 추가 작업 불필요 — backfill 의무 없음

### 3. 회고 §1 regex 완화

- 기존: `^## §1 결과` strict 매칭 (제목 텍스트 강제)
- 신규: `^## §1\s+\S` (§1 prefix만 강제, 제목 자유 — closure / cross-Story / sprint / session 회고별 자연스러운 명칭 사용)

### 4. consumer overlay 영향

없음. `.claude/_overlay/**` 변경 의무 없음. 본 lint은 plugin repo 자체 dogfooding 영역.

---

## v0.16 → v0.17 (CFP-29 Phase 1) — codeforge-review plugin 추출 (BREAKING)

**범위**: 5 review agent + base + 3 checklist을 별도 plugin으로 분리. consumer는 두 plugin 모두 등록 의무.

**필요 조치**:

### 1. codeforge-review plugin 설치

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true   // 추가
  }
}
```

또는 CLI:

```
/plugins install codeforge-review@mclayer
```

### 2. consumer overlay 영향

- consumer overlay에 5 review agent 중 어느 것이라도 override 하던 경우 (드뭄): overlay 파일을 codeforge-review repo의 동일 path 구조로 이동
- review packet/verdict schema는 v2 contract (v1 은 CFP-D 시점 Archived) — overlay 호환성 영향 없음

### 3. 자동 감지

- codeforge-review의 SessionStart hook이 codeforge core 설치 여부 verify. 미설치 시 fail-fast + install 안내 메시지
- codeforge core의 SessionStart hook도 codeforge-review 설치 여부 감지 (필수 플러그인 5종 list에 추가) — 미설치 시 review lane 진입 불가 안내

### 4. Inter-plugin Contract 인지

본 추출의 핵심 메커니즘:
- codeforge core (Orchestrator) → codeforge-review: `review_packet` 주입
- codeforge-review (PL) → codeforge core: `review_verdict v2` 반환 (typed, v1 은 CFP-D 시점 Archived)
- codeforge core (Orchestrator → lane plugin): verdict 받아 Story §9 / PR comment / gate label 처리 *(v0.x에서는 DocsAgent가 담당했으나 CFP-40 final delete 후 각 lane plugin self-write로 전환)*

상세 schema: codeforge core repo의 [`docs/inter-plugin-contracts/review-verdict-v2.md`](inter-plugin-contracts/review-verdict-v2.md) (Active). v1 (Archived, historical record): [`docs/inter-plugin-contracts/review-verdict-v1.md`](inter-plugin-contracts/review-verdict-v1.md). Versioning + archive 룰: [ADR-008](adr/ADR-008-inter-plugin-contract-versioning.md) §5/§5.1.

### 5. 설계 SSOT

- [`docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md) (CFP-29 design spec)
- parent: [CFP-25](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) staged ε strategy

### 6. 향후 단계 안내

- CFP-29.5 (조건부): codeforge-review 자체 lint workflow 추가
- CFP-30+ (조건부): contract validation lint (v1 schema 위반 자동 detect)

자세한 사항: 본 spec (CFP-29) §6 + CHANGELOG [0.17.0] 참조.

---

## v0.15 → v0.16 (CFP-27 Phase 0b) — Lint 강화 + CI Integration (Non-BREAKING)

**범위**: 신규 owner doc 템플릿 2건 + 신규 lint 2건 (warning 모드) + redistribution lint CI integration.

**필요 조치**:

### Consumer overlay에서 owner doc schema 따르려면 (선택)
- `templates/domain-knowledge.md` / `templates/retro.md` 를 frontmatter + 섹션 schema source로 활용 가능
- consumer overlay에 `_overlay/templates/<doc-type>.md` 작성하면 owner agent가 그 schema도 따름 (overlay-aware)

### Consumer CI workflow 동기화 (권장)
- `.github/workflows/lint.yml` 에 다음 3 job 추가 동기화:
  - `write-permission-redistribution` (strict)
  - `doc-frontmatter` (warning)
  - `doc-section-schema` (warning)
- 생략해도 codeforge plugin 동작에는 영향 없음. 다만 본 plugin이 consumer 워크플로우의 invariant를 보지 않게 됨.

### 향후 단계 안내
- CFP-28 (Phase 0c): 2 lint를 strict 모드로 전환 + 1-2 real Story 실행 검증. 이 시점에 backfill 필요한 모든 docs 파일 schema 갱신 의무.
- CFP-29 (Phase 1): codeforge-review plugin 추출.

### 설계 SSOT
- [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 design spec)

자세한 사항: 본 plan (CFP-27) 참조.

---

## v0.14 → v0.15 (CFP-26 Phase 0a) — Single-owner write 권한 재분배 (BREAKING)

**범위**: agent permission frontmatter 4건 갱신 + DocsAgent scope 축소 (당시 v0.15 context — DocsAgent 는 CFP-40에서 최종 삭제됨) + SSOT 문서 일관성 갱신.

**필요 조치**:

### Consumer overlay에서 agent 권한 확장하던 경우

overlay의 frontmatter `permissions.allow` 항목은 core와 **concat+dedup** 처리되므로 자동 흡수 — 별도 조치 불필요.

### Consumer overlay에서 DocsAgent 권한 명시 override 하던 경우 (v0.15 당시 — 현재 DocsAgent 부재 · CFP-40)

core가 `docs/{change-plans,adr,domain-knowledge,retros}/**` 4 path에 대해 deny를 추가했음.
- overlay에서 다시 allow를 명시하면 path-scoped allow가 우선
- 단 의도가 4 path에 대한 owner agent 분담 모델이 아니라면 core 모델에 맞추는 것을 권장

### Consumer 자동화 (CI / pre-commit)에서 invariant 강제

core가 신설한 `scripts/check-write-permission-redistribution.sh` 호출 권장:

```bash
./scripts/check-write-permission-redistribution.sh
```

exit=0 이어야 통과. 16 assertion check.

### 향후 단계 안내

- CFP-27 (Phase 0b): frontmatter / 섹션 schema lint 강화
- CFP-28 (Phase 0c): real Story 실행 검증
- CFP-29 (Phase 1): codeforge-review plugin 추출 — 별도 plugin marketplace 등록 + dependency 추가 필요

### 설계 SSOT

- [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 design spec)

자세한 사항: 본 spec §1·§5 참조.

---

## v0.13 → v0.14

### 변경 사항
- **신규 에이전트 1종**: `DataMigrationArchitectAgent` (설계 lane 6번째 deputy, 데이터 무결성 advocate for §11 데이터 마이그레이션)
- **agent count**: 23 → 24
- **ArchitectPLAgent**: deputy 4 → 5 (Phase 1 spawn diagram + Phase 1.5 sanity check 1 항목 + 메타-규칙 1번 §11 매핑 1행 추가)
- **ArchitectAgent (chief author)**: §11 author input 통합 절차 추가 — Change Plan §1-§10 → §1-§11
- **`templates/change-plan.md`**: §10 다음 §11 데이터 마이그레이션 신설 (§11.1 Schema 영향 / §11.2 Migration 전략 / §11.3 Rollback 경로 / §11.4 Data integrity invariant / §11.5 Backfill / §11.6 N/A)
- **DesignReview checklist**: §11 audit 절 신설 + 3 P0 차단 룰 (§11 누락 / §11.6 N/A 사유 부재 / DataMigrationArch 매핑 미반영)
- **lane=design category enum**: `data-migration` 추가 (7 → 8 카테고리)
- **3-way → 4-way 대립 재명명**: Mapper(보수) / Refactor(혁신) / SecurityArch(공격자) / DataMigrationArch(데이터 무결성)
- **ADR-007** (Accepted) — DataMigrationArchitectAgent 도입 결정 (ADR-006 패턴 mirror)
- **CFP-21**: Codex audit #2 (High severity) 직접 closure

### 변경 의도
- shift-left 데이터 무결성: schema 진화·rollback·integrity invariant·backfill 결정이 설계 단계에서 별도 author input으로 가시화 → 구현 테스트 / 보안 테스트 lane FIX 회귀 비용 감소
- ADR-004 / ADR-006 패턴 세 번째 적용 — 구조적 정합성 검증 (dogfooding success metric)

### Consumer 액션

#### 진행 중 Story (phase: 설계 / 설계 리뷰)
1. Change Plan에 §11 데이터 마이그레이션 추가 (DataMigrationArchitectAgent 산출물 통합)
   - DB·schema·migration이 무관한 Story (예: pure UI / docs-only / plugin meta) → §11.6 N/A + 사유 1줄
   - DB·schema·migration이 관련된 Story → §11.1-§11.5 작성
2. ArchitectPLAgent Phase 3 검수 재실행 (메타-규칙 1번에 §11 매핑 추가됨)
3. DesignReview 재실행 (§11 누락 또는 N/A 사유 부재 시 P0 차단)

#### 신규 Story
- 자동 적용 — story-init.yml Action이 신규 template 사용
- consumer overlay에 `has_data_layer: false` 설정 시 DataMigrationArchitectAgent가 항상 §11.6 N/A 결과 반환 (단 사유 1줄 의무)

### 위험·완화

- **위험**: 진행 중 Story가 §11 누락 상태로 설계 리뷰 진입 시 P0 차단
- **완화**: 본 가이드의 "진행 중 Story" 절차 따라 §11 추가 후 재진입

### 토큰 비용

- 설계 lane peak: 175k → 200k (+25k DataMigrationArch deputy)
- 1 Story당 5-10k 토큰 추가 추정 (실제 §11 작성 시점에만 소요, §11.6 N/A 케이스는 minimal)

### 자기 적용 paradox

본 CFP-21 자체는 plugin meta paradox로 자기 적용 안 함 (CFP-17/CFP-18/CFP-19/CFP-20 동일 패턴, ADR-005 정합). 본 §11 신설은 **다음 Story부터 발효**.

---

## v0.11.0 → v0.12.0

### 변경 사항
- **신규 에이전트 1종**: `TestContractArchitectAgent` (설계 lane 5번째 deputy, QA perspective contributor for §8 Test Contract)
- **ArchitectPL 검수 메타-규칙 압축**: 4 항목 enumerate -> 2 항목 메타-규칙 (Refactor STRONG ROI 채택)
- **ADR-005 status 전이**: Proposed -> Accepted (결정 1·2·3 한정 — N/A 표기 형식·면제 분류·N/A inheritance 차단)
- **ADR-006 신규 발행**: TestContractArch 도입 근거 + 사용자 5 BLOCKING 결정 verbatim 인용

### Consumer 액션 필요
- **없음** (Orchestrator 경유 호출이라 직접 영향 없음)
- 권장: SessionStart hook 재실행해 새 agent md 인식

### 기존 docs/change-plans/* 회귀 갱신 불필요
- 과거 Change Plan은 historical record 보존
- 새 §8 author input 규칙은 v0.12.0 이후 신규 Story부터 적용

---

## v0.10.0 → v0.11.0

### 변경 사항
- **신규 에이전트 2종**: `ArchitectPLAgent` (설계 lane PL), `SecurityArchitectAgent` (설계 lane deputy)
- **ArchitectAgent 역할 변경**: 단독 PL → ArchitectPL 직속 chief author (Change Plan §1-§10 + ADR draft + §8 Test Contract author)
- **Change Plan template 신규 §7 보안 설계 섹션** — 신규 Story부터 적용 (외부 입력·인증·민감데이터 무관 시 §7.6 N/A 권한)
- **ADR-004** 발행: 설계 lane 재구조화 결정 기록
- **책임 매트릭스 변경**: trust boundary·auth·민감데이터 등 설계 결정은 Design lane (SecurityArch), 코드 준수 검증은 Security Test (시점 분리)

### Consumer 액션 필요
- **없음** (Orchestrator 경유 호출이라 직접 영향 없음)
- **권장**: SessionStart hook 재실행해 새 agent md 인식 (`~/.claude/plugins/cache/...` refresh)

### 기존 docs/change-plans/* 회귀 갱신 불필요
- 과거 Change Plan은 historical record로 보존
- 새 §7 섹션은 v0.11.0 이후 신규 Story부터 적용

### Rollback
- v0.11.0 이슈 발견 시 v0.11.1 hotfix 우선
- Last resort: `/plugins install codeforge@0.10.0`로 다운그레이드 (data migration 0건이라 안전)

---

## v0.8 → v0.9 (Review/Test 워커 통합)

### Breaking changes

[ADR-001](adr/ADR-001-review-agent-unification.md) 결정에 따라 **3 lane × 2 vendor = 6 워커**(Claude{Design,Code,SecurityTest}ReviewAgent + Codex 동등 6종)를 **2 lane-agnostic 워커**(`ClaudeReviewAgent`, `CodexReviewAgent`)로 통합. lane-specific 도메인(체크리스트·스코프·category enum·severity 자동 룰)은 호출 PL이 `review_packet`으로 주입.

- 24 core agents → **20 core agents** (워커 6 삭제 + 워커 2 신규)
- Codex 플러그인이 단일 의존성으로 격상 — 미설치 시 3 리뷰 lane 전부 진입 불가
- SecurityTestPL이 `Bash(gh api repos/*)` 권한 사용 — 1차 layer (Dependabot/CodeQL/Secret Scanning/Push Protection) 결과를 packet에 inline 첨부

### Affected files (consumer overlay 측)

| 파일 | 액션 |
|------|------|
| `.claude/_overlay/agents/ClaudeDesignReviewAgent.md` (있다면) | **제거** — `agents/ClaudeReviewAgent.md` (core)로 통합 |
| `.claude/_overlay/agents/Codex{Design,Code,SecurityTest}ReviewAgent.md` (있다면) | **제거** — `agents/CodexReviewAgent.md` (core)로 통합 |
| `.claude/_overlay/templates/review-checklists/<lane>.md` (선택) | **신규 가능** — 언어·프레임워크 특화 체크 항목 추가 (Python·Go·React 등) |
| `.claude/_overlay/CLAUDE.md` 내 워커 인용 | "Claude/Codex<Domain>ReviewAgent" 패턴이 있다면 "ClaudeReviewAgent / CodexReviewAgent" lane-agnostic 참조로 갱신 |

### Migration 절차 (consumer)

1. **Codex 플러그인 인증 확인**: 3 리뷰 lane 전부 진입 불가가 되므로 `codex@openai-codex` 플러그인 미설치 시 즉시 설치
2. **6 워커 오버라이드 제거**: `.claude/_overlay/agents/`에 `Claude{Design,Code,SecurityTest}ReviewAgent.md` 또는 Codex 동등 파일이 있다면 제거. 도메인 특화 체크는 lane checklist (`templates/review-checklists/<lane>.md`)로 이동
3. **GitHub 토큰 권한 확인**: SecurityTestPL이 `gh api repos/*/dependabot/alerts` 등을 호출하므로 Dependabot/CodeQL/Secret Scanning alerts read 권한 필요
4. **첫 리뷰 lane 실행 시 검증**: PL이 `review_packet` 필수 필드(lane / checklist_path / scope_globs / category_enum / story_key, security 추가 시 first_layer_findings) 누락 시 워커가 `ESCALATE_PACKET_INCOMPLETE` 반환 — generic fallback 없음
5. **CHANGELOG·코멘트의 historical 인용 유지**: 과거 `Codex<Domain>ReviewAgent` 명칭은 historical로 보존 (변경 금지)

### Backward compatibility

- 라벨·워크플로우·phase 전이 invariant **무변경**: `phase:설계-리뷰` / `phase:구현-리뷰` / `phase:보안-테스트` / `gate:design-review-pass` / `gate:security-test-pass` / `fix:<레인>-retry` 라벨, `phase-gate-mergeable.yml`·`fix-ledger-sync.yml` Action 동작 유지
- `docs/stories/<KEY>.md` 섹션 구조(§1-11) **무변경**

기존 v0.8 활성 Story가 있다면, 다음 리뷰 iteration부터 자연스럽게 새 워커가 packet 수령. Phase 2 PR 진행 중 Story는 즉시 영향 없음.

---

## v0.7 → v0.8 (Atlassian 제거 + GitHub 전환)

### Breaking changes

이 release는 Atlassian backend (Confluence/Jira)를 완전 제거한다. v0.7 이하 consumer는 in-place 업그레이드 불가 — fresh GitHub-based setup 필요.

- **MCP 의존**: `atlassian` (HTTP) → **`github`**
- **필수 플러그인**: `github@claude-plugins-official` 권장에서 격상, `atlassian@claude-plugins-official` 제거
- **필수 CLI**: `gh` 추가 (Milestone·Discussions·기타 GraphQL fallback)
- **워크플로우 모델**:
  - Story 페이지 (Confluence) → `docs/stories/<KEY>.md` (single-file SSOT, §1-11)
  - ADR (Confluence pages) → `docs/adr/ADR-NNN-<slug>.md` (flat, frontmatter `category:`)
  - Domain Knowledge (Confluence tree) → `docs/domain-knowledge/<area>/<topic>.md` (계층)
  - Jira workflow → GitHub Issue + `phase:*` labels + GitHub Actions
  - Jira sub-task → GitHub Sub-issue (subissue-from-impl-manifest.yml Action 자동 생성)
  - Jira Epic → GitHub Milestone + Epic Issue
- **PR 모델**: 1 Story = **2 PRs** (Phase 1 docs / Phase 2 code+docs append)
- **§1 변조 금지 invariant**: `story-section-1-immutable.yml` Action이 강제
- **Phase 라벨 single-active**: `phase-label-invariant.yml` Action이 강제
- **보안 테스트 1차 layer**: GitHub native (Dependabot / CodeQL / Secret Scanning / Push Protection)

### project.yaml 스키마

`atlassian.*` 키 모두 삭제 → `github.*` 키 신설.

```yaml
# OLD (v0.7)
atlassian:
  site: ...
  confluence:
    space_key: ...
    stories_parent_page_id: ...
    domain_knowledge_parent_page_id: ...
    adr_root_page_id: ...
  jira:
    project_key: ...

github:
  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"

# NEW (v0.8)
github:
  org: ...
  repo: ...
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: ...                   # e.g. "TM"
  codeowners:
    architect_team: "@org/architects"
    domain_expert_team: "@org/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"
```

자세한 형식은 [project-config-schema.md](project-config-schema.md) 참조.

### Consumer 절차 (fresh setup)

기존 v0.7 consumer가 0건이므로 자동 마이그레이션 도구·자동 변환은 제공하지 않는다. 신규 또는 v0.7에서 v0.8로 이전하는 consumer는 [consumer-guide.md](consumer-guide.md) 셋업 절차를 따른다:

1. `.github/workflows/` 6개 plugin 워크플로우 복사
2. `.github/ISSUE_TEMPLATE/` 3 Forms + `config.yml` (blank issue 비활성화) 복사
3. `.github/PULL_REQUEST_TEMPLATE.md` 복사
4. `.github/CODEOWNERS` 복사 + team placeholder 치환
5. `.claude/_overlay/project.yaml` 새 schema로 재작성
6. GitHub Labels 일괄 생성 (gh label create ...)
7. Branch protection 설정 (main 브랜치, required status check `phase-gate-mergeable`)
8. Dependabot / CodeQL / Secret Scanning / Push Protection 활성화

### 영향 범위

- consumer 리포의 `.github/`·`.claude/_overlay/project.yaml`·`docs/` 디렉토리 모두 영향
- 기존 Confluence 페이지·Jira issue는 별도 export 후 `docs/` 마크다운으로 수동 이전 권장 (자동 도구 미제공)
- 기존 활성 Story (Atlassian상)가 있다면 v0.8에서 새 Story로 다시 시작하는 게 가장 단순

### 참고

- 설계 spec: `docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md`
- 구현 plan: `docs/superpowers/plans/2026-04-25-atlassian-to-github-migration.md`

---

## v0.6 → v0.7 (요구사항·설계 레인 병렬화)

### Breaking changes (오케스트레이션 semantics)

- **요구사항 레인**: `DomainAgent → Analyst → Researcher` 순차 (조건부 생략 포함) → **`DomainAgent ∥ Analyst ∥ Researcher` 병렬** (셋 다 non-skippable)
- **설계 레인**: `CodebaseMapper → Refactor` 순차 (Refactor가 Mapper 요약 입력 수신) → **`CodebaseMapper ∥ Refactor` 병렬** (둘 다 원 소스 직접 독해, 산출물 교차 참조 없음)
- **Clarification 재스폰 프로토콜**: PL↔서브 continuous dialog가 불가하므로, PL이 통합 중 추가 질의가 필요하면 Orchestrator 경유 재스폰 요청 (이전 출력 pointer + clarification context + 범위 제한). 동일 에이전트 2회 재스폰 이후 미해소면 사용자 ESCALATE
- **Researcher·DomainAgent non-skippable 승격**: 이전엔 조건부 생략 가능이었으나, 이제 "조사 불필요" 판정도 명시 반환 필수 (null skip 금지)

### 영향 범위

- **Consumer overlay가 RequirementsPLAgent 또는 ArchitectAgent 행동을 override하지 않는다면 영향 없음** — core agent 이름·경로·Story 페이지 섹션 규격 모두 동일
- Override 중인 consumer만 아래 절차 필요

### 마이그레이션 절차 (override 중인 consumer만)

#### 1. RequirementsPLAgent override 수정

overlay에 "DomainAgent → Analyst → Researcher 순서로 스폰" 류 지시가 있으면:

**Before**:
```markdown
1. DomainAgent 스폰 → 지식 공백 수령
2. Analyst 스폰 (DomainAgent 지식 공백 payload 포함)
3. Analyst 산출물의 Researcher 키워드 존재 시 Researcher 스폰
```

**After**:
```markdown
1. 공통 입력 패키지 준비 (사용자 원문 + Story §1-2 + 관련 ADR + Project Config Packet)
2. DomainAgent · Analyst · Researcher **병렬 스폰** (공통 입력만 전달, 타 에이전트 산출물 미포함)
3. 세 결과 병렬 수령 → dedup · 상충 조정
4. Clarification 필요 시 Orchestrator 경유 재스폰
```

#### 2. ArchitectAgent override 수정

"Mapper → Refactor 순 스폰" 류 지시가 있으면:

**Before**:
```markdown
1. CodebaseMapper 스폰 → as-is 산출물 수령
2. Refactor 스폰 (Mapper 산출물 입력)
```

**After**:
```markdown
1. 공통 입력 패키지 준비 (변경 대상 코드 경로 + 관련 ADR + Change Plan 초안 + Story §1-7)
2. CodebaseMapper · Refactor **병렬 스폰** (둘 다 원 소스 직접 독해, 상호 산출물 미전달)
3. 두 결과 병렬 수령 → 교차 검토 → Change Plan §2·§3에 각각 반영
4. Clarification 필요 시 Orchestrator 경유 재스폰
```

#### 3. Story 페이지 §6 null 결과 규정 확인

Consumer overlay가 `templates/story-page-structure.md` §6을 override하면 "Researcher 키워드 비어있으면 섹션 생략" 서술이 있는지 점검, "외부 지식 보강 불필요 사유 명시" 로 변경.

### 검증 체크리스트

- [ ] overlay의 RequirementsPLAgent/ArchitectAgent에서 "순차"·"→" 표기 제거
- [ ] Researcher·DomainAgent를 "조건부 생략 가능"으로 표기한 overlay 있으면 제거
- [ ] 세션 1회 수행 후 Story 페이지 §10 FIX Ledger에 clarification 재스폰 이력이 적절히 기록되는지 확인

---

## v0.5 → v0.6 (Plugin name rename `dev-orchestrator` → `codeforge`)

### Breaking changes

- **Plugin name 변경**: `dev-orchestrator` → `codeforge`
- **Marketplace install URL 변경** (해당 시): `/plugins install dev-orchestrator@<marketplace>` → `/plugins install codeforge@<marketplace>`
- **`CLAUDE_PLUGIN_ROOT` 하위 경로 변경**: `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/` → `${CLAUDE_PLUGIN_ROOT}/codeforge/`
- **GitHub repo 이동**: `mctrader/plugin-codeforge` → `mctrader/plugin-codeforge` (GitHub 자동 URL redirect 30일 유지)

### 영향받는 consumer 파일

- `.claude/settings.json` — SessionStart hook 커맨드의 경로

### 마이그레이션 절차

#### 1. Plugin 재설치 (marketplace 사용 시)

```bash
/plugins uninstall dev-orchestrator
/plugins install codeforge@<marketplace>
```

로컬 개발용 plugin (directory-based install) 은 재설치 불필요 — 플러그인 디렉토리가 `codeforge`로 바뀌었는지만 확인.

#### 2. `.claude/settings.json` hook 경로 수정

**Before**:
```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

**After**:
```json
{
  "hooks": {
    "SessionStart": [
      { "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
    ]
  }
}
```

#### 3. Preset 임포트 경로 (사용 중이면)

**Before**:
```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

**After**:
```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

#### 4. project.yaml skeleton 복사 경로 (신규 설치 시)

**Before**:
```bash
cp ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

**After**:
```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

#### 5. 검증

```bash
claude
# SessionStart hook이 새 경로로 정상 작동, .claude/agents/*.md 생성 확인
ls .claude/agents/ | wc -l
```

### 체크리스트

- [ ] `.claude/settings.json` hook 커맨드에 `dev-orchestrator` 잔존 없음 (grep 확인)
- [ ] Plugin 재설치 완료 (해당 시)
- [ ] 세션 개시 후 `.claude/agents/` 정상 생성
- [ ] consumer repo README·doc에 plugin 이름 참조 있다면 일괄 교체

### 참고

- `CHANGELOG.md` v0.6.0 엔트리
- Repo 새 주소: https://github.com/mctrader/plugin-codeforge (30일간 `mctrader/plugin-codeforge` 자동 redirect)

---

## v0.3 → v0.4 (Stage 2 `project.yaml` 구조화)

### Breaking changes

- **Atlassian·GitHub·labels 상수 위치 변경**: `.claude/_overlay/CLAUDE.md` 에 free text로 작성하던 SSOT 상수가 `.claude/_overlay/project.yaml`로 이동.
- **에이전트 동작 변경**: DomainAgent·RequirementsPLAgent·PMOAgent 및 각 lane plugin agent가 `project.yaml`을 `Read`하는 것이 의무. 파일이 없거나 필수 필드 누락 시 Orchestrator 경유 사용자 에스컬레이션.

### 영향받는 consumer 파일

- `.claude/_overlay/CLAUDE.md` — SSOT 상수 섹션 제거 필요
- `.claude/_overlay/project.yaml` — **신규 작성 필수**

### 마이그레이션 절차

#### 1. `project.yaml` 신설

```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example \
   .claude/_overlay/project.yaml
```

#### 2. 기존 CLAUDE.md overlay에서 상수 값 이동

**Before** (`.claude/_overlay/CLAUDE.md` 일부):
```markdown
## SSOT 상수

- Confluence space: `TM` (spaceId=12345)
- Story parent pageId: 23456
- Story template pageId: 34567
- Jira project key: `TM`
- Atlassian host: `https://acme.atlassian.net`

## Domain Knowledge

- Domain Knowledge 루트 pageId: 45678
- ADR 루트 pageId: 56789
```

**After** (`.claude/_overlay/project.yaml`):
```yaml
project:
  name: task-manager
  repo: github.com/acme/task-manager

atlassian:
  site: acme.atlassian.net
  confluence:
    space_key: TM
    stories_parent_page_id: 23456
    domain_knowledge_parent_page_id: 45678
    adr_root_page_id: 56789
  jira:
    project_key: TM

github:
  pr_title_prefix_template: "[{project_key}-{story_number}] {title}"

labels:
  components:
    - api
    - ui
    - data
    - infra
```

**After** (`.claude/_overlay/CLAUDE.md` — narrative만 유지):
```markdown
## Project

`task-manager` — 팀 단위 할 일 관리 웹 애플리케이션. Python + FastAPI 기반.

SSOT 상수는 `.claude/_overlay/project.yaml` 참조.

## Domain

할 일(Task) 관리와 팀 협업. Task status lifecycle·팀 권한 모델이 핵심.

## 기술 스택 (선택 근거)

- 언어 Python 3.12: 기존 팀 역량·생태계
- 프레임워크 FastAPI: async 지원·OpenAPI 자동 생성
- DB PostgreSQL: ACID·RLS 지원

## 경로 관습

- `src/api/**` — REST 라우트
- `src/domain/**` — 도메인 로직
- `src/adapters/**` — 외부 시스템 어댑터
```

#### 3. 검증

```bash
# project.yaml 파싱 확인
python3 -c "import yaml; yaml.safe_load(open('.claude/_overlay/project.yaml'))"

# 세션 개시 → SessionStart hook이 .claude/agents/ 재생성
claude

# lane plugin overlay 본문 확인 — project.yaml 참조 문구 포함 (DocsAgent 부재 — CFP-40)
# cat .claude/agents/<LanePluginAgent>.md | grep -A1 "project.yaml"
```

#### 4. 체크리스트

- [ ] `.claude/_overlay/project.yaml` 존재 + 필수 필드 채움 (project·atlassian·github)
- [ ] `.claude/_overlay/CLAUDE.md`에서 SSOT 상수 섹션 제거 (혹은 "project.yaml 참조" 명시)
- [ ] 기존 `component:*` 라벨 값이 `project.yaml`의 `labels.components`와 일치
- [ ] `cat .claude/_overlay/project.yaml` 결과를 팀과 공유·검증 (pageId·key 오타 방지)

### 참고

- Schema SSOT: [`project-config-schema.md`](project-config-schema.md)
- Consumer 가이드: [`consumer-guide.md`](consumer-guide.md) §3a

---

## v0.2 → v0.3 (Generic Dev roster + preset)

### Breaking changes

- **Core 에이전트 이름·위치 변경**:
  - `BackendDeveloperAgent`·`FrontendDeveloperAgent` → `presets/webapp/agents/`로 이동 (core에서 제거)
  - `ServerEngineerAgent` → `InfraEngineerAgent`로 **리네임**
  - 신규 core agent: `DeveloperAgent` (generic)
- **DevPL roster 동작 변경**: 하드코딩된 "4 Dev" → `role: dev` frontmatter 태그로 **동적 discovery**. consumer가 추가 Dev 에이전트를 overlay로 정의 가능.
- **`merge.py` 동작 변경**: "core 없음 + overlay 있음" 케이스가 이전엔 abort였으나 이제 **overlay-only 렌더** (`--overlay-only` 모드). preset 임포트·consumer-defined agent 지원.

### 영향받는 consumer 파일

- `.claude/_overlay/agents/ServerEngineerAgent.md` → `InfraEngineerAgent.md`로 rename (있다면)
- `.claude/_overlay/agents/BackendDeveloperAgent.md`, `FrontendDeveloperAgent.md` → core 제거로 인해 preset에서 복사해야 정상 작동 (웹앱 프로젝트 한정)
- `.claude/_overlay/CLAUDE.md` — Dev roster 구성 설명이 있으면 업데이트

### 마이그레이션 절차

#### A. 웹앱 프로젝트 (preset/webapp 사용)

1. **preset 복사**
   ```bash
   cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
         .claude/_overlay/agents/
   ```
   (기존 overlay 본문이 있으면 수동 병합)

2. **ServerEngineer → InfraEngineer 리네임** (overlay가 있었다면)
   ```bash
   git mv .claude/_overlay/agents/ServerEngineerAgent.md \
          .claude/_overlay/agents/InfraEngineerAgent.md
   # 파일 내부 frontmatter name: 필드도 "InfraEngineerAgent"로 수정 (선택 — overlay에 name 없으면 불필요)
   ```

3. **Generic `DeveloperAgent` 충돌 방지**
   Backend+Frontend가 `src/**`를 충분히 커버하므로 generic DeveloperAgent는 중복. CLAUDE.md overlay에 다음 명시:
   ```markdown
   > 이 프로젝트는 webapp preset(Backend+Frontend)을 쓰므로 core의 generic `DeveloperAgent`는 비활성화.
   ```
   또는 `.claude/_overlay/agents/DeveloperAgent.md` overlay로 permissions를 제한 (`deny` 경로로 preset 영역 제외).

4. **세션 개시 → 결과 확인**
   ```bash
   claude
   ls .claude/agents/ | grep -E "Backend|Frontend|Infra"
   # BackendDeveloperAgent.md, FrontendDeveloperAgent.md, InfraEngineerAgent.md 존재
   ```

#### B. 비웹앱 프로젝트 (CLI 툴·라이브러리·임베디드 등)

1. **Backend/Frontend overlay 제거** (있었다면)
   ```bash
   rm -f .claude/_overlay/agents/BackendDeveloperAgent.md
   rm -f .claude/_overlay/agents/FrontendDeveloperAgent.md
   ```

2. **ServerEng → Infra 리네임** (A와 동일)

3. **Generic DeveloperAgent 활용**
   core의 `DeveloperAgent`가 자동으로 roster에 포함됨. 경로 scoping이 필요하면 overlay 작성:
   ```markdown
   ---
   permissions:
     allow:
       - Edit(src/cli/**)
       - Write(src/cli/**)
       - Edit(src/core/**)
       - Write(src/core/**)
   ---

   ### 기술 스택
   - 언어: Go 1.22
   - CLI 프레임워크: cobra
   ```

4. **추가 Dev 에이전트 정의 (선택)**
   프로젝트에 `ParserDev`·`FirmwareDev` 같은 특화 역할이 필요하면 `role: dev` 태그로 overlay-only agent 작성:
   ```markdown
   ---
   name: FirmwareDeveloperAgent
   role: dev
   description: 임베디드 펌웨어 구현 — MCU·드라이버·실시간 제약
   permissions:
     allow:
       - Edit(firmware/**)
       - Write(firmware/**)
   ---

   ### 담당
   STM32 HAL·FreeRTOS 태스크·인터럽트 핸들러
   ```

#### 체크리스트

- [ ] `ls .claude/_overlay/agents/`에 `ServerEngineerAgent.md` 없음
- [ ] 웹앱: Backend/Frontend preset 복사됨 + role: dev 태그 존재
- [ ] 비웹앱: generic `DeveloperAgent` overlay로 경로 scoping (필요 시)
- [ ] 세션 개시 후 `.claude/agents/`에 예상 roster만 존재 (불필요한 preset agent 없음)

---

## v0.1 → v0.2 (보안 테스트 레인 + templates)

### Non-breaking

v0.2는 consumer overlay에 영향 없음. Core만 확장:
- 신규 core agent 3종: `SecurityTestPLAgent`, `ClaudeSecurityTestAgent`, `CodexSecurityTestAgent`
- 신규 `templates/` 디렉토리: `change-plan.md`, `adr.md`, `story-page-structure.md`, `impl-manifest.md`
- 기존 "테스트" 레인 → "구현 테스트" + "보안 테스트" 2단계로 분리

### 선택적 작업

보안 테스트 레인이 consumer 프로젝트 특화 기준을 요구하면:
- `.claude/_overlay/agents/ClaudeSecurityTestAgent.md`, `CodexSecurityTestAgent.md` 신설 — 프로젝트 특화 보안 체크포인트 추가
- 예: "이 프로젝트는 결제 PG 연동 있음 → PCI DSS 범위 체크 추가"

### 체크리스트

- [ ] Jira 대시보드 JQL이 `phase:보안-테스트` 라벨을 조회하도록 갱신 (기존 `phase:테스트`만 쓰던 경우)
- [ ] 보안 테스트 P0/P1 FIX 무제한임을 팀에 공유 (기존 "테스트 FIX 무제한" 정책 동일)

---

## 일반 원칙

### 버전업 전 확인

1. `CHANGELOG` 또는 [`README.md`](../README.md) 연혁 섹션에서 target version의 breaking change 확인
2. `archive/` 태그 존재 여부 (주요 pivot 시 보존) — rollback 경로
3. 본 가이드의 해당 섹션 수행

### 버전업 후 검증

1. 세션 개시 → SessionStart hook 성공 (`regenerated N core + M overlay-only agents` 메시지)
2. `.claude/agents/`의 에이전트 수·이름이 기대대로
3. Dry-run 1건: 간단한 Story 요건 → 설계 → 구현 1~2 단계 실행해서 Orchestrator가 정상 roster를 discover하는지 관찰

### 문제 발생 시

- 플러그인 repo의 해당 버전 PR·이슈 확인
- consumer CLAUDE.md overlay에 `project.yaml` 참조가 누락됐거나 이름 오타가 있는지 grep
- `git log --oneline <archive-tag>..HEAD` 로 변경 범위 파악 후 부분 rollback

## 관련 문서

- [`consumer-guide.md`](consumer-guide.md) — 신규 consumer 설치 가이드
- [`project-config-schema.md`](project-config-schema.md) — `project.yaml` schema SSOT
- [`plugin-design.md`](plugin-design.md) — core/overlay 경계 원칙
- [`../README.md`](../README.md) — 버전 연혁
