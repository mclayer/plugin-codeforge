# Changelog

`codeforge` 플러그인 릴리스 이력. 각 엔트리는 버전 bump 단위.
Breaking change 있는 버전은 [`docs/migration-guide.md`](docs/migration-guide.md) 해당 섹션 참조.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.10.0] — 2026-04-27 (Self-application 6 layer 완성 — CFP-1~16)

### Architecture
- **Plugin self-application 정합화 sprint** — 16 CFP Story로 6 layer 완성:
  1. **정책** (CFP-1): `story_cutoff` policy + dogfooding rule (CLAUDE.md "Story 작성 의무" 섹션)
  2. **인프라** (CFP-2): GitHub Issue Forms 3종 + 6 workflows + CODEOWNERS + PR template
  3. **메타 정합** (CFP-4): story-init.yml drift sync + CLAUDE.md self-application stage 정정 + plugin.json 메타
  4. **CI invariant** (CFP-5/6/7/8/9/10/13/16): `invariant-check.yml` 8 step (workflow parity / version match / agent count / write queue 권한 / ADR-002 footer / 3-lane category enum / migration-guide BREAKING / severity overrides count+breakdown)
  5. **SessionStart 부트스트랩** (CFP-12): `overlay/hooks/check-bootstrap.sh` (org permission + 18 label 자동 검출, non-blocking) + `scripts/bootstrap-labels.sh` (idempotent 부트스트랩)
  6. **end-to-end 실측** (CFP-11): Issue Form → workflow chain 첫 실증 + 3 drift 발견·정합 회복
- **ADR-003 도입**: SSOT drift 검출·회복 책임을 3 layer로 분리 (CI invariant / SessionStart 부트스트랩 / 사용자 가이드) — 향후 새 drift 검출 추가 시 layer 결정 기준 (Q1-Q3 tree)
- **CFP-15 폴리시**: story-init workflow의 docs h1·PR title에서 `[STORY]` prefix strip (cosmetic 정합)

### Added
- `.github/workflows/invariant-check.yml` (CI level layer)
- `overlay/hooks/check-bootstrap.sh` (SessionStart non-blocking 진단)
- `scripts/bootstrap-labels.sh` (consumer 1회 부트스트랩)
- `docs/adr/ADR-003-three-layer-drift-responsibility.md`
- `docs/stories/CFP-1.md` ~ `CFP-16.md` (15 Story files; CFP-3 deferred)
- `docs/change-plans/cfp-*.md` (대응 Change Plan 14건)

### Changed
- `overlay/hooks/regen-agents.sh` — SessionStart에 `check-bootstrap.sh` 호출 wiring (`|| true` 비차단)
- `overlay/hooks/validate_config.py` — `story_cutoff.additional_exempt_categories` schema + unknown key reject (CFP-1 invariant 영구 보존, CFP-6)
- `.github/workflows/story-init.yml` — sed Korean range bug fix (Python re.UNICODE 교체) + `[STORY]` prefix strip
- `docs/adr/ADR-002-docsagent-inherit-footer-pattern.md` — §3.2 path example 오타 정정
- `docs/consumer-guide.md` — §2d label bootstrap script 자동화 참조 + §2g org permission 부트스트랩 단계 신설
- `CLAUDE.md` — "Story 작성 의무 (모든 변경 적용)" 섹션 추가 (cutoff 정책 + dogfood 단계)
- `docs/project-config-schema.md` — `story_cutoff.additional_exempt_categories` schema 추가

### Migration

v0.9 → v0.10은 **non-BREAKING** (모든 추가는 opt-in 또는 자동 적용). consumer 마이그레이션 절차 없음.

다만 **권장**:
- 신규 invariant-check.yml은 plugin maintainer 전용 — consumer는 복사 불필요
- consumer는 `bash scripts/bootstrap-labels.sh` 1회 실행으로 18 plugin label 일괄 부트스트랩
- consumer-guide §2g 따라 org-level "Workflow permissions" 활성화 (story-init.yml의 PR auto-create 정상 동작 조건)

## [0.9.0] — 2026-04-26 (BREAKING — Review/Test 워커 통합)

