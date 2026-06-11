# Changelog

`codeforge-develop` plugin 릴리스 이력.

## 0.9.1 (2026-06-12) — CFP-2178 S6 lane repo archive 참조 sweep (PATCH)

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `overlay/hooks/session-start-deps-check.sh` 안내 URL — 구 lane repo (`mclayer/plugin-codeforge-develop`) → wrapper 모노레포 앵커 (`mclayer/plugin-codeforge/tree/main/plugins/codeforge-develop#dependencies`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1) — read-only repo 안내 차단.
- `CLAUDE.md` `story_issues` repo 좌표 — `mclayer/plugin-codeforge-develop` → `mclayer/plugin-codeforge` (archive 후 read-only repo 에 issue 생성 지시 = 기능 파손 해소).

## 0.8.0 (2026-05-31) — CFP-1869 InfraEngineerAgent compose overlay 격리 guard (MINOR)

### Added

- `agents/InfraEngineerAgent.md` (UPDATE) — 신설 sub-section "Compose overlay 격리 (list-merge append 주의)". 3 항목: (1) compose list 필드(ports/networks/volumes)는 overlay 합성 시 교체가 아니라 **append 병합** → 격리 overlay 에서 base prod 값 제거는 `!override`/`!reset` tag 의무. (2) `docker compose config --quiet` exit 0 ≠ 격리 정상 (문법만 검사) → 진짜 게이트 = `config`(non-quiet) 렌더 직접 verify (`published:`/`networks:`/`volumes:` prod 값 잔존 grep 확인). (3) cross-ref consumer mctrader MCT-208 + MCT-269 (N=2) + escalation #1869.
- `.claude-plugin/plugin.json` — version 0.7.1 → 0.8.0 MINOR + description CFP-1869 entry append.

### Why

consumer escalation mclayer/plugin-codeforge#1869 — mctrader 가 stg/blue-green compose overlay 작성 중 list-merge append 함정으로 silent mis-isolation 2회 재발 (MCT-208 회피적 + MCT-269 정면 `ports:` prod 값 잔존 노출, N=2 ≥ ADR-045 §D-9 threshold 2). InfraEngineerAgent prompt 에 함정 codify → 다른 consumer 재발 차단.

### Compatibility

- **Wire**: agent prompt 지침 추가만. runtime contract / overlay / API surface 영향 0. consumer project 동작 무변경 (retroactive 면제, 본 mandate effective 후 신규 compose overlay 작성부터 적용).
- **Marketplace sync**: 본 MINOR bump 의 marketplace.json mirror = sibling sync PR (mclayer/marketplace cfp-1869) 에서 처리 (ADR-063 atomic invariant — marketplace sync PR 선행 merge → plugin PR merge).
- **ADR cross-ref**: ADR-037 §결정 1 (a) Agent file "추가" = MINOR bump 근거 (CFP-609 0.6.0→0.7.0 선례 동형).

## 0.7.1 (2026-05-30)

