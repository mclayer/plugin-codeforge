# codeforge-design

[`codeforge`](https://github.com/mclayer/plugin-codeforge) ζ arc CFP-40 (LAST) — Design lane plugin.

7 agent (ArchitectPL + chief author + 5 deputies) + change-plan/adr templates owned. ζ arc 의 가장 큰 표면 — 마지막 추출 (Codex round 2 sequencing 권고).

## Dependencies

**필수**: [`codeforge@mclayer`](https://github.com/mclayer/plugin-codeforge) (>= 5.0.0).

## 설치

```jsonc
{
  "enabledPlugins": {
    "codeforge@mclayer": true,
    "codeforge-review@mclayer": true,
    "codeforge-pmo@mclayer": true,
    "codeforge-requirements@mclayer": true,
    "codeforge-test@mclayer": true,
    "codeforge-develop@mclayer": true,
    "codeforge-design@mclayer": true
  }
}
```

## Architecture

ArchitectPLAgent 가 5 deputies 병렬 spawn → ArchitectAgent (chief author) 가 통합 + Change Plan §1-11 + 신규 ADR draft + Story §3/§7/§11 mirror self-write.

## Inter-plugin Contract

`design_output v1` — `docs/inter-plugin-contracts/design-output-v1.md` (canonical).

## Owner doc paths

- `docs/change-plans/**` (ArchitectAgent direct write)
- `docs/adr/**` (ArchitectAgent direct write)

## Templates

- `templates/change-plan.md` — Change Plan §1-11 schema
- `templates/adr.md` — ADR 페이지 schema

## ζ arc 종료

본 plugin 추출 완료로 codeforge wrapper 는 agent 0개 (DocsAgent 도 동시 삭제). codeforge 가 wrapper-only 모델로 완전 수렴 — parent spec mclayer/plugin-codeforge CFP-31 의 end-state 도달.
