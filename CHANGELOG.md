# Changelog

`codeforge-deploy` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

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
