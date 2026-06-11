# codeforge-deploy-review

[`codeforge`](https://github.com/mclayer/plugin-codeforge) CFP-1059 — Deploy Review (배포 리뷰) lane plugin.

DeployReviewPLAgent (Opus) + DeployReviewWorkerAgent (Sonnet) + ProductionEvidenceDeputy (CONDITIONAL deputy, ADR-72 이관). **production 환경 성능 측정을 1st-class 검증 phase 로 격상** ([ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md)). 성능 기준 미충족 시 요구사항 / 설계 lane 으로 back.

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 6.0.0) + [`codeforge-deploy@mclayer`](../codeforge-deploy/) (직전 배포 lane, 동일 모노레포 `plugins/codeforge-deploy/`). 단독 동작 불가 — codeforge wrapper의 Orchestrator가 DeployReviewPLAgent를 스폰.

## 설치

```jsonc
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "mclayer": { "source": { "source": "github", "repo": "mclayer/marketplace" } }
  },
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-deploy@mclayer": true,
    "codeforge-deploy-review@mclayer": true
  }
}
```

또는 CLI:

```
/plugins install codeforge@mclayer
/plugins install codeforge-deploy@mclayer
/plugins install codeforge-deploy-review@mclayer
```

## Architecture

8 lane composition 의 #7 배포 리뷰 lane:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → [배포 리뷰]
```

- **DeployReviewPLAgent** (Opus) — 성능 측정 1st-class lead. smoke / 성능 비교 / cutover 사후 검증 verdict 종합. 성능 미충족 시 root cause 진단 + debate-protocol-v1 trigger + lane FIX dispatch.
- **DeployReviewWorkerAgent** (Sonnet) — smoke test (HTTP shadow / WebSocket·daemon 대기) + 성능 baseline 수집 + cutover 사후 측정.
- **ProductionEvidenceDeputyAgent** (CONDITIONAL) — production cutover evidence quad (functional / security / monitoring / testing). ADR-72 이관.

### 검증 3종 (한 번 끝나는)

| 검증 | 시점 | 매커니즘 |
|---|---|---|
| smoke | atomic swap 직전 | HTTP shadow / WebSocket·daemon 대기 |
| 성능 비교 | atomic swap 직전 | latency p50/p95/p99 / throughput / error rate baseline 대비 |
| cutover 사후 검증 | atomic swap 직후 ~ 3-시간 | 실 production 트래픽 회귀 감지 |

운영 phase (continuous monitoring) 와 disjoint — 본 lane = "한 번 끝나는" 검증만.

### 성능 미충족 시 회귀 (ADR-088 §결정 5)

- code-level → DeveloperPL FIX (구현 lane)
- design-level → ArchitectPL FIX (설계 lane)
- requirements-level → RequirementsPL FIX (요구사항 lane)
- cross-module → debate-protocol-v1 자동 발동 (ADR-059)

## 관련 ADR

- [ADR-088](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane 신설 + ProductionEvidenceDeputy 이관 (본 plugin SSOT carrier)
- [ADR-087](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane (직전)
- [ADR-042](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-042-agent-model-selection-policy.md) — Amendment 9 (DeployReviewPL Opus / Worker Sonnet)
- [ADR-72](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md) — ProductionEvidenceDeputy
- [ADR-068](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-068-boundary-completeness-invariants.md) — I-5 성능 측정 dimensional empirical grounding
- [ADR-059](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-059-debate-protocol-v1.md) — debate-protocol-v1
