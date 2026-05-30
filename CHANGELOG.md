# Changelog

`codeforge-deploy-review` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

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
