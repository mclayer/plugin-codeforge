# codeforge-develop

[`codeforge`](https://github.com/mclayer/plugin-codeforge) ζ arc CFP-39 — Develop lane plugin.

5 agent 집합 (DeveloperPL + QADev + 3 role:dev core) + presets/webapp (Backend/Frontend Developer). DeveloperPL 이 role:dev roster 동적 discover + 병렬 spawn + Story §8/§8.5 self-write + Phase 2 PR open.

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 4.0.0).

## 설치

```jsonc
{
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true,
    "codeforge-pmo@mclayer": true,
    "codeforge-requirements@mclayer": true,
    "codeforge-test@mclayer": true,
    "codeforge-develop@mclayer": true
  }
}
```

## Inter-plugin Contract

`develop_output v1` — `docs/inter-plugin-contracts/develop-output-v1.md` (canonical).

## Presets

`presets/webapp/` — webapp 프로젝트용 BackendDeveloperAgent + FrontendDeveloperAgent. consumer overlay 가 활성 preset 지정.
