# Changelog

`codeforge-test` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [1.4.0] - 2026-07-03 — CFP-2560 전 에이전트 opus 단일 tier (MINOR)

### Changed

[CFP-2560] 전 에이전트 opus 단일 tier (ADR-141) — model frontmatter opus 통일 + Sonnet tier 표/ADR-057 fallback 청산.

- test lane 에이전트(IntegrationTest 외) frontmatter `model: opus` 통일 + CLAUDE.md/docs/architecture Sonnet tier 표 → opus 정정 + ADR-057 fallback 문장 → "ADR-141 단일 opus tier — fallback 대상 없음".

## [1.3.3] - 2026-06-12

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `overlay/hooks/session-start-deps-check.sh` 안내 URL — 구 lane repo (`mclayer/plugin-codeforge-test`) → wrapper 모노레포 앵커 (`mclayer/plugin-codeforge/tree/main/plugins/codeforge-test#dependencies`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1) — read-only repo 안내 차단.
- `CLAUDE.md` `story_issues` repo 좌표 — `mclayer/plugin-codeforge-test` → `mclayer/plugin-codeforge` (archive 후 read-only repo 에 issue 생성 지시 = 기능 파손 해소).

## [1.3.1] - 2026-05-30

### [CFP-1845 follow-up] agent model 핀 → 별칭 전환 (PATCH)