- [CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 7건 (presets/webapp 포함). tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.

## 0.7.0 (2026-05-14)

- CFP-609: DeveloperPLAgent.md 자율 병렬 결정 tree 4-분기 신설 (parallel-dispatch-protocol-v1 §5 sibling sync — wrapper canonical mclayer/plugin-codeforge `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`)

## 0.6.0 — 2026-05-13 — CFP-507 DeveloperPLAgent Phase 2 PR body composition convention section 신설 (MINOR)

CFP-490 (#490, merged) §7.5 origin investigation 의 sibling carrier. `## Lane evidence` first heading auto-include 의 actual origin 정정 — 가설 (wrapper PR template 부재) verified false, actual origin = 본 plugin DeveloperPLAgent body composition convention 부재 + wrapper Orchestrator manual append 정책 부재 결합 (Story CFP-507 §2.3).

### Added

- `agents/DeveloperPLAgent.md` (UPDATE) — 신설 section "Phase 2 PR body composition convention (CFP-507 / ADR-031 정합)". 4 룰: (1) `## Lane evidence` heading 1회만 inject (2) 7-row format 사용 (wrapper `templates/github-pr-template.md` SSOT line 79 verbatim 정합) (3) Orchestrator manual append 시 heading 재추가 금지 (4) 위반 시 `lane-evidence-check.yml` 5a guard 발화 (CFP-490 §결정 1 정합). Cross-ref 5종 (wrapper playbook §3.0.13 / PR template SSOT / ADR-031 §결정 3 / CFP-490 §결정 1 / Story CFP-507 §2.3 verified facts).
- `.claude-plugin/plugin.json` — version 0.5.2 → 0.6.0 MINOR + description CFP-507 entry append.

### Why

CFP-490 retro `2026-05-12-cfp-490.md` follow-up #1 (medium severity) — 본 plugin agent body 안 codified guidance 부재로 인한 duplicate heading 위험 root prevention. ADR-037 §결정 정합 (agent file 변경 = MINOR bump).

### Compatibility

- **Wire**: agent body narrative 만 변경. runtime contract / overlay / API surface 영향 없음. in-flight PR backward compat 안전 (narrative documentation 추가만).
- **Marketplace sync**: 본 MINOR bump 의 marketplace.json mirror 는 wrapper PR sibling (mclayer/marketplace cfp-507) 에서 동시 처리 (ADR-063 §결정 5 atomic invariant — concurrent merge gate).
- **Wrapper sibling**: codeforge wrapper plugin 5.39.0 → 5.40.0 MINOR 와 짝 (docs/orchestrator-playbook.md §3.0.13 신설 — Orchestrator manual append 정책).

## 0.5.2 — 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113 Story frontmatter trust + CFP-123 Live touching gate + CFP-133 PR comment evidence + CFP-342 Phase 2 PR gate 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## 0.5.1 — 2026-05-12

- [CFP-448 sibling] DeveloperPLAgent model `claude-opus-4-7` → `claude-sonnet-4-6` PATCH
- ADR-042 Amendment 5 §결정 1 (b) + ADR-057 Amendment 3 정합
- Sibling PRs: design#34 (merged), wrapper#502 (merged)

## [0.4.0] - 2026-05-10

### Added
- presets/docker-compose.test.yml: 통합테스트 격리 환경 템플릿 신규 (CFP-367 / ADR-055) — 3-service(app/test-db/wiremock) ephemeral 구성, InfraEngineerAgent §8.6 사용

## [0.3.0] - 2026-05-10

### Changed
- InfraEngineerAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2, mechanical pattern execution)
- QADeveloperAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2)
- DataEngineerAgent: model claude-sonnet-4-6 → claude-haiku-4-5 (ADR-042 Amendment 2)

## [0.2.0] - 2026-05-07

### CFP-128 / ADR-033 — InfraEngineer Docker-first mandate + presets/k8s/ (MINOR)

#### Added

- InfraEngineer mandate Docker-first 재작성 (D1 sibling sync PR #8, commit b6bda7c)
- `presets/k8s/` NEW directory (Kubernetes preset)

#### Why

ADR-033 (wrapper canonical) — InfraEngineer 의 backing mandate 를 Docker-first 로 확정 + Kubernetes preset 도입. CFP-128 marketplace mirror prep 의 일환으로 minor bump.

#### Compatibility

- **Wire**: codeforge >= 4.0.0

## [0.1.0] - 2026-04-29

### CFP-39 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 다섯 번째 lane plugin (parent §5.9).

### Added

- 5 agents 이전: DeveloperPLAgent, QADeveloperAgent, DeveloperAgent, DataEngineerAgent, InfraEngineerAgent
- presets/{webapp,README.md} 이전 (BackendDeveloperAgent, FrontendDeveloperAgent)
- docs/inter-plugin-contracts/develop-output-v1.md (canonical)
- overlay/hooks/{regen-agents,session-start-deps-check}.sh
- README + CLAUDE.md

### Why

ζ arc §5.9: DeveloperPL이 role:dev roster 동적 discover. 5 agent + presets 가 함께 이전. CFP-31 §3.5 거부 (overlay 충분 권고)는 wrapper-only end-state 와 충돌이라 폐기.

### Compatibility

- **Wire**: codeforge >= 4.0.0