### Breaking
- **3 lane × 2 vendor = 6 워커 → 2 워커로 통합** ([ADR-001](docs/adr/ADR-001-review-agent-unification.md)). consumer overlay에 `agents/Claude{Design,Code,SecurityTest}ReviewAgent.md` 또는 `Codex...` 파일이 있다면 마이그레이션 필요
- 24 core agents → **20 core agents** (워커 6 삭제, 워커 2 신규)
- Codex 플러그인 단일 의존성: 미설치 시 3 리뷰 lane 모두 진입 불가 (이전: 각 lane별 개별 차단)

### Architecture
- **워커 통합**: `ClaudeReviewAgent` + `CodexReviewAgent` 2종이 lane=design/code/security 3 lane 공통 처리. 도메인은 호출 PL이 review packet으로 주입 (체크리스트·스코프·category enum·severity 자동 룰)
- **공통 base SSOT**: `templates/review-pl-base.md` — severity 종합·dedup·noise 분류·보고 형식·escalation 절차. 3 PL이 9번 복제하던 표가 1군데로
- **체크리스트 SSOT**: `templates/review-checklists/{design,code,security}.md` — consumer overlay가 도메인 특화 체크 추가 가능
- **Packet 누락 invariant**: 워커는 packet 필수 필드 누락 시 즉시 `ESCALATE_PACKET_INCOMPLETE` 반환 — generic fallback 금지
- 3 PL md 슬림화 (~120줄 → ~60줄): base 템플릿 참조 + lane-specific 4가지(체크리스트 packet·FIX 카운터 정책·검증 스코프·다음 게이트 라벨)만 본문에 명시
- SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여 — 1차 layer (Dependabot/CodeQL/Secret Scanning) 결과 fetch 후 packet inline 첨부
- 레인 명칭·라벨·워크플로우 invariant 그대로 유지 (`phase:보안-테스트`·`gate:security-test-pass`·`fix:보안-테스트-retry`)

### Added
- `docs/adr/ADR-001-review-agent-unification.md` (첫 ADR)
- `templates/review-pl-base.md` (3 PL 공통 base SSOT)
- `templates/review-checklists/design.md` · `code.md` · `security.md`
- `agents/ClaudeReviewAgent.md` · `agents/CodexReviewAgent.md` (lane-agnostic 워커)

### Changed
- `agents/DesignReviewPLAgent.md` · `agents/CodeReviewPLAgent.md` · `agents/SecurityTestPLAgent.md` 슬림화 (base + lane-specific만)
- `CLAUDE.md` (agent tree·never-skippable·write 권한 표·외부 도구 wrapper·Codex 의존성)
- `docs/orchestrator-playbook.md` (스폰 시퀀스 다이어그램·핵심 의무 표·외부 의존성 표·세션 회고 테이블)
- `docs/plugin-design.md` (agent enumeration)
- `agents/DocsAgent.md` (phase prefix 매핑·Codex 보고 기록 형식)

### Removed
- `agents/ClaudeDesignReviewAgent.md`
- `agents/CodexDesignReviewAgent.md`
- `agents/ClaudeCodeReviewAgent.md`
- `agents/CodexCodeReviewAgent.md`
- `agents/ClaudeSecurityTestAgent.md`
- `agents/CodexSecurityTestAgent.md`

### Migration
v0.8 → v0.9 마이그레이션:
1. consumer overlay에 6 워커 오버라이드가 있다면 → `ClaudeReviewAgent.md` / `CodexReviewAgent.md` 1쌍으로 통합 + lane-specific 부분은 `templates/review-checklists/<lane>.md`로 이동
2. SecurityTestPL이 `gh api repos/*` 호출하므로 GitHub 인증 (Dependabot/CodeQL/Secret Scanning alerts read 권한) 확인
3. CHANGELOG 기록·코멘트의 `Codex<Domain>ReviewAgent` 인용은 historical로 유지

## [0.8.0] — 2026-04-26 (BREAKING — Atlassian 제거 + GitHub 전환)

### Breaking
- **Atlassian backend 완전 제거** (Confluence/Jira). consumer는 GitHub-only로만 사용 가능
- `atlassian.*` project.yaml 스키마 → `github.*`로 교체 (org / repo / default_branch / pr_title_prefix_template / story_key_prefix / codeowners / discussions / milestone)
- 24 agents의 atlassian MCP 권한 제거. DocsAgent는 `mcp__github__*` write + gh CLI Bash fallback
- 필수 의존성: MCP `github` (`atlassian` 대체), 플러그인 4종 (`github@claude-plugins-official` 격상), CLI 2종 (`gh` 추가)
- 권장 플러그인 5종 → 4종 (`atlassian@claude-plugins-official` 제거, `github@claude-plugins-official`은 격상)

