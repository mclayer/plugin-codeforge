# Changelog

`codeforge` 플러그인 릴리스 이력. 각 엔트리는 버전 bump 단위.
Breaking change 있는 버전은 [`docs/migration-guide.md`](docs/migration-guide.md) 해당 섹션 참조.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [2.0.0] - 2026-04-29

### CFP-37 (ζ arc) — codeforge-requirements plugin extraction (BREAKING)

ζ arc 세 번째 lane plugin 추출 (parent §5.7). 4 sub-agent (RequirementsPL + Domain + Analyst + Researcher) + 도메인 KB owner write + Story §2/§5/§6 self-write 를 별도 plugin `codeforge-requirements` 으로 이전.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.7.

### Removed (BREAKING for consumer)
- `agents/RequirementsPLAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/DomainAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/RequirementsAnalystAgent.md` → mclayer/plugin-codeforge-requirements
- `agents/ResearcherAgent.md` → mclayer/plugin-codeforge-requirements
- `templates/domain-knowledge.md` → mclayer/plugin-codeforge-requirements

### Changed
- `CLAUDE.md` 필수 플러그인 6종 → 7종 (`codeforge-requirements@mclayer` 추가). agent count 18 → 14
- `CLAUDE.md` Write queue 의뢰 권한 표 — 4 agent 제거 + 외부 plugin listing 갱신
- `CLAUDE.md` 외부 도구 wrapper 표 — RequirementsAnalyst codex CLI 의존성 codeforge-requirements 로 이전 표시
- 3 file 의 DomainAgent / domain-knowledge 링크 → mclayer/plugin-codeforge-requirements external URL
- `.claude-plugin/plugin.json` v1.0.0 → v2.0.0 BREAKING

### Why
ζ arc §5.7: 4 sub-agent 병렬 패턴이 본 plugin 의 응집성 핵심. 도메인 KB owner write 이전이 "writer-distributed + path-scoped permission travels with agent" 모델 검증 두 번째 사례 (CFP-36 PMOAgent retro 이전 다음).

