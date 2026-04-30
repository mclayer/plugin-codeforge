# CLAUDE.md

Claude Code 범용 SW 개발 오케스트레이션 플러그인. **0 core 에이전트 (wrapper-only)** · 7 레인 구조 + `role: dev` 동적 roster로 요구사항 접수부터 보안 테스트 통과까지 자율 실행. 에이전트 상세는 각 lane plugin 의 `agents/<Name>.md` (codeforge-{review,pmo,requirements,test,develop,design} 각 repo SSOT — 본 wrapper repo 에는 agent file 없음). 공통 문서 양식은 [`templates/`](templates/) SSOT 참조. **Review subsystem (3 PL + 2 worker + base + 3 checklist)은 별도 plugin [`codeforge-review`](https://github.com/mclayer/plugin-codeforge-review)** 로 추출 (CFP-29 Phase 1). Inter-plugin contract `review_verdict v1` 은 [`docs/inter-plugin-contracts/review-verdict-v1.md`](docs/inter-plugin-contracts/review-verdict-v1.md) SSOT ([ADR-001](docs/adr/ADR-001-review-agent-unification.md) lane-agnostic 통합 + [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md) versioning). 프로젝트 shape별 Dev 구성 preset은 [`presets/`](https://github.com/mclayer/plugin-codeforge-develop/tree/main/presets) 참조.

## Plugin

이 리포는 **consumer 프로젝트가 설치해 사용하는 Claude Code 플러그인**. 프로젝트별 도메인·기술 스택·SSOT 상수는 **overlay 메커니즘**(consumer 측 `.claude/_overlay/` + SessionStart merge hook)으로 주입. 상세는 [`docs/consumer-guide.md`](docs/consumer-guide.md) 참조.

**Objective SSOT 상수** (GitHub org/repo·story_key_prefix·CODEOWNERS team·Discussions 카테고리·Milestone naming·label taxonomy)는 **`.claude/_overlay/project.yaml`** 에 structured로 기재. 에이전트는 해당 파일을 `Read`로 직접 참조. Schema: [`docs/project-config-schema.md`](docs/project-config-schema.md). Narrative 컨텍스트(도메인 해설·기술 스택 근거)는 `.claude/_overlay/CLAUDE.md`에 기재.

### Marketplace cross-repo 동기화 의무

본 플러그인은 [`mclayer/marketplace`](https://github.com/mclayer/marketplace)를 통해 사용자에게 노출된다 (`/plugins install codeforge@mclayer`). codeforge `.claude-plugin/plugin.json`의 **mirrored 필드 — `name` · `version` · `description` · `author`** — 변경 시 `mclayer/marketplace`의 [`/.claude-plugin/marketplace.json`](https://github.com/mclayer/marketplace/blob/main/.claude-plugin/marketplace.json) `plugins[name=codeforge]`의 동일 필드를 같은 Story 범위 내에서 **반드시 동기화 PR로 반영**한다 (codeforge PR 머지 직후 즉시 marketplace sync PR open·merge).

**규칙**:
- mirrored 필드 변경이 포함된 codeforge PR은 본문 / Story file §11에 "marketplace sync PR 후속 의무" 명시
- codeforge PR merge → 즉시 marketplace 측 동기화 PR open (gh API로 cross-check 후 merge)
- 비-mirrored 필드(`keywords` 등 marketplace.json schema 비대상)만 변경 시 sync 면제 (예외 사유는 Story §4·§7에 명시)
- 정식 인프라화는 cross-repo parity CI 후속 CFP에서 처리 — 자동 차단 도입 전까지 author·Orchestrator 의무

**근거**: 사용자 명시 (CFP-24, 2026-04-28). drift 시 사용자가 stale version·어긋난 description을 install하게 되어 marketplace의 단일 진입점 의미가 무너진다.

## SSOT Boundary (ADR-012)

본 wrapper CLAUDE.md content scope 는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md) 에 따라 strictly limited:
1. **Plugin identity** (composition · marketplace sync · dependency check)
2. **Cross-cutting policy** (dogfood Story 작성 의무 · write boundary table · inter-plugin contract index · ADR list)
3. **3 SSOT 예외** (cross-lane scope, no single-plugin home): 책임 매트릭스 · 원인 판정 decision table · FIX Ledger §10 schema

Lane internal · per-lane spawn detail · severity rule detail · GitHub workflow subsection 상세는 각 lane plugin CLAUDE.md SSOT 또는 [playbook](docs/orchestrator-playbook.md) 위임.

## 세션 개시 의무 (필수 의존성 자동 확인 + 복구 or 요구)

세션 시작 직후, 모든 작업보다 먼저 의존성의 노출·설치·인증 상태 확인. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 설치·재인증 요구. 복구 완료 전까지 모든 작업 중단.

### 필수 의존성 SSOT

**MCP 서버 (1종)**:
- `github` — Issue/PR/sub-issue/comment·label·milestone 는 각 lane plugin self-write; `docs/{change-plans,adr,domain-knowledge,retros}/**` 직접 write 는 owner agent (CFP-26 Phase 0a)

**필수 플러그인 (9종)**:
- `codeforge-{review,pmo,requirements,test,develop,design}@mclayer` — 6 lane plugin
- `codex@openai-codex` — codeforge-review 의 CodexReviewAgent + codex CLI dependency
- `superpowers@claude-plugins-official` — agent md skill 의존
- `github@claude-plugins-official` — GitHub MCP 도구 노출

**필수 CLI (2종)**: `codex`, `gh`

**권장 플러그인 (4종, 미설치 시 권유만)**: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 확인·복구 절차

상세 절차는 [playbook §1.1](docs/orchestrator-playbook.md) checklist 0번 SSOT. 요약:
1. **노출 확인** — MCP `ToolSearch` / 플러그인 `~/.claude/settings.json` enabledPlugins / CLI `which` + `gh auth status`
2. **자동 복구 시도** — 플러그인 cache 있으나 disabled → settings.json 직접 토글
3. **사용자 요구** (자동 불가 · blocking wait) — `/mcp` 재인증 / `/plugins install <name>@<marketplace>` / CLI 설치 / `gh auth login`
4. **추가 검증** (consumer repo) — `.github/workflows/` 권장 6개 + ISSUE_TEMPLATE + PULL_REQUEST_TEMPLATE + CODEOWNERS 부재 시 알림 (자동 복사 안 함)

## Development Agent Team

Wrapper agent **0개** (ζ arc 완료, [ADR-009](docs/adr/ADR-009-wrapper-only-decomposition.md)). Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

| Lane | Plugin | Agent count | SSOT |
|---|---|---|---|
| 요구사항 | codeforge-requirements | 4 (PL + DomainAgent + RequirementsAnalyst + Researcher) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/CLAUDE.md) |
| 설계 | codeforge-design | 7 (PL + ArchitectAgent chief + 5 deputy) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
| 설계리뷰 / 구현리뷰 / 보안테스트 | codeforge-review | 5 (3 PL + 2 worker) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) |
| 구현 | codeforge-develop | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-develop/blob/main/CLAUDE.md) |
| 구현테스트 | codeforge-test | 1 (TestAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-test/blob/main/CLAUDE.md) |
| Cross-cutting | codeforge-pmo | 1 (PMOAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) |

