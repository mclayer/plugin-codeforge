# 배포 매커니즘 template (blue-green + atomic swap + 3-시간 보존)

> consumer application repo 의 배포 매커니즘 참조 template. 실 workflow yml seed = wrapper repo `templates/github-workflows/` (auto-deploy.yml / blue-green-swap.yml / retention-window-timer.yml / auto-rollback.yml — CFP-1059 Story-1). 본 file 은 9-step sequence + consumer declare schema 참조용.

## 9-step blue-green sequence (ADR-087 §결정 5)

| 단계 | 내용 | 책임 |
|---|---|---|
| 1 | 빌드 → Docker Hub push | DeployWorker (GitHub Actions build) |
| 2 | 확장 (expand) 마이그레이션 apply | DeployWorker (Alembic / 빅데이터 expand — ADR-089 §결정 2) |
| 3 | green 컨테이너 시작 | DeployWorker (blue 유지) |
| 4 | 건강 확인 | DeployPL 검증 (healthcheck `/healthz` + log signature, default 60s `[empirical-source: TBD]`) |
| 5 | 검증 단계 | 배포 리뷰 lane (smoke + 성능 비교 — ADR-088) |
| 6 | atomic swap | DeployPL trigger (Traefik label swap, cutover 순간) |
| 7 | blue graceful drain | DeployWorker (HTTP 30s / WebSocket 300s `[empirical-source: TBD]`) |
| 8 | blue 3-시간 보존 | DeployPL timer (retention_hours default 3) |
| 9 | 3-시간 후 정리 | DeployWorker (container stop, image 보존). contract 마이그레이션 = 다음 Epic step 2 |

## consumer project.yaml deploy block schema (ADR-027 Amendment N)

```yaml
deploy:
  enabled: true                          # default false (backward-compat) — 본 lane 활성 조건
  environments: [production]             # default 1, staging/canary optional (Wave 5+ promotion)
  registry: docker.io/<org>              # Docker Hub default 또는 self-hosted fork override (EC-7)
  secret_provider: onepassword_connect   # onepassword_connect | env_github_actions (EC-1 fallback)
  reverse_proxy: traefik                 # traefik (primary) | nginx | caddy | haproxy (EC-2 Wave 5+)
  retention_hours: 3                     # blue 보존 시간 (default 3, consumer override)
  acceptable_downtime_ms: 0              # 단일 호스트 환경 declare 의무 (EC-6 이중화 부재)
  hosts:                                 # SSH 배포 대상 다중 호스트
    - { name: host-1, ssh: user@host-1 }
    - { name: host-2, ssh: user@host-2 }
  services:                              # service 별 검증 mode (배포 리뷰 lane — ADR-088 §결정 6)
    - { repo: app-web, verification_mode: http }
    - { repo: app-market, verification_mode: websocket }
    - { repo: app-engine, verification_mode: daemon }
```

## Edge Cases (배포 매커니즘)

- **EC-1** 1Password Connect 부재 → `.env` + GitHub Actions secret fallback
- **EC-2** Traefik 부재 → 다른 reverse proxy abstraction (Phase 1 = Traefik primary, abstract interface 만)
- **EC-3** 큰 변경 hard limit (column 100+ / row 1억+ / lock 5분+) → 자동 흐름 외 + 사용자 수동 trigger
- **EC-4** 3-시간 보존 중 결함 발견 → 자동 rollback (blue 복원). 3-시간 이후 = hotfix path
- **EC-5** 호스트 자원 2배 한계 초과 → rolling (한 대씩) fallback 자동 선택
- **EC-6** 이중화 호스트 부재 → downtime 0 보장 불가, consumer `acceptable_downtime_ms` declare 의무
- **EC-7** Consumer self-hosted Docker Hub fork → `deploy.registry` override

## [empirical-source: TBD] annotation (ADR-068 I-5)

3개소 — consumer mctrader 첫 적용 시 실측 후 lock-in:
1. healthcheck window (default 60s timeout)
2. graceful drain timeout (HTTP 30s / WebSocket 300s)
3. retention period (3-시간 default)