### Architecture
- **Story 페이지 → `docs/stories/<KEY>.md`** (single-file SSOT, §1-11)
- **ADR → `docs/adr/ADR-NNN-<slug>.md`** (flat, frontmatter `category:`)
- **Domain KB → `docs/domain-knowledge/<area>/<topic>.md`** (계층)
- **Story 1건 = PR 2건** (Phase 1 docs / Phase 2 code+docs append)
- **GitHub Workflow 자동화 6종**: story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync
- **보안 테스트 1차 layer**: Dependabot + CodeQL + Secret Scanning + Push Protection (GitHub native)
- **Phase 라벨 single-active invariant**: phase-label-invariant.yml Action이 강제
- **§1 변조 금지 invariant**: story-section-1-immutable.yml Action이 강제
- **CODEOWNERS**: `docs/adr/**`·`docs/change-plans/**`·`docs/stories/**` → architect team / `docs/domain-knowledge/**` → domain expert team
- **Branch protection**: phase-gate-mergeable required status check + CODEOWNERS review

### Added
- `templates/github-workflows/*.yml` 6개 (Action SSOT)
- `templates/github-issue-forms/*.yml` 3개 (story / bug / audit)
- `templates/github-pr-template.md` (Phase 1 / Phase 2 양식 분리)
- `templates/CODEOWNERS.template`
- `scripts/check-no-atlassian.sh`, `scripts/check-agent-frontmatter.sh`, `scripts/check-doc-links.sh`

### Changed
- `CLAUDE.md` major rewrite (atlassian 제거 + GitHub-native 워크플로우 + 세션 개시 의무 갱신)
- `docs/orchestrator-playbook.md` major rewrite (§1.1 / §3B / §11 / §12 / §12.5 갱신)
- `docs/project-config-schema.md` (atlassian.* 제거, github.* 신설)
- `docs/consumer-guide.md` (GitHub-native 셋업 절차)
- `agents/DocsAgent.md` major rewrite (권한 + GitHub primitive 매핑)
- 23 agents (frontmatter MCP + 본문 prose 일괄 변환)
- `templates/story-page-structure.md`, `adr.md`, `impl-manifest.md`, `change-plan.md`
- `presets/webapp/agents/*` (Jira/Confluence → GitHub Issue/PR)
- `.claude/settings.json`, `.claude/settings.local.json` (atlassian MCP 제거, github MCP + gh CLI 추가)
- `overlay/_overlay/project.yaml.example`, `overlay/_overlay/README.md`, `overlay/hooks/validate_config.py`, `overlay/hooks/tests/test_validate_config.py`
- `examples/*/.claude/_overlay/project.yaml` (3개 fixture)