### Migration (BREAKING)
- consumer install: `/plugins install codeforge-requirements@mclayer`
- 기존 docs/domain-knowledge/* 그대로 유지 (codeforge-requirements 의 DomainAgent 가 동일 path 직접 write)
- codex CLI 의존성: codeforge-requirements 측 SessionStart hook 이 검증 (codeforge wrapper 측 부담 해소)

### Followups (CFP-38+)
- CFP-38: codeforge-test (TestAgent 단독 — 가장 단순)
- CFP-39: codeforge-develop (5 agent + presets)
- CFP-40: codeforge-design (7 agent + change-plan/adr templates — 가장 큰 표면, last per Codex)

## [1.0.0] - 2026-04-29

### CFP-36 (ζ arc) — codeforge-pmo plugin extraction (BREAKING)

ζ arc 두 번째 lane plugin 추출 (parent §5.6). PMOAgent + retro template + retros owner write 를 별도 plugin `codeforge-pmo` 으로 이전. wrapper agent 수 감소 (writer-distributed 모델 본격 진행).

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.6.

### Removed (BREAKING for consumer)
- `agents/PMOAgent.md` — codeforge-pmo plugin 으로 이전
- `templates/retro.md` — codeforge-pmo plugin 으로 이전

### Changed
- `CLAUDE.md` 필수 플러그인 5종 → 6종 (`codeforge-pmo@mclayer` 추가). codeforge-review 항목 v1.0.0 retrofit 사실 반영
- `scripts/check-write-permission-redistribution.sh` — PMOAgent.md 부재 시 skip (extraction 후 wrapper 영역 외 invariant)
- `.claude-plugin/plugin.json` v0.22.0 → v1.0.0 BREAKING (consumer 신규 plugin install 의무)

### Why
ζ arc 로드맵 §5.6: PMOAgent 가 가장 작은 lane (1 agent) + 가장 약한 결합 (Cross-cutting, lane gate 무관) → writer-distributed 패턴의 두 번째 검증 단계로 적합. CFP-35 review v2 retrofit (코드 이동 0) 검증 후 코드 이전 첫 사례.

거부된 대안: PMOAgent를 wrapper 잔류 (overlay 충분 — Codex round 2 표면적 권고이지만 wrapper-only end-state 와 충돌), retro template 도 wrapper 잔류 (cross-plugin schema 인지 lane-owned 인지 모호 — codeforge-pmo 단일 owner 가 명료).

### Migration (BREAKING)
- consumer 측 install 추가 필수: `/plugins install codeforge-pmo@mclayer`
- 기존 docs/retros/* 그대로 유지 (codeforge-pmo의 PMOAgent 가 동일 path 직접 write — schema 변화 없음)
- CFP-26 Phase 0a single-owner write 모델 유지 (단 owner 가 wrapper 의 PMOAgent → codeforge-pmo 의 PMOAgent 로 이동)

### Validation
- 5 신규 lint 모두 PASS (PMOAgent.md 삭제 후에도 invariant 통과 — CFP-26 invariant 가 부재 시 skip 처리)
- codeforge-pmo plugin v0.1.0 정상 install 가능 (자체 SessionStart hook + regen-agents.sh)
- marketplace sync 동시 진행 (codeforge v1.0.0 + codeforge-pmo v0.1.0 신규 등록)

### Followups (CFP-37+)
- CFP-37: codeforge-requirements (RequirementsPL + Domain + Analyst + Researcher 추출)
- CFP-38: codeforge-test (TestAgent 추출)
- CFP-39: codeforge-develop (DeveloperPL + role:dev 추출)
- CFP-40: codeforge-design (가장 마지막 — 가장 큰 표면)

## [0.22.0] - 2026-04-29

### CFP-35 (ζ arc) — review_verdict v2 retrofit (Non-BREAKING for wrapper · BREAKING for codeforge-review)

ζ arc 첫 lane plugin self-write 검증 단계 (parent spec §5.5). codeforge-review v1.0.0 BREAKING + codeforge wrapper sibling sync.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.5. Codex round 2 sequencing 권고 (review v2 retrofit이 코드 이동 0의 첫 self-write 검증으로 적합).

### Added
- `docs/inter-plugin-contracts/review-verdict-v2.md` — sibling reference (canonical은 mclayer/plugin-codeforge-review repo)

### Changed
- `docs/inter-plugin-contracts/review-verdict-v1.md` status: Active → Deprecated. 본문 상단 deprecation 안내 추가 (6 CFP 무사고 후 archive 예정)
- `.claude-plugin/plugin.json` version 0.21.0 → 0.22.0

### Why
codeforge-review v1.0.0 BREAKING (Self-write 도입) 시 wire compatibility 위해 wrapper 도 동시 bump. wrapper 자체 코드 변경 없음 (Orchestrator는 verdict status·findings만 소비, write 책임은 codeforge-review로 이전).

거부된 대안: v1 + v2 동시 지원 (write 책임 분기 → DocsAgent 절반만 해체 = ζ arc 모호. v1 deprecate가 명료), wrapper BREAKING bump (실제 wrapper API/runtime 변화 없음 — minor 가 정확).

### Migration
**Non-BREAKING for wrapper consumer** — wrapper 자체 동작 변화 없음. 단 codeforge-review v1.0.0 동시 install 의무 (CFP-29 BREAKING 정책 동일).

- consumer: `gh plugins update codeforge-review` 후 `gh plugins update codeforge` (또는 동시 install)
- v1 contract reference (codeforge core CLAUDE.md "Inter-plugin Contract" 섹션) — Deprecated 표기 후 본문 변경 없음 (audit 보존)

### Validation
- All 10 lint scripts PASS (review-verdict-v2.md 신설로 inter-plugin-contracts 2 contract 검증)
- 1-2 dogfood Story (다음 real Story)에서 codeforge-review v1.0.0 self-write 정상 동작 확인 — 본 PR scope 외

### Followups (CFP-36+)
- CFP-36: codeforge-pmo 신설 (PMOAgent 이전 + retro template + pmo writer + pmo-output-v1 contract). v2 self-write 패턴 두 번째 검증

## [0.21.0] - 2026-04-29

### CFP-34 (ζ arc F3) — Workflow yaml syntax tests + marketplace sync drift detection (Non-BREAKING)

ζ arc 세번째 foundation step. 3 핵심 workflow yaml 의 regex 패턴 fixture 검증 + mclayer/marketplace mirrored 필드 drift CI 자동 감지. CFP-35+ lane plugin 추출 진입 전 Codex round 2 5조건 충족 마무리 단계.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.4. Codex round 2 조건 #3(workflow regex CI 사전 lint) + 조건 #4(marketplace 4-plugin 임계점 전 sync 자동화) 직접 대응.

### Added
- `scripts/check-workflow-yaml.sh` — 3 workflow (fix-ledger-sync · subissue-from-impl-manifest · phase-gate-mergeable) yaml syntax + 핵심 regex 패턴 존재 + Python re-impl fixture 검증
- `scripts/check-marketplace-sync.sh` — `.claude-plugin/plugin.json` mirrored 필드 (name/version/description/author) ↔ mclayer/marketplace marketplace.json plugins[name=local] entry 양방향 비교. drift 시 CI fail + sync 안내
- `.github/workflows/contract-lint.yml` — `workflow-yaml` + `marketplace-sync` job 2종 추가

### Changed
- `.claude-plugin/plugin.json` version 0.20.0 → 0.21.0

### Why
CFP-32 (SSOT 도입) + CFP-33 (lint harness)에 이은 ζ arc foundation 마무리. 본 CFP 후 Codex round 2 5조건 모두 충족 → CFP-35 review v2 retrofit 부터 lane plugin 추출 본격 진입 가능.

거부된 대안: marketplace 자동 PR 생성까지 단일 CFP 포함 (cross-repo PAT 설정 + secret 관리 추가 → 본 CFP scope 초과. drift 감지만 우선 도입, 자동 sync PR open 은 token 인프라 후속 CFP), workflow yaml regex 추출 + 직접 실행 (Node.js 설치 + js engine 통합 → 복잡도 대비 가치 낮음).

### Migration
**Non-BREAKING** — 본 CFP는 lint 추가 + version bump 만. consumer 영향 없음.

- 기존 9 lint job 그대로 + 신규 2 lint job (`workflow-yaml`, `marketplace-sync`)
- workflow yaml 변경 시 fixture와 drift 시 lint catch — yaml 의 핵심 regex 보호
- marketplace 동기 의무 자동 enforcement (CFP-24 정책 manual → automated)

### Validation
- 5 신규 lint 모두 정상 상태 PASS (workflow-yaml 3 fixture, marketplace-sync 양방향 비교)
- 기존 8 lint 회기 없음
- 의도적 yaml regex break 도입 → fixture fail 검증
- 의도적 plugin.json mirrored 필드 변경 (sync 누락) → CI fail 검증

### Followups (CFP-35+)
- CFP-35: codeforge-review v2 retrofit (review-verdict-v2 신설, 첫 lane self-write 검증)
- 향후 (별도): marketplace sync 자동 PR 생성 (cross-repo PAT secret 인프라 + auto-PR workflow)
- 본 CFP 머지 직후: mclayer/marketplace 에 codeforge entry sync (v0.18.0 stale → v0.21.0)

## [0.20.0] - 2026-04-29

### CFP-33 (ζ arc F2) — Contract Lint Harness (Non-BREAKING)

ζ arc 두번째 foundation step. Inter-plugin contract + cross-system registry 검증을 자동화하는 lint harness 3종 신설. CFP-32에서 도입한 invariant SSOT 3종을 CI에서 일관 강제 + 기존 review-verdict-v1.md frontmatter 백필로 legacy allowlist 제거.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.3. Codex round 2 조건 #2 후속(machine-readable shared contract) + 조건 #3(workflow regex 사전 lint).

### Added
- `scripts/check-inter-plugin-contracts.sh` — `kind: contract` 파일 frontmatter (kind, contract_version, status, related_plugins, related_adrs, authors) + 본문 sanity (≥3 ## 섹션) 검증
- `scripts/check-comment-prefix.sh` — `comment-prefix-registry-v1.md` ## 3. 항목 yaml self-validation (11 prefix · 필수 field · auto_mirror bool · 중복 검출)
- `scripts/check-label-registry.sh` — `label-registry-v1.md` ↔ `bootstrap-labels.sh --dry-run` 양방향 sync (name set + color drift + single_active invariant)
- `.github/workflows/contract-lint.yml` — 위 3 lint job CI 통합

### Changed
- `docs/inter-plugin-contracts/review-verdict-v1.md` — frontmatter 백필 (kind: contract, contract_version: 1.0, status: Active, related_plugins, related_adrs, authors)
- `scripts/bootstrap-labels.sh` — `--dry-run` 플래그 추가 (gh 미호출, name|color|desc tab-separated stdout 출력 → check-label-registry.sh 가 parse)
- `scripts/check-doc-frontmatter.sh` — kind:contract dispatch (kind:registry 만 본 lint 적용, kind:contract 는 check-inter-plugin-contracts.sh 가 별도)
- `scripts/check-doc-section-schema.sh` — 동일 dispatch
- `.claude-plugin/plugin.json` version 0.19.0 → 0.20.0

### Why
CFP-32 가 SSOT를 도입했지만 CI 강제는 일부만 (frontmatter + section 만). CFP-33 은 내용물(`## 3. 항목`) 자체 + script ↔ registry sync 까지 자동 검증. CFP-35 review v2 retrofit 진입 전 contract 변경 안전성 보장.

거부된 대안: 모든 lint 를 `check-doc-frontmatter.sh` 안에 inline (단일 스크립트가 너무 많은 역할), `bootstrap-labels.sh` 자체를 registry 에서 자동 생성 (CFP-33 scope 초과 — 이전은 후속 CFP).

### Migration
**Non-BREAKING** — 본 CFP는 추가 lint 만. consumer 영향 없음. 기존 동작 변화 없음.

- review-verdict-v1.md 의 frontmatter 백필은 narrative 영향 없음 (본문 그대로)
- bootstrap-labels.sh 정상 호출 시 동작 동일 (--dry-run 추가만)
- consumer overlay 영향 없음

### Validation
- 3 신규 lint 모두 정상 상태 PASS (review-verdict-v1.md 1건 contract 검증, registry 11+20 entry sync)
- 의도적 break (frontmatter 누락 / yaml schema mismatch / bootstrap-labels.sh 라벨 추가 누락) 시 CI fail 검증
- 기존 5 lint (frontmatter / section-schema / write-permission / no-atlassian / doc-links) 회기 없음

### Followups (CFP-34+)
- CFP-34: workflow yaml syntax test + marketplace sync auto + story-section-write-guard.yml
- CFP-35: codeforge-review v2 retrofit (review-verdict-v2 신설 + v1 deprecate)

## [0.19.0] - 2026-04-29

### CFP-32 (ζ arc F1) — Foundation: Invariant SSOT 3종 + §10 Orchestrator 단독 owner (Non-BREAKING)

ζ arc 첫 foundation step. 3 invariant SSOT(`comment-prefix-registry-v1` · `label-registry-v1` · `fix-event-v1`)을 `docs/inter-plugin-contracts/`에 신설하고 lint로 강제. §10 FIX Ledger 갱신 권한을 DocsAgent → Orchestrator 단독으로 이관. 후속 CFP-35~40 lane plugin 추출의 contract surface 준비 완료.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.2. Codex round 2 조건 #2(machine-readable shared contract 사전 구축) 직접 대응.

### Added
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — 11종 phase prefix machine-readable SSOT (kind: registry)
- `docs/inter-plugin-contracts/label-registry-v1.md` — 20종 GitHub label machine-readable SSOT
- `docs/inter-plugin-contracts/fix-event-v1.md` — §10 FIX Ledger row schema + append 규칙 + RESET 시맨틱스
- `docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md` — 본 implementation plan

### Changed
- `scripts/check-doc-frontmatter.sh` — `docs/inter-plugin-contracts/**` path 규칙 추가 (필수: kind/registry/version/status/authors). `review-verdict-v1.md` legacy allowlist
- `scripts/check-doc-section-schema.sh` — `docs/inter-plugin-contracts/**` 본문 섹션 규칙 추가 (## 1-4. 목적/Schema/항목/변경 규칙). 같은 legacy allowlist
- `docs/orchestrator-playbook.md` §6.4 — DocsAgent → Orchestrator §10 단독 갱신자 이관 명시 + 3 SSOT cross-ref. §6.6 parallel diagnosis narrative 정정 (DeveloperPL typed return)
- `agents/DocsAgent.md` — ζ arc 단계적 해체 진행 표시 + §10 권한 회수 + 11 phase prefix narrative → registry SSOT cross-ref
- `.claude-plugin/plugin.json` version 0.18.0 → 0.19.0

### Why
ζ arc parent spec(CFP-31)이 정의한 9 CFP 로드맵의 첫 단계. Codex round 2 명시: lane plugin 추출 시작 전 phase prefix · label · FIX event 필드 contract를 machine-readable로 fix해야 split-brain 위험 회피. 본 CFP는 "추출"이 아닌 "추출 전 invariant 동결" — 추출 자체는 CFP-35부터.

거부된 대안: F1+F2+F3 압축 1 CFP (Codex 명시 거부 — 검증 신호 분리 불가), F1을 review-verdict-v1.md 백필 포함 확장 (scope creep — CFP-33 contract harness 영역).

### Migration
**Non-BREAKING** — 본 CFP는 schema 도입 + 권한 narrative 갱신만. 기존 Story file·GitHub Issue·CI Action 동작 변화 없음.

- consumer overlay 영향 없음
- agent permission frontmatter 변화 없음 (DocsAgent narrative만 갱신)
- §10 갱신 주체가 Orchestrator로 명시되었으나 실제 mechanics는 동일 (Orchestrator → DocsAgent 의뢰 → §10 Edit이 → Orchestrator 직접 Edit으로 변경 — Orchestrator는 top-level 세션이라 path-scoped 권한 무관)

### Validation
- `scripts/check-doc-frontmatter.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-section-schema.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-links.sh` — 신규 cross-ref 무결
- `scripts/check-agent-frontmatter.sh` — DocsAgent 변경분 통과
- 1-2 dogfood Story (CFP-33 또는 다음 real Story)에서 Orchestrator §10 직접 Edit 동작 확인 (본 CFP scope 외 — 다음 PR 검증)

### Followups (CFP-33+)
- CFP-33: contract lint harness 신설 — `docs/inter-plugin-contracts/**` 의 cross-contract 의존성 + example 유효성 검증. `review-verdict-v1.md` frontmatter 백필 (allowlist 제거)
- CFP-34: workflow yaml syntax test + marketplace sync auto + `story-section-write-guard.yml`
- CFP-35: codeforge-review v2 retrofit (verdict 반환 → self-write)

## [0.18.0] - 2026-04-28

### CFP-28 — Phase 0c · Lint strict 전환 + retro frontmatter backfill (Non-BREAKING)

CFP-27 Phase 0b에서 도입된 4 owner doc path schema lint(`scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh`) 을 warning 모드 → strict 모드 전환. retro 3 file frontmatter backfill + 회고 §1 regex 완화 + legacy change-plan allowlist 도입.

설계 SSOT: [`docs/stories/CFP-28.md`](docs/stories/CFP-28.md) (plugin-meta-na 1-PR 패턴, ADR-005). Phase 0a (CFP-26) → Phase 0b (CFP-27) → 본 Phase 0c (CFP-28) 의 staged ε path 마지막 단계.

### Changed
- `scripts/check-doc-frontmatter.sh` — strict 전환 (`exit 0` → `sys.exit(1)` on warns), 헤더 주석 갱신
- `scripts/check-doc-section-schema.sh` — strict 전환 + 회고 §1 regex 완화 (`^## §1 결과` → `^## §1\s+\S` — 회고 종류별 §1 명칭 자유) + legacy change-plan allowlist (CFP-1 ~ CFP-18 중 docs/change-plans/ 존재분 16건 면제)
- `.github/workflows/lint.yml` — `doc-frontmatter` / `doc-section-schema` job name `(CFP-27 — warning)` → `(CFP-28 — strict)`
- `.claude-plugin/plugin.json` version 0.17.0 → 0.18.0

### Added
- `docs/retros/2026-04-27-v0.11.0-sprint-close.md` frontmatter (title/date/sprint_period/cfp_keys/authors/related_stories/sentinel_refs)
- `docs/retros/2026-04-28-codex-audit-closure-sprint.md` frontmatter
- `docs/retros/2026-04-28-marketplace-bootstrap-sprint.md` frontmatter
- `docs/stories/CFP-28.md` — Story file
- `docs/migration-guide.md` `## v0.17 → v0.18` 섹션 (Non-BREAKING 안내)

### Why
CFP-27 도입 시점에 명시적으로 "CFP-28 strict 전환" 약속. drift 위험을 silent에서 PR 차단으로 격상. legacy 16 change-plan은 backfill 비용 회피하고 신규 작성에 대해서만 strict 적용 (CFP-19+ 부터 docs/superpowers/{specs,plans}/* 패턴 전환으로 docs/change-plans/ 디렉토리는 사실상 freeze — 미래 backfill 부담 없음).

거부된 대안: legacy 16 change-plan 전부 backfill (busywork, 결정은 commit 이력 + ADR에 이미 보존), 별도 디렉토리 이동 (URL/링크 영향, 보존 가치 낮음), schema 자체 폐기 (consumer 프로젝트 규약은 유지 필요).

### Migration
**Non-BREAKING for plugin runtime — schema 위반 시 lint.yml CI에서 PR 차단**:

- 신규 `docs/{change-plans,adr,domain-knowledge,retros}/**` 작성 시 [`templates/<doc-type>.md`](templates/) frontmatter + 본문 섹션 schema 준수 필수
- 회고 §1 명칭 자유 — 첫 메이저 섹션이 `## §1 ...`로 시작하면 통과
- pre-CFP-27 legacy change-plan(`cfp-1` ~ `cfp-18`)은 자동 면제 — 추가 작업 불필요
- consumer overlay (`.claude/_overlay/**`) 영향 없음

상세는 [`docs/migration-guide.md`](docs/migration-guide.md) `## v0.17 → v0.18` 섹션 참조.

## [0.17.0] - 2026-04-28

### CFP-29 — Phase 1 · codeforge-review plugin 추출 (BREAKING — staged ε strategic payoff)

**BREAKING (v1.0 이전 minor 표기)**. 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker) + `templates/review-pl-base.md` + 3 lane checklist을 별도 plugin [`codeforge-review`](https://github.com/mclayer/plugin-codeforge-review) v0.1.0 으로 추출. Inter-plugin Contract `review_verdict v1` 동결.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`](docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md) (CFP-29 — 본 구현 Story, parent CFP-25 staged ε design).

### Removed
- `agents/DesignReviewPLAgent.md` (codeforge-review로 이동)
- `agents/CodeReviewPLAgent.md` (이동)
- `agents/SecurityTestPLAgent.md` (이동)
- `agents/ClaudeReviewAgent.md` (이동)
- `agents/CodexReviewAgent.md` (이동)
- `templates/review-pl-base.md` (이동)
- `templates/review-checklists/{design,code,security}.md` (이동)
- `templates/review-checklists/` 디렉토리 (자동 정리)

### Added
- `docs/inter-plugin-contracts/review-verdict-v1.md` — review_packet (core → review) + review_verdict (review → core) v1 contract 상세 schema
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` — SemVer-style versioning 룰 (v1.x compat / v2.0 BREAKING)
- `CLAUDE.md` "## Inter-plugin Contract" 신규 섹션 — review_verdict v1 요약 + 향후 plugin 추출 시 동일 패턴 안내
- 필수 플러그인 목록에 `codeforge-review@mclayer` (4종 → 5종)

### Changed
- `.claude-plugin/plugin.json` version 0.16.0 → 0.17.0 + description 갱신 (24 → 19 + codeforge-review 추출 명시)
- `CLAUDE.md` 9 곳: agent count 24 → 19, ASCII 다이어그램의 review 5 agent에 `[codeforge-review]` marker, 리뷰 워커 통합 paragraph + Never-skippable + 판정 SSOT 등 cross-ref 갱신
- `docs/orchestrator-playbook.md` 5 곳: frontmatter related_files / 첫 paragraph / review-pl-base path 참조 / 에이전트 표 / dry-run 예시
- `docs/plugin-design.md` 5 곳: §1 §2a §5 §6 헤딩 + Group A 분류 (codeforge core vs codeforge-review plugin 분리)

### Why
CFP-25 ([staged ε design — Claude Opus 4.7 + Codex GPT-5.4 4 라운드 협업](docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md))의 strategic payoff. CFP-21 (DataMigrationArchitectAgent 6th deputy 추가)이 9+ file 동시 갱신 + BREAKING bump을 일으킨 사례에서 monolithic plugin의 revision 비용 高를 진단. Phase 0a (CFP-26 DocsAgent scope 축소) + Phase 0b (CFP-27 lint 강화) 가 inter-plugin extraction의 prerequisite 정착 — Phase 1이 이 구조 위에서 review subsystem 분리 실현. ADR-001 lane-agnostic worker 통합 결정을 plugin 경계로 보존.

거부된 대안: soft transition (deprecation 기간 — drift 위험), subdirectory plugin (단일 repo 2 plugin — marketplace 단위와 mismatch), dual install (두 곳에 같은 agent — overlay merge 우선순위 모호), manifest dependency field (Claude Code schema 부재).

### Migration
**BREAKING — consumer 영향**:

기존 codeforge consumer는 다음과 같이 두 plugin 모두 등록 의무:

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

또는 CLI: `/plugins install codeforge-review@mclayer`.

codeforge-review의 SessionStart hook이 codeforge core 설치 여부 verify — codeforge만 설치하고 review 미설치 시 review lane 진입 시 fail-fast + install 안내. codeforge core의 SessionStart hook도 codeforge-review 설치 여부 감지해 안내.

자세한 사항: `docs/migration-guide.md` v0.16 → v0.17 섹션 참조.

## [0.16.0] - 2026-04-28

### CFP-27 — Phase 0b · Lint 강화 + CI Integration

**Non-BREAKING** — 신규 lint 2종 (doc-frontmatter / doc-section-schema)은 **warning 모드** 시작. 기존 docs 파일 fail 없음. CFP-28 dogfood 검증 통과 후 strict 전환 예정.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 — 설계 spec, CFP-27 — 본 구현 Story).

### Added
- `templates/domain-knowledge.md` — DomainAgent owner doc schema SSOT (CFP-26 Phase 0a부터 owner direct write이나 schema 부재였음)
- `templates/retro.md` — PMOAgent owner doc schema SSOT (동일)
- `scripts/check-doc-frontmatter.sh` — 4 owner doc path frontmatter 필수 필드 검증 (warning 모드)
- `scripts/check-doc-section-schema.sh` — 4 owner doc path 본문 필수 섹션 헤딩 검증 (warning 모드)
- `.github/workflows/lint.yml` 3 신규 job: `write-permission-redistribution` (strict, CFP-26 invariant CI 통합) + `doc-frontmatter` + `doc-section-schema` (warning 모드)

### Changed
- `scripts/check-write-permission-redistribution.sh` — `allow_block` / `deny_block` 두 함수를 단일 `extract_block(file, key)` 파라미터화 (CFP-26 code review minor follow-up)
- `CLAUDE.md` "## ADR" + "## Domain Knowledge" + "## docs/stories markdown 규약" 섹션 — CFP-27 lint enforcement 안내 추가

### Why
CFP-26 Phase 0a가 4 owner agent direct write를 도입했으나 **schema enforcement는 manual convention**에 그침. CFP-27이 schema를 lint로 자동 강제 시작 (warning 모드 → CFP-28 dogfood → CFP-28+ strict). 또한 부재했던 owner doc 템플릿 2건(domain-knowledge / retro) 신설로 SSOT 완결성 회복.

추가로 CFP-26에서 식별된 follow-up 2건 처리: redistribution lint CI integration (이전 manual call only) + awk 코드 정리.

### Migration
**Non-BREAKING — consumer 영향 미미**:
- 신규 lint 2종은 warning 모드라 기존 consumer docs 파일 호환
- consumer가 `templates/domain-knowledge.md` / `templates/retro.md` 를 schema source로 사용 가능 — 강제 아님 (CFP-28에서 strict 전환 시 backfill 필요)
- CI workflow 6 jobs 운영 — consumer가 `.github/workflows/lint.yml` 복사한 경우 새 job 3개 동기화 권장

자세한 사항: `docs/migration-guide.md` v0.15 → v0.16 섹션 참조.

## [0.15.0] - 2026-04-28

### CFP-26 — Phase 0a · Single-owner write 권한 재분배 (BREAKING — DocsAgent scope 축소)

**BREAKING (v1.0 이전 minor 표기)**. DocsAgent 단독 writer 모델을 "DocsAgent + 3 owner agent 분담"으로 변경.
4 single-owner 문서 경로(`docs/{change-plans,adr,domain-knowledge,retros}/**`)가 owner agent direct write로 이관.
DocsAgent는 Story file (multi-writer 직렬화) + GitHub Issue/PR/comment·label·body·milestone 책임 유지.

설계 SSOT: [`docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`](docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md) (CFP-25 — 설계 spec, CFP-26 — 본 구현 Story).

### Changed
- `agents/ArchitectAgent.md` frontmatter — `docs/change-plans/**` + `docs/adr/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DomainAgent.md` frontmatter — `docs/domain-knowledge/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/PMOAgent.md` frontmatter — `docs/retros/**` Edit/Write 추가, `docs/**` 블랭킷 deny 제거
- `agents/DocsAgent.md` frontmatter — 4 owner-path deny 추가, "소유 영역" 표 갱신 (취소선으로 이관 audit trail 보존)
- `CLAUDE.md` "Write 권한 (path-scoped)" + "문서 write 책임 분담" 섹션 (이전 "단독 writer 원칙") 갱신
- `docs/orchestrator-playbook.md` §5.1 + §5.2 + §11.2/§11.4 + §13.4 — 단계 종료 시 DocsAgent 스폰 체크리스트의 4 single-owner trigger를 owner direct로 변경, write queue type enum에서 4 deprecated type 제거

### Added
- `scripts/check-write-permission-redistribution.sh` — Phase 0a invariant lint (4 owner-path direct write + DocsAgent deny 16 assertion)

### Why
CFP-21 (DataMigrationArchitectAgent — 6th deputy) 추가가 9+ 파일 동시 갱신 + BREAKING bump을 일으킨 사례에서, codeforge 본체 revision 비용이 monolithic single-writer 모델 때문에 과도하게 상승함이 명확. DocsAgent의 funnel 가치(multi-writer 직렬화·GitHub lifecycle 일관성·comment phase prefix)는 보존하되, single-author 산출물은 owner agent direct write로 이관해 funnel 부담을 줄이고, 향후 plugin 추출(CFP-29 codeforge-review)의 cross-plugin 결합점을 narrow하게 한다.

설계 협업: Claude Opus 4.7 + Codex GPT-5.4 (4 라운드, 라운드 4에서 Path A 합의). 거부된 대안: Path B (DocsAgent 완전 제거 — multi-writer 직렬화 깨짐), Path C (skill 다운그레이드 — knowledge 보존하지만 enforcement 잃음).

### Migration
**BREAKING — consumer 영향**:
- consumer overlay에서 ArchitectAgent · DomainAgent · PMOAgent 권한을 추가로 확장하던 경우, frontmatter `permissions.allow` 항목이 **core와 concat+dedup** 되므로 변경 없음 (overlay 메커니즘이 새 항목 자동 흡수)
- consumer overlay가 DocsAgent 권한을 명시 override 하던 경우(드뭄), `docs/{change-plans,adr,domain-knowledge,retros}/**` 4 path deny가 추가됨에 유의 — overlay에서 다시 allow를 명시하면 path-scoped allow가 우선
- 자동화: `scripts/check-write-permission-redistribution.sh`가 invariant 강제. CI에서 호출 권장

자세한 사항: 본 spec (CFP-25) §1·§5 참조.

## [0.14.3] - 2026-04-28

### CFP-24 — Marketplace cross-repo 동기화 의무 정식 잠금

**Non-BREAKING**. 사용자 명시 규칙을 CLAUDE.md에 SSOT로 명문화. plugin.json의 mirrored 필드(`name` · `version` · `description` · `author`) 변경 시 `mclayer/marketplace`의 marketplace.json `plugins[name=codeforge]` 동일 필드도 같은 Story 범위 내 sync PR 의무.

### Added
- CLAUDE.md `## Plugin` 섹션 하위 `### Marketplace cross-repo 동기화 의무` 신규 — mirrored 필드 정의 + 의무 절차 + 면제 조건 + 향후 자동화 후보

### Why
CFP-23(2026-04-28)에서 `mclayer/marketplace` 단일 진입점 노출 시작. 두 리포가 plugin.json·marketplace.json 양쪽에 같은 필드를 가져 drift surface 신규 발생. 사용자 입장에서 단일 좌표(`codeforge@mclayer`)로 보이는데 실제는 두 리포 분리 → drift 시 stale version 또는 어긋난 description 노출. 본 규칙으로 author·Orchestrator 의무화. 자동화는 cross-repo parity CI 후속 CFP에서 처리.

### Migration
Non-BREAKING — 기존 사용자 영향 없음. 향후 codeforge plugin.json 변경 PR 작성 시 mirrored 필드 점검 + marketplace sync PR 후속 의무가 author/Orchestrator 절차에 추가됨.

자세한 사항: CLAUDE.md `Marketplace cross-repo 동기화 의무` 섹션 참조.

## [0.14.2] - 2026-04-28

### CFP-23 — `mclayer` marketplace 노출

**Non-BREAKING**. 본 플러그인이 [`mclayer/marketplace`](https://github.com/mclayer/marketplace) 단일 진입점으로 노출됨. 사용자는 `/plugins install codeforge@mclayer`로 설치 가능. 기존 GitHub 좌표 직접 등록 사용자에 영향 없음.

### Added
- README.md `설치 · 사용` 섹션: `mclayer` marketplace 등록 명령 + `~/.claude/settings.json` 영구 등록 예시

### Why
v0.14.1까지 marketplace 노출 부재 — 사용자가 GitHub 원본 좌표를 직접 등록해야 했음. `mclayer/marketplace` 별도 wrapper 리포 신설(2026-04-28)로 단일 진입점 확보. 향후 `mclayer/plugin-<X>` 시리즈 추가 시에도 동일 marketplace에서 일괄 설치 가능.

### Migration
Non-BREAKING — 기존 사용자(직접 GitHub 좌표 등록)는 그대로 유지 가능. 신규/이주 권장 경로:

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": { "codeforge@mclayer": true }
}
```

자세한 사항: `mclayer/marketplace` README 참조.

## [0.14.1] - 2026-04-28

### CFP-22 — DesignReview checklist 확장 (Codex audit #4·#5·#6)

**Non-BREAKING**. ADR-004 §"후속 조치" #4·#5·#6 직접 적용. 새 deputy 없음, 새 §섹션 없음 — 기존 design.md에 3 audit 섹션만 추가.

### Added
- design.md: §4 API 호환 감사 (Codex #5)
- design.md: §3·§4 관측성 감사 (Codex #4)
- design.md: §3 SLO 감사 (Codex #6)
- lane=design category enum: api-compatibility / observability / slo-missing (3개 추가, 8 → 11)
- DesignReviewPL severity_overrides: P0 3건 추가 (조건부 — 공개 API·SLA·boundary만)
- CodexReviewAgent lane=design prompt: auto-P0 3건 추가

### Why
Codex audit #4 (관측성) / #5 (API 호환) / #6 (SLO) 모두 설계 시점 누락 위험 — 운영 단계에서 발견 시 비싼 회귀. shift-left 정합성 (ADR-004 / ADR-006 / ADR-007 동일 trade-off, 단 새 deputy 불필요).

### Migration
Non-BREAKING — 기존 Story 진행 중인 경우 새 audit 룰은 다음 DesignReview 진입 시 자동 적용. P0 룰은 조건부 (공개 API·SLA·boundary 컴포넌트만) — 내부 도구·docs-only는 P1 또는 N/A 사유 1줄로 처리.

자세한 사항: [docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md](docs/superpowers/specs/2026-04-28-cfp-22-design-checklist-expansion.md)

## [0.14.0] - 2026-04-28 (BREAKING)

### CFP-21 — DataMigrationArchitectAgent (Codex audit #2)

**BREAKING**. ADR-004 §"후속 조치" #2 직접 적용. ADR-006 (TestContractArch precedent) 패턴 그대로 차용 — shift-left 데이터 무결성 advocate. 본 plugin은 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na).

### Added
- `agents/DataMigrationArchitectAgent.md` (신설, 6번째 deputy)
- ADR-007 (Accepted) — DataMigrationArchitectAgent 도입 결정
- `templates/change-plan.md` §11 데이터 마이그레이션 (§11.1 Schema 영향 / §11.2 Migration 전략 / §11.3 Rollback 경로 / §11.4 Data integrity invariant / §11.5 Backfill / §11.6 N/A)
- `templates/review-checklists/design.md` §11 audit 절 + 3 P0 차단 룰 (누락 / N/A 사유 부재 / DataMigrationArch 매핑 미반영)
- lane=design category enum: `data-migration` (7 → 8 카테고리)

### Changed
- agent count: 23 → 24
- ArchitectPLAgent: deputy 4 → 5 (Phase 1.5 sanity check 1 항목 + 메타-규칙 1번 §11 매핑 1행 추가)
- ArchitectAgent: deputy 5인 산출물 통합 + Change Plan §1-§10 → §1-§11 + §11 author input 절차
- 4 deputy md (Mapper / Refactor / SecurityArch / TestContractArch): cross-ref 1줄 (DataMigrationArch §11 author input + 4-way 대립 참여)
- CLAUDE.md: 24 core, 다이어그램, Never-skippable, 책임 매트릭스 6행 (§11 5 항목 + 누락/N/A 1행), FIX decision table 1행 추가, 3-way → 4-way 대립 재명명, ArchitectAgent 재스폰 §1-§11
- orchestrator-playbook.md: 24 core, deputy 5인 일괄, 토큰 budget 175k → 200k peak, §3.1 스폰 시퀀스, §3.2 PL 표 DataMigrationArch 행, §14 progress dashboard 5/5 deputies

### Migration
- BREAKING: agent count 23 → 24 (DataMigrationArchitectAgent 추가)
- BREAKING: Change Plan template §1-§10 → §1-§11 (신규 §11 데이터 마이그레이션)
- BREAKING: DesignReview checklist §11 누락 차단 룰 추가
- Consumer 액션: 진행 중 Story (phase: 설계 / 설계 리뷰)는 §11 추가 후 ArchitectPLAgent 검수 재실행. Plugin meta / docs-only / pure UI Story는 §11.6 N/A 사유 1줄 명시
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.13.0 → v0.14.0 절

## [0.13.0] - 2026-04-28

### CFP-19 — 오케스트레이션 병렬화 (R1-R11 Tier 1+2)

**Non-BREAKING**. 사용자 critical feedback ("전체적으로 너무 느리다") 대응. Codex(GPT-5) + general-purpose 두 독립 감사 합의 11개 직렬 병목 제거. 본 plugin은 자기 적용 안 함 (paradox 처리, ADR-005 plugin-meta-na).

**Tier 1 (R1-R8)**:
- R1: DocsAgent dual-mode (blocking/background) write queue drain — `mode` 필드 필수, blocking 7종 / background 4종 분류
- R2: ReviewPL verdict-return-first protocol — DocsAgent save 대기 안 함, 다음 lane spawn 트리거 후 background drain
- R3: Orchestrator-direct dual review worker spawn — PL이 packet return → Orchestrator 한 메시지에 (Claude ∥ Codex) dispatch
- R4: FIX speculative pipelining — DeveloperPL 1차 진단 ∥ ArchitectPL 최종 판정 병렬, 불일치 시 ArchitectPL 우선
- R5: §8.5 Impl Manifest 자동 생성 — DocsAgent kind=impl-manifest helper, DeveloperPL은 review-edit only
- R6: Lane Context Packet warm cache — `.claude-work/cache/<KEY>-sections.json` git commit hash invalidation
- R7: Phase 1 merge ↔ Phase 2 prep parallel — 설계 리뷰 PASS 즉시 Track A(merge) ∥ Track B(prep) 병렬
- R8: ArchitectPL fail-fast pre-synthesis — Phase 1.5 sanity check, 결격 deputy clarification 재spawn

**Tier 2 (R9-R11)**:
- R9: TestAgent subset 병렬 — `subset: functional` ∥ `subset: performance`
- R10: SecurityTestPL 1차 layer pre-fetch — `.claude-work/cache/<KEY>-sec1.json` background prefetch
- R11: FIX mechanical fast-path — typo/broken-link/minor-naming/comment-only 자격 시 ArchitectPL 판정 skip + §10 row 안 매김

**예상 효과**: Story 1건당 평균 20-32분 단축 (60-90분 → 40-60분 예상, 30-40% reduction).

**변경 파일**: `templates/review-pl-base.md`, `agents/{DocsAgent,ArchitectPLAgent,DeveloperPLAgent,DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,TestAgent}.md`, `docs/orchestrator-playbook.md`, `CLAUDE.md`. ADR 변경 0건.

**Spec/Plan**: [docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md](docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md), [docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md](docs/superpowers/plans/2026-04-27-cfp-19-orchestration-parallelization.md).

### Migration
- Non-BREAKING — 모든 변경은 SSOT 문서·agent md·playbook 추가 절. consumer 액션 없음.
- 본 plugin은 자기 적용 안 함 (paradox 처리). 다음 Story부터 발효.

## [0.12.0] - 2026-04-27

### Added
- **TestContractArchitectAgent** 신설 — 설계 lane 5번째 deputy (§8 Test Contract author input contributor, QA perspective)
- **ADR-006** — TestContractArch 도입 결정 기록 (status=Accepted)
- **ArchitectPL 검수 메타-규칙 압축** — 4 항목 enumerate -> 2 항목 메타-규칙 (§섹션별 deputy author input 통합 + §섹션 누락 차단)

### Changed
- **ArchitectAgent**: deputy 3인 -> 4인 (TestContractArch 추가) + §8 Test Contract author 라인 §7 동형 보강
  > Note: "deputy" 카운트는 perspective 차이 — ArchitectAgent peer view = 4 (Mapper/Refactor/SecurityArch/TestContractArch), ArchitectPL chief-inclusive view = 5 (+chief author).
- **ArchitectPLAgent**: deputy 4인 -> 5인 + 검수 4 항목 -> 메타-규칙 2 항목 압축
- **CodebaseMapper / RefactorAgent / SecurityArchitectAgent**: "Mapper/Refactor와의 관계" 절 끝에 "TestContractArch는 §3·§7 도형 대립 비참여" 1줄 cross-reference 추가
- **QADeveloperAgent**: 계약 소유자 라인 보강 ("TestContractArch input 통합 후 §8 확정")
- **CLAUDE.md / orchestrator-playbook.md / plugin-design.md**: 22 core -> 23 core, deputy 4 -> 5 일괄, 검수 메타-규칙 압축 반영
- **ADR-005**: status Proposed -> **Accepted (결정 1·2·3 한정)** — N/A 표기 형식·면제 분류·N/A inheritance 차단. 결정 4 (invariant-check Step 신설)는 follow-up CFP

### Migration
- BREAKING: agent count 22 -> 23 (TestContractArchitectAgent 추가)
- BREAKING: 책임 매트릭스에 TestContractArch perspective 추가 (§8 author input contributor)
- Consumer 액션: 없음 (Orchestrator 경유 호출). SessionStart hook 재실행 권장
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.11.0 -> v0.12.0 절

## [0.11.0] - 2026-04-27

### Added
- **ArchitectPLAgent** 신설 — 설계 레인 PL (supervisor + FIX 루프 최종 판정자)
- **SecurityArchitectAgent** 신설 — 설계 레인 deputy (trust boundary / threat model / auth / data)
- **Change Plan §7 보안 설계** 섹션 신설 (templates/change-plan.md)
- **ADR-004** — 설계 lane 재구조화 결정 기록

### Changed
- **ArchitectAgent** 책임 분리: PL → chief author. FIX 최종 판정·deputy 스폰·Impl Manifest 감사 책임을 ArchitectPLAgent로 이관. 신규 ADR draft 작성 책임 명문화 (Codex #7)
- **CodebaseMapperAgent / RefactorAgent**: 상위 ArchitectAgent → ArchitectPLAgent. 2-way → 3-way 대립 (+ SecurityArch)
- **CLAUDE.md**: 다이어그램·Never-skippable·스폰 시퀀스·책임 매트릭스·FIX decision table·병렬 스폰·Write 권한 모두 갱신
- **DesignReviewPL**: review packet에 §7 보안 설계 차단 룰 추가
- **DeveloperPL**: FIX 1차 진단 → ArchitectPLAgent 최종 판정 (3 lane 갱신)

### Migration
- Consumer 액션 필요 없음 (Orchestrator 경유 호출이라 직접 영향 없음)
- 기존 docs/change-plans/* 회귀 갱신 불필요 (신규 Story부터 §7 적용)
- 자세한 사항: [docs/migration-guide.md](docs/migration-guide.md) v0.10.0 → v0.11.0 절

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
