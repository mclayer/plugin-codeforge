# Changelog

`codeforge` 플러그인 릴리스 이력. 각 엔트리는 버전 bump 단위.
Breaking change 있는 버전은 [`docs/migration-guide.md`](docs/migration-guide.md) 해당 섹션 참조.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [0.6.0] — 2026-04-24

### Changed
- **BREAKING**: Plugin name rename `dev-orchestrator` → `codeforge`. `${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/*` 경로 references 전부 `${CLAUDE_PLUGIN_ROOT}/codeforge/*` 로 교체
- Repo 예정 rename: `mctrader/mctrader` → `mctrader/plugin-codeforge` (PLG-19, admin UI)
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