### Migration
v0.7.x 이하에서 v0.8로 in-place 업그레이드 불가. 기존 consumer는 fresh GitHub-based setup 필요. [migration-guide.md](docs/migration-guide.md#v07--v08-atlassian-제거--github-전환) 참조.

### Affected — 32+ files
- Core: `CLAUDE.md`, `docs/orchestrator-playbook.md`, `docs/project-config-schema.md`, `docs/consumer-guide.md`, `docs/migration-guide.md`, `docs/plugin-design.md`, `docs/README.md`, `README.md`
- Agents: 24 agent .md 전부
- Templates: 4 templates 전부 + 신규 11개 (workflows · forms · CODEOWNERS · PR template)
- Settings: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/_overlay/project.yaml`
- Overlay/Hook: `overlay/_overlay/*`, `overlay/hooks/validate_config.py`
- Scripts: 신규 3개 검증 스크립트
- Examples: 3개 project.yaml fixture
- Presets: webapp agents 2개

## [0.7.1] — 2026-04-24

### Fixed (v0.7.0 병렬 모델 정합성 결함 보정)

- **§2 Story 페이지 섹션 타이밍 drift**: v0.7.0에서 Analyst·Researcher가 §2(DomainAgent 해석)를 입력 참조한다는 서술이 남아있었음. 병렬 모델에서 §2는 Domain 자신의 output destination이며 페이지 생성 시엔 placeholder → Analyst·Researcher 프롬프트에서 §2 참조 제거, templates/story-page-structure.md에 타이밍 주석 추가
- **섹션별 atomic 갱신 규정 누락**: Domain/Analyst/Researcher 결과를 배치로 기록하면 resume 시 부분 완료 감지 불가. DocsAgent가 §2·§5·§6 각각 **atomic 갱신** 의무 명시 (배치 금지)
- **Clarification 재스폰 로그 위치 불명**: §10 FIX Ledger와 구분이 모호 → **§9.0 "Clarification 재스폰 이력"** 섹션 신설, Jira `fix:*` 라벨 미추가 (게이트 실패 아님)
- **DesignReview 감사 항목 표류**: 병렬 모델에서 Mapper·Refactor 상호 대응이 없는데 "Mapper 변호 근거 일축 여부"를 두 에이전트 산출물에 묻는 서술이 남아있었음 → "**Architect 통합 판정**이 Mapper 변호를 근거 있게 일축·수용했는가"로 리프레이밍 (CLAUDE.md, ArchitectAgent, CodebaseMapper, Refactor 4곳)

### Added

- **§8.2 토큰 예산 peak/total 구분** (playbook): 병렬화로 peak concurrent context 증가 반영. 요구사항 peak 3× (~60k), 설계 peak 2× (~50k+Architect). "Peak 접근 시 순차 fallback 검토" 지침
- **§3B.3 Preflight 공통 입력 준비 체크**: 요구사항·설계 레인 진입 전 Orchestrator가 ADR 목록·코드 경로·Project Config Packet·Change Plan 초안 등 공통 입력 패키지 완비 확인 의무
- **§7.3 Resume 부분 완료 매핑**: §2·§5·§6 중 일부만 채워진 상태에서 중단됐을 때 비어있는 섹션의 에이전트만 선택 재스폰 (이미 채워진 섹션 재활용). 설계 레인도 동일 규칙
- **DocsAgent §2·§5·§6 null 결과 템플릿**: "공백 없음"·"추가 해석 불필요"·"외부 지식 보강 불필요" 판정 시 섹션 생략 금지 — 독립 관점 결과 보존을 위해 사유 기록 템플릿 명시

### Affected
- `CLAUDE.md`, `docs/orchestrator-playbook.md`, `templates/story-page-structure.md`
- `agents/DocsAgent.md`, `agents/DomainAgent.md`, `agents/RequirementsAnalystAgent.md`, `agents/ResearcherAgent.md`
- `agents/ArchitectAgent.md`, `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md`

### Migration
- Non-breaking (v0.7.0 semantic 유지, 정합성만 보정)
- Consumer overlay override가 §2를 입력으로 참조하던 경우 제거 필요

## [0.7.0] — 2026-04-24

### Changed
- **BREAKING (오케스트레이션 semantics)**: 요구사항·설계 레인 서브 에이전트 **sequential → parallel** 전환
  - 요구사항 레인: `DomainAgent → Analyst → Researcher` 순차 (조건부 생략 포함) → `DomainAgent ∥ Analyst ∥ Researcher 병렬` (셋 다 non-skippable)
  - 설계 레인: `CodebaseMapper → Refactor` 순차 (Refactor가 Mapper 요약 입력 수신) → `CodebaseMapper ∥ Refactor 병렬` (둘 다 원 소스 직접 독해, 산출물 교차 참조 없음)
  - 이유: 순차 모델에서 후속 에이전트가 선행 결과에 오염되어 **독립 관점** 소실. 병렬 모델에서 PL/Architect가 진정한 synthesizer 역할
- **Clarification 재스폰 프로토콜 신설**: 서브 에이전트는 one-shot 실행이므로 PL↔서브 continuous dialog 불가. PL이 통합 중 추가 질의 필요 시 Orchestrator 경유 재스폰 요청 (이전 출력 pointer + clarification context + 범위 제한). 동일 에이전트 2회 재스폰 이후 미해소면 사용자 ESCALATE

### Affected
- `CLAUDE.md` — 스폰 시퀀스·Never-skippable·병렬 스폰 권장·CodebaseMapper↔Refactor 대립 섹션 전면 개편
- `agents/RequirementsPLAgent.md` — 병렬 스폰 원칙·dedup·상충 조정 프로토콜·clarification 재스폰 절차 신설
- `agents/DomainAgent.md`, `agents/RequirementsAnalystAgent.md`, `agents/ResearcherAgent.md` — 타 에이전트 산출물 수신 제거, 각자 공통 입력에서 관점 자체 도출. Researcher·DomainAgent는 **non-skippable**로 승격 (null 결과도 명시 반환)
- `agents/ArchitectAgent.md` — 설계 레인 실행 흐름 8단계 재구성 (공통 입력 패키지 → 병렬 스폰 → 대립 조정 → clarification 재스폰)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` — 상호 산출물 미참조, 원 소스 직접 독해 의무. RefactorAgent에 "잠재 변호 논리 예상" 섹션 신설 (self-identify)
- `docs/orchestrator-playbook.md` — §3.2 스폰 템플릿 특이 블록, §4.2 표준 병렬 패턴 표에 요구사항·설계 레인 추가, §4.4 Clarification 재스폰 절차 신설, §7.3 resume 매핑 수정
- `templates/story-page-structure.md` — §6 "(Researcher, 조건부)" → "(Researcher)" + null 결과 보존 규정

### Migration
- Consumer overlay가 RequirementsPLAgent/ArchitectAgent 행동을 override하지 않는다면 영향 없음
- Override 중이면 `docs/migration-guide.md` §v0.6→v0.7 섹션 참조 — 병렬 스폰 지시 블록 추가 필요

## [0.6.0] — 2026-04-24

### Changed
- **BREAKING**: Plugin name rename `dev-orchestrator` → `codeforge`. `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/*` 경로 references 전부 `${CLAUDE_PLUGIN_ROOT}/codeforge/*` 로 교체
- Repo 예정 rename: `mctrader/plugin-codeforge` → `mctrader/plugin-codeforge` (PLG-19, admin UI)
- Atlassian workspace 이관: 플러그인 dev를 `mctrader.atlassian.net` PLG space + PLG project (component=codeforge)로 운영

### Added
- `.claude/_overlay/project.yaml` — 플러그인 자체의 dog-food config (PLG 좌표)
- Confluence PLG tree: CodeForge top + Stories/Domain Knowledge/ADR/Retrospective/Architecture Overview + 6 retroactive ADRs + 5 per-version retrospectives
- Jira retroactive: 6 Epics (v0.1~v0.5.x) + 11 Stories (PR 1:1)

### Migration
- v0.5.x 사용자: `docs/migration-guide.md` §v0.5→v0.6 섹션 참조 — consumer `.claude/settings.json` hook 커맨드 `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh` → `${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh` 교체 필수

## [0.5.1] — 2026-04-24

### Added
- **Project Config Packet** (playbook §12.5): Orchestrator가 `.claude/_overlay/project.yaml`을 세션 개시 시 1회 로드하고 Atlassian/GitHub 호출이 필요한 에이전트 (DocsAgent·RequirementsPL·DomainAgent·PMO) 프롬프트에 slice를 자동 주입 → 반복 `Read` 회피
- CLAUDE.md에 Project Config Packet 간단 언급 추가

### Changed
- `agents/DocsAgent.md` — Packet SSOT 우선, fallback으로 `Read` 명시

## [0.5.0] — 2026-04-24

### Added
- `overlay/hooks/validate_config.py` — `project.yaml` schema 검증기 (hand-rolled, PyYAML만 의존). Missing file=WARN, malformed YAML=exit 3, schema 위반=exit 4
- `regen-agents.sh`에 validator 통합 — SessionStart 시 자동 검증, 위반 시 abort
- `overlay/hooks/tests/test_validate_config.py` — 22 테스트 (unit + E2E + bundled examples 검증)
- `.github/workflows/test.yml` — GitHub Actions CI (PR/push to main): pytest + yaml 파싱 + example 스모크 + frontmatter 유효성
- `CHANGELOG.md` — SemVer 형식 릴리스 이력

### Changed
- `docs/project-config-schema.md` §6 신설 (Hook 통합 Schema 검증), §7 장래 확장 축소
- README.md "연혁" → CHANGELOG 링크로 축약

## [0.4.0] — 2026-04-24

### Added
- `.claude/_overlay/project.yaml` — consumer SSOT 상수 (Atlassian·GitHub·labels) 구조화 주입
- `docs/project-config-schema.md` — `project.yaml` schema SSOT (경계·필드·접근 규칙·missing 동작)
- `overlay/_overlay/project.yaml.example` — consumer 복사용 스켈레톤
- `examples/library-minimal/` — 라이브러리 shape consumer 예시 (preset 미사용, 공개 API 경로 scoping)
- `docs/migration-guide.md` — 버전업 절차 가이드 (v0.1 → v0.4)

### Changed
- `DocsAgent`·`DomainAgent` 등 Atlassian 호출 에이전트가 `project.yaml`을 `Read`하는 것 의무화
- `.claude/_overlay/CLAUDE.md` 역할 변경 — SSOT 상수 제거, narrative 컨텍스트 (도메인 해설·기술 스택 근거) 전담
- `examples/webapp-minimal/`·`examples/cli-tool-minimal/` overlay 재구성 (`project.yaml` 분리)
- `docs/plugin-design.md` Stage 2 partial 완료 표기

### Migration
- v0.3 사용자: `docs/migration-guide.md` v0.3→v0.4 섹션 참조 (CLAUDE.md overlay의 SSOT 상수를 project.yaml로 이동)

## [0.3.0] — 2026-04-24

### Added
- `agents/DeveloperAgent.md` — generic 구현 담당 (core, `role: dev`)
- `agents/InfraEngineerAgent.md` — 인프라·배포·패키징 전반 (ServerEng 리네임, 범위 확장)
- `presets/webapp/agents/` — 웹앱 preset (BackendDev·FrontendDev 이동)
- `presets/README.md`, `presets/webapp/README.md` — preset 개념·사용법 가이드
- `examples/webapp-minimal/`, `examples/cli-tool-minimal/` — consumer overlay 예시 2종
- `overlay/hooks/merge.py --overlay-only` — core 없는 consumer-defined agent 지원
- `overlay/hooks/tests/test_merge.py` — merge.py 계약 유닛·E2E 테스트 42건

### Changed
- **BREAKING**: `BackendDeveloperAgent`·`FrontendDeveloperAgent` → `presets/webapp/agents/`로 이동 (core에서 제거)
- **BREAKING**: `ServerEngineerAgent` → `InfraEngineerAgent`로 리네임 (범위 확장: systemd/Docker/K8s → 전 플랫폼 배포·패키징)
- **BREAKING**: `DeveloperPLAgent`가 하드코딩된 "4 Dev" 대신 `role: dev` frontmatter 태그로 런타임 roster discovery
- `merge.py` §4d 변경 — "core 없음 + overlay 있음"이 이전엔 abort였으나 이제 overlay-only 렌더
- Core agent 수: 25 → 24 (Backend/Frontend 제거 + DeveloperAgent 추가, ServerEng → InfraEng 리네임)

### Migration
- v0.2 사용자: `docs/migration-guide.md` v0.2→v0.3 섹션 참조 (preset 복사 또는 generic Dev로 전환, ServerEng→InfraEng 리네임)

## [0.2.0] — 2026-04-24

### Added
- **보안 테스트 레인** (7번째 레인) — `SecurityTestPLAgent` + `ClaudeSecurityTestAgent` + `CodexSecurityTestAgent`
- `templates/` 디렉토리 SSOT — `change-plan.md`, `adr.md`, `story-page-structure.md`, `impl-manifest.md`
- Claude + Codex peer 리뷰 3중 (설계·코드·보안)

### Changed
- 기존 "테스트" 레인 → "구현 테스트" + "보안 테스트" 2단계 분리
- FIX 루프: 보안 테스트 FAIL 시 Architect 원인 판정 (구현/설계) — 무제한 FIX

### Migration
- Non-breaking. Jira 대시보드 JQL에 `phase:보안-테스트` 라벨 추가 권장

## [0.1.0] — 2026-04-24

### Added
- 플러그인 pivot — 기존 crypto FW repo(`mctrader`)에서 범용 SW 개발 플러그인 `dev-orchestrator`로 재편 (v0.6.0에서 `codeforge`로 최종 rename)
- 22 에이전트 · 6 레인 오케스트레이션 구조
- Overlay 메커니즘 (β) — consumer 측 `.claude/_overlay/` + SessionStart merge hook
- `overlay/hooks/merge.py` + `regen-agents.sh` — core+overlay 병합 tooling
- Archive tag `archive/pre-plugin-pivot-20260424` — pivot 직전 상태 보존

### Breaking
- 기존 crypto FW 코드 전부 삭제 (`src/mctrader/**`, `tests/**`)
- `.claude/agents/` → `agents/` 경로 이동 (plugin core SSOT)
