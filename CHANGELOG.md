# Changelog

`codeforge-deploy` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [Unreleased]

### CFP-1317-S2 — `templates/deploy-mechanism.md` SSOT 정합 (d-B redirect pattern, ADR-068 I-4)

mctrader [#1272](https://github.com/mclayer/plugin-codeforge/issues/1272) consumer-escalation **(d)** 해소 cross-repo carrier. plugin file 의 9-flat schema block 을 wrapper SSOT 5-nested + 4 optional 단일 anchor 로 redirect (6회 누적 G-1/G-3/G-6 동형 drift super-class 차단).

#### Changed

- `templates/deploy-mechanism.md` — schema block (이전 9-flat field `enabled` / `environments` / `registry` / `secret_provider` / `reverse_proxy` / `retention_hours` / `acceptable_downtime_ms` / `hosts` / `services`) 제거 + wrapper [`docs/project-config-schema.md` deploy 섹션](https://github.com/mclayer/plugin-codeforge/blob/main/docs/project-config-schema.md#deploy-섹션-설명-cfp-1059--adr-087--adr-088) redirect 로 전환. 9-step blue-green sequence (ADR-087 §결정 5) + Edge Cases reference doc layer 만 retain. `[empirical-source: TBD]` annotation 3개소 = wrapper ADR-087 §결정 5 본문 단일 anchor 로 자연 제거. 결정 근거 = ArchitectAgent chief tie-break ladder Step 2 (ADR-068 I-4 invariant d-B 직접 발사, 3중 concur: Researcher 5/5 산업 prior art + PL d-B + I-4 invariant).
- `CLAUDE.md` — Self-write 책임 단락 + 관련 ADR 표 cross-ref 추가 (consumer overlay schema authoring scope = wrapper SSOT 영역 명시, ADR-045 / ADR-013 cross-ref).

#### Notes

- doc-only fast-path (ADR-054 Category 2) — src/tests/workflow yml 변경 0 + plugin.json version bump 0 (1.0.0 retain). ADR-063 marketplace atomic invariant 미발효 (mirrored field 4종 변경 0).
- §13 sub-finding declare (본 Story scope 외):
  - **(c) wrapper SSOT 영역**: `templates/github-workflows/` 안 `blue-green-swap.yml` / `retention-window-timer.yml` / `auto-rollback.yml` 명칭 yml 부재 + ADR-087 §관련 파일 L201-204 stale reference → S3 ADR-107 (drift detection process) 안 부분 흡수 후보, 또는 별 wrapper CFP carrier
  - **mctrader-data#81**: `image-publish.yml` matrix `[data, engine, signal-collector]` pilot web 미포함 + registry SSOT `ghcr.io` vs `docker.io` → mctrader-side 별 Issue carrier

## [1.0.0] - 2026-05-21

### CFP-1059 (Epic Story-2) — Deploy lane plugin 첫 release (신규 plugin baseline)

codeforge family 6 → 8 lane 확장의 #6 배포 lane plugin 신설 ([ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md)). consumer application repo 의 Epic 묶음 종료 후 배포 행위를 1st-class lane 으로 정립.

#### Added

- `.claude-plugin/plugin.json` — codeforge-deploy plugin manifest (1.0.0 baseline).
- `agents/DeployPLAgent.md` — 배포 lane PL (Sonnet tier, ADR-042 Amendment 9):
  - Epic 묶음 단위 발동 — 변경 repo enumeration + blue-green sequence orchestration
  - healthcheck 검증 + atomic swap trigger + 3-시간 보존 timer + 자동 rollback 결정
  - 배포 단위 = repo (consumer 묶음 Epic 안 변경된 repo 만, ADR-087 §결정 3)
- `agents/DeployWorkerAgent.md` — 배포 worker (Sonnet tier):
  - 각 repo 배포 실행 — 9-step 마이그레이션 sequence (빌드 → expand migration → green start → 건강 확인 → 검증 → atomic swap → blue drain → 3-시간 보존 → 정리)
  - idempotent script 실행 + graceful shutdown + healthcheck endpoint poll + secret provider lookup (1Password Connect 또는 fallback) + reverse proxy label 갱신 (Traefik primary)
- `CLAUDE.md` — codeforge-deploy lane plugin identity + DeployPLAgent / DeployWorkerAgent 역할 + self-write boundary + ADR-087 cross-ref.
- `templates/` — 배포 매커니즘 template (배포 흐름 9-step 참조 + Story-1 7 workflow seed cross-ref).
- `README.md` — plugin 설치 / 의존성 / architecture.

#### Notes

- 본 release = Phase 1 declarative + agent file seed. 배포 매커니즘 실 wire (auto-deploy.yml / blue-green-swap.yml workflow) = Story-1 wrapper repo seed (Phase 2 wire 별 carrier).
- `[empirical-source: TBD]` annotation 3개소 (healthcheck window / graceful drain / retention period) — consumer mctrader 실측 후 lock-in (ADR-068 I-5 dimensional empirical grounding).