각 lane plugin 의 agent 역할·동작은 해당 plugin CLAUDE.md SSOT. 본 표는 composition map 만.

**주체 명칭**: **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유) · **(Human) 사용자** = 인간 행위자 · **Cross-cutting** = 모든 레인에 걸쳐 작동하는 에이전트 (PMOAgent).

리뷰 워커 통합 근거: [ADR-001](docs/adr/ADR-001-review-agent-unification.md) (3 lane × 2 vendor → 2 lane-agnostic worker). [Inter-plugin Contract `review_verdict`](docs/inter-plugin-contracts/review-verdict-v2.md) versioning: [ADR-008](docs/adr/ADR-008-inter-plugin-contract-versioning.md).

## 레인 7개 · 단계 정의

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 구현 테스트 → 보안 테스트
```

모든 Story는 **full 7 레인** 통과. Fast-path 없음 (단 **Hotfix 경로** 2종은 예외 — 운영 장애 대응, 사후 감사 의무. 상세는 [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) §10 참조).

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md`
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**레인 진입 전 Preflight 체크 의무** — 각 레인 진입 직전 Orchestrator가 3개 체크 수행 (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성 가용). FAIL 시 block+report. 상세는 playbook §3B.

- **요구사항**: 사용자가 GitHub Issue Forms (story.yml) 제출 → `story-init.yml` Action이 자동 `<KEY>` 번호 계산 + `docs/stories/<KEY>.md` 생성 (§1 verbatim, §2-11 placeholder) + Phase 1 PR 자동 open + Issue body link 변환 → RequirementsPLAgent 아래 **병렬** (DomainAgent · Analyst · Researcher 동시 스폰, 각자 독립 관점) → RequirementsPL이 세 결과 dedup·상충 조정 → §2/§5/§6 직접 self-write + §3-4 갱신 (codeforge-requirements self-write 표)
- **설계**: ArchitectPLAgent가 CodebaseMapper(변호자) · Refactor(혁신자) · SecurityArchitectAgent(위협 변호자) · TestContractArchitectAgent(QA perspective contributor) · DataMigrationArchitectAgent(데이터 무결성 변호자) **5 deputy 병렬 스폰** → ArchitectAgent(chief author)가 통합 → Change Plan 확정 (§7 보안 설계 + §8 Test Contract + §11 데이터 마이그레이션 포함) → ArchitectAgent가 `docs/change-plans/<slug>.md` + 신규 `docs/adr/ADR-NNN-<slug>.md` direct write (CFP-26 Phase 0a 후) + ArchitectAgent 가 Story file §7/§3/§11 직접 self-write (CFP-40 codeforge-design 추출 후 — codeforge-design self-write 표)
- **설계 리뷰**: DesignReviewPL이 Claude/Codex 설계 리뷰 종합 → PASS 시 `gate:design-review-pass` 라벨 부착 → Phase 1 PR mergeable → merge → 구현 진입 / FIX 시 ArchitectPLAgent 회귀 → ArchitectAgent (chief author) 재스폰 (최대 3회)
- **구현**: Phase 2 PR open (DeveloperPL 이 첫 commit 준비 후 직접 `mcp__github__create_pull_request` — codeforge-develop self-write 표). Orchestrator가 QADev + DeveloperPL 병렬 스폰. DevPL이 프로젝트 `role: dev` roster를 동적 discover해 의존성 없는 한 **모두 병렬** 스폰. ArchitectPLAgent가 stateless 재스폰되어 매핑표 감사
- **구현 리뷰**: CodeReviewPL이 Claude/Codex 코드 리뷰 종합 → PASS 시 구현 테스트 진입 / FIX 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (최대 3회)
- **구현 테스트**: TestAgent (기능 → 성능 순차). ALL PASS 시 보안 테스트 진입 / FAIL 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (무제한)
- **보안 테스트**: 1차 layer = Dependabot/CodeQL/Secret Scanning/Push Protection (GitHub native). 2차 layer = SecurityTestPL이 Claude/Codex 보안 테스트 종합 (OWASP·CWE·CVE·trust boundary·credential). PASS 시 `gate:security-test-pass` 라벨 → Phase 2 PR mergeable → merge → Story 완료 / FAIL 시 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 (무제한)