[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 3건. tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.

## [1.2.0] - 2026-05-20

### CFP-698 — ADR-014 Amendment 4 cross-repo sibling sync — §7.4 운영 리스크 측정 contract 3-axis (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge#1035 `abcd92bf` CFP-676 merged 2026-05-19) Epic CFP-1026 Wave 2 Story-4 carrier. ADR-014 Amendment 4 §결정 2 cross-ref shell 분류 (§7.4.2 cancel-on-disconnect + §7.4.4 rate limit, policy 값 미결정 — evidence-driven design 3-axis split) 의 codeforge-test repo cross-repo sibling 반영. ADR-054 Category 2 doc-only fast-path. ADR-010 §4 wrapper-first allowed pattern 정합.

#### Added

- `agents/IntegrationTestAgent.md` — §7.4 운영 리스크 측정 contract 3-axis sub-section 신설 (Baseline 자동 승격 § 후, 보고 형식 § 전). 3-axis 표 (Axis 1: 측정 대상 정의 ArchitectAgent §8.6 IntegrationTest contract pointer DesignLane / Axis 2: 실측 본 lane / Axis 3: policy 결정 ArchitectLane post-measurement). FIX 루프 disjoint axis (evidence 수집 ≠ FIX root-cause decision table `local P1 → 구현 / boundary P1 → 설계` 별 axis). Per-Story aggregation = Epic-level lane spawn 1회 within N Story (`tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/` self-write 표 already-codified). codeforge-test#17 (Epic-level mandate body + test-verdict-v2 schema) file diff disjoint 회피.
- `CLAUDE.md` — 핵심 요약 section 안 1-line cross-ref bullet 추가 (`§7.4 측정 contract → agents/IntegrationTestAgent.md §7.4` reference only). lane policy vs agent mandate 분리.
- `docs/architecture/codeforge-test.md` — Governance ADR anchor 영역 §7.4 측정 contract 1-line cross-ref (ADR-078 living architecture doc SSOT 정합).

#### Changed (mandate frontmatter rename, 2 occurrence)

- `agents/StatefulTestAgent.md` — mandate consult yaml: `OperationalRiskArchitectAgent` → `InfraOperationalArchitectAgent` (1 occurrence) + `DataMigrationArchitectAgent` → `DataArchitectAgent` (1 occurrence). codeforge family deputy 명칭 일관성. L89 historical pattern reference `CFP-46 OperationalRiskArch 패턴 동일` = historical retain (CFP-46 carrier 시점 명칭 사실 기록).

#### Why

S1 CFP-676 wrapper#1035 `abcd92bf` merged 시점에 wrapper SSOT 만 갱신되어 codeforge-test repo 의 cross-repo sibling 반영 미완 상태. ADR-014 Amd 4 §결정 2 cross-ref shell 분류 (cancel-on-disconnect / rate limit) 의 evidence-driven 3-axis split 정착 — design-time pointer existence (DesignLane) + runtime measurement (본 lane) + post-measurement policy decision (ArchitectLane) 의 axis disjoint 명문화. 이전 IntegrationTest measurement 결과의 FIX iteration trigger 혼동 (측정 실패 = 구현 실패 ≠ 실제는 policy 결정 needed) 차단. codeforge-test#17 conflict 회피 — §7.4 codify 위치 = agent file primary + CLAUDE.md 1-line cross-ref (lane policy ≠ agent mandate 분리, file diff disjoint).

#### Compatibility

- **Wire**: §7.4 sub-section 신설 = 신규 contract (declarative-only, mechanical enforcement 부재 — Wave 2 sub-CFP carrier). agent mandate scope 보존 (test-verdict-v2 schema 변경 0건). ratchet 강화 방향 (ADR-058 §결정 5 정합).
- **Marketplace sync**: 본 MINOR bump 의 marketplace.json mirror = ADR-063 atomic invariant 발효 (별 sync PR carrier).
- **Carrier**: CFP-698 (Epic CFP-1026 Wave 2 Story-4, sibling Story = codeforge-review 1.7.0).

## [1.1.2] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113/123/133/342 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## [1.1.1] - 2026-05-11

(earlier entry retained — pre-existing)

## [1.0.0] - 2026-05-10

### CFP-367 / ADR-055 — IntegrationTestAgent 도입 (통합테스트 lane 전용 부활)

ADR-048로 deprecated된 codeforge-test plugin을 통합테스트 lane 전용으로 부활. MAJOR bump = 기존 TestAgent/StatefulTestAgent deprecated + IntegrationTestAgent 신규 도입.

### Added

- `agents/IntegrationTestAgent.md` — Sonnet tier, §8.6 Integration Test Contract 이행, docker-compose.test.yml 동적 실행, 전체 suite regression 검증, test-verdict-v2 생성
- `docs/inter-plugin-contracts/test-verdict-v2.md` — canonical contract (lane: integration, suite_summary, dynamic_test_compliance, §8.6 N/A 면제 패킷 포함)

### Changed

- `CLAUDE.md` — DEPRECATED → REVIVED (ADR-055 / ADR-048 Amendment 1); 통합테스트 lane 동작 문서화; 기존 TestAgent/StatefulTestAgent 섹션에 deprecated 배너 추가

### Deprecated

- `agents/TestAgent.md`, `agents/StatefulTestAgent.md` — CFP-317 / ADR-048로 deprecated 유지 (파일 보존, spawn 불가)
- `docs/inter-plugin-contracts/test-verdict-v1.md` — Archived (superseded by test-verdict-v2)

## [DEPRECATED] - 2026-05-09

### CFP-317 — CI-native 테스트 전환으로 인한 deprecated 선언

TestAgent 및 StatefulTestAgent spawn 폐지. GitHub Actions CI가 구현 테스트 실행을 담당하게 되어 별도 test lane plugin이 불필요해짐.

- QADeveloperAgent (codeforge-develop plugin)가 `.github/workflows/test.yml` 작성 의무 추가
- Orchestrator가 `gh pr checks` polling으로 CI 결과 직접 처리
- `test_verdict v1` contract Archived
- 본 plugin은 역사적 참조용으로 보존 (ADR-023 lifecycle — 삭제 아님)

관련: [ADR-048](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-048-ci-native-test-execution.md)

## [0.1.0] - 2026-04-29

### CFP-38 (codeforge ζ arc) — Initial extraction (NEW)

codeforge ζ arc 네 번째 lane plugin (parent spec mclayer/plugin-codeforge CFP-31 §5.8). 가장 단순한 lane (TestAgent 1개 + owner doc 부재).

### Added

- `agents/TestAgent.md` — codeforge wrapper 에서 이전. self-write 권한 추가 (mcp__github__add_issue_comment, mcp__github__issue_write — phase comment + phase 전환)
- `docs/inter-plugin-contracts/test-verdict-v1.md` — canonical contract
- `overlay/hooks/{regen-agents,session-start-deps-check}.sh`
- README + CLAUDE.md

### Why

CFP-31 §5.8: TestAgent 1개 + owner doc 부재로 가장 단순한 lane 추출. Codex round 2 권고 sequencing (Sequence #4) 따름. 이전 3 plugin (review v2 + pmo + requirements) 검증 후 진입.

### Compatibility

- **Wire**: codeforge >= 3.0.0
- **Migration**: Story §10 FIX Ledger append 는 그대로 Orchestrator 단독. lane plugin 은 fix_routing_hint 만 verdict 에 첨부 (FAIL 시)
