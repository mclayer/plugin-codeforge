# 배포 매커니즘 template (blue-green + atomic swap + 3-시간 보존)

> **DEPRECATED — schema SSOT 이동 (CFP-1317-S2, ADR-068 I-4 wording SSOT)**:
> consumer overlay `project.yaml deploy.*` schema 의 canonical SSOT = wrapper [`docs/project-config-schema.md` deploy 섹션](https://github.com/mclayer/plugin-codeforge/blob/main/docs/project-config-schema.md#deploy-섹션-설명-cfp-1059--adr-087--adr-088) (5 mandatory nested: `host_mapping` / `docker_hub` / `traefik` / `1password` / `ssh_targets` + 4 optional: `auto_rollback` / `operational_monitor` / `self_improving_loop` / `canary`). 본 file 안 schema block mirror = 제거 (6회 누적 drift evidence — mctrader#1272 (d) carrier, ADR-045 §D-9 pattern_count=6).
> 본 file 의 retain scope = **9-step blue-green sequence (reference) + Edge Cases reference** 만. schema 작성 시 wrapper SSOT 직접 참조 의무.
> 결정 근거 = ArchitectAgent chief tie-break ladder Step 2 (ADR-068 I-4 invariant d-B 직접 발사, 3중 concur: Researcher 5/5 prior art + PL d-B + I-4 invariant). 산업 prior art (Kubernetes / Helm / Terraform / OpenAPI / JSON Schema) 5/5 single-SSOT pattern 답습.

## 9-step blue-green sequence (ADR-087 §결정 5)

| 단계 | 내용 | 책임 |
|---|---|---|
| 1 | 빌드 → Docker Hub push | DeployWorker (GitHub Actions build) |
| 2 | 확장 (expand) 마이그레이션 apply | DeployWorker (Alembic / 빅데이터 expand — ADR-089 §결정 2) |
| 3 | green 컨테이너 시작 | DeployWorker (blue 유지) |
| 4 | 건강 확인 | DeployPL 검증 (healthcheck `/healthz` + log signature, default 60s) |
| 5 | 검증 단계 | 배포 리뷰 lane (smoke + 성능 비교 — ADR-088) |
| 6 | atomic swap | DeployPL trigger (Traefik label swap, cutover 순간) |
| 7 | blue graceful drain | DeployWorker (HTTP 30s / WebSocket 300s) |
| 8 | blue 3-시간 보존 | DeployPL timer (retention_hours default 3) |
| 9 | 3-시간 후 정리 | DeployWorker (container stop, image 보존). contract 마이그레이션 = 다음 Epic step 2 |

> **시간 차원 empirical-source annotation**: 4단계 healthcheck window / 7단계 graceful drain / 8단계 retention 3-시간 = wrapper [ADR-087 §결정 5](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) 본문 `[empirical-source: TBD]` 3개소 (ADR-068 I-5 dimensional empirical grounding, consumer mctrader 첫 적용 시 실측 후 lock-in). 본 file 안 별도 annotation 제거 — wrapper SSOT 단일 anchor.

## consumer overlay schema 참조 (wrapper SSOT redirect)

consumer `project.yaml deploy.*` 작성 = wrapper [`docs/project-config-schema.md` deploy 섹션](https://github.com/mclayer/plugin-codeforge/blob/main/docs/project-config-schema.md#deploy-섹션-설명-cfp-1059--adr-087--adr-088) **단일 SSOT 직접 참조** 의무 (본 file 안 schema mirror 0건 — drift 0 invariant, ADR-068 I-4).

- **5 mandatory nested**: `host_mapping` (multi-host topology) / `docker_hub` (registry 좌표) / `traefik` (reverse proxy) / `1password` (secret provider) / `ssh_targets` (SSH 배포 대상)
- **4 optional nested**: `auto_rollback` (CFP-1193 / ADR-105) / `operational_monitor` (CFP-1194 / ADR-106 Amd 2) / `self_improving_loop` (CFP-1195 / ADR-106 §결정 4) / `canary` (CFP-1196 / ADR-105 §결정 3)
- **enforce workflow**: wrapper [`templates/github-workflows/deployment-schema-check.yml`](https://github.com/mclayer/plugin-codeforge/blob/main/templates/github-workflows/deployment-schema-check.yml) (warning tier, `continue-on-error: true`, `hotfix-bypass:deployment-schema` label)
- **fallback semantic / write boundary / cross-layer 영향 / schema 7 원칙 binding**: wrapper SSOT 본문 verbatim 참조 (본 file 안 mirror 0건)

## Edge Cases (배포 매커니즘 — wrapper SSOT cross-ref)

각 EC 의 의미 anchor = wrapper [`docs/project-config-schema.md` deploy 섹션](https://github.com/mclayer/plugin-codeforge/blob/main/docs/project-config-schema.md#deploy-섹션-설명-cfp-1059--adr-087--adr-088) fallback semantic 단락 + [ADR-087 §결정 5](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) 본문 verbatim 참조.

- **EC-1** 1Password Connect 부재 → `.env` + GitHub Actions secret fallback (wrapper SSOT `deploy.1password.enabled=false` fallback semantic)
- **EC-2** Traefik 부재 → 다른 reverse proxy abstraction (wrapper SSOT `deploy.traefik.enabled=false` fallback semantic — Phase 1 = Traefik primary, abstract interface Wave 5+)
- **EC-3** 큰 변경 hard limit (column 100+ / row 1억+ / lock 5분+) → 자동 흐름 외 + 사용자 수동 trigger (ADR-089 §결정 7 hard limit cross-ref)
- **EC-4** 3-시간 보존 중 결함 발견 → 자동 rollback (blue 복원). 3-시간 이후 = hotfix path (ADR-087 §결정 5 step 8 retention + wrapper SSOT `deploy.auto_rollback` optional block)
- **EC-5** 호스트 자원 2배 한계 초과 → rolling (한 대씩) fallback 자동 선택
- **EC-6** 이중화 호스트 부재 → downtime 0 보장 불가, consumer 영역 declare 의무 (wrapper SSOT 안 별도 field 미정의 — consumer-side 자율 영역)
- **EC-7** Consumer self-hosted Docker Hub fork → wrapper SSOT `deploy.docker_hub.org` override (registry 좌표 5-nested 안 cover)

## 관련 cross-ref

- ADR-087 §결정 5 = 9-step sequence 본문 SSOT (본 file 안 표 = mirror, 의미 verbatim)
- ADR-088 §결정 6 = 배포 리뷰 lane verification_mode (step 5 검증 단계 정합)
- ADR-068 I-4 wording SSOT + I-5 dimensional empirical = 본 d-B 결정 invariant 근거
- ADR-045 §D-9 = mctrader#1272 (d) 6회 누적 drift super-class evidence (escalation_action: adr_draft_emitted → S3 ADR-107 carrier)
- ADR-013 = codeforge family dogfood-out (본 plugin = lane plugin self-write boundary, schema authoring scope = wrapper SSOT 영역)