## 오케스트레이션 규칙

> **Orchestrator 행동 SSOT**: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) — 세션 생명주기, 사용자 상호작용, 스폰 프롬프트 템플릿, 병렬 스폰 판단, docs file 동기화 체크리스트, FIX 상태 머신, 세션 재개 복원, 토큰 예산, 트러블슈팅.

### 플랫폼 제약
하위 에이전트는 Agent 툴 사용 불가 — 재귀 스폰 금지. 모든 스폰은 최상위 Claude가 직접. 서브에이전트 간 직접 통신 불가 (Orchestrator 경유).

### 컨텍스트 전달

각 Story 마다 `docs/stories/<KEY>.md` 가 SSOT. 에이전트 프롬프트는 docs file 경로 주입, 본문은 에이전트 자체 fetch. Context Packet · §0 Live Progress · Project Config Packet 상세는 [playbook §12 + §14](docs/orchestrator-playbook.md) SSOT.

각 lane plugin 이 자기 owned section 직접 self-write — § Lane plugin self-write boundary 표 SSOT.

### Never-skippable 에이전트

각 lane plugin 의 PL agent + non-skippable sub-agent 는 해당 plugin CLAUDE.md SSOT. wrapper Orchestrator 는 lane 진입 시 PL agent 1개만 spawn — PL 이 sub-agent fan-out 책임. `role: dev` 만 조건부 생략 (Change Plan 경로 매핑 따라).

### 스폰 시퀀스

