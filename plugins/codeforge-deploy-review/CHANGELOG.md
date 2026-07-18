# Changelog

`codeforge-deploy-review` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [1.2.0] - 2026-07-18 — CFP-2748 ADR-141 Amendment 2 DeployReviewWorker opus→sonnet carve-out (MINOR)

### Changed (CFP-2748 — ADR-141 Amendment 2, MINOR)

[CFP-2748] ADR-141 Amendment 2 — 중간추론 역할 14종 opus→sonnet carve-out. 본 plugin 의 **DeployReviewWorkerAgent** frontmatter `model: opus`→`model: sonnet` + frontmatter comment 정정 + subagent self-refusal guard(#846) 1줄 배치(A2-3 canonical) + CLAUDE.md tier 표 + docs/architecture mirror opus→sonnet. **DeployReviewPLAgent 은 OOS(opus 유지 — adversarial debate 자동 발동 backstop, AC-12)**. agent tier 변경 = additive behavior (ADR-037/ADR-008 MINOR). marketplace version sync(ADR-063, sync PR 선행 merge).

## [1.1.0] - 2026-07-03 — CFP-2560 전 에이전트 opus 단일 tier (MINOR)

### Changed

[CFP-2560] 전 에이전트 opus 단일 tier (ADR-141) — model frontmatter opus 통일 + Sonnet tier 표/ADR-057 fallback 청산.

- 배포 리뷰 lane 에이전트(DeployReviewWorker) frontmatter `model: opus` 통일 + CLAUDE.md/docs/architecture Sonnet tier 표 → opus 정정 + ADR-057 fallback 문장 → "ADR-141 단일 opus tier — fallback 대상 없음". (본 plugin 은 2026-07-13 KST sunset 예정 — ADR-121, deprecation 상태 무변경.)

## [1.0.5] - 2026-06-15

### Changed (CFP-2249 — superpowers 의존 완전 제거, PATCH)

Epic CFP-2249 (superpowers 의존 완전 제거, ADR-122 — supersede ADR-028) 의 lane 반영. 배포 리뷰 lane agent 의 `superpowers:*` skill 호출 / `docs/superpowers-integration.md` 참조를 codeforge native discipline 으로 교체. 필수 plugin 4→3 의 wrapper 정책 변경 동반 lane catch-up. capability 추가/제거 0 — PATCH. (본 plugin 은 2026-07-13 KST sunset 예정 — ADR-121, deprecation 상태 무변경.)

- `agents/DeployReviewPLAgent.md` · `agents/DeployReviewWorkerAgent.md` — `superpowers:*` 호출 / `superpowers-integration.md` 참조 제거 → codeforge native (ADR-122) 흡수.

#### Why

ADR-122 — superpowers 외부 plugin 의존을 codeforge native 로 내재화. consumer breaking 0.

## [1.0.4] - 2026-06-13

### Changed (CFP-2225 — deprecation 마킹, PATCH)

- **DEPRECATED 선언** (ADR-121, Epic #2217 S2) — sunset **2026-07-13 KST**, 이후 Wave 2 (S5/S6) 물리 제거. CLAUDE.md 최상단 deprecation 배너 + plugin.json description 선두 `[DEPRECATED — sunset 2026-07-13 KST, ADR-121]` prefix. 대체 경로 = consumer repo GitHub Actions + GitHub Environments (dev/stg/prd) 완전 위임. 본 bump = 선언적 마킹만 (agent/template 기능 무변경).

## [1.0.3] - 2026-06-12

### Changed (CFP-2178 — S6 lane repo archive 참조 sweep, PATCH)

- `README.md` 필수 의존 `codeforge-deploy@mclayer` 링크 — 구 lane repo URL (`mclayer/plugin-codeforge-deploy`) → 동일 모노레포 상대 경로 (`plugins/codeforge-deploy/`). 구 lane repo 8개 = 2026-06-12 GitHub archive (ADR-118 D1).

## [1.0.1] - 2026-05-30

### CFP-1845 follow-up — agent model 핀 → 별칭 전환

[CFP-1845 follow-up] agent model 핀 → 별칭 전환. frontmatter model field 2건. tier 분류 변경 0건. wrapper [#1846](https://github.com/mclayer/plugin-codeforge/pull/1846) / [#1847](https://github.com/mclayer/plugin-codeforge/issues/1847) 연계. marketplace sibling sync 동반.

#### Changed

- `agents/DeployReviewPLAgent.md` — frontmatter `model: claude-opus-4-7` → `model: opus` (Opus tier 분류 불변).
- `agents/DeployReviewWorkerAgent.md` — frontmatter `model: claude-sonnet-4-6` → `model: sonnet` (Sonnet tier 분류 불변).

#### Notes

- frontmatter `model:` field 만 별칭 전환 — 본문/description 과거 버전 서술 보존.
- `agents/ProductionEvidenceDeputyAgent.md` 은 `model:` field 부재 (CONDITIONAL deputy, parent_pl spawn) — 변경 없음.
- tier 분류 변경 0건 (Opus → Opus, Sonnet → Sonnet). version PATCH bump (1.0.0 → 1.0.1) + marketplace sibling sync 동반.

## [1.0.0] - 2026-05-21

### CFP-1059 (Epic Story-3) — Deploy Review lane plugin 첫 release + ProductionEvidenceDeputy 이관 (신규 plugin baseline)

codeforge family 6 → 8 lane 확장의 #7 배포 리뷰 lane plugin 신설 ([ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md)). production 환경 성능 측정을 1st-class 검증 phase 로 격상.

#### Added

- `.claude-plugin/plugin.json` — codeforge-deploy-review plugin manifest (1.0.0 baseline).
- `agents/DeployReviewPLAgent.md` — 배포 리뷰 lane PL (Opus tier, ADR-042 Amendment 9):
  - production-grade 성능 측정 1st-class lead — smoke / 성능 비교 / cutover 사후 검증 verdict 종합
  - 성능 미충족 시 root cause 1차 진단 + debate-protocol-v1 cross-module trigger (ADR-059) + 구현/설계/요구사항 lane FIX dispatch
  - Opus tier = adversarial debate 자동 발동 영역 mandatory (ADR-042 §결정 1)
- `agents/DeployReviewWorkerAgent.md` — 배포 리뷰 worker (Sonnet tier):
  - smoke test (HTTP shadow / WebSocket·daemon 대기 mode) + 성능 baseline 수집 (latency p50/p95/p99 / throughput / error rate / CPU·memory) + cutover 사후 검증
- `agents/ProductionEvidenceDeputyAgent.md` — **ProductionEvidenceDeputy ownership 이관** (ADR-088 §결정 4 + ADR-72 Amendment 4):
  - codeforge-design CONDITIONAL deputy → codeforge-deploy-review 정식 deputy
  - parent_pl: ArchitectPLAgent → DeployReviewPLAgent / ssot_position: codeforge-design → codeforge-deploy-review
  - mandate body = ADR-72 §결정 1-7 verbatim 유지 (production evidence quad 4 source / EPIC CLOSED gate / Family atomic canary pin)
  - codeforge-design repo 의 기존 file 은 deprecate marker 부착 (별 sibling 갱신)
- `CLAUDE.md` — 배포 리뷰 lane plugin identity + 검증 3종 + 기존 review lane disjoint axis + ProductionEvidenceDeputy 이관 + ADR-088 cross-ref.
- `templates/` — 배포 리뷰 매커니즘 (production-grade 성능 측정 + cutover evidence 4-quad).
- `README.md` — plugin 설치 / 의존성 / architecture.

#### Notes

- 본 lane scope = "한 번 끝나는 검증" 만 (smoke / 성능 비교 / cutover 사후 검증). 운영 phase (continuous monitoring) 와 disjoint — 별 Epic carrier.
- `[empirical-source: TBD]` — 성능 baseline (latency / throughput / error rate) consumer mctrader 첫 적용 시 측정 후 lock-in (ADR-068 I-5).
