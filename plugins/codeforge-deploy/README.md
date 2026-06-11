# codeforge-deploy

[`codeforge`](https://github.com/mclayer/plugin-codeforge) CFP-1059 — Deploy (배포) lane plugin.

DeployPLAgent + DeployWorkerAgent 2종 (Sonnet tier). consumer application repo 의 Epic 묶음 종료 후, 변경된 repo 만 production 환경에 배포하는 매커니즘을 1st-class lane 으로 실행. 배포 행위 자체 정립 ([ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md)).

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 6.0.0). 단독 동작 불가 — codeforge wrapper의 Orchestrator가 DeployPLAgent를 스폰하고 결과 수령.

본 plugin은 codeforge core (wrapper) 의 8 lane composition 중 #6 배포 lane. 통합테스트 → 보안테스트 통과 후 Epic close 시점 발동.

## 설치

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-deploy@mclayer": true
  }
}
```

또는 CLI:

```
/plugins install codeforge@mclayer
/plugins install codeforge-deploy@mclayer
```

## Architecture

8 lane composition 의 #6 배포 lane:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → [배포] → 배포 리뷰
```

- **DeployPLAgent** (Sonnet) — 배포 매커니즘 실행 lead. Epic 묶음 단위 발동, 변경 repo 결정, blue-green sequence orchestration, healthcheck 검증, atomic swap trigger, 3-시간 보존 timer, 자동 rollback 결정.
- **DeployWorkerAgent** (Sonnet) — 각 repo 배포 worker. 9-step 마이그레이션 sequence (빌드 → expand migration → green start → 건강 확인 → 검증 → atomic swap → blue drain → 3-시간 보존 → 정리).

### 배포 매커니즘 (단일)

blue-green + atomic swap + 3-시간 보존 + 자동 rollback. 인프라 stack:

| 영역 | Primary | Consumer override |
|---|---|---|
| 빌드 | GitHub Actions | consumer 자체 workflow |
| 저장 | Docker Hub | `project.yaml deploy.registry` |
| 배포 | SSH pull (다중 호스트) | — |
| 비밀 | 1Password Connect | `.env` + GitHub Actions secret fallback |
| traffic 분배 | Traefik (label-based) | nginx / Caddy / haproxy (Wave 5+ abstraction) |

### 배포 단위

repo. consumer 묶음 Epic 안 변경된 repo 만 배포 (변경 안 된 repo skip). mctrader 사례: 5 repo 중 손댄 것만.

## 관련 ADR

- [ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane 신설 + lane lifecycle 6→8 단계 확장 (본 plugin SSOT carrier)
- [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane (sibling)
- [ADR-042](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) — Amendment 9 (DeployPL/Worker Sonnet tier)
- [ADR-023](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-023-lane-plugin-lifecycle.md) — lane plugin lifecycle