각 lane 별 상세 스폰 흐름·branch logic 은 [playbook §3 스폰 시퀀스](docs/orchestrator-playbook.md) SSOT. 요약:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → 보안테스트
```

각 lane 진입 시 Orchestrator 가 해당 lane plugin 의 PL agent 를 spawn → PL 이 sub-agent 병렬 spawn (요구사항 3개 / 설계 5 deputy / 리뷰 2 worker / 구현 N role:dev). PL 산출물 종합 후 Orchestrator 에 verdict return → 다음 lane 라우팅.

**Clarification 재스폰**: 서브에이전트 one-shot 이라 PL ↔ 서브 continuous dialog 불가 → PL 이 Orchestrator 에 재 spawn 의뢰 (각 lane plugin CLAUDE.md SSOT).

**Track 병렬** (R7 — 설계리뷰 PASS 시): Track A (DesignReviewPL self-write merge gate) ∥ Track B (DeveloperPL Phase 2 PR 준비). 상세 [playbook §3.1](docs/orchestrator-playbook.md).

### FIX 루프

**판정 SSOT**: codeforge-review 의 [`templates/review-pl-base.md`](https://github.com/mclayer/plugin-codeforge-review/blob/main/templates/review-pl-base.md) §3 — severity 종합·dedup·종합 판정. codeforge core 입장에서는 [`docs/inter-plugin-contracts/review-verdict-v2.md`](docs/inter-plugin-contracts/review-verdict-v2.md) §3.2 review_verdict.status 필드 (PASS / FIX / FIX_DISCRETIONARY) 가 contract surface.

**트리거** (review-pl-base.md §3 결과 FIX 또는 FIX 재량):
- 설계 리뷰 → ArchitectPLAgent 회귀
- 구현 리뷰 / 구현 테스트 / 보안 테스트 FAIL → DeveloperPL 1차 진단 + ArchitectPLAgent 최종 판정 (parallel diagnosis, R4)

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 (CFP-32 monopoly · `fix-event-v1` contract). GitHub Issue 라벨은 보조 지표 (fix-ledger-sync.yml Action 자동 mirror).

**§10 FIX Ledger 스키마**:
```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
```

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](docs/orchestrator-playbook.md) SSOT.

### 원인 판정 decision table (설계 리뷰·구현 리뷰·구현 테스트·보안 테스트 FAIL 시)

**프로세스**: 설계 리뷰 FIX는 DeveloperPL 개입 없이 ArchitectPLAgent 직접 회귀. 구현 리뷰·구현 테스트·보안 테스트 FIX는 DeveloperPL 1차 원인 진단 → Orchestrator 경유 → ArchitectPLAgent 최종 판정. 모든 경우 evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무. Story file §10 FIX Ledger에 누적.

| Failure 유형 | 1차 가정 | 설계 원인 escalate 조건 |
|---|---|---|
| **설계 리뷰 P0 §7 누락** | **설계** | 항상 설계 (ArchitectAgent chief author 미흡) |
| Unit test FAIL | 구현 | 테스트 사양이 Change Plan 계약과 불일치 |
| Integration test FAIL | 구현 | 모듈 경계·계약 위반 |
| Infra test FAIL | 구현 | 배포/환경 요구 Change Plan 누락 |
| 성능 test FAIL | **설계** | 단순 최적화로 해결되면 구현 |
| Code review P0 보안 | 구현 | trust boundary 설계 오류 |
| Code review P0 아키텍처 | **설계** | 레이어·의존성 방향 위반 |
| **Code review P1 품질 (local)** | 구현 | 단일 파일·함수 내 품질 (naming, 작은 중복, 가독성) |
| **Code review P1 품질 (boundary)** | **설계** | 모듈 경계·인터페이스·패턴 일관성 (여러 파일 공통 이슈, 설계 지침 부재) |
| **보안 테스트 P0 injection·credential hardcode** | 구현 | 코드 단위 결함 |
| **보안 테스트 P1 암호학 오용·CVE** | 구현 | 코드 수정·버전 업그레이드로 해결 |
| **보안 테스트 P1 boundary 권한 일관성** | **설계** | 여러 파일·레이어 공통 지침 부재 |
| **보안 테스트 P0 trust boundary 위반** | 구현 | §7.1에 boundary 부재·모순 또는 §7.1과 코드 boundary 불일치 → 설계 |
| **보안 테스트 P0 auth/authz 결함** | 구현 | §7.3 인증·권한 모델 자체 결함 → 설계. 모델은 맞으나 구현 결함 → 구현 유지 |
| **구현 테스트 Migration FAIL · data integrity 위반 · rollback 실패** | 구현 | §11.1-§11.5 부재·모순 (schema 영향 누락 / Migration 전략 부재 / Rollback 경로 부재 / invariant 정의 부재) → 설계. 모델은 맞으나 script 결함 → 구현 유지 |

**P1 품질 local vs boundary 판정 기준**:
- **local**: finding이 1개 파일 또는 1개 함수 범위에 한정, 설계 결정과 무관한 개별 구현 결함
- **boundary**: finding이 여러 파일·계층에 걸침, 또는 Change Plan에 "이 경계·패턴 어떻게 가야 하는지" 지침이 부족해서 발생한 이슈
- DeveloperPL이 1차 진단 시 이 분류를 포함 → ArchitectPLAgent 최종 판정

- **설계 원인 판정 시**: Change Plan 갱신 (특히 §3 도입할 설계 / §6 리팩터링 선행 / §7 보안 설계 / §8 Test Contract 중 해당 항목) → Phase 1 follow-up PR → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, Phase 2 PR commit append → 구현 리뷰 재실행

### Review severity 종합 규칙

3 review/test PL(DesignReviewPL · CodeReviewPL · SecurityTestPL) 공통 — **codeforge-review plugin 소속**. SSOT는 codeforge-review repo의 `templates/review-pl-base.md` §3 (dedup · 종합 판정 표 · noise 분류). 본 CLAUDE.md에서는 SSOT 참조만 두고 표를 재인용하지 않는다.

### Design / Code / Security 리뷰 책임 매트릭스 (중복 방지)

네 레인의 체크 항목이 겹치지 않도록 분담. 한쪽에서 커버된 항목은 다른 쪽에서 재검토하지 않음.

| 체크 항목 | DesignLane | DesignReview | CodeReview | SecurityTest |
|-----------|:----------:|:------------:|:----------:|:------------:|
| Change Plan 완결성(§1-10 섹션 존재) | — | ✅ | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — |
| API 계약 일관성 (라우트·스키마·타입) | — | ✅ | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — |
| 성능 baseline §8.3 프로토콜 타당성 | — | ✅ | — | — |
| **§7 Trust boundary 정의** | ✅ | (감사) | — | (검증) |
| **§7 Threat model (STRIDE-LITE)** | ✅ | (감사) | — | — |
| **§7 Auth/Authz 모델 결정** | ✅ | (감사) | — | (검증) |
| **§7 민감 데이터 분류·흐름** | ✅ | (감사) | — | (검증) |
| **§7 위협↔완화 매핑** | ✅ | (감사) | — | (검증) |
| **§7 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§11 Schema 변경 영향** | ✅ | (감사) | — | (검증) |
| **§11 Migration 전략** | ✅ | (감사) | — | (검증) |
| **§11 Rollback 경로** | ✅ | (감사) | — | (검증) |
| **§11 Data integrity invariant** | ✅ | (감사) | — | (검증) |
| **§11 Backfill / 기존 데이터 처리** | ✅ | (감사) | — | (검증) |
| **§11 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| 코드 ↔ Change Plan 변경 계획 준수 | — | — | ✅ | — |
| 코드 스타일·네이밍·가독성 | — | — | ✅ | — |
| 테스트 코드 품질 (커버리지·경계·mock 경계) | — | — | ✅ | — |
| 런타임 오류 가능성 (null·타입·race 일반) | — | — | ✅ | — |
| 레이어 경계·의존성 방향 준수 | — | 부분(패턴 수준) | 주(실구현) | — |
| Impl Manifest §8.5 ↔ 실제 파일 일치 | — | — | ✅ | — |
| Injection 공격 표면 (SQL·Command·Template·NoSQL) | — | — | — | ✅ |
| **Trust boundary 위반 (외부 입력 검증 누락)** | (설계) | — | — | ✅ (코드 준수 검증) |
| Credential / secret 노출 (hardcoded·log·error) | — | — | — | ✅ (1차: Secret Scanning) |
| **Auth / 세션 결함 (CSRF·session fixation·JWT 무결성)** | (설계) | — | — | ✅ (코드 준수 검증) |
| 암호학 오용 (weak algo·nonce reuse·ECB·hardcoded key) | — | — | — | ✅ |
| **민감 데이터 유출 (PII·금융·헬스 데이터 로그·응답)** | (설계 분류) | — | — | ✅ (런타임 노출 검증) |
| 의존성 CVE 스캔 | — | — | — | ✅ (1차: Dependabot) |
| 정적 분석 결함 | — | — | — | ✅ (1차: CodeQL) |
| 설정·배포 보안 (default credential·open port·TLS) | — | — | — | ✅ |
| Race / TOCTOU 보안 취약 | — | — | — | ✅ |

> **DesignLane vs SecurityTest**:
> - DesignLane(SecurityArch) = "**어디에 boundary가 있어야 하는가**" — 설계 결정 (예방)
> - SecurityTest = "**코드가 그 boundary를 지키는가**" — 구현 검증 (검출)
> - 두 lane이 같은 카테고리(예: trust boundary)를 다루지만 **시점이 다름**: 설계 결정 vs 코드 준수
> - DesignReview는 "§7 보안 설계 자체의 완결성"을 감사 (추가 보안 검토 X — SecurityArch 산출물이 충분한가만)

- **DesignLane**: 대상은 설계 단계의 보안 결정 (SecurityArchitectAgent 산출물 → ArchitectAgent §7 반영). trust boundary·threat model·auth model·민감 데이터 흐름 정의
- **DesignReview**: 대상은 문서(Change Plan + ADR). 실구현 코드 미검토. §7 보안 설계 완결성 감사
- **CodeReview**: 대상은 코드(src·config·deploy·tests). 일반 품질·런타임 결함·테스트 품질 중심. 보안은 SecurityTest가 깊게 검증
- **SecurityTest**: 대상은 코드 + 인프라 + 의존성. 보안 카테고리 전담. 1차 layer는 GitHub native 도구(Dependabot/CodeQL/Secret Scanning), 2차 layer는 Claude/Codex 통합 워커(lane=security packet)
- 중복 지적 발생 시 해당 레인의 ReviewPL이 dedup → severity 높은 쪽 채택

### PMOAgent (Cross-cutting)

스폰 트리거: Epic 창설 / Story 완료 회고 / 사용자 요청. 단일 Story lane 게이트에 개입 없음. 상세 동작·산출물 schema 는 [codeforge-pmo CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) SSOT.

### Lane plugin self-write boundary

`docs/**` + GitHub Issue/PR/comment + label 영역의 write 책임은 lane plugin 별로 분산. wrapper repo 자체에는 agent 0개 — Orchestrator 가 lane plugin 을 spawn 하면 lane plugin 이 자기 owner section 을 직접 write.

**Lane plugin owner path**:

| Lane plugin | docs/ self-write 영역 | GitHub self-write |
|---|---|---|
| codeforge-requirements | `docs/stories/<KEY>.md §2·§5·§6`, `docs/domain-knowledge/<area>/<topic>.md` | `[요구사항]` prefix comment, phase:요구사항→phase:설계 transition, Discussions Q&A routing |
| codeforge-design | `docs/stories/<KEY>.md §3·§7·§11`, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md` | `[설계]` prefix comment, phase:설계→phase:설계-리뷰 transition |
| codeforge-review | `docs/stories/<KEY>.md §9` (각 Review PL) | `[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]` prefix comment, gate:design-review-pass / gate:security-test-pass label, phase transition (review-verdict-v2) |
| codeforge-develop | `docs/stories/<KEY>.md §8·§8.5`, Phase 2 PR creation | `[구현]` prefix comment, phase:구현→phase:구현-리뷰 transition |
| codeforge-test | (§9.3 은 Orchestrator 가 verdict receipt 후 처리 — lane plugin 직접 write 안 함) | `[구현-테스트]` prefix comment |
| codeforge-pmo | `docs/retros/<sprint>.md`, `docs/stories/<KEY>.md §11`, Epic Issue body, Milestone description | `[PMO]` prefix comment, Epic Milestone via gh api |

**Wrapper Orchestrator 단독 영역**:
- `docs/stories/<KEY>.md §10` FIX Ledger append (CFP-32 monopoly · `fix-event-v1` contract)
- general `docs/**` write (lane plugin owner 외)
- branch protection · CI workflow · cross-plugin schema templates

**4 single-owner doc** (CFP-26 Phase 0a 이후): `docs/{change-plans,adr,domain-knowledge,retros}/**` 는 owner agent direct write — lane plugin 의 ArchitectAgent / DomainAgent / PMOAgent 자기 owner path write.

문서화 표준 4 single-owner doc 템플릿은 [`templates/`](templates/) — change-plan / adr 현재 존재, domain-knowledge schema / retro schema CFP-27 신설. owner agent는 본인 owner path write 시 해당 템플릿 schema 준수 필수 — `scripts/check-write-permission-redistribution.sh` (CFP-26) + 향후 frontmatter/section schema lint (CFP-27)에서 강제.

자세한 owner path / mechanism / trigger 는 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 (codeforge-{review,pmo,requirements,test,develop,design}) 참조.

## Inter-plugin Contract (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](docs/inter-plugin-contracts/) 디렉터리는 두 종류 보유:

### kind:contract (typed inter-plugin schema, 6 entry / 7 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 는 [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

| Contract | Producer plugin | Files (wrapper sibling) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Active) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Active) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Active) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |

각 wrapper sibling 은 lane plugin canonical 의 verbatim mirror + "**상위 SSOT 위치**" 섹션. canonical 변경 시 wrapper sibling sync PR 후속 의무 ([ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)).

### kind:registry (cross-cutting protocol, 3 file)

wrapper-owned. 본 lint scope 밖 — `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

- [comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly
- [label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy

### Versioning + sync 정책

- [ADR-008 Inter-plugin Contract Versioning](docs/adr/ADR-008-inter-plugin-contract-versioning.md): SemVer 룰 (v1.x backward-compat, v2.0 BREAKING + 양쪽 plugin 동시 bump + 새 ADR)
- [ADR-010 Inter-plugin Contract Sibling Sync](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md): canonical/sibling 책임 + sync 트리거 + 신규 contract 추가 4단계 절차

### Write boundary

각 lane plugin 이 자기 contract 의 producer + self-writer. wrapper Orchestrator 는 contract verdict 에 응답해 다음 lane 라우팅·Story §10 FIX Ledger 만 처리. 상세 흐름은 [docs/orchestrator-playbook.md](docs/orchestrator-playbook.md) 참조.

---

## ADR (`docs/adr/` SSOT)

- **위치**: `docs/adr/ADR-NNN-<slug>.md` (flat). frontmatter `category:` 필드로 분류
- **목록**: `Glob(docs/adr/ADR-*.md)` + `Grep` frontmatter category·status 필터
- **상세**: `Read(docs/adr/ADR-NNN-<slug>.md)`
- **CODEOWNERS** 가 `docs/adr/**` 을 architect team review 강제 → ADR 변경은 Phase 1 PR 로 architect 결재 필수

### 생성 기준

라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 도메인 핵심 개념 (consumer overlay 가 도메인 특화 기준 추가)

DesignReview 의 ADR 정합성 체크 (Change Plan §3·§7 ↔ ADR 위반 검출) 는 [codeforge-review CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) SSOT.

### 페이지 템플릿

[`templates/adr.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/adr.md) 참조 (CFP-40 으로 codeforge-design 추출 후 SSOT 위치).

## 버그 기록 (GitHub Issues)
- Issue Forms: `.github/ISSUE_TEMPLATE/bug.yml`. Severity dropdown (P0/P1/P2)
- 신규 버그: Orchestrator 또는 해당 lane agent 가 `mcp__github__issue_write(action='create', title=..., body=..., labels=['type:bug', 'component:<name>'])`
- 해결 시: PR body에 `Closes #<bug-issue>` keyword → merge 시 자동 close (GitHub native)

## GitHub Workflow

사용자 요구사항 접수부터 PR merge 까지의 워크플로우 자동화. wrapper 가 templates/github-workflows/ 6종 fixture 제공:

- `story-init.yml` — Issue Forms (story.yml) 제출 → docs file 생성 + Phase 1 PR 자동 open
- `phase-label-invariant.yml` — `phase:*` single-active 강제
- `story-section-1-immutable.yml` — §1 line range 변경 PR 자동 reject
- `subissue-from-impl-manifest.yml` — §8.5 매핑표 → file 단위 sub-issue 자동 생성
- `phase-gate-mergeable.yml` — required status check (linked Story Issue 의 phase + gate 라벨 검사)
- `fix-ledger-sync.yml` — §10 FIX Ledger commit 감지 → Issue `[FIX #N]` mirror + `fix:<레인>-retry` 라벨 자동

상세 hierarchy (Epic / Story / sub-issue / Audit) · phase / gate / fix label 분류 · 코멘트 규칙 · 대시보드 search syntax 는 [docs/consumer-guide.md](docs/consumer-guide.md) §1.3 + [docs/inter-plugin-contracts/label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) + [docs/inter-plugin-contracts/comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) SSOT.

### Branch protection + Required status checks

- Main 브랜치: `phase-gate-mergeable` required status check + CODEOWNERS review 필수
- CODEOWNERS template: [`templates/CODEOWNERS.template`](templates/CODEOWNERS.template)

## Story 작성 의무 (모든 변경 적용)

매 변경 시작 시 Orchestrator가 cutoff 분류 → 강제/면제 결정. **모호 시 강제 측 분류** (false positive < false negative). 이 정책은 plugin 자체와 consumer 프로젝트 모두에 적용.

### 강제 대상 (Story file 작성 의무)

- 신규 ADR 결정 / 기존 ADR 변경
- 아키텍처·도메인 모델 추가·삭제·재정의
- 에이전트 추가·삭제·역할 재정의
- Workflow 정의(`templates/github-workflows/**`) 변경
- SSOT 문서(`templates/`·`presets/`·`CLAUDE.md`·`docs/orchestrator-playbook.md`) 의미 변경
- Breaking change · consumer migration 영향

### 면제 대상 (chore commit OK)

- Typo · 문법 · 줄바꿈 · 마크다운 형식 정리
- 링크 깨짐 수정 / 죽은 링크 제거
- Lint 자동 fix · dependency lock · version bump (security 영향 없는 경우)
- README 단순 문구 수정

면제 시 commit body에 `Story 면제 사유: <이유>` 1줄 명시 의무. 사유 없는 면제 commit은 PR review에서 reject 대상.

### Consumer overlay 확장

Consumer는 `.claude/_overlay/project.yaml`의 `story_cutoff.additional_exempt_categories[]`로 도메인 특화 면제 항목을 추가할 수 있다 (예: "auto-generated migration files", "vendored library updates"). **강제 항목 축소는 불허** — 안전 방향(면제 추가) 확장만 허용. Schema는 [`docs/project-config-schema.md`](docs/project-config-schema.md) §2 참조.

### Plugin 자체 적용 (dogfooding)

이 plugin repo도 동일 정책 적용. KEY prefix는 `CFP` (CodeForge Plugin). Plugin meta 변경은 §8 Test Contract / §9 리뷰·테스트 결과 등 무의미한 lane을 `N/A — <사유>`로 명시 (lane 게이트 면제 audit trail). 인프라 자동화는 단계적 도입:

- **1단계 완료** (CFP-1): Story 작성 의무 정책 + `docs/stories/` 디렉토리 + 수동 Story 작성
- **2단계 완료** (CFP-2): `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` + `.github/workflows/`에 6종 워크플로우(story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync) + `.github/PULL_REQUEST_TEMPLATE.md` + `.github/CODEOWNERS` 도입
- **3단계 향후** (CFP-5 잠정): `templates/**` ↔ `.github/**` parity + frontmatter ↔ CLAUDE.md 표 ↔ `.claude-plugin/plugin.json` 정합 자동 점검 CI. SSOT drift 자동 차단
- **End-to-end 실증 향후** (CFP-7 잠정): 임의 plugin meta 변경을 GitHub Issue Form으로 시작 → workflow 자동 동작 첫 검증

**Branch protection** (수동 적용, GitHub Settings > Branches): main 브랜치에 `phase-gate-mergeable` required status check 권장. 1인 maintainer 환경에서는 `Require review from Code Owners`는 OFF 권장 (PR self-merge 차단 방지).

판단 시점: Orchestrator가 변경 시작 시 cutoff 분류 선언, commit 직전 재확인.

## docs/stories markdown 규약 요약

- 위치: `docs/stories/<KEY>.md` (single-file SSOT, KEY = `<github.story_key_prefix>-N`)
- Template: [`templates/story-page-structure.md`](templates/story-page-structure.md). story-init.yml Action이 신규 생성
- 각 lane plugin 이 자기 owned section 직접 갱신 (§ "Lane plugin self-write boundary" 표 참조)
- 세부 규약·섹션 책임: 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 SSOT (codeforge-{review,pmo,requirements,test,develop,design})
- §1 변조 금지 invariant: `story-section-1-immutable.yml` Action이 강제
- **Retro page schema** (참고): `docs/retros/<sprint>.md` 페이지는 PMOAgent 직접 write — 형식은 [`templates/retro.md`](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/templates/retro.md) (CFP-27 신설) 따름. `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 검증 (warning 모드)

## Domain Knowledge

- 위치: `docs/domain-knowledge/<area>/<topic>.md` (계층 구조). Consumer overlay가 area 자유 정의
- CODEOWNERS가 `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review
- DomainAgent 입력 4소스: `docs/domain-knowledge/**` + `docs/adr/**` + 도메인 코드 + 사용자 원문 §1
- Q&A는 GitHub Discussions의 "Domain Q&A" 카테고리 (consumer overlay `github.discussions.domain_kb_category` 지정)
- **페이지 schema**: [`templates/domain-knowledge.md`](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/templates/domain-knowledge.md) (CFP-27 신설). frontmatter (title / area / topic_slug / status / sources / related_adrs / related_stories / updated) + 본문 섹션 (`## 정의 / ## 컨텍스트 / ## 핵심 규칙 / ## 경계 / ## 관련 ADR / ## 변경 이력`). `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` 검증 (warning 모드)
